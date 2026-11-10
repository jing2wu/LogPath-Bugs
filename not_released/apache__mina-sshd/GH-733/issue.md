# Cannot download file from SFTP in parts - NPE in SftpRemotePathChannel.transferTo (buffer is null)

- Issue: https://github.com/apache/mina-sshd/issues/733
- Opened by chylek-qr on 2025-04-14, closed on 2025-04-14
- Labels: bug
- Fix commit: b5c3b34dbec73477d47a2312773757a307eb7597

## Report

### Version

2.15.0

### Bug description

Hi! There seems to be an issue with the `SftpRemotePathChannel#transferTo` implementation.

Demonstration code, assumes that `ClientSession session` is already obtained, and expects a `source-file` to be present on the SFTP server. In my case, the file is about 256 kB.

```java
SftpFileSystem fileSystem = SftpClientFactory.instance().createSftpFileSystem(session);

Path sourcePath = fileSystem.getPath("source-file");
Path targetPath = Path.of("/tmp/test");

try (FileChannel sourceChannel = FileChannel.open(sourcePath, StandardOpenOption.READ);
     FileChannel targetChannel = FileChannel.open(targetPath, StandardOpenOption.CREATE, StandardOpenOption.WRITE, StandardOpenOption.TRUNCATE_EXISTING)) {
	
	long totalBytes = sourceChannel.size();
	long copiedBytes = 0L;
	
	while (copiedBytes < totalBytes) {
		copiedBytes += sourceChannel.transferTo(targetChannel.position(), /* count = */ 1024, targetChannel);
	}
}
```

I'm copying the data using `FileChannel#transferTo` in a loop, so I can track the progress. The count is only 1024 bytes for demonstration, because it has to be less than half the size of the file downloaded from SFTP to trigger the bug.

Note that `transferFrom` does not have this issue. I always want to call the transfer method on the SftpRemotePathChannel for best performance, so in the real code, I do the following to decide which one to use, depending on whether the destination is local (`sourceFileChannel` is `SftpRemotePathChannel` and transfers **to** a local file) or not (`writer` is `SftpRemotePathChannel` and transfers **from** a local file). Only `transferTo` does not work.

```java
long copyTo(FileChannel writer, long count) throws IOException {
	if (isDestinationLocal) {
		return sourceFileChannel.transferTo(writer.position(), count, writer);
	}
	else {
		return writer.transferFrom(sourceFileChannel, sourceFileChannel.position(), count);
	}
}
````

### Actual behavior

The code successfully copies 2048 bytes (2 iterations of the loop), then throws an exception:
```
java.lang.NullPointerException: Cannot invoke "org.apache.sshd.common.util.buffer.Buffer.available()" because "this.buffer" is null
	at org.apache.sshd.sftp.client.impl.SftpInputStreamAsync.sendRequests(SftpInputStreamAsync.java:245)
	at org.apache.sshd.sftp.client.impl.SftpInputStreamAsync.doRead(SftpInputStreamAsync.java:195)
	at org.apache.sshd.sftp.client.impl.SftpInputStreamAsync.transferTo(SftpInputStreamAsync.java:152)
	at org.apache.sshd.sftp.client.impl.SftpRemotePathChannel.transferTo(SftpRemotePathChannel.java:369)
```

The crash happens in this condition, which is only triggered when `position` > `count`, so it only happens on the 3rd iteration of the loop when `position = 2048` and `count = 1024`.

<img width="715" alt="Image" src="https://github.com/user-attachments/assets/cb28efd2-8da8-4f81-85e1-9b3e99703130" />

The issue seems to be that `fileSize` is set to `count`, i.e. the number of bytes I want to download, and not the actual size of the file on the SFTP server.

### Expected behavior

Download the file in 1024-byte chunks.

### Relevant log output

```Shell

```

### Other information

_No response_

## Comment by tomaswolf on 2025-04-14

Thanks for the report. The bug is at https://github.com/apache/mina-sshd/blob/c5a3aac0ae2b1d6d03f4e05b5d71d9c52f22b7af/sshd-sftp/src/main/java/org/apache/sshd/sftp/client/impl/SftpRemotePathChannel.java#L368C68-L368C72 We should not pass `count` but `position + count`.
