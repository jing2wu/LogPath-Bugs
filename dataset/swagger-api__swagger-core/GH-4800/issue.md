# BUG @Schema annotation is propagated from a property to the class defined in @Schema#implementation 

- Issue: https://github.com/swagger-api/swagger-core/issues/4800
- Opened by OllieKosh on 2024-11-28, closed on 2025-09-16
- Labels: Bug, P2
- Fix commit: 0b467f3366e3edadd71bef8dcfd9e19fe6b643a9

## Report

### Problem
When `Schema#implementation` is defined on a property, all information specified through `@Schema` is propagated to the schema created for the type defined in `Schema#implementation`. However this information should only be used when generating the property schema. I am using Open API 3.1. This problem was introduced after upgrading from 2.2.22 to 2.2.25.

### Expected behavior
`@Schema` annotation is processed on the property level, but not used in schema generation for the class specified in `Schema#implementation` of that property.

For example if I have the following DTO
```
public class Example {
    @Schema(implementation = MyEnum.class, description = "My description", defaultValue = "yes")
    private String whyYes;
    //getters, setters
}
``` 
and MyEnum class looks like this
```
enum MyEnum {
    yes, no
}
```
the generated contract for the two components is expected to look like this
```
  schemas:
    Example:
      type: object
      properties:
        whyYes:
          description: My description
          $ref: "#/components/schemas/MyEnum"
          default: "yes"
    MyEnum:
      type: `string`
      enum:
      - "yes"
      - "no"
```
However current behavior propagates the schema annotation (and the properties from that schema annotation, in this case `description` and `defaultValue`) to the underlying object, which is incorrect
```
  schemas:
    Example:
      type: object
      properties:
        whyYes:
          description: My description
          $ref: "#/components/schemas/MyEnum"
          default: "yes"
    MyEnum:
      type: string
      description: My description
      default: "yes"
      enum:
      - "yes"
      - "no"
```
Note that if `@Schema#implementation` was not specified this problem would not occur.

### Reproducer
Add something similar to the provided example above (if using enum, set enums to be resolved as references) to this [test class](https://github.com/swagger-api/swagger-core/blob/c37b72cc653c41dc1ab90a4e10d2c957c84d52d4/modules/swagger-core/src/test/java/io/swagger/v3/core/resolving/Ticket4679Test.java) (which was created to test the solutions for this [issue](https://github.com/swagger-api/swagger-core/issues/4679)).

### Investigation
While previously `@Schema` and `@ArraySchema` annotations were not added to the annotation list, which is then added to the type of the property to be processed, this [change](https://github.com/swagger-api/swagger-core/pull/4720) introduced the behavior where it actually gets added to the list of annotations which are passed to the underlying object. This does not seem to be the right solution, since the class for the property should be agnostic of the `@Schema`/`@ArraySchema` annotations on the field where it is used.

## Comment by ewaostrowska on 2025-09-16

Hi @OllieKosh, 
Thanks for reporting the issue and providing the steps to reproduce the issue. It should be fixed in the new release :)
