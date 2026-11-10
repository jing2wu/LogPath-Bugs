# SSH_FX_NO_SUCH_FILE when reading a dir with a space character at the end

- Issue: https://github.com/apache/mina-sshd/issues/628
- Opened by dadoonet on 2024-11-03, closed on 2024-11-08
- Labels: bug
- Fix commit: 827e81e913fc50aceae736347a99caeee034e162

## Report

### Version

2.14.0

### Bug description

Let say you have the following tree:

```
/
/dirNameWithSpace 
/dirNameWithSpace /foobar.txt
```

If you want to ls the files within the `/dirNameWithSpace ` dir it fails with a `SSH_FX_NO_SUCH_FILE` error.
I attached at the end a test case which reproduces the issue.

### Actual behavior

The stacktrace is:

```
java.io.UncheckedIOException: SFTP error (SSH_FX_NO_SUCH_FILE): No such file or directory

	at org.apache.sshd.sftp.client.impl.SftpIterableDirEntry.iterator(SftpIterableDirEntry.java:67)
	at org.apache.sshd.sftp.client.impl.SftpIterableDirEntry.iterator(SftpIterableDirEntry.java:35)
	at java.base/java.lang.Iterable.spliterator(Iterable.java:101)
	at fr.pilato.test.zombie.sshd.SshdIT.testServingSshFiles(SshdIT.java:68)
	at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:103)
	at java.base/java.lang.reflect.Method.invoke(Method.java:580)
	at org.junit.runners.model.FrameworkMethod$1.runReflectiveCall(FrameworkMethod.java:59)
	at org.junit.internal.runners.model.ReflectiveCallable.run(ReflectiveCallable.java:12)
	at org.junit.runners.model.FrameworkMethod.invokeExplosively(FrameworkMethod.java:56)
	at org.junit.internal.runners.statements.InvokeMethod.evaluate(InvokeMethod.java:17)
	at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
	at org.junit.runners.BlockJUnit4ClassRunner$1.evaluate(BlockJUnit4ClassRunner.java:100)
	at org.junit.runners.ParentRunner.runLeaf(ParentRunner.java:366)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:103)
	at org.junit.runners.BlockJUnit4ClassRunner.runChild(BlockJUnit4ClassRunner.java:63)
	at org.junit.runners.ParentRunner$4.run(ParentRunner.java:331)
	at org.junit.runners.ParentRunner$1.schedule(ParentRunner.java:79)
	at org.junit.runners.ParentRunner.runChildren(ParentRunner.java:329)
	at org.junit.runners.ParentRunner.access$100(ParentRunner.java:66)
	at org.junit.runners.ParentRunner$2.evaluate(ParentRunner.java:293)
	at org.junit.runners.ParentRunner$3.evaluate(ParentRunner.java:306)
	at org.junit.runners.ParentRunner.run(ParentRunner.java:413)
	at org.junit.runner.JUnitCore.run(JUnitCore.java:137)
	at com.intellij.junit4.JUnit4IdeaTestRunner.startRunnerWithArgs(JUnit4IdeaTestRunner.java:69)
	at com.intellij.rt.junit.IdeaTestRunner$Repeater$1.execute(IdeaTestRunner.java:38)
	at com.intellij.rt.execution.junit.TestsRepeater.repeat(TestsRepeater.java:11)
	at com.intellij.rt.junit.IdeaTestRunner$Repeater.startRunnerWithArgs(IdeaTestRunner.java:35)
	at com.intellij.rt.junit.JUnitStarter.prepareStreamsAndStart(JUnitStarter.java:232)
	at com.intellij.rt.junit.JUnitStarter.main(JUnitStarter.java:55)
Caused by: SFTP error (SSH_FX_NO_SUCH_FILE): No such file or directory
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.throwStatusException(AbstractSftpClient.java:272)
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.checkHandleResponse(AbstractSftpClient.java:294)
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.checkHandle(AbstractSftpClient.java:285)
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.openDir(AbstractSftpClient.java:882)
	at org.apache.sshd.sftp.client.impl.SftpDirEntryIterator.<init>(SftpDirEntryIterator.java:61)
	at org.apache.sshd.sftp.client.impl.SftpIterableDirEntry.iterator(SftpIterableDirEntry.java:65)
	... 28 more
```


### Expected behavior

I'm expecting the directory to be read.

### Relevant log output

```Shell
import org.apache.sshd.client.SshClient;
import org.apache.sshd.client.keyverifier.AcceptAllServerKeyVerifier;
import org.apache.sshd.client.session.ClientSession;
import org.apache.sshd.server.SshServer;
import org.apache.sshd.server.keyprovider.SimpleGeneratorHostKeyProvider;
import org.apache.sshd.sftp.client.SftpClient;
import org.apache.sshd.sftp.client.SftpClientFactory;
import org.apache.sshd.sftp.server.SftpFileSystemAccessor;
import org.apache.sshd.sftp.server.SftpSubsystemFactory;
import org.apache.sshd.sftp.server.SftpSubsystemProxy;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

import java.nio.file.Files;
import java.nio.file.InvalidPathException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;

public class SshdIT {

    public static final TemporaryFolder folder = new TemporaryFolder();

    @Test
    public void testServingSshFiles() throws Exception {
        folder.create();
        Path rootTmpDir = Paths.get(folder.getRoot().toURI());

        // Create a txt file where name is "foobar " and content is "Hello, World!"
        Path txtFile = rootTmpDir.resolve("foobar ");
        Files.write(txtFile, "Hello, World!".getBytes());

        Path dirNameWithSpace = rootTmpDir.resolve("dirNameWithSpace ");
        Files.createDirectory(dirNameWithSpace);
        Path foobar = dirNameWithSpace.resolve("foobar.txt");
        Files.write(foobar, "Hello, World!".getBytes());

        // Print all files and directories recursively from the rootTmpDir
        Files.walk(rootTmpDir).forEach(System.out::println);

        SftpSubsystemFactory factory = new SftpSubsystemFactory.Builder()
                .withFileSystemAccessor(new SftpFileSystemAccessor() {
                    @Override
                    public Path resolveLocalFilePath(SftpSubsystemProxy subsystem, Path rootDir, String remotePath) throws InvalidPathException {
                        String path = remotePath;
                        if (remotePath.startsWith("/")) {
                            path = remotePath.substring(1);
                        }
                        return rootTmpDir.resolve(path);
                    }
                })
                .build();

        try (SshServer sshd = SshServer.setUpDefaultServer()) {
            sshd.setHost("localhost");
            sshd.setPasswordAuthenticator((username, password, session) ->
                    "user".equals(username) && "password".equals(password));
            sshd.setKeyPairProvider(new SimpleGeneratorHostKeyProvider(rootTmpDir.resolve("host.ser")));
            sshd.setSubsystemFactories(Collections.singletonList(factory));
            sshd.start();
            try (SshClient client = SshClient.setUpDefaultClient()) {
                client.setServerKeyVerifier(AcceptAllServerKeyVerifier.INSTANCE);
                client.start();
                ClientSession session = client.connect("user", "localhost", sshd.getPort()).verify().getSession();
                session.addPasswordIdentity("password");
                session.auth().verify();
                SftpClient sftpClient = SftpClientFactory.instance().createSftpClient(session);
                sftpClient.readDir("/").spliterator();
                System.out.println("Reading [/] is ok");
                sftpClient.readDir("/dirNameWithSpace ").spliterator();
                System.out.println("Reading [/dirNameWithSpace ] is ko");
            }
        }
    }
}
```


### Other information

_No response_
