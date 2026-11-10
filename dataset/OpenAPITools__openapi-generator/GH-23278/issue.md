# [BUG,rust] oneOf array enums produce invalid syntax for generated object types

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/23278
- Opened by rgroothuijsen on 2026-03-17, closed on 2026-03-22
- Labels: Issue: Bug
- Fix commit: 165465a92ae243f657313fbae161127f26938b2e

## Report

##### Description

This is a continuation of #21599 which fixed arrays in enums for primitive types, but syntax errors still arise for generated types as pointed out in [this comment](https://github.com/OpenAPITools/openapi-generator/pull/21599#issuecomment-4039761015). Instead of enum values like `ArrayVecString(Vec<String>)`, it will produce values like `ArrayVecmodels::TestObject(Vec<models::TestObject>)`, where the first set of double colons produces the problem. 

##### openapi-generator version

7.21.0

##### OpenAPI declaration file content or url

```yaml
openapi: 3.1.0
info:
  title: oneOf with object arrays
  description: Support object types in oneOf array enums.
  version: 1.0.0
components:
  schemas:
    ObjectArrays:
      type: object
      properties:
        Options:
          oneOf:
            - type: array
              items:
                $ref: '#/components/schemas/TestObject'
            - type: array
              items:
                $ref: '#/components/schemas/TestArray'
    TestObject:
      type: object
      properties:
        test:
          type: string
    TestArray:
      properties:
        test:
          type: array
          items:
            type: string
```

##### Steps to reproduce

Run the Rust client generator with default settings and the above YAML file.

##### Suggest a fix

Since I'm already looking into this, I'll create a PR for it.
