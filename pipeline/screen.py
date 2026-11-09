import os, re, sys, csv
SKIP = re.compile(r'/(test|tests|it|jmh|examples?|benchmarks?|testing|test-?utils?|src/site)/', re.I)
LOGCALL = re.compile(r'(?:\b(?:\w*log\w*|LOG\w*|getLog\(\))\s*\.\s*)((?:trace|debug|info|warn|error|fatal)[fv]?|warning|fine|finer|finest|severe|config|atDebug|atInfo|atWarn|atError|atTrace|log)\s*\(', re.I)
NOTLOG = re.compile(r'\b(Math|StrictMath|FastMath|Precision|BigDecimal)\s*\.\s*log', re.I)
DEBUGLVL = {'trace','debug','tracef','debugf','tracev','debugv','fine','finer','finest','atdebug','attrace'}
# JBoss Logging typed message loggers, e.g. UndertowLogger.ROOT_LOGGER.cannotStart(...) or DEPLOYMENT_LOGGER.foo(...)
TYPED = re.compile(r'\b[A-Z]\w*Logger\s*\.\s*[A-Z_]*LOGGER\s*\.\s*(?!is\w*Enabled)[a-z]\w*\s*\(|\b[A-Z_]*_LOGGER\s*\.\s*(?!is\w*Enabled)[a-z]\w*\s*\(')
THREAD = re.compile(r'new\s+Thread\s*\(|\bExecutors\.|\bExecutorService\b|\bThreadPoolExecutor\b|\bCompletableFuture\b|\bForkJoinPool\b|implements\s+Runnable\b|\.parallelStream\(')
def measure(root, pkg_aware=False):
    """Production-code metrics of one checked-out project (tests, examples, benchmarks skipped).
    pkg_aware (GitHub version only): apply SKIP only to the directories before src/main/java/, so Java packages
    named it.*, *.examples, *.testing ... are not mistaken for test code. The Apache screening used pkg_aware=False."""
    loc=files=logfiles=calls=dbg=thr=0
    uniq=set()  # distinct logging statements: level + the rest of the line, whitespace removed
    for dp,dn,fn in os.walk(root):
        dn[:]=[d for d in dn if not d.startswith('.')]
        for f in fn:
            if not f.endswith('.java'): continue
            p=os.path.join(dp,f); rel='/'+os.path.relpath(p,root)
            if pkg_aware and '/src/main/java/' in rel: rel=rel.split('/src/main/java/')[0]+'/src/main/java/'
            if SKIP.search(rel) or f.endswith('Test.java') or f.startswith('Test'): continue
            try: txt=open(p,encoding='utf8',errors='ignore').read()
            except OSError: continue
            files+=1; c=0; incomment=False
            for l in txt.splitlines():
                s=l.strip()
                if incomment:
                    if '*/' in s: incomment=False
                    continue
                if not s or s.startswith('//'): continue
                if s.startswith('/*'):
                    if '*/' not in s: incomment=True
                    continue
                loc+=1
                if NOTLOG.search(s): continue
                c0=c
                for m in LOGCALL.finditer(s):
                    c+=1
                    if m.group(1).lower() in DEBUGLVL: dbg+=1
                    uniq.add(m.group(1).lower()+' '+''.join(s[m.end():].split()))
                if c==c0:
                    for m in TYPED.finditer(s):
                        c+=1; uniq.add(''.join(s[m.start():].split()))
                thr+=len(THREAD.findall(s))
            calls+=c; logfiles+= c>0
    k=loc/1000 or 1
    return dict(kloc=round(loc/1000,1),files=files,log_calls=calls,
        logs_per_kloc=round(calls/k,2),pct_files_with_logs=round(100*logfiles/max(files,1),1),
        pct_debug_trace=round(100*dbg/max(calls,1),1),thread_refs_per_kloc=round(thr/k,2),
        distinct_log_statements=len(uniq))

if __name__=='__main__':
    repos_dir, list_file, out_csv = sys.argv[1:4]
    rows=[]
    for line in open(list_file):
        grp,name,url=line.split()
        rows.append(dict(group=grp,project=name,**measure(os.path.join(repos_dir,name))))
    rows.sort(key=lambda r:-r['logs_per_kloc'])
    with open(out_csv,'w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    hdr=f"{'group':7}{'project':24}{'KLOC':>7}{'logs':>7}{'log/KLOC':>9}{'%files':>8}{'%dbg':>7}{'thr/KLOC':>9}"
    print(hdr)
    for r in rows:
        print(f"{r['group']:7}{r['project']:24}{r['kloc']:>7}{r['log_calls']:>7}{r['logs_per_kloc']:>9}{r['pct_files_with_logs']:>8}{r['pct_debug_trace']:>7}{r['thread_refs_per_kloc']:>9}")
