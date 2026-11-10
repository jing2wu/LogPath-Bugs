# [BUG,Bounty,typescript-axios] Doesn't generate an union with null when type is an array (works in Stoplight)

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/19890
- Opened by darkbasic on 2024-10-16, closed on 2026-07-31
- Labels: Issue: Bug
- Fix commit: df2d81bb672fd5de03731ce25d6f34c7a53fc571

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [ ] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))? **That domain has expired.**
- [ ] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. Eg:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

We use [scramble](https://github.com/dedoc/scramble/issues/70#issuecomment-2356592623) to generate the OpenAPI 3.1 JSON schema and I want a certain field to be an union with `null`.

When scramble generates the following:
```json
"requirements": {
  "type": [
    "array",
    "null"
  ],
  "items": {
    "type": "string"
  }
}
```

It doesn't translate into a typescript type which is an union with `null`:
```ts
export interface MappingItemResourceSettings {
    /**
     *
     * @type {{ [key: string]: string; }}
     * @memberof MappingItemResourceSettings
     */
    'validation'?: { [key: string]: string; };
    /**
     *
     * @type {Array<string>}
     * @memberof MappingItemResourceSettings
     */
    'requirements'?: Array<string>;
}
```

The expected output should be:
```ts
export interface MappingItemResourceSettings {
    /**
     *
     * @type {{ [key: string]: string; }}
     * @memberof MappingItemResourceSettings
     */
    'validation'?: { [key: string]: string; } | null;
    /**
     *
     * @type {Array<string>}
     * @memberof MappingItemResourceSettings
     */
    'requirements'?: Array<string> | null;
}
```

##### openapi-generator version

7.9.0 (AFAIK it's not a regression)

##### OpenAPI declaration file content or url

```json
{
    "openapi": "3.1.0",
    "info": {
        "title": "API Portal Demo",
        "version": "1.0.0",
        "description": "This is the **mapping API** description"
    },
    "components": {
        "schemas": {
            "MappingItemResource": {
                "type": "object",
                "properties": {
                    "settings": {
                        "type": [
                            "object",
                            "null"
                        ],
                        "description": "Additional settings for mapping item validation. (JSON)",
                        "properties": {
                            "validation": {
                                "type": [
                                    "object",
                                    "null"
                                ],
                                "additionalProperties": {
                                    "type": "string"
                                }
                            },
                            "requirements": {
                                "type": [
                                    "array",
                                    "null"
                                ],
                                "items": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                },
                "required": [
                    "settings"
                ],
                "title": "MappingItemResource"
            },
        },
    }
}
```

##### Generation Details

`openapi-generator-cli generate -i file.json -g typescript-axios -o src/api/mapping --additional-properties=withInterfaces=true,useSquareBracketsInArrayNames=true"`

##### Steps to reproduce

`openapi-generator-cli generate -i file.json -g typescript-axios -o src/api/mapping --additional-properties=withInterfaces=true,useSquareBracketsInArrayNames=true"`

##### Related issues/PRs

https://github.com/dedoc/scramble/issues/70#issuecomment-2356592623

The author of Scramble thinks this is a valid OpenAPI format and the issue is in the openapi-generator typescript plugin. This affermation is backed by the fact that Stoplight correctly displays `null` in the union:

![image](https://github.com/user-attachments/assets/13f3c4bc-d229-4a1a-9e5f-5c419822fce8)

##### Suggest a fix

<!-- if you can't fix the bug yourself, perhaps you can point to what might be
  causing the problem (line of code or commit), or simply make a suggestion -->

## Comment by GeorgeFkd on 2024-10-26

This is indeed a problem, what i noticed is that in the template in file: `resources/typescript-axios/api.mustache` that the isNullable property is not used at all, this is likely a template bug.

Also consider reading [this stackoverflow post](https://stackoverflow.com/questions/48111459/how-to-define-a-property-that-can-be-string-or-null-in-openapi-swagger), as there were some related changes from 3.0.x to 3.1.X in this matter.

Typescript-fetch generator seems to actually do it properly so if it applies to your case you could generate it with fetch and then convert it to axios, if it is that critical and urgent.

## Comment by darkbasic on 2024-10-26

@GeorgeFkd thanks for your answer. I've already ended up migrating the whole app(s) to openapi-typescript and openapi-fetch. For a while I've considered fixing it myself but the risk of having no one reviewing and merging my PR was too high and past experience pointed me against it: https://github.com/OpenAPITools/openapi-generator/pull/19293

From what I can see it looks like openapi-generator is basically dead and migrating the whole app(s) to openapi-typescript was worth the effort.

## Comment by WeberG619 on 2026-03-01

Hey,

I'd like to take this on. Looking at the typescript-axios generator's handling of OpenAPI 3.1's type arrays with null, the issue is that the generator isn't properly recognizing `type: ["array", "null"]` as a nullable union type.

**My approach:**
I'll fix this in the TypeScript model template by updating how it processes schema types when they're arrays containing "null". The generator should detect when `type` is an array containing both a base type and "null", then generate the appropriate union type (`Array<string> | null` instead of just `Array<string>`).

**Relevant background:**
- Active open-source contributor with TypeScript and OpenAPI tooling experience
- Familiar with mustache templating and the openapi-generator's TypeScript code paths
- I write clean, tested code that follows existing project conventions

**What you can expect:**
- A well-tested PR targeting the typescript-axios generator specifically
- Test cases covering the OpenAPI 3.1 nullable array pattern
- No breaking changes to existing behavior
- Updates to the typescript-axios docs if needed

I can have a draft PR up within 2-3 days. Have you already tried any workarounds with preprocessors, or would you prefer this fixed directly in the generator?

Weber Gouin

## Comment by darkbasic on 2026-03-01

@WeberG619 thanks but in the meantime I've moved off of openapi-generator. I've migrated to openapi-typescript which is built with a language I am familiar with and in turn I've contributed several patches myself.
