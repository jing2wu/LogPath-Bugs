# [BUG,ASPNETCORE] README.md is outdated

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/23223
- Opened by MisinformedDNA on 2026-03-12, closed on 2026-07-13
- Labels: Issue: Bug
- Fix commit: 231c3c4cf0990ccfb60cf97e85386c643adb444b

## Report

#### Bug Report Checklist

- [X] Have you provided a full/minimal spec to reproduce the issue?
- [ ] Have you validated the input using an OpenAPI validator?
- [ ] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [X] Have you searched for related issues/PRs?
- [X] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. E.g.:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

Generating a server with aspnetcore results in the creation of a README.md that is very outdated.

<img width="498" height="286" alt="Image" src="https://github.com/user-attachments/assets/d99d9e4a-f9c0-42d9-99d8-6e97cf6e8cb1" />

##### openapi-generator version

7.10.0

##### Suggest a fix

Remove or update the README.md at the project/wwwroot level.
