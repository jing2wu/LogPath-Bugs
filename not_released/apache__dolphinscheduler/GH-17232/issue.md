# [Bug] [Master] when use K8S to  deploy master nodes use scroll batch deploy mode,  the master nodes may gain the same slot id

- Issue: https://github.com/apache/dolphinscheduler/issues/17232
- Opened by ZhongJinHacker on 2025-06-01, closed on 2025-06-05
- Labels: bug, backend, priority:high
- Fix commit: 7266e3fe9cbd741e6a5ee43021c6fcdfb604bf8b

## Report

### Search before asking

- [x] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

when we  use K8S to  deploy master nodes use scroll batch deploy mode,  This situation has occurred with a certain probability that the master may gain the same slot id that lead some task would not be processed

### What you expected to happen

I have read the log， and find the code location that can fix this issue, please assign this issue to me , I am glad to fix it

### How to reproduce

use k8s  to make master nodes pod down and make master nodes up when use k8s scroll deploy mode. ZooKeeper cannot ensure message ordering between different temporary znodes.  And the field `masterServerMap` 's type is **ConcurrentHashMap**  in Class `MasterClusters`. the` values` method of ConcurrentHashMap do not apply the ablity of ordering，so when the `getNormalServers`method in  `MasterClusters`  is called, it may return a list  with different  element order. It lead different master node may gain the same slot id .this situation will lead some task would not be processed forerver

### Anything else

_No response_

### Version

dev

### Are you willing to submit PR?

- [x] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)
