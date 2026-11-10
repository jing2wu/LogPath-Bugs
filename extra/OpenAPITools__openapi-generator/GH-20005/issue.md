# [BUG] [JAVA] allOf object are not correctly generated with properties REF_AS_PARENT_IN_ALLOF=true and REFACTOR_ALLOF_WITH_PROPERTIES_ONLY=true

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/20005
- Opened by JelmerBouma1985 on 2024-10-31, closed on 2024-11-13
- Labels: Issue: Bug
- Fix commit: 301af6050b517f518ab534edce3f728e5100dbf8

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?

##### Description

Since release of 7.9.0 allOf objects don´t extend the parent anymore when normalizer REF_AS_PARENT_IN_ALLOF=true and REFACTOR_ALLOF_WITH_PROPERTIES_ONLY=true are used.

I expect the child object extends the parent object which works as expected until 7.9.0. Below generated code from 7.8.0:
```java
public class Child1 extends Parent {
...
}
```

below code is generated code from 7.9.0

```java
public class Child1 {
...
}
```

##### openapi-generator version

7.9.0

##### OpenAPI declaration file content or url
test.yaml
```yaml
openapi: 3.0.0
info:
  title: 'AllOf does not work'
  description: 'Minimal yaml to showcase allOf does not work anymore'
  version: info
paths:
  /allOf:
    get:
      operationId: allOf
      responses:
        "200":
          description: oke
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Parent'
components:
  schemas:
    Parent:
      type: object
      properties:
        p1:
          type: integer
    Child1:
      properties:
        p2:
          type: string
      allOf:
        - $ref: '#/components/schemas/Parent'

```

##### Generation Details

I'm using the openapi-generator-maven-plugin

```xml
<plugin>
                <groupId>org.openapitools</groupId>
                <artifactId>openapi-generator-maven-plugin</artifactId>
                <version>7.9.0</version>
                <configuration>
                    <openapiNormalizer>REF_AS_PARENT_IN_ALLOF=true,REFACTOR_ALLOF_WITH_PROPERTIES_ONLY=true</openapiNormalizer>
                    <generatorName>spring</generatorName>
                    <configOptions>
                        <useSpringBoot3>true</useSpringBoot3>
                        <interfaceOnly>true</interfaceOnly>
                    </configOptions>
                </configuration>
                <executions>
                    <execution>
                        <id>allOf</id>
                        <goals>
                            <goal>generate</goal>
                        </goals>
                        <configuration>
                            <inputSpec>${basedir}/src/main/resources/openapi/Showcase.yaml</inputSpec>
                            <generatorName>spring</generatorName>
                            <generateSupportingFiles>true</generateSupportingFiles>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
```

##### Steps to reproduce
java -jar openapi-generator-cli.jar generate -g spring -i test.yaml -o output/ --openapi-normalizer REF_AS_PARENT_IN_ALLOF=true,REFACTOR_ALLOF_WITH_PROPERTIES_ONLY=true

## Comment by wing328 on 2024-11-01

thanks for reporting the issue. i will try to take a look over the weekend

## Comment by wing328 on 2024-11-12

UPDATE: I've filed #20083 to fix the issue

## Comment by AlexanderEvstatiev on 2024-12-04

This issue is still present in 7.10.0. The latest version it works is 7.1.0. Please check again. Meanwhile 7.1.0 has another issue which creates conflicting setters when using the normalizer flags, so major version 7 is unusable for such examples at the moment.

## Comment by wing328 on 2024-12-05

@AlexanderEvstatiev can you please share your spec (minimal) to reproduce the issue?

@JelmerBouma1985 does the fix (in v7.10.0) work for you?

## Comment by JelmerBouma1985 on 2024-12-05

> @JelmerBouma1985 does the fix (in v7.10.0) work for you?

@wing328 yes, v7.10.0 works like a charm 👍

## Comment by AlexanderEvstatiev on 2024-12-05

@wing328 
These definitions are in a task-base.yaml schema
```
AbstractOperation:
  required:
    - code
  type: object
  properties:
    code:
      type: string
    comment:
      type: string
Response:
  allOf:
    - $ref: '#/components/schemas/AbstractOperation'
Action:
  allOf:
    - $ref: '#/components/schemas/AbstractOperation'
```

And are being referenced in the task-api.yaml like this:

```
content:
  application/json:
    schema:
      $ref: './task-base.yaml#/components/schemas/Action'
```

The last confirmed working version for these schemas was 4.3.1 if that helps.

java -jar openapi-generator-cli-7.10.0.jar generate --input-spec task-api.yaml --generator-name spring --output dma --openapi-normalizer REF_AS_PARENT_IN_ALLOF=true,REFACTOR_ALLOF_WITH_PROPERTIES_ONLY=true --additional-properties=containerDefaultToNull=true,useJakartaEe=true,skipDefaultInterface=true,hideGenerationTimestamp=true --artifact-id dma --api-package test --model-name-prefix Api --model-package test.model.api  --type-mappings=URI=String --type-mappings=AnyType=Object --schema-mappings=...

## Comment by voidMainReturn0 on 2025-02-21

This still doesn't work with 7.9, 7.10 or 7.11
Here's my spec :
```
/scripts/search:
    post:
      operationId: getScriptByFilter
      requestBody:
        description: JSON Request Data
        content:
          application/json:
            schema:
              allOf:
                - $ref: "#/components/schemas/ScriptSearchRequest"
                - $ref: "HttpServletRequest"

```

openapi plugin config
```
<plugin>
    <groupId>org.openapitools</groupId>
    <artifactId>openapi-generator-maven-plugin</artifactId>
    <version>${openapi.generator.maven.plugin}</version>
    <executions>
        <execution>
            <goals>
                <goal>generate</goal>
            </goals>
            <configuration>
                <inputSpec>${project.basedir}/api-spec/ApiSpec.yaml</inputSpec>
                <generatorName>spring</generatorName>
                <output>${project.build.directory}/generated-sources/</output>
                <generateSupportingFiles>false</generateSupportingFiles>
                <apiPackage>${default.package}.api</apiPackage>
                <modelPackage>${default.package}.models</modelPackage>
                <configOptions>
                    <skipDefaultInterface>true</skipDefaultInterface>
                    <interfaceOnly>true</interfaceOnly>
                    <useSpringBoot3>true</useSpringBoot3>
                    <schemaInheritanceSupport>true</schemaInheritanceSupport>
                    <modelInheritance>true</modelInheritance>
                </configOptions>
                <openapiNormalizer>REF_AS_PARENT_IN_ALLOF=true</openapiNormalizer>
                <importMappings>
                    <importMapping>HttpServletRequest=jakarta.servlet.http.HttpServletRequest</importMapping>
                </importMappings>
            </configuration>
        </execution>
    </executions>
</plugin>
```
But the generator is not generating the correct contract in the .java file. The contract generated is like this

```
ResponseEntity<> getScriptByFilter(
        @Parameter(name = "GetScriptByFilterRequest", description = "JSON Request Data", required = true) @Valid @RequestBody GetScriptByFilterRequest getScriptByFilterRequest
    );
```
