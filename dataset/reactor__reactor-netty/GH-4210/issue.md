# NullPointerException in SniProvider when AsyncMapping returns null

- Issue: https://github.com/reactor/reactor-netty/issues/4210
- Opened by kwondh5217 on 2026-05-07, closed on 2026-05-29
- Labels: type/bug
- Fix commit: 4e228a48e2440dfbdfe41bd017fcb224ecb3118e

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
When an `AsyncMapping` configured via `setSniAsyncMappings` resolves with `null`, `SniProvider.SniHandler.onLookupComplete` should fail with a clear, diagnosable exception that includes the offending hostname.

## Actual Behavior
`onLookupComplete` checks `future.isSuccess()` but does not validate that `future.getNow()` is non-null. A null result causes a bare `NullPointerException` with no hostname information.

`reactor-netty-core/src/main/java/reactor/netty/tcp/SniProvider.java`:

```java
SslProvider sslProvider = future.getNow();    // can be null
SslHandler sslHandler = null;
try {
    sslHandler = sslProvider.getSslContext().newHandler(ctx.alloc()); // NPE
```

Stack trace:

```
java.lang.NullPointerException: Cannot invoke "reactor.netty.tcp.SslProvider.getSslContext()" because "sslProvider" is null
    at reactor.netty.tcp.SniProvider$SniHandler.onLookupComplete(SniProvider.java:131)
    at io.netty.handler.ssl.AbstractSniHandler.onLookupComplete(AbstractSniHandler.java:191)
```

Two things stand out:

- The javadoc of `Builder.setSniAsyncMappings` does not state that the `AsyncMapping` must return a non-null `SslProvider`, so callers have no signal that null-success is invalid usage.
- Error handling in the same method is inconsistent: the `!future.isSuccess()` path wraps the failure in `DecoderException` with the hostname, while the null-success path produces a bare NPE that loses both the wrapping and the hostname.


## Steps to Reproduce
This was discovered downstream in Spring Boot. See https://github.com/spring-projects/spring-boot/issues/50246

Even though the Spring Boot side can avoid the null, I think this should also be addressed in reactor-netty itself, since other consumers using `setSniAsyncMappings` could easily run into the same bare NPE.

Minimal reproducer:

```java
@Test
public void sniHandlerThrowsBareNpeOnNullSuccess() {
    HttpServer.create()
        .secure(spec -> spec
            .sslContext(defaultSslContext)
            .setSniAsyncMappings((serverName, promise) -> promise.setSuccess(null)))
        .bindNow();
    // Any TLS client that sends an SNI extension triggers the bare NPE.
}
```


## Possible Solution
Add a null check that mirrors the existing failure path in the same method:

```java
SslProvider sslProvider = future.getNow();
if (sslProvider == null) {
    throw new DecoderException("failed to get the SslContext for " + hostname
            + ": the SNI mapping returned null");
}
```

This preserves the hostname in the error message and uses the same `DecoderException` type already used by the failure branch.

Optional follow-up: document the non-null contract on `Builder.setSniAsyncMappings` javadoc.

I'm willing to submit a PR if this is accepted.
## Your Environment
<!--- Include as many relevant details about the environment you experienced the bug in. -->
<!--- Especially, always include the version(s) of Reactor library/libraries you used! -->

* Reactor version(s) used: reactor-netty 1.2.17 (verified `main` branch is also affected)
* Other relevant libraries versions: netty 4.1.x, Spring Boot 3.5.14 (downstream)
* JVM version: Temurin 21
* OS and version: Linux x86_64

## Comment by violetagg on 2026-05-08

@kwondh5217 Yes please go ahead and provide a PR! Thanks a lot!
