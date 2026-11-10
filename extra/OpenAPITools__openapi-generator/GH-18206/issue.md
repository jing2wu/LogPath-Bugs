# [BUG,Kotlin,kotlin-spring] Multi-level inheritance doesn't work

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/18206
- Opened by taviLaies on 2024-03-22, closed on 2026-09-27
- Labels: Issue: Bug
- Fix commit: d7dd6d04ccfd1c2ed45db6ac2ba415674895abb0

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. Eg:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

When using multi-level inheritance, the `kotlin-spring` generator produces non-compiling code.

```
> Task :compileKotlin FAILED
e: .../src/main/kotlin/org/openapitools/model/BigDog.kt: (21, 1): Function 'component1' generated for the data class conflicts with member of supertype 'Dog'
e: .../src/main/kotlin/org/openapitools/model/BigDog.kt: (21, 1): Function 'component2' generated for the data class conflicts with member of supertype 'Dog'
e: .../src/main/kotlin/org/openapitools/model/BigDog.kt: (21, 1): Function 'component3' generated for the data class conflicts with member of supertype 'Dog'
e: .../src/main/kotlin/org/openapitools/model/BigDog.kt: (31, 32): 'breed' in 'Dog' is final and cannot be overridden
e: .../src/main/kotlin/org/openapitools/model/BigDog.kt: (32, 5): This type is final, so it cannot be inherited from
e: .../src/main/kotlin/org/openapitools/model/BigDog.kt: (32, 5): This type has a constructor, and thus must be initialized here
```

It's especially unfortunate because Java does support this. We must use mechanisms that work across Java & Kotlin and therefore we have to go with the least common denominator preventing us from using multi-level polymorphism.
##### openapi-generator version

<!-- which version of openapi-generator are you using, is it a regression? -->
```bash
% openapi-generator --version
openapi-generator-cli 7.0.1
  commit : 5b720de
  built  : -999999999-01-01T00:00:00+18:00
  source : https://github.com/openapitools/openapi-generator
  docs   : https://openapi-generator.tech/
```

##### OpenAPI declaration file content or url

```yaml
openapi: 3.0.0
info:
  title: Sample API
  description: API description in Markdown.
  version: 1.0.0
paths:
  /animals:
    get:
      summary: Returns all animals.
      description: Optional extended description in Markdown.
      responses:
        200:
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Animal'
components:
  schemas:
    Dog:
      allOf:
        - $ref: '#/components/schemas/Animal'
        - type: object
          properties:
            breed:
              type: string
    Cat:
      allOf:
        - $ref: '#/components/schemas/Animal'
        - type: object
          properties:
            breed:
              type: string
    BigDog:
      allOf:
        - $ref: '#/components/schemas/Dog'
        - type: object
          required:
            - dogType
          properties:
            dogType:
              type: string
            declawed:
              type: boolean
    Animal:
      type: object
      discriminator:
        propertyName: className
      required:
        - className
      properties:
        className:
          type: string
        color:
          type: string
          default: red
```

##### Generation Details

<!-- 
    Prefer CLI steps, including the language, libraries and various options. 
    Providing config-based settings allows for simpler testing across CLI and plugins. 
    For examples, see https://github.com/OpenAPITools/openapi-generator/tree/master/bin/configs
-->
```bash
openapi-generator generate -g kotlin-spring -i spec.yaml --additional-properties documentationProvider=none --additional-properties useSpringBoot3=true
```

##### Steps to reproduce

1. run generation command above
2. run gradle build

##### Related issues/PRs

Similar issue has been submitted for Java a long time ago: https://github.com/OpenAPITools/openapi-generator/issues/3058.

##### Suggest a fix

Unfortunately Kotlin doesn't support data class inheritance. 

So the options I can think of:
- generate an interface hierarchy and use data classes for the "leaf" DTOs: e.g. interfaces: `IAnimal`, `IDog : IAnimal`, data classes: `Cat : IAnimal`, `Dog: IDog`, `BigDog: IDog` not very pretty but most times you work with the DTOs.
- move away from data classes - use regular classes, however this would prevent usage of data class capabilities (e.g. `copy`) which I personally find very useful

## Comment by DennisHartrampf on 2024-12-04

Is someone looking into this? It would be really good to have this capability. Without inheritance in the generated schema classes/DTOs we must write a lot of redundant code that I'd love to get rid off!
@wing328 could you maybe take a look at this? (Tagging you, because I found you as a core team member who contributed to kotlin-spring generator)

## Comment by wing328 on 2024-12-04

maybe related can you please try enabling the normalizer rule `REF_AS_PARENT_IN_ALLOF`?

ref: https://github.com/openapitools/openapi-generator/blob/master/docs/customization.md#openapi-normalizer

## Comment by DennisHartrampf on 2024-12-04

Thanks for the ultra fast reply!
I tried your suggestion and the generator then indeed tried to create classes with inheritance. Unfortunately with a lot of compile errors.

Here is for example a "super class" that is generated, which compiles, but is still a data class:

```kotlin
data class AbstractVertragDto(


    @get:JsonProperty("vertragId", required = true) val vertragId: kotlin.String = "VertragId",


    @get:JsonProperty("regelwerkId", required = true) val regelwerkId: kotlin.String,

    @field:Valid

    @get:JsonProperty("beginndatum", required = true) val beginndatum: DatumDto
    ) : Serializable{

    companion object {
        private const val serialVersionUID: kotlin.Long = 1
    }
}
```

And here is another data class that extends the super class. This has multiple compile errors. The `override val` properties can't override, because they are final in the parent. The "extends"-part (colon) yields "This type has a constructor, and thus must be initialized here" and "This type is final, so it cannot be inherited from".

```kotlin
data class VertragMitZieldatumDto(

    @field:Valid

    @get:JsonProperty("zieldatum", required = true) val zieldatum: DatumDto,


    @get:JsonProperty("vertragId", required = true) override val vertragId: kotlin.String = "VertragId",


    @get:JsonProperty("regelwerkId", required = true) override val regelwerkId: kotlin.String,

    @field:Valid

    @get:JsonProperty("beginndatum", required = true) override val beginndatum: DatumDto
    ) : AbstractVertragDto, Serializable{

    companion object {
        private const val serialVersionUID: kotlin.Long = 1
    }
}
```

So using `REF_AS_PARENT_IN_ALLOF` doesn't work here. I think the best option would be the second @taviLaies proposed:

> So the options I can think of:
> 
> * move away from data classes - use regular classes, however this would prevent usage of data class capabilities (e.g. `copy`) which I personally find very useful

As you shouldn't do any (business) logic with DTOs (because their only purpose is to transfer data as the name suggests) and use proper domain objects for that, I think the limitation of not being able to use the generated `copy` function of data classes is one that we can easily cope with.

## Comment by taviLaies on 2024-12-04

I just wanted to chime in here. The copy feature is very useful in tests for one. Hopefully we can keep some form of it. 
Ultimately what’s needed is a way to create a copy of the object and optionally change some fields at the same time (or being able to modify the state after creation).
Since code gen is used, maybe it’d be possible to still keep that functionality in some form even if it’s not a data class.

## Comment by DennisHartrampf on 2024-12-17

> Since code gen is used, maybe it’d be possible to still keep that functionality in some form even if it’s not a data class.

I think that should be possible. In the end Kotlin is also using code gen to create all these handy functions of a data class for us (copy, equals, hashCode, ...). Maybe the openapi-generator could "just" copy the logic of Kotlin generating these functions. (Of course not realy copy&paste because Kotlin generates these functions on the bytecode level and the openapi-generator would need to generate them on the source-code level.)

I still would be fine without the additional data class functionality in DTOs. And maybe/probably it is easier to implement it without data class functionality in a first iteration.

## Comment by tempacc21 on 2025-07-02

Would love to have this supported!

## Comment by ffffionn on 2025-07-03

Just ran into this issue trying to use this normalizer feature - I think supporting the inheritance properly for data classes is better (and likely easier?) than rewriting to plain classes. It seems all we need is to have `open` on all model fields, and then pass the relevant fields into the constructor of the base class. 
Though I'm not sure if there's any negative implications of having `open` set on fields. 

EDIT: Nevermind, I just tried implementing a fix for this and ran into the what the OP is getting at. Inheritance for data classes is not supported, and then we would lose `.copy()` functionality (which is a must I think..)

## Comment by ffffionn on 2025-07-04

So, the requirements to support this are to use a separate mustache template when the extension "x-parent" is true, which is a regular class instead of a data class.
This class template then needs to have open vars - to support inheritance; and implement toString(), equals(), hashCode(), and copy() - to mimic Data Class functionality. 

Inheriting classes then need to pass in the fields to the base class with constructor invocation. Other than the custom implementations of data class methods, I think this is mostly fine, though I would prefer to keep a single class template rather than duplicate most of what is in `dataClass.mustache`.  

I may try create a PR for this when I have some time.

## Comment by rvlasveld on 2026-06-05

[Claude] Hi @ffffionn — your July 3–4 comments describe exactly the approach we've taken in PR #23954. Quick summary of what's implemented:

- Single template (`dataClass.mustache`) with conditional blocks gated on `x-is-open-class` — no duplicate template
- `open` keyword on the mid-level model's own properties
- Explicit `equals()` (exact-class check so `Dog(…) != BigDog(…)` always), `hashCode()`, `toString()`, and `copy()`
- `copy()` returns `Dog`; `data class BigDog` generates its own `copy()` returning `BigDog` — different arities, no JVM conflict
- Leaf models (`BigDog`, `Cat`) remain `data class` and are fully unaffected
- Inheriting classes pass parent fields via named constructor arguments

The one piece still missing is `componentN()` for destructuring, which would require language-level support to generate correctly.

PR is open for review if you'd like to take a look: https://github.com/OpenAPITools/openapi-generator/pull/23954
