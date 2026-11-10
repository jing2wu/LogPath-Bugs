# [Bug] [API] Workflow versions cannot be deleted due to workflow lineage

- Issue: https://github.com/apache/dolphinscheduler/issues/17637
- Opened by det101 on 2025-11-03, closed on 2025-11-11
- Labels: bug, backend
- Fix commit: 06d365dbe4b045a349ef78a2a886c5256757aff4

## Report

### Search before asking

- [x] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

When I try to delete a non-current version of a workflow, I get a message saying that deletion failed and cannot be deleted.

<img width="1789" height="737" alt="Image" src="https://github.com/user-attachments/assets/1e4c3c6b-4917-4f7f-bc15-c69af587cfbb" />

### What you expected to happen

Workflow history versions that do not involve blood relations can be deleted normally.

### How to reproduce

Create a new workflow with no dependencies, generate more than one version, and delete a version.

### Anything else

_No response_

### Version

dev

### Are you willing to submit PR?

- [x] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)
