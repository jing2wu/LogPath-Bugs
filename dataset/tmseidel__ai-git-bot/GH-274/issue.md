# fix(review): propagate bot response write failures

- Issue: https://github.com/tmseidel/ai-git-bot/issues/274
- Opened by SingularityKChen on 2026-07-15, closed on 2026-07-18
- Labels: bug
- Fix commit: 75f372d39f193213a250c505d44642b2c8d54d5c

## Report

## Observed behavior

`CodeReviewService#handleBotCommand` catches every exception, logs it, and returns normally. If the AI response was generated but `RepositoryApiClient#postPullRequestComment` failed, `ReviewWorkflow` can still return `SUCCESS` even though no response reached the pull request.

## Expected behavior

The command handler should keep its detailed log and propagate the failure. The existing workflow orchestrator should then mark the run failed, and the existing bot-level error handling should record the error.

## Provider scope

The failure is in the shared review layer and affects every provider through `RepositoryApiClient`. Provider retry semantics and API clients are intentionally unchanged.

## Relevant code path

`CodeReviewService#handleBotCommand` swallows the exception; `ReviewWorkflow#doBotCommand` therefore returns `WorkflowResult.success("Bot command handled")`.

## Acceptance criteria

- A PR-comment write exception propagates from `handleBotCommand`.
- `ReviewWorkflow` does not return success for that failure.
- The existing orchestrator failure path remains responsible for persisted `FAILED` status.
- Successful command behavior remains unchanged.
- No automatic comment retry is added.
- Focused tests and the full test suite pass.

## Comment by tmseidel on 2026-07-18

bugfix verified in 1.17.0
