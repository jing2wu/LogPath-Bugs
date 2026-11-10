# Custom HttpURLConnection throwing unchecked exception can stall the agent

- Issue: https://github.com/elastic/apm-agent-java/issues/4590
- Opened by jackshirazi on 2026-10-07, closed on 2026-10-15
- Labels: bug, agent-java
- Fix commit: 5cabf9ceeaea99f7a811b896064bf7aa8b131e5d

## Report

## Describe the bug

A custom HttpURLConnection implementation or a custom response stream which throws an unchecked exception during agent intake handling cleanup can cause the agent to fail to cleanup handling and then fail to send any subsequent data


## Expected behavior

Agent should continue to cleanup normally
