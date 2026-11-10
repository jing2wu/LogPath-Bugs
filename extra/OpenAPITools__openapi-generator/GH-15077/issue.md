# [BUG,TypeScript - axios] Redundant models - the same type is generated multiple times

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/15077
- Opened by MartinNovak1991 on 2023-03-30, closed on 2024-06-19
- Labels: Issue: Bug
- Fix commit: 5bc7aa3cd603abff2e320e7a5cefa9abfa5ea936

## Report

#### Bug Report Checklist

- [*] Have you provided a full/minimal spec to reproduce the issue?
- [*] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [ ] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [*] Have you searched for related issues/PRs?
- [*] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. Eg:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

OpenApi description generated just one model file in 5.4.0. In 6+ (tested with 6.0.0 and 6.4.0) every property (of the same schema) is generating one file per property, and all these files are pointing to the one (same) model/type.

##### openapi-generator version

5.4.0 ok, but generating with 6.0.0 and 6.4.0 causes issue described above.

##### OpenAPI declaration file content or url

There is sample of problematic part (in schemas)
```yaml
    PaginationOffsetType:
      type: object
      properties:
        offset:
          type: integer
          minimum: 0
      required:
        - offset
    OffsetsObjectType:
      type: object
      properties:
        _offsets:
          type: object
          properties:
            self:
              allOf:
                - description: |
                    desc 1
                - $ref: '#/components/schemas/PaginationOffsetType'
            first:
              allOf:
                - description: |
                    desc 2
                - $ref: '#/components/schemas/PaginationOffsetType'
            previous:
              allOf:
                - description: >
                    desc 3
                - $ref: '#/components/schemas/PaginationOffsetType'
            next:
              allOf:
                - description: >
                   desc 4
                - $ref: '#/components/schemas/PaginationOffsetType'
          required:
            - first
            - self
      required:
        - _offsets
```


##### Generation Details

"npx openapi-generator-cli generate --generator-key ${yaml-filename}"
I tried "--openapi-normalizer REF_AS_PARENT_IN_ALLOF=true"   but no effect

##### Steps to reproduce

simply run generate  sample above ... it will create (useless?) four  (suffixed) models:
![image](https://user-images.githubusercontent.com/71878667/228747748-15222e37-730f-4897-9ed5-fc70d5e3ba58.png)

You can see  propertyName suffix ... with contents:

offsets-object-type-offsets.ts:

```
export interface OffsetsObjectTypeOffsets {  
       'self': OffsetsObjectTypeOffsetsSelf;  
       'first': OffsetsObjectTypeOffsetsFirst;  
       'previous'?: OffsetsObjectTypeOffsetsPrevious;   
       'next'?: OffsetsObjectTypeOffsetsNext;
}
```

offsets-object-type-offsets-first.ts:
```
export type OffsetsObjectTypeOffsetsFirst = PaginationOffsetType;
```

offsets-object-type-offsets-next..ts:
```
export type OffsetsObjectTypeOffsetsNext = PaginationOffsetType;
```

offsets-object-type-offsets-previous.ts:
```
export type OffsetsObjectTypeOffsetsPrevious= PaginationOffsetType;
```

offsets-object-type-offsets-self.ts:
```
export type OffsetsObjectTypeOffsetsSelf= PaginationOffsetType;
```

pagination-offset-type.ts:  
```
export interface PaginationOffsetType {
    'offset': number;
}
```

**v5.4.0 was generating:**
![image](https://user-images.githubusercontent.com/71878667/228750286-06c9c559-11e6-43d3-837f-1f32389d59c7.png)

offsets-object-type.ts:
```
export interface OffsetsObjectType {  
   '_offsets': OffsetsObjectTypeOffsets;
}
```

offsets-object-type-offsets.ts:  
```
export interface OffsetsObjectTypeOffsets {  
      'self': PaginationOffsetType ;  
      'first': PaginationOffsetType ;  
      'previous'?: PaginationOffsetType ;  
      'next'?: PaginationOffsetType ;
}
```

pagination-offset-type.ts:  

```
export interface PaginationOffsetType {
    'offset': number;
}
```

I would exepect the same result, optimized, not reduntant files/types (with "equal" content)


##### Related issues/PRs

I have not found any related issue

##### Suggest a fix

No idea

## Comment by ReneZeidler on 2023-04-19

I'm having the same problem, and it seems to be caused by having a description in combination with allOf.
My declaration looks like this:

```json
"NumberRange": {
  "type": "object",
  "properties": {
    "min": { "type": "number", "description": "Minimum value of the range" },
    "max": { "type": "number", "description": "Maximum value of the range" },
    "step": { "type": "number", "description": "Step size for valid values" }
  },
  "required": ["min", "max"]
},
"MyModel": {
  "type": "object",
  "properties": {
    "range1": {
      "description": "This range describes...",
      "readOnly": true,
      "allOf": [{ "$ref": "#/components/schemas/NumberRange" }]
    },
    "range2": {
      "readOnly": true,
      "allOf": [{ "$ref": "#/components/schemas/NumberRange" }]
    }
  },
  "required": ["range1", "range2"]
}
```

---

Using OpenAPI Generator **6.5.0** with `REF_AS_PARENT_IN_ALLOF=true` already enabled, I get this output (using the `typescript-angular` generator):

```ts
export interface MyModel {
    readonly range1: MyModelRange1;
    readonly range2: NumberRange;
}

/**
 * This range describes...
 */
export interface MyModelRange1 extends NumberRange { 
}
```
It creates a new model for each property with a description, which in reality are many more than just one. The new models extend the base model (because of `REF_AS_PARENT_IN_ALLOF`), but this is still suboptimal. Without `REF_AS_PARENT_IN_ALLOF`, the new models would be copies of the base model.
The property description is retained in some form, but as the description of the new model instead of the property on the main model. Therefore it won't be shown by IDEs when autocompleting the property name.

Of course I can remove the description, which gets rid of the additional models:
```ts
export interface MyModel {
    readonly range1: NumberRange;
    readonly range2: NumberRange;
}
```
However, especially in a case like this, where the model of the property is something general (like `NumberRange` here), having a description would be really helpful.

---

The output I really want is this, which is what OpenAPI Generator **5.4.0** generated:
```ts
export interface MyModel {
    /**
     * This range describes...
     */
    readonly range1: NumberRange;
    readonly range2: NumberRange;
}
```

---

This issue is realted to #12838, where special case handling of `allOf` in combination with `nullable` and `readOnly` has already been added, however `description` was missed.

The temporary workaround was supposed to be replaced by a Normalizer ruleset, but as far as I can tell none of the currently available rulesets solve this issue.

## Comment by MartinNovak1991 on 2023-06-19

Any update?

I tried v6.6.0 ... same result > It generates  4 same type (OffsetsObjectTypeOffsets**SUFFIX**.ts files). I noticed this in console:

> [srcFile] [main] WARN  o.o.codegen.InlineModelResolver - allOf schema "null" containing multiple types (not model) is not supported at the moment.

> [srcFile] [main] INFO  o.o.codegen.InlineModelResolver - Inline schema created as OffsetsObjectType__offsets_self. To have complete control of the model name, set the "title" field or use the inlineSchemaNameMapping option (--inline-schema-name-mappings in CLI).

> [srcFile] [main] WARN  o.o.codegen.InlineModelResolver - allOf schema "null" containing multiple types (not model) is not supported at the moment.

> [srcFile] [main] INFO  o.o.codegen.InlineModelResolver - Inline schema created as OffsetsObjectType__offsets_first. To have complete control of the model name, set the "title" field or use the inlineSchemaNameMapping option (--inline-schema-name-mappings in CLI).

> [srcFile] [main] WARN  o.o.codegen.InlineModelResolver - allOf schema "null" containing multiple types (not model) is not supported at the moment.

> [srcFile] [main] INFO  o.o.codegen.InlineModelResolver - Inline schema created as OffsetsObjectType__offsets_previous. To have complete control of the model name, set the "title" field or use the inlineSchemaNameMapping option (--inline-schema-name-mappings in CLI).

> [srcFile] [main] WARN  o.o.codegen.InlineModelResolver - allOf schema "null" containing multiple types (not model) is not supported at the moment.

> [srcFile] [main] INFO  o.o.codegen.InlineModelResolver - Inline schema created as OffsetsObjectType__offsets_next. To have complete control of the model name, set the "title" field or use the inlineSchemaNameMapping option (--inline-schema-name-mappings in CLI).

> [srcFile] [main] INFO  o.o.codegen.InlineModelResolver - Inline schema created as OffsetsObjectType__offsets. To have complete control of the model name, set the "title" field or use the inlineSchemaNameMapping option (--inline-schema-name-mappings in CLI).

I mean this:  WARN  o.o.codegen.InlineModelResolver - allOf schema "null" containing multiple types (not model) is not supported at the moment.

What to do?

This is part of YAMLfile:

>    OffsetsObjectType:
      type: object
      properties:
        _offsets:
          description: >
            desc
          type: object
          properties:
            self:
              allOf:
                - description: |
                    desc
                - $ref: '#/components/schemas/PaginationOffsetType'
            first:
              allOf:
                - description: |
                    desc
                - $ref: '#/components/schemas/PaginationOffsetType'
            previous:
              allOf:
                - description: >
                    desc
                - $ref: '#/components/schemas/PaginationOffsetType'
            next:
              allOf:
                - description: >
                    des
                - $ref: '#/components/schemas/PaginationOffsetType'
          required:
            - first
            - self
      required:
        - _offsets



What is wrong? What command can it do correctly without redundancy? Im lost with this :/


ok ... there is problematic location:
this:
![image](https://github.com/OpenAPITools/openapi-generator/assets/71878667/e55f7c9f-1004-48cc-8d1a-f57ebd68705f)
generates this:
![image](https://github.com/OpenAPITools/openapi-generator/assets/71878667/d7e5ed14-6b37-4a80-ae5c-2325fd6d0ca4)


and this:
![image](https://github.com/OpenAPITools/openapi-generator/assets/71878667/62327365-0895-4f38-ad69-33373f543200)
generates these redundant types:
![image](https://github.com/OpenAPITools/openapi-generator/assets/71878667/0132c5bd-4392-4bad-8934-4d05fda70597)

## Comment by ReneZeidler on 2024-06-17

This was partially fixed by #16096, however the issue still persists if `readOnly` and/or `nullable` are used together with any other property (like `description`).
