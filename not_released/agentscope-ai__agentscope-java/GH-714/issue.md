# [Bug]:RAGFlowClient中重试机制无法正确处理

- Issue: https://github.com/agentscope-ai/agentscope-java/issues/714
- Opened by liuxh613 on 2026-02-04, closed on 2026-08-28
- Labels: bug, area/ext/rag
- Fix commit: 6b535067a463c81fc65f9c9ded9b9471d363f014

## Report

java.lang.IllegalStateException: closed
        at okio.RealBufferedSource.select(RealBufferedSource.kt:244)
        at okhttp3.internal._UtilJvmKt.readBomAsCharset(-UtilJvm.kt:88)
        at okhttp3.ResponseBody.string(ResponseBody.kt:190)
        at io.agentscope.core.rag.integration.ragflow.RAGFlowClient.lambda$retrieve$1(RAGFlowClient.java:219)
        at reactor.core.publisher.MonoCallable$MonoCallableSubscription.request(MonoCallable.java:134)
        at reactor.core.publisher.FluxMapFuseable$MapFuseableSubscriber.request(FluxMapFuseable.java:172)
        at reactor.core.publisher.Operators$MultiSubscriptionSubscriber.set(Operators.java:2361)
        at reactor.core.publisher.FluxOnErrorResume$ResumeSubscriber.onSubscribe(FluxOnErrorResume.java:75)
        at reactor.core.publisher.FluxMapFuseable$MapFuseableSubscriber.onSubscribe(FluxMapFuseable.java:96)
        at reactor.core.publisher.MonoCallable.subscribe(MonoCallable.java:48)
        at reactor.core.publisher.Mono.subscribe(Mono.java:4569)
        at reactor.core.publisher.Mono.block(Mono.java:1772)
错误发生在RAGFlowClient第219行：response.body().string()。这个问题是因为：

1、响应体只能读取一次 - 一旦调用了 response.body().string()，响应流就被消费了
2、重试机制可能导致连接关闭 - 在重试过程中，之前的响应连接被关闭
3、try-with-resources 自动关闭 - try (Response response = ...) 会自动关闭响应
问题在于当网络超时或连接问题发生时，重试机制可能无法正确处理已经部分读取的响应。

## Comment by Ycymac on 2026-08-09

I would like to work on this issue. I traced the current RAGFlowClient retry path and found that the final non-success response can be closed by RetryInterceptor before retrieve() reads its body, which surfaces as an IllegalStateException: closed. I plan to make the response lifecycle retry-safe and add a focused retry-enabled regression test.

## Comment by Ycymac on 2026-08-09

已完成修复并提交草稿 PR：#2631。

根因是 `RetryInterceptor` 在 `finally` 中关闭了准备返回给上层的最终 5xx 响应，导致 `retrieve()` 读取响应体时抛出 `IllegalStateException: closed`。本次改为按响应所有权判断：仅关闭拦截器内部废弃、未返回的响应，最终响应继续由调用方读取并关闭。

已新增可稳定覆盖该场景的回归测试；RAGFlow 模块 97 个测试及仓库级 Spotless 检查均通过。仓库全量测试另受 Windows 符号链接权限影响，在 `agentscope-core` 的两个既有测试处停止，相关情况已在 PR 中如实说明。欢迎审阅。

## Comment by Ycymac on 2026-08-09

补充 PR #2631 的 CI 状态：首轮 [GitHub Actions](https://github.com/agentscope-ai/agentscope-java/actions/runs/31291131574) 在无关的 `agentscope-harness` 模块中停止，`HarnessAgentDynamicHookBuilderTest.disableDynamicSkills_freezesRepositoriesIntoStaticMiddleware` 在 JUnit 清理 `@TempDir` 时遇到 `DirectoryNotEmptyException`（812 tests、0 failures、1 cleanup error）。同一次运行中，RAGFlow 模块被标记为 `SKIPPED`，Windows 构建随后因矩阵 fail-fast 被取消。

License、Module Sync 和 CLA 均已通过，本地 RAGFlow 模块测试为 97/97。由于外部贡献者没有 Actions 重跑权限，烦请维护者协助重跑 PR #2631 的 CI。

CI follow-up: the first workflow run stopped during JUnit `@TempDir` cleanup in the unrelated `agentscope-harness` module (`DirectoryNotEmptyException`; 812 tests, 0 failures, 1 cleanup error). The RAGFlow module was marked `SKIPPED`, and the Windows matrix job was then canceled by fail-fast. Since external contributors cannot rerun repository workflows, a maintainer rerun would be appreciated.

## Comment by Ycymac on 2026-08-09

补充状态：PR #2631 已在不修改代码和提交 SHA（`ac7c997a`）的情况下重新触发 CI。新一轮 [GitHub Actions](https://github.com/agentscope-ai/agentscope-java/actions/runs/31291933858) 中，Ubuntu、Windows、License 和 Module Sync 均已通过，CLA 与 Codecov 也为成功状态；本地针对首轮偶发失败的 `HarnessAgentDynamicHookBuilderTest` 重跑结果为 11/11 通过。

因此，之前请求维护者协助重跑 CI 的事项已经解决，不再需要重跑。PR #2631 已转为 Ready for review，目前等待维护者评审。
