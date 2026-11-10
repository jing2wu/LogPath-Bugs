# Once a label set for a schema it can't be removed afterwards.

- Issue: https://github.com/kit-data-manager/metastore2/issues/334
- Opened by VolkerHartmann on 2023-06-27, closed on 2023-07-11
- Labels: bug
- Fix commit: 34c419146b2d064655604b67829fd7d3fd20bbe8

## Report

**Describe the bug**
Once a label is assigned for a schema it can't be removed.

**To Reproduce**
Steps to reproduce the behavior:
1. Select or create a schema with a label.
2. Click on 'Update'
3. Remove label
4. Validate record
5. Submit update
6. Label is still there.

**Expected behavior**
It should be also possible to remove labels.
