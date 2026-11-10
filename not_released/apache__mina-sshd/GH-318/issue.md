# Support for more than one jump host

- Issue: https://github.com/apache/mina-sshd/issues/318
- Opened by nightman68 on 2023-02-06, closed on 2024-06-02
- Labels: bug
- Fix commit: 12e5283710a95a48d17ba70a7082fefe936b4964

## Report

### Description

I have a special server running to which the connection is only possible via 2 jump hosts and my configuration for SSH looks like this:

``` bash
Host jump1
  Hostname                    jump1.corp
  Port                        22
  User                        nightman
  LogLevel                    QUIET

Host jump2
  HostName                    jump2.dmz.corp
  Port                        22
  User                        nightman
  ProxyJump                   jump1
  LogLevel                    QUIET

Host host*.dmz.corp
  ProxyJump                   nightman@jump2:22
```

This is working well with the native SSH clients.

It would be nice when your great libary would support such a configuration as well!

 :-)

### Motivation

Enhancements would make the library better usable for jump hosts.

### Alternatives considered

There is no workaround I found so far.

### Additional context

_No response_

## Comment by tomaswolf on 2023-02-07

Looks like a shortcoming/bug in [SshClient.java](https://github.com/apache/mina-sshd/blob/801edabdb7723e9f5bf03fd66c6e48a2d240bb9f/sshd-core/src/main/java/org/apache/sshd/client/SshClient.java#L545), `connect()` and `doConnect()`: it appears to parse only the ProxyJump in the top-level Host entry.

As a work-around, try
```
Host host*.dmz.corp
  ProxyJump nightman@jump2:22,nightman@jump1:22
```
That should work (if I read the code right), and also should work with openSSH.

## Comment by nightman68 on 2023-02-08

@tomaswolf thanks for the quick response! I tested the workaround and it's working with one edit: the order of the proxy must be changed:

``` bash
Host host*.dmz.corp
  ProxyJump nightman@jump1:22,nightman@jump2:22
```
The other settings like in the original post.

For the native SSH client the order must be like proposed by you :-( Tested with openSSH 1.0.2 k on RH 7 and 1.1.1 i in a git bash.

## Comment by tomaswolf on 2023-02-09

> For the native SSH client the order must be like proposed by you :-(

So there's even a bug in that implementation in Apache MINA sshd. Really :-(.

## Comment by nightman68 on 2023-02-09

If it will help I can run tests with a fixed pre package.

## Comment by tomaswolf on 2023-02-09

Thanks for the offer. I won't have any time for any coding in the next few weeks, but perhaps someone else takes this on. Otherwise I'll take look sometime in March.

## Comment by nightman68 on 2023-06-26

Any update?

## Comment by tomaswolf on 2023-06-29

Nope; I didn't get around to this yet. But it's up for grabs; we do welcome PRs.

## Comment by nightman68 on 2024-03-18

A PR #477 is available to fix this issue. I tested it with the 2 configurations below.

configuration 1:
```
Host host*.dmz.corp
  ProxyJump     nightman@jump1.corp:22,nightman@jump2.corp:22,nightman@jump3.corp:22
```

configuration 2:
```
Host jump1
  Hostname                    jump1.corp
  Port                        22
  User                        nightman
  ProxyJump                   jump2
  LogLevel                    QUIET

Host jump2
  HostName                    jump2.dmz.corp
  Port                        22
  User                        nightman
  ProxyJump                   jump3
  LogLevel                    QUIET

Host jump3
  HostName                    jump3.dmz.corp
  Port                        22
  User                        nightman
  LogLevel                    QUIET

Host host*.dmz.corp
  ProxyJump                   jump1
```
