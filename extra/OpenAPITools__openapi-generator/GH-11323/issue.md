# [BUG,JAVA,SPRING] missing JsonValue import if allOf used as inline-scheme composition

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/11323
- Opened by souwa on 2022-01-15, closed on 2022-02-21
- Labels: Issue: Bug
- Fix commit: 735dae41a554787910da1cb5d62fda7b3debd978

## Report

##### Description
When using allOf as a composition inline-scheme without inheritance/discriminator the import `import com.fasterxml.jackson.annotation.JsonValue` for the Enum method `@JsonValue public String getValue()` is not added to the imports of the generated class.
 
This happens when the inline model doesn't have enums, but the parent does.

Also, the syntax that was used is the only workaround that prevents the generation of the redundant additional ParentTitle+AllOf class (see [Java generation of 'extra' class with allOf Workaraound](https://github.com/OpenAPITools/openapi-generator/issues/3100#issuecomment-703481081)):

```yaml
    Address:
      type: object
      properties:
        locationType:
          type: string
          enum:
            - VILLAGE
            - SMALL_TOWN
            - BIG_CITY
      allOf:
        - $ref: '#/components/schemas/BasicAddress'

    BasicAddress:
      type: object
      properties:
        street:
          type: string
        housenumber:
          type: string
        zip:
          type: string
        city:
          type: string
        country:
          type: string
```

The result includes the following imports from Jackson,
```java
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
```

 but not the JsonValue-Import: although the method is generated

```java
    @JsonValue
    public String getValue() {
      return value;
    }
```

##### openapi-generator version
openapi-generator v. 5.3.1 ( for java spring)

##### Related issues/PRs
If the generation of the additional unnecessary ParentTitle+AllOf class is fixed then I believe that will fix this problem as well.
[Opt-in solution to remove unnecessary model for inline schema composition](https://github.com/OpenAPITools/openapi-generator/pull/9834)

##### Suggest a fix
For the solution, this method [postProcessModelProperty (SpringCodegen)](https://github.com/OpenAPITools/openapi-generator/blob/0eca6291275394dab1bff79c9b4b6737202a9be9/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/SpringCodegen.java#L896) might probably be adapted at the point where Jackson imports are added and the model will be checked if it is or has enums or not.

## Comment by wing328 on 2022-02-21

The issue has been fixed by #11653 by @kthoms.

Please pull the latest master to give it another try.

## Comment by souwa on 2022-05-20

@kthoms, @wing328  Thank you:)!

## Comment by efriandika on 2022-07-06

Does the api spec you provide follow [OpenAPI inheritance  / polymorphism](https://swagger.io/docs/specification/data-models/inheritance-and-polymorphism/) standard? Although this spec does not provide "unecessary *allOf files", But I don't think this follow the standard.
