"""Step 1 of the GitHub Java dataset: list every GitHub repository that passes the search filters.
usage: python3 -I scripts/gh_list_repos.py <out dir> [pushed since=2021-10-22] [min stars=10] [max stars]
(max stars: list only a star band, e.g. 5 9 to add the 5-9 star repositories to an earlier >= 10 list)
Filters (same as tools/run/github_repo_funnel.py): language:java fork:false pushed:>SINCE archived:false stars:>=N.
The search API returns at most 1,000 results per query, so the creation dates are split into windows that each
hold <= 1,000 repositories (a window is halved until it fits; a single day that is still too big is split by stars).
Output (resumable; rerun the same command to continue):
  repos.jsonl     one repository per line (fields below), duplicates removed
  windows.jsonl   every finished window with the count the API reported and the number of repositories written
  total.json      the API's total count for the whole query when the run started, and the date of the run"""
import datetime, json, os, subprocess, sys, time

out = sys.argv[1]
SINCE = sys.argv[2] if len(sys.argv) > 2 else '2021-10-22'
STARS = int(sys.argv[3]) if len(sys.argv) > 3 else 10
STARS_MAX = int(sys.argv[4]) if len(sys.argv) > 4 else None
os.makedirs(out, exist_ok=True)
BASE = f'language:java fork:false pushed:>{SINCE} archived:false'
FIRST, LAST = datetime.date(2007, 10, 1), datetime.date.today()
STAR_CUTS = ([STARS, 12, 15, 20, 30, 50, 100, 300, 1000, 10 ** 9] if STARS_MAX is None   # used only for single days
             else list(range(STARS, STARS_MAX + 2)))                                       # with > 1,000 repos


def gh(*a):
    for i in range(8):
        r = subprocess.run(['gh', 'api', *a], capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout)
        wait = 65 if ('rate' in r.stderr.lower() or '403' in r.stderr or '429' in r.stderr) else 10 * (i + 1)
        print('  retry', i + 1, 'in', wait, 's:', r.stderr.strip()[:150], flush=True)
        time.sleep(wait)
    sys.exit('GitHub API keeps failing; rerun later, the run resumes')


def search(q, page=1, per_page=100):
    r = gh('-X', 'GET', 'search/repositories', '-f', f'q={q}', '-f', f'per_page={per_page}', '-f', f'page={page}',
           '-f', 'sort=stars', '-f', 'order=desc')
    time.sleep(2.2)            # search API: 30 requests per minute
    return r


def query(a, b, s0=STARS, s1=STARS_MAX):
    stars = f'stars:>={s0}' if s1 is None else f'stars:{s0}..{s1}'
    return f'{BASE} {stars} created:{a}..{b}'


seen = set()
rpath, wpath = os.path.join(out, 'repos.jsonl'), os.path.join(out, 'windows.jsonl')
if os.path.exists(rpath):
    seen = {json.loads(l)['repo'] for l in open(rpath)}
done = {json.loads(l)['q'] for l in open(wpath)} if os.path.exists(wpath) else set()
if not os.path.exists(os.path.join(out, 'total.json')):
    band = f'stars:>={STARS}' if STARS_MAX is None else f'stars:{STARS}..{STARS_MAX}'
    t = search(f'{BASE} {band}', per_page=1)['total_count']
    json.dump(dict(query=f'{BASE} {band}', total=t, date=str(datetime.date.today())),
              open(os.path.join(out, 'total.json'), 'w'), indent=1)
total = json.load(open(os.path.join(out, 'total.json')))['total']
print('total reported by the API:', total, '| already listed:', len(seen), flush=True)


def fetch(q, n):
    """Write all repositories of a query that has n <= 1,000 results."""
    new = 0
    for page in range(1, (n + 99) // 100 + 1):
        r = search(q, page)
        with open(rpath, 'a') as fh:
            for it in r.get('items', []):
                if it['full_name'] in seen:
                    continue
                seen.add(it['full_name'])
                new += 1
                fh.write(json.dumps(dict(
                    repo=it['full_name'], stars=it['stargazers_count'], created=it['created_at'][:10],
                    pushed=it['pushed_at'][:10], language=it['language'], size_kb=it['size'],
                    has_issues=it['has_issues'], open_issues=it['open_issues_count'],
                    default_branch=it['default_branch'], license=(it.get('license') or {}).get('spdx_id'),
                    topics=it.get('topics', []))) + '\n')
    with open(wpath, 'a') as fh:
        fh.write(json.dumps(dict(q=q, reported=n, written=new)) + '\n')
    done.add(q)


def window(a, b):
    q = query(a, b)
    if q in done:
        return
    n = search(q, per_page=1)['total_count']
    if n <= 1000:
        if n:
            fetch(q, n)
        else:
            with open(wpath, 'a') as fh:
                fh.write(json.dumps(dict(q=q, reported=0, written=0)) + '\n')
            done.add(q)
        print(a, b, n, '| listed', len(seen), flush=True)
    elif a < b:
        mid = a + (b - a) // 2
        window(a, mid)
        window(mid + datetime.timedelta(days=1), b)
    else:                      # one day with > 1,000 repositories: split by stars
        for lo, hi in zip(STAR_CUTS, STAR_CUTS[1:]):
            sq = query(a, b, lo, hi - 1)
            if sq in done:
                continue
            n = search(sq, per_page=1)['total_count']
            if n > 1000:
                print('WARNING', sq, 'has', n, '> 1000, only the first 1,000 are listed', flush=True)
            fetch(sq, min(n, 1000))
            print(a, f'stars {lo}..{hi - 1}', n, '| listed', len(seen), flush=True)


# one window per year first, so progress is visible and a restart skips finished years quickly
y = FIRST
while y <= LAST:
    end = min(datetime.date(y.year, 12, 31), LAST)
    window(y, end)
    y = end + datetime.timedelta(days=1)
print('done: listed', len(seen), 'of', total, 'reported', flush=True)
