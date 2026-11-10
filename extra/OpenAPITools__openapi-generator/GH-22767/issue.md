# [BUG] [TYPESCRIPT] BasePath is incorrectly using full urls instead of relative ones when a dash is present in the server url

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/22767
- Opened by Romanow88 on 2026-01-22, closed on 2026-01-24
- Labels: Issue: Bug
- Fix commit: 5926c3175e2e5a5409d9fbb9487f615428ede019

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [ ] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))


##### Description

When generating typescript clients (and probably other clients) the URL is incorrectly determined to be absolute, in case the url has "-", "@", "~", "." in it.

##### openapi-generator version

7.19.0, 7.20.0-SNAPSHOT

##### OpenAPI declaration file content or url


```yaml
openapi: 3.0.1
info:
  title: OpenAPI Petstore
  description: "sample spec"
  license:
    name: Apache-2.0
    url: https://www.apache.org/licenses/LICENSE-2.0.html
  version: 1.0.0
servers:
  - url: /api-v3
tags: []
paths: {}
components:
  schemas: {}
  securitySchemes: {}
```

##### Generation Details

```
java -jar modules/openapi-generator-cli/target/openapi-generator-cli.jar generate \
   -i test.yaml \
   -g typescript-angular \
   -o ./typescript-angular
```

##### Steps to reproduce

Generate a typescript-angular, open api.base.service.ts and check the `protected basePath = "{{{baseUrl}}}"` 

##### Related issues/PRs

<!-- has a similar issue/PR been reported/opened before? Please do a search in https://github.com/openapitools/openapi-generator/issues?utf8=%E2%9C%93&q=is%3Aissue%20 -->

##### Suggest a fix

Update Regex in URLPathUtils#URLPathUtils to handle the above mentioned symbols.
