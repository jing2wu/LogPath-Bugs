# [BUG] [Java] Object defaults with enum properties generate invalid fluent builder expressions

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/24298
- Opened by nh-ive on 2026-07-14, closed on 2026-07-30
- Labels: Issue: Bug
- Fix commit: 095eedab261417fa4d674bb0e34c6d8520550c5b

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

<!-- describe what is the question, suggestion or issue and why this is a problem for you. -->
When a schema defines a default value for an object that contains an enum property, the Java generator generates an invalid fluent builder expression.

Expected output:
```java
private OutputFormat format = new OutputFormat().order(OutputFormat.OrderEnum.SIMILARITY).limit(10);
```

Actual output:
```java
private OutputFormat format = new OutputFormat().order("SIMILARITY").limit(10);
```

##### openapi-generator version

<!-- which version of openapi-generator are you using, is it a regression? -->
7.24.0-SNAPSHOT (latest master)

##### OpenAPI declaration file content or url


```yaml
openapi: "3.1.0"
info:
  title: Enum Default Issue Demo
  version: 1.0.0

components:
  schemas:
    OutputFormat:
      type: object
      properties:
        order:
          type: string
          enum:
            - IMPORTANCE
            - SIMILARITY
        limit:
          type: integer
      default:
        order: SIMILARITY
        limit: 10

    Formatter:
      type: object
      properties:
        format:
          $ref: '#/components/schemas/OutputFormat'
```

##### Generation Details

```xml
<plugin>
    <groupId>org.openapitools</groupId>
    <artifactId>openapi-generator-maven-plugin</artifactId>
    <version>7.24.0-SNAPSHOT</version>
    <executions>
        <execution>
            <goals>
                <goal>generate</goal>
            </goals>
            <configuration>
                <inputSpec>${project.basedir}/src/main/resources/api/OpenApi.yaml</inputSpec>
                <generatorName>java</generatorName>
                <library>native</library>
                <skipValidateSpec>true</skipValidateSpec>
                <generateApiTests>false</generateApiTests>
                <generateModelTests>false</generateModelTests>
                <configOptions>
                    <useJakartaEe>true</useJakartaEe>
                </configOptions>
            </configuration>
        </execution>
    </executions>
</plugin>
```

##### Steps to reproduce

<!-- unambiguous set of steps to reproduce the bug.-->

##### Related issues/PRs

<!-- has a similar issue/PR been reported/opened before? Please do a search in https://github.com/openapitools/openapi-generator/issues?utf8=%E2%9C%93&q=is%3Aissue%20 -->

##### Suggest a fix

<!-- if you can't fix the bug yourself, perhaps you can point to what might be
  causing the problem (line of code or commit), or simply make a suggestion -->
The issue seems to be that the if statement in the method `toObjectDefaultValue` of the class `AbstractJavaCodegen` is missing a case for enums.
