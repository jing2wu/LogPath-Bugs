# [Bug] DashScopeHttpClient.isMultimodalModel() misses qwen3.8-flash (and other 3.8 variants except -max), causing AUTO endpoint routing to the wrong API

- Issue: https://github.com/agentscope-ai/agentscope-java/issues/2981
- Opened by qlprimer on 2026-09-04, closed on 2026-09-05
- Labels: bug
- Fix commit: 3a04de0d1d6853a21eb5533b86b74a5527c19999

## Report

## Describe the bug

`DashScopeHttpClient.isMultimodalModel(String)` only routes models starting with
`qwen3.8-max` to the multimodal-generation endpoint. As of the Qwen3.8 release, the
whole commercial Qwen3.8 series (same as 3.5 / 3.6 / 3.7) is served through the
**multimodal-generation** API on DashScope native endpoints — but `qwen3.8-flash`
does not match any rule, so with the default `EndpointType.AUTO` it is routed to
`/api/v1/services/aigc/text-generation/generation` and the request fails
(URL/endpoint error from the server side).

## Affected version

- `io.agentscope:agentscope-extensions-model-dashscope:2.0.2`
- Also present on `master` as of today (verified against source), so it's not yet fixed.

## Relevant code

`io.agentscope.extensions.model.dashscope.DashScopeHttpClient` — `isMultimodalModel()`
(sources jar of 2.0.2, lines 389–407):

```java
// Reverse exclusions: text-only models whose prefix would otherwise match.
if (lowerModelName.equals("qwen3.6-max-preview")
        || lowerModelName.startsWith("qwen3.7-max")) {
    return false;
}
return lowerModelName.startsWith("qvq")
        || lowerModelName.contains("-vl")
        || lowerModelName.contains("-asr")
        || lowerModelName.startsWith("qwen3.5")   // entire 3.5 series → multimodal
        || lowerModelName.startsWith("qwen3.6")   // entire 3.6 series → multimodal
        || lowerModelName.startsWith("qwen3.7")   // entire 3.7 series (except -max) → multimodal
        || lowerModelName.startsWith("qwen3.8-max") // ← 3.8: only "-max" covered, "-flash" missed
        || lowerModelName.contains("kimi-k2.5")
        || lowerModelName.contains("kimi-k2.6");
Note the inconsistency: for 3.5/3.6/3.7 the rule covers the whole series prefix, while for 3.8 it was narrowed to -max only.

Steps to reproduce
DashScopeChatModel model = DashScopeChatModel.builder()
        .apiKey(System.getenv("DASHSCOPE_API_KEY"))
        .modelName("qwen3.8-flash")
        .stream(true)
        .build();
// AUTO detection → text-generation endpoint → request fails against DashScope,
// because qwen3.8-flash is only available on the multimodal-generation API.
Symptom: call fails with an endpoint/url error from the server (the model is not served by the text-generation API), while qwen3.8-max works fine with the same code.

Expected behavior
isMultimodalModel("qwen3.8-flash") (and other non-max Qwen3.8 commercial variants) should return true, so EndpointType.AUTO routes them to /api/v1/services/aigc/multimodal-generation/generation.

Suggested fix
Align the 3.8 rule with the 3.5/3.6/3.7 convention:

- || lowerModelName.startsWith("qwen3.8-max")
+ || lowerModelName.startsWith("qwen3.8")
(If some future 3.8 text-only variant needs the old text endpoint, add it to the reverse-exclusion block at the top instead, mirroring qwen3.7-max.)

Workaround (current releases)
Explicitly override the routing:

DashScopeChatModel.builder()
        .apiKey(...)
        .modelName("qwen3.8-flash")
        .endpointType(EndpointType.MULTIMODAL)
        .build();

## Comment by ZHCHJ888 on 2026-09-04

Hi, I'd like to work on this issue.Would you mind assigning it to me?
