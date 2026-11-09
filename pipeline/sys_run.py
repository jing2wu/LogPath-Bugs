"""Run pipeline.py over every sampled project of the systematic selection, a few projects at a time.
Results go to results/pipeline/<project>_pipeline.jsonl (projects already run under an older name keep
that name, so their finished candidates are skipped).  A project's worktrees are removed when it is done.
Before each project starts, the script waits while free disk space is below MIN_FREE_GB, because a full
disk makes builds fail and would be recorded as non-reproducible candidates (see HANDOFF.md, pitfall 6).

usage: python3 -I sys_run.py <selected.tsv> <samples dir> [projects in parallel] [workers per project]"""
import os, shutil, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SCREENING = os.path.dirname(HERE)
WORK = os.environ.get('LRB_WORK', os.path.join(os.path.dirname(SCREENING), 'workspace'))
REPOS, RWORK = os.path.join(WORK, 'repos'), os.path.join(WORK, 'rwork')
OUT = os.environ.get('LRB_PIPELINE_OUT', os.path.join(SCREENING, 'results', 'pipeline'))   # GitHub version: results/github_java/pipeline
JAR = os.environ.get('LRB_SELOGGER_JAR', os.path.join(SCREENING, 'tools', 'selogger-0.6.0-asm9.jar'))   # GitHub run: selogger-0.6.0-asm98.jar
MIN_FREE_GB = 8
# apache repo name -> (pipeline project name, clone directory) where they differ from the repo name
ALIAS = {'velocity-engine': ('velocity', 'velocity-engine'), 'xmlgraphics-fop': ('fop', 'fop'),
         'ws-wss4j': ('wss4j', 'wss4j'), 'santuario-xml-security-java': ('santuario', 'santuario'),
         'logging-log4j2': ('log4j2', 'log4j2')}

sel, sdir = sys.argv[1], sys.argv[2]
lanes = int(sys.argv[3]) if len(sys.argv) > 3 else 3
workers = int(sys.argv[4]) if len(sys.argv) > 4 else 3
lock = threading.Lock()


def free_gb():
    return shutil.disk_usage(WORK).free / 1024 ** 3


def run(repo):
    project, clone = ALIAS.get(repo, (repo, repo))
    sample = os.path.join(sdir, f'{repo}_sample.json')
    while free_gb() < MIN_FREE_GB:
        print(f'{repo}: waiting, only {free_gb():.0f} GB free', flush=True)
        time.sleep(600)
    t0 = time.time()
    with open(os.path.join(OUT, f'{project}_run.out'), 'a') as log:
        subprocess.run([sys.executable, '-I', os.path.join(HERE, 'pipeline.py'), project, os.path.join(REPOS, clone),
                        sample, RWORK, OUT, JAR, str(workers)], stdout=log, stderr=subprocess.STDOUT)
    with lock:  # git worktree bookkeeping is per repository, but keep removals serialized anyway
        for i in range(workers):
            wt = os.path.join(RWORK, f'{project}_w{i}')
            if os.path.isdir(wt):
                subprocess.run(['git', '-C', os.path.join(REPOS, clone), 'worktree', 'remove', '--force', wt],
                               capture_output=True)
                shutil.rmtree(wt, ignore_errors=True)
    print(f'{repo} done in {(time.time() - t0) / 3600:.1f} h, {free_gb():.0f} GB free', flush=True)


repos = [l.split()[0] for l in open(sel)
         if os.path.exists(os.path.join(sdir, f'{l.split()[0]}_sample.json'))
         and open(os.path.join(sdir, f'{l.split()[0]}_sample.json')).read().strip() != '[]']
print(len(repos), 'projects', flush=True)
with ThreadPoolExecutor(lanes) as ex:
    list(ex.map(run, repos))
