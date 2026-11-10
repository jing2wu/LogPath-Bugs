# [core] Unexpected throw in synchronized method [dx/d8]

- Issue: https://github.com/skylot/jadx/issues/2949
- Opened by nitram84 on 2026-09-05, closed on 2026-10-08
- Labels: bug, Core
- Fix commit: c5aedb312cbdd31e13ca1359b003c7a0d1400451

## Report

### Issue details

In this synchronized method, compiled with openjdk8 and decompiled with latest git and option "use dx/d8", jadx generates an unexpected throw: 

```java
package jadx.test;

public class SynchronizedTest1 {
    private int i;

    public synchronized void doSomething() {
        switch (this.i) {
            case 42:
                doSomething2();
            default:
                break;
        }
    }

    private void doSomething2() {
    }
}
```

Decompilation result:

```java
package jadx.test;

/* JADX INFO: loaded from: classes.dex */
public class SynchronizedTest1 {
    private int i;

    public synchronized void doSomething() {
        switch (this.i) {
            case 42:
                doSomething2();
                break;
            default:
                break;
        }
        throw th;
    }

    private void doSomething2() {
    }
}
```

Without the option "use dx/d8" this error can't be reproduced.

### Relevant log output or stacktrace

```java
DEBUG: Var reference 'VarRef{VarNode{r0v0}, name=th, mth=jadx.test.SynchronizedTest1.doSomething():void}' incorrect (ref pos is zero) and was removed from metadata
```

### Provide sample and class/method full name

Example:
The same pattern can be found in

https://apkpure.net/basketball-shot/com.droidhen.basketball/download/2.4.0

class: `com.droidhen.basketball.GameActivity`
methods: `prepareResume()` and `preparePause()`

### Jadx version

1.5.6, latest git

## Comment by noy-solvin on 2026-10-08

Hi @skylot
I've submitted PR #2983 that fixes this issue.
Would love a review whenever you get a chance. Happy to adjust anything!
