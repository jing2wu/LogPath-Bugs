# TableOperationsImpl.locate Retry can fail when backOffFactor > 1

- Issue: https://github.com/apache/accumulo/issues/3414
- Opened by dlmarion on 2023-05-18, closed on 2023-05-23
- Labels: blocker, bug
- Fix commit: 487f2a34f126dad45d8c32465e74d19a357bbf4c

## Report

**Describe the bug**
Retry.waitForNextAttempt can pass a negative value to Thread.sleep [here](https://github.com/apache/accumulo/blob/2.1/core/src/main/java/org/apache/accumulo/core/util/Retry.java#L183). It appears that we might be overflowing `waitFactor` [here](https://github.com/apache/accumulo/blob/2.1/core/src/main/java/org/apache/accumulo/core/util/Retry.java#L174) which is used when the backOffFactor is greater than `1`. I wonder if switching from `Random.nextDouble` to `Random.nextLong` would resolve the issue.

**Versions (OS, Maven, Java, and others, as appropriate):**
 - Affected version(s) of this project: 2.1.0
 - OS: [e.g. CentOS 7.5]
 - Others:

**To Reproduce**
Add the following to `RetryTest` and run it.
```
  @Test
  public void testInfiniteRetryWithBackoff() throws InterruptedException {
    Retry retry = Retry.builder().infiniteRetries().retryAfter(100, MILLISECONDS)
        .incrementBy(100, MILLISECONDS).maxWait(2, SECONDS).backOffFactor(1.5)
        .logInterval(3, MINUTES).createRetry();
    for (int i = 0; i < Integer.MAX_VALUE; i++) {
      try {
        retry.waitForNextAttempt(log, i + "");
      } catch (IllegalArgumentException e) {
        log.error("Failed on iteration: {}", i);
        throw e;
      }
    }
  }
```

The test fails with the error below on iteration 97 for me:
```
java.lang.IllegalArgumentException: timeout value is negative
	at java.base/java.lang.Thread.sleep(Native Method)
	at org.apache.accumulo.core.util.Retry.sleep(Retry.java:194)
	at org.apache.accumulo.core.util.Retry.waitForNextAttempt(Retry.java:183)
	at org.apache.accumulo.core.util.RetryTest.testInfiniteRetryWithBackoff(RetryTest.java:217)
```

**Expected behavior**
Retry should not pass a negative value to `Thread.sleep`

## Comment by dlmarion on 2023-05-23

At the 96th iteration, the value of  `waitFactor` is `1.72034982760886272E17` and `waitIncrement` is `9223372036854775807`. When `waitIncrement` is added to the initial wait, it overflows the value of a long turning the value of `currentWait` negative.
