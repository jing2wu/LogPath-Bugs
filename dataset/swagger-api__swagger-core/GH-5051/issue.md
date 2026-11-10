# [Bug]: Array schema description leaks into items

- Issue: https://github.com/swagger-api/swagger-core/issues/5051
- Opened by jochenberger on 2026-02-05, closed on 2026-02-26
- Labels: Bug
- Fix commit: 6143beea76144a2ae1ab2a09f1c99a59ef83acfb

## Report

I have an annotation like this
```java
 @ApiResponse(
      responseCode = "201",
      content = @Content(
              mediaType = MediaType.APPLICATION_JSON_VALUE,
              array =
                  @ArraySchema(
                          arraySchema = @Schema(description = "Array description"),
                      schema =
                          @Schema(
                              description = "Item description",
                              implementation = Item.class
                              )))))
List<Item> doSomething();
```
The generated schema looks like this:
```
[
  type:array,
  description: Array description,
  items: [
    $ref:#/components/schemas/Item,
    description:Array description
  ]
]
```
The array description overrides the item description.

If I remove the `implementation = Item.class`, I get
```
[
  type:array,
  description: Array description,
  items: [
    type:string,
    description:Item description
  ]
]
```
The item description is there, but the type is wrong. IIUC, It should be deduced from the method signature.

If I remove the whole  `schema = ...` part, I get
```
[
  type:array,
  description: Array description
]
```
The items section is missing completely. At least the type info should be there.

I remember there were similar issues in the *components* schema generation. This concerns the API response schemas. I assumed they were using the same logic.

## Comment by Mattias-Sehlstedt on 2026-02-05

Hi @jochenberger, could we specify whether you are resolving to a 3.1 or a 3.0 OpenAPI specification? I believe there are certain issues that are specifically tied to 3.1, and this sound very similar to that kind of issue.

## Comment by jochenberger on 2026-02-05

Yes, I'm generating 3.1 with the latest version. Sorry, I should have included that in the description right away.

## Comment by Mattias-Sehlstedt on 2026-02-09

It is most likely tied to the issue [discussed here](https://github.com/swagger-api/swagger-core/pull/5048), were the introspection is overeager with trying to handle potential OAS 3.1 siblings, and thus branch into a path that does not produce the same result as 3.0.

I could investigate once my my [current fix](https://github.com/swagger-api/swagger-core/pull/5049) on the area are reviewed and merged.

## Comment by jochenberger on 2026-02-09

I can test once a new version including your fix is released.

## Comment by Mattias-Sehlstedt on 2026-02-14

I have investigated the issue a bit further and to me it seems like the current intended behavior of `content = @Content(...)` is to allow for a complete redefinition of what the endpoint serves. I.e., if annotations are present, those and those alone are used to generate the OpenApi-specification. And if they are omitted it deduces the types as per usual. 

This means that if you want to add an extra description you will have to make sure to add all information that you expect to be present (so for the second example, that you keep the `implementation = ...`). But I cannot for certain say that this is something intentional for `@Content`.

The behavior presented in the first scenario is a bug. But I have yet to find the correct solution for it.

## Comment by ewaostrowska on 2026-02-26

This issue has been resolved in https://github.com/swagger-api/swagger-core/pull/5055 and will be part of the next release. Thank you for pointing this issue out!
