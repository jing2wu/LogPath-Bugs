# [BUG] [kotlin-client,kotlin-spring] Discriminator is serialized twice when defined as property

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/21733
- Opened by dgenchev-uniper on 2025-08-12, closed on 2025-08-27
- Labels: Issue: Bug
- Fix commit: 8ce639ddae7b20fc7e0b98f011ca350f04cee3fd

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
Also please indicate in the issue title which language/library is concerned. Eg:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

When the property used as discriminator is specified as a property within the model definitions and jackson is used as serialization library, the discriminator is serialized twice.

##### openapi-generator version

7.14.0

##### OpenAPI declaration file content or url

```yaml
components:
  schemas:
    ShapeType:
      type: string
      enum:
        - TRIANGLE
        - SQUARE
    Shape:
      type: object
      required:
        - type
      properties:
        type:
          $ref: "#/components/schemas/ShapeType"
      discriminator:
        propertyName: type
        mapping:
          TRIANGLE: '#/components/schemas/Triangle'
          SQUARE: '#/components/schemas/Square'
    Triangle:
      allOf:
        - $ref: '#/components/schemas/Shape'
        - type: object
          required:
            - base
            - height
          properties:
            base:
              type: number
            height:
              type: number
    Square:
      allOf:
        - $ref: '#/components/schemas/Shape'
        - type: object
          required:
            - side
          properties:
            side:
              type: number

```

produces

```json
[
    {
        "type": "TRIANGLE",
        "base": 1,
        "height": 1,
        "type": "TRIANGLE"
    },
    {
        "type": "SQUARE",
        "side": 1,
        "type": "SQUARE"
    }
]
```

##### Generation Details

Using gradle plugin 
```kotlin
configOptions.set(
    mapOf(
        "dateLibrary" to "java8",
        "disallowAdditionalPropertiesIfNotPresent" to "false",
        "documentationProvider" to "none",
        "enumPropertyNaming" to "original",
        "exceptionHandler" to "false",
        "hideGenerationTimestamp" to "true",
        "interfaceOnly" to "true",
        "modelMutable" to "true",
        "serializationLibrary" to "jackson",
        "useSpringBoot3" to "true",
        "useTags" to "true",
    )
)
```

##### Steps to reproduce

1. Generate using jackson as serialization library
2. Check the JSON payload.

##### Related issues/PRs
Issue [#9441](https://github.com/OpenAPITools/openapi-generator/issues/9441) / PR [#11691](https://github.com/OpenAPITools/openapi-generator/pull/11691)

Issue [#3796](https://github.com/OpenAPITools/openapi-generator/issues/3796)

##### Suggest a fix

Adopt existing solution from Java / JavaSpring

## Comment by dgenchev-uniper on 2025-08-12

I created [#21734](https://github.com/OpenAPITools/openapi-generator/pull/21734) as proposed solution
