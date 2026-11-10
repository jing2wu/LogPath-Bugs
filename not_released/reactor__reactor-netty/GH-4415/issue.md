# HTTP/2: a connection that received GOAWAY keeps its slot in the connection pool until the server closes it

- Issue: https://github.com/reactor/reactor-netty/issues/4415
- Opened by kenluluuuluuuuu on 2026-10-07, closed on 2026-10-12
- Labels: type/bug
- Fix commit: a230865a91facc0289d011044185f326b7f6f12e

## Report

<!--- Provide a general summary of the issue in the title above -->

<!-- Make sure you use a supported version
https://projectreactor.io/support
-->

<!--- /!\ Make sure to follow the Contribution Guidelines and notably for security issues:
https://github.com/reactor/.github/blob/main/CONTRIBUTING.md
https://projectreactor.io/security-policy
-->
<!--- /!\ Questions should be asked on [Gitter](https://gitter.im/reactor/reactor-netty) or [StackOverflow](https://stackoverflow.com/questions/tagged/reactor-netty). -->

## Expected Behavior
<!--- Tell us what you think should happen. -->

When an HTTP/2 connection receives a graceful GOAWAY and its last active stream completes, it should stop counting against `maxConnections`, so the pool can open a replacement connection right away.

## Actual Behavior
<!--- Tell us what happens instead of the expected behavior. -->

`Http2Pool` stops handing out the connection after GOAWAY (since #2396 / #2408) and, once its streams finish, drops it and returns its own permit (`Slot.invalidate()`). The TCP connection, however, was acquired from the parent connection pool, and that pool keeps counting it until the channel closes. Nothing on the client side closes it: the GOAWAY branches in `findConnection` and `evictInBackground` invalidate the slot but, unlike the eviction-predicate branch, don't call `closeChannel`.

So while the server keeps the drained connection open, the pool is full of connections it will never use again. New requests wait for a connection that can't be allocated and fail with `PoolAcquireTimeoutException` after `pendingAcquireTimeout`, until the server closes the socket.

This shows up behind Envoy, for example Istio ingress gateways. On shutdown Envoy sends a graceful GOAWAY (last stream id 2^31-1) and only sends the final GOAWAY and closes the connection after its `drain_timeout`, which defaults to 5s but is often set to minutes. If the pod is killed before that, the client keeps the socket until TCP keepalive detects the dead peer. When many gateway pods drain at once, clients see bursts of `PoolAcquireTimeoutException` for that whole window, even though their remaining connections have plenty of free streams.

With `minConnections > 0` it gets worse: below the minimum, `drainLoop` allocates a new connection for each pending borrower instead of using the healthy connections, so those borrowers are the ones that time out.

Relevant code in 1.3.7:

- GOAWAY branch in `findConnection` (invalidates only): https://github.com/reactor/reactor-netty/blob/v1.3.7/reactor-netty-http/src/main/java/reactor/netty/http/client/Http2Pool.java#L600-L614
- Eviction-predicate branch (closes the channel): https://github.com/reactor/reactor-netty/blob/v1.3.7/reactor-netty-http/src/main/java/reactor/netty/http/client/Http2Pool.java#L618-L634
- GOAWAY branch in `evictInBackground`: https://github.com/reactor/reactor-netty/blob/v1.3.7/reactor-netty-http/src/main/java/reactor/netty/http/client/Http2Pool.java#L537-L545
- The connection comes from the parent pool: https://github.com/reactor/reactor-netty/blob/v1.3.7/reactor-netty-http/src/main/java/reactor/netty/http/client/Http2ConnectionProvider.java#L700-L703

Related: #2396 (stop opening streams after GOAWAY), #3804 (a closed connection that kept counting until the pool was exhausted).

## Steps to Reproduce
<!--- Provide a link to a live example, or an unambiguous set of steps to
reproduce this bug, eg. a unit test. Include code to reproduce, if relevant.
https://stackoverflow.com/help/minimal-reproducible-example -->

The server sends a graceful GOAWAY and keeps the connection open, as Envoy does during `drain_timeout`. Default pool settings apart from `maxConnections(1)`, which makes the result deterministic. The test passes on 1.3.7, i.e. the bug reproduces every time:

```java
    @Test
    public void repoCase() throws Exception {
        Set<Channel> serverConnections = ConcurrentHashMap.newKeySet();
        DisposableServer server =
                HttpServer.create()
                          .protocol(HttpProtocol.H2C)
                          .port(0)
                          .doOnChannelInit((observer, channel, address) -> {
                              serverConnections.add(channel);
                              channel.closeFuture().addListener(f -> serverConnections.remove(channel));
                          })
                          .handle((req, res) -> res.sendString(Mono.just("ok")))
                          .bindNow();

        ConnectionProvider provider =
                ConnectionProvider.builder("repro")
                                  .allocationStrategy(Http2AllocationStrategy.builder().maxConnections(1).build())
                                  .pendingAcquireTimeout(Duration.ofSeconds(2))
                                  .build();
        HttpClient client = HttpClient.create(provider).protocol(HttpProtocol.H2C).port(server.port());

        try {
            assertThat(get(client)).isEqualTo("ok");

            // Graceful GOAWAY (last stream id 2^31-1, like Envoy when draining); the server keeps the connection open
            serverConnections.forEach(ch -> ch.writeAndFlush(
                    new DefaultHttp2GoAwayFrame(Http2Error.NO_ERROR).setExtraStreamIds(Integer.MAX_VALUE)));
            Thread.sleep(500);

            // The drained connection has no active streams and is never used again, but it still holds the only slot
            assertThatThrownBy(() -> get(client)).hasCauseInstanceOf(PoolAcquireTimeoutException.class);
            assertThat(serverConnections).hasSize(1);

            // Only once the server closes it does the pool recover
            serverConnections.forEach(Channel::close);
            Thread.sleep(500);
            assertThat(get(client)).isEqualTo("ok");
        }
        finally {
            provider.disposeLater().block(Duration.ofSeconds(5));
            server.disposeNow();
        }
    }

    private static String get(HttpClient client) {
        return client.get().uri("/").responseContent().aggregate().asString().block(Duration.ofSeconds(5));
    }
```

Imports: `reactor.netty.internal.shaded.reactor.pool.PoolAcquireTimeoutException` (`reactor.pool.PoolAcquireTimeoutException` inside this repository), `io.netty.handler.codec.http2.DefaultHttp2GoAwayFrame`, `io.netty.handler.codec.http2.Http2Error`, and AssertJ.

## Possible Solution
<!--- Not obligatory, but you can suggest a fix/reason for the bug. -->

Either of these fixes it:

1. Release the connection from the parent pool when `Http2Pool` drops a GOAWAY'd connection with no active streams, and keep waiting for the server to close the socket. This matches the HTTP/2 spec most closely.
2. Close the channel once it has received GOAWAY and has no active streams, as the eviction-predicate branch already does. A short delay before closing avoids cutting a stream that was handed out just before the GOAWAY arrived.

As a workaround we register an `Http2Connection.Listener` and close the channel ourselves once it has received GOAWAY and has no active streams. This removed the timeouts during gateway drains for us. We're happy to send a PR for whichever option you prefer.

## Your Environment
<!--- Include as many relevant details about the environment you experienced the bug in. -->
<!--- Especially, always include the version(s) of Reactor library/libraries you used! -->

* Reactor version(s) used: reactor-netty 1.3.7, reactor-core 3.8.7
* Other relevant libraries versions (eg. `netty`, ...): Netty 4.2.18.Final
* JVM version (`java -version`): OpenJDK 25.0.2
* OS and version (eg. `uname -a`): reproduced on macOS 26 (Darwin 25.6.0 arm64); also seen on Linux in production

## Comment by ra-grover on 2026-10-07

In Go's implementation the connection is also proactively closed from the client side when it reaches zero active streams. This was implemented below:
https://github.com/golang/net/commit/d0c6ba3f52d93c7050946b638e6c317c1d7ea069

## Comment by violetagg on 2026-10-08

@kenluluuuluuuuu @ra-grover Would you like to propose a PR?

## Comment by kenluluuuluuuuu on 2026-10-08

@violetagg yes, thanks for triaging the issue. I'll prepare a PR and share once it's ready

## Comment by kenluluuuluuuuu on 2026-10-08

@violetagg which one do you prefer among the options?
We think the 2nd option may be better because the resources can be released, but you may have a better idea of what would work better.

> 1. Release the connection from the parent pool when Http2Pool drops a GOAWAY'd connection with no active streams, and keep waiting for the server to close the socket. This matches the HTTP/2 spec most closely.
> 2. Close the channel once it has received GOAWAY and has no active streams, as the eviction-predicate branch already does. A short delay before closing avoids cutting a stream that was handed out just before the GOAWAY arrived.

## Comment by violetagg on 2026-10-08

@kenluluuuluuuuu Yes, let's go with option 2. What do you think about these?

- Close the channel in all `GOAWAY` branches (findConnection, evictInBackground and destroyPoolableInternal), like the eviction predicate branch does. This includes `Http3Pool.destroyPoolableInternal`.
- No delay is needed, as long as we close only when there are no active streams (see destroyPoolable).

## Comment by kenluluuuluuuuu on 2026-10-08

Sounds good to me. I'm going to work on the fixes and draft a PR later

## Comment by kenluluuuluuuuu on 2026-10-08

I've raised a PR https://github.com/reactor/reactor-netty/pull/4416
Please let me know if there's anything that needs improvement, thanks!
