# Teammate.java: postJSAction runs unconditionally even when skipFieldUpdate=true (requireCliOutputFile strict-mode CLI failure)

- Issue: https://github.com/epam/dm.ai/issues/409
- Opened by IstiN on 2026-07-30, closed on 2026-10-01
- Labels: bug
- Fix commit: f49b84ac7289fac2d30d291497b4466e2be73744

## Report

## Description

When `requireCliOutputFile=true" (strict mode) and the CLI command fails to produce `outputs/response.md", `Teammate.java` correctly detects this, sets `skipFieldUpdate = true`, and later posts an error comment ("⚠️ CLI command execution issue: CLI command executed but did not produce output file...") instead of writing the configured output field. However, `postJSAction` is invoked **before** that check, unconditionally, regardless of `skipFieldUpdate`:

```java
AtomicReference<Exception> postJsError = new AtomicReference<>();
CliExecutionHelper.runWithTimer(timerRunnable, timerIntervalSeconds, () -> {
    try {
        js(expertParams.getPostJSAction())
            .mcp(trackerClient, ai, confluence, null)
            .withJobContext(expertParams, ticket, response)
            .with(TrackerParams.INITIATOR, initiator)
            .with("systemRequest", systemRequestCommentAlias)
            .execute();
    } catch (Exception e) {
        postJsError.set(e);
    }
});
// ... only AFTER this does the code check skipFieldUpdate and decide whether
// to post an error comment instead of processing outputType
```

## Confirmed in production (IstiN/dmtools-agents, po_refinement.json)

`po_refinement.json` runs `agents/scripts/run-agent.sh` as its CLI command and uses `postJSAction: agents/js/closeQuestionTicket.js`, which unconditionally adds a label and calls `jira_move_to_status(..., DONE)` — it has no way to know the CLI failed, because `response` at that point is just whatever string the engine passed in (in this failure case, the "CLI command executed but did not produce output file" error text), and the action has no `skipFieldUpdate`/failure flag to check.

Job log for ticket SOHO-182 (question subtask under project SOHO):

```
[po_refinement] Processing started...
⚠️ CLI command execution issue:
CLI command executed but did not produce output file:
CLI Command: ./agents/scripts/run-agent.sh "/tmp/dmtools_cli_prompt_....txt"
Error: Failed to execute CLI command ...: Command failed (exit code 127): ...
[po_refinement] ✅ Teammate run completed.
```

Despite the CLI genuinely failing (exit 127), `closeQuestionTicket.js`'s postJSAction still ran and moved the subtask straight to Done with the `Answer` field left empty — a real question went unanswered but was reported/logged as a completed success. This is the same class of bug as #309 (preCliJSAction failures not stopping downstream execution), but on the CLI-execution-failure path instead of the preCliJSAction path.

## Expected behaviour

When `skipFieldUpdate` is (or would be) set to `true` due to a strict-mode CLI failure, `postJSAction` should be skipped entirely (mirroring the fix already applied for `preCliJSAction` failures in #309 / PR epam/dm.ai#406) — the engine already knows to post its own error comment; downstream JS actions should not run against a failed/missing response.

## Suggested fix

Move the `skipFieldUpdate`-determining logic (or at least a cheap pre-check of `cliResult.hasOutputResponse()` when `requireCliOutputFile=true`) before the `postJSAction` invocation in `Teammate.java`, and skip `postJSAction` (posting the existing error comment instead) when it's true — consistent with how a `preCliJSAction` failure already short-circuits both `cliCommands` and `postJSAction`.

## Related

- #309 (preCliJSAction failures not stopping execution) — fixed in PR #406, but that fix only covers the `preCliJSAction` hard-stop path, not this `requireCliOutputFile`/`skipFieldUpdate` path.
- Filed alongside a same-symptom-class fix in `IstiN/dmtools-agents` (run-teammate-local.sh not clearing scratch `outputs/`/`input/` dirs between tickets in the single-reused-checkout local-execution model), which independently caused wrong content to leak between unrelated tickets — a different root cause but the same overall "CLI didn't really produce fresh output, but downstream code proceeded as if it had" failure class.
