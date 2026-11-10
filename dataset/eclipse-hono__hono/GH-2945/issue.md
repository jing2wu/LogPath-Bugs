# Kafka based Command response does not contain tenant ID

- Issue: https://github.com/eclipse-hono/hono/issues/2945
- Opened by sophokles73 on 2021-11-12, closed on 2021-11-22
- Labels: bug, C&C
- Fix commit: 846bcdedc633ed6dc09beaed1056a053503aee0e

## Report

The Command & Control API contains a definition of the response message format which includes an application property called `tenant_id` which contains the identifier of the tenant that the device belongs to.
The response message format defined by the Kafka based variant of the C&C API does not include a corresponding header which may lead to incompatibilities in downstream applications which expect to find it.
