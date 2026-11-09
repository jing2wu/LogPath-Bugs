"""Summarise a SELogger omni trace (weave=EXEC+CALL+LINE) as log pairs.

Only production classes count (classes not loaded from */test-classes/).  A log event is a CALL to
a logging method (Log4j2 Logger, commons-logging Log, JUL Logger).  Following the AgenTrace setup,
two consecutive log events on the same thread form a pair; its ground-truth path is the ordered,
duplicate-free list of (class, line) executed between them, both log lines included.

usage: python3 -I analyse_trace.py <trace dir>...   (each dir holds selogger/ and meta.json)
prints one JSON summary per trace dir and writes pairs.json next to it
"""
import csv, glob, json, os, re, statistics, sys

LOG_OWNERS = {'org.apache.logging.log4j.Logger', 'org.apache.commons.logging.Log', 'java.util.logging.Logger',
              'org.slf4j.Logger', 'org.apache.log4j.Logger', 'org.apache.log4j.Category',
              'org.apache.velocity.runtime.log.Log', 'org.codehaus.plexus.logging.Logger',
              'org.apache.maven.plugin.logging.Log'}
LOG_NAMES = {'trace', 'debug', 'info', 'warn', 'error', 'fatal', 'log',
             'severe', 'warning', 'config', 'fine', 'finer', 'finest'}


def attrs(s):
    out = {}
    for kv in s.strip('"').split(','):
        if '=' in kv:
            k, v = kv.split('=', 1)
            out[k] = v
    return out


def load_tokens(tdir):
    """Per-thread event tokens: ('L'|'G', class, method, line) for production code."""
    sel = os.path.join(tdir, 'selogger')
    prod_classes = set()
    with open(os.path.join(sel, 'classes.txt'), newline='') as fh:
        for row in csv.DictReader(fh):
            if '/test-classes/' not in row['LoadedFrom'] and not re.search(r'/build/classes/\w+/test/', row['LoadedFrom']):
                prod_classes.add(row['ClassID'])
    info = {}
    with open(os.path.join(sel, 'dataids.txt'), newline='') as fh:
        for row in csv.DictReader(fh):
            if row['ClassID'] not in prod_classes:
                continue
            et = row['EventType']
            if et == 'LINE_NUMBER':
                info[row['DataID']] = ('L', row['ClassName'], row['MethodName'], int(row['Line']))
            elif et == 'CALL':
                a = attrs(row['Attributes'])
                if a.get('owner') in LOG_OWNERS and a.get('name') in LOG_NAMES:
                    info[row['DataID']] = ('G', row['ClassName'], row['MethodName'], int(row['Line']))
    threads = {}          # thread -> list of tokens
    n_lines = 0
    for f in sorted(glob.glob(os.path.join(sel, 'log-*.txt'))):
        with open(f) as fh:
            next(fh)
            for line in fh:
                parts = line.split(',', 3)
                tok = info.get(parts[1])
                if tok is None:
                    continue
                threads.setdefault(parts[2], []).append(tok)
                n_lines += tok[0] == 'L'
    return threads, n_lines


def analyse(tdir):
    threads, n_lines = load_tokens(tdir)
    pairs, log_events, log_sites = [], 0, set()
    for tid, toks in threads.items():
        last = None          # index of last log token
        for i, t in enumerate(toks):
            if t[0] != 'G':
                continue
            log_events += 1
            log_sites.add(t[1:])
            if last is not None:
                seg = [toks[last]] + [x for x in toks[last + 1:i] if x[0] == 'L'] + [t]
                path, seen = [], set()
                for x in seg:
                    key = (x[1], x[3])
                    if key not in seen:
                        seen.add(key)
                        path.append(x)
                pairs.append(dict(thread=tid, start=f'{toks[last][1]}:{toks[last][3]}', end=f'{t[1]}:{t[3]}',
                                  lines=len(path), methods=len({(x[1], x[2]) for x in path}),
                                  classes=len({x[1] for x in path}), same_site=toks[last][1:] == t[1:]))
            last = i
    json.dump(pairs, open(os.path.join(tdir, 'pairs.json'), 'w'), indent=0)
    meta = json.load(open(os.path.join(tdir, 'meta.json')))
    L = [p['lines'] for p in pairs]
    distinct = [p for p in pairs if not p['same_site']]
    Ld = [p['lines'] for p in distinct]
    return dict(issue=meta['issue'], sha=meta['sha'], test=meta['test'], status=meta['status'],
                prod_threads=len(threads), trace_line_events=n_lines,
                distinct_lines=len({(x[1], x[3]) for t in threads.values() for x in t if x[0] == 'L'}),
                log_events=log_events, log_statements=len(log_sites), pairs=len(pairs),
                pairs_between_different_statements=len(distinct),
                path_lines_median=statistics.median(L) if L else None, path_lines_max=max(L) if L else None,
                distinct_pairs_path_median=statistics.median(Ld) if Ld else None,
                distinct_pairs_path_max=max(Ld) if Ld else None,
                distinct_pairs_le20=sum(x <= 20 for x in Ld),
                distinct_pairs_single_method=sum(p['methods'] == 1 for p in distinct))


if __name__ == '__main__':
    for d in sys.argv[1:]:
        print(json.dumps(analyse(d)), flush=True)
