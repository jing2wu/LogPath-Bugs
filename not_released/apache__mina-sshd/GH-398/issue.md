# SftpInputStreamAsync#read(byte[], int, int) fails on calls with len = 0 

- Issue: https://github.com/apache/mina-sshd/issues/398
- Opened by mkeckmkeck on 2023-07-19, closed on 2023-07-22
- Labels: bug
- Fix commit: 511cd92a68d08c591a2a4030728971a1c36172c3

## Report

### Version

2.9.2

### Bug description

When passing len = 0 on a second read call, after eofIndicator has already be set to true, the read method returns -1. This can lead to an incomplete read when using e.g. java.io.InputStream#readAllBytes or java.io.InputStream#readNBytes(int). 

A possible solution would be an early return of 0 in case of len = 0




### Actual behavior

First reading offset 0, len 8192,
then offset 8192, len 0
then offset 8192, len 8192

Return in sum at most 8192 bytes (if available)

### Expected behavior

First reading offset 0, len 8192,
then offset 8192, len 0
then offset 8192, len 8192

Return in sum more 8192 bytes (if available)

### Relevant log output

_No response_

### Other information

_No response_
