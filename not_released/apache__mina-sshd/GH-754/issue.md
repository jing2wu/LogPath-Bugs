# Port Forwarding can't start after Port bind Error

- Issue: https://github.com/apache/mina-sshd/issues/754
- Opened by Linindoo on 2025-05-21, closed on 2025-07-20
- Labels: bug
- Fix commit: 9d1ff5dd0d9b96f91b34ef24a7d759171ea35972

## Report

### Version

sshd-client:2.15.0

### Bug description

It throw `Address already in use: bind` Exception after invoke `startLocalPortForwarding` , and then  invoke `startLocalPortForwarding`  at the same port  again, it throw `TcpipForwarder is closed or closing: Closed` exception, the Port Forwarding can't restart until create new `ClientSession` .

### Actual behavior

Port forwarding was closed after throw `Address already in use: bind` exception,and can't restart in the same `ClientSession`  until create new instance

### Expected behavior

No matter how many times invoke It should throw the same exception `Address already in use: bind` ，it should invoke `startLocalPortForwarding` success after solve the local port conflict problem at the same `ClientSession` instance

### Relevant log output

```Shell
java.net.BindException: Address already in use: bind
	at java.base/sun.nio.ch.Net.bind0(Native Method)
	at java.base/sun.nio.ch.Net.bind(Net.java:555)
	at java.base/sun.nio.ch.ServerSocketChannelImpl.netBind(ServerSocketChannelImpl.java:337)
	at java.base/sun.nio.ch.ServerSocketChannelImpl.bind(ServerSocketChannelImpl.java:294)
	at io.netty.channel.socket.nio.NioServerSocketChannel.doBind(NioServerSocketChannel.java:141)
	at io.netty.channel.AbstractChannel$AbstractUnsafe.bind(AbstractChannel.java:562)
	at io.netty.channel.DefaultChannelPipeline$HeadContext.bind(DefaultChannelPipeline.java:1334)
	at io.netty.channel.AbstractChannelHandlerContext.invokeBind(AbstractChannelHandlerContext.java:506)
	at io.netty.channel.AbstractChannelHandlerContext.bind(AbstractChannelHandlerContext.java:491)
	at io.netty.handler.logging.LoggingHandler.bind(LoggingHandler.java:230)
	at io.netty.channel.AbstractChannelHandlerContext.invokeBind(AbstractChannelHandlerContext.java:506)
	at io.netty.channel.AbstractChannelHandlerContext.bind(AbstractChannelHandlerContext.java:491)
	at io.netty.channel.DefaultChannelPipeline.bind(DefaultChannelPipeline.java:973)
	at io.netty.channel.AbstractChannel.bind(AbstractChannel.java:260)
	at io.netty.bootstrap.AbstractBootstrap$2.run(AbstractBootstrap.java:356)
	at io.netty.util.concurrent.AbstractEventExecutor.runTask(AbstractEventExecutor.java:174)
	at io.netty.util.concurrent.AbstractEventExecutor.safeExecute$$$capture(AbstractEventExecutor.java:167)
	at io.netty.util.concurrent.AbstractEventExecutor.safeExecute(AbstractEventExecutor.java)
	at --- Async.Stack.Trace --- (captured by IntelliJ IDEA debugger)
	at io.netty.util.concurrent.SingleThreadEventExecutor.addTask(SingleThreadEventExecutor.java)
	at io.netty.util.concurrent.SingleThreadEventExecutor.execute(SingleThreadEventExecutor.java:836)
	at io.netty.util.concurrent.SingleThreadEventExecutor.execute0(SingleThreadEventExecutor.java:827)
	at io.netty.util.concurrent.SingleThreadEventExecutor.execute(SingleThreadEventExecutor.java:817)
	at io.netty.bootstrap.AbstractBootstrap.doBind0(AbstractBootstrap.java:352)
	at io.netty.bootstrap.AbstractBootstrap.access$000(AbstractBootstrap.java:53)
	at io.netty.bootstrap.AbstractBootstrap$1.operationComplete(AbstractBootstrap.java:299)
	at io.netty.bootstrap.AbstractBootstrap$1.operationComplete(AbstractBootstrap.java:286)
	at io.netty.util.concurrent.DefaultPromise.notifyListener0(DefaultPromise.java:578)
	at io.netty.util.concurrent.DefaultPromise.notifyListenersNow(DefaultPromise.java:552)
	at io.netty.util.concurrent.DefaultPromise.notifyListeners(DefaultPromise.java:491)
	at io.netty.util.concurrent.DefaultPromise.setValue0(DefaultPromise.java:616)
	at io.netty.util.concurrent.DefaultPromise.setSuccess0(DefaultPromise.java:605)
	at io.netty.util.concurrent.DefaultPromise.trySuccess(DefaultPromise.java:104)
	at io.netty.channel.DefaultChannelPromise.trySuccess(DefaultChannelPromise.java:84)
	at io.netty.channel.AbstractChannel$AbstractUnsafe.safeSetSuccess(AbstractChannel.java:990)
	at io.netty.channel.AbstractChannel$AbstractUnsafe.register0(AbstractChannel.java:516)
	at io.netty.channel.AbstractChannel$AbstractUnsafe.access$200(AbstractChannel.java:429)
	at io.netty.channel.AbstractChannel$AbstractUnsafe$1.run(AbstractChannel.java:486)
	at io.netty.util.concurrent.AbstractEventExecutor.runTask(AbstractEventExecutor.java:174)
	at io.netty.util.concurrent.AbstractEventExecutor.safeExecute$$$capture(AbstractEventExecutor.java:167)
	at io.netty.util.concurrent.AbstractEventExecutor.safeExecute(AbstractEventExecutor.java)
	at --- Async.Stack.Trace --- (captured by IntelliJ IDEA debugger)
	at io.netty.util.concurrent.SingleThreadEventExecutor.addTask(SingleThreadEventExecutor.java)
	at io.netty.util.concurrent.SingleThreadEventExecutor.execute(SingleThreadEventExecutor.java:836)
	at io.netty.util.concurrent.SingleThreadEventExecutor.execute0(SingleThreadEventExecutor.java:827)
	at io.netty.util.concurrent.SingleThreadEventExecutor.execute(SingleThreadEventExecutor.java:817)
	at io.netty.channel.AbstractChannel$AbstractUnsafe.register(AbstractChannel.java:483)
	at io.netty.channel.SingleThreadEventLoop.register(SingleThreadEventLoop.java:89)
	at io.netty.channel.SingleThreadEventLoop.register(SingleThreadEventLoop.java:83)
	at io.netty.channel.MultithreadEventLoopGroup.register(MultithreadEventLoopGroup.java:86)
	at io.netty.bootstrap.AbstractBootstrap.initAndRegister(AbstractBootstrap.java:323)
	at io.netty.bootstrap.AbstractBootstrap.doBind(AbstractBootstrap.java:272)
	at io.netty.bootstrap.AbstractBootstrap.bind(AbstractBootstrap.java:268)
	at org.apache.sshd.netty.NettyIoAcceptor.bindInternal(NettyIoAcceptor.java:151)
	at org.apache.sshd.netty.NettyIoAcceptor.bind(NettyIoAcceptor.java:141)
	at org.apache.sshd.common.forward.DefaultForwarder.doBind(DefaultForwarder.java:937)
	at org.apache.sshd.common.forward.DefaultForwarder.startLocalPortForwarding(DefaultForwarder.java:194)
	at org.apache.sshd.client.session.AbstractClientSession.startLocalPortForwarding(AbstractClientSession.java:446)
	at cn.olange.SshDDemo.main(SshDDemo.java:56)
java.lang.IllegalStateException: TcpipForwarder is closed or closing: Closed
	at org.apache.sshd.common.forward.DefaultForwarder.startLocalPortForwarding(DefaultForwarder.java:186)
	at org.apache.sshd.client.session.AbstractClientSession.startLocalPortForwarding(AbstractClientSession.java:446)
	at cn.olange.SshDDemo.main(SshDDemo.java:63)
```

### Other information

` SshClient client = SshClient.setUpDefaultClient();
        List<KeyExchangeFactory> keyExchangeFactories = BaseBuilder.DEFAULT_KEX_PREFERENCE
            .stream()
            .map(ClientBuilder.DH2KEX)
            .toList();
        client.setKeyExchangeFactories(keyExchangeFactories);
        client.setCipherFactories(new ArrayList<>(NamedFactory.setUpBuiltinFactories(false, BaseBuilder.DEFAULT_CIPHERS_PREFERENCE)));
        client.setMacFactories(new ArrayList<>(NamedFactory.setUpBuiltinFactories(false, BaseBuilder.DEFAULT_MAC_PREFERENCE)));
        client.setSignatureFactories(new ArrayList<>(NamedFactory.setUpBuiltinFactories(false, BaseBuilder.DEFAULT_SIGNATURE_PREFERENCE)));
        client.start();
        ClientSession session = null;
        try {
            session = client
                .connect("root", "host", 22)
                .verify(1000)
                .getSession();
            session.addPasswordIdentity("password");
            session.auth().verify(10000);
            session.startLocalPortForwarding(new SshdSocketAddress("127.0.0.1", 3306), new SshdSocketAddress("127.0.0.1", 3306));

            System.out.println("connection success");
        } catch (IOException e) {
            e.printStackTrace();
            try {
                session.startLocalPortForwarding(new SshdSocketAddress("127.0.0.1", 3306), new SshdSocketAddress("127.0.0.1", 3306));
            } catch (Exception exception) {
                exception.printStackTrace();
            }

        }
    }
`
