# [BUG,Kotlin-Spring] JsonSetter(nulls = Nulls.FAIL) generated for nullable properties

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/24139
- Opened by swurzinger on 2026-06-26, closed on 2026-06-28
- Labels: Issue: Bug
- Fix commit: 2c7bbce6fc9d9fa657da29b9f76f470f65418fc9

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [ ] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. E.g.:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

The generator adds `@field:JsonSetter(nulls = Nulls.FAIL)` annotation for nullable properties when using OAS 3.1 nullable style (e.g. `type: [ object, "null" ]`) on $ref schema.

##### openapi-generator version

7.23.0

##### OpenAPI declaration file content or url

```yaml
openapi: 3.1.1
info:
  title: Test
  version: 1.0.0

components:
  schemas:
    NestedNullable:
      type: [ object, "null" ]
      properties:
        value:
          type: [ number, "null" ]
    Nested:
      type: object
      properties:
        value:
          type: [ number, "null" ]

    Item:
      type: object
      properties:
        nestedNullable:
          $ref: '#/components/schemas/NestedNullable'
          
        nestedNullable2:
          anyOf:
            - $ref: '#/components/schemas/Nested'
            - type: 'null'
              
        nested:
          $ref: '#/components/schemas/Nested'

```

##### Generation Details

```kotlin
    generatorName.set("kotlin-spring")

    configOptions.set(mapOf(
        "dateLibrary" to "java8",
        "library" to "spring-boot",
        "interfaceOnly" to "true",
        "useSpringBoot3" to "true",
        "useTags" to "true",
        "documentationProvider" to "none",
        "serializableModel" to "false",
        "useBeanValidation" to "true",
        "openApiNullable" to "false",
        "skipDefaultInterface" to "true",
    ))
```

The generator creates different annotations for `nestedNullable` and `nestedNullable2`, although the spec in the schema is equivalent. Below is the generated kotlin code for object `Item`. The generated code for `NestedNullable` and `Nested` is identical (as expected).

```kotlin
data class ItemSapDto(

    @field:Valid
    @field:JsonSetter(nulls = Nulls.FAIL)
    @get:JsonProperty("nestedNullable") val nestedNullable: NestedNullableSapDto? = null,

    @field:Valid
    @get:JsonProperty("nestedNullable2") val nestedNullable2: NestedSapDto? = null,

    @field:Valid
    @field:JsonSetter(nulls = Nulls.FAIL)
    @get:JsonProperty("nested") val nested: NestedSapDto? = null
) { }
```


##### Steps to reproduce

1. Setup a project with Kotlin-Spring OpenAPI generator with the provided configuration.
2. Create a OAS 3.1 schema with a $ref to a nullable type (e.g. `type: [ object, "null" ]`)
3. Generate the Kotlin classes and observe that the generated field contains `@field:JsonSetter(nulls = Nulls.FAIL)` annotation.

##### Related issues/PRs

https://github.com/OpenAPITools/openapi-generator/pull/23804 by @Picazsoo 
https://github.com/OpenAPITools/openapi-generator/issues/23976

##### Suggest a fix

The generator should treat the cases `nestedNullable` and `nestedNullable2` the same.

## Comment by Picazsoo on 2026-06-26

Thanks for the bug report. I will take a look and will try to provide a fix for 7.24

## Comment by Picazsoo on 2026-06-26

It seems to be a bug in the OpenApiNormalizer when normalizing from OAS 3.1.x to OAS 3.0.x
