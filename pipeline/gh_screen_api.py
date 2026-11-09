"""Step 2a of the GitHub Java dataset: screen the listed repositories with the GraphQL API only (no clone).
usage: python3 -I scripts/gh_screen_api.py <repos.jsonl from gh_list_repos.py> <out.jsonl> [since=2021-10-22]
Per repository (pass 1, 50 repositories per query):
  pom          the default branch has a root pom.xml (the pipeline supports Maven only)
  java_bytes   bytes of Java code reported by GitHub. Threshold MIN_JAVA_BYTES = 200,000: every one of the 282
               Apache repositories with >= 10 KLOC (screen.measure) has more (smallest 239,151), so this only
               removes repositories that cannot reach 10 KLOC; the exact KLOC rule is applied after cloning
  bug_labels   labels whose name contains the word "bug" (bug, type: bug, kind/bug, ...; not "debug"),
               except labels with the word "not" ("not a bug")
Pass 2, only for repositories that pass pass 1 (10 per query):
  bug_fixed    closed issues with a bug label, created on/after SINCE, closed by a merged pull request that was
               merged on/after SINCE (the newest 50 such labelled issues are checked, so the count is capped)
  pass         pom and java_bytes >= MIN_JAVA_BYTES and bug_fixed >= 1
Results are appended; repositories already in out.jsonl are skipped, so the script can be rerun."""
import json, os, re, subprocess, sys, time

src, out = sys.argv[1], sys.argv[2]
SINCE = sys.argv[3] if len(sys.argv) > 3 else '2021-10-22'
MIN_JAVA_BYTES = int(os.environ.get('LRB_MIN_JAVA_BYTES', 200_000))   # new standard (2026-10-23): 10,000
GRADLE = bool(os.environ.get('LRB_GRADLE'))   # new standard: Gradle builds count too
BUG = re.compile(r'(?<![a-z])bug(?![a-z])', re.I)
NOTBUG = re.compile(r'(?<![a-z])not(?![a-z])', re.I)     # "not a bug", "not-a-bug", "Resolution/Not a bug"


def gql(q):
    for i in range(8):
        r = subprocess.run(['gh', 'api', 'graphql', '-f', f'query={q}'], capture_output=True, text=True)
        try:
            res = json.loads(r.stdout)
        except ValueError:
            res = None
        if res and 'data' in res and res['data'] is not None:
            return res['data']   # partial errors (e.g. a renamed or deleted repository) leave that alias null
        wait = 65 if ('rate' in (r.stdout + r.stderr).lower() or 'abuse' in (r.stdout + r.stderr).lower()) else 10 * (i + 1)
        print('  retry', i + 1, 'in', wait, 's:', (r.stderr or r.stdout).strip()[:150], flush=True)
        time.sleep(wait)
    sys.exit('GitHub API keeps failing; rerun later, the run resumes')


def esc(s):
    return json.dumps(s)


repos = [json.loads(l) for l in open(src)]
done = {json.loads(l)['repo'] for l in open(out)} if os.path.exists(out) else set()
todo = [r for r in repos if r['repo'] not in done]
print(len(repos), 'listed,', len(done), 'already screened,', len(todo), 'to do', flush=True)

P1 = '''r{j}: repository(owner:{o}, name:{n}) {{ nameWithOwner
  pom: object(expression:"HEAD:pom.xml") {{ id }}
  g1: object(expression:"HEAD:build.gradle") {{ id }}
  g2: object(expression:"HEAD:build.gradle.kts") {{ id }}
  g3: object(expression:"HEAD:settings.gradle") {{ id }}
  g4: object(expression:"HEAD:settings.gradle.kts") {{ id }}
  languages(first:20) {{ edges {{ size node {{ name }} }} }}
  labels(first:30, query:"bug") {{ nodes {{ name }} }} }}'''
P2 = '''r{j}: repository(owner:{o}, name:{n}) {{
  issues(first:50, states:CLOSED, labels:{labels}, orderBy:{{field:CREATED_AT, direction:DESC}}) {{
    nodes {{ number createdAt closedByPullRequestsReferences(first:3, includeClosedPrs:false) {{ nodes {{ merged mergedAt }} }} }} }} }}'''

P1_BATCH = int(os.environ.get('LRB_P1_BATCH', 50))   # smaller batches when the 5 file lookups per repository time out (HTTP 502)
for i in range(0, len(todo), P1_BATCH):
    part = todo[i:i + P1_BATCH]
    data = gql('{' + '\n'.join(P1.format(j=j, o=esc(r['repo'].split('/')[0]), n=esc(r['repo'].split('/')[1]))
                               for j, r in enumerate(part)) + '}')
    rows = []
    for j, r in enumerate(part):
        rep = data.get(f'r{j}')
        if not rep:
            rows.append(dict(repo=r['repo'], error='not found'))
            continue
        java = sum(e['size'] for e in rep['languages']['edges'] if e['node']['name'] == 'Java')
        labels = [l['name'] for l in rep['labels']['nodes'] if BUG.search(l['name']) and not NOTBUG.search(l['name'])]
        rows.append(dict(repo=r['repo'], stars=r['stars'], pom=bool(rep['pom']), java_bytes=java, bug_labels=labels,
                         gradle=bool(rep['g1'] or rep['g2'] or rep['g3'] or rep['g4'])))
    build = lambda x: x.get('pom') or (GRADLE and x.get('gradle'))
    p2 = [x for x in rows if build(x) and x['java_bytes'] >= MIN_JAVA_BYTES and x['bug_labels']]
    for k in range(0, len(p2), 10):
        sub = p2[k:k + 10]
        d2 = gql('{' + '\n'.join(P2.format(j=j, o=esc(x['repo'].split('/')[0]), n=esc(x['repo'].split('/')[1]),
                                           labels=json.dumps(x['bug_labels'])) for j, x in enumerate(sub)) + '}')
        for j, x in enumerate(sub):
            nodes = ((d2.get(f'r{j}') or {}).get('issues') or {}).get('nodes') or []
            x['bug_fixed'] = sum(1 for it in nodes if it['createdAt'][:10] >= SINCE and any(
                p and p['merged'] and (p['mergedAt'] or '')[:10] >= SINCE
                for p in it['closedByPullRequestsReferences']['nodes']))
    for x in rows:
        x['pass'] = bool(build(x) and x.get('java_bytes', 0) >= MIN_JAVA_BYTES and x.get('bug_fixed', 0) >= 1)
    with open(out, 'a') as fh:
        for x in rows:
            fh.write(json.dumps(x) + '\n')
    print(f'{i + len(part)}/{len(todo)} screened, passed in this batch: {sum(x["pass"] for x in rows)}', flush=True)
    time.sleep(1)
print('done', flush=True)
