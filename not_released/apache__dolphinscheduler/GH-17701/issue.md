# [Bug] [SqlTask] When field names are duplicated in a query statement, the result set suffers from name collision, causing values to overwrite each other

- Issue: https://github.com/apache/dolphinscheduler/issues/17701
- Opened by njnu-seafish on 2025-11-18, closed on 2025-12-04
- Labels: bug, backend
- Fix commit: 9ce565ecc8d3f752ef4f12be247a8af0d42c20bc

## Report

### Search before asking

- [x] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

When field names are duplicated in a query statement, the result set suffers from name collision, causing values to overwrite each other;

For example:

SELECT
  user.name AS display_name,
  admin.name AS display_name
FROM user
JOIN admin ON user.id = admin.user_id;

### What you expected to happen

If field names are duplicated, the result set should automatically append suffixes to disambiguate them.


### How to reproduce

When field names are duplicated in a query statement, the result set suffers from name collision, causing values to overwrite each other;

For example:

SELECT
  user.name AS display_name,
  admin.name AS display_name
FROM user
JOIN admin ON user.id = admin.user_id;

### Anything else

_No response_

### Version

dev

### Are you willing to submit PR?

- [x] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)
