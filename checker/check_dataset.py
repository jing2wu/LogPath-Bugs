r"""Consistency checks over an exported dataset, independent of the export code.

For every bug (default: only those that passed the automatic checks) it verifies against the git history and
the files written by export_dataset.py:
  files      meta.json, pairs.jsonl and one app log per test exist
  printed    every pair end marked printed has its text on some line of that test's app log, and for each
             covering pair with both ends printed the start text occurs on a line before some end-text line
  source     every path entry and both log statements name a file that exists in the buggy version, at a line
             number within the file (paths of classes without a source file, e.g. generated, are counted apart)
  endpoints  a path starts at its start log's line and ends at its end log's line
  fault      a pair flagged covers_fault has a faulty line strictly inside its path, and every faulty line is
             a line of the buggy version
  passed     a bug that passed has a covering pair with both logs printed, a fixed rerun that passed, and a
             first traced run that failed
The buggy version is the fix commit with the files listed in meta.buggy_version reverted to the parent.

usage: [LRB_REPOS=<dir of clones>] python3 -I check_dataset.py <dataset dir> [--all]   ->  prints a summary, writes <dataset dir>/check.jsonl"""
import json, os, re, subprocess, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPOS = os.environ.get('LRB_REPOS', os.path.join(os.path.dirname(os.path.dirname(HERE)), 'workspace', 'repos'))   # clones named owner__name
CLONE = {'velocity': 'velocity-engine'}


class Git:
    """git cat-file --batch over one repository, with a cache of line counts."""
    def __init__(self, repo):
        self.p = subprocess.Popen(['git', '-C', repo, 'cat-file', '--batch'], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)
        self.cache = {}

    def lines(self, rev, path):
        key = (rev, path)
        if key not in self.cache:
            self.p.stdin.write(f'{rev}:{path}\n'.encode())
            self.p.stdin.flush()
            head = self.p.stdout.readline().decode().split()
            if len(head) < 3 or head[1] == 'missing':
                self.cache[key] = None
            else:
                body = self.p.stdout.read(int(head[2]) + 1)[:-1]
                # Java line terminators: \n, \r\n and \r (generated OpenWire marshallers in ActiveMQ use \r only)
                self.cache[key] = re.split(r'\r\n|\r|\n', body.decode('utf-8', 'replace'))
        return self.cache[key]

    def close(self):
        self.p.stdin.close()
        self.p.wait()


def check(bdir, meta, git):
    problems, stats = [], collections.Counter()
    sha = meta['fix_commit']
    m = re.search(r' with (.*) reverted to ', meta['buggy_version'])
    reverted = set(m.group(1).split(', ')) if m else set()
    src = lambda f: git.lines(f'{sha}^' if f in reverted else sha, f)
    logs = {}
    for t in meta['tests']:
        p = os.path.join(bdir, f'app_{t.replace("#", ".")}.log')
        if not os.path.exists(p):
            problems.append(f'files: no app log for {t}')
        logs[t] = open(p, errors='ignore').read().splitlines() if os.path.exists(p) else []
    pairs = [json.loads(l) for l in open(os.path.join(bdir, 'pairs.jsonl'))]
    faulty = set()
    for fl in meta['faulty_lines']:
        f, l = fl.rsplit(':', 1)
        faulty.add((f, int(l)))
        lines = src(f)
        if lines is None or not 1 <= int(l) <= len(lines):
            problems.append(f'fault: {fl} is not a line of the buggy version')
    ok_cover = False
    for i, p in enumerate(pairs):
        log = logs.get(p['test'], [])
        where = {}
        for end in ('start', 'end'):
            e = p[end]
            if e['printed']:
                hits = [j for j, l in enumerate(log) if e['text'] in l]   # an empty message matches any line
                if not hits:
                    problems.append(f'printed: pair {i} {end} text not in the app log: {e["text"][:60]!r}')
                where[end] = hits
        if p['covers_fault'] and len(where) == 2 and where['start'] and where['end']:
            if min(where['start']) > max(where['end']):
                problems.append(f'printed: pair {i} start text only after end text in the app log')
        for f, l in [(p['start']['file'], p['start']['line']), (p['end']['file'], p['end']['line'])] + \
                [tuple(x) for x in p['path']]:
            stats['path_entries'] += 1
            lines = src(f)
            if lines is None:
                if not re.search(r'(^|/)src/', f):
                    # export falls back to <class path>.java for classes without a source file in the
                    # repository: generated (Thrift, JavaCC, Jute) or in a directory named test
                    stats['no_source_entries'] += 1
                else:
                    problems.append(f'source: pair {i}: {f} not in the buggy version')
            elif not 1 <= l <= len(lines):
                problems.append(f'source: pair {i}: {f}:{l} beyond the file ({len(lines)} lines)')
            elif not lines[l - 1].strip():
                stats['blank_line_entries'] += 1
        path = [tuple(x) for x in p['path']]
        if path and (path[0] != (p['start']['file'], p['start']['line'])
                     or path[-1] != (p['end']['file'], p['end']['line'])):
            # a path is duplicate-free, so an end log whose line also ran earlier keeps its first position
            if path[0] != (p['start']['file'], p['start']['line']):
                problems.append(f'endpoints: pair {i} path does not start at the start log')
            elif (p['end']['file'], p['end']['line']) not in path:
                problems.append(f'endpoints: pair {i} path does not contain the end log')
        if p['covers_fault']:
            # the two log statements do not count; the end log keeps its first position when its line also
            # ran earlier in the pair (a loop), so the last entry is then an ordinary line
            end_at = len(path) - 1 if path and path[-1] == (p['end']['file'], p['end']['line']) else len(path)
            inner = set(path[1:end_at])
            if not inner & faulty:
                problems.append(f'fault: pair {i} flagged covering but no faulty line inside its path')
            if p['start']['printed'] and p['end']['printed']:
                ok_cover = True
    passed = bool(meta.get('stable') and meta.get('covering_pairs_printed'))
    if passed:
        if not ok_cover:
            problems.append('passed: no covering pair with both logs printed')
        if meta.get('fixed_rerun') != 'pass':
            problems.append('passed: fixed rerun did not pass')
        if any(v.get('status') != 'fail' for v in meta.get('runs', {}).values()):
            problems.append('passed: a first traced run did not fail')
    stats['pairs'] = len(pairs)
    return problems, stats


def main():
    ds = sys.argv[1]
    every = '--all' in sys.argv
    metas = collections.defaultdict(list)
    for l in open(os.path.join(ds, 'index.jsonl')):
        m = json.loads(l)
        if m.get('error') or not m.get('covering_pairs'):
            continue
        if every or (m.get('stable') and m.get('covering_pairs_printed')):
            metas[m['project']].append(m)
    out, kinds, tot, bad = [], collections.Counter(), collections.Counter(), 0
    for proj, ms in sorted(metas.items()):
        git = Git(os.path.join(REPOS, CLONE.get(proj, proj)))
        for m in ms:
            bdir = os.path.join(ds, proj, m['issue'])
            if not os.path.exists(os.path.join(bdir, 'pairs.jsonl')):
                probs, st = ['files: no pairs.jsonl'], collections.Counter()
            else:
                probs, st = check(bdir, m, git)
            tot.update(st)
            bad += bool(probs)
            for p in probs:
                kinds[p.split(':')[0]] += 1
            out.append(dict(project=proj, issue=m['issue'], problems=probs, **st))
        git.close()
    with open(os.path.join(ds, 'check.jsonl'), 'w') as fh:
        for r in out:
            fh.write(json.dumps(r) + '\n')
    print(f'{len(out)} bugs checked, {bad} with problems; problems by kind: {dict(kinds)}')
    print(f'path entries {tot["path_entries"]}, without a source file {tot["no_source_entries"]}, '
          f'on blank lines {tot["blank_line_entries"]}')
    for r in out:
        if r['problems']:
            print(r['issue'], '|', ' ; '.join(r['problems'][:3]), f'(+{len(r["problems"]) - 3})' if len(r['problems']) > 3 else '')


if __name__ == '__main__':
    main()
