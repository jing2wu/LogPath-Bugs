# [Bug] [Master] TaskDispatchableEvent might block when the queue exist hight priority delay event

- Issue: https://github.com/apache/dolphinscheduler/issues/17555
- Opened by ruanwenjun on 2025-09-30, closed on 2025-10-09
- Labels: bug, priority:high
- Fix commit: 2cdf39fc099d9f25c1c2a7b696738ff0f4348a10

## Report

### Search before asking

- [x] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

Right now, we only compare the `TaskDispatchableEvent` with priority, if there exist two `TaskDispatchableEvent`, EventA delay time is 1h, priority is higher, EventB delay time is 0, priority is smaller, then the EventB will block until EventA is take.

### What you expected to happen

-

### How to reproduce

-

### Anything else

_No response_

### Version

dev

### Are you willing to submit PR?

- [x] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)
