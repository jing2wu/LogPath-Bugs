# HttpClient with H2+ HTTP/1.1 fallback sometimes throws IOExceptionfrom SimpleDequePoolwhen server only supports HTTP/1.1

- Issue: https://github.com/reactor/reactor-netty/issues/4251
- Opened by yikuo123 on 2026-06-10, closed on 2026-06-23
- Labels: type/bug
- Fix commit: 63fe670db7c0284a91d5cf3bc2f4a04f8bcf4812

## Report

When configuring reactor-netty's HttpClient with both HttpProtocol .H2 and Http Protocol .HTTP11 (i.e., allowing HTTP/2 with fallback to HTTP/1.1), requests to servers that only support HTTP/1.1 sometimes fail with:

```
java.io.IOException: Error while acquiring from reactor.netty.internal.shaded.reactor.pool.SimpleDequePool@...
```

This does not​ happen when using only Http Protocol HTTP1.1 or omitting .protocol() entirely. The issue appears to be related to connection pooling in the HTTP/2 path.

## Steps to Reproduce

Configure the WebClient with:

```java
ConnectionProvider connectionProvider = ConnectionProvider
    .builder("test")
    .maxConnections(500)
    .maxIdleTime(Duration.ofSeconds(180))
    .evictInBackground(Duration.ofSeconds(360))
    .lifo()
    .build();

HttpClient httpClient = HttpClient.create(connectionProvider)
    .secure()
    .protocol(HttpProtocol.H2, HttpProtocol.HTTP11)
    .http2Settings(http2 -> http2.pingAckTimeout(Duration.ofMillis(2000)).pingAckDropThreshold(3));

WebClient client = WebClient.builder()
    .clientConnector(new ReactorClientHttpConnector(httpClient))
    .build();
```

And then make repeated requests to an endpoint that only supports HTTP/1.1.

Observe intermittent failures with the above exception.

## Expected Behavior

Requests should succeed transparently via HTTP/1.1 fallback when the server does not support HTTP/2. No pool-related errors should occur.

## Actual Behavior

IOException during connection acquisition from SimpleDequePool. The error originates from Http2Pool(see stack trace).

```
Original Stack Trace:
		at org.springframework.web.reactive.function.client.ExchangeFunctions$DefaultExchangeFunction.lambda$wrapException$0(ExchangeFunctions.java:139)
		at reactor.core.publisher.MonoErrorSupplied.subscribe(MonoErrorSupplied.java:56)
		at reactor.core.publisher.Mono.subscribe(Mono.java:4569)
		at reactor.core.publisher.FluxOnErrorResume$ResumeSubscriber.onError(FluxOnErrorResume.java:104)
		at reactor.core.publisher.FluxPeek$PeekSubscriber.onError(FluxPeek.java:225)
		at reactor.core.publisher.FluxPeek$PeekSubscriber.onError(FluxPeek.java:225)
		at reactor.core.publisher.FluxPeek$PeekSubscriber.onError(FluxPeek.java:225)
		at reactor.core.publisher.MonoNext$NextSubscriber.onError(MonoNext.java:94)
		at reactor.core.publisher.MonoFlatMapMany$FlatMapManyMain.onError(MonoFlatMapMany.java:206)
		at reactor.core.publisher.SerializedSubscriber.onError(SerializedSubscriber.java:125)
		at reactor.core.publisher.FluxRetryWhen$RetryWhenMainSubscriber.whenError(FluxRetryWhen.java:230)
		at reactor.core.publisher.FluxRetryWhen$RetryWhenOtherSubscriber.onError(FluxRetryWhen.java:282)
		at reactor.core.publisher.FluxContextWrite$ContextWriteSubscriber.onError(FluxContextWrite.java:123)
		at reactor.core.publisher.FluxConcatMapNoPrefetch$FluxConcatMapNoPrefetchSubscriber.maybeOnError(FluxConcatMapNoPrefetch.java:326)
		at reactor.core.publisher.FluxConcatMapNoPrefetch$FluxConcatMapNoPrefetchSubscriber.onNext(FluxConcatMapNoPrefetch.java:211)
		at reactor.core.publisher.FluxContextWrite$ContextWriteSubscriber.onNext(FluxContextWrite.java:109)
		at reactor.core.publisher.SinkManyEmitterProcessor.drain(SinkManyEmitterProcessor.java:480)
		at reactor.core.publisher.SinkManyEmitterProcessor$EmitterInner.drainParent(SinkManyEmitterProcessor.java:624)
		at reactor.core.publisher.FluxPublish$PubSubInner.request(FluxPublish.java:879)
		at reactor.core.publisher.FluxContextWrite$ContextWriteSubscriber.request(FluxContextWrite.java:138)
		at reactor.core.publisher.FluxConcatMapNoPrefetch$FluxConcatMapNoPrefetchSubscriber.request(FluxConcatMapNoPrefetch.java:336)
		at reactor.core.publisher.FluxContextWrite$ContextWriteSubscriber.request(FluxContextWrite.java:138)
		at reactor.core.publisher.Operators$DeferredSubscription.request(Operators.java:1740)
		at reactor.core.publisher.FluxRetryWhen$RetryWhenMainSubscriber.onError(FluxRetryWhen.java:197)
		at reactor.core.publisher.MonoCreate$DefaultMonoSink.error(MonoCreate.java:206)
		at reactor.netty.http.client.HttpClientConnect$MonoHttpConnect$ClientTransportSubscriber.onError(HttpClientConnect.java:336)
		at reactor.core.publisher.MonoCreate$DefaultMonoSink.error(MonoCreate.java:206)
		at reactor.netty.http.client.Http2ConnectionProvider$DisposableAcquire.onError(Http2ConnectionProvider.java:353)
		at reactor.core.publisher.FluxContextWrite$ContextWriteSubscriber.onError(FluxContextWrite.java:123)
		at reactor.netty.http.client.Http2Pool$Borrower.fail(Http2Pool.java:905)
		at reactor.netty.http.client.Http2Pool.lambda$drainLoop$2(Http2Pool.java:493)
		at reactor.core.publisher.FluxDoOnEach$DoOnEachSubscriber.onError(FluxDoOnEach.java:186)
		at reactor.core.publisher.FluxMap$MapConditionalSubscriber.onError(FluxMap.java:265)
		at reactor.core.publisher.MonoCreate$DefaultMonoSink.error(MonoCreate.java:206)
		at reactor.netty.resources.DefaultPooledConnectionProvider$DisposableAcquire.run(DefaultPooledConnectionProvider.java:258)
		at reactor.netty.resources.DefaultPooledConnectionProvider$DisposableAcquire.onNext(DefaultPooledConnectionProvider.java:199)
		at reactor.netty.resources.DefaultPooledConnectionProvider$DisposableAcquire.onNext(DefaultPooledConnectionProvider.java:115)
		at reactor.core.publisher.FluxContextWrite$ContextWriteSubscriber.onNext(FluxContextWrite.java:109)
		at reactor.netty.internal.shaded.reactor.pool.AbstractPool$Borrower.deliver(AbstractPool.java:496)
		at reactor.netty.internal.shaded.reactor.pool.SimpleDequePool.lambda$drainLoop$8(SimpleDequePool.java:382)
		at reactor.core.scheduler.ImmediateScheduler.schedule(ImmediateScheduler.java:53)
		at reactor.netty.internal.shaded.reactor.pool.SimpleDequePool.drainLoop(SimpleDequePool.java:382)
		at reactor.netty.internal.shaded.reactor.pool.SimpleDequePool.pendingOffer(SimpleDequePool.java:629)
		at reactor.netty.internal.shaded.reactor.pool.SimpleDequePool.doAcquire(SimpleDequePool.java:307)
		at reactor.netty.internal.shaded.reactor.pool.AbstractPool$Borrower.request(AbstractPool.java:440)
		at reactor.core.publisher.FluxContextWrite$ContextWriteSubscriber.request(FluxContextWrite.java:138)
		at reactor.netty.resources.DefaultPooledConnectionProvider$DisposableAcquire.onSubscribe(DefaultPooledConnectionProvider.java:226)
		at reactor.core.publisher.FluxContextWrite$ContextWriteSubscriber.onSubscribe(FluxContextWrite.java:103)
		at reactor.netty.internal.shaded.reactor.pool.SimpleDequePool$QueueBorrowerMono.subscribe(SimpleDequePool.java:746)
		at reactor.core.publisher.InternalMonoOperator.subscribe(InternalMonoOperator.java:75)
		at reactor.netty.resources.DefaultPooledConnectionProvider$DisposableAcquire.run(DefaultPooledConnectionProvider.java:255)
		at io.netty.util.concurrent.AbstractEventExecutor.runTask(AbstractEventExecutor.java:148)
		at io.netty.util.concurrent.AbstractEventExecutor.safeExecute(AbstractEventExecutor.java:141)
		at io.netty.util.concurrent.SingleThreadEventExecutor.runAllTasks(SingleThreadEventExecutor.java:535)
		at io.netty.channel.SingleThreadIoEventLoop.run(SingleThreadIoEventLoop.java:201)
		at io.netty.util.concurrent.SingleThreadEventExecutor$5.run(SingleThreadEventExecutor.java:1195)
		at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74)
		at io.netty.util.concurrent.FastThreadLocalRunnable.run(FastThreadLocalRunnable.java:30)
		at java.base/java.lang.Thread.run(Thread.java:1474)
Caused by: java.io.IOException: Error while acquiring from reactor.netty.internal.shaded.reactor.pool.SimpleDequePool@6509082e
	at reactor.netty.resources.DefaultPooledConnectionProvider$DisposableAcquire.run(DefaultPooledConnectionProvider.java:258)
	at reactor.netty.resources.DefaultPooledConnectionProvider$DisposableAcquire.onNext(DefaultPooledConnectionProvider.java:199)
	at reactor.netty.resources.DefaultPooledConnectionProvider$DisposableAcquire.onNext(DefaultPooledConnectionProvider.java:115)
	at reactor.core.publisher.FluxContextWrite$ContextWriteSubscriber.onNext(FluxContextWrite.java:109)
	at reactor.netty.internal.shaded.reactor.pool.AbstractPool$Borrower.deliver(AbstractPool.java:496)
	at reactor.netty.internal.shaded.reactor.pool.SimpleDequePool.lambda$drainLoop$8(SimpleDequePool.java:382)
	at reactor.core.scheduler.ImmediateScheduler.schedule(ImmediateScheduler.java:53)
	at reactor.netty.internal.shaded.reactor.pool.SimpleDequePool.drainLoop(SimpleDequePool.java:382)
	at reactor.netty.internal.shaded.reactor.pool.SimpleDequePool.pendingOffer(SimpleDequePool.java:629)
	at reactor.netty.internal.shaded.reactor.pool.SimpleDequePool.doAcquire(SimpleDequePool.java:307)
	at reactor.netty.internal.shaded.reactor.pool.AbstractPool$Borrower.request(AbstractPool.java:440)
	at reactor.core.publisher.FluxContextWrite$ContextWriteSubscriber.request(FluxContextWrite.java:138)
	at reactor.netty.resources.DefaultPooledConnectionProvider$DisposableAcquire.onSubscribe(DefaultPooledConnectionProvider.java:226)
	at reactor.core.publisher.FluxContextWrite$ContextWriteSubscriber.onSubscribe(FluxContextWrite.java:103)
	at reactor.netty.internal.shaded.reactor.pool.SimpleDequePool$QueueBorrowerMono.subscribe(SimpleDequePool.java:746)
	at reactor.core.publisher.InternalMonoOperator.subscribe(InternalMonoOperator.java:75)
	at reactor.netty.resources.DefaultPooledConnectionProvider$DisposableAcquire.run(DefaultPooledConnectionProvider.java:255)
	at io.netty.util.concurrent.AbstractEventExecutor.runTask(AbstractEventExecutor.java:148)
	at io.netty.util.concurrent.AbstractEventExecutor.safeExecute(AbstractEventExecutor.java:141)
	at io.netty.util.concurrent.SingleThreadEventExecutor.runAllTasks(SingleThreadEventExecutor.java:535)
	at io.netty.channel.SingleThreadIoEventLoop.run(SingleThreadIoEventLoop.java:201)
	at io.netty.util.concurrent.SingleThreadEventExecutor$5.run(SingleThreadEventExecutor.java:1195)
	at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74)
	at io.netty.util.concurrent.FastThreadLocalRunnable.run(FastThreadLocalRunnable.java:30)
	at java.base/java.lang.Thread.run(Thread.java:1474)
```

## Your Environment
<!--- Include as many relevant details about the environment you experienced the bug in. -->
<!--- Especially, always include the version(s) of Reactor library/libraries you used! -->

* Reactor version(s) used:

reactor-netty 1.3.5

* Other relevant libraries versions (eg. `netty`, ...):
* JVM version (`java -version`):

openjdk 25.0.1 2025-10-21 LTS
OpenJDK Runtime Environment Temurin-25.0.1+8 (build 25.0.1+8-LTS)
OpenJDK 64-Bit Server VM Temurin-25.0.1+8 (build 25.0.1+8-LTS, mixed mode, sharing)

* OS and version (eg. `uname -a`):
* 
Linux iZbp13zobg49l6ha5nowh1Z 6.12.0-124.27.1.el10_1.x86_64 #1 SMP PREEMPT_DYNAMIC Tue Jan 13 07:47:29 EST 2026 x86_64 GNU/Linux

## Comment by LivingLikeKrillin on 2026-06-13

The failure surfaces through `Http2Pool` but originates in the parent pool. The message is `Error while acquiring from …SimpleDequePool` with **no** `". Max active streams is reached."` suffix, which is `DefaultPooledConnectionProvider.run()` (1.3.5 line 258) — the `!c.isActive() && retried` branch. So the parent pool handed out a **dead connection twice in a row**, exhausting the single built-in re-acquire retry.

**Why it reproduces with `.protocol(H2, HTTP11)` + `pingAckTimeout` but not with plain HTTP/1.1** (refs are 1.3.5):

1. That config makes `Http2ConnectionProvider.PooledConnectionAllocator` install an **idle-only** `Http11EvictionPredicate` on the parent pool (`Http2ConnectionProvider` 646-652; predicate body 685-695 — idle time only, no `isActive()`).
2. In `PooledConnectionProvider` (626-632), supplying a custom `evictionPredicate` *replaces* the built-in liveness predicate (`!channel.isActive() || !isPersistent()`, `DefaultPooledConnectionProvider` 624-625) instead of composing with it — the `else` branch uses `.or(...)`, the custom-predicate branch does not.
3. A parent that dies while idle isn't proactively removed either: `registerClose` only invalidates when the owner is a `DisposableAcquire`, and a released/idle connection's owner is NOOP (`DefaultPooledConnectionProvider` 329-347).

So a dead idle parent is never evicted at acquire, gets delivered, and a second one trips line 258. Without `pingAckTimeout` (or without H2) no custom predicate is installed, the liveness check survives, and the client recovers — which matches the report that plain HTTP/1.1 is fine.

**Deterministic reproduction** (no race needed, since dead *idle* connections stay in the pool): open 2 pooled connections, close their channels while idle, then issue one more request.

| config | result |
|---|---|
| plain HTTP/1.1 | recovers (allocates a fresh connection) |
| plain HTTP/1.1 + a custom `evictionPredicate` | **`IOException: Error while acquiring`** |
| H2 + HTTP11, no `pingAckTimeout` | recovers |
| H2 + HTTP11 + `pingAckTimeout` (this report) | **`IOException: Error while acquiring`** |

The second row (no HTTP/2 at all) reproduces the same `IOException` as soon as a custom `evictionPredicate` is set, which suggests the issue is the eviction-predicate composition rather than anything HTTP/2-specific. I reproduced this on 1.3.5; the relevant code looks unchanged through current `main`.

Since this is assigned to you I won't jump ahead, but I already have a deterministic failing test for it and I'd be glad to open a PR if that would help.

## Comment by violetagg on 2026-06-13

@LivingLikeKrillin Yes please open a PR. Thanks!
