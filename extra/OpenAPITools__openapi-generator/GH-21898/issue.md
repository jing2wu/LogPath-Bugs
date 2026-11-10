# [BUG] [Golang] xml wrapped and name is ignored

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/21898
- Opened by sruehl on 2025-09-04, closed on 2025-09-04
- Labels: Issue: Bug
- Fix commit: 08733aaf251cede20ac048fa7ff4cf0a64bb929c

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?

##### Description

When you use wrapped xml arrays the instructions are completely ignored.

##### openapi-generator version

master

##### OpenAPI declaration file content or url

src/test/resources/3_0/petstore.yaml

##### Generation Details

just activate withXML

##### Steps to reproduce

activate withXML and observe that all xml instructions are ignored (e.g. `tags>tag` or `photoUrls>photoUrl`)

##### Related issues/PRs

TBD

##### Suggest a fix

Merge PR TBD
