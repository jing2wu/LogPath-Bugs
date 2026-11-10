# [Bug]:sse请求模型，模型的requestid未返回

- Issue: https://github.com/agentscope-ai/agentscope-java/issues/2197
- Opened by 707348125 on 2026-07-14, closed on 2026-07-30
- Labels: bug, area/core/model
- Fix commit: 5700e5fedeacb3ab0418d5b64028334339cc70e8

## Report

流式请求发生异常时，错误响应里没有返回模型请求id。

SSE-error 场景：DashScopeHttpClient.stream() 把 error 响应的 request_id 传成了 null（框架 bug）
框架未透传 body，服务端根本没回可解析响应，客户端侧无 request_id

java  版本1.0.12
