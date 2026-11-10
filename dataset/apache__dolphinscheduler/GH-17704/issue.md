# [Bug] [HttpTask] The output parameters of an HTTP task cannot be referenced in downstream tasks.

- Issue: https://github.com/apache/dolphinscheduler/issues/17704
- Opened by Jaltte on 2025-11-19, closed on 2025-12-08
- Labels: bug, backend
- Fix commit: 4f693a5fa14a433b35d559c612e8e07382cc2910

## Report

### Search before asking

- [x] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

The output parameters of an HTTP task cannot be referenced using `${taskName.response}` in downstream tasks.

My workflow is shown in the diagram below.The HTTP task has succeeded, and the logs show that the correct response is being received.
<img width="974" height="450" alt="Image" src="https://github.com/user-attachments/assets/3fab6eb6-529c-4a10-95bc-64aa2c4e148e" />
As described in the official documentation, a shell task is configured here to receive the output of the upstream HTTP task and print it out using `echo`.
<img width="626" height="860" alt="Image" src="https://github.com/user-attachments/assets/8c9542bf-fede-4f49-9ff6-2b9ecaf2ef1c" />
However, the downstream shell task did not actually receive the output of the HTTP task, and the printed content was empty.
<img width="1128" height="595" alt="Image" src="https://github.com/user-attachments/assets/4f5df95e-c358-4d67-9396-8019a06d5996" />

### What you expected to happen

During my debugging and comparison, I discovered that the HTTP task was missing this line of code to persist the varPool.
<img width="966" height="446" alt="Image" src="https://github.com/user-attachments/assets/cec897db-1f9b-479a-bbc0-4b1090447019" />

### How to reproduce

Please confirm if this is the cause of the problem, and hopefully it can be fixed.

### Anything else

_No response_

### Version

3.3.2

### Are you willing to submit PR?

- [ ] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)

## Comment by baiyu515 on 2026-01-04

Is this issue resolved? My current version is 3.3.2, and this issue still exists.
