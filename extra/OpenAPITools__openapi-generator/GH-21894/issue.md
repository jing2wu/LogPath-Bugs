# [BUG] [Rust] Generator produces empty structs for anyOf schemas

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/21894
- Opened by timvw on 2025-09-04, closed on 2025-09-06
- Labels: Issue: Bug
- Fix commit: ee40887d47f6d7a16318772f49c63b8eb0553488

## Report

## Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [x] Have you tested with the latest master to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?

## Description

The OpenAPI Generator for Rust produces empty structs when encountering `anyOf` schemas, making it impossible to use these types properly. This issue affects any OpenAPI specification that uses `anyOf` to define fields that can accept multiple types (e.g., a string or an enum).

While `oneOf` support was added in previous PRs (#20336, #20101), the `anyOf` construct remains unsupported and generates unusable empty structs.

## OpenAPI Generator Version

- 7.10.0
- 7.15.0  
- 7.16.0-SNAPSHOT (latest master)

## OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths:
  /test:
    get:
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TestResponse'
components:
  schemas:
    TestResponse:
      type: object
      properties:
        model:
          $ref: '#/components/schemas/ModelIdentifier'
    ModelIdentifier:
      description: Model identifier that can be a string or specific enum value
      anyOf:
        - type: string
          description: Any model name as string
        - type: string
          enum:
            - gpt-4
            - gpt-3.5-turbo
            - dall-e-3
          description: Known model enum values
```

## Steps to Reproduce

```bash
# Using Docker
docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli:latest generate \
    -i /local/spec.yaml \
    -g rust \
    -o /local/generated \
    --package-name test_api

# Examine the generated file
cat generated/src/models/model_identifier.rs
```

## Current Behavior (Actual Output)

The generator produces an empty struct that cannot hold any data:

```rust
#[derive(Clone, Default, Debug, PartialEq, Serialize, Deserialize)]
pub struct ModelIdentifier {
}

impl ModelIdentifier {
    pub fn new() -> ModelIdentifier {
        ModelIdentifier {
        }
    }
}
```

## Expected Behavior

The generator should produce a usable type that can handle both variants. Following the pattern used for `oneOf`, it should generate an untagged enum:

```rust
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(untagged)]
pub enum ModelIdentifier {
    String(String),
}
```

## Impact

This makes the generated client unusable for any API that uses `anyOf` schemas. Real-world examples include:

- OpenAI API: Model parameters that accept either a string or predefined model enum

## Related Issues

- #1369 - Related issue about `oneOf` not generating enums (marked as fixed, but only for `oneOf`, not `anyOf`)
- #20101 - Rust-Axum `oneOf` handling 
- #20336 - PR that fixed `oneOf` support for Rust client

## Proposed Solution

The `anyOf` construct should be handled similarly to how `oneOf` is currently handled in the Rust generator. Since Rust's serde untagged enum will deserialize to the first matching variant, this approach works well for `anyOf` semantics where one or more schemas must match.

The fix would involve extending the existing `oneOf` logic in `RustClientCodegen.java` to also process `anyOf` schemas, generating the same untagged enum structure.

## Workaround

Currently, users must either:

1. Modify the OpenAPI spec to change `anyOf` to `oneOf` before generation
2. Post-process the generated code to replace empty structs with proper types
3. Use `serde_json::Value` and lose all type safety

## Suggest a fix

I have a PR ready that extends the existing `oneOf` implementation to handle `anyOf` schemas in the same way, which resolves this issue.
