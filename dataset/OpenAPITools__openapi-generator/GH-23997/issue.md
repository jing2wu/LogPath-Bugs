# [BUG] [JAVA,SPRING] @JsonTypeName ignores x-discriminator-value and discriminator mappings

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/23997
- Opened by SirCremefresh on 2026-06-11, closed on 2026-06-23
- Labels: Issue: Bug
- Fix commit: d3dde379a7b401ce971f4e89902dc4e6966b0b72

## Report

### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [x] Have you tested with the latest master to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?

### Description

For the `java` and `spring` generators, generated child models can get a Jackson `@JsonTypeName` annotation using the schema/model name instead of the discriminator value declared in the OpenAPI contract.

This breaks Jackson polymorphic serialization when the discriminator value differs from the schema name.

This is especially visible when `modelNameSuffix` is used, but the bug is not limited to suffix usage. It occurs whenever the generated `@JsonTypeName` uses the schema/model name while the contract discriminator value is different.

### OpenAPI declaration file content

```yaml
openapi: 3.0.1
info:
  title: x-discriminator-value JsonTypeName bug
  version: 1.0.0
paths:
  /locks:
    get:
      operationId: getLocks
      responses:
        '200':
          description: list of locks
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/BrLock'
components:
  schemas:
    LockType:
      type: string
      enum:
        - USER
        - COMPONENT

    BrLock:
      type: object
      required:
        - lockType
      properties:
        lockType:
          $ref: '#/components/schemas/LockType'
      oneOf:
        - $ref: '#/components/schemas/UserBrLock'
        - $ref: '#/components/schemas/ComponentBrLock'
      discriminator:
        propertyName: lockType
        mapping:
          USER: '#/components/schemas/UserBrLock'
          COMPONENT: '#/components/schemas/ComponentBrLock'

    BaseBrLock:
      type: object
      required:
        - lockType
      properties:
        lockType:
          $ref: '#/components/schemas/LockType'

    UserBrLock:
      x-discriminator-value: USER
      allOf:
        - $ref: '#/components/schemas/BaseBrLock'
        - type: object
          required:
            - userId
          properties:
            userId:
              type: string

    ComponentBrLock:
      x-discriminator-value: COMPONENT
      allOf:
        - $ref: '#/components/schemas/BaseBrLock'
        - type: object
          required:
            - componentId
          properties:
            componentId:
              type: string
```

### Generation Details

For the java generator:
```
openapi-generator-cli generate \
  -i discriminator-bug.yaml \
  -g java \
  -o /tmp/discriminator-java \
  --model-name-suffix ConsumerDTO \
  --additional-properties library=restclient,useOneOfInterfaces=true,useJakartaEe=true,serializableModel=true
```
For the spring generator:
```
openapi-generator-cli generate \
  -i discriminator-bug.yaml \
  -g spring \
  -o /tmp/discriminator-spring \
  --model-name-suffix ProviderDTO \
  --additional-properties interfaceOnly=true,useSpringBoot4=true,useJakartaEe=true
```
### Actual Output

The parent type contains the correct discriminator mapping:
```
@JsonSubTypes({
  @JsonSubTypes.Type(value = ComponentBrLockConsumerDTO.class, name = "COMPONENT")
})
```
But the generated child model uses the schema name in @JsonTypeName:
```
@JsonTypeName("ComponentBrLock")
public class ComponentBrLockConsumerDTO implements BrLockConsumerDTO {
}
```
Jackson can then serialize the discriminator as:
```
{
  "lockType": "ComponentBrLock"
}
```
### Expected Output

The child model should use the discriminator value:
```
@JsonTypeName("COMPONENT")
public class ComponentBrLockConsumerDTO implements BrLockConsumerDTO {
}
```
Jackson should serialize the discriminator as:
```
{
  "lockType": "COMPONENT"
}
```
### Related Issues / PRs

Related to #17343 and the partial JAX-RS fix in #23509 / commit 13e053a.

### Suggest a Fix

Use vendorExtensions.x-discriminator-value when rendering Jackson @JsonTypeName, falling back to the schema/model name only when no discriminator value is available.

## Comment by jpfinne on 2026-06-13

@SirCremefresh @seonwooj0810 x-discriminator-value is mainly used for swagger 2.  For openapi 3+, use the discriminator mapping.

You can change the API to:
```
components:
  schemas:
    LockType:
      type: string
      enum:
        - USER
        - COMPONENT
    BrLock:
      type: object
      required:
        - lockType
      properties:
        lockType:
          $ref: '#/components/schemas/LockType'
      oneOf:
        - $ref: '#/components/schemas/UserBrLock'
        - $ref: '#/components/schemas/ComponentBrLock'
      discriminator:
        propertyName: lockType
        mapping:
          USER: '#/components/schemas/UserBrLock'
          COMPONENT: '#/components/schemas/ComponentBrLock'
    UserBrLock:
      allOf:
        - $ref: '#/components/schemas/BrLock'
        - type: object
          required:
            - userId
          properties:
            userId:
              type: string

    ComponentBrLock:
      allOf:
        - $ref: '#/components/schemas/BrLock'
        - type: object
          required:
            - componentId
          properties:
            componentId:
              type: string
```

It generates a correct BrLockProviderDTO.java
```
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "lockType", visible = true)
@JsonSubTypes({
  @JsonSubTypes.Type(value = ComponentBrLockProviderDTO.class, name = "COMPONENT"),
  @JsonSubTypes.Type(value = UserBrLockProviderDTO.class, name = "USER")
})
e/Brussels]", comments = "Generator version: unset")
public interface BrLockProviderDTO {
  public LockTypeProviderDTO getLockType();
}
```

Unfortunately the child classes are invalid.  They extends and implements the parent.
```
public class ComponentBrLockProviderDTO extends BrLockProviderDTO implements BrLockProviderDTO {
```
This can be fixed by:

- removing the oneOf in BrLock
- using the new REPLACE_ONE_OF_BY_DISCRIMINATOR_MAPPING normalizer 
- with the API from #24003, REPLACE_ONE_OF_BY_DISCRIMINATOR_MAPPING also works: the `@JsonTypeName` is not generated in the child classes
