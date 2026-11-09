"""Recovery pass of gh_mine.py (2026-10-30): re-mines projects and keeps only the (issue, pull request) pairs that
gh_mine.py dropped for technical reasons, with the same bug filters (check()) as gh_mine.py:
  commit not fetchable      -> fetch the pull request head (refs/pull/N/head); fix = head, buggy = merge-base of the
                               head with the base branch; kept only if base..head changes exactly the PR's files
  multi-commit PR (rebase)  -> buggy = <merge commit>~k (k = the PR's commit count, first-parent line); kept only if
                               that range changes exactly the PR's files
  PR file list incomplete   -> GraphQL gave no file list although the PR has <= 100 files: take the files from git
                               and require their number to equal the PR's changedFiles
A PR with > 100 files stays dropped. Recovered candidates carry 'base' (the buggy revision; pipeline.py uses it
instead of <sha>^) and 'recovered' (how). Pairs gh_mine.py already accepted are not repeated.

usage: python3 -I scripts/gh_mine_recover.py <projects.txt> <out dir> [parallel=4]
Writes <out dir>/samples/<p>_bugs.json (recovered candidates shuffled with SEED) and _sample.json (all of them),
<out dir>/summary.jsonl and <out dir>/selected.txt."""
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
PAR = int(sys.argv[3]) if len(sys.argv) > 3 else 4
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
        number merged mergedAt changedFiles mergeCommit { oid } headRefOid baseRefName commits { totalCount }
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


def files_of(clone, a, b):
    return set(git(clone, 'diff', '--name-only', a, b).split('\n')) - {''}


def fix_commit(clone, pr):
    """(sha, base, how) of a pair gh_mine.py dropped for a technical reason, or (None, None, reason).
    how == 'orig' marks a pair gh_mine.py already accepted (not repeated here)."""
    sha = pr['mergeCommit']['oid']
    pr_files = {f['path'] for f in ((pr['files'] or {}).get('nodes') or [])}  # files can be null on huge PRs
    if not git(clone, 'cat-file', '-t', sha).strip():
        git(clone, 'fetch', '-q', 'origin', sha)
    if not git(clone, 'cat-file', '-t', sha).strip():
        # gh_mine.py: 'commit not fetchable' -> use the pull request head
        head, ref = pr.get('headRefOid'), f'refs/lrb/pr-{pr["number"]}'
        git(clone, 'fetch', '-q', 'origin', f'+refs/pull/{pr["number"]}/head:{ref}')
        if not head or not git(clone, 'cat-file', '-t', head).strip():
            return None, None, 'PR head not fetchable'
        tip = git(clone, 'rev-parse', '-q', '--verify', f'origin/{pr.get("baseRefName")}').strip() \
            or git(clone, 'rev-parse', 'origin/HEAD').strip()
        base = git(clone, 'merge-base', head, tip).strip()
        if not base or not pr_files or pr['changedFiles'] > 100 or files_of(clone, base, head) != pr_files:
            return None, None, 'PR head: files differ'
        return head, base, 'pr-head'
    if pr['changedFiles'] > 100:
        return None, None, 'PR file list incomplete'
    files = files_of(clone, f'{sha}^', sha)
    if not pr_files:
        # gh_mine.py: 'PR file list incomplete' (files null) -> trust git if the count matches
        if files and len(files) == pr['changedFiles']:
            return sha, sha + '^', 'files-from-git'
        return None, None, 'PR file list incomplete'
    if files == pr_files:
        return None, None, 'orig'
    # gh_mine.py: 'multi-commit PR (rebase)' -> the PR's k commits end at the merge commit
    k = (pr.get('commits') or {}).get('totalCount') or 0
    if k > 1 and len(git(clone, 'show', '-s', '--format=%P', sha).split()) == 1:
        base = git(clone, 'rev-parse', '-q', '--verify', f'{sha}~{k}').strip()
        if base and files_of(clone, base, sha) == pr_files:
            return sha, base, 'rebase-range'
    return None, None, 'multi-commit PR (rebase)'


def check(clone, sha, base):
    """mine.py filters + sys_sample.py Maven check; returns the candidate fields or (None, reason)."""
    main, tests, churn = [], [], 0
    for l in git(clone, 'diff', '--numstat', base, sha).splitlines():
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
        sha, base, why = fix_commit(clone, pr)
        if sha is None and why == 'orig':
            continue
        if sha and sha in seen:
            continue
        if sha:
            seen.add(sha)
            how = why
            info, why = check(clone, sha, base)
        if why:
            reasons[why] = reasons.get(why, 0) + 1
            continue
        reasons['recovered: ' + how] = reasons.get('recovered: ' + how, 0) + 1
        cands.append(dict(sha=sha[:10], base=git(clone, 'rev-parse', base).strip(), recovered=how,
                          date=git(clone, 'show', '-s', '--format=%ad', '--date=short', sha).strip(),
                          subject=git(clone, 'show', '-s', '--format=%s', sha).strip()[:110], **info,
                          pr=pr['number'],
                          jira={f'GH-{it["number"]}': dict(type='Bug', summary=it['title'][:200],
                                                           has_log_in_report=bool(REPORT_LOG.search(it['body'] or '')))}))
    json.dump(cands, open(os.path.join(CDIR, f'{p}_candidates.json'), 'w'), indent=1)
    random.Random(SEED).shuffle(cands)
    json.dump(cands, open(os.path.join(SDIR, f'{p}_bugs.json'), 'w'), indent=1)
    json.dump(cands, open(os.path.join(SDIR, f'{p}_sample.json'), 'w'), indent=1)
    return dict(project=repo, fixed_issue_pr_pairs=len(pairs), recovered=len(cands), dropped=reasons)


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
        print(i, len(todo), row['project'], row.get('recovered', row.get('error')), flush=True)
rows = [json.loads(l) for l in open(SUMMARY)]
with open(os.path.join(odir, 'selected.txt'), 'w') as fh:
    for r in rows:
        if r.get('recovered'):
            fh.write(r['project'].replace('/', '__') + '\n')
print('done', flush=True)
