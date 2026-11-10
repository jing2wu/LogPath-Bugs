# [BUG,Python] not with enum is ignored during model validation

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/25069
- Opened by AndreyVMarkelov on 2026-09-30, closed on 2026-10-05
- Labels: Issue: Bug
- Fix commit: ba7fb8baf194d2467bf7c3e86e23b1ff1389cde3

## Report

#### Bug Report Checklist

-   [x] Have you provided a full/minimal spec to reproduce the issue?
-   [ ] Have you validated the input using an OpenAPI validator?
-   [x] Have you [tested with the latest
    master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator)
    to confirm the issue still exists?
-   [x] Have you searched for related issues/PRs?
-   [x] What's the actual output vs expected output?
-   [ ] \[Optional\] Sponsorship to speed up the bug fix or feature
    request
    ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

The Python client generator ignores a string enum constraint nested
under `not`.

For example:

``` yaml
kind:
  type: string
  not:
    enum:
      - known
```

is currently generated as:

``` python
kind: StrictStr
```

without validation excluding `"known"`.

This causes incorrect `oneOf` behavior when `not: enum` is used to make
variants mutually exclusive. A value such as `{"kind":"known"}` can
validate against both variants, causing generated `oneOf`
deserialization to fail with a multiple-match error.

##### openapi-generator version

`7.26.0-SNAPSHOT`

Reproduced against the latest `master`.

##### OpenAPI declaration file content or url

``` yaml
openapi: 3.1.0

info:
  title: oneOf not enum repro
  version: 1.0.0

paths: {}

components:
  schemas:
    Known:
      type: object
      required:
        - kind
      properties:
        kind:
          type: string
          enum:
            - known

    Other:
      type: object
      required:
        - kind
      properties:
        kind:
          type: string
          not:
            enum:
              - known

    TaggedUnion:
      oneOf:
        - $ref: '#/components/schemas/Known'
        - $ref: '#/components/schemas/Other'
```

##### Generation Details

Generator: `python`

``` bash
java -jar modules/openapi-generator-cli/target/openapi-generator-cli.jar generate \
  -i /tmp/python-oneof-not-enum.yaml \
  -g python \
  -o /tmp/python-oneof-not-enum
```

##### Steps to reproduce

1.  Build the current `master`.
2.  Save the OpenAPI document above as
    `/tmp/python-oneof-not-enum.yaml`.
3.  Generate the Python client using the command above.
4.  Inspect `openapi_client/models/other.py`.

Actual generated model:

``` python
class Other(BaseModel):
    kind: StrictStr
```

There is no validation corresponding to:

``` yaml
not:
  enum:
    - known
```

As a result:

``` python
Other.from_json('{"kind":"known"}')
```

is accepted.

When deserializing through `TaggedUnion`, both `Known` and `Other`
therefore match `{"kind":"known"}`, causing the generated `oneOf`
handling to report multiple matches.

Expected behavior is for `Other` to reject values excluded by `not`.

With the expected validation:

-   `{"kind":"known"}` matches `Known` only.
-   `{"kind":"other"}` matches `Other` only.

##### Related issues/PRs

Related Java generator issue/PR: #25065 / #25066.

This is the equivalent issue in the Python client generator.

##### Suggest a fix

The generated `CodegenProperty` retains the `not` schema in
`composedSchemas.not`, including the excluded enum values.

The Python generator can preserve those values as a property vendor
extension and generate a Pydantic `field_validator` which rejects values
listed by the `not` enum.

For example:

``` python
@field_validator('kind')
def kind_validate_not_enum(cls, value):
    if value in set(["known"]):
        raise ValueError("must not be one of excluded enum values")
    return value
```
