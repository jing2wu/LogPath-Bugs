# Http2Pool: `computeMaxConcurrentStreams()` returns 0 during TLS handshake, and `deliver()` reuses invalidated slots

- Issue: https://github.com/reactor/reactor-netty/issues/4171
- Opened by markalanrichards on 2026-03-28, closed on 2026-04-02
- Labels: type/bug
- Fix commit: f045bb158cf187a9ec9d3efac0104f90aa9e3154

## Report

## Discovery

When upgrading from 1.3.2 to 1.3.4, as part of just a dependency upgrade only, CI pipeline failures started to repeatedly happen.

```
java.lang.IllegalStateException: Timeout on blocking read for 300000000000 NANOSECONDS
at reactor.core.publisher.BlockingSingleSubscriber.blockingGet(BlockingSingleSubscriber.java:128)
at reactor.core.publisher.Mono.block(Mono.java:1800)
...
Caused by: java.util.concurrent.TimeoutException: Timeout on blocking read for 300000000000 NANOSECONDS
```

A test suite that executed with many test threads running at once was seeing request timeouts for maybe 1% of requests; but whilst the exact test failing may change the failure was always happening when running the full suite. However, no sign on the Load Balancer side of any degredation to the server. The HttpClient was created with HTTP11 and H2 protocols. I'm not very familiar with the innards of this library so rather than just report this blind; I asked Claude to checkout the repo, compare the differences between 1.3.2 (which reverting back to solved the timeouts) and 1.3.4 to find the bug.

This is what Claude Opus 4.6 found and I hope you don't mind this otherwise AI generated issue and I apologise if this output is sending you down a rabbit hole.
Regardless of the below, the experience with the tests suggests there is a bug and by asking Claude to generate a patch for this in our application; the tests started passing again.


## Expected Behavior

When connecting to a TLS+H2 endpoint with `Http2AllocationStrategy.maxConcurrentStreams(100)` configured:

1. Each H2 connection should allow up to `min(pool.maxConcurrentStreams, server MAX_CONCURRENT_STREAMS)` concurrent streams, even if the `Http2FrameCodec` has not yet been added to the pipeline at `Slot` creation time.
2. `Borrower.deliver()` should never deliver a borrower to an invalidated slot, and should never call `deactivate()` on an invalidated slot (which would reinsert a dead connection into the pool).

## Actual Behavior

**Problem 1 — H2 streams serialize to one-at-a-time:**

`Slot.computeMaxConcurrentStreams()` returns `0` when the `Http2FrameCodec` is not yet in the Netty pipeline (TLS handshake still in progress). `availableStreams()` interprets `maxConcurrentStreams == 0` as "HTTP/1.1 mode" and limits the slot to exactly 1 concurrent stream. The `H2MaxConcurrentStreamsHandler` (added in #4106) cannot recover this because during the initial SETTINGS frame the channel `OWNER` is a `PendingConnectionObserver`, not a `DisposableAcquire`, so the update is silently dropped. The slot stays at `maxConcurrentStreams=0` permanently.

In 1.3.2 this was masked because `canOpenStream()` re-read the value from the live `Http2FrameCodec` on every delivery rather than relying on a cached field.

**Problem 2 — Intermittent 5-minute hangs under concurrent load (invalidated slot reuse):**

The drain loop (running off the event loop) increments `ACQUIRED` and schedules `deliver()` via `eventLoop.execute()`. Between dispatch and delivery, the slot can be invalidated (channel closes). `deliver()` only checks `canOpenStream()`, which returns `true` for an invalidated slot with `concurrency=0` and `maxConcurrentStreams > 0`. The borrower is delivered a dead connection and hangs.

Even when `canOpenStream()` returns `false`, the `else` branch calls `deactivate()` on the invalidated slot, reinserting a dead slot into the pool's `connections` queue.

Both problems disappear when downgrading to 1.3.2.

## Steps to Reproduce

### Problem 1 — Unit test demonstrating `maxConcurrentStreams` stuck at 0

```java
@Test
void computeMaxConcurrentStreamsFallsBackForH2WithoutFrameCodec() {
    // Channel with SslHandler reporting "h2" but NO Http2FrameCodec (mid-handshake)
    SslHandler mockSslHandler = Mockito.mock(SslHandler.class);
    Mockito.when(mockSslHandler.applicationProtocol()).thenReturn(ApplicationProtocolNames.HTTP_2);
    EmbeddedChannel channel = new EmbeddedChannel(new TestChannelId());
    channel.pipeline().addFirst(mockSslHandler);

    Http2AllocationStrategy strategy = Http2AllocationStrategy.builder()
            .maxConnections(1)
            .maxConcurrentStreams(100)
            .build();
    PoolBuilder<Connection, PoolConfig<Connection>> poolBuilder =
            PoolBuilder.from(Mono.just(Connection.from(channel)))
                       .idleResourceReuseLruOrder()
                       .maxPendingAcquireUnbounded()
                       .sizeBetween(0, 1);
    Http2Pool http2Pool = poolBuilder.build(config -> new Http2Pool(config, strategy));

    try {
        Http2Pool.Slot slot = http2Pool.createSlot(Connection.from(channel));
        // FAILS: maxConcurrentStreams is 0 instead of 100
        assertThat(slot.maxConcurrentStreams)
                .as("H2 slot without frame codec should use pool.maxConcurrentStreams as fallback")
                .isEqualTo(100);
    }
    finally {
        channel.finishAndReleaseAll();
        Connection.from(channel).dispose();
    }
}
```

### Problem 1 — Integration test demonstrating serialization with real H2 server

```java
@Test
void concurrentRequestsOverH2() throws Exception {
    SelfSignedCertificate cert = new SelfSignedCertificate();
    DisposableServer server = HttpServer.create()
            .port(0)
            .secure(spec -> spec.sslContext(
                Http2SslContextSpec.forServer(cert.certificate(), cert.privateKey())))
            .protocol(HttpProtocol.H2, HttpProtocol.HTTP11)
            .route(routes -> routes.get("/test", (req, resp) -> resp.sendString(Mono.just("OK"))))
            .bindNow();

    ConnectionProvider provider = ConnectionProvider.builder("test")
            .maxConnections(10)
            .allocationStrategy(Http2AllocationStrategy.builder()
                .maxConnections(10)
                .maxConcurrentStreams(100)
                .build())
            .pendingAcquireTimeout(Duration.ofSeconds(30))
            .build();

    HttpClient client = HttpClient.create(provider)
            .protocol(HttpProtocol.HTTP11, HttpProtocol.H2)
            .secure(spec -> spec.sslContext(
                Http2SslContextSpec.forClient()
                    .configure(b -> b.trustManager(InsecureTrustManagerFactory.INSTANCE))));

    try {
        int concurrentRequests = 50;
        AtomicInteger successCount = new AtomicInteger();
        CountDownLatch latch = new CountDownLatch(concurrentRequests);

        for (int i = 0; i < concurrentRequests; i++) {
            client.get()
                .uri("https://localhost:" + server.port() + "/test")
                .responseContent().aggregate().asString()
                .doOnNext(r -> successCount.incrementAndGet())
                .doFinally(s -> latch.countDown())
                .subscribe();
        }

        // With the bug, requests serialize (1 per connection) and this takes > 30s or times out
        boolean completed = latch.await(30, TimeUnit.SECONDS);
        assertThat(completed).as("all requests should complete within 30s").isTrue();
        assertThat(successCount.get()).isEqualTo(concurrentRequests);
    }
    finally {
        provider.disposeLater().block(Duration.ofSeconds(5));
        server.disposeNow();
    }
}
```

### Problem 2 — Unit test demonstrating invalidated slot reuse

```java
@SuppressWarnings("unchecked")
@Test
void deliverDoesNotDeactivateInvalidatedSlot() throws Exception {
    EmbeddedChannel channel = new EmbeddedChannel(new TestChannelId(),
            Http2FrameCodecBuilder.forClient().build(),
            new Http2MultiplexHandler(new ChannelHandlerAdapter() {}));
    PoolBuilder<Connection, PoolConfig<Connection>> poolBuilder =
            PoolBuilder.from(Mono.just(Connection.from(channel)))
                       .idleResourceReuseLruOrder()
                       .maxPendingAcquireUnbounded()
                       .sizeBetween(0, 1);
    Http2AllocationStrategy strategy = Http2AllocationStrategy.builder()
            .maxConnections(1)
            .maxConcurrentStreams(10)
            .build();
    Http2Pool http2Pool = poolBuilder.build(config -> new Http2Pool(config, strategy));

    try {
        List<PooledRef<Connection>> acquired = new ArrayList<>();
        http2Pool.acquire().doOnNext(acquired::add).block(Duration.ofSeconds(1));
        assertThat(acquired).hasSize(1);

        Http2Pool.Slot originalSlot = ((Http2Pool.Http2PooledRef) acquired.get(0)).slot;

        // Second acquire — drain loop increments ACQUIRED and schedules deliver()
        http2Pool.acquire().subscribe(acquired::add);

        // Invalidate the slot BEFORE deliver() runs on the event loop.
        // Simulates the race where a channel closes between dispatch and delivery.
        originalSlot.invalidate();

        // Run the pending deliver() task
        channel.runPendingTasks();

        // The invalidated slot must NOT be in the connections queue.
        // Without a fix, deliver() calls deactivate() on the invalidated slot,
        // reinserting a dead connection into the pool.
        Field connectionsField = Http2Pool.class.getDeclaredField("connections");
        connectionsField.setAccessible(true);
        ConcurrentLinkedQueue<Http2Pool.Slot> connections =
                (ConcurrentLinkedQueue<Http2Pool.Slot>) connectionsField.get(http2Pool);
        assertThat(connections)
                .as("invalidated slot must not be reinserted via deactivate()")
                .doesNotContain(originalSlot);
    }
    finally {
        channel.finishAndReleaseAll();
        Connection.from(channel).dispose();
    }
}
```

## Possible Solution

### Problem 1

In `Slot.computeMaxConcurrentStreams()`, when the frame codec is absent but the `SslHandler` has already negotiated `"h2"` via ALPN, fall back to `pool.maxConcurrentStreams` instead of `0`. This preserves the correct `0` for HTTP/1.1 connections.

```diff
 private int computeMaxConcurrentStreams() {
     ChannelHandlerContext frameCodec = http2FrameCodecCtx();
     if (frameCodec != null && http2MultiplexHandlerCtx() != null) {
         int maxActiveStreams = ((Http2FrameCodec) frameCodec.handler())
             .connection().local().maxActiveStreams();
         return pool.maxConcurrentStreams == -1 ? maxActiveStreams :
             Math.min(pool.maxConcurrentStreams, maxActiveStreams);
     }
+    if (ApplicationProtocolNames.HTTP_2.equals(applicationProtocol)
+            && pool.maxConcurrentStreams != -1) {
+        return pool.maxConcurrentStreams;
+    }
     return 0;
 }
```

When `pool.maxConcurrentStreams == -1` (unlimited), there is no configured cap to fall back to, so `0` (conservative single-stream) is correct until `updateMaxConcurrentStreams()` fires from a SETTINGS frame.

### Problem 2

In `Borrower.deliver()`, check `slot.get()` (the `AtomicBoolean` invalidation flag) before proceeding. Skip `deactivate()` for invalidated slots to prevent reinserting dead connections.

```diff
 void deliver(Http2PooledRef poolSlot, boolean alreadyReserved) {
     assert poolSlot.slot.connection.channel().eventLoop().inEventLoop();

     int effectiveConcurrency = poolSlot.slot.concurrency() - (alreadyReserved ? 1 : 0);
-    if (!poolSlot.slot.canOpenStream(effectiveConcurrency)) {
+    boolean canOpen = poolSlot.slot.canOpenStream(effectiveConcurrency);
+    boolean slotInvalidated = poolSlot.slot.get();
+    if (!canOpen || slotInvalidated) {
         if (alreadyReserved) {
             poolSlot.slot.decrementConcurrencyAndGet();
         }
-        else {
+        else if (!slotInvalidated) {
             poolSlot.slot.deactivate();
         }
         ACQUIRED.decrementAndGet(pool);
         pool.addPending(pool.pending, this, true);
         return;
     }
```

## Your Environment

* Reactor version(s) used: reactor-netty-http **1.3.4** (regression from 1.3.2)
* Other relevant libraries versions: Netty 4.1.x (as pulled by reactor-netty 1.3.4), Spring Boot 3.4.x
* JVM version: OpenJDK 21
* OS and version: Linux (observed on both Amazon Linux 2 and macOS)

Related PRs that introduced the regression:
- #4106 — replaced per-delivery `updateMaxConcurrentStreams()` with push-based `H2MaxConcurrentStreamsHandler` (removed the safety net that masked Problem 1)
- #4051 — refactored drain loop to schedule `deliver()` via `eventLoop.execute()` (created the race window for Problem 2)
- #4099 — fixed `ACQUIRED` counter rollback on deliver rejection (partial fix, did not address the invalidation race)

## Comment by violetagg on 2026-03-31

@markalanrichards Thanks for reaching out.

> Other relevant libraries versions: Netty 4.1.x (as pulled by reactor-netty 1.3.4), Spring Boot 3.4.x

Reactor Netty 1.3.x depends on Netty 4.2.x. Downgrading to Netty 4.1.x is on your own risk.

Release notes https://github.com/reactor/reactor-netty/releases/tag/v1.3.0

Spring Boot 3.4.x/3.5.x depends on Reactor Netty 1.2.x and Netty 4.1.x
Spring Boot 4 depends on Reactor Netty 1.3.x and Netty 4.2.x

## Comment by markalanrichards on 2026-03-31

@violetagg 

Part of the AI fun: I think that's Claude adding a general comment here (being unnecessarily chatty about the world) and when it was trained, Spring Boot 3 was probably prevalent. -

I asked it to emulate the problem in test in a fresh git checkout of the reactor-netty repo standalone (no Spring) and it probably lost context that the original application the was discovered in was upgrading from Spring Boot 4.0.2 to 4.0.4 .

I didn't mention Spring in the discovery; as whilst it was part of an upgrade of Spring Boot; it was in a maven submodule that didn't include any Spring dependencies except reactor-netty (it was just version managed by Spring Boot dependencies pom) (for a test client used by junit). I think the netty version being used is 4.2.12

## Comment by violetagg on 2026-03-31

@markalanrichards 

> Problem 1 — Unit test demonstrating maxConcurrentStreams stuck at 0

This is not a correct junit test because of the channel pipeline (see below for more explanation)

> Problem 1 — Integration test demonstrating serialization with real H2 server

This test doesn't reproduce the problem - it always shows 100 max concurrent streams and this is the expectation. Why?
See the logs that are produced by the test (they are chronological and are sorted by the channel id `843ef9c8 `):

`Http2Pool` asks `Http11Pool` for a connection

```
14:05:37.569 [reactor-http-nio-2] DEBUG r.netty.transport.TransportConnector - [843ef9c8] Connecting to [localhost/127.0.0.1:53480].
14:05:37.573 [reactor-http-nio-2] DEBUG r.n.r.DefaultPooledConnectionProvider - [843ef9c8, L:/127.0.0.1:53497 - R:localhost/127.0.0.1:53480] Registering pool release on close event for channel
14:05:37.574 [reactor-http-nio-2] DEBUG r.n.r.PooledConnectionProvider - [843ef9c8, L:/127.0.0.1:53497 - R:localhost/127.0.0.1:53480] Channel connected, now: 5 active connections, 0 inactive connections 0 pending acquire requests.
14:05:37.661 [reactor-http-nio-2] DEBUG r.netty.http.client.HttpClientConfig - [843ef9c8, L:/127.0.0.1:53497 - R:localhost/127.0.0.1:53480] Negotiated application-level protocol [h2]
14:05:37.661 [reactor-http-nio-2] DEBUG r.n.r.DefaultPooledConnectionProvider - [843ef9c8, L:/127.0.0.1:53497 - R:localhost/127.0.0.1:53480] onStateChange(PooledConnection{channel=[id: 0x843ef9c8, L:/127.0.0.1:53497 - R:localhost/127.0.0.1:53480]}, [connected])
14:05:37.677 [reactor-http-nio-2] DEBUG r.n.r.DefaultPooledConnectionProvider - [843ef9c8, L:/127.0.0.1:53497 - R:localhost/127.0.0.1:53480] onStateChange(PooledConnection{channel=[id: 0x843ef9c8, L:/127.0.0.1:53497 - R:localhost/127.0.0.1:53480]}, [configured])
```

Once the `TLS` handshake finishes, the protocol is known and the pipeline is configured, `Http11Pool` gives the connection to the `Http2Pool`, at that point the max concurrent streams are known - it is either `Integer.MAX_VALUE` (the default value) or the value that the server sent with `Settings` frame, or as it is in this case a configuration provided with the connection pool.

```
14:05:37.678 [reactor-http-nio-2] DEBUG reactor.netty.http.client.Http2Pool - [843ef9c8, L:/127.0.0.1:53497 - R:localhost/127.0.0.1:53480] Max concurrent streams for this channel [100]
14:05:37.678 [reactor-http-nio-2] DEBUG reactor.netty.http.client.Http2Pool - [843ef9c8, L:/127.0.0.1:53497 - R:localhost/127.0.0.1:53480] Channel activated
```

`Max concurrent streams for this channel [100]` - this is a new log that I added to the SNAPSHOT so that we have this information in a debug mode.

You configured the pool with max connections 10, so 10 connections are opened in parallel in order to serve the first 10 requests:

```
14:05:37.569 [reactor-http-nio-6] DEBUG r.netty.transport.TransportConnector - [4020cc7d] Connecting to [localhost/127.0.0.1:53480].
14:05:37.569 [reactor-http-nio-4] DEBUG r.netty.transport.TransportConnector - [cbac0759] Connecting to [localhost/127.0.0.1:53480].
14:05:37.569 [reactor-http-nio-8] DEBUG r.netty.transport.TransportConnector - [db52bb34] Connecting to [localhost/127.0.0.1:53480].
14:05:37.569 [reactor-http-nio-2] DEBUG r.netty.transport.TransportConnector - [843ef9c8] Connecting to [localhost/127.0.0.1:53480].
14:05:37.570 [reactor-http-nio-10] DEBUG r.netty.transport.TransportConnector - [46f91b65] Connecting to [localhost/127.0.0.1:53480].
14:05:37.572 [reactor-http-nio-4] DEBUG r.netty.transport.TransportConnector - [3e5d19ef] Connecting to [localhost/127.0.0.1:53480].
14:05:37.572 [reactor-http-nio-6] DEBUG r.netty.transport.TransportConnector - [a2c94ac5] Connecting to [localhost/127.0.0.1:53480].
14:05:37.572 [reactor-http-nio-2] DEBUG r.netty.transport.TransportConnector - [201a488b] Connecting to [localhost/127.0.0.1:53480].
14:05:37.572 [reactor-http-nio-8] DEBUG r.netty.transport.TransportConnector - [c6e43c59] Connecting to [localhost/127.0.0.1:53480].
14:05:37.572 [reactor-http-nio-10] DEBUG r.netty.transport.TransportConnector - [5d2a0bb2] Connecting to [localhost/127.0.0.1:53480].
```

## Comment by markalanrichards on 2026-03-31

@violetagg 
Sorry, I had some reservations about asking AI to check in to this; I hope it didn't waste too much of your time.
There does still seem to be a bug from 1.3.2 to 1.3.4; as the version change breaks our builds.
If I get a chance today I'll try to make more sense of it and recheck the testing of Claude's attempt to fix it.

## Comment by markalanrichards on 2026-04-01

@violetagg 


Retesting, still finding that 1.3.2 works and 1.3.4 fails with unexplained timeouts.

Sorry for the further AI content here, but Claude's fix does seem to work; so it hopefully has found something in what it offered.

Does the following AI content help?

There is still a real issue with HTTP/1.1 connections through the H2 pool. We've narrowed it down to a zombie slot race in `deliver()`.

## The behavioral change (1.3.2 to 1.3.4)

`Slot.availableStreams()` returns 1 for `max=0, concurrency=0`:

```java
int availableStreams(int concurrency) {
    int max = this.maxConcurrentStreams;
    if (max == 0) {
        return concurrency == 0 ? 1 : 0;  // returns 1 for idle HTTP/1.1 slots
    }
    ...
}
```

In 1.3.2, `canOpenStream()` returned `false` for connections without `Http2FrameCodec`. In 1.3.4, `canOpenStream()` delegates to `availableStreams()` which returns 1 for `max=0, concurrency=0` — making invalidated HTTP/1.1 zombie slots eligible for re-selection by `findConnection()`.

## The race

```
Event loop                                Drain thread
──────────                                ────────────
deliver():
  incrementConcurrency (→1)
  deactivate() → queue.offer(slot)
  actual.onNext() → HTTP/1.1 →
    invalidate → destroyPoolable →
    decrementConcurrency (→0)             findConnection() → queue.poll(slot)
                                           concurrency=0, max=0
                                           availableStreams(0)=1 → TRUE
                                           dispatch borrower
  slot.invalidate()
  removeSlot() (already polled!)
                                          deliver(zombie) → same channel to 2nd caller
```

`findConnection()` does not check `slot.get()` (the `AtomicBoolean` invalidation flag). The zombie slot passes all existing checks: `isActive()=true`, `canOpenStream()=true`.

## Test

This test uses the existing `Http2PoolTest` patterns. It creates an HTTP/1.1 slot (no `Http2FrameCodec` in the pipeline), acquires and invalidates it, and shows that `canOpenStream(0)` still returns `true` on the dead slot:

```java
@Test
void invalidatedHttp11SlotStillPassesCanOpenStream() {
    // HTTP/1.1 channel — no Http2FrameCodec, so maxConcurrentStreams=0
    EmbeddedChannel channel = new EmbeddedChannel(new TestChannelId(), true, false);
    PoolBuilder<Connection, PoolConfig<Connection>> poolBuilder =
            PoolBuilder.from(Mono.just(Connection.from(channel)))
                       .idleResourceReuseLruOrder()
                       .maxPendingAcquireUnbounded()
                       .sizeBetween(0, 1);
    Http2AllocationStrategy strategy = Http2AllocationStrategy.builder()
            .maxConnections(1)
            .maxConcurrentStreams(100)
            .build();
    Http2Pool http2Pool = poolBuilder.build(config -> new Http2Pool(config, strategy));

    try {
        PooledRef<Connection> ref = http2Pool.acquire().block(Duration.ofSeconds(1));
        assertThat(ref).isNotNull();

        Http2Pool.Slot slot = ((Http2Pool.Http2PooledRef) ref).slot;

        // HTTP/1.1 slot: maxConcurrentStreams=0 (no frame codec)
        assertThat(slot.maxConcurrentStreams).isZero();

        // Invalidate the slot (simulating one-shot HTTP/1.1 usage)
        ref.invalidate().block(Duration.ofSeconds(1));
        channel.runPendingTasks();

        // Slot is invalidated
        assertThat(slot.get()).as("slot should be invalidated").isTrue();

        // BUG: canOpenStream(0) returns true for the invalidated slot.
        // availableStreams(0) with max=0 returns 1, so canOpenStream=true.
        // findConnection() would select this zombie slot for a new borrower.
        assertThat(slot.canOpenStream(0)).as("zombie slot passes canOpenStream").isTrue();
        assertThat(slot.availableStreams(0)).as("availableStreams returns 1 for dead slot").isEqualTo(1);

        // The slot is dead (invalidated) but looks alive to findConnection().
        // Neither findConnection() nor deliver() check slot.get().
    }
    finally {
        channel.finishAndReleaseAll();
        Connection.from(channel).dispose();
    }
}
```

## Suggested fix

Check `slot.get()` in `Borrower.deliver()`:

```diff
 void deliver(Http2PooledRef poolSlot, boolean alreadyReserved) {
     assert poolSlot.slot.connection.channel().eventLoop().inEventLoop();

     int effectiveConcurrency = poolSlot.slot.concurrency() - (alreadyReserved ? 1 : 0);
-    if (!poolSlot.slot.canOpenStream(effectiveConcurrency)) {
+    boolean canOpen = poolSlot.slot.canOpenStream(effectiveConcurrency);
+    boolean slotInvalidated = poolSlot.slot.get();
+    if (!canOpen || slotInvalidated) {
         if (alreadyReserved) {
             poolSlot.slot.decrementConcurrencyAndGet();
         }
-        else {
+        else if (!slotInvalidated) {
             poolSlot.slot.deactivate();
         }
         ACQUIRED.decrementAndGet(pool);
         pool.addPending(pool.pending, this, true);
         return;
     }
```

Alternatively, `findConnection()` could check `slot.get()` alongside the existing `isActive()` and `goAwayReceived()` checks.

We patched `deliver()` with this guard and our intermittent 5-minute timeouts (HTTP/1.1 through the H2 pool) were eliminated.

## Comment by violetagg on 2026-04-02

@markalanrichards Thanks for the detailed description. Would you be able to verify PR #4180?
