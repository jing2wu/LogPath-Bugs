# WebSocket over HTTP/2: server streams.active gauge leaks and connections.active goes negative after the connection closes

- Issue: https://github.com/reactor/reactor-netty/issues/4290
- Opened by LivingLikeKrillin on 2026-07-14, closed on 2026-07-21
- Labels: type/bug
- Fix commit: c430260dad0f816c95974cfeafcd66506a81fdf7

## Report

## Expected Behavior

After a WebSocket-over-HTTP/2 connection closes, the server-side gauges should return to the values they held before it was opened, the same way they do for WebSocket over HTTP/1.1:

- `reactor.netty.http.server.streams.active` back to `0`
- `reactor.netty.http.server.connections.active` unchanged (`0` in a single-connection test)

## Actual Behavior

After the HTTP/2 stream carrying the WebSocket closes:

- `reactor.netty.http.server.streams.active` stays at `1`. It is incremented when the upgrade request is read (`recordOpenStream`) and never decremented, so it leaks by one per WebSocket-over-HTTP/2 connection.
- `reactor.netty.http.server.connections.active` is decremented to `-1`.

The HTTP/1.1 WebSocket path is not affected; its gauges return to `0`.

Root cause (verified against `main`): when the upgrade completes, `WebsocketServerOperations#initHandshaker` replaces the HTTP metrics handler in place with the pass-through `WebsocketHttpServerMetricsHandler` added in #3229 for HTTP/1.1. Its `channelInactive` records `recorder.recordServerConnectionInactive(...)` regardless of the channel type. On an `Http2StreamChannel` the active unit is a stream — counted earlier through `recordOpenStream` — so the close should decrement `streams.active` via `recordClosedStream`. Recording a connection-inactive instead leaves `streams.active` incremented and decrements `connections.active` for a unit that was never counted there (`connections.active` is only incremented for a `SocketChannel`, never for an `Http2StreamChannel`).

The base handler already dispatches correctly — `AbstractHttpServerMetricsHandler#recordInactiveConnectionOrStream` routes an `Http2StreamChannel` to `recordClosedStream` — but the pass-through predates the HTTP/2 WebSocket path (#3691) and overrides `channelInactive` without going through it.

## Steps to Reproduce

The following test fails on `main`; the HTTP/1.1 sibling (`testServerConnectionsWebsocketMicrometer`) passes, which rules out a measurement artifact. It uses `.handle(...)` (Extended CONNECT uses the `CONNECT` method, so routing by `GET` would 404) and waits for the stream to close on the server before reading the gauges (`StreamCloseHandler` is a small `doOnConnection` helper that latches when the server-side stream channel goes inactive).

```java
@Test
void testServerConnectionsWebsocketMicrometerHttp2() throws Exception {
	disposableServer =
			createServer()
					.channelGroup(group)
					.host("127.0.0.1")
					.protocol(HttpProtocol.H2C)
					.http2Settings(spec -> spec.connectProtocolEnabled(true))
					.metrics(true, Function.identity())
					.handle((req, res) -> res.sendWebsocket((in, out) -> out.sendString(Mono.just("Hello World!"))))
					.doOnConnection(cnx -> StreamCloseHandler.INSTANCE.register(cnx.channel()))
					.bindNow();

	String address = formatSocketAddress(disposableServer.address());

	httpClient.protocol(HttpProtocol.H2C)
	          .websocket()
	          .uri("/ws")
	          .handle((in, out) -> in.receive().aggregate().asString())
	          .as(StepVerifier::create)
	          .expectNext("Hello World!")
	          .expectComplete()
	          .verify(Duration.ofSeconds(30));

	// wait until the stream is closed on the server side (pass-through channelInactive ran)
	assertThat(StreamCloseHandler.INSTANCE.awaitClientClosedOnServer()).as("awaitClientClosedOnServer timeout").isTrue();

	Gauge streamsActiveGauge = registry.find(SERVER_STREAMS_ACTIVE).tags(URI, HTTP, LOCAL_ADDRESS, address).gauge();
	Gauge connectionsActiveGauge = registry.find(SERVER_CONNECTIONS_ACTIVE).tags(URI, HTTP, LOCAL_ADDRESS, address).gauge();
	double streamsActive = streamsActiveGauge != null ? streamsActiveGauge.value() : 0d;
	double connectionsActive = connectionsActiveGauge != null ? connectionsActiveGauge.value() : 0d;

	// currently observed: streams.active = 1.0, connections.active = -1.0
	assertThat(streamsActive).isEqualTo(0d);
	assertThat(connectionsActive).isEqualTo(0d);
}
```

## Possible Solution

Have `WebsocketHttpServerMetricsHandler#channelInactive` dispatch on the channel type the way `recordInactiveConnectionOrStream` already does — for an `Http2StreamChannel`, record a stream close (`recordClosedStream`) instead of a connection-inactive. The HTTP/1.1 path keeps its current behavior. I'm happy to open a PR with the fix and this test if you'd like.

## Your Environment

* Reactor version(s) used: reactor-netty-http 1.3.6 (also reproduces on `main` / 1.3.7-SNAPSHOT)
* Other relevant libraries versions: Netty 4.2.15.Final
* JVM version (`java -version`): OpenJDK 25.0.2 (build 25.0.2+10-LTS)
* OS and version: Windows 11

## Comment by violetagg on 2026-07-14

@LivingLikeKrillin Yes, please open a PR. Thanks!
