# [BUG,JAVA,Spring] Pattern message not working in path param, query param and  header param

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/18959
- Opened by rodrigoma3 on 2024-06-18, closed on 2024-06-24
- Labels: Issue: Bug
- Fix commit: 5532203f9f421582ee219fcf187ff451948ad3b2

## Report

#### Bug Report Checklist

- [X] Have you provided a full/minimal spec to reproduce the issue?
- [X] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [X] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [X] Have you searched for related issues/PRs?
- [X] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

Pattern message not working in path param, query param and  header param for Java Spring

##### openapi-generator version

openapi-generator 7.7.0-SNAPSHOT (latest master)

##### OpenAPI declaration file content or url


```
openapi: 3.0.3
info:
  title: sample spec
  version: 1.0.0
paths:
  /test/{groupObj}:
    post:
      summary: Post to test
      description: ''
      operationId: postToTest
      parameters:
        - $ref: '#/components/parameters/groupObj'
        - $ref: '#/components/parameters/token'
        - $ref: '#/components/parameters/clientId'
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ObjTest'
      responses:
        201:
          description: success
components:
  parameters:
    groupObj:
      in: path
      name: groupObj
      required: true
      schema:
        type: string
        pattern: "[a-zA-Z]"
        x-pattern-message: "Only letters"
    token:
      in: query
      name: token
      required: true
      schema:
        type: string
        pattern: "[0-9a-fA-F]"
        x-pattern-message: "Only numbers and letters a-f"
    clientId:
      in: header
      name: clientId
      required: true
      schema:
        type: string
        pattern: "\\d"
        x-pattern-message: "Only numbers"
  schemas:
    ObjTest:
      description: A model to return
      type: object
      properties:
        field1:
          type: integer
          format: int64
        field2:
          type: string
          pattern: "\\w"
          x-pattern-message: "Only letters, numbers and underscore"
        field3:
          type: string
          pattern: "\\w"
```


##### Generation Details

```
<useResponseEntity>false</useResponseEntity>
<delegatePattern>true</delegatePattern>
<interfaceOnly>true</interfaceOnly>
<requestMappingMode>api_interface</requestMappingMode>
<useBeanValidation>true</useBeanValidation>
<performBeanValidation>true</performBeanValidation>
```

##### Steps to reproduce

Generate API with the specified spec and look in the TestApi interface for the _postToTest method that contains the 3 parameters with the @Pattern annotation without the message.

##### Related issues/PRs

No related issues/PRs found.

##### Suggest a fix

generated code:
```
default void _postToTest(
        @Pattern(regexp = "[a-zA-Z]") @Parameter(name = "groupObj", description = "", required = true, in = ParameterIn.PATH) @PathVariable("groupObj") String groupObj,
        @NotNull @Pattern(regexp = "[0-9a-fA-F]") @Parameter(name = "token", description = "", required = true, in = ParameterIn.QUERY) @Valid @RequestParam(value = "token", required = true) String token,
        @NotNull @Pattern(regexp = "\\d") @Parameter(name = "clientId", description = "", required = true, in = ParameterIn.HEADER) @RequestHeader(value = "clientId", required = true) String clientId,
        @Parameter(name = "ObjTest", description = "") @Valid @RequestBody(required = false) ObjTest objTest
    ) {
        postToTest(groupObj, token, clientId, objTest);
    }
```

code that must be generated:
```
default void _postToTest(
        @Pattern(regexp = "[a-zA-Z]", message = "Only letters") @Parameter(name = "groupObj", description = "", required = true, in = ParameterIn.PATH) @PathVariable("groupObj") String groupObj,
        @NotNull @Pattern(regexp = "[0-9a-fA-F]", message = "Only numbers and letters a-f") @Parameter(name = "token", description = "", required = true, in = ParameterIn.QUERY) @Valid @RequestParam(value = "token", required = true) String token,
        @NotNull @Pattern(regexp = "\\d", message = "Only numbers") @Parameter(name = "clientId", description = "", required = true, in = ParameterIn.HEADER) @RequestHeader(value = "clientId", required = true) String clientId,
        @Parameter(name = "ObjTest", description = "") @Valid @RequestBody(required = false) ObjTest objTest
    ) {
        postToTest(groupObj, token, clientId, objTest);
    }
```
