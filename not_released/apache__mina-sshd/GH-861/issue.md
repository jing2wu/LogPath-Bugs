# Throwing a SSH_FX_BAD_MESSAGE exception when file_size % 32726 = 0

- Issue: https://github.com/apache/mina-sshd/issues/861
- Opened by davidfilipovic on 2025-12-26, closed on 2026-01-02
- Labels: bug
- Fix commit: 32038f1dc4d1a2f327412336ab1243a34c23846c

## Report

### Version

2.16.0

### Bug description

For years, we have been uploading thousands of files to an SFTP server per day, using mina-sshd. But, once per six or seven months, we encounter a file for which the following is true: 

```
file_size % 32276 = 0
```
This was true for our files with sizes 32726B, 7625158B, and 916328B. 

In cases like this, we have encountered that an additional packet with a length of zero is being sent after all previous packets are successfully sent. 

By enabling TRACE logs in our application, we observe that a packet with zero length is sent, which results in an SSH_FX_BAD_MESSAGE exception being thrown. Although the exception is thrown, the file is successfully uploaded to the server. 



### Actual behavior

For a file with a size divisible by 32726 without reminder an additional packet is being sent with a length of zero after all the packets are successfully sent. This leads to an exception being thrown and the file marked as not delivered althought it is uploaded successfully to the SFTP server. 

### Expected behavior

A file with a size that is divisible by 32726 is uploaded successfully, just like any other file. 

### Relevant log output

```Shell
o.a.s.s.client.impl.DefaultSftpClient    : send(SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]) cmd=SSH_FXP_WRITE, len=28, id=103
DefaultSftpClient$SftpChannelSubsystem$1 : writePacket([SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]] cmd=SSH_MSG_CHANNEL_DATA)[resume=false] attempting to write 37 out of 37
o.a.sshd.common.channel.RemoteWindow     : Consume RemoteWindow[client](SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]) by 37 down to 2064269
o.a.s.client.session.ClientSessionImpl   : encode(ClientSessionImpl[username@/0.0.0.0:22]) packet #14 sending command=94[SSH_MSG_CHANNEL_DATA] len=46
...
o.a.s.s.c.impl.SftpOutputStreamAsync     : flush(SftpOutputStreamAsync[ClientSessionImpl[username@/0.0.0.0:22],/file.csv]) enqueue pending ack=SftpAckData[id=103, offset=32726, length=0]
o.a.sshd.common.io.nio2.Nio2Session      : handleCompletedWriteCycle(Nio2Session[local=/0.0.0.0:60186, remote=/0.0.0.0:22]) finished writing len=76 at cycle=16 after 91692 nanos
DefaultSftpClient$SftpChannelSubsystem$1 : onWritten([SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]] cmd=SSH_MSG_CHANNEL_DATA) completed write len=37
o.a.s.s.c.impl.SftpOutputStreamAsync     : close(SftpOutputStreamAsync[ClientSessionImpl[username@/0.0.0.0:22],/file.csv]) processing ack #1: SftpAckData[id=102, offset=0, length=32726]
...
i.DefaultSftpClient$SftpChannelSubsystem : handleData(SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]) SSH_MSG_CHANNEL_DATA len=21
o.a.s.s.client.impl.DefaultSftpClient    : process(SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]) id=102, type=SSH_FXP_STATUS, len=17
o.a.s.s.client.impl.DefaultSftpClient    : data(SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]) Processed 1 data messages
o.a.s.s.c.impl.SftpOutputStreamAsync     : close(SftpOutputStreamAsync[ClientSessionImpl[username@/0.0.0.0:22],/file.csv]) processing ack #1 response for SftpAckData[id=102, offset=0, length=32726]
o.a.s.s.c.impl.SftpOutputStreamAsync     : close(SftpOutputStreamAsync[ClientSessionImpl[username@/0.0.0.0:22],/file.csv]) processing ack #2: SftpAckData[id=103, offset=32726, length=0]
 o.a.s.client.session.ClientSessionImpl   : doHandleMessage(ClientSessionImpl[username@/0.0.0.0:22]) process #16 SSH_MSG_CHANNEL_DATA
 o.a.sshd.common.channel.LocalWindow      : Consume LocalWindow[client](SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]) by 21 down to 2097076
 i.DefaultSftpClient$SftpChannelSubsystem : handleData(SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]) SSH_MSG_CHANNEL_DATA len=21
 o.a.s.s.client.impl.DefaultSftpClient    : process(SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]) id=103, type=SSH_FXP_STATUS, len=17
 o.a.s.s.client.impl.DefaultSftpClient    : data(SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]) Processed 1 data messages
o.a.s.s.c.impl.SftpOutputStreamAsync     : close(SftpOutputStreamAsync[ClientSessionImpl[username@/0.0.0.0:22],/file.csv]) processing ack #2 response for SftpAckData[id=103, offset=32726, length=0]
o.a.s.s.client.impl.DefaultSftpClient    : throwStatusException(SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp])[id=103] cmd=SSH_FXP_WRITE status=SSH_FXP_STATUS[SSH_FX_BAD_MESSAGE, language=, message=]
o.a.s.s.c.impl.SftpOutputStreamAsync     : close(SftpOutputStreamAsync[ClientSessionImpl[username@/0.0.0.0:22],/file.csv]) closing file handle
o.a.s.s.client.impl.DefaultSftpClient    : close(SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]) /file.csv: 374635304337413138453130
o.a.s.s.client.impl.DefaultSftpClient    : open(SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp])[/file.csv: 374635304337413138453130]: send SSH_FXP_CLOSE
o.a.s.s.client.impl.DefaultSftpClient    : send(SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]) cmd=SSH_FXP_CLOSE, len=16, id=104
DefaultSftpClient$SftpChannelSubsystem$1 : writePacket([SftpChannelSubsystem[id=0, recipient=0]-ClientSessionImpl[username@/0.0.0.0:22,sftp]] cmd=SSH_MSG_CHANNEL_DATA)[resume=false] attempting to write 25 out of 25
```

### Other information

_No response_

## Comment by tomaswolf on 2025-12-27

1. How exactly are you uploading the file? Please show the client code. There are many ways to upload a file.
2. What's the server? I cannot reproduce this with an Apache MINA sshd server.

## Comment by davidfilipovic on 2025-12-30

Hi, thanks for the reply!

1. We are using the spring-integration project to get the session and write the file to the SFTP. We are using the write method from here: [SftpSession:write(InputStream, String)](https://github.com/spring-projects/spring-integration/blob/18c72d1f4f4e5127e5af44edbdfbf09b1572526f/spring-integration-sftp/src/main/java/org/springframework/integration/sftp/session/SftpSession.java#L163-L166). 
2. We are uploading to the third-party server. We are not aware of the details, but we know it is an IBM DataPower SFTP server.

## Comment by tomaswolf on 2025-12-30

Unfortunately that link is broken. So: which version of spring-framework and spring-integration are you using, and which Java version? Also, on which OS is the client?

## Comment by tomaswolf on 2025-12-30

Never mind. I managed to reproduce that extra zero-byte write, but at what byte size this occurs depends on the SFTP file handle size, which is determined by the server. That IBM server uses 12 bytes while an Apache MINA sshd server by default uses 4 bytes. So with an Apache MINA shd server and the default buffer size this occurs if the file size is a multiple of 32734 bytes.

While it is a bug in the client side of Apache MINA sshd that such a zero-length SSH_FXP_WRITE is sent (and I'm going to fix that), I'd also like to point out that this IBM server is wrong to reject the write with SSH_FX_BAD_MESSAGE. I see nothing in the SFTP draft RFCs that would forbid SSH_FXP_WRITE with zero length data.

## Comment by davidfilipovic on 2025-12-31

Thanks for checking it out and confirming! Unfortunately, there is not a lot we can do with our client server except of letting them know aboout the issue.

## Comment by yannickdeturck on 2026-01-02

Thanks for already pushing a fix, @tomaswolf! Any idea when version 2.17.0 would be planned for release?

## Comment by tomaswolf on 2026-01-02

Probably some time this month.
