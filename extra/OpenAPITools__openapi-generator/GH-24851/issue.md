# [BUG,KOTLIN,jvm-ktor] Inline enum array default generates invalid Kotlin -> compile error

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/24851
- Opened by MattFromGer on 2026-09-03, closed on 2026-09-14
- Labels: Issue: Bug
- Fix commit: 5a0fa873919d662c2223df94637cea25bfbca2aa

## Report

##### Description

Since 7.25.0, an inline enum array default generates invalid Kotlin:

```kotlin
colors: Set<String>? =
    Set<Color>.setOfLeft_ParenthesisColorPeriodRedCommaColorPeriodBlueRight_Parenthesis
```

Expected:

```kotlin
colors: Set<String>? = setOf("red", "blue")
```

##### openapi-generator version

`7.25.0`. Regression from `7.24.0`, exposed by [#24556](https://github.com/OpenAPITools/openapi-generator/pull/24556).

##### OpenAPI declaration file content or url

```yaml
openapi: 3.0.3
info:
  title: Reproduction
  version: 1.0.0
paths:
  /items:
    get:
      operationId: getItems
      parameters:
        - name: colors
          in: query
          schema:
            type: array
            uniqueItems: true
            items:
              type: string
              enum: [red, blue]
            default: [red, blue]
      responses:
        "204":
          description: No content
```

##### Generation Details

```shell
openapi-generator-cli generate -g kotlin -i repro.yaml -o out \
  -p library=jvm-ktor,serializationLibrary=jackson
```

##### Steps to reproduce

1. Generate the client with 7.25.0.
2. Compile the generated code.
3. Observe unresolved `Color` and mangled `setOf...` references.

##### Related issues/PRs

- [#24556](https://github.com/OpenAPITools/openapi-generator/pull/24556) added default values to optional `jvm-ktor` parameters and exposed this issue.
- [#20394](https://github.com/OpenAPITools/openapi-generator/issues/20394) reports a similar invalid default for an array of inline enum values in the Kotlin `jvm-retrofit2` generator.
- [#14873](https://github.com/OpenAPITools/openapi-generator/issues/14873) concerns invalid Kotlin defaults for arrays of referenced enums.

##### Suggest a fix

`KotlinClientCodegen.adjustEnumRefDefault()` treats the complete container default as a scalar enum value. Skip containers:

```diff
if (StringUtils.isEmpty(param.defaultValue)
+       || param.isContainer
        || !(param.isEnum || param.isEnumRef)) {
```

Additionally, render inline enum-array parameter defaults according to their exposed type:

```kotlin
setOf("red", "blue")
```
