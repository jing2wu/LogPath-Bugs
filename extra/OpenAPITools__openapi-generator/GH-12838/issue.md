# [BUG] [Engine] InlineModelResolver creates weird named duplicate inline models and there is no way to turn it off

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/12838
- Opened by c0dezli on 2022-07-11, closed on 2022-12-22
- Labels: Issue: Bug, code line count reduction
- Fix commit: 71a7a822f41ded491d823bafaf0cefb4744b6b71

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. Eg:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

InlineModelResolver introduced a critical regression bug for nullable objects in OpenAPI schema

##### openapi-generator version

6.0.1

##### OpenAPI declaration file content or URL

https://github.com/OpenAPITools/openapi-generator/pull/12237

modules/openapi-generator/src/main/java/org/openapitools/codegen/InlineModelResolver.java


##### Generation Details


Let's say we have an object defined in my OpenAPI 3.0.3 schema
```
    LoginPasswordlessResponse:
      type: object
      properties:
        user:
          allOf:
          - $ref: '#/components/schemas/BaseUser'
          nullable: true
        token:
          type: string
          nullable: true
```

Before this PR, the OpenAPI generator will link `LoginPasswordlessResponse.user` to `BaseUser` without creating a redundant inline model.

But now it will create a new model called `LoginPasswordlessResponse_user`

```
[main] INFO  o.o.codegen.InlineModelResolver - Inline schema created as LoginPasswordlessResponse_user. To have complete control of the model name, set the `title` field or use the inlineSchemaNameMapping option (--inline-schema-name-mapping in CLI).
```

And I cannot overwrite it with `--inline-schema-name-mappings` option because if I overwrite `LoginPasswordlessResponse_user` with `BaseUser `the whole openapi generator will just break due to duplicate model names.

(and by the way you missed the ending "s" in the log output, which is very misleading. I spend hours on figuring out why --inline-schema-name-mapping is an invalid option, turns out it should be --inline-schema-name-mappings)

##### Steps to reproduce

Shown above

##### Related issues/PRs

https://github.com/OpenAPITools/openapi-generator/pull/12237

##### Suggest a fix

<!-- if you can't fix the bug yourself, perhaps you can point to what might be
  causing the problem (line of code or commit), or simply make a suggestion -->

## Comment by christophercotton on 2022-08-01

Same issue here, this is causing our models to be incorrect now.

## Comment by christophercotton on 2022-08-01

We definitely want the previous behavior where it would auto link: `LoginPasswordlessResponse.user` to `BaseUser`.

## Comment by spacether on 2022-08-03

Related: https://github.com/OpenAPITools/openapi-generator/pull/13056

## Comment by ReneZeidler on 2022-09-22

It seems like this bug was actually caused by #12348, which always turns allOf-schemas into inline models.

This caused another regression in combination with `readonly` (#13303), which has been fixed in 6.1.0.

This bug is another instance of the same regression, where a combination with `nullable` should not create a new model. `nullable` is also a change to the parent, not the referenced model itself.

## Comment by ReneZeidler on 2022-09-22

Quick addition:
This also affects other properties in combination with `allOf` that don't affect the model and only apply to the property itself on the parent, e.g. `description`. For example, using this schema:
```json
"MyClass": {
    "type": "object",
    "properties": {
        "subclass": {
            "description": "This is a description",
            "allOf": [{ "$ref": "#/components/schemas/MySubclass" }]
        },
    },
    "required": ["subclass"]
}
```
The description should apply to the property on the parent and and generate a comment in the parent model:
```ts
export interface MyClass { 
    /**
     * This is a description
     */
    subclass: MySubclass;
}
```
This worked fine in v5.x.
Starting with v6, instead I get this:
```ts
export interface MyClass { 
    subclass: MyClassMySubclass;
}
```
The description gets swallowed into a new inline model `MyClassMySubclass` which is an exact copy of `MySubclass`, and no comment is generated.

I think the change in #12348 needs to be reevaluated on when exactly an `allOf`-schemas get converted into a new inline model.

## Comment by wing328 on 2022-09-22

I'll try to squeeze some time to take a look at this issue in Oct. I already have some solutions in mind.

Can you guys please share the minimal spec to reproduce the issue? Thanks.

## Comment by ReneZeidler on 2022-09-22

Here is a minimal spec, including the relevant typescript-angular output from version 5.4 and version 6.1:
https://gist.github.com/ReneZeidler/bc29d342ea95e2d0da839e11960c5a71

An additional note I found while researching this, is that the allOf-nullable-pattern does not actually mean what most people think it means, according to a clarifaction in the OpenAPI spec (see also https://github.com/OAI/OpenAPI-Specification/issues/1368). A schema that is non-nullable cannot be made nullable using `allOf` and `nullable: true`.
However, this is how people recommend doing it in many sources online, and how many tools generate specs from code. In my case, I'm using `@nestjs/swagger`, which outputs this allOf-nullable-pattern.

<details>
Neither v5.4 nor v6.1 follow spec here, since the `nullableSubclass` property should _not_ be nullable according to spec. I don't think current behavior here should be changed, since this would probably break even more things. There is no alternative nice way to describe nullable properties in the OpenAPI 3.0 spec.

OpenAPI 3.1 will get rid of `nullable` altogether and instead use `type: 'null'`, so the correct pattern for a nullable property would be:
```yaml
oneOf:
  - type: 'null'
  - $ref: '#/components/schemas/MySubclass'
```
However, OpenAPI 3.1 is not widely supported yet.
</details>

The second case using `allOf` together with `description` is similar. Technically, this creates a new schema which overrides the description field, and thus it is different and extracted as an inline schema. The previous behavior was that the `description` field of an inline schema was used to annotate the _property_ of the parent schema, and not to annotate the inline schema itself (whose contents are just an exact copy of the referenced schema).

---

I think the fix to this is that the usage of `allOf` should only count as a new inline model if it has at least two items*. Using `allOf` with just one item (which is a reference to an existing model) is just using that same model. Other properties alongside `allOf`, like `readonly`, `nullable` and `description` only serve to annotate the usage of that reference model in the parent.

*Edit: Or, like in the [original bug](https://github.com/OpenAPITools/openapi-generator/issues/8892) that was fixed, `allOf` in combination with `required`, since setting the required flag of individual properties of the inherited model necessarily requires a separate copy of that model.

## Comment by c0dezli on 2022-10-25

@wing328 
When can we have an update/fix on this? 
We have been blocked from using OpenAPI generator 6.x.x and we desperately need some bug fixes that come with it. However, this bug makes 6.x.x unusable for us

## Comment by mrginglymus on 2022-10-28

Ah, this looks like we can probably apply the same fix for readonly as nullable. I'll raise a new PR.

## Comment by rob-spoor on 2023-07-26

https://github.com/OpenAPITools/openapi-generator/pull/16096 improves this even further, where it also doesn't generate new classes for a combination of description + a single ref `allOf`.
