# [BUG] Same name element with a different inline type in the XSD is wrongly `cached`

- Issue: https://github.com/atlasmap/atlasmap/issues/3470
- Opened by igarashitm on 2021-11-10, closed on 2021-11-10
- Labels: group/runtime, cat/bug
- Fix commit: a7da120f2ae9bc176782c3d86046442e58138bbd

## Report

**Describe the bug**
<!--
A clear and concise description of what the bug is. The more info is provided, the more likely we can fix it earlier.
-->
Say there's `/foo/bar/foo/else`, the 2nd `foo` is wrongly inspected as `cached` and UI disables it.
[Not_working.xsd.txt](https://github.com/atlasmap/atlasmap/files/7514478/Not_working.xsd.txt)


**Expected behavior**
<!--
A clear and concise description of what you expected to happen.
-->
Should not be cached with just having a same name. Check the type.
