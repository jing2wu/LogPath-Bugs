"""Turn one SELogger trace into log pairs, the same way the dataset export does, and print them.

usage: python3 trace_pairs.py <selogger dir> <worktree> <test Class#method> <fix sha> <buggy file>... [--base REV]

  selogger dir  the output=... directory given to the SELogger agent
  worktree      the checked-out repository (buggy version), used for fault lines and file names
  fix sha       the fix commit; faulty lines are the lines it deletes or changes in <base> (default <fix sha>^)
  buggy file    the production file(s) reverted to the buggy version (meta.json -> buggy_version)

Prints one line per pair: index, line numbers on the path, covers_fault, and which two printed messages
(1-based, in the order of the app log). Compare it with the bug's pairs.jsonl (same order).
Uses export_dataset.read_trace / pairs_of and fault_coverage.fault_lines unchanged (read-only).
"""
import glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'scripts'))
import export_dataset, fault_coverage  # noqa: E402

args = sys.argv[1:]
base = None
if '--base' in args:
    i = args.index('--base'); base = args[i + 1]; del args[i:i + 2]
sel, wt, test, sha, *files = args
faults = fault_coverage.fault_lines(wt, sha, files, base)
print('faulty lines:', ', '.join(f'{c.split("/")[-1]}:{l}' for c, l in sorted(faults)))

java = {}
for f in glob.glob(os.path.join(wt, '**', '*.java'), recursive=True):
    m = f.split('/src/main/java/')
    if len(m) == 2:
        java.setdefault(m[1][:-5], []).append(os.path.relpath(f, wt))
src_of = lambda cls: (java.get(cls.split('$')[0]) or [cls.split('$')[0] + '.java'])[0]

threads, inside, inlog = export_dataset.read_trace(sel, test)
for i, p in enumerate(export_dataset.pairs_of(threads, faults, src_of, inside, inlog)):
    lines = ' '.join(str(l) for _, l in p['path'])
    print(f"{i}  log {p['start']['idx'] + 1} -> log {p['end']['idx'] + 1}  path [{lines}]  covers_fault={p['covers_fault']}")
