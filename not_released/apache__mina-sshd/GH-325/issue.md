# exceptions in SftpFileSystemProvider on Files.delete( Path p)

- Issue: https://github.com/apache/mina-sshd/issues/325
- Opened by sijskes on 2023-03-02, closed on 2023-03-24
- Labels: bug
- Fix commit: 2779bbc8d15308ce09b9661df5298c035cc70624

## Report

### Version

sshd-sftp 2.9.2

### Bug description

While using a Path on SftpFileSystemProvider:

Exceptions thrown in on Files.delete( Path p), when deleting symbolic links.

  * When deleting a symbolic links to non-existing file.
  * When deleting a symbolic link to existing directory
  * When deleting a symbolic link to existing file
 

### Actual behavior

probably the links are followed, and the link is handled like the linkdestination. this causes exceptions.

### Expected behavior

No exception but deletion of  the symbolic link.


### Relevant log output

_No response_

### Other information

Server OpenSSH_8.9p1 Ubuntu-3ubuntu0.1

## Comment by sijskes on 2023-03-02

delete of link to existing directory.

```
Caused by: org.apache.sshd.sftp.common.SftpException: No such file
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.throwStatusException(AbstractSftpClient.java:217)
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.checkResponseStatus(AbstractSftpClient.java:212)
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.checkResponseStatus(AbstractSftpClient.java:186)
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.checkCommandStatus(AbstractSftpClient.java:164)
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.rmdir(AbstractSftpClient.java:817)
	at org.apache.sshd.sftp.client.fs.SftpFileSystem$Wrapper.rmdir(SftpFileSystem.java:372)
	at org.apache.sshd.sftp.client.fs.SftpFileSystemProvider.delete(SftpFileSystemProvider.java:591)
	at java.base/java.nio.file.Files.delete(Files.java:1152)
	at nl.qcg.br.releaser.util.FileUtil.fixedFileDelete(FileUtil.java:135)
	at nl.qcg.br.releaser.cmds.comp.PathCopier.lambda$remove$3(PathCopier.java:181)
	... 19 common frames omitted

```
```
Path = usr/share/icons/Humanity-Dark/status@2

# ls -al usr/share/icons/Humanity-Dark/status@2
lrwxrwxrwx 1 root root 6 mrt 18  2022 'usr/share/icons/Humanity-Dark/status@2' -> status/
# ls -ald usr/share/icons/Humanity-Dark/status
drwxr-xr-x 1 root root 16 mrt  2 12:26 usr/share/icons/Humanity-Dark/status

```

## Comment by sijskes on 2023-03-02

deleting an symbolic link pointing to a file
````
# ls -ald usr/share/icons/ubuntu-mono-light/stock/22/avatar-default.svg
lrwxrwxrwx 1 root root 22 mrt 18  2022 usr/share/icons/ubuntu-mono-light/stock/22/avatar-default.svg -> stock_person-panel.svg
# ls -ald usr/share/icons/ubuntu-mono-light/stock/22/stock_person-panel.svg
-rw-r--r-- 3 root root 2616 mrt 18  2022 usr/share/icons/ubuntu-mono-light/stock/22/stock_person-panel.svg
````


````
Caused by: java.nio.file.NoSuchFileException: usr/share/icons/ubuntu-mono-light/stock/22/avatar-default.svg
	at org.apache.sshd.sftp.client.fs.SftpFileSystemProvider.resolveRemoteFileAttributes(SftpFileSystemProvider.java:994)
	at org.apache.sshd.sftp.client.fs.SftpFileSystemProvider.lambda$readRemoteAttributes$0(SftpFileSystemProvider.java:969)
	at org.apache.sshd.sftp.client.impl.SftpPathImpl.withAttributeCache(SftpPathImpl.java:120)
	at org.apache.sshd.sftp.client.impl.SftpPathImpl.withAttributeCache(SftpPathImpl.java:140)
	at org.apache.sshd.sftp.client.fs.SftpFileSystemProvider.readRemoteAttributes(SftpFileSystemProvider.java:969)
	at org.apache.sshd.sftp.client.impl.AbstractSftpFileAttributeView.readRemoteAttributes(AbstractSftpFileAttributeView.java:71)
	at org.apache.sshd.sftp.client.fs.SftpPosixFileAttributeView.readAttributes(SftpPosixFileAttributeView.java:52)
	at org.apache.sshd.sftp.client.fs.SftpPosixFileAttributeView.readAttributes(SftpPosixFileAttributeView.java:40)
	at org.apache.sshd.sftp.client.fs.SftpFileSystemProvider.checkAccess(SftpFileSystemProvider.java:826)
	at org.apache.sshd.sftp.client.fs.SftpFileSystemProvider.delete(SftpFileSystemProvider.java:581)
	at java.base/java.nio.file.Files.delete(Files.java:1152)
	at nl.qcg.br.releaser.cmds.comp.PathCopier.lambda$remove$3(PathCopier.java:180)
	... 19 common frames omitted
Caused by: org.apache.sshd.sftp.common.SftpException: No such file
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.throwStatusException(AbstractSftpClient.java:217)
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.checkAttributesResponse(AbstractSftpClient.java:305)
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.checkAttributes(AbstractSftpClient.java:283)
	at org.apache.sshd.sftp.client.impl.AbstractSftpClient.stat(AbstractSftpClient.java:997)
	at org.apache.sshd.sftp.client.fs.SftpFileSystem$Wrapper.stat(SftpFileSystem.java:412)
	at org.apache.sshd.sftp.client.fs.SftpFileSystemProvider.resolveRemoteFileAttributes(SftpFileSystemProvider.java:981)
	... 30 common frames omitted
````

## Comment by sijskes on 2023-03-02

i can't reproduce the case with the symlink pointing to non-existing file anymore, but i pretty sure there was an exception as well.

## Comment by tomaswolf on 2023-03-19

```
	at org.apache.sshd.sftp.client.fs.SftpFileSystemProvider.checkAccess(SftpFileSystemProvider.java:826)
	at org.apache.sshd.sftp.client.fs.SftpFileSystemProvider.delete(SftpFileSystemProvider.java:581)
	at java.base/java.nio.file.Files.delete(Files.java:1152)
```
There is definitely a problem here. `Files.delete()` is specified _not_ to follow symlinks, but `SftpFileSystemProvider.checkAccess()` does.
