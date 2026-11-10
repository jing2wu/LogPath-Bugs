# [BUG,Kotlin-Spring] Wrong parameter type for multipart-form-data file upload when using kotlin-spring with reactive

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/21548
- Opened by cgual206 on 2025-07-11, closed on 2026-07-30
- Labels: Issue: Bug
- Fix commit: a282c80979754e13663a308ba1beba3c992329bf

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

The kotlin-spring generator allows users to generate Spring Boot controllers & service interfaces for both reactive ([Spring WebFlux](https://docs.spring.io/spring-framework/reference/web/webflux.html)) or non-reactive ([Spring MVC](https://spring.io/guides/gs/serving-web-content)) servers.  

The WebFlux or MVC variants of Spring have different mechanisms to support file upload using multipart-form-data.  

The kotlin-spring generator is creating controllers & interfaces which are appropriate for Spring MVC, but not for Spring WebFlux, even when the `reactive` option is set to `true` in the generator config.

##### openapi-generator version

version 7.14.0

##### OpenAPI declaration file content or url

```yaml
  /upload:
    post:
      summary: uploads a file
      operationId: uploadFile
      tags:
        - upload
      description: upload a file
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                  description: file to upload
      responses:
        201:
          description: upload was successful
```

##### Generation Details

Full pom.xml & an openapi spec can be found in this [Gist](https://gist.github.com/btpnlsl/abb323ab06a638feddaa2c55a143c8e7)

The OpenAPI generator section of the Maven POM.xml file is

```xml
            <plugin>
                <groupId>org.openapitools</groupId>
                <artifactId>openapi-generator-maven-plugin</artifactId>
                <version>${openapi-generator.version}</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>generate</goal>
                        </goals>
                        <configuration>
                            <inputSpec>${project.basedir}/src/main/resources/openapi-spec.yaml</inputSpec>
                            <generatorName>kotlin-spring</generatorName>
                            <library>spring-boot</library>
                            <generateApiTests>false</generateApiTests>
                            <generateApiDocumentation>false</generateApiDocumentation>
                            <generateModelTests>false</generateModelTests>
                            <generateModelDocumentation>false</generateModelDocumentation>
                            <generateSupportingFiles>false</generateSupportingFiles>
                            <configOptions>
                                <useSpringBoot3>true</useSpringBoot3>
                                <reactive>true</reactive>
                                <serviceInterface>true</serviceInterface>
                            </configOptions>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
``` 

The resulting controller method looks like this

```kotlin
    @Operation(
        summary = "uploads a file",
        operationId = "uploadFile",
        description = """upload a file""",
        responses = [
            ApiResponse(responseCode = "201", description = "upload was successful") ]
    )
    @RequestMapping(
        method = [RequestMethod.POST],
        value = ["/upload"],
        consumes = ["multipart/form-data"]
    )
    suspend fun uploadFile(@Parameter(description = "file to upload") @Valid @RequestPart("file", required = false) file: org.springframework.web.multipart.MultipartFile?): ResponseEntity<Unit> {
        return ResponseEntity(service.uploadFile(file), HttpStatus.valueOf(201))
    }
```

and the results interface method looks like 

```kotlin
    suspend fun uploadFile(file: org.springframework.web.multipart.MultipartFile?): Unit
```

This would be valid for non-reactive Spring MVC but is not valid for reactive Spring WebFlux.

##### Steps to reproduce

`mvn clean generate-sources`

##### Related issues/PRs

<!-- has a similar issue/PR been reported/opened before? Please do a search in https://github.com/openapitools/openapi-generator/issues?utf8=%E2%9C%93&q=is%3Aissue%20 -->

There was a similar issue created for the Java Spring generator: [#6993 ](https://github.com/OpenAPITools/openapi-generator/pull/6993)

The change to support Spring MVC was made in this PR: #20108 

##### Suggest a fix

The Java support for reactive multipart-form-data uploads looks like it modified the following template files:

- [apiDelegate.mustache](https://github.com/OpenAPITools/openapi-generator/blob/65cb95bef048b5110fda362feee52e76795fa26d/modules/openapi-generator/src/main/resources/JavaSpring/apiDelegate.mustache#L71)
- [api.mustache](https://github.com/OpenAPITools/openapi-generator/blob/65cb95bef048b5110fda362feee52e76795fa26d/modules/openapi-generator/src/main/resources/JavaSpring/api.mustache#L278)
- [formParams.mustache](https://github.com/OpenAPITools/openapi-generator/blob/65cb95bef048b5110fda362feee52e76795fa26d/modules/openapi-generator/src/main/resources/JavaSpring/formParams.mustache#L1)

The general template logic for creating a parameter distinguishes between whether the parameters is a file or not, and if so, is it reactive or not, similar to this (from api.mustache):

```mustache
        {{#allParams}}
          {{^isFile}}
            {{^isBodyParam}}
              {{>optionalDataType}}
            {{/isBodyParam}}
            {{#isBodyParam}}
              {{^reactive}}
                {{>optionalDataType}}
              {{/reactive}}
              {{#reactive}}
                {{^isArray}}
                    Mono<{{{dataType}}}>
                {{/isArray}}
                {{#isArray}}
                    Flux<{{{baseType}}}>
                {{/isArray}}
              {{/reactive}}
            {{/isBodyParam}}
          {{/isFile}}
          {{#isFile}}
            {{#reactive}}
                Flux<Part>
            {{/reactive}}
            {{^reactive}}
              {{#isArray}}
                  List<MultipartFile>
              {{/isArray}}
              {{^isArray}}
                  MultipartFile
              {{/isArray}}
            {{/reactive}}
          {{/isFile}}
          {{paramName}}
          {{^-last}}, {{/-last}}
        {{/allParams}}
```

For some reason I don't understand the template logic is different in Java Spring's api.mustache vs apiDelegate.mustache.

On the kotlin-spring side of things it looks like the `MultipartFile` class is only referenced in [optionalDataType.mustache](https://github.com/OpenAPITools/openapi-generator/blob/65cb95bef048b5110fda362feee52e76795fa26d/modules/openapi-generator/src/main/resources/kotlin-spring/optionalDataType.mustache#L1)

I'm not sure that this is the right place to template File params, but I'm also unsure about what is the function of `optionalDataType.mustache` in the Kotlin Spring generator.  In the Java Spring generator, the same file looks like it is designed to use / not-use the `Optional` class in order to do null checking.  In the Kotlin Spring generator, prior to the change which added support for `MultipartFile`, `optionalDataType.mustache` was about whether to use the Kotlin `?` null-operator for non-required data types which did not have a default value that might be null.

I think having File / not-File & reactive / non-reactive template logic in `optionalDataType.mustache` might be the wrong place and the logic should be moved to a higher level like `apiDelegate.mustache` & `formParams.mustache`.  Additionally, `optionalDataType.mustache` is used in a bunch of other template files in the Kotlin Spring generator for header, cookie, body & path parameters (for example), where the logic to use a `MultipartFile` vs `Flux<Part>` not may not be applicable or desirable.

## Comment by cgual206 on 2025-07-14

Also of interest, I think there is also a bug with how Java Spring is handling the parameter type for multipart-form-data with multi file uploads: [https://github.com/OpenAPITools/openapi-generator/issues/21559](https://github.com/OpenAPITools/openapi-generator/issues/21559)

## Comment by Picazsoo on 2026-02-17

Hello @btpnlsl

I _tried_ to prepare some general comprehensive fix for **java-spring** for multipart-form-data and would like to eventually also do the same for **kotlin-spring** if the java version is deemed correct. However I would definitely need some good pair of eyes or two to check whether my approach is ok:
https://github.com/OpenAPITools/openapi-generator/pull/22930

My knowledge in this domain is quite limited and the documentation to my best understanding also seemed to be a bit inconsistent. So I tried to create very complex examples of open api spec and also complex integration tests which I am running in both reactive and blocking mode. The tests are currently passing (as a part of the ci pipeline)

blocking - controller impl (with asserts) - https://github.com/OpenAPITools/openapi-generator/pull/22930/changes#r2800259876 and tests - https://github.com/OpenAPITools/openapi-generator/pull/22930/changes#r2800263225
reactive - controller impl (with asserts) - https://github.com/OpenAPITools/openapi-generator/pull/22930/changes#r2800251171 and tests - https://github.com/OpenAPITools/openapi-generator/pull/22930/changes#r2800256108

## Comment by kadamar on 2026-06-10

i only can confirm 
generated with reactive in 7.12:
Flux<Part> files,

generated in latest:
Part files,


@Picazsoo 
is PR will be merged?


workaround 
change one part to array
```
                file:
                  type: array
                  items:
                    type: string
                    format: binary
```
