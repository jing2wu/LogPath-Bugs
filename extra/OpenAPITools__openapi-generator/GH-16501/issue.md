# [BUG,Kotlin] Cannot generate Map with nullable value type

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/16501
- Opened by dwawrzyniak1 on 2023-09-04, closed on 2026-03-04
- Labels: Issue: Bug
- Fix commit: 1283d1bf0fb564d45a9385287f1d4f11f203f35d

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

During migration from `java` to `kotlin` _Open API generator_ we encountered some issues with `Map<String, Any?>` data type. Our use case is:

1. Application A has a data class with a `val dynamicProperties: Map<String, Any?>` field in the API model
2. We use [sprindocs openapi-gradle-plugin](https://github.com/springdoc/springdoc-openapi-gradle-plugin) gradle plugin in version 1.7.0 to generate openApi.yml specification
3. We use _org.openapi.generator_ gradle plugin in version 7.0.0 with configuration described in _Generation Details_ to generate SDKs for API
4. Data class mentioned in point 1 has a `val dynamicProperties: Map<String, Any>` field in generated code.

Nullability of the values in this map is important for us and we don't want to change it. 

Would it be possible to support nullable value types in kotlin maps?

##### openapi-generator version

7.0.0

##### OpenAPI declaration file content or url

```yaml
openapi: 3.0.1
info:
  title: OpenAPI Petstore
  license:
    name: Apache-2.0
    url: https://www.apache.org/licenses/LICENSE-2.0.html
  version: 1.0.0
paths:
  /nullableMapValue:
    get:
      responses:
        '200':
          description: 'nullable map value'
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExampleClass'
components:
  schemas:
    ExampleClass:
      required:
        - dynamicProperties
      type: object
      properties:
        dynamicProperties:
          type: object
          additionalProperties:
            type: object

```

##### Generation Details

Gradle _org.openapi.generator_ plugin in version 7.0.0 was used with following configuration:

```
openApiGenerate {
  val packageName = "org.example"
  generatorName.set("kotlin")
  library.set("jvm-spring-webclient")
  inputSpec.set(tasks.generateOpenApiDocs.flatMap { it.outputFile })
  outputDir.set("$buildDir/generated/open-api-client")
  this.packageName.set(packageName)
  apiPackage.set("$packageName.api")
  modelPackage.set("$packageName.model")
  configOptions.set(
    mapOf(
      "serializationLibrary" to "jackson",
      "dateLibrary" to "java8",
      "useSpringBoot3" to "false",
      "enumPropertyNaming" to "UPPERCASE"
    )
  )
  importMappings.set(
    mapOf(
      "Pageable" to "org.springframework.data.domain.Pageable"
    )
  )
}
```

##### Steps to reproduce

It is reproducable by adding this test case to `KotlinModelCodegenTest.java` while having attached `yaml` added to test resources:

```
@Test(dataProvider = "generators")
    public void mapWithNullableValues(AbstractKotlinCodegen codegen) throws IOException {
        String outputPath = generateModels(codegen, "src/test/resources/3_0/maps-with-nullable-values.yaml", false);

        assertFileContains(
            Paths.get(outputPath + "/src/main/kotlin/models/ExampleClass.kt"),
            "val dynamicProperties: kotlin.collections.Map<kotlin.String, kotlin.Any>"
        );
    }
```

##### Related issues/PRs

No related issues found.
