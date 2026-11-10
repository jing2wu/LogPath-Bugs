# fix(review): include current diff in bot follow-ups

- Issue: https://github.com/tmseidel/ai-git-bot/issues/273
- Opened by SingularityKChen on 2026-07-15, closed on 2026-07-18
- Labels: bug
- Fix commit: 239c0ea94afc6a5c3b62bfa484579af495ca2664

## Report

## Observed behavior

After an initial pull-request review, a later `@bot` question reuses the review session but sends only the new comment to the model. If commits were pushed after the initial review, the model can answer from stale code context or report that it has no current diff.

## Expected behavior

Each follow-up in an existing review session should fetch the latest filtered PR diff and include it in the current model input. The persisted conversation should still contain only the original user comment so repeated questions do not accumulate full diff copies.

## Provider scope

This belongs in the shared review layer and should apply to every provider through `RepositoryApiClient`; no provider webhook or API-client behavior needs to change.

## Relevant code path

`CodeReviewService#handleBotCommand` fetches the PR diff only when the session is empty. Existing sessions call `AiClient.chat` with the comment body alone.

## Acceptance criteria

- Existing sessions fetch and send the latest filtered diff with the current question.
- A diff-fetch failure stops the command before any AI call instead of falling back to stale context.
- New-session context behavior remains unchanged.
- The transient diff is capped by the existing review-context limit and carries the existing truncation marker.
- Session history stores the original comment, not the expanded model input.
- Focused tests and the full test suite pass.

## Comment by tmseidel on 2026-07-18

bugfix verified in 1.17.0
