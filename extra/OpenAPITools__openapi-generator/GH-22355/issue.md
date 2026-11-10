# [BUG] [SWIFT] Array items cannot be nullable

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/22355
- Opened by dan-magnusson-lowes on 2025-11-14, closed on 2026-08-26
- Labels: Issue: Bug
- Fix commit: cd242fd161b9e13cd0c3f99f5ab606b4ae88dcc2

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

In the Swift 6 codegen array item types cannot be nullable.

##### openapi-generator version

Latest: 7.17.0
Not a regression

##### OpenAPI declaration file content or url

```yaml
        ArrayWithNullableItemsModel:
          required:
            - foo
          properties:
            foo:
              type: array
              items:
                type: string
                nullable: true
```

##### Generation Details

Expected:
```swift
public struct ArrayWithNullableItemsModel: Sendable, Codable, ParameterConvertible, Hashable {

    public var foo: [String?]

    public init(foo: [String?]) {
        self.foo = foo
    }
    ...
}
```

Actual:
```swift
public struct ArrayWithNullableItemsModel: Sendable, Codable, ParameterConvertible, Hashable {

    public var foo: [String]

    public init(foo: [String]) {
        self.foo = foo
    }
    ...
}
```

##### Steps to reproduce

See above.

##### Related issues/PRs

https://github.com/OpenAPITools/openapi-generator/issues/19070 - Kotlin bug report
https://github.com/OpenAPITools/openapi-generator/pull/19080 - Kotlin PR
https://github.com/OpenAPITools/openapi-generator/pull/19157 - TypeScript PR

##### Suggest a fix

On line 742:
https://github.com/OpenAPITools/openapi-generator/blob/fd72d4d521b78eef101b532a8a7fcc90302315e3/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/Swift6ClientCodegen.java#L742

Account for nullable item schemas in the way the Kotlin generator does since [PR 19080](https://github.com/OpenAPITools/openapi-generator/pull/19080), with a `getItemsTypeDeclaration(Schema items)` function.

## Comment by 4brunu on 2025-11-20

Hi, could you please open a pull request and I can help with the review? Thanks

## Comment by HarelM on 2026-08-24

@4brunu is the offer still on the table for a quick review and release?
We encountered this issue here: 
- https://github.com/Rallista/valhalla-openapi-models-swift/pull/15

I'll be happy to contribute a fix.
