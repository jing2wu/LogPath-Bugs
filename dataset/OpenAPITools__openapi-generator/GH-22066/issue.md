# [BUG,CSHARP] Regression with collections and nullable types

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/22066
- Opened by seniorquico on 2025-10-03, closed on 2025-10-18
- Labels: Issue: Bug
- Fix commit: 23a2aafe9171b9f2ff97a320bef08161ba755dfe

## Report

##### Description

I am generating a set of ASP.NET Core controller stubs and models. I upgraded to v7.16.0 from v7.15.0, and the newly generated code fails to compile with invalid nullable reference type declarations:

```cs
public Collection?<string> Items { get; set; }
//               ^
//               error CS1519: Invalid token '<' in a member declaration
```

The question mark is placed in between the type name and the generic type argument. It needs to be placed after the generic type argument.

##### openapi-generator version

The problem occurs in v7.16.0. Reverting to v7.15.0, the problem does not occur.

##### OpenAPI declaration file content or url

I can't share this OpenAPI specification file, but the JSON schema that produces the error is pretty straightforward:

```yaml
type: object
properties:
  items:
    type: array
    items:
      type: string
```

##### Generation Details

```yaml
additionalProperties:
  aspnetCoreVersion: "8.0"
  buildTarget: library
  licenseUrl: https://example.com/license
  newtonsoftVersion: "8.0.20"
  nullableReferenceTypes: true
  operationResultTask: true
  packageAuthors: me
  packageCopyright: 2025 Me
  packageDescription: An API server
  packageGuid: "{3D10FC07-0C87-4C7E-B168-D9729EE1C918}"
  packageName: ApiServer
  packageTitle: API Server
  packageVersion: "0.0.0"
  returnICollection: false
  schemaMappings:
    ProblemDetails: Microsoft.AspNetCore.Mvc.ProblemDetails
  useCollection: true
  useDateTimeOffset: true
  useNewtonsoft: true
  useSwashbuckle: false
  userSecretsGuid: 3d10fc07-0c87-4c7e-b168-d9729ee1c918
generatorName: aspnetcore
```

##### Related issues/PRs

I suspect the issue was introduced with #21600. I see a test was changed to actually expect this type declaration?

https://github.com/OpenAPITools/openapi-generator/blob/1c082c7287960681f592142ce0d487a1cd4ec9a8/modules/openapi-generator/src/test/java/org/openapitools/codegen/csharpnetcore/CSharpModelTest.java#L401

I don't see any recent changes to the model template, and the model template inserts the question mark after the type name. The template doesn't appear to have any knowledge of generic type arguments.

https://github.com/OpenAPITools/openapi-generator/blob/1c082c7287960681f592142ce0d487a1cd4ec9a8/modules/openapi-generator/src/main/resources/aspnetcore/3.0/model.mustache#L84

I think the question mark is being placed in between the type name and the generic type argument in the Java code?

## Comment by wing328 on 2025-10-03

thanks for reporting the issue

cc @Mattias-Sehlstedt (the author of #21600)

## Comment by Mattias-Sehlstedt on 2025-10-03

Hello, thanks for the report and sorry for the inconvenience. I will start looking into fixing that behavior.

## Comment by Mattias-Sehlstedt on 2025-10-03

@seniorquico I have created a suggested fix. 

Since my previous commit implemented support for deep aliases, could you look at these new [method signature types](https://github.com/OpenAPITools/openapi-generator/pull/22071/files#diff-311c1de1202adc0dd0769d45ccf005ee709fdb68a3c124ebb24d0797ef2b9c9aR43) and verify that they look good as well?

## Comment by seniorquico on 2025-10-09

> Since my previous commit implemented support for deep aliases, could you look at these new [method signature types](https://github.com/OpenAPITools/openapi-generator/pull/22071/files#diff-311c1de1202adc0dd0769d45ccf005ee709fdb68a3c124ebb24d0797ef2b9c9aR43) and verify that they look good as well?

@Mattias-Sehlstedt The types on the line look correct (assuming I understand the use cases 😅). I'm not sure if you're looking for more test cases, but these would be other possible combinations:

```
Option<Dictionary<string, string?>?>
                                ^
Option<List<List<string?>>?>
                       ^
Option<List<List<string>?>?>
                        ^
```

## Comment by Mattias-Sehlstedt on 2025-10-10

Hi, thanks for the examples. That then suggests that some further corrections could be made to my solution, since I assume your examples would be produced from the different tiers/depths of arrays being marked as nullable (for examples as in this [new test case](https://github.com/OpenAPITools/openapi-generator/pull/22071/files#diff-e63411f2d98a07a1a625809b7bc0106dfea4fcdc1cee8866d1169b06d32f3185R379)).

Given that this was never supported to begin with before 7.15 (since deep aliases failed completely), I believe it is not "breaking". But I will look into fixing those when I find time. Please feel free to branch from me and if anyone wants to get this fixed faster.
