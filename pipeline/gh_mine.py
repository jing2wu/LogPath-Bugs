"""Step 4 of the GitHub Java dataset: find the fix commit of each bug and draw a per-project sample.
GitHub counterpart of sys_clone_mine.sh + mine.py + jira_label.py + sys_sample.py (Apache used JIRA keys in commit
messages; here a bug is an issue with a bug label, closed by a merged pull request).

usage: python3 -I scripts/gh_mine.py <projects.txt (owner/name per line)> <out dir> [N=10] [parallel=4]
Per project:
 1. GraphQL: closed issues with one of the project's bug labels (from results/github_java/api_screen.jsonl),
    created on/after SINCE, and the merged pull requests that closed them (merged on/after SINCE).
 2. Full clone into workspace/repos/<owner>__<name> (kept for pipeline.py); fix commits outside the cloned branches
    are fetched by SHA.
 3. Fix commit of each pull request = GitHub's merge commit. pipeline.py compares <sha> with <sha>^ (the first
    parent), so <sha>^..<sha> must hold the whole pull request (its changed files equal the pull request's files):
      squash merge, single-commit pull request merged by rebase, or a merge commit (first parent = base branch)
    a multi-commit pull request merged by rebase (the merge commit is only its last commit) is skipped.
 4. Same filters as the Apache round 2 (mine.py 3 80 1): 1-3 production .java files, at least one test file,
    <= 80 production lines changed, >= 1 logging call and no thread construct in the changed production files;
    and the Maven check of sys_sample.py (root pom.xml and a pom.xml in every changed test module).
 5. The eligible bugs are shuffled with SEED and stored in that order (<p>_bugs.json); the first N are the
    sample (<p>_sample.json), in the candidate format pipeline.py reads (the issue sits in the 'jira' field
    as GH-<number> with type Bug). <p> = owner__name, which is also the pipeline project name.
Writes <out dir>/candidates/, <out dir>/samples/, <out dir>/selected.txt (projects with >= 1 bug, for sys_run.py)
and appends one line per project to <out dir>/summary.jsonl; projects already in it are skipped."""
import json, os, random, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SCREENING = os.path.dirname(HERE)
REPOS = os.path.join(os.environ.get('LRB_WORK', os.path.join(os.path.dirname(SCREENING), 'workspace')), 'repos')
API_SCREEN = os.path.join(SCREENING, 'results', 'github_java', 'api_screen.jsonl')
SINCE = '2021-10-22'
GRADLE = bool(os.environ.get('LRB_GRADLE'))   # also accept Gradle builds (new standard, 2026-10-23)
SEED = 20261009                       # same seed as sys_sample.py
MAX_MAIN, MAX_CHURN, MIN_LOGS = 3, 80, 1
# regexes copied from mine.py so the filters match the Apache dataset
LOG = re.compile(r'\b(?:\w*log\w*|LOG\w*)\s*\.\s*(trace|debug|info|warn|error|fatal)\s*\(', re.I)
THR = re.compile(r'new\s+Thread\s*\(|\bExecutors\.|\bExecutorService\b|\bCompletableFuture\b|\.parallelStream\(')
REPORT_LOG = re.compile(r'(WARN|ERROR|DEBUG|INFO)\b|Exception')   # as jira_label.py

lst, odir = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 10
PAR = int(sys.argv[4]) if len(sys.argv) > 4 else 4
CDIR, SDIR = os.path.join(odir, 'candidates'), os.path.join(odir, 'samples')
for d in (CDIR, SDIR, REPOS):
    os.makedirs(d, exist_ok=True)
SUMMARY = os.path.join(odir, 'summary.jsonl')
labels_of = {d['repo']: d.get('bug_labels', []) for d in map(json.loads, open(API_SCREEN))}

Q = '''query($o:String!, $n:String!, $labels:[String!], $after:String) { repository(owner:$o, name:$n) {
  issues(first:25, after:$after, states:CLOSED, labels:$labels, orderBy:{field:CREATED_AT, direction:DESC}) {
    pageInfo { hasNextPage endCursor }
    nodes { number title body createdAt
      closedByPullRequestsReferences(first:5, includeClosedPrs:false) { nodes {
        number merged mergedAt changedFiles mergeCommit { oid }
        files(first:100) { nodes { path } } } } } } } }'''


def gql(repo, after):
    o, n = repo.split('/')
    args = ['gh', 'api', 'graphql', '-f', f'query={Q}', '-f', f'o={o}', '-f', f'n={n}']
    for l in labels_of.get(repo, []):
        args += ['-f', f'labels[]={l}']
    if after:
        args += ['-f', f'after={after}']
    for i in range(8):
        r = subprocess.run(args, capture_output=True, text=True)
        try:
            res = json.loads(r.stdout)
            if res.get('data') and res['data'].get('repository'):
                return res['data']['repository']['issues']
        except ValueError:
            pass
        time.sleep(65 if 'rate' in (r.stdout + r.stderr).lower() else 10 * (i + 1))
    raise RuntimeError('GitHub API keeps failing: ' + (r.stderr or r.stdout)[:200])


def git(repo, *a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True, errors='ignore').stdout


def fixes(repo):
    """(issue, pull request) pairs: bug issue created on/after SINCE, closed by a PR merged on/after SINCE."""
    out, after = [], None
    while True:
        page = gql(repo, after)
        for it in page['nodes']:
            if it['createdAt'][:10] < SINCE:
                return out
            for pr in (it['closedByPullRequestsReferences'] or {}).get('nodes') or []:
                if pr and pr['merged'] and (pr['mergedAt'] or '')[:10] >= SINCE and pr['mergeCommit']:
                    out.append((it, pr))
        if not page['pageInfo']['hasNextPage']:
            return out
        after = page['pageInfo']['endCursor']


def fix_commit(clone, pr):
    """The single commit holding the whole pull request, or (None, reason)."""
    sha = pr['mergeCommit']['oid']
    if not git(clone, 'cat-file', '-t', sha).strip():
        # merged into another branch (release branch, deleted branch): GitHub serves the commit by its SHA
        git(clone, 'fetch', '-q', 'origin', sha)
        if not git(clone, 'cat-file', '-t', sha).strip():
            return None, 'commit not fetchable'
    pr_files = {f['path'] for f in ((pr['files'] or {}).get('nodes') or [])}  # files can be null on huge PRs
    if pr['changedFiles'] > 100 or not pr_files:
        return None, 'PR file list incomplete'
    files = set(git(clone, 'diff', '--name-only', f'{sha}^', sha).split('\n')) - {''}
    if files != pr_files:
        return None, 'multi-commit PR (rebase)'
    return sha, None


def check(clone, sha):
    """mine.py filters + sys_sample.py Maven check; returns the candidate fields or (None, reason)."""
    main, tests, churn = [], [], 0
    for l in git(clone, 'diff', '--numstat', f'{sha}^', sha).splitlines():
        p = l.split('\t')
        if len(p) != 3 or not p[2].endswith('.java'):
            continue
        is_test = '/test/' in p[2]
        (tests if is_test else main).append(p[2])
        if not is_test and p[0].isdigit():
            churn += int(p[0]) + int(p[1])
    if not 1 <= len(main) <= MAX_MAIN:
        return None, f'{len(main)} production files'
    if not tests:
        return None, 'no test change'
    if churn > MAX_CHURN:
        return None, 'more than 80 lines'
    logs = thr = 0
    for f in main:
        src = git(clone, 'show', f'{sha}:{f}')
        logs += len(LOG.findall(src)); thr += len(THR.findall(src))
    if logs < MIN_LOGS:
        return None, 'no logging call'
    if thr:
        return None, 'thread construct'
    has = lambda p: subprocess.run(['git', '-C', clone, 'cat-file', '-e', f'{sha}:{p}'], capture_output=True).returncode == 0
    mods = {t.split('/src/test/')[0] for t in tests if '/src/test/' in t}
    maven = has('pom.xml') and all(has(m + '/pom.xml') for m in mods)
    gradle = not has('pom.xml') and any(has(f) for f in ('build.gradle', 'build.gradle.kts', 'settings.gradle', 'settings.gradle.kts'))
    if not (maven or (GRADLE and gradle)):
        return None, 'not Maven at the fix' if not GRADLE else 'not Maven or Gradle at the fix'
    return dict(main=main, tests=tests, churn=churn, logs_in_changed_files=logs), None


def one(repo):
    p = repo.replace('/', '__')
    clone = os.path.join(REPOS, p)
    if not os.path.isdir(clone):
        r = subprocess.run(['git', 'clone', '-q', f'https://github.com/{repo}.git', clone], capture_output=True, text=True)
        if r.returncode:
            return dict(project=repo, error='clone failed: ' + r.stderr.strip()[-200:])
    pairs = fixes(repo)
    cands, reasons, seen = [], {}, set()
    for it, pr in pairs:
        sha, why = fix_commit(clone, pr)
        if sha and sha in seen:
            continue
        if sha:
            seen.add(sha)
            info, why = check(clone, sha)
        if why:
            reasons[why] = reasons.get(why, 0) + 1
            continue
        cands.append(dict(sha=sha[:10], date=git(clone, 'show', '-s', '--format=%ad', '--date=short', sha).strip(),
                          subject=git(clone, 'show', '-s', '--format=%s', sha).strip()[:110], **info,
                          pr=pr['number'],
                          jira={f'GH-{it["number"]}': dict(type='Bug', summary=it['title'][:200],
                                                           has_log_in_report=bool(REPORT_LOG.search(it['body'] or '')))}))
    json.dump(cands, open(os.path.join(CDIR, f'{p}_candidates.json'), 'w'), indent=1)
    random.Random(SEED).shuffle(cands)
    json.dump(cands, open(os.path.join(SDIR, f'{p}_bugs.json'), 'w'), indent=1)
    json.dump(cands[:N], open(os.path.join(SDIR, f'{p}_sample.json'), 'w'), indent=1)
    return dict(project=repo, fixed_issue_pr_pairs=len(pairs), eligible=len(cands), sample=min(N, len(cands)),
                dropped=reasons)


projects = [l.strip() for l in open(lst) if l.strip()]
done = {json.loads(l)['project'] for l in open(SUMMARY)} if os.path.exists(SUMMARY) else set()
todo = [r for r in projects if r not in done]
print(len(projects), 'projects,', len(todo), 'to do', flush=True)


def safe(repo):
    try:
        return one(repo)
    except Exception as e:
        return dict(project=repo, error=repr(e)[:300])


with ThreadPoolExecutor(PAR) as ex, open(SUMMARY, 'a') as fh:
    for i, row in enumerate(ex.map(safe, todo), 1):
        fh.write(json.dumps(row) + '\n'); fh.flush()
        print(i, len(todo), row['project'], row.get('eligible', row.get('error')), flush=True)
rows = [json.loads(l) for l in open(SUMMARY)]
with open(os.path.join(odir, 'selected.txt'), 'w') as fh:
    for r in rows:
        if r.get('eligible'):
            fh.write(r['project'].replace('/', '__') + '\n')
print('done', flush=True)
