# [BUG] rust-server codegen: enum parameters in form bodies incorrectly serialized as their enum variant names by clients, rather than the values described in the OpenAPI definition

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/24366
- Opened by holdeg on 2026-07-20, closed on 2026-07-21
- Labels: Issue: Bug
- Fix commit: 82cb1ad5ab515e81cf54a598b91cf5ff61b718c1

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

For endpoints with request bodies of type form (e.g. `application/x-www-form-urlencoded`) and `enum` properties, the generated Rust client invokes `format!("{:?}", param_foo)` where `param_foo` is the model generated in `models.rs` for the `enum` property. `{:?}` is the debug formatter, which uses the derived `impl Debug` on the enum model, which resolves to the name of the enum variant (as per [the rust docs](<https://doc.rust-lang.org/std/fmt/trait.Debug.html>)) - however, we should instead be serializing this with the `impl Display` on the enum model, which produces the defined allowable values from the API definition. This incorrect serialization does not obey the OpenAPI spec and will cause any server policing the value of the enum to reject requests created by this client.

##### openapi-generator version

Present in all 7.x releases

##### OpenAPI declaration file content or url

```yaml
openapi: "3.0.3"
info:
  title: Enum Form Parameter Example
  version: "1.0.0"
paths:
  /authentication-endpoint:
    post:
      operationId: authenticate
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                target_resource:
                  type: string
                  enum:
                    - resource_one
                    - resource_two
                  description: "Resource to authenticate for - must be one of `resource_one` or `resource_two`"
      responses:
        '200':
          description: Authorization successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
```

##### Generation Details

No specific generation is required.

##### Steps to reproduce

1. Generate Rust bindings for the above spec with `rust-server`
1. Open generated `src/client/mod.rs` bindings, find `authenticate` method
1. Observe the serialization of the enum form:
    ```rust
    ```
1. Call this method and note that `target_resource` is supplied as `ResourceOne` or `ResourceTwo`, not their correct serializations

**Expected**: it should be set to the serialized version, `resource_one` or `resource_two`.

##### Suggest a fix

The RustServerCodegen.java file should check if the parameter is an enum and set `x-format-string` to `{}` instead of `{:?}` - this is safe because all models `impl Display` and all enums have `allowedValues` in their `impl Display`.
