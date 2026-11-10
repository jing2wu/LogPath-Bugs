# [BUG] [JAVA] items: allOf: [$ref: Pet] does not generate List<@Valid Pet>

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/25113
- Opened by jpfinne on 2026-10-04, closed on 2026-10-08
- Labels: Issue: Bug
- Fix commit: 065b6c50a424c8f2c8a026828610c01c91e2d094

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

'List<@Valid>` not generated for items using allOf.

```
 listStubb:
    type: array
    items:
      allOf:
        - $ref: '#/components/schemas/Stubb'
```

Expected generation:
`private List<@Valid Stubb> listStubb;`

Actual generation
`private List<Stubb> listStubb;`

The allOf is needed if vendorExtensions ared used.  The swagger parser does not allow items with $ref and x- vendorExtensions.
For example:
```
listStubb:
  type: array
  items:
    allOf:
      - $ref: '#/components/schemas/Stubb'
    x-field-extra-annotation: '@NotEmpty' 
```

##### openapi-generator version

7.25.0

##### OpenAPI declaration file content or url

```yaml
openapi: 3.0.3
info:
  title: allOf+$ref+annotation
  version: 1.0.0
components:
  schemas:
    Stubb:
      type: object
      properties:
        name:
          type: string
    SampleModel:
      type: object
      properties:
        listStubb:
          type: array
          items:
            allOf:
              - $ref: '#/components/schemas/Stubb'
```

##### Generation Details

`openapi-generator-cli generate  -g spring --skip-validate-spec -i issue_25113.yaml`

##### Steps to reproduce

Build the sample and look at the generate List of Stubb.  It lacks `@Valid`

##### Related issues/PRs

#25049 highlight the issue

##### Suggest a fix

Detect the pattern items + allOf of a single $ref
