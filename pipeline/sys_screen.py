"""Systematic screening: shallow-clone each repo, measure it with screen.measure, delete the clone.
usage: sys_screen.py [--pkg-aware] <repo list (one apache repo name, or owner/name, per line)> <out.jsonl> <scratch dir> [parallel]
--pkg-aware: see screen.measure (used for the GitHub version only).
Results are appended to out.jsonl; repos already in it are skipped, so the script can be rerun."""
import json, os, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from screen import measure

pkg_aware = '--pkg-aware' in sys.argv
args = [a for a in sys.argv[1:] if a != '--pkg-aware']
names, out, scratch = args[:3]
par = int(args[3]) if len(args) > 3 else 6
done = set()
if os.path.exists(out):
    done = {json.loads(l)['project'] for l in open(out)}
todo = [n.strip() for n in open(names) if n.strip() and n.strip() not in done]
os.makedirs(scratch, exist_ok=True)

def one(name):
    d = os.path.join(scratch, name.replace('/', '__'))
    slug = name if '/' in name else f'apache/{name}'
    shutil.rmtree(d, ignore_errors=True)
    try:
        r = subprocess.run(['git', 'clone', '-q', '--depth', '1', '--single-branch', '--no-tags',
                            f'https://github.com/{slug}.git', d],
                           capture_output=True, text=True, timeout=1800)
        if r.returncode:
            row = dict(project=name, error=r.stderr.strip()[-300:])
        else:
            sha = subprocess.run(['git', '-C', d, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
            row = dict(project=name, sha=sha, **measure(d, pkg_aware))
    except Exception as e:
        row = dict(project=name, error=repr(e)[:300])
    shutil.rmtree(d, ignore_errors=True)
    return row

with ThreadPoolExecutor(par) as ex, open(out, 'a') as fh:
    for i, f in enumerate(as_completed([ex.submit(one, n) for n in todo]), 1):
        row = f.result()
        fh.write(json.dumps(row) + '\n'); fh.flush()
        print(i, len(todo), row['project'], row.get('logs_per_kloc', row.get('error')), flush=True)
