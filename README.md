# LogPath-Bugs

LogPath-Bugs is a dataset of 116 real Java bugs from 57 GitHub projects. For each bug it gives the
application log printed by a failing test, the source lines that executed between every two consecutive log
messages (recorded with SELogger), and the faulty lines changed by the developers' fix. In every bug, at least
one pair of printed log messages has a faulty line on the path between them.

Each bug comes from a GitHub issue labeled as a bug and closed by a merged pull request. The failing test is
the test the developers added or changed in that fix: it fails on the buggy version and passes on the fixed
one.

## Contents

| Folder | What it holds |
|---|---|
| `dataset/` | The 116 bugs (at most 10 per project). `dataset/index.jsonl` has one line per bug. |
| `extra/` | 54 more bugs that passed every check but exceed the 10-per-project cap (all from openapi-generator). |
| `not_released/` | 46 bugs that failed one of the final checks; `index.jsonl` gives the reason. |
| `funnel/` | Every selection decision, from the repository search to the final checks. |
| `pipeline/` | The scripts that built the dataset and the patched SELogger. |
| `checker/` | An independent checker and a script that turns a new SELogger trace into log pairs. |

The three bug folders share one layout: `<owner>__<repo>/<issue>/`, with three files per bug.

| File | Content |
|---|---|
| `meta.json` | The issue, the fix commit, how the buggy version is derived, JDK, module, failing test(s), faulty lines, number of pairs and of pairs that cover the fault, shortest covering path, and the outcome of the checks. |
| `app_<TestClass>.<method>.log` | Everything the failing test printed, at all log levels. |
| `pairs.jsonl` | One log pair per line (see below). |

The source code is not included. The buggy version is the fix commit with the files listed in
`meta.json` → `buggy_version` reverted to the parent commit, so the new test is present and the code under test
is the old one. All line numbers in the dataset refer to this buggy version.

## Example: pf4j #670

Issue: "Extension#ordinal is never read by the ASM-based ExtensionInfo". Fix commit `47b006a0be`.
The failing test `ExtensionVisitorTest#shouldReadAllAttributesFromCompiledExtension` prints six messages:

```
DEBUG org.pf4j.asm.ExtensionVisitor - Load annotation attribute plugins = alpha (java.lang.String)
DEBUG org.pf4j.asm.ExtensionVisitor - Found plugin alpha
DEBUG org.pf4j.asm.ExtensionVisitor - Load annotation attribute plugins = beta (java.lang.String)
...
```

The first line of `pairs.jsonl` (shortened):

```json
{"thread": "0",
 "start": {"file": "pf4j/src/main/java/org/pf4j/asm/ExtensionVisitor.java", "line": 70, "level": "debug",
           "template": "Load annotation attribute {} = {} ({})", "printed": true,
           "text": "Load annotation attribute plugins = alpha (java.lang.String)"},
 "end":   {"file": "pf4j/src/main/java/org/pf4j/asm/ExtensionVisitor.java", "line": 75, "level": "debug",
           "template": "Found plugin {}", "printed": true, "text": "Found plugin alpha"},
 "path": [["pf4j/.../ExtensionVisitor.java", 70], [".../ExtensionVisitor.java", 71], ..., [".../ExtensionVisitor.java", 41]],
 "path_lines": 6, "covers_fault": true, "in_test_method": true,
 "test": "ExtensionVisitorTest#shouldReadAllAttributesFromCompiledExtension"}
```

The faulty lines are 65, 71, 72 and 73 (the lines the fix deletes or changes). This path runs through 71 and
73, so `covers_fault` is true. The next pair, from "Found plugin alpha" back to the next "Load annotation
attribute", runs through lines 75, 76, 41, 90, 91, 70 and does not cover the fault.

### Fields of a pair

- `start`, `end`: the two log statements: file, line, level, message template, whether the message was
  printed, and the printed text. `idx` is the position of the message among the logging calls of the thread.
- `args`: values the tracer recorded for the logging call. They are not reliable: in about a fifth of the
  log statements they do not match the placeholders of the template. For example, with three or more
  placeholders the logging API receives an array and the tracer records the array's object id. Use `text`
  for the printed message.
- `path`: the source lines executed between the two messages, in execution order, as `[file, line]`.
  A line can appear twice when it runs code of two classes, e.g. a line that creates an anonymous class
  (line 66 in the fourth pair of pf4j #670).
- `covers_fault`: the path contains a faulty line, not counting the two log statements, and both messages
  were logged inside the test method.
- `in_test_method`: both messages were logged while the test method itself was running (not in set-up or
  tear-down).

A pair file holds every pair that covers the fault and, per test, up to 500 distinct other pairs.

## Running a bug again

The dataset can be used without running anything. To rerun a bug you need the project's repository, the
JDK named in `meta.json`, and Maven or Gradle. For pf4j #670 (Maven, JDK 17):

```bash
git clone https://github.com/pf4j/pf4j && cd pf4j
git checkout -f 47b006a0be8c3456073587b5d7306510424c3407
git checkout 47b006a0be^ -- pf4j/src/main/java/org/pf4j/asm/ExtensionVisitor.java    # buggy version

# send all log levels to a file (pf4j logs through slf4j-simple)
cat > pf4j/src/test/resources/simplelogger.properties <<'EOF'
org.slf4j.simpleLogger.defaultLogLevel=trace
org.slf4j.simpleLogger.logFile=target/app.log
EOF

T='ExtensionVisitorTest#shouldReadAllAttributesFromCompiledExtension'
F='-DfailIfNoTests=false -Dsurefire.failIfNoSpecifiedTests=false -Djacoco.skip=true'
mvn -B -pl pf4j -am test -Dtest=$T $F                      # fails: expected: <5> but was: <0>
cat pf4j/target/app.log                                       # the six messages

# record the executed lines and rebuild the pairs
mvn -B -pl pf4j -am test -Dtest=$T $F \
  "-DargLine=-javaagent:$PWD/../LogPath-Bugs/pipeline/selogger-0.6.0-asm98.jar=output=$PWD/../trace,format=omni,weave=EXEC+CALL+LINE,exlocation=.m2"
python3 ../LogPath-Bugs/checker/trace_pairs.py ../trace . "$T" 47b006a0be \
  pf4j/src/main/java/org/pf4j/asm/ExtensionVisitor.java
```

`trace_pairs.py` prints each pair's path and `covers_fault`; they match `pairs.jsonl`. Other projects need a
different logging configuration (Logback, Log4j 2, java.util.logging), a different module, or Gradle;
`pipeline/pipeline.py` handles these cases (`run_tests`, `run_tests_gradle`, `inject_argline`).

Rerunning depends on the repositories and their dependencies still being available on GitHub and Maven
Central. The logs and paths in the dataset do not.

## How the bugs were selected

| Step | Script | Count |
|---|---|---|
| Java repositories with ≥ 5 stars, not forks or archived, pushed since 2021-10-22 | `gh_list_repos.py` | 123,344 |
| Maven or Gradle build, ≥ 10 KB of Java, a bug label, a bug issue closed by a merged PR | `gh_screen_api.py` | 4,871 |
| ≥ 1 KLOC, ≥ 1 log call per KLOC, ≥ 10 distinct log statements, ≤ 1 thread reference per KLOC | `sys_screen.py`, `screen.py` | 1,825 |
| Not a course project, example, template, or test suite (read by hand) | | 1,752 |
| Fixes touching 1–3 production files and ≤ 80 lines, with a test and a log call | `gh_mine.py`, `gh_mine_recover.py` | 4,810 candidates |
| Run on the buggy and fixed versions | `sys_run.py`, `pipeline.py` | 4,044 runs |
| Reproduced (fails on buggy, passes on fixed) | | 1,169 |
| A pair of log messages covers a faulty line | `analyse_trace.py`, `fault_coverage.py` | 216 issues |
| Final checks: fixed version passes again, two recorded runs agree, the covering pair lies in the test method, both messages printed | `gh_export.py`, `export_dataset.py` | 170 |
| At most 10 per project | | 116 |

`funnel/repositories.csv` lists every repository from the search with the step where it stopped and why.
`funnel/manual_removed.csv` lists the 73 repositories removed by hand with their category.
`funnel/runs.csv` lists every run with its outcome, and `funnel/bugs.csv` the 216 issues that reached the
final checks.

The scripts are the ones used to build the dataset. They read paths from environment variables (`LRB_WORK`,
`LRB_PIPELINE_OUT`, `LRB_SELOGGER_JAR`) and call the GitHub API through `gh`.

## Checking the dataset

```bash
LRB_REPOS=<directory with the clones, named owner__repo> python3 checker/check_dataset.py dataset
```

The checker shares no code with the pipeline. For every bug it confirms that each printed message occurs in
the application log, that every path line exists in the buggy version, that each path runs from its start
log to its end log, and that every covering path contains a faulty line. Its output for each folder is in
`<folder>/check.jsonl` (0 problems in `dataset/` and `extra/`).

## SELogger

`pipeline/selogger-0.6.0-asm98.jar` is SELogger 0.6.0 (https://github.com/takashi-ishio/selogger, MIT
license, see `pipeline/SELOGGER_LICENSE`) with `pipeline/selogger-asm9.patch` applied and ASM updated to 9.8
so that it can instrument Java 25 class files.

## Citation

To be added.

## License

Data: CC BY 4.0. Code: MIT. Log messages and source references come from the listed projects and
remain under their licenses. See `LICENSE`.
