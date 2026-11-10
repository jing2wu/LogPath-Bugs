# [BUG] LDAP auth broke after upgrading from opensearch:2 to opensearch:3

- Issue: https://github.com/opensearch-project/security/issues/5832
- Opened by dforste on 2025-12-03, closed on 2025-12-17
- Labels: bug, triaged, v3.7.0
- Fix commit: 212c1326192f42b78e3fc7dc6b79040790dcf314

## Report

**What is the bug?**
There are two methods to integrate LDAP auth documented here: https://docs.opensearch.org/latest/security/authentication-backends/ldap/#approach-1-query-the-role-subtree
https://docs.opensearch.org/latest/security/authentication-backends/ldap/#approach-2-use-a-users-attribute-as-the-role-name

Approach 2 no longer works after upgrading. 
The LDAP server(FreeIPA) has all group memberships under the user as memberOf attribute. 

**How can one reproduce the bug?**
Steps to reproduce the behavior:
Use a config similar to: 
```
      authz:
        ldap_roles:
          description: "Authorize using LDAP"
          http_enabled: true
          transport_enabled: true
          authorization_backend:
            type: ldap
            config:
              enable_ssl: false
              enable_start_tls: false
              enable_ssl_client_auth: false
              verify_hostnames: true
              hosts:
                - "freeipa-1:389"
              bind_dn: uid=opensearch,cn=users,cn=accounts,dc=example,dc=com
              password: "${password}"
              userbase: cn=users,cn=accounts,dc=example,dc=com
              usersearch: (uid={0})
              username_attribute: uid
              skip_users:
                - admin
                - kibanaserver
              userroleattribute: memberOf
              rolesearch_enabled: false
              rolebase: cn=groups,cn=accounts,dc=example,dc=com
              rolename: cn
```

**What is the expected behavior?**
Roles to be resolved as they were in opensearch:2

**What is your host/environment?**
 - OS: Linux (docker)
 - Version: 9
 - Plugins (default in the image)

**Do you have any additional context?**
Related Forum posts: 
https://forum.opensearch.org/t/ldap-login-does-not-work-after-upgrade-from-2-19-1-to-3-1-0/25603
https://forum.opensearch.org/t/solved-unable-to-log-in-with-ldap-after-upgrade-to-3-3/27360/4

## Comment by pawelw1 on 2025-12-05

@dforste You have `rolesearch_enabled: false`. Could you try setting this to true? The `false` value is valid for option 2.

## Comment by dforste on 2025-12-06

@pawelw1 Sorry I typed incorrectly. Using a user attribute is the method that is broken. Using the role searching does work. I was correctly working with method 2 before updating and it broke after updating with an exception.

## Comment by pawelw1 on 2025-12-06

@dforste Thanks for clarifying. Could you also tell me what the exact original version of 2.x was, and what your current one, 3.x, is?

## Comment by dforste on 2025-12-08

It was this past week and I was using the latest public.ecr.aws/opensearchproject/opensearch:2 and public.ecr.aws/opensearchproject/opensearch:3 images. I believe these are 2.19.4 and 3.3.2.

## Comment by nibix on 2025-12-09

@dforste would it be possible that you test it against OpenSearch 3.0? That would give us a better idea when the regression happened.

Additionally, one of the forum posts gives this stack trace:

```
[2025-07-07T13:59:45,569,ERROR,o.o.s.a.BackendRegistry  ] [devnode1] Cannot retrieve roles for User [name=admin1, backend_roles=[], requestedTenant=null] from ldap due to OpenSearchSecurityException[java.lang.NullPointerException: Cannot invoke "org.ldaptive.Connection.getProviderConnection()" because the return value of "org.ldaptive.SearchOperation.getConnection()" is null]; nested: NullPointerException[Cannot invoke "org.ldaptive.Connection.getProviderConnection()" because the return value of "org.ldaptive.SearchOperation.getConnection()" is null];
org.opensearch.OpenSearchSecurityException: java.lang.NullPointerException: Cannot invoke "org.ldaptive.Connection.getProviderConnection()" because the return value of "org.ldaptive.SearchOperation.getConnection()" is null
        at org.opensearch.security.auth.ldap.backend.LDAPAuthorizationBackend.addRoles(LDAPAuthorizationBackend.java:1012) ~[?:?]
        at org.opensearch.security.auth.BackendRegistry.authz(BackendRegistry.java:620) ~[?:?]
        at org.opensearch.security.auth.BackendRegistry$5.call(BackendRegistry.java:671) ~[?:?]
        at org.opensearch.security.auth.BackendRegistry$5.call(BackendRegistry.java:660) ~[?:?]
        at com.google.common.cache.LocalCache$LocalManualCache$1.load(LocalCache.java:4860) ~[?:?]
        at com.google.common.cache.LocalCache$LoadingValueReference.loadFuture(LocalCache.java:3551) ~[?:?]
        at com.google.common.cache.LocalCache$Segment.loadSync(LocalCache.java:2302) ~[?:?]
        at com.google.common.cache.LocalCache$Segment.lockedGetOrLoad(LocalCache.java:2177) ~[?:?]
        at com.google.common.cache.LocalCache$Segment.get(LocalCache.java:2068) ~[?:?]
        at com.google.common.cache.LocalCache.get(LocalCache.java:3986) ~[?:?]
        at com.google.common.cache.LocalCache$LocalManualCache.get(LocalCache.java:4855) ~[?:?]
        at org.opensearch.security.auth.BackendRegistry.authcz(BackendRegistry.java:660) ~[?:?]
        at org.opensearch.security.auth.BackendRegistry.authenticate(BackendRegistry.java:393) ~[?:?]
        at org.opensearch.security.filter.SecurityRestFilter.checkAndAuthenticateRequest(SecurityRestFilter.java:306) ~[?:?]
        at org.opensearch.security.ssl.http.netty.Netty4HttpRequestHeaderVerifier.channelRead0(Netty4HttpRequestHeaderVerifier.java:90) ~[?:?]
        at org.opensearch.security.ssl.http.netty.Netty4HttpRequestHeaderVerifier.channelRead0(Netty4HttpRequestHeaderVerifier.java:37) ~[?:?]
        at io.netty.channel.SimpleChannelInboundHandler.channelRead(SimpleChannelInboundHandler.java:99) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:444) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:412) ~[?:?]
        at io.netty.handler.codec.ByteToMessageDecoder.fireChannelRead(ByteToMessageDecoder.java:346) ~[?:?]
        at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:318) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:444) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:412) ~[?:?]
        at io.netty.handler.timeout.IdleStateHandler.channelRead(IdleStateHandler.java:289) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:442) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:412) ~[?:?]
        at io.netty.handler.codec.MessageToMessageDecoder.channelRead(MessageToMessageDecoder.java:107) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:444) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:412) ~[?:?]
        at io.netty.handler.ssl.SslHandler.unwrap(SslHandler.java:1519) ~[?:?]
        at io.netty.handler.ssl.SslHandler.decodeJdkCompatible(SslHandler.java:1377) ~[?:?]
        at io.netty.handler.ssl.SslHandler.decode(SslHandler.java:1428) ~[?:?]
        at io.netty.handler.codec.ByteToMessageDecoder.decodeRemovalReentryProtection(ByteToMessageDecoder.java:530) ~[?:?]
        at io.netty.handler.codec.ByteToMessageDecoder.callDecode(ByteToMessageDecoder.java:469) ~[?:?]
        at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:290) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:444) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:412) ~[?:?]
        at io.netty.channel.DefaultChannelPipeline$HeadContext.channelRead(DefaultChannelPipeline.java:1357) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:440) ~[?:?]
        at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
        at io.netty.channel.DefaultChannelPipeline.fireChannelRead(DefaultChannelPipeline.java:868) ~[?:?]
        at io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:166) ~[?:?]
        at io.netty.channel.nio.NioEventLoop.processSelectedKey(NioEventLoop.java:796) ~[?:?]
        at io.netty.channel.nio.NioEventLoop.processSelectedKeysPlain(NioEventLoop.java:697) ~[?:?]
        at io.netty.channel.nio.NioEventLoop.processSelectedKeys(NioEventLoop.java:660) ~[?:?]
        at io.netty.channel.nio.NioEventLoop.run(NioEventLoop.java:562) ~[?:?]
        at io.netty.util.concurrent.SingleThreadEventExecutor$4.run(SingleThreadEventExecutor.java:998) ~[?:?]
        at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74) ~[?:?]
        at java.base/java.lang.Thread.run(Thread.java:1583) [?:?]
Caused by: java.lang.NullPointerException: Cannot invoke "org.ldaptive.Connection.getProviderConnection()" because the return value of "org.ldaptive.SearchOperation.getConnection()" is null
        at org.ldaptive.SearchOperation.executeSearch(SearchOperation.java:103) ~[?:?]
        at org.ldaptive.SearchOperation.invoke(SearchOperation.java:85) ~[?:?]
        at org.ldaptive.SearchOperation.invoke(SearchOperation.java:15) ~[?:?]
        at org.ldaptive.AbstractOperation.execute(AbstractOperation.java:126) ~[?:?]
        at org.opensearch.security.auth.ldap.util.LdapHelper$1.run(LdapHelper.java:74) ~[?:?]
        at org.opensearch.security.auth.ldap.util.LdapHelper$1.run(LdapHelper.java:58) ~[?:?]
        at java.base/java.security.AccessController.doPrivileged(AccessController.java:571) ~[?:?]
        at org.opensearch.security.auth.ldap.util.LdapHelper.search(LdapHelper.java:58) ~[?:?]
        at org.opensearch.security.auth.ldap.util.LdapHelper.lookup(LdapHelper.java:101) ~[?:?]
        at org.opensearch.security.auth.ldap.backend.LDAPAuthorizationBackend.getRoleFromEntry(LDAPAuthorizationBackend.java:1184) ~[?:?]
        at org.opensearch.security.auth.ldap.backend.LDAPAuthorizationBackend.addRoles(LDAPAuthorizationBackend.java:982) ~[?:?]
        ... 53 more
[2025-07-07T13:59:45,571,INFO ,o.o.s.p.PrivilegesEvaluator] [devnode1] No cluster-level perm match for User [name=admin1, backend_roles=[], requestedTenant=null] Resolved [aliases=[*], allIndices=[*], types=[*], originalRequested=[*], remoteIndices=[]] [Action [cluster:monitor/health]] [RolesChecked [own_index]]. No permissions for [cluster:monitor/health]
```

Is this directly related to the issue? If so, can we ascertain the version of OpenSearch  that produced that stack trace?

## Comment by dforste on 2025-12-09

With this config: 
```
      authz:
        ldap_roles:
          description: "Authorize using LDAP"
          http_enabled: true
          transport_enabled: true
          authorization_backend:
            type: ldap
            config:
              enable_ssl: false
              enable_start_tls: false
              enable_ssl_client_auth: false
              verify_hostnames: true
              hosts:
                - "freeipa-1:389"
              bind_dn: uid=opensearch,cn=users,cn=accounts,dc=example,dc=com
              password: "${password}"
              userbase: cn=users,cn=accounts,dc=example,dc=com
              usersearch: (uid={0})
              username_attribute: uid
              skip_users:
                - admin
                - kibanaserver
              userroleattribute: memberOf
              rolesearch_enabled: false
              rolename: cn
```

I can confirm 3.0.0 works and 3.1.0 doesn't with the following error: 
```
[2025-12-09T20:07:34,521,ERROR,o.o.s.a.BackendRegistry  ] [opensearch-1-local] Cannot retrieve roles for User [name=dforster, backend_roles=[], requestedTenant=null] from ldap due to OpenSearchSecurityException[java.lang.NullPointerException: Cannot invoke "org.ldaptive.Connection.getProviderConnection()" because the return value of "org.ldaptive.SearchOperation.getConnection()" is null]; nested: NullPointerException[Cannot invoke "org.ldaptive.Connection.getProviderConnection()" because the return value of "org.ldaptive.SearchOperation.getConnection()" is null];
org.opensearch.OpenSearchSecurityException: java.lang.NullPointerException: Cannot invoke "org.ldaptive.Connection.getProviderConnection()" because the return value of "org.ldaptive.SearchOperation.getConnection()" is null
	at org.opensearch.security.auth.ldap.backend.LDAPAuthorizationBackend.addRoles(LDAPAuthorizationBackend.java:1012) ~[?:?]
	at org.opensearch.security.auth.BackendRegistry.authz(BackendRegistry.java:620) ~[?:?]
	at org.opensearch.security.auth.BackendRegistry$5.call(BackendRegistry.java:671) ~[?:?]
	at org.opensearch.security.auth.BackendRegistry$5.call(BackendRegistry.java:660) ~[?:?]
	at com.google.common.cache.LocalCache$LocalManualCache$1.load(LocalCache.java:4860) ~[?:?]
	at com.google.common.cache.LocalCache$LoadingValueReference.loadFuture(LocalCache.java:3551) ~[?:?]
	at com.google.common.cache.LocalCache$Segment.loadSync(LocalCache.java:2302) ~[?:?]
	at com.google.common.cache.LocalCache$Segment.lockedGetOrLoad(LocalCache.java:2177) ~[?:?]
	at com.google.common.cache.LocalCache$Segment.get(LocalCache.java:2068) ~[?:?]
	at com.google.common.cache.LocalCache.get(LocalCache.java:3986) ~[?:?]
	at com.google.common.cache.LocalCache$LocalManualCache.get(LocalCache.java:4855) ~[?:?]
	at org.opensearch.security.auth.BackendRegistry.authcz(BackendRegistry.java:660) ~[?:?]
	at org.opensearch.security.auth.BackendRegistry.authenticate(BackendRegistry.java:393) ~[?:?]
	at org.opensearch.security.filter.SecurityRestFilter.checkAndAuthenticateRequest(SecurityRestFilter.java:306) ~[?:?]
	at org.opensearch.security.ssl.http.netty.Netty4HttpRequestHeaderVerifier.channelRead0(Netty4HttpRequestHeaderVerifier.java:90) ~[?:?]
	at org.opensearch.security.ssl.http.netty.Netty4HttpRequestHeaderVerifier.channelRead0(Netty4HttpRequestHeaderVerifier.java:37) ~[?:?]
	at io.netty.channel.SimpleChannelInboundHandler.channelRead(SimpleChannelInboundHandler.java:99) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:444) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:412) ~[?:?]
	at io.netty.handler.codec.ByteToMessageDecoder.fireChannelRead(ByteToMessageDecoder.java:346) ~[?:?]
	at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:318) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:444) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:412) ~[?:?]
	at io.netty.handler.timeout.IdleStateHandler.channelRead(IdleStateHandler.java:289) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:442) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:412) ~[?:?]
	at io.netty.handler.codec.MessageToMessageDecoder.channelRead(MessageToMessageDecoder.java:107) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:444) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:412) ~[?:?]
	at io.netty.handler.ssl.SslHandler.unwrap(SslHandler.java:1519) ~[?:?]
	at io.netty.handler.ssl.SslHandler.decodeJdkCompatible(SslHandler.java:1377) ~[?:?]
	at io.netty.handler.ssl.SslHandler.decode(SslHandler.java:1428) ~[?:?]
	at io.netty.handler.codec.ByteToMessageDecoder.decodeRemovalReentryProtection(ByteToMessageDecoder.java:530) ~[?:?]
	at io.netty.handler.codec.ByteToMessageDecoder.callDecode(ByteToMessageDecoder.java:469) ~[?:?]
	at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:290) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:444) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:412) ~[?:?]
	at io.netty.channel.DefaultChannelPipeline$HeadContext.channelRead(DefaultChannelPipeline.java:1357) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:440) ~[?:?]
	at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:420) ~[?:?]
	at io.netty.channel.DefaultChannelPipeline.fireChannelRead(DefaultChannelPipeline.java:868) ~[?:?]
	at io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:166) ~[?:?]
	at io.netty.channel.nio.NioEventLoop.processSelectedKey(NioEventLoop.java:796) ~[?:?]
	at io.netty.channel.nio.NioEventLoop.processSelectedKeysPlain(NioEventLoop.java:697) ~[?:?]
	at io.netty.channel.nio.NioEventLoop.processSelectedKeys(NioEventLoop.java:660) ~[?:?]
	at io.netty.channel.nio.NioEventLoop.run(NioEventLoop.java:562) ~[?:?]
	at io.netty.util.concurrent.SingleThreadEventExecutor$4.run(SingleThreadEventExecutor.java:998) ~[?:?]
	at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74) ~[?:?]
	at java.base/java.lang.Thread.run(Thread.java:1583) [?:?]
Caused by: java.lang.NullPointerException: Cannot invoke "org.ldaptive.Connection.getProviderConnection()" because the return value of "org.ldaptive.SearchOperation.getConnection()" is null
	at org.ldaptive.SearchOperation.executeSearch(SearchOperation.java:103) ~[?:?]
	at org.ldaptive.SearchOperation.invoke(SearchOperation.java:85) ~[?:?]
	at org.ldaptive.SearchOperation.invoke(SearchOperation.java:15) ~[?:?]
	at org.ldaptive.AbstractOperation.execute(AbstractOperation.java:126) ~[?:?]
	at org.opensearch.security.auth.ldap.util.LdapHelper$1.run(LdapHelper.java:74) ~[?:?]
	at org.opensearch.security.auth.ldap.util.LdapHelper$1.run(LdapHelper.java:58) ~[?:?]
	at java.base/java.security.AccessController.doPrivileged(AccessController.java:571) ~[?:?]
	at org.opensearch.security.auth.ldap.util.LdapHelper.search(LdapHelper.java:58) ~[?:?]
	at org.opensearch.security.auth.ldap.util.LdapHelper.lookup(LdapHelper.java:101) ~[?:?]
	at org.opensearch.security.auth.ldap.backend.LDAPAuthorizationBackend.getRoleFromEntry(LDAPAuthorizationBackend.java:1184) ~[?:?]
	at org.opensearch.security.auth.ldap.backend.LDAPAuthorizationBackend.addRoles(LDAPAuthorizationBackend.java:982) ~[?:?]
	... 53 more
```

## Comment by nibix on 2025-12-09

@dforste Thank you for the update! I believe I could already identify the issue. I will try to get a fix PR ready within the next three days.

The reason is that the `connection` property is not always properly initialized in this code; the conditions seem to be off:

https://github.com/opensearch-project/security/blob/64c3709f683ae00e6051c4bc564683c6ec96ff19/src/main/java/org/opensearch/security/auth/ldap/backend/LDAPAuthorizationBackend.java#L742-L750

## Comment by cwperks on 2025-12-15

[Triage] @nibix thank you for the deep dive, can you attribute the regression to any PR?

## Comment by nibix on 2025-12-16

@cwperks pretty sure that it is #5212 ...

## Comment by dforste on 2026-02-12

@nibix I have tried using userroleattribute: memberOf on the 3.5.0 and still get NPE. 
```
{"type": "opensearch-log", "timestamp": "2026-02-12T17:50:11,978+0000", "level": "TRACE", "component": "o.o.s.a.l.LDAPAuthorizationBackend2", "cluster.name": "test.opensearch", "node.name": "opensearch-test", "message": "roles count total 64", "cluster.uuid": "il4Co70jQUCrUzCJn-bDiw", "node.id": "HIBvUttySYSEkdFs6Kpgww"  }
{"type": "opensearch-log", "timestamp": "2026-02-12T17:50:12,457+0000", "level": "DEBUG", "component": "o.o.s.a.l.LDAPAuthorizationBackend2", "cluster.name": "test.opensearch", "node.name": "opensearch-test", "message": "Roles for dforster -\u003e []", "cluster.uuid": "il4Co70jQUCrUzCJn-bDiw", "node.id": "HIBvUttySYSEkdFs6Kpgww"  }
{"type": "opensearch-log", "timestamp": "2026-02-12T17:50:12,457+0000", "level": "TRACE", "component": "o.o.s.a.l.LDAPAuthorizationBackend2", "cluster.name": "test.opensearch", "node.name": "opensearch-test", "message": "returned user: User [name=dforster, backend_roles=[], requestedTenant=null]", "cluster.uuid": "il4Co70jQUCrUzCJn-bDiw", "node.id": "HIBvUttySYSEkdFs6Kpgww"  }
{"type": "opensearch-log", "timestamp": "2026-02-12T17:50:12,457+0000", "level": "DEBUG", "component": "o.o.s.a.l.LDAPAuthorizationBackend2", "cluster.name": "test.opensearch", "node.name": "opensearch-test", "message": "Unable to fill user roles due to ", "cluster.uuid": "il4Co70jQUCrUzCJn-bDiw", "node.id": "HIBvUttySYSEkdFs6Kpgww", 
"stacktrace": ["java.lang.NullPointerException",
"at com.google.common.base.Preconditions.checkNotNull(Preconditions.java:906) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.collect.ImmutableSet$Builder.add(ImmutableSet.java:520) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.collect.ImmutableSet$Builder.add(ImmutableSet.java:473) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.collect.ImmutableCollection$Builder.addAll(ImmutableCollection.java:477) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.collect.ImmutableSet$Builder.addAll(ImmutableSet.java:544) ~[guava-33.2.1-jre.jar:?]",
"at org.opensearch.security.user.User.withRoles(User.java:175) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.auth.ldap2.LDAPAuthorizationBackend2.addRoles0(LDAPAuthorizationBackend2.java:390) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.auth.ldap2.LDAPAuthorizationBackend2.lambda$addRoles$0(LDAPAuthorizationBackend2.java:123) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.secure_sm.AccessController.doPrivilegedChecked(AccessController.java:110) ~[opensearch-agent-policy-3.5.0.jar:3.5.0]",
"at org.opensearch.security.auth.ldap2.LDAPAuthorizationBackend2.addRoles(LDAPAuthorizationBackend2.java:123) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.auth.BackendRegistry.authz(BackendRegistry.java:746) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.auth.BackendRegistry$5.call(BackendRegistry.java:797) ~[?:?]",
"at org.opensearch.security.auth.BackendRegistry$5.call(BackendRegistry.java:786) ~[?:?]",
"at com.google.common.cache.LocalCache$LocalManualCache$1.load(LocalCache.java:4903) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache$LoadingValueReference.loadFuture(LocalCache.java:3574) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache$Segment.loadSync(LocalCache.java:2316) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache$Segment.lockedGetOrLoad(LocalCache.java:2189) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache$Segment.get(LocalCache.java:2079) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache.get(LocalCache.java:4017) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache$LocalManualCache.get(LocalCache.java:4898) ~[guava-33.2.1-jre.jar:?]",
"at org.opensearch.security.auth.BackendRegistry.authcz(BackendRegistry.java:786) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.auth.BackendRegistry.authenticate(BackendRegistry.java:424) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.filter.SecurityRestFilter.checkAndAuthenticateRequest(SecurityRestFilter.java:365) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.ssl.http.netty.Netty4HttpRequestHeaderVerifier.channelRead0(Netty4HttpRequestHeaderVerifier.java:90) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.ssl.http.netty.Netty4HttpRequestHeaderVerifier.channelRead0(Netty4HttpRequestHeaderVerifier.java:37) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at io.netty.channel.SimpleChannelInboundHandler.channelRead(SimpleChannelInboundHandler.java:99) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:356) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.ByteToMessageDecoder.fireChannelRead(ByteToMessageDecoder.java:361) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:325) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:356) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.timeout.IdleStateHandler.channelRead(IdleStateHandler.java:293) ~[netty-handler-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:354) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.MessageToMessageDecoder.channelRead(MessageToMessageDecoder.java:107) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:356) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.ssl.SslHandler.unwrap(SslHandler.java:1540) ~[netty-handler-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.ssl.SslHandler.decodeJdkCompatible(SslHandler.java:1398) ~[netty-handler-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.ssl.SslHandler.decode(SslHandler.java:1449) ~[netty-handler-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.ByteToMessageDecoder.decodeRemovalReentryProtection(ByteToMessageDecoder.java:545) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.ByteToMessageDecoder.callDecode(ByteToMessageDecoder.java:484) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:296) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:356) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.DefaultChannelPipeline$HeadContext.channelRead(DefaultChannelPipeline.java:1429) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.DefaultChannelPipeline.fireChannelRead(DefaultChannelPipeline.java:918) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:172) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.AbstractNioChannel$AbstractNioUnsafe.handle(AbstractNioChannel.java:445) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.NioIoHandler$DefaultNioRegistration.handle(NioIoHandler.java:388) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.NioIoHandler.processSelectedKey(NioIoHandler.java:596) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.NioIoHandler.processSelectedKeysPlain(NioIoHandler.java:541) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.NioIoHandler.processSelectedKeys(NioIoHandler.java:514) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.NioIoHandler.run(NioIoHandler.java:484) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.SingleThreadIoEventLoop.runIo(SingleThreadIoEventLoop.java:225) [netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.SingleThreadIoEventLoop.run(SingleThreadIoEventLoop.java:196) [netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.util.concurrent.SingleThreadEventExecutor$5.run(SingleThreadEventExecutor.java:1195) [netty-common-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74) [netty-common-4.2.9.Final.jar:4.2.9.Final]",
"at java.base/java.lang.Thread.run(Thread.java:1474) [?:?]"] }
{"type": "opensearch-log", "timestamp": "2026-02-12T17:50:12,459+0000", "level": "ERROR", "component": "o.o.s.a.BackendRegistry", "cluster.name": "test.opensearch", "node.name": "opensearch-test", "message": "Cannot retrieve roles for User [name=dforster, backend_roles=[], requestedTenant=null] from ldap due to OpenSearchSecurityException[java.lang.NullPointerException]; nested: NullPointerException;", "cluster.uuid": "il4Co70jQUCrUzCJn-bDiw", "node.id": "HIBvUttySYSEkdFs6Kpgww" , 
"stacktrace": ["org.opensearch.OpenSearchSecurityException: java.lang.NullPointerException",
"at org.opensearch.security.auth.ldap2.LDAPAuthorizationBackend2.addRoles0(LDAPAuthorizationBackend2.java:395) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.auth.ldap2.LDAPAuthorizationBackend2.lambda$addRoles$0(LDAPAuthorizationBackend2.java:123) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.secure_sm.AccessController.doPrivilegedChecked(AccessController.java:110) ~[opensearch-agent-policy-3.5.0.jar:3.5.0]",
"at org.opensearch.security.auth.ldap2.LDAPAuthorizationBackend2.addRoles(LDAPAuthorizationBackend2.java:123) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.auth.BackendRegistry.authz(BackendRegistry.java:746) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.auth.BackendRegistry$5.call(BackendRegistry.java:797) ~[?:?]",
"at org.opensearch.security.auth.BackendRegistry$5.call(BackendRegistry.java:786) ~[?:?]",
"at com.google.common.cache.LocalCache$LocalManualCache$1.load(LocalCache.java:4903) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache$LoadingValueReference.loadFuture(LocalCache.java:3574) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache$Segment.loadSync(LocalCache.java:2316) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache$Segment.lockedGetOrLoad(LocalCache.java:2189) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache$Segment.get(LocalCache.java:2079) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache.get(LocalCache.java:4017) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.cache.LocalCache$LocalManualCache.get(LocalCache.java:4898) ~[guava-33.2.1-jre.jar:?]",
"at org.opensearch.security.auth.BackendRegistry.authcz(BackendRegistry.java:786) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.auth.BackendRegistry.authenticate(BackendRegistry.java:424) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.filter.SecurityRestFilter.checkAndAuthenticateRequest(SecurityRestFilter.java:365) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.ssl.http.netty.Netty4HttpRequestHeaderVerifier.channelRead0(Netty4HttpRequestHeaderVerifier.java:90) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.ssl.http.netty.Netty4HttpRequestHeaderVerifier.channelRead0(Netty4HttpRequestHeaderVerifier.java:37) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at io.netty.channel.SimpleChannelInboundHandler.channelRead(SimpleChannelInboundHandler.java:99) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:356) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.ByteToMessageDecoder.fireChannelRead(ByteToMessageDecoder.java:361) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:325) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:356) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.timeout.IdleStateHandler.channelRead(IdleStateHandler.java:293) ~[netty-handler-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:354) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.MessageToMessageDecoder.channelRead(MessageToMessageDecoder.java:107) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:356) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.ssl.SslHandler.unwrap(SslHandler.java:1540) ~[netty-handler-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.ssl.SslHandler.decodeJdkCompatible(SslHandler.java:1398) ~[netty-handler-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.ssl.SslHandler.decode(SslHandler.java:1449) ~[netty-handler-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.ByteToMessageDecoder.decodeRemovalReentryProtection(ByteToMessageDecoder.java:545) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.ByteToMessageDecoder.callDecode(ByteToMessageDecoder.java:484) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:296) ~[netty-codec-base-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:356) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.DefaultChannelPipeline$HeadContext.channelRead(DefaultChannelPipeline.java:1429) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.DefaultChannelPipeline.fireChannelRead(DefaultChannelPipeline.java:918) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:172) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.AbstractNioChannel$AbstractNioUnsafe.handle(AbstractNioChannel.java:445) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.NioIoHandler$DefaultNioRegistration.handle(NioIoHandler.java:388) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.NioIoHandler.processSelectedKey(NioIoHandler.java:596) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.NioIoHandler.processSelectedKeysPlain(NioIoHandler.java:541) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.NioIoHandler.processSelectedKeys(NioIoHandler.java:514) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.nio.NioIoHandler.run(NioIoHandler.java:484) ~[netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.SingleThreadIoEventLoop.runIo(SingleThreadIoEventLoop.java:225) [netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.channel.SingleThreadIoEventLoop.run(SingleThreadIoEventLoop.java:196) [netty-transport-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.util.concurrent.SingleThreadEventExecutor$5.run(SingleThreadEventExecutor.java:1195) [netty-common-4.2.9.Final.jar:4.2.9.Final]",
"at io.netty.util.internal.ThreadExecutorMap$2.run(ThreadExecutorMap.java:74) [netty-common-4.2.9.Final.jar:4.2.9.Final]",
"at java.base/java.lang.Thread.run(Thread.java:1474) [?:?]",
"Caused by: java.lang.NullPointerException",
"at com.google.common.base.Preconditions.checkNotNull(Preconditions.java:906) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.collect.ImmutableSet$Builder.add(ImmutableSet.java:520) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.collect.ImmutableSet$Builder.add(ImmutableSet.java:473) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.collect.ImmutableCollection$Builder.addAll(ImmutableCollection.java:477) ~[guava-33.2.1-jre.jar:?]",
"at com.google.common.collect.ImmutableSet$Builder.addAll(ImmutableSet.java:544) ~[guava-33.2.1-jre.jar:?]",
"at org.opensearch.security.user.User.withRoles(User.java:175) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"at org.opensearch.security.auth.ldap2.LDAPAuthorizationBackend2.addRoles0(LDAPAuthorizationBackend2.java:390) ~[opensearch-security-3.5.0.0.jar:3.5.0.0]",
"... 48 more"] }
{"type": "opensearch-log", "timestamp": "2026-02-12T17:50:12,461+0000", "level": "DEBUG", "component": "o.o.s.a.BackendRegistry", "cluster.name": "test.opensearch", "node.name": "opensearch-test", "message": "Rest user 'User [name=dforster, backend_roles=[], requestedTenant=null]' is authenticated", "cluster.uuid": "il4Co70jQUCrUzCJn-bDiw", "node.id": "HIBvUttySYSEkdFs6Kpgww"  }
```
Is there a better way for me to test updates to ensure the PR actually fixes the issue? I run opensearch in docker.

## Comment by tronboto on 2026-04-22

Hey, we're also seeing this issue with the same stack trace after upgrading from 2.19 to 3.6. I've linked the relevant config and debug logs - hopefully that can help.

As mentioned in one of the threads, setting `rolesearch_enabled: true` also fixed it for us, however, we originally disabled this because it can add quite a bit of latency for us in certain circumstances.

[log.txt](https://github.com/user-attachments/files/26966533/log.txt)
[config.txt](https://github.com/user-attachments/files/26966534/config.txt)

And this is the same request but with `rolesearch_enabled: true`:

[log-rolesearch-enabled.txt](https://github.com/user-attachments/files/26967598/log-rolesearch-enabled.txt)

And then here is the same request on a 2.19 cluster (for clarity, `rolesearch_enabled: false`):

[log-2.19.txt](https://github.com/user-attachments/files/26968097/log-2.19.txt)

## Comment by tronboto on 2026-04-23

I think I know what the issue is - will submit a fix later today

## Comment by tronboto on 2026-04-23

PR raised: https://github.com/opensearch-project/security/pull/6112
