# [Bug] [API] Global and local parameters are not replaced with XX value in SQL/SHELL components

- Issue: https://github.com/apache/dolphinscheduler/issues/14869
- Opened by mchcz on 2023-09-07, closed on 2023-09-15
- Labels: bug, priority:high
- Fix commit: f6a6794289ff984227548ff74affcf83fbced289

## Report

### Search before asking

- [X] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

1、create process  ”test0907“ && add shell components ”echo ${dt}" 
2、add global parameter： name：“dt”，value：“$[yyyy-MM-dd]” && save process
3、run this process，view logs after finished

### What you expected to happen

Global and local parameters can be replaced correctly.

### How to reproduce

eg. "what happened"
![image](https://github.com/apache/dolphinscheduler/assets/18095523/5bfcdbfa-0145-4b5d-8ad3-47d8755403f8)
![image](https://github.com/apache/dolphinscheduler/assets/18095523/6b2722a2-2ff6-4082-a5bc-47faf32f96d0)
![image](https://github.com/apache/dolphinscheduler/assets/18095523/6bd54701-d9f3-4d7b-afc2-a99484768ce0)


### Anything else

_No response_

### Version

3.2.0-prepare

### Are you willing to submit PR?

- [ ] Yes I am willing to submit a PR!

### Code of Conduct

- [X] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)

## Comment by zhongjiajie on 2023-09-14

report by @Gallardot SQL task still have a problem when pass parameter from startup parameter

## Comment by Gallardot on 2023-09-14

> report by @Gallardot SQL task still have a problem when pass parameter from startup parameter

After verification, the SQL task issue was found to be in the regular expression of this [PR](https://github.com/apache/dolphinscheduler/pull/13378/files#diff-4158abf179330ca3a77b119f5c8896eeed3155332b2fc86743d1efdbab47eadfL41). I replaced the regular expression with the original version `"['\"]*\\$\\{(.*?)\\}['\"]*"`, and the issue was fixed.
