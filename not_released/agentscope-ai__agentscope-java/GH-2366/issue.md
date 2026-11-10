# [Bug]: Streaming: non-chunk chat.completion summary event (MiniMax-M3) doubles accumulated content, halting the agent

- Issue: https://github.com/agentscope-ai/agentscope-java/issues/2366
- Opened by Buktal on 2026-07-23, closed on 2026-07-24
- Labels: bug
- Fix commit: 1a1d3593a512d88b29b9381db4ba3fd5a607934b

## Report

### Summary

Some OpenAI-compatible providers (confirmed with **MiniMax-M3**) emit an extra
non-chunk `chat.completion` **summary** event at the end of a streaming response.
AgentScope does not strip this summary, so `ReasoningContext` accumulates the
summary's `message` on top of the incremental deltas already received. This
**doubles** `reasoning_content` and concatenates `tool_call.arguments` into
`{...}{...}` (invalid JSON). On the next round the malformed payload is sent back
to the model, which returns an empty `choices:[]`, and the agent silently halts.

### Root cause

`OpenAIClient.stream()` emits every parsed `OpenAIResponse` as-is. A summary event
has `object = "chat.completion"`, so `OpenAIResponse.isChunk()` returns `false`
and `OpenAIResponseParser.parseResponse` routes it to `parseCompletionResponse`,
which extracts the **full** `message` (reasoning text + complete tool-call args)
into `ContentBlock`s — identical to what the incremental `delta` chunks already
produced.

`ReasoningContext.processChunk` then appends those blocks to the accumulators that
already hold the delta-accumulated content:

- `ThinkingAccumulator`: reasoning text is appended twice (delta-accumulated full
  text + summary full text).
- `ToolCallsAccumulator`: the summary's complete `arguments` are concatenated onto
  the already-assembled `arguments`, producing `{"skillId":...}{"skillId":...}`.

The loose JSON validation accepts the first object of `{...}{...}`, so the doubled
args survive into the next request, the model rejects it, and the run stops.

### Reproduction

Captured SSE sequence from a real MiniMax-M3 stream (5 incremental
`chat.completion.chunk` events + 1 non-chunk `chat.completion` summary):

1. chunk: `delta.reasoning_content = "The"`
2. chunk: `delta.reasoning_content = " user wants me to ... fetch"`
3. chunk: `delta.reasoning_content = " the data ... Let me start by loading the AIHOT skill."`
4. chunk: `delta.tool_calls[0].function.arguments = "{\"skillId\": \"AIHOT_marketplace\", \"path\": \"SKILL.md\""`
5. chunk: `delta.tool_calls[0].function.arguments = "}"`  (`finish_reason = tool_calls`)
6. **summary**: `object = "chat.completion"`, `message` restates the full reasoning
   text + complete tool-call args (`{"skillId": "AIHOT_marketplace", "path": "SKILL.md"}`),
   plus the real `usage` (only place token counts appear).

The 6th event (summary):

```json
{"id":"06b0ebbde818dbb3769e9726ab05cb9f","choices":[{"finish_reason":"tool_calls","index":0,"message":{"role":"assistant","name":"MiniMax AI","tool_calls":[{"id":"call_function_fo7n64ha38ds_1","type":"function","function":{"name":"load_skill_through_path","arguments":"{\"skillId\": \"AIHOT_marketplace\", \"path\": \"SKILL.md\"}"},"index":0}],"reasoning_content":"The user wants me to generate a daily AI briefing HTML dashboard using the AIHOT skill. Let me load the skill first to understand how to fetch the data, then create the HTML dashboard according to the specifications.\n\nLet me start by loading the AIHOT skill."}}],"object":"chat.completion","usage":{"total_tokens":12078,"prompt_tokens":11977,"completion_tokens":101}}
```

With the current code, feeding these 6 events through `OpenAIClient.stream()` ->
`OpenAIResponseParser` -> `ReasoningContext` yields:
- accumulated reasoning contains `"Let me start by loading"` **twice** (expected once)
- accumulated tool-call `arguments` contains `AIHOT_marketplace` **twice**

### Impact

Any OpenAI-compatible provider that terminates a stream with a non-chunk
`chat.completion` summary event triggers the duplication. The agent stops responding
after the first tool-call round — the user-visible symptom is "MiniMax does not
continue replying". `compat/minimax/MiniMaxFormatter` is currently an empty subclass
of `OpenAIChatFormatter`, so it does not mitigate this.

### Suggested fix

Strip the summary event's `message` at the transport layer, keeping the `choice`
(so `finish_reason` is preserved) and `usage` (the only place real token counts
appear):

```java
// in OpenAIClient.stream() handle block, before sink.next(response)
if (!response.isChunk()) {
    OpenAIChoice summaryChoice = response.getFirstChoice();
    if (summaryChoice != null) {
        summaryChoice.setMessage(null);
    }
}
sink.next(response);
```

This is provider-agnostic (benefits any provider with this quirk) and keeps the
fix at the protocol-normalization layer alongside the existing `[DONE]` filtering
and error detection. A regression test that replays the 6-event trace above
through the real `OpenAIClient.stream()` -> `OpenAIResponseParser` ->
`ReasoningContext` and asserts single-copy reasoning / tool args passes with the
fix and fails without it.

### Environment

- AgentScope Java: 2.0.0 (main, commit `a7008d05`)
- Model: MiniMax-M3 (OpenAI-compatible endpoint)
- JDK: 21

## Comment by oss-maintainer on 2026-07-23

**Issue Evaluation**

Category: `bug` | Status: **Triaged**

Thank you for reporting this issue. It has been classified as a potential bug.

**Next steps:**
- The issue will be verified against the current codebase
- If confirmed, an automated fix proposal may be generated
- Community feedback is welcome

---
*Automated triage by github-manager-bot*
