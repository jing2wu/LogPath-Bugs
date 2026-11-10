# The audit table in the Administration tool does not include the user name for API calls

- Issue: https://github.com/phax/phoss-smp/issues/238
- Opened by javierestevez on 2023-03-03, closed on 2026-09-04
- Labels: bug, REST interface
- Fix commit: b338ed08ef5b4faa9acc87247bb987b4d068fee9

## Report

**Affects:** phoss-smp-sql:6.0.7

The audit table shows `$GUEST$` under the User column for operations made via the API. The audit entry still contains the user id which could help us determining the user performing the action. But there is no reason why the user would not be properly displayed in the table.

![image](https://user-images.githubusercontent.com/17927469/222715236-7e584eda-31ee-44d7-abf8-e1633a18575f.png)

We tested both using Basic Auth and user tokens.

## Comment by stale[bot] on 2024-01-07

This issue has been automatically marked as stale because it has not had recent activity. It will be closed if no further activity occurs. Thank you for your contributions.

## Comment by phax on 2026-09-04

Fixed in 8.4.0
