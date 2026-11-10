# [Bug,API] WorkflowDefinition version is not synced back after create/update, always returns 0

- Issue: https://github.com/apache/dolphinscheduler/issues/18132
- Opened by wcmolin on 2026-04-03, closed on 2026-04-03
- Labels: bug, backend
- Fix commit: 7022d56e4be2fb6bf7dce7f3ef5e9f490bbb1f14

## Report

### Search before asking

- [x] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues) and found no similar issue.

### Describe the bug

When creating or updating a workflow definition via the API (`POST /projects/{projectCode}/workflow-definition` and `PUT /projects/{projectCode}/workflow-definition/{code}`), the returned `WorkflowDefinition` object always has `version=0` instead of the actual version number persisted to the database.

### Root Cause

In `WorkflowDefinitionServiceImpl`, the callers of `processService.saveWorkflowDefine()` correctly receive the `insertVersion` return value, but never sync it back to the `workflowDefinition` object before returning it to the API response.

**`createDagDefine()` (line ~325):**
```java
int insertVersion =
        processService.saveWorkflowDefine(loginUser, workflowDefinition, Boolean.TRUE, Boolean.TRUE);
// ... validation ...
// Missing: workflowDefinition.setVersion(insertVersion);
int insertResult = processService.saveTaskRelation(..., insertVersion, ...);
```

**`updateWorkflowDefinition()` (line ~815):**
```java
int insertVersion =
        processService.saveWorkflowDefine(loginUser, workflowDefinition, Boolean.TRUE, Boolean.TRUE);
// ... validation ...
// Missing: workflowDefinition.setVersion(insertVersion);
```

Note that the newer API method `saveWorkflowDefine()` (local method, line ~1948) already has the correct pattern:
```java
workflowDefinition.setVersion(insertVersion);
```

### Fix

Add `workflowDefinition.setVersion(insertVersion)` after `saveWorkflowDefine()` returns successfully in both `createDagDefine()` and `updateWorkflowDefinition()`.

### Expected behavior

The `version` field in the API response should reflect the actual version persisted in the database (e.g., `1`, `2`, `3`), not always `0`.

### Version

- [x] 3.4.x
- [x] 3.3.x
- [x] 3.2.x
- [ ] others

### Are you willing to submit a PR?

- [x] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)
