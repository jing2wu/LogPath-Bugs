# [BUG] Mappings aren't restored in 1st .adm import attempt

- Issue: https://github.com/atlasmap/atlasmap/issues/3507
- Opened by igarashitm on 2021-11-22, closed on 2021-11-23
- Labels: group/runtime, cat/bug
- Fix commit: 43405d92345f0f3795492997dbcf43aee259286d

## Report

**Describe the bug**
<!--
A clear and concise description of what the bug is. The more info is provided, the more likely we can fix it earlier.
-->
The .adm import doesn't restore mappings in 1st loading attempt, although it succeeds in 2nd attempt. The 1st attempt here means 1st time after backend starts. Once backend is restarted then the symptom reproduces again.

**Attach .adm file and source document examples**
<!--
The .adm archive file you can export from AtlasMap UI contains all metadata to reproduce your mapping. Also don't forget to provide source document examples to reproduce the runtime behavior exactly what you see.
NOTE: GitHub doesn't allow uploading the file with unsupported extension, e.g. .adm and .xsd. You would need to either 1) pack into a ZIP file or 2) add a fake extension like schema.xsd.txt
 -->
 https://github.com/atlasmap/atlasmap/blob/main/standalone/src/test/resources/json-schema-source-to-xml-schema-target.adm

**Expected behavior**
<!--
A clear and concise description of what you expected to happen.
-->
Mappings to be restored in 1st attempt.

**Screenshots**
<!--
If applicable, add screenshots to help explain your problem.
-->

![atlasmap](https://user-images.githubusercontent.com/265462/142891280-3c85a2d0-61a5-440d-9a4e-e984d08cfde3.gif)
