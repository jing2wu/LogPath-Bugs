"""End-to-end pipeline: reproduce bug -> trace with SELogger -> log pairs -> fault coverage.

For each candidate fix commit (from mine.py output, JIRA type = Bug):
 1. reproduce Defects4J style: fixed = fix commit, buggy = fix commit with production files
    reverted to the parent; run the fix's test methods on both (most verbose logging).
    Reproduced = tests pass on fixed and fail on buggy.
 2. if reproduced, run each fix test method on the buggy version under SELogger
    (format=omni, weave=EXEC+CALL+LINE, exlocation=.m2), build log pairs (analyse_trace.py)
    and locate the faulty lines relative to them (fault_coverage.py).  Raw traces are deleted
    after analysis; pairs, coverage and logs are kept.
 A bug is usable when at least one log pair's path contains a faulty line, in the trace of a test
 that fails on the buggy version (also under SELogger).

usage: python3 -I pipeline.py <project> <repo> <candidates.json> <work dir> <out dir> <selogger.jar> [workers]
  project = pdfbox | velocity      results are appended to <out dir>/<project>_pipeline.jsonl
"""
import glob, gzip, html, json, os, re, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyse_trace  # noqa: E402
import fault_coverage  # noqa: E402

SDK = os.path.expanduser('~/.sdkman/candidates/java')
JDK8, JDK17, JDK21 = (os.path.join(SDK, v) for v in ('8.0.412-zulu', '17.0.14-zulu', '21.0.7-zulu'))
JDK25 = os.path.join(SDK, '25.0.4+1.1-zulu')   # GitHub version only (LRB_JDK_PROPS)
MVN_FLAGS = ['-B', '-Drat.skip=true', '-Danimal.sniffer.skip=true', '-Djacoco.skip=true',
             '-Dmaven.javadoc.skip=true', '-Dcheckstyle.skip=true', '-Dspotbugs.skip=true', '-Denforcer.skip=true', '-Ddownload.plugin.skip=true',
             # plugins that do not affect tests but fail in a git worktree, offline, or on old releases
             '-Dmaven.gitcommitid.skip=true', '-Dimpsort.skip=true', '-Drat.ignoreErrors=true', '-Dmaven.buildNumber.skip=true',
             '-Dmaven.site.skip=true', '-Dspotless.check.skip=true', '-Dspotless.apply.skip=true', '-Dskip.npm', '-Dskip.yarn',
             '-Dskip.installnodenpm', '-Dskip.installyarn', '-Dlicense.skip=true', '-Dformatter.skip=true',
             '-DfailIfNoTests=false', '-Dsurefire.failIfNoSpecifiedTests=false', '-DtrimStackTrace=false']

# GitHub version only (LRB_JDK_PROPS): tell Maven-plugin tests where Maven lives, skip exec-plugin steps
# (front-end/TypeScript builds), and let Testcontainers run without its reaper image
GH = bool(os.environ.get('LRB_JDK_PROPS'))
MAVEN_HOME = os.path.dirname(os.path.dirname(os.path.realpath(shutil.which('mvn') or '/usr/bin/mvn')))
GH_FLAGS = ['-Dmaven.home=' + MAVEN_HOME, '-Dexec.skip=true'] if GH else []
GH_ENV = dict(MAVEN_HOME=MAVEN_HOME, TESTCONTAINERS_RYUK_DISABLED='true') if GH else {}
# build-failure rerun (2026-10-30): LRB_FORCE_UPDATE retries downloads whose failure Maven cached (-U);
# LRB_CLONE_WT builds in a shared clone instead of a git worktree (Gradle git-properties / JGit / git-hook plugins
# cannot read a worktree's .git file)
if os.environ.get('LRB_FORCE_UPDATE'):   # also undo POM properties that skip unit tests by default (DSpace)
    GH_FLAGS += ['-U', '-DskipTests=false', '-DskipUnitTests=false', '-DskipUTs=false', '-Dskip.unit.tests=false']
FORCE_JDK = {}   # sha -> JDK chosen from a version error of the first attempt (GitHub version only)

JUL = """handlers=java.util.logging.FileHandler
.level=ALL
java.util.logging.FileHandler.level=ALL
java.util.logging.FileHandler.pattern=target/app.log
java.util.logging.FileHandler.append=true
java.util.logging.FileHandler.formatter=java.util.logging.SimpleFormatter
java.util.logging.SimpleFormatter.format=%1$tFT%1$tT.%1$tL %4$s %2$s - %5$s%6$s%n
"""
LOG4J2 = """<?xml version="1.0" encoding="UTF-8"?>
<Configuration status="WARN">
  <Appenders><File name="F" fileName="target/app.log" append="true">
    <PatternLayout pattern="%d{yyyy-MM-dd'T'HH:mm:ss.SSS} %level %logger [%t] - %msg%n"/></File></Appenders>
  <Loggers><Root level="all"><AppenderRef ref="F"/></Root></Loggers>
</Configuration>
"""
LOG4J1 = """log4j.rootLogger=ALL, F
log4j.appender.F=org.apache.log4j.FileAppender
log4j.appender.F.File=target/app.log
log4j.appender.F.layout=org.apache.log4j.PatternLayout
log4j.appender.F.layout.ConversionPattern=%d{ISO8601} %p %c [%t] - %m%n
"""
LOGBACK = """<configuration>
  <appender name="F" class="ch.qos.logback.core.FileAppender"><file>target/app.log</file><append>true</append>
    <encoder><pattern>%d{yyyy-MM-dd'T'HH:mm:ss.SSS} %level %logger [%t] - %msg%n</pattern></encoder></appender>
  <root level="ALL"><appender-ref ref="F"/></root>
</configuration>
"""


# ---------------------------------------------------------------- project-specific logging set-up
def setup_logging_pdfbox(mod_dir):
    res = os.path.join(mod_dir, 'src/test/resources')
    os.makedirs(res, exist_ok=True)
    for name, text in (('logging.properties', JUL), ('log4j2.xml', LOG4J2), ('log4j2-test.xml', LOG4J2),
                       ('log4j.properties', LOG4J1), ('logback-test.xml', LOGBACK)):
        open(os.path.join(res, name), 'w').write(text)
    return ['-Djava.util.logging.config.file=src/test/resources/logging.properties',
            '-Dlogback.configurationFile=src/test/resources/logback-test.xml']


def setup_logging_velocity(mod_dir):
    pom = os.path.join(mod_dir, 'pom.xml')
    if os.path.exists(pom):
        s = open(pom).read()
        s = re.sub(r'(<name>org\.slf4j\.simpleLogger\.defaultLogLevel</name>\s*<value>)\w+(</value>)', r'\1trace\2', s)
        s = re.sub(r'(<name>org\.slf4j\.simpleLogger\.logFile</name>\s*<value>)[^<]*(</value>)',
                   r'\1${project.build.directory}/app.log\2', s)
        open(pom, 'w').write(s)
    return []


SLF4J_SIMPLE = """org.slf4j.simpleLogger.defaultLogLevel=trace
org.slf4j.simpleLogger.logFile=target/app.log
org.slf4j.simpleLogger.showThreadName=true
org.slf4j.simpleLogger.showDateTime=true
"""


def setup_logging_generic(mod_dir):
    """Tika, Maven: cover JUL, Log4j 1/2, Logback and slf4j-simple, whichever the version uses."""
    extra = setup_logging_pdfbox(mod_dir)
    open(os.path.join(mod_dir, 'src/test/resources/simplelogger.properties'), 'w').write(SLF4J_SIMPLE)
    return extra


PROJECTS = {'pdfbox': setup_logging_pdfbox, 'velocity': setup_logging_velocity,
            'tika': setup_logging_generic, 'maven': setup_logging_generic}

# ---------------------------------------------------------------- test-method detection
ANNOT = re.compile(r'@(?:Test|ParameterizedTest)\b[^\n]*\n(?:\s*@[^\n]*\n)*\s*(?:public\s+)?(?:static\s+)?void\s+(\w+)\s*\(')
JUNIT3 = re.compile(r'public\s+void\s+(test\w*)\s*\(\s*\)')


def test_starts(src):
    pat = ANNOT if '@Test' in src or '@ParameterizedTest' in src else JUNIT3
    return [(src[:m.start()].count('\n') + 1, m.group(1)) for m in pat.finditer(src)]


def git(repo, *a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True, errors='ignore').stdout


def fix_tests(repo, sha, tf, base=None):
    base = base or f'{sha}^'
    new, old = git(repo, 'show', f'{sha}:{tf}'), git(repo, 'show', f'{base}:{tf}')
    added = {n for _, n in test_starts(new)} - {n for _, n in test_starts(old)}
    if added:
        return sorted(added)
    changed = set()
    for m in re.finditer(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', git(repo, 'diff', '-U0', base, sha, '--', tf), re.M):
        s, n = int(m.group(1)), int(m.group(2) or 1)
        changed.update(range(s, s + max(n, 1)))
    starts, hit = test_starts(new), set()
    for i, (ln, name) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else 10 ** 9
        if any(ln <= c < end for c in changed):
            hit.add(name)
    return sorted(hit)


# ---------------------------------------------------------------- running tests
def run_tests(project, wt, module, tests, jdk, agent=None, mvn_props=()):
    if is_gradle(wt):
        return run_tests_gradle(project, wt, module, tests, jdk, agent)
    mod_dir = os.path.join(wt, module) if module else wt
    extra = PROJECTS.get(project, setup_logging_generic)(mod_dir)
    tgt = os.path.join(mod_dir, 'target')
    for f in ('app.log', 'velocity.log', 'pdfbox.log'):
        for d in (tgt, mod_dir):
            p = os.path.join(d, f)
            if os.path.exists(p):
                os.remove(p)
    shutil.rmtree(os.path.join(tgt, 'surefire-reports'), ignore_errors=True)
    env = dict(os.environ, **GH_ENV, JAVA_HOME=jdk, PATH=f'{jdk}/bin:' + os.environ['PATH'], SELOGGER_ARG=agent or '')
    # mvn_props: Maven user properties (-Dk=v); surefire forwards them to the test JVM after the POM's
    # <systemPropertyVariables>, so they win over a logging configuration the POM sets there
    if GH and agent:  # an <argLine>${jacocoArgLine}</argLine> whose property only a skipped plugin sets would reach
        # the test JVM verbatim and stop it from starting: define such properties as empty
        mvn_props = [*mvn_props, *(f'-D{k}=' for k in undefined_argline_props(wt))]
    cmd = ['mvn', *MVN_FLAGS, *GH_FLAGS, *extra, *mvn_props, 'test', '-Dtest=' + ','.join(tests)]
    if module:
        cmd[1:1] = ['-pl', module, '-am']
    if agent and not pom_has_argline(wt, mod_dir):
        # only when no POM sets <argLine>: such POMs already carry the agent via inject_argline, and a POM
        # argLine that expands @{argLine} would otherwise load the agent twice
        cmd.append('-DargLine=' + agent)
    out, killed = run_guarded(cmd, wt, env, trace_dir=agent_output(agent))
    up, orig = os.path.dirname(module), list(cmd)
    while not killed and up and 'Could not find the selected project in the reactor' in out:
        # the root POM does not list the module (nested aggregator, e.g. plugins/pom.xml): build it from the
        # nearest enclosing aggregator instead
        if os.path.exists(os.path.join(wt, up, 'pom.xml')):
            c2 = list(orig)
            c2[c2.index('-pl') + 1] = os.path.relpath(module, up)
            c2[1:1] = ['-f', os.path.join(up, 'pom.xml')]
            out, killed = run_guarded(c2, wt, env, trace_dir=agent_output(agent))
            out = f'[pipeline] module not in root reactor: built from {up}/pom.xml\n' + out
            cmd = c2
        up = os.path.dirname(up)
    if (not killed and 'maven-download-plugin:wget skipped' in out and 'BUILD FAILURE' in out
            and not re.search(r'Tests run: \d', out)):  # failed before any test ran
        # we skip download-maven-plugin by default (PDFBox/HttpClient fetch test files from the network), but
        # some builds download a tool they need (IoTDB's thrift compiler): retry once with downloads allowed
        cmd = [a for a in cmd if a != '-Ddownload.plugin.skip=true']
        out, killed = run_guarded(cmd, wt, env, trace_dir=agent_output(agent))
        out = '[pipeline] build failed with download-maven-plugin skipped: rerun with downloads\n' + out
    if not killed and re.search(r'git-commit-id-plugin:[\d.]+:revision .*Could not complete Mojo execution', out):
        # old git-commit-id-plugin (JGit) cannot read a git worktree and has no -D switch to skip it:
        # set <skip>true</skip> in the worktree POMs (restored by the next checkout -f) and rebuild
        if skip_git_commit_id(wt):
            out, killed = run_guarded(cmd, wt, env, trace_dir=agent_output(agent))
            out = '[pipeline] git-commit-id-plugin failed on the worktree: rerun with <skip>true</skip>\n' + out
    if not killed and re.search(r'maven-dependency-plugin:[\d.]+:(copy|unpack)\S* .*Artifact has not been packaged yet',
                                out):
        # copy/unpack of a reactor module bound before `package` (Zeppelin interpreters) cannot work in a
        # `test` build: retry once with maven-dependency-plugin skipped
        cmd.append('-Dmdep.skip=true')
        out, killed = run_guarded(cmd, wt, env, trace_dir=agent_output(agent))
        out = '[pipeline] maven-dependency-plugin needs packaged reactor artifacts: rerun with -Dmdep.skip\n' + out
    if not killed and old_surefire(out):
        # surefire < 2.7.3 ignores the #method part of -Dtest and runs nothing: invoke a newer surefire
        # goal directly (the POM's surefire <configuration>, including argLine, still applies)
        cmd[cmd.index('test')] = 'test-compile'
        cmd.insert(cmd.index('test-compile') + 1, NEW_SUREFIRE)
        out, killed = run_guarded(cmd, wt, env, trace_dir=agent_output(agent))
        out = f'[pipeline] surefire < 2.7.3: rerun with {NEW_SUREFIRE}\n' + out
    if killed:
        return dict(status=killed, msgs=[], log_lines=0, out=out, log='')
    m = re.findall(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)\s*$', out, re.M)
    if 'COMPILATION ERROR' in out or (not m and 'BUILD FAILURE' in out):
        status = 'build_error'
    elif not m or int(m[-1][0]) == 0:
        status = 'no_tests_run'
    else:
        run, fail, err, skip = map(int, m[-1])
        status = 'pass' if fail + err == 0 and run > skip else ('skipped' if run == skip else 'fail')
    log = ''
    for f in ('app.log', 'velocity.log', 'pdfbox.log'):
        for d in (tgt, mod_dir):
            p = os.path.join(d, f)
            if os.path.exists(p):
                log += open(p, errors='ignore').read()
    lines = [l for l in log.splitlines() if l.strip() and not l.startswith(('\t', 'at ', 'Caused by'))]
    return dict(status=status, msgs=re.findall(r'^\[ERROR\]\s{2,}(\S.*)$', out, re.M)[:3],
                log_lines=len(lines), out=out, log='\n'.join(lines))


NEW_SUREFIRE = 'org.apache.maven.plugins:maven-surefire-plugin:2.22.2:test'


# ---------------------------------------------------------------- Gradle (GitHub version only)
GRADLE_INIT = """allprojects {
  tasks.withType(Test).configureEach {
    def a = System.getenv('LRB_TEST_JVM_ARGS')
    if (a) { jvmArgs(a.split('\\n').findAll { it } as List) }
    ignoreFailures = true
    doFirst { def jc = extensions.findByName('jacoco'); if (jc != null) { jc.enabled = false } }   // its agent would be traced too
    maxParallelForks = 1
    try { filter.failOnNoMatchingTests = false } catch (ignored) { }   // root 'test' runs in every subproject
    outputs.upToDateWhen { false }
    try { reports.html.required = false } catch (ignored) { }
  }
  tasks.matching { it.name ==~ /(?i)(javadoc|jacoco|spotless|checkstyle|pmd|spotbugs|npm|yarn|node|license)\\w*|rat/ && !(it instanceof Test) }.configureEach { enabled = false }
}
"""


def is_gradle(wt):
    """GitHub version: a Gradle build without a root pom.xml."""
    return GH and not os.path.exists(os.path.join(wt, 'pom.xml')) and any(
        os.path.exists(os.path.join(wt, f)) for f in ('build.gradle', 'build.gradle.kts', 'settings.gradle', 'settings.gradle.kts'))


def gradle_version(wt):
    p = os.path.join(wt, 'gradle/wrapper/gradle-wrapper.properties')
    m = re.search(r'gradle-(\d+)\.(\d+)', open(p).read()) if os.path.exists(p) else None
    return (int(m.group(1)), int(m.group(2))) if m else None


def run_tests_gradle(project, wt, module, tests, jdk, agent=None):
    mod_dir = os.path.join(wt, module) if module else wt
    extra = setup_logging_generic(mod_dir)          # same log configuration files, picked up from src/test/resources
    tgt = os.path.join(mod_dir, 'target')           # the configurations write target/app.log in the test's directory
    for d in (tgt, mod_dir, *gradle_project_dirs(wt)):
        p = os.path.join(d, 'app.log')
        if os.path.exists(p):
            os.remove(p)
        p = os.path.join(d, 'target', 'app.log')
        if os.path.exists(p):
            os.remove(p)
    for d in gradle_project_dirs(wt):       # a subproject may compile a source folder outside its own directory
        shutil.rmtree(os.path.join(d, 'build', 'test-results'), ignore_errors=True)
    init = os.path.join(wt, '.lrb-init.gradle')
    open(init, 'w').write(GRADLE_INIT)
    jvm = [*extra, *(agent.split() if agent else [])]
    env = dict(os.environ, **GH_ENV, JAVA_HOME=jdk, PATH=f'{jdk}/bin:' + os.environ['PATH'],
               LRB_TEST_JVM_ARGS='\n'.join(jvm), SELOGGER_ARG=agent or '')
    gw = os.path.join(wt, 'gradlew')
    if os.path.exists(gw):
        os.chmod(gw, 0o755)
    task = (':' + module.replace('/', ':') + ':test') if module else 'test'
    cmd = [gw if os.path.exists(gw) else 'gradle', '--no-daemon', '--console=plain', '-I', init,
           f'-Dorg.gradle.java.home={jdk}', '-Dorg.gradle.configuration-cache=false',   # the init script's doFirst breaks it
           task, *(a for t in tests for a in ('--tests', '*.' + t.replace('#', '.')))]
    out, killed = run_guarded(cmd, wt, env, trace_dir=agent_output(agent))
    if not killed and module and 'Cannot locate tasks that match' in out:
        # the subproject's name differs from its directory (e.g. polaris): run the root 'test' task with the same filter
        cmd[cmd.index(task)] = 'test'
        out, killed = run_guarded(cmd, wt, env, trace_dir=agent_output(agent))
    if killed:
        return dict(status=killed, msgs=[], log_lines=0, out=out, log='')
    run = fail = skip = 0
    msgs = []
    ran = [d for d in gradle_project_dirs(wt) if glob.glob(os.path.join(d, 'build', 'test-results', '*', 'TEST-*.xml'))]
    for x in (x for d in ran for x in glob.glob(os.path.join(d, 'build', 'test-results', '*', 'TEST-*.xml'))):
        t = open(x, errors='ignore').read()
        m = re.search(r'<testsuite [^>]*', t)
        a = dict(re.findall(r'(\w+)="(\d+)"', m.group(0))) if m else {}
        run += int(a.get('tests', 0)); fail += int(a.get('failures', 0)) + int(a.get('errors', 0)); skip += int(a.get('skipped', 0))
        msgs += [html.unescape(v)[:200] for v in re.findall(r'<(?:failure|error) message="([^"]*)"', t)]
    if run == 0 and re.search(r'compile\w*Java FAILED|Compilation failed|BUILD FAILED|Could not resolve', out):
        status = 'build_error'
        msgs = re.findall(r'^(?:e: |> |\S+\.java:\d+: error: ).*$', out, re.M)[:3]
    elif run == 0:
        status = 'no_tests_run'
    else:
        status = 'pass' if fail == 0 and run > skip else ('skipped' if run == skip else 'fail')
    log = ''
    for d in dict.fromkeys((tgt, mod_dir, *ran, *(os.path.join(r, 'target') for r in ran))):   # app.log sits in the test JVM's directory
        p = os.path.join(d, 'app.log')
        if os.path.exists(p):
            log += open(p, errors='ignore').read()
    lines = [l for l in log.splitlines() if l.strip() and not l.startswith(('\t', 'at ', 'Caused by'))]
    return dict(status=status, msgs=msgs[:3], log_lines=len(lines), out=out, log='\n'.join(lines))


def gradle_project_dirs(wt):
    """Directories holding a build.gradle(.kts): the Gradle (sub)projects of the worktree."""
    out = []
    for dp, dn, fn in os.walk(wt):
        dn[:] = [d for d in dn if d not in ('.git', 'build', 'node_modules', 'src', '.gradle', 'target')]
        if 'build.gradle' in fn or 'build.gradle.kts' in fn:
            out.append(dp)
    return out


def old_surefire(out):
    """True when the run used surefire < 2.7.3 (no Class#method filtering) and ran no tests."""
    m = re.findall(r'surefire:(\d+)\.(\d+)(?:\.(\d+))?[^:\s]*:test', out)
    if not m or re.search(r'Tests run: [1-9]', out):
        return False
    return any((int(a), int(b), int(c or 0)) < (2, 7, 3) for a, b, c in m)


TRACE_LIMIT_BYTES = 3 * 1024 ** 3   # a runaway (e.g. infinite-loop) trace is cut off here
LOG_LIMIT_BYTES = 3 * 1024 ** 3     # same for the application log (a ranger ugsync test wrote 13 GB and filled the disk)
MIN_FREE_BYTES = 2 * 1024 ** 3      # stop a run before the disk is full; recorded as disk_low and requeued later
TRACED_TIMEOUT, PLAIN_TIMEOUT = 900, 5400


def agent_output(agent):
    m = re.search(r'output=([^,]+)', agent or '')
    return m.group(1) if m else None


def dir_bytes(d):
    total = 0
    for root, _, files in os.walk(d):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def app_log_bytes(wt):
    """Size of the largest log file the logging configs write (target/app.log of the project or a module)."""
    sizes = [0]
    pats = ('target/*.log', '*/target/*.log', '*/*/target/*.log')
    if GH:   # Gradle keeps test stdout in build/test-results/<task>/binary/output.bin (an eddie test wrote 72 GB there)
        pats += tuple(d + 'build/test-results/*/binary/output.bin' for d in ('', '*/', '*/*/'))
    for pat in pats:
        for f in glob.glob(os.path.join(wt, pat)):
            try:
                sizes.append(os.path.getsize(f))
            except OSError:
                pass
    return max(sizes)


def run_guarded(cmd, wt, env, trace_dir=None):
    """Run Maven in its own process group; kill the whole group on timeout or when the trace grows
    past TRACE_LIMIT_BYTES.  Returns (stdout, None | 'timeout' | 'trace_too_large' | 'log_too_large' | 'disk_low')."""
    import signal, tempfile, time
    waited = 0
    while shutil.disk_usage(wt).free < 2 * MIN_FREE_BYTES and waited < 3600:
        # parallel workers' traces can fill the disk: wait for them to be read and removed before starting
        time.sleep(30)
        waited += 30
    with tempfile.TemporaryFile('w+', errors='ignore') as buf:
        p = subprocess.Popen(cmd, cwd=wt, env=env, stdout=buf, stderr=subprocess.STDOUT, text=True,
                             start_new_session=True)
        limit = TRACED_TIMEOUT if trace_dir else PLAIN_TIMEOUT
        start, killed = time.time(), None
        while p.poll() is None:
            time.sleep(5)
            if time.time() - start > limit:
                killed = 'timeout'
            elif trace_dir and os.path.isdir(trace_dir) and dir_bytes(trace_dir) > TRACE_LIMIT_BYTES:
                killed = 'trace_too_large'
            elif app_log_bytes(wt) > LOG_LIMIT_BYTES:
                killed = 'log_too_large'
            elif shutil.disk_usage(wt).free < MIN_FREE_BYTES:
                killed = 'disk_low'
            if killed:
                try:
                    os.killpg(p.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):   # the group exited meanwhile
                    pass
                p.wait()
                if trace_dir:
                    shutil.rmtree(trace_dir, ignore_errors=True)
        buf.seek(0)
        return buf.read(), killed


def pom_has_argline(wt, mod_dir):
    return any(os.path.exists(p) and '<argLine>' in open(p).read()
               for p in {os.path.join(wt, 'pom.xml'), os.path.join(wt, 'parent/pom.xml'), os.path.join(mod_dir, 'pom.xml')})


def skip_git_commit_id(wt):
    """Add <skip>true</skip> to every git-commit-id-plugin block (plugin and execution configurations)."""
    def patch(m):
        b = m.group(0)
        if '<configuration>' not in b:
            return b.replace('</artifactId>', '</artifactId><configuration><skip>true</skip></configuration>', 1)
        b = re.sub(r'<skip>[^<]*</skip>', '', b)
        return b.replace('<configuration>', '<configuration><skip>true</skip>')
    changed = False
    for root, dirs, files in os.walk(wt):
        dirs[:] = [d for d in dirs if d not in ('.git', 'target', 'node_modules', 'src')]
        if 'pom.xml' in files:
            pom = os.path.join(root, 'pom.xml')
            s = open(pom, errors='ignore').read()
            s2 = re.sub(r'<plugin>(?:(?!</?plugin>).)*?git-commit-id-plugin(?:(?!</?plugin>).)*?</plugin>',
                        patch, s, flags=re.S)
            if s2 != s:
                open(pom, 'w').write(s2)
                changed = True
    return changed


def inject_argline(wt, mod_dir):
    """Make every <argLine> in the root, parent and module POMs carry the agent
    (a POM-level argLine overrides the CLI -DargLine)."""
    poms = [p for p in {os.path.join(wt, 'pom.xml'), os.path.join(wt, 'parent/pom.xml'), os.path.join(mod_dir, 'pom.xml')}
            if os.path.exists(p)]
    def plugin_arglines(s):
        props = [(m.start(), m.end()) for m in re.finditer(r'<properties>.*?</properties>', s, re.S)]
        return [m for m in re.finditer(r'<argLine>', s) if not any(a <= m.start() < b for a, b in props)]
    # GitHub version: when no POM has a plugin <argLine>, surefire reads the <argLine> property itself: patch that
    property_only = GH and not any(plugin_arglines(open(p).read()) for p in poms)
    for pom in poms:
        s = open(pom).read()
        # only plugin <argLine> settings; an <argLine> *property* is expanded into them via @{argLine},
        # so patching both would load the agent twice
        props = [(m.start(), m.end()) for m in re.finditer(r'<properties>.*?</properties>', s, re.S)]
        if property_only:
            props = []
        s2 = re.sub(r'<argLine>(.*?)</argLine>',
                    lambda m: m.group(0) if any(a <= m.start() < b for a, b in props)
                    else f'<argLine>{m.group(1)} ${{env.SELOGGER_ARG}}</argLine>', s, flags=re.S)
        if s2 != s:
            open(pom, 'w').write(s2)


def undefined_argline_props(wt):
    """${...} properties used in some POM's <argLine> but defined in no POM of the worktree."""
    poms = ''
    for dp, dn, fn in os.walk(wt):
        dn[:] = [d for d in dn if d not in ('.git', 'target', 'node_modules', 'resources', 'test', 'java')]
        if 'pom.xml' in fn:
            poms += open(os.path.join(dp, 'pom.xml'), errors='ignore').read()
    used = {k for a in re.findall(r'<argLine>(.*?)</argLine>', poms, re.S) for k in re.findall(r'\$\{([\w.-]+)\}', a)}
    return sorted(k for k in used if not k.startswith(('env.', 'project.', 'settings.', 'basedir'))
                  and f'<{k}>' not in poms and f'<{k}/>' not in poms)


def pick_jdk(wt):
    pom = ''
    for p in ('pom.xml', 'parent/pom.xml'):
        if os.path.exists(os.path.join(wt, p)):
            pom += open(os.path.join(wt, p)).read()
    m = [int(v) for v in re.findall(r'<(?:maven\.compiler\.)?(?:release|source|target)>(?:1\.)?(\d+)<', pom)]
    if os.environ.get('LRB_JDK_PROPS'):  # GitHub version: also resolve <release>${java.compiler.version}</release> etc.
        for dp, dn, fn in os.walk(wt):      # and read every module POM, not only the root and parent/
            dn[:] = [d for d in dn if d not in ('.git', 'target', 'node_modules', 'resources', 'test', 'java')]
            if 'pom.xml' in fn and dp not in (wt, os.path.join(wt, 'parent')):
                pom += open(os.path.join(dp, 'pom.xml'), errors='ignore').read()
        m = [int(v) for v in re.findall(r'<(?:maven\.compiler\.)?(?:release|source|target)>(?:1\.)?(\d+)<', pom)]
        props = dict(re.findall(r'<([\w.-]+)>(?:1\.)?(\d+)</\1>', pom))
        refs = re.findall(r'<(?:maven\.compiler\.)?(?:release|source|target)>\$\{([\w.-]+)\}<', pom)
        m += [int(props[r]) for r in refs if r in props] + [int(v) for k, v in props.items() if k == 'java.version']
        for dp, dn, fn in os.walk(wt):      # Gradle builds: sourceCompatibility, toolchains, release
            dn[:] = [d for d in dn if d not in ('.git', 'build', 'node_modules', 'src', '.gradle')]
            for f in fn:
                if f.endswith(('.gradle', '.gradle.kts')) or f == 'libs.versions.toml':
                    g = open(os.path.join(dp, f), errors='ignore').read()
                    m += [int(v) for v in re.findall(r'(?:JavaVersion\.VERSION_(?:1_)?|JavaLanguageVersion\.of\(|'
                                                     r'(?:source|target)Compatibility\s*=\s*[\'"]?(?:1\.)?|release\.set\(|release\s*=\s*|jvmTarget\s*=\s*[\'"]?)(\d+)', g)
                          if 8 <= int(v) <= 30]
        m.append(17)  # recent projects often target 8 but their test setup (argLine --add-exports ...) needs 9+
    v = max(m) if m else 8
    gv = gradle_version(wt) if is_gradle(wt) else None   # the JDK must also be able to run the project's Gradle
    if os.environ.get('LRB_JDK_PROPS') and v >= 22 and not (gv and gv < (9, 1)):   # Gradle runs on JDK 25 from 9.1
        return JDK25
    if gv and gv < (7, 3):
        return JDK8
    if gv and gv < (8, 5) and v >= 21:
        return JDK17
    return JDK21 if v >= 21 else JDK17 if v >= 11 else JDK8


# ---------------------------------------------------------------- one candidate
def process(cfg, c, wt):
    project, repo, out_dir, agent_jar = cfg
    sha = git(repo, 'rev-parse', c['sha']).strip()
    base = c.get('base') or f'{sha}^'   # buggy revision; 'base' is set only for recovered multi-commit fixes (gh_mine_recover.py)
    issue = next(k for k, v in c['jira'].items() if v and v['type'] == 'Bug')
    rec = dict(project=project, issue=issue, sha=sha[:10], date=c['date'], summary=c['jira'][issue]['summary'],
               main=c['main'], report_has_logs=c['jira'][issue]['has_log_in_report'])
    bdir = os.path.join(out_dir, f'{project}_runs', f'{issue}_{sha[:10]}')
    os.makedirs(bdir, exist_ok=True)

    def checkout(buggy):
        git(wt, 'checkout', '-q', '-f', sha)
        git(wt, 'clean', '-q', '-fdx')  # no stale generated sources between commits
        if buggy:
            git(wt, 'checkout', '-q', base, '--', *c['main'])

    checkout(False)
    jdk = FORCE_JDK.get(sha) or pick_jdk(wt)
    rec['jdk'] = {JDK8: '8', JDK17: '17', JDK21: '21', JDK25: '25'}[jdk]
    by_mod = {}
    for cls, m in c.get('trigger_tests', []):     # benchmark bugs: run exactly the trigger tests
        tf = c['test_paths'][cls]
        module = tf.split('/src/test/')[0] if '/src/test/' in tf else ''
        by_mod.setdefault(module, []).append(f"{cls.split('.')[-1].split('$')[0]}#{m}")
    for tf in ([] if c.get('trigger_tests') else c['tests']):
        if tf.endswith('.java') and '/test/' in tf:
            module = tf.split('/src/test/')[0] if '/src/test/' in tf else ''
            for m in fix_tests(repo, sha, tf, base):
                by_mod.setdefault(module, []).append(f'{os.path.basename(tf)[:-5]}#{m}')
    if not by_mod:
        rec['result'] = 'no_test_methods_found'
        return rec
    module, tests = max(by_mod.items(), key=lambda kv: len(kv[1]))
    rec.update(module=module, tests=tests)

    results = {}
    for tag, buggy in (('fixed', False), ('buggy', True)):
        checkout(buggy)
        r = run_tests(project, wt, module, tests, jdk)
        open(os.path.join(bdir, f'{tag}_mvn.log'), 'w').write(r.pop('out'))
        log = r.pop('log')
        if len(log) > 100_000_000:  # TRACE logging can produce GBs; nothing rereads these, keep them compressed
            with gzip.open(os.path.join(bdir, f'{tag}_app.log.gz'), 'wt') as fh:
                fh.write(log)
        else:
            open(os.path.join(bdir, f'{tag}_app.log'), 'w').write(log)
        results[tag] = r
    rec['fixed'], rec['buggy'] = results['fixed'], results['buggy']
    f, b = results['fixed']['status'], results['buggy']['status']
    if not (f == 'pass' and b == 'fail'):
        rec['result'] = 'not_reproduced_buggy_passes' if f == b == 'pass' else f'invalid_fixed_{f}_buggy_{b}'
        return rec

    # ---- trace each test method on the buggy version
    faults = fault_coverage.fault_lines(repo, sha, c['main'], base)
    rec['fault_lines'] = len(faults)
    rec['traces'] = []
    for test in tests:
        checkout(True)
        mod_dir = os.path.join(wt, module) if module else wt
        inject_argline(wt, mod_dir)
        tdir = os.path.join(bdir, 'trace_' + test.replace('#', '.'))
        shutil.rmtree(tdir, ignore_errors=True)
        os.makedirs(tdir)
        dep = '.gradle' if is_gradle(wt) else '.m2'   # skip classes from dependency jars (Maven or Gradle cache)
        agent = f'-Xmx4g -javaagent:{agent_jar}=output={tdir}/selogger,format=omni,weave=EXEC+CALL+LINE,exlocation={dep}'
        r = run_tests(project, wt, module, [test], jdk, agent)
        open(os.path.join(tdir, 'app.log'), 'w').write(r['log'])
        json.dump(dict(issue=issue, sha=sha[:10], test=test, status=r['status']), open(os.path.join(tdir, 'meta.json'), 'w'))
        t = dict(test=test, status=r['status'])
        if os.path.isdir(os.path.join(tdir, 'selogger')):
            try:
                s = analyse_trace.analyse(tdir)
                cov = fault_coverage.coverage(tdir, faults)
                json.dump(cov, open(os.path.join(tdir, 'coverage.json'), 'w'), indent=0)
                t.update({k: s[k] for k in ('prod_threads', 'trace_line_events', 'log_events', 'log_statements', 'pairs')})
                cp = sorted(p['lines'] for p in cov['covering_pairs'])
                t.update(fault_exec=cov['executions'], fault_in_pair=cov['in_pair'], fault_prefix=cov['prefix'],
                         fault_suffix=cov['suffix'], covering_pairs=len(cp), covering_min_lines=cp[0] if cp else None)
            except Exception as e:  # keep the batch going
                t['analysis_error'] = repr(e)
            shutil.rmtree(os.path.join(tdir, 'selogger'), ignore_errors=True)
        rec['traces'].append(t)
    covering = [t for t in rec['traces'] if t.get('covering_pairs') and t['status'] == 'fail']
    if covering:
        rec['result'] = 'usable'
        rec['covering_min_lines'] = min(t['covering_min_lines'] for t in covering)
    elif any(t.get('covering_pairs') for t in rec['traces']):
        rec['result'] = 'reproduced_covering_test_passes'  # the traced test did not fail: not a failing execution
    elif any(t.get('fault_suffix') for t in rec['traces']):
        rec['result'] = 'reproduced_fault_after_last_log'
    elif any(t.get('log_events') for t in rec['traces']):
        rec['result'] = 'reproduced_fault_not_in_pair'
    else:
        rec['result'] = 'reproduced_no_logs'
    return rec


def jdk_from_errors(out_dir, project, rec):
    """JDK ('8'/'17'/'21'/'25') that a build or test-start error asks for, else None."""
    if not ('build_error' in rec.get('result', '') or 'no_tests_run' in rec.get('result', '')):
        return None
    d = os.path.join(out_dir, f'{project}_runs', f"{rec.get('issue')}_{rec.get('sha')}")
    txt = ''.join(open(os.path.join(d, f), errors='ignore').read() for f in ('fixed_mvn.log', 'buggy_mvn.log')
                  if os.path.exists(os.path.join(d, f)))
    v = [int(x) for x in re.findall(r'release version (\d+) not supported', txt)]
    v += [int(float(x)) - 44 for x in re.findall(r'class file (?:has wrong )?version (\d+(?:\.\d+)?)', txt)]
    v += [int(x) for x in re.findall(r'invalid source release: (?:1\.)?(\d+)', txt)]   # javac under Gradle
    v += [8 for _ in re.findall(r'Java 1\.8 is required', txt)]
    if not v:
        return None
    v = max(v)
    return '25' if v >= 22 else '21' if v >= 18 else '17' if v >= 9 else '8'


def main():
    project, repo, cands, work, out_dir, agent_jar = sys.argv[1:7]
    out_dir, work, agent_jar = map(os.path.abspath, (out_dir, work, agent_jar))  # agent output must be absolute
    workers = int(sys.argv[7]) if len(sys.argv) > 7 else 3
    out = os.path.join(out_dir, f'{project}_pipeline.jsonl')
    todo = [c for c in json.load(open(cands)) if 'skip' not in c and c.get('main')
            and any(v and v['type'] == 'Bug' for v in c['jira'].values())]
    done = {json.loads(l)['sha'] for l in open(out)} if os.path.exists(out) else set()
    todo = [c for c in todo if c['sha'] not in done]
    pool = Queue()
    for i in range(workers):
        wt = os.path.join(work, f'{project}_w{i}')
        if not os.path.isdir(wt):
            if os.environ.get('LRB_CLONE_WT'):
                subprocess.run(['git', 'clone', '-q', '--shared', '--no-checkout', repo, wt], check=True)
                subprocess.run(['git', '-C', wt, 'checkout', '-q', '--detach', git(repo, 'rev-parse', 'HEAD').strip()], check=True)
            else:
                subprocess.run(['git', '-C', repo, 'worktree', 'add', '-q', '-f', '--detach', wt, 'HEAD'], check=True)
        pool.put(wt)
    cfg = (project, repo, out_dir, agent_jar)

    def job(c):
        wt = pool.get()
        try:
            try:
                rec = process(cfg, c, wt)
                retry = GH and jdk_from_errors(out_dir, project, rec)
                if retry and retry != rec.get('jdk'):   # GitHub version: one more attempt with the JDK the error names
                    FORCE_JDK[git(repo, 'rev-parse', c['sha']).strip()] = {'8': JDK8, '17': JDK17, '21': JDK21, '25': JDK25}[retry]
                    rec = process(cfg, c, wt)
                    rec['jdk_retry'] = True
            except Exception as e:
                rec = dict(project=project, sha=c['sha'], result=f'script_error: {e!r}')
            with open(out, 'a') as fh:
                fh.write(json.dumps(rec) + '\n')
            print(rec.get('issue'), rec['sha'], rec['result'], rec.get('covering_min_lines', ''), flush=True)
        finally:
            pool.put(wt)

    print(f'{project}: {len(todo)} to run ({len(done)} done)', flush=True)
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(job, todo))


if __name__ == '__main__':
    main()
