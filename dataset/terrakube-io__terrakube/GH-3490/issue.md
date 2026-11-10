# Executor discards all Terraform output when the process-stream drain fails ("Failed to capture process output stream")

- Issue: https://github.com/terrakube-io/terrakube/issues/3490
- Opened by jakegroves on 2026-09-01, closed on 2026-09-01
- Labels: bug
- Fix commit: bae9d1d8170f0a64f202195982e7e324cafd806c

## Report

### Bug description 🐞


When a `plan`/`apply`/`destroy` fails **after** Terraform/OpenTofu has already streamed output, the executor throws away everything it captured and reports only the exception message.

Observed with a `plan` on latest `main`: OpenTofu ran fine, produced a plan, then failed late during a `data "external"` read because `python3` is not on the executor's `PATH`:

```
Error: External Program Lookup Failed

  with module.compute_aggregates.data.external.example,
  on ../../modules/example/main.tf line 2, in data "external" "example":
   2:   program = ["python3", "${path.module}/scripts/example.py"]
...
Program: "python3"
Error: exec: "python3": executable file not found in $PATH
```

That full text appears **only in the executor pod logs**. Users see:

| Surface | Output |
| --- | --- |
| Web UI (step output) | `java.lang.RuntimeException: Failed to capture process output stream` — nothing else |
| CLI (`tofu plan`) | stops after the `Refreshing state...` lines; no error, no plan, no diff |
| Executor pod log | everything: full diff, `Changes to Outputs`, the real `Error: External Program Lookup Failed` block |

**Root cause**

1. `executor/pom.xml` uses `terraform-spring-boot-starter` **1.6.0** (bumped in #3470). Its `ProcessLauncher` has a 60s stream-drain watchdog that throws `RuntimeException("Failed to capture process output stream")` if the stdout-reader thread cannot finish draining in time, or if a listener throws:

   ```java
   private static final long STREAM_DRAIN_TIMEOUT_SECONDS = 60;
   ...
   if (!drained.get(STREAM_DRAIN_TIMEOUT_SECONDS, TimeUnit.SECONDS)) {
       throw new RuntimeException("Failed to capture process output stream");
   }
   ```

2. `TerraformExecutorServiceImpl`'s `-json` line consumer does synchronous work on that reader thread for every line / periodic flush: `publishPlanProgress` (HTTP `GET`+`POST` to `/context/v1`, each preceded by a `getJobById`) and `pushLiveStructuredUpdate` (Redis). On a large plan whose rendered diff + diagnostics arrive in a burst at process exit, draining that burst against a busy API exceeds 60s and the library throws.

3. `plan()`/`apply()`/`destroy()` catch the resulting `ExecutionException` and call `setError(exception)` → `generateJobResult(false, "", exception.getMessage())`. The accumulated console buffer (`jobOutput` / `terraformOutput`) is discarded.

4. `UpdateJobStatusImpl.updateStepStatus` persists `saveOutput(output + outputError)`, now just `"" + "java.lang.RuntimeException: Failed to capture process output stream"` — what the Web UI renders. The CLI reads the Redis log stream and stops polling once the step flips to `failed`.

`pushLiveStructuredUpdate` also only catches `JsonProcessingException`, so a null `stepId` in `Map.of(...)` or a Redis transport error can escape onto the reader thread and trip the same watchdog.

**Impact:** any operation that fails after output has started streaming — late data source errors, provider errors after the diff, or a large plan against a loaded API — surfaces as an opaque `Failed to capture process output stream` with none of the real Terraform output or error.


### Steps to reproduce

1. Run a workspace whose config produces a large `plan` (many modules / resources, so the `-json` diff + refresh output is sizeable).
2. Make the plan fail late — e.g. a `data "external"` whose `program` (`python3`, a script, etc.) is not available on the executor, so the error is emitted after the plan has been rendered.
3. Trigger the job from the Web UI (or `terraform`/`tofu` CLI against the Terrakube remote backend).
4. Observe:
   - Web UI step output shows only `java.lang.RuntimeException: Failed to capture process output stream`.
   - CLI output stops after the `Refreshing state...` lines with no error.
   - The executor pod log contains the full plan output and the real `Error: External Program Lookup Failed` / `exec: "python3": executable file not found in $PATH`.

Reliability increases with plan size and API/Redis latency (the 60s drain budget is easier to exceed).

### Expected behavior

- The step output shown in the Web UI and CLI contains everything Terraform/OpenTofu streamed **plus** the real error (`Error: External Program Lookup Failed` in this case), not just `Failed to capture process output stream`.
- A failure in structured-progress publishing or JSON parsing does not kill process-stream capture.

### Example repository

_n/a — reproducible with any large plan that errors after rendering; the `data "external"` + missing `python3` case above is the minimal trigger._


### Anything else?

- Related: #3483 (restores full diagnostic text on the path where the client returns normally; this issue is the path where the client's future throws before the result is built).
