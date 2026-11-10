# `ProcessDefinitionImporter` only imports 10 definitions

- Issue: https://github.com/camunda-community-hub/spring-zeebe/issues/336
- Opened by chillleader on 2023-02-14, closed on 2023-02-27
- Labels: bug, connectors
- Fix commit: 459bd3d25cc814cf8e6ea0c2cbf973759ee97abb

## Report

`ProcessDefinitionImporter` is only able to import 10 process definitions, so when there are more, they are simply ignored. This results in invalid Webhook Connector behavior.

The root cause is apparently the fact that Operate API returns 10 records only by default.
This can be configured by specifying size query parameter explicitly.

See also: [discussion in Slack (internal)](https://camunda.slack.com/archives/C02JLRNQQ05/p1676384475066629?thread_ts=1675846928.363399&cid=C02JLRNQQ05)

## Comment by chillleader on 2023-02-22

Discussed this with Operate team. Key takeaways:
- We can implement smart polling & pagination by using `searchAfter` field in request
- In this case. we will need to remove the sort we currently use (by version), otherwise pagination will not work correctly if new process definitions are deployed in between
