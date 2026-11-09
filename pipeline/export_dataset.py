"""Export the usable bugs as an AgenTrace-style log-pair dataset.

For every usable bug (one fix commit per issue: the one with the shortest covering pair), each fix
test that produced a covering pair is re-run on the buggy version under SELogger with
weave=EXEC+CALL+LINE+PARAM, so the trace also holds the arguments of every logging call
(message template and argument values).  The test is run twice; a bug is `stable` when both runs
give the same covering pairs.

Output, per bug:  <out>/<project>/<issue>/
  meta.json     issue, fix commit, buggy version, test(s), faulty lines, stability, thread counts
  pairs.jsonl   one log pair per line: start/end log (file, line, level, template, args),
                ground-truth path (ordered, duplicate-free [file, line] list, both logs included),
                covers_fault, path_lines.  All covering pairs are kept; other pairs are deduplicated
                by (start, end, path) and capped at MAX_OTHER per test.
and <out>/index.csv with one row per bug.

usage: python3 -I export_dataset.py <out dir> <selogger.jar> <work dir> <workers> <project=repo>...
  env SAMPLE_DIR=results/systematic/samples restricts to the systematic sample
  env ISSUES=JCR-3552,IOTDB-2465 restricts to these issues
"""
import bisect, collections, csv, glob, json, os, re, shutil, subprocess, sys
csv.field_size_limit(sys.maxsize)  # SELogger records whole string values (AMQ-4897 has one over 128 KiB)
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipeline as pl  # noqa: E402
import fault_coverage  # noqa: E402
from analyse_trace import LOG_OWNERS, LOG_NAMES, attrs  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, '..', 'results', 'pipeline')
MAX_OTHER = 500
# a captured log above this size is not aligned with the trace (CAMEL-9143's leak test prints 2 GB, and matching its
# millions of calls to lines did not finish in two hours); its logs then count as not printed
ALIGN_LIMIT_BYTES = 1024 ** 3


def sampled_shas():
    """SAMPLE_DIR=<dir of <repo>_sample.json>: only commits in the systematic sample count (older rounds
    ran other candidates too).  Returns {pipeline project: set of shas}, or None without SAMPLE_DIR."""
    sdir = os.environ.get('SAMPLE_DIR')
    if not sdir:
        return None
    alias = {'velocity-engine': 'velocity', 'xmlgraphics-fop': 'fop', 'ws-wss4j': 'wss4j',
             'santuario-xml-security-java': 'santuario', 'logging-log4j2': 'log4j2'}
    out = {}
    for sf in glob.glob(os.path.join(sdir, '*_sample.json')):
        repo = os.path.basename(sf)[:-len('_sample.json')]
        out[alias.get(repo, repo)] = {c['sha'] for c in json.load(open(sf))}
    return out


ONLY = set(filter(None, os.environ.get('ISSUES', '').split(',')))  # env ISSUES=A-1,B-2: just these


# bugs dropped after manual review (the buggy failure is unrelated to the fix), see HANDOFF section 10
EXCLUDE_TSV = os.path.join(os.path.dirname(RESULTS), 'systematic', 'manual_exclude.tsv')


def usable_bugs():
    best, sample = {}, sampled_shas()
    excluded = {l.split('\t')[0] for l in open(EXCLUDE_TSV)} if os.path.exists(EXCLUDE_TSV) else set()
    for f in glob.glob(os.path.join(RESULTS, '*_pipeline.jsonl')):
        project = os.path.basename(f)[:-len('_pipeline.jsonl')]
        for line in open(f):
            r = json.loads(line)
            cov = [t for t in r.get('traces', []) if t.get('covering_pairs') and t['status'] == 'fail']
            if r['result'] != 'usable' or not cov:  # the covering trace must come from a failing test
                continue
            r = dict(r, covering_min_lines=min(t['covering_min_lines'] for t in cov))
            if sample is not None and r['sha'] not in sample.get(project, ()):
                continue
            if r['issue'] in excluded:
                continue
            if ONLY and r['issue'] not in ONLY:
                continue
            k = (project, r['issue'])
            if k not in best or r['covering_min_lines'] < best[k]['covering_min_lines']:
                best[k] = dict(r, project=project)
    return sorted(best.values(), key=lambda r: r['covering_min_lines'])


def read_trace(sel, test=None):
    """Per-thread tokens: ('L', cls, line) or ('G', cls, line, level, [params]).
    With test = 'Class#method', also returns, per thread, whether each token ran inside that test method
    (between its METHOD_ENTRY and exit), i.e. not in the constructor, @Before/@After, class set-up or another
    test method of the class (old surefire and some JUnit 5 set-ups run the whole class)."""
    prod, tcls = set(), set()
    with open(os.path.join(sel, 'classes.txt'), newline='') as fh:
        for row in csv.DictReader(fh):
            if '/test-classes/' not in row['LoadedFrom']:
                prod.add(row['ClassID'])
            else:
                tcls.add(row['ClassID'])
    tname, tmeth = (test.split('#', 1) if test else (None, None))
    info, log_calls = {}, set()
    with open(os.path.join(sel, 'dataids.txt'), newline='') as fh:
        for row in csv.DictReader(fh):
            if row['ClassID'] in tcls and tname and row['MethodName'] == tmeth \
                    and re.split(r'[/.]', row['ClassName'])[-1] == tname:
                if row['EventType'] == 'METHOD_ENTRY':
                    info[row['DataID']] = ('T+',)
                elif row['EventType'] in ('METHOD_NORMAL_EXIT', 'METHOD_EXCEPTIONAL_EXIT'):
                    info[row['DataID']] = ('T-',)
                continue
            if row['ClassID'] not in prod:
                continue
            et = row['EventType']
            if et == 'LINE_NUMBER':
                info[row['DataID']] = ('L', row['ClassName'], int(row['Line']))
            elif et == 'CALL':
                a = attrs(row['Attributes'])
                if a.get('owner') in LOG_OWNERS and a.get('name') in LOG_NAMES:
                    info[row['DataID']] = ('G', row['ClassName'], int(row['Line']), a['name'])
                    log_calls.add((row['MethodID'], row['InstructionIndex']))
            elif et == 'CALL_RETURN' and (row['MethodID'], row['InstructionIndex']) in log_calls:
                info[row['DataID']] = ('R',)  # the logging call returned
            elif et == 'CALL_PARAM':
                info[row['DataID']] = ('P', row['ClassName'], int(row['Line']), row['ValueDesc'])
    strings = {}
    for f in glob.glob(os.path.join(sel, 'LOG$String*.txt')):
        # one string per line: id,length,"content" with JSON escapes (\" \n \\), not CSV quoting
        with open(f, errors='ignore') as fh:
            for line in fh:
                row = line.rstrip('\n').split(',', 2)
                if len(row) == 3:
                    try:
                        strings[row[0]] = json.loads(row[2])
                    except ValueError:
                        strings[row[0]] = row[2].strip('"')
    threads, inside, inlog, depth, in_call = {}, {}, {}, collections.Counter(), {}
    for f in sorted(glob.glob(os.path.join(sel, 'log-*.txt'))):
        with open(f, errors='ignore') as fh:
            next(fh)
            for line in fh:
                parts = line.rstrip('\n').split(',', 3)
                if len(parts) < 3:   # truncated last line of a trace file (reactor-netty GH-4415, 2026-11-03)
                    continue
                _, did, tid, val = (parts + [''])[:4]
                tok = info.get(did)
                if tok is None:
                    continue
                if tok[0] in ('T+', 'T-'):
                    depth[tid] += 1 if tok[0] == 'T+' else -1
                    continue
                if tok[0] == 'R':
                    in_call[tid] = False
                    continue
                seq = threads.setdefault(tid, [])
                if tok[0] == 'P':
                    if seq and seq[-1][0] == 'G' and seq[-1][1:3] == tok[1:3]:
                        seq[-1][4].append(strings.get(val, val))
                    continue
                seq.append(('G', tok[1], tok[2], tok[3], []) if tok[0] == 'G' else tok)
                inside.setdefault(tid, []).append(depth[tid] > 0)
                # production code the logging framework calls back while formatting (e.g. toString() of a {} argument)
                inlog.setdefault(tid, []).append(tok[0] != 'G' and in_call.get(tid, False))
                if tok[0] == 'G':
                    in_call[tid] = True
    if test is None:
        return threads
    if not any(depth_seen for v in inside.values() for depth_seen in v):
        inside = None  # the test method's entry was not traced: cannot tell, do not filter
    return threads, inside, inlog


def class_origins(sel):
    """Class path -> where SELogger saw it loaded from (e.g. file:/.../activemq-broker/target/classes/)."""
    with open(os.path.join(sel, 'classes.txt'), newline='') as fh:
        # a malformed row (seen in two Gradle projects, 2026-11-03) has no ClassName: skip it
        return {r['ClassName'].replace('.', '/'): r['LoadedFrom'] for r in csv.DictReader(fh) if r.get('ClassName')}


def under_symlink(p, wt):
    """True when a directory between wt and the file p is a symbolic link (glob follows them)."""
    cur = wt
    for part in os.path.relpath(p, wt).split('/')[:-1]:
        cur = os.path.join(cur, part)
        if os.path.islink(cur):
            return True
    return False


def source_file(java_files, cls, origins):
    """Repository file of a class path; when several modules have one (ActiveMQ's IOHelper, Camel, IoTDB),
    the one whose module the class was loaded from. Classes without a source file (generated) keep
    <class path>.java."""
    files = java_files.get(cls)
    if not files:
        return cls + '.java'
    if len(files) > 1:
        loaded = origins.get(cls) or next((v for k, v in origins.items() if k.split('$')[0] == cls), '')
        # deepest module first, so a root-module file (prefix '') only matches when no module does
        for f in sorted(files, key=lambda f: -len(('/' + f).split('/src/')[0])):
            if ('/' + f).split('/src/')[0] + '/target/' in loaded:
                return f
    return files[0]


def pairs_of(threads, faults, src_of, inside=None, inlog=None):
    """inside: per thread, whether each token ran inside the traced test method (see read_trace); when given,
    on the test method's thread a pair covers the fault only when both logs and the faulty-line execution run
    inside the test method; threads where the test method never ran (worker threads it started) are kept as
    they are."""
    out = []
    for tid, toks in threads.items():
        ins = inside.get(tid) if inside else None
        inl = inlog.get(tid) if inlog else None
        if ins is not None and not any(ins):
            ins = None
        logs = [i for i, t in enumerate(toks) if t[0] == 'G']
        ordinal = {pos: k for k, pos in enumerate(logs)}
        for a, b in zip(logs, logs[1:]):
            in_test = ins is None or (ins[a] and ins[b])  # both logs inside the test method (on its thread)
            # code run while the end log's arguments are evaluated (from that log statement's line event to the
            # logging call, e.g. a toString() the message formats) runs only because we log: it does not count
            args_from = max((i for i in range(a + 1, b) if toks[i][0] == 'L' and toks[i][1:3] == toks[b][1:3]),
                            default=b)
            fault_hit = in_test and any(t[0] == 'L' and (t[1].split('$')[0], t[2]) in faults
                            and (t[1], t[2]) not in ((toks[a][1], toks[a][2]), (toks[b][1], toks[b][2]))
                            and a + 1 + j < args_from and (ins is None or ins[a + 1 + j])
                            and not (inl and inl[a + 1 + j])
                            for j, t in enumerate(toks[a + 1:b]))
            path, seen = [], set()
            for t in [toks[a]] + [x for x in toks[a + 1:b] if x[0] == 'L'] + [toks[b]]:
                if (t[1], t[2]) not in seen:
                    seen.add((t[1], t[2]))
                    path.append((t[1], t[2]))
            log = lambda pos: dict(file=src_of(toks[pos][1]), cls=toks[pos][1], line=toks[pos][2], level=toks[pos][3],
                                   template=toks[pos][4][0] if toks[pos][4] else None, args=toks[pos][4][1:],
                                   idx=ordinal[pos])
            out.append(dict(thread=tid, start=log(a), end=log(b),
                            path=[[src_of(c), l] for c, l in path], path_lines=len(path),
                            # the two log statements themselves do not count: a fix that only edits a log
                            # message would otherwise make every pair ending at that log "cover" the fault
                            covers_fault=fault_hit, in_test_method=in_test))
    return out


def logging_props(cfg_dir, log_file):
    """JVM options that send JUL, Log4j 1/2 and commons-logging output, at the most verbose level, to one
    file in append mode (so frameworks writing to the same file do not truncate each other)."""
    os.makedirs(cfg_dir, exist_ok=True)
    jul, l4j2, l4j1 = (os.path.join(cfg_dir, f) for f in ('logging.properties', 'log4j2.xml', 'log4j.properties'))
    open(jul, 'w').write(
        'handlers=java.util.logging.FileHandler\n.level=ALL\n'
        'java.util.logging.FileHandler.level=ALL\n'
        f'java.util.logging.FileHandler.pattern={log_file}\n'
        'java.util.logging.FileHandler.append=true\n'
        'java.util.logging.FileHandler.formatter=java.util.logging.SimpleFormatter\n'
        'java.util.logging.SimpleFormatter.format=%1$tFT%1$tT.%1$tL %4$s %3$s - %5$s%6$s%n\n')
    open(l4j2, 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<Configuration status="WARN"><Appenders>'
        f'<File name="F" fileName="{log_file}" append="true">'
        '<PatternLayout pattern="%d{yyyy-MM-dd\'T\'HH:mm:ss.SSS} %level %logger [%t] - %msg%n"/></File>'
        '</Appenders><Loggers><Root level="all"><AppenderRef ref="F"/></Root></Loggers></Configuration>\n')
    open(l4j1, 'w').write(
        'log4j.rootLogger=ALL, F\nlog4j.appender.F=org.apache.log4j.FileAppender\n'
        f'log4j.appender.F.File={log_file}\nlog4j.appender.F.Append=true\n'
        'log4j.appender.F.layout=org.apache.log4j.PatternLayout\n'
        'log4j.appender.F.layout.ConversionPattern=%d{ISO8601} %p %c [%t] - %m%n\n')
    return (f'-Djava.util.logging.config.file={jul} -Dlog4j2.configurationFile={l4j2} '
            f'-Dlog4j.configurationFile={l4j2} -Dlog4j.configuration=file:{l4j1} '
            '-Dorg.slf4j.simpleLogger.defaultLogLevel=trace')


def patch_velocity_logging(wt, mod_dir, log_file):
    """Velocity's POM pins slf4j-simple to WARN (output target/velocity.log); raise it to TRACE."""
    pom = os.path.join(mod_dir, 'pom.xml')
    if os.path.exists(pom):
        s = open(pom).read()
        s = re.sub(r'(<name>org\.slf4j\.simpleLogger\.defaultLogLevel</name>\s*<value>)\w+(</value>)', r'\1trace\2', s)
        s = re.sub(r'(<org\.slf4j\.simpleLogger\.defaultLogLevel>)\w+(</org\.slf4j\.simpleLogger\.defaultLogLevel>)',
                   r'\1trace\2', s)
        open(pom, 'w').write(s)
    patch_velocity_test_logger(wt, log_file)


def patch_velocity_test_logger(wt, log_file):
    """Velocity's tests log through TestLogger (INFO, to stderr/memory). Test-only patch: TRACE level, and
    every message is also appended to the log file. Production code is untouched."""
    for p in glob.glob(os.path.join(wt, '**', 'test', 'misc', 'TestLogger.java'), recursive=True):
        src = open(p).read()
        src = src.replace('private int enabledLevel = LOG_LEVEL_INFO;', 'private int enabledLevel = LOG_LEVEL_TRACE;')
        src = src.replace('writer.println(msg);',
                          'writer.println(msg); try (java.io.FileWriter fw = new java.io.FileWriter("'
                          + log_file + '", true)) { fw.write(getPrefix(level).trim() + " " + '
                          'Thread.currentThread().getName() + " - " + msg + "\\n"); } catch (java.io.IOException e) { }', 1)
        open(p, 'w').write(src)


def template_regex(t):
    """'{} upgrading to TLS {}:{}' -> regex; also handles %s/%d and {0}-style placeholders."""
    if t is None:
        return None
    r = re.escape(t)
    r = r.replace(re.escape('{}'), '(.*?)')
    r = re.sub(r'\\\{\d+\\\}', '(.*?)', r)
    r = re.sub(r'%[-#+ 0,(]*\d*(?:\.\d+)?[sdfxXbcoeEgGn]', '(.*?)', r)
    try:
        return re.compile(r + r'\s*', re.S)
    except re.error:
        return None


def longest_alignment(cands):
    """cands[k] = increasing line indices call k may have printed.  Returns {k: line} for a largest set of
    calls whose lines strictly increase with k (Hunt-Szymanski: longest increasing subsequence)."""
    tails, tail_node, nodes = [], [], []          # nodes: (k, line, previous node)
    for k, js in enumerate(cands):
        for j in reversed(js):                   # descending, so one call never extends itself
            i = bisect.bisect_left(tails, j)
            node = (k, j, tail_node[i - 1] if i else None)
            if i == len(tails):
                tails.append(j); tail_node.append(node)
            else:
                tails[i], tail_node[i] = j, node
    out, node = {}, tail_node[-1] if tail_node else None
    while node:
        out[node[0]] = node[1]
        node = node[2]
    return out


OUR_LINE = re.compile(r'(\d{4}-\d\d-\d\d[ T][\d:.,]+ [A-Z]+ \S+ \[.*?\]) - (.*)', re.S)


def align(threads, log_text):
    """Map (thread, ordinal) of every logging call in the trace to the printed log line it produced.

    The printed message is the text after the first ' - ' (all log formats used here put it there), or after
    the thread name in our own Log4j layouts. A call
    may have printed any line whose message fits its template (or, if the template is unknown or only
    placeholders, any line whose logger is the calling class).  Per trace thread, we keep the largest
    order-preserving matching of calls to lines; when the log format shows thread names and most matched
    lines come from one name, the matching is redone on that name's lines only, so that lines of other
    threads with the same message are not taken.  A call left unmatched was not printed (below the level,
    or redirected)."""
    lines = log_text.splitlines()
    # in our own layouts (date level logger [thread] - message) the message starts after '] - ', since thread
    # names may themselves contain ' - ' (Camel: '[Camel (camel-1) thread #0 - file://in]')
    ours = [OUR_LINE.match(l) for l in lines]
    heads = [m[1] if m else l.split(' - ', 1)[0] if ' - ' in l else '' for l, m in zip(lines, ours)]
    msgs = [m[2] if m else l.split(' - ', 1)[1] if ' - ' in l else l for l, m in zip(lines, ours)]
    tnames = [(re.search(r'\[([^\]]*)\]\s*$', h) or [None, None])[1] for h in heads]
    by_tpl, by_cls = {}, {}

    def cands(t):
        # a multi-line message prints as several log lines: match its first line
        tpl = t[4][0].split('\n', 1)[0] if t[4] and t[4][0] else None
        if tpl and not re.fullmatch(r'-?\d+', tpl) and re.sub(r'\{\d*\}|%\w', '', tpl).strip():
            if tpl not in by_tpl:
                rx = template_regex(tpl)
                by_tpl[tpl] = [j for j, m in enumerate(msgs) if rx and rx.fullmatch(m)]
            return by_tpl[tpl]
        fqcn = t[1].split('$')[0].replace('/', '.')
        if fqcn not in by_cls:
            by_cls[fqcn] = [j for j, h in enumerate(heads) if fqcn in h]
        return by_cls[fqcn]

    out = {}
    for tid, toks in threads.items():
        calls = [t for t in toks if t[0] == 'G']
        cs = [cands(t) for t in calls]
        hit = longest_alignment(cs)
        names = collections.Counter(tnames[j] for j in hit.values() if tnames[j] is not None)
        if names:
            name, n = names.most_common(1)[0]
            if n > 0.5 * len(hit):
                hit = longest_alignment([[j for j in c if tnames[j] in (name, None)] for c in cs])
        for k in range(len(calls)):
            out[(tid, k)] = msgs[hit[k]] if k in hit else None
    return out


def stable(a, b):
    """Both runs cover the fault with the same (test, start log, end log) pairs, and each such pair's
    path overlaps by at least 90% (Jaccard) - small differences come from caching/iteration order."""
    key = lambda s: {x[:5]: x[5] for x in s}
    ka, kb = key(a), key(b)
    if not ka or ka.keys() != kb.keys():
        return False
    return all(len(ka[k] & kb[k]) / len(ka[k] | kb[k]) >= 0.9 for k in ka)


def export(rec, wt, out_dir, agent_jar, repo):
    project, issue = rec['project'], rec['issue']
    sha = pl.git(repo, 'rev-parse', rec['sha']).strip()
    base = rec.get('base') or f'{sha}^'   # buggy revision ('base' only for recovered multi-commit fixes, GitHub version)
    bdir = os.path.join(out_dir, project, issue)
    shutil.rmtree(bdir, ignore_errors=True)
    os.makedirs(bdir)
    faults = fault_coverage.fault_lines(repo, sha, rec['main'], base)
    jdk = {'8': pl.JDK8, '17': pl.JDK17, '21': pl.JDK21, '25': pl.JDK25}[rec['jdk']]
    tests = list(dict.fromkeys(t['test'] for t in rec['traces'] if t.get('covering_pairs') and t['status'] == 'fail'))
    module = rec['module']
    java_files = {}
    runs, all_pairs, threads_n, log_too_large = [], [], {}, False
    # re-check that the fix's tests pass again on the fixed version (a flaky test can fake a reproduction)
    pl.git(wt, 'checkout', '-q', '-f', sha)
    pl.git(wt, 'clean', '-q', '-fdx')
    fr = pl.run_tests(project, wt, module, tests, jdk)
    fixed_rerun = fr['status']
    if fixed_rerun == 'disk_low' or 'No space left on device' in fr['out']:
        raise RuntimeError('disk low during the fixed rerun')   # recorded as an error and retried, not as a result
    for run in ((1,) if os.environ.get('SINGLE_RUN') else (1, 2)):
        sigs = set()
        for test in tests:
            pl.git(wt, 'checkout', '-q', '-f', sha)
            pl.git(wt, 'clean', '-q', '-fdx')
            pl.git(wt, 'checkout', '-q', base, '--', *rec['main'])
            if not java_files:
                for p in glob.glob(os.path.join(wt, '**', '*.java'), recursive=True):
                    # class path = part after the source root; a module directory named like a package
                    # root (e.g. PDFBox's io/) must not be taken for the package
                    rel = '/' + os.path.relpath(p, wt)
                    if under_symlink(p, wt):   # reactor-netty's docs/ links back to the modules (2026-11-05): not a second copy
                        continue
                    m = (re.search(r'/src/(?:main/)?java/(.*)\.java$', rel)
                         or re.search(r'/((?:org|com|net|io)/.*)\.java$', rel))
                    if m and '/test/' not in p:
                        java_files.setdefault(m.group(1), []).append(os.path.relpath(p, wt))
            mod_dir = os.path.join(wt, module) if module else wt
            log_file = os.path.join(mod_dir, 'target', 'app.log')
            if project == 'velocity':
                patch_velocity_logging(wt, mod_dir, log_file)
            pl.inject_argline(wt, mod_dir)
            tdir = os.path.join(bdir, f'_trace{run}')
            shutil.rmtree(tdir, ignore_errors=True)
            r = None
            for weave in ('EXEC+CALL+LINE+PARAM', 'EXEC+CALL+LINE'):   # without PARAM if the trace is too large
                shutil.rmtree(tdir, ignore_errors=True)
                logcfg = logging_props(os.path.join(bdir, "_logcfg"), log_file)
                agent = f'-Xmx4g {logcfg} -javaagent:{agent_jar}=output={tdir},format=omni,weave={weave},exlocation=.m2'
                # also as Maven properties: Hive and Atlas set log4j.configurationFile / log4j.configuration in
                # the POM's <systemPropertyVariables>, which surefire applies after the JVM options
                r = pl.run_tests(project, wt, module, [test], jdk, agent,
                                 [o for o in logcfg.split() if o.startswith('-Dlog4j')])
                if r['status'] == 'disk_low' or 'No space left on device' in r['out']:
                    shutil.rmtree(tdir, ignore_errors=True)
                    raise RuntimeError(f'disk low during traced run {run} of {test}')
                if os.path.isdir(tdir):
                    break
                pl.git(wt, 'checkout', '-q', '-f', sha)
                pl.git(wt, 'clean', '-q', '-fdx')
                pl.git(wt, 'checkout', '-q', base, '--', *rec['main'])
                if project == 'velocity':
                    patch_velocity_logging(wt, mod_dir, log_file)
                pl.inject_argline(wt, mod_dir)
            if project == 'velocity':
                # engine start-up logs go to velocity.log (slf4j-simple), later ones to app.log (TestLogger):
                # read them in that order so the in-order matching sees the real sequence
                txt = ''
                for f in ('velocity.log', 'app.log'):
                    pth = os.path.join(mod_dir, 'target', f)
                    if os.path.exists(pth):
                        txt += open(pth, errors='ignore').read()
                r['log'] = '\n'.join(l for l in txt.splitlines()
                                      if l.strip() and not l.startswith(('\t', 'at ', 'Caused by')))
            if run == 1:
                open(os.path.join(bdir, f'app_{test.replace("#", ".")}.log'), 'w').write(r['log'])
            shutil.rmtree(os.path.join(bdir, '_logcfg'), ignore_errors=True)
            if not os.path.isdir(tdir):
                continue
            threads, inside, inlog = read_trace(tdir, test)
            origins = class_origins(tdir)
            if os.environ.get('KEEP'):
                os.rename(tdir, f'{tdir}_{test.replace("#", ".")}')
            else:
                shutil.rmtree(tdir, ignore_errors=True)
            src_of = lambda c: source_file(java_files, c.split('$')[0], origins)
            ps = pairs_of(threads, faults, src_of, inside, inlog)
            if run == 1 and len(r['log']) > ALIGN_LIMIT_BYTES:
                log_too_large, printed = True, {}
            else:
                printed = align(threads, r['log']) if run == 1 else {}
            for p in ps:
                p['test'] = test
                for end in ('start', 'end'):
                    txt = printed.get((p['thread'], p[end]['idx']))
                    p[end]['printed'] = txt is not None
                    p[end]['text'] = txt
                if p['covers_fault']:
                    sigs.add((test, p['start']['cls'], p['start']['line'], p['end']['cls'], p['end']['line'],
                              frozenset(map(tuple, p['path']))))
            if run == 1:
                all_pairs += ps
                ran = re.findall(r'Tests run: (\d+), Failures', r.get('out', ''))
                threads_n[test] = dict(threads=len(threads), log_threads=len({p['thread'] for p in ps}),
                                       status=r['status'], tests_run=int(ran[-1]) if ran else None)
        runs.append(sigs)
    kept, seen, other_n = [], set(), {}
    for p in all_pairs:
        if p['covers_fault']:
            kept.append(p)
            continue
        k = (p['test'], p['start']['cls'], p['start']['line'], p['end']['cls'], p['end']['line'], len(p['path']))
        if k in seen or other_n.get(p['test'], 0) >= MAX_OTHER:
            continue
        seen.add(k)
        other_n[p['test']] = other_n.get(p['test'], 0) + 1
        kept.append(p)
    with open(os.path.join(bdir, 'pairs.jsonl'), 'w') as fh:
        for p in kept:
            fh.write(json.dumps(p) + '\n')
    cov = [p for p in kept if p['covers_fault']]
    both = [p for p in cov if p['start']['printed'] and p['end']['printed']]
    meta = dict(project=project, issue=issue, summary=rec['summary'], fix_commit=sha,
                buggy_version=f'{sha[:10]} with {", ".join(rec["main"])} reverted to {rec.get("base") or sha[:10] + "^"}',
                jdk=rec['jdk'], module=module, tests=tests,
                # the fix's own files (a class path may exist in several modules)
                faulty_lines=sorted(f'{next((f for f in rec["main"] if f.endswith("/" + c + ".java")), c + ".java")}:{l}'
                                    for c, l in faults),
                covering_pairs=len(cov), shortest_covering_pair=min((p['path_lines'] for p in cov), default=None),
                pairs_exported=len(kept),
                covering_pairs_printed=len(both),
                shortest_covering_pair_printed=min((p['path_lines'] for p in both), default=None),
                # stable = the covering pairs repeat in both runs; it is also the gate every later count uses, so a
                # bug whose fix test does not pass again on the fixed version, or that has no covering pair under
                # the stricter rules of pairs_of, is not stable
                stable=(stable(runs[0], runs[1]) if len(runs) > 1 else bool(os.environ.get('STABLE_FROM')))
                       and fixed_rerun == 'pass' and bool(cov)
                       and all(v['status'] == 'fail' for v in threads_n.values()),   # a flaky test may pass when traced
                runs=threads_n,
                fixed_rerun=fixed_rerun,
                whole_class_run=any((v['tests_run'] or 0) > 1 for v in threads_n.values()),
                alignment='single thread' if all(v['log_threads'] <= 1 for v in threads_n.values())
                          else 'several threads (approximate)')
    if log_too_large:
        meta['log_too_large'] = True
    json.dump(meta, open(os.path.join(bdir, 'meta.json'), 'w'), indent=1)
    return meta


def main():
    out_dir, agent_jar, work, workers = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    out_dir, agent_jar, work = map(os.path.abspath, (out_dir, agent_jar, work))
    repos = dict(a.split('=', 1) for a in sys.argv[5:])
    bugs = [b for b in usable_bugs() if b['project'] in repos]
    if os.environ.get('STABLE_FROM'):  # single re-export of the bugs that passed the stability check
        prev = {}
        for l in open(os.environ['STABLE_FROM']):
            m = json.loads(l)
            prev[(m['project'], m['issue'])] = m.get('stable')
        bugs = [b for b in bugs if prev.get((b['project'], b['issue']))]
    if os.environ.get('ONLY'):  # comma-separated issue keys, for testing
        bugs = [b for b in bugs if b['issue'] in os.environ['ONLY'].split(',')]
    pl.TRACE_LIMIT_BYTES, pl.TRACED_TIMEOUT = 10 * 1024 ** 3, 1800   # export may need bigger traces
    # logging is configured through JVM options (logging_props); the pipeline's per-project set-up adds a
    # Maven -Djava.util.logging.config.file that surefire forwards to the test JVM and would override ours
    for p in list(pl.PROJECTS) + ['tika', 'maven', 'gb-metamodel', 'struts', 'fop', 'httpclient', 'wss4j',
                                  'shiro', 'santuario']:
        pl.PROJECTS[p] = lambda mod_dir: []
    done = set()
    idx = os.path.join(out_dir, 'index.jsonl')
    if os.path.exists(idx):
        last = {}
        for l in open(idx):
            m = json.loads(l)
            last[(m['project'], m['issue'])] = m
        retry = os.environ.get('RETRY_UNSTABLE')
        # retrying only helps when the two runs disagreed, not when the fixed rerun failed or nothing covers the fault
        done = {k for k, m in last.items() if m.get('stable') or not retry
                or m.get('fixed_rerun', 'pass') != 'pass' or not m.get('covering_pairs', 1)}
    if os.environ.get('FORCE') and os.environ.get('ONLY'):   # re-export the listed bugs whatever the index says
        done = set()
    bugs = [b for b in bugs if (b['project'], b['issue']) not in done]
    pools = {}
    for p in {b['project'] for b in bugs}:
        q = Queue()
        for i in range(workers):
            wt = os.path.join(work, f'{p}_x{i}')
            if not os.path.isdir(wt):
                subprocess.run(['git', '-C', repos[p], 'worktree', 'add', '-q', '-f', '--detach', wt, 'HEAD'], check=True)
            q.put(wt)
        pools[p] = q

    def job(b):
        wt = pools[b['project']].get()
        try:
            try:
                m = export(b, wt, out_dir, agent_jar, repos[b['project']])
            except Exception as e:
                import traceback
                m = dict(project=b['project'], issue=b['issue'], error=repr(e), trace=traceback.format_exc()[-600:])
            with open(idx, 'a') as fh:
                fh.write(json.dumps(m) + '\n')
            print(m['issue'], m.get('shortest_covering_pair'), 'stable' if m.get('stable') else 'UNSTABLE', m.get('error', ''), flush=True)
        finally:
            pools[b['project']].put(wt)

    print(len(bugs), 'bugs to export', flush=True)
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(job, bugs))


if __name__ == '__main__':
    main()
