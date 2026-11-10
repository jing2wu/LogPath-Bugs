# [BUG,typescript] Missing import statements in model with circular oneOf

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/23286
- Opened by minusinus on 2026-03-19, closed on 2026-10-14
- Labels: Issue: Bug
- Fix commit: e17e024b2bcb9565bbe59586e8ad1cdd2780909f

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. E.g.:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

When using a circular oneOf schema, the typescript generator does not generate the import statements anymore. 

##### openapi-generator version

This is a regression that I noticed after upgrading from 6.5 to 7.20.

##### OpenAPI declaration file content or url

```yaml
openapi: 3.0.3
info:
  title: Repro
  version: 1.0.0
paths: {}
components:
  schemas:
    Repro:
      type: object
      properties:
        content:
          oneOf:
            - type: string
            - type: array
              items:
                $ref: '#/components/schemas/Repro'
```

##### Generation Details

```
java -jar openapi-generator-cli.jar generate -i /tmp/repro.yaml -g typescript -o /tmp/out
```

##### Steps to reproduce

1. Generate the provided schema using the options above.
2. Verify that Repro and ReproContent models are created
3. Observe that ReproContent is missing the import statement to Repro

##### Related issues/PRs

<!-- has a similar issue/PR been reported/opened before? Please do a search in https://github.com/openapitools/openapi-generator/issues?utf8=%E2%9C%93&q=is%3Aissue%20 -->
I've found several somewhat similar issues (on other typescript generators, though). This one may be relevant:
https://github.com/openapitools/openapi-generator/issues/21441

Search used: https://github.com/openapitools/openapi-generator/issues?q=is%3Aissue%20typescript%20import%20oneOf%20sort%3Acreated-desc

##### Suggest a fix

I can't submit a PR myself right now, but I've tried to run an LLM over the issue so please take the following with a grain of salt:

When generating union types for schemas using `oneOf`, the `TypeScriptClientCodegen.java` attempts to filter out unused imports and only keep imports related to the schemas specified within the `oneOf` definition. It is however performing an exact match between the import name (e.g. `Repro`) and the string representation of the `oneOf` elements (e.g. `Array<Repro>`). 

When modifying the code to instead perform a substring match, it seems to resolve the problem **for me** (though I have NOT verified potential side-effects):

```diff
diff --git a/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/TypeScriptClientCodegen.java b/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/TypeScriptClientCodegen.java
index 085461f446e..0981ba5f5d5 100644
--- a/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/TypeScriptClientCodegen.java
+++ b/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/TypeScriptClientCodegen.java
@@ -394,8 +394,11 @@ public class TypeScriptClientCodegen extends AbstractTypeScriptClientCodegen imp
                 // For oneOfs only import $refs within the oneOf
                 TreeSet<String> oneOfRefs = new TreeSet<>();
                 for (String im : cm.imports) {
-                    if (cm.oneOf.contains(im)) {
-                        oneOfRefs.add(im);
+                    for (String oneOf : cm.oneOf) {
+                        if (oneOf.contains(im)) {
+                            oneOfRefs.add(im);
+                            break;
+                        }
                     }
                 }
                 cm.imports = oneOfRefs;
```
