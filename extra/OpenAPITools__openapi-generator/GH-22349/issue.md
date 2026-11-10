# [BUG,Kotlin] Empty (invalid) data class generated when using discriminator and kotlinx.serialization

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/22349
- Opened by diastremskii on 2025-11-13, closed on 2025-11-16
- Labels: Issue: Bug
- Fix commit: 039de98d4f195c9d8ae8c86c032a02c77391c9c7

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. E.g.:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

When using `kotlinx.serialization` as serialization library and having an object without any properties other than discriminator itself, the outputted class is invalid - generator outputs an empty `data class` and makes Kotlin compilation fail.

##### openapi-generator version

v7.17.0

##### OpenAPI declaration file content or url

```yaml
openapi: 3.0.0
info:
  title: Test Empty Model
  version: 1.0.0
paths: {}
components:
  schemas:
    Response:
      type: "object"
      properties:
        result_or_error:
          nullable: true
          discriminator:
            propertyName: "_type"
            mapping:
              result: "#/components/schemas/EmptyModel"
              error: "#/components/schemas/Error"
          oneOf:
            - $ref: "#/components/schemas/EmptyModel"
            - $ref: "#/components/schemas/Error"
    EmptyModel:
      type: object
      properties:
        _type:
          required:
            - "_type"
          type: string
          default: "result"
      additionalProperties: false
    Error:
      type: object
      required:
        - "code"
      properties:
        code:
          type: integer
        _type:
          required:
            - "_type"
          type: string
          default: "error"
      additionalProperties: false
```

##### Generation Details

`kotlinx.serialization` should be used.

##### Steps to reproduce

1. Use the schema provided as an example
2. Set serialization library to `kotlinx.serialization`
3. Generate the Kotlin client
4. Try to compile the client

##### Related issues/PRs

https://github.com/OpenAPITools/openapi-generator/issues/14710
https://github.com/OpenAPITools/openapi-generator/issues/19993

##### Suggest a fix

Going to open a PR in a bit.

## Comment by wing328 on 2025-11-16

thanks for filing a PR to fix the issue

btw, when i tested with this spec, the compilation is fine:

```
Deprecated Gradle features were used in this build, making it incompatible with Gradle 9.0.

You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.

For more on this, please refer to https://docs.gradle.org/8.14.1/userguide/command_line_interface.html#sec:command_line_warnings in the Gradle documentation.

BUILD SUCCESSFUL in 7s
4 actionable tasks: 4 executed
```
