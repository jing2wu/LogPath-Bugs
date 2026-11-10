# [BUG] [OpenAPI 3.1] siblings of `$ref` are lost

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/20304
- Opened by Felk on 2024-12-12, closed on 2025-11-19
- Labels: Issue: Bug
- Fix commit: 554e10dc345e5142ef222fc3da5d74d6cb167cd0

## Report

#### Bug Report Checklist

- [X] Have you provided a full/minimal spec to reproduce the issue? -> see https://github.com/OpenAPITools/openapi-generator/pull/20303
- [X] ~~Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?~~ The correctness of the snippets I'm trying to parse were discussed in https://github.com/swagger-api/swagger-parser/issues/2036
- [X] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [X] Have you searched for related issues/PRs?
- [X] What's the actual output vs expected output? -> see the test
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

Starting with OpenAPI 3.1, it is allowed for $ref-objects to have sibling properties and those sibling properties should not be lost. A simple example would be:

```yaml
components:
  schemas:
    ModelWithTitledProperties:
      properties:
        refProperty:
          type: string
          title: Ref-Property-Title
          $ref: '#/components/schemas/RefObject'
      type: object
    RefObject:
      type: string
```

Expected: when generating code, I have access to `refProperty`'s `title` field.
Reality: The value of `title` (and other fields, such as `description`) are lost.

For example, if I try to generate TypeScript code that includes a model's title using a custom template (but the issue is not TypeScript-specific):
```mustache
export const {{classname}}Meta = {
{{#vars}}
    {{name}}: {
        title: `{{{title}}}`,
        description: `{{{description}}}`
    },
{{/vars}}
} as const;
```

this works for regular properties, but `title` and `description` are always empty for properties that include a `$ref`.

##### openapi-generator version

7.10.0 (actually latest master, d29196a1f0ad41fc17f5d4875650f87480d66a40).
As far as I understand, this is not a regression, but just a yet undetected bug for OpenAPI 3.1 schemas.

##### Steps to reproduce

I opened a complimentary pull request that adds a test case showcasing the problem: https://github.com/OpenAPITools/openapi-generator/pull/20303

##### Suggest a fix

Best lead I found while debugging was that `ModelUtils#unaliasSchema` seems to just 100% forward the $ref'ed schema if it detects a ref that doesn't fall into one of the special cases like `isObjectSchema(...)`.

## Comment by FrankShaw on 2025-03-19

For reference, the only sibling fields allowed for [ReferenceObjects](https://spec.openapis.org/oas/v3.1.1.html#reference-object) in OAS 3.1.X are `summary` and `description`. If your spec has these fields, it is a bug that they are ignored. But, in your example, `type` and `title` are not valid fields for a ReferenceObject so they should be ignored by the parser.

## Comment by Felk on 2025-06-04

@FrankShaw are you sure about that restriction? I thought the same initially too, but got some more context here: https://github.com/swagger-api/swagger-parser/issues/2036#issuecomment-2523701571 (see the linked comment and the comment after that one)

## Comment by FrankShaw on 2025-06-05

@Felk you are right. The restriction I mentioned is enforced in every other area of an OpenAPI 3.1 specification, but in the `schemas` section that follows the SchemaObject model which is based on the JSON Schema Draft 2020-12 which does not have any restrictions on sibling fields for objects using a `$ref`

## Comment by wing328 on 2025-11-17

update: I've filed https://github.com/OpenAPITools/openapi-generator/pull/22364 to fix the issue. if when you've time, please kindly do a test.
