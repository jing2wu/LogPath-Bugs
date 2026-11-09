"""GitHub Java version of export_dataset.py (same export and checks, see that file).

Differences: the usable bugs come from the GitHub pipeline results (results/github_java/pipeline*/, the
record each bug was last run in, as listed in report_github_java/paper_gh.json), the pipeline runs in its
GitHub mode (LRB_JDK_PROPS, LRB_FORCE_UPDATE, JDK 25), and each worker builds in a shared clone instead
of a git worktree (some Gradle/JGit plugins cannot read a worktree).  Gradle projects are skipped unless
GH_GRADLE=1 (export_dataset.py has no Gradle-specific log handling yet).

usage: python3 -I gh_export.py <out dir> <workers> <owner__repo>...
  env ONLY=GH-123,GH-456  only these issues;  FORCE=1 with ONLY re-exports them;  KEEP=1 keeps raw traces
Output: <out>/<owner__repo>/<issue>/{meta.json,pairs.jsonl,app_*.log} and <out>/index.jsonl (resumable)."""
import glob, json, os, shutil, subprocess, sys

os.environ.setdefault('LRB_JDK_PROPS', '1')      # GitHub mode of pipeline.py (read at import)
os.environ.setdefault('LRB_FORCE_UPDATE', '1')   # -U and unit tests forced on, as in the last pipeline batches
HERE = os.path.dirname(os.path.abspath(__file__))
SCREENING = os.path.dirname(HERE)
WORK = os.environ.get('LRB_WORK', os.path.join(os.path.dirname(SCREENING), 'workspace'))
REPOS, RWORK = os.path.join(WORK, 'repos'), os.path.join(WORK, 'rwork')
G = os.path.join(SCREENING, 'results', 'github_java')
JAR = os.environ.get('LRB_SELOGGER_JAR', os.path.join(SCREENING, 'tools', 'selogger-0.6.0-asm98.jar'))
PAPER = os.path.join(SCREENING, 'report_github_java', 'paper_gh.json')

sys.path.insert(0, HERE)
import export_dataset as e  # noqa: E402


def usable_bugs_github():
    """The final usable set of the GitHub report: one record per bug, read from the pipeline file it was last
    run in (the report lets later batches supersede earlier runs of the same bug)."""
    want = json.load(open(PAPER))['usable_bugs']
    best = {}
    for b in want:
        if b['build'] != 'Maven' and not os.environ.get('GH_GRADLE'):
            continue
        project = b['project'].replace('/', '__')
        f = os.path.join(G, b['dir'], f'{project}_pipeline.jsonl')
        recs = [json.loads(l) for l in open(f) if l.strip()]
        rec = next((r for r in recs if r.get('sha') == b['sha'] and r.get('result') == 'usable'), None)
        if rec is None:
            print(f'{project} {b["issue"]} {b["sha"]}: usable record not found in {b["dir"]}', file=sys.stderr)
            continue
        cov = [t for t in rec.get('traces', []) if t.get('covering_pairs') and t['status'] == 'fail']
        if not cov:
            continue
        r = dict(rec, project=project, issue=b['issue'], covering_min_lines=min(t['covering_min_lines'] for t in cov))
        k = (project, b['issue'])   # one fix commit per issue: the one with the shortest covering pair (as for Apache)
        if k not in best or r['covering_min_lines'] < best[k]['covering_min_lines']:
            best[k] = r
    return sorted(best.values(), key=lambda r: r['covering_min_lines'])


e.usable_bugs = usable_bugs_github

_run_tests = e.pl.run_tests


def run_tests_gh(project, wt, module, tests, jdk, agent=None, mvn_props=()):
    # Gradle projects keep dependency jars under ~/.gradle, not ~/.m2: exclude those from tracing, as pipeline.py does
    if agent and e.pl.is_gradle(wt):
        agent = agent.replace('exlocation=.m2', 'exlocation=.gradle')
    return _run_tests(project, wt, module, tests, jdk, agent, mvn_props)


e.pl.run_tests = run_tests_gh


def main():
    out_dir, workers, projects = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
    args = [f'{p}={os.path.join(REPOS, p)}' for p in projects]
    todo = {b['project'] for b in usable_bugs_github() if b['project'] in projects}
    clones = []
    for p in todo:   # shared clones as the worker directories (export_dataset.main would add git worktrees)
        repo = os.path.join(REPOS, p)
        head = subprocess.run(['git', '-C', repo, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        for i in range(workers):
            wt = os.path.join(RWORK, f'{p}_x{i}')
            if not os.path.isdir(wt):
                subprocess.run(['git', 'clone', '-q', '--shared', '--no-checkout', repo, wt], check=True)
                subprocess.run(['git', '-C', wt, 'checkout', '-q', '--detach', head], check=True)
            clones.append(wt)
    sys.argv = ['export_dataset.py', out_dir, JAR, RWORK, str(workers), *args]
    try:
        e.main()
    finally:
        for wt in clones:
            shutil.rmtree(wt, ignore_errors=True)


if __name__ == '__main__':
    main()
