"""Where do the faulty lines run, relative to the logs?

Faulty lines = lines of the buggy version that the fix deletes or modifies; for a hunk that only
adds code, the buggy lines right before and after the insertion point.  For every execution of a
faulty line in a trace we report whether it falls inside a log pair (and that pair's path size),
before the first log (prefix) or after the last log (suffix) of its thread.

usage: python3 -I fault_coverage.py <pdfbox repo> <trace dir>...
"""
import json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyse_trace import load_tokens  # noqa: E402


# lines that never execute: blank, package/import, comments, a bare annotation
NON_EXECUTABLE = re.compile(r'^\s*(?:import\s|package\s|//|/\*|\*|@\w+(?:\(.*\))?\s*$|$)')


def non_executable(line):
    return bool(NON_EXECUTABLE.match(line))


def fault_lines(repo, sha, files, base=None):
    """Faulty lines of the buggy version (numbered as in sha^): the lines a hunk deletes or modifies, or for a
    pure insertion the lines just before and after it, keeping only lines that can execute."""
    out = set()
    base = base or f'{sha}^'
    for f in files:
        m = re.search(r'(?:^|/)src/main/java/(.*)\.java$', f) or re.search(r'(?:^|/)((?:org|com|net|io)/.*)\.java$', f)
        if m is None:
            # GitHub projects: a test file in a custom source set (reactor-netty src/http3Test/java) is not a fault
            # location; any other source set is taken as production code (any package name, e.g. ai.*, de.*)
            if re.search(r'(?:^|/)src/[^/]*[Tt]est[^/]*/', f):
                continue
            m = re.search(r'(?:^|/)src/[^/]+/java/(.*)\.java$', f)
            if m is None:
                continue
        cls = m.group(1)  # GitHub projects also use packages such as ai.*, de.*, fr.*
        diff = subprocess.run(['git', '-C', repo, 'diff', '-U0', base, sha, '--', f],
                              capture_output=True, text=True).stdout
        src = subprocess.run(['git', '-C', repo, 'show', f'{base}:{f}'],
                             capture_output=True, text=True, errors='ignore').stdout.split('\n')
        for m in re.finditer(r'^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@', diff, re.M):
            start, n = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
            lines = {start, start + 1} if n == 0 else range(start, start + n)  # n == 0: insertion after `start`
            out.update((cls, l) for l in lines if 0 < l <= len(src) and not non_executable(src[l - 1]))
    return out


def coverage(tdir, faults):
    threads, _ = load_tokens(tdir)
    res = dict(executions=0, in_pair=0, prefix=0, suffix=0, no_logs=0, covering_pairs=[])
    for toks in threads.values():
        logs = [i for i, t in enumerate(toks) if t[0] == 'G']
        seen_pairs = {}
        for i, t in enumerate(toks):
            if t[0] != 'L' or (t[1].split('$')[0], t[3]) not in faults:
                continue
            res['executions'] += 1
            if not logs:
                res['no_logs'] += 1
            elif i < logs[0]:
                res['prefix'] += 1
            elif i > logs[-1]:
                res['suffix'] += 1
            else:
                k = max(j for j in logs if j < i)
                e = min(j for j in logs if j > i)
                if (t[1], t[3]) in ((toks[k][1], toks[k][3]), (toks[e][1], toks[e][3])):
                    continue  # the line of a log statement itself (e.g. a fix that only edits the message)
                res['in_pair'] += 1
                if k not in seen_pairs:
                    path = {(x[1], x[3]) for x in toks[k:e + 1] if x[0] == 'L'}
                    seen_pairs[k] = dict(start=f'{toks[k][1]}:{toks[k][3]}', end=f'{toks[e][1]}:{toks[e][3]}',
                                         lines=len(path), log_index=logs.index(k), logs_total=len(logs))
        res['covering_pairs'] += list(seen_pairs.values())
    return res


if __name__ == '__main__':
    repo = sys.argv[1]
    for d in sys.argv[2:]:
        meta = json.load(open(os.path.join(d, 'meta.json')))
        rec = next(json.loads(l) for l in open(os.path.join(os.path.dirname(__file__), '../results/pdfbox_repro.jsonl'))
                   if json.loads(l)['sha'] == meta['sha'])
        faults = fault_lines(repo, subprocess.run(['git', '-C', repo, 'rev-parse', meta['sha']],
                                                  capture_output=True, text=True).stdout.strip(), rec['main'])
        r = coverage(d, faults)
        r.update(issue=meta['issue'], sha=meta['sha'], test=meta['test'], fault_lines=sorted(f'{c}:{l}' for c, l in faults))
        print(json.dumps(r), flush=True)
