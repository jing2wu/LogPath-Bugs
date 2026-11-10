# [BUG] [JAVA] [SPRING] missing import for schemaMapping in api

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/24232
- Opened by jpfinne on 2026-07-07, closed on 2026-08-24
- Labels: Issue: Bug
- Fix commit: 61c6a9ae1e76b6900f7ca65e0b147d252f9ef851

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))


##### Description

schemaMapping + importMapping does not generate the import in the generated apis class.  

It works only for Models.
typeMapping + importMapping correctly generated the parameters and the imports.

Example:

##### openapi-generator version

7.23.0

##### OpenAPI declaration file content or url


```yaml
openapi: 3.0.0
info:
  version: "1.0.0"
  title: mapping
paths:
  /some/dummy/endpoint/{id}:
    get:
      operationId: getDummy
      parameters:
        - name: id
          in: path
          required: true
          description: My Custom Id
          schema:
            $ref: '#/components/schemas/MyId'
        - name: key
          in: query
          required: true
          description: filter on key
          schema:
            $ref: '#/components/schemas/MyKey'

      responses:
        200:
          description: Successfully created reverse listings for retail
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Dummy'
components:
  schemas:
    Dummy:
      type: object
      properties:
        id:
          $ref: '#/components/schemas/MyId'
        key:
          $ref: '#/components/schemas/MyKey'
    MyId:
      type: string
      format: custom
    MyKey:
      type: string
```

##### Generation Details

java -jar modules/openapi-generator-cli/target/openapi-generator-cli.jar generate -g spring -i mapping.yaml -o /tmp/spring/ --type-mappings string+custom=MyCustomId --schema-mappings MyKey=MyCustomKey --import-mappings MyCustomId=org.myord.MyCustomId --import-mappings MyCustomKey=org.myorg.MyCustomKey

##### Steps to reproduce

The generated SomeApoi.java has the correct method:
```
ResponseEntity<Dummy> getDummy(MyCustomId id,     MyCustomKey key)
```
and the correct import for MyId
`import org.myord.MyCustomId;`

But no import for MyKey (or MyCustomKey)

The models contain the correct imports.  Dummy.java contains
```
import org.myord.MyCustomId;
import org.myorg.MyCustomKey;
```

##### Related issues/PRs

<!-- has a similar issue/PR been reported/opened before? Please do a search in https://github.com/openapitools/openapi-generator/issues?utf8=%E2%9C%93&q=is%3Aissue%20 -->

##### Suggest a fix

Workaround: use fully qualified name in schema-mappings
```
--schema-mappings MyKey=org.myorg.MyCustomKey 
```

## Comment by Chrimle on 2026-07-07

Isn't the issue setting the `import-mappings` property twice in the CLI, and it only applies the first?

What if you try 
```
java -jar modules/openapi-generator-cli/target/openapi-generator-cli.jar generate
-g spring
-i mapping.yaml
-o /tmp/spring/
--type-mappings string+custom=MyCustomId 
--schema-mappings MyKey=MyCustomKey 
--import-mappings MyCustomId=org.myord.MyCustomId,MyCustomKey=org.myorg.MyCustomKey
```

## Comment by jpfinne on 2026-07-07

@Chrimle The syntax is correct.   The cli supports multiple mappings or comma separated values.
It works for the models.  See generated Dummy.java

Type mapped with type-mappings are "complexType".
It is handle here: https://github.com/OpenAPITools/openapi-generator/blob/77bdb0ba1e126984838e6ab7423ed9bbe58a1776/modules/openapi-generator/src/main/java/org/openapitools/codegen/DefaultCodegen.java#L5541

schema-mappings are handled differently for models.  For apis, the implementation is missing.

Jersey uses this workaround:
https://github.com/OpenAPITools/openapi-generator/blob/77bdb0ba1e126984838e6ab7423ed9bbe58a1776/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/AbstractJavaCodegen.java#L2241

I will create a PR to fix the issue both for java and spring

## Comment by Picazsoo on 2026-07-08

This issue most probably also exists in kotlin-spring.

## Comment by Picazsoo on 2026-07-08

Ok, based on my quick interaction with github copilot about the codebase directly from the github web interface, if you plan on fixing the issue directly in `DefaultCodegen` then the fix should supposedly apply universally. But you obviously have deeper understanding, having reported the issue and all.

I will paste the output of the interaction below 👇 . I hope you do not take it personally - I just find it useful to burn some of my monthly allotment of tokens on open source projects such as this one. Feel free to put me in my place (-:

## Fix Description

### Root Cause

In `DefaultCodegen.fromOperation()` (around line 4808), after all parameters have been processed, their types are added to `op.imports` via the local `imports` set:

```java
// add imports to operation import tag
for (String i : imports) {
    if (needToImport(i)) {
        op.imports.add(i);
    }
}
```

The local `imports` set is populated during `fromParameter()`. For a **`schemaMapping`-resolved** parameter (e.g. `--schema-mappings MyKey=MyCustomKey`), `fromParameter()` sets `codegenParameter.dataType = "MyCustomKey"` but **does not add `"MyCustomKey"` to `imports`** — because the schema is treated as a referenced/external type that bypasses the normal model import paths.

By contrast, a **`typeMapping`-resolved** parameter (e.g. `--type-mappings string+custom=MyCustomId`) goes through `getParameterDataType()` → `toModelName()` → the result gets added to `imports` via `codegenProperty.complexType` at line 4425:

```java
if (codegenProperty.complexType != null) {
    imports.add(codegenProperty.complexType);
}
```

For a `schemaMapping`, `codegenProperty.complexType` is `null` because the schema is an alias of a simple type (string), so this branch is skipped. The `dataType` is overridden later at line 4370:

```java
if (parameterModelName != null) {
    codegenParameter.dataType = parameterModelName;
    ...
}
```

...but by then the `imports` set is no longer updated.

### The Fix

In `DefaultCodegen.fromOperation()`, after building `op.imports` from the local `imports` set, add an additional pass over all parameters to check if their `dataType` has a corresponding entry in `importMapping`. If so, add the `dataType` token to `op.imports` so that `DefaultGenerator.getAllImportsMappings()` can resolve it to the correct FQN.

**File:** `modules/openapi-generator/src/main/java/org/openapitools/codegen/DefaultCodegen.java`

```diff
         // add imports to operation import tag
         for (String i : imports) {
             if (needToImport(i)) {
                 op.imports.add(i);
             }
         }

+        // Ensure imports are added for parameters whose type was resolved via schemaMapping.
+        // When --schema-mappings is used, the parameter dataType is set to the mapped type name
+        // (e.g. "MyCustomKey") but this token is never added to the local imports set, because
+        // the schema is treated as an alias of a simple type and codegenProperty.complexType is null.
+        // We need the token in op.imports so that DefaultGenerator.getAllImportsMappings() can
+        // look it up in importMapping and emit the correct fully-qualified import statement.
+        for (CodegenParameter p : allParams) {
+            if (p.dataType != null && importMapping.containsKey(p.dataType)
+                    && !op.imports.contains(p.dataType)) {
+                op.imports.add(p.dataType);
+            }
+        }
+
         op.bodyParam = bodyParam;
```

### Why no template changes are needed

Both `JavaSpring/api.mustache` and `kotlin-spring/api.mustache` already render:

```mustache
{{#imports}}import {{import}}
{{/imports}}
```

The import tokens in `op.imports` flow through `DefaultGenerator.processOperations()` → `getAllImportsMappings()`, which resolves each token via `importMapping` to its FQN. Once `"MyCustomKey"` is present in `op.imports`, `getAllImportsMappings()` finds `importMapping.get("MyCustomKey") = "org.myorg.MyCustomKey"` and the import is emitted correctly. No template changes are needed for any generator.

### Scope

This fix is in `DefaultCodegen` (the shared base class) and therefore fixes the issue for **all generators** that rely on `importMapping` for schema-mapped parameter types, including both `spring` and `kotlin-spring`.

## Comment by jpfinne on 2026-07-09

@Picazsoo  thanks for the use of your tokens.

It is a bit scary to touch DefaultCodeGen... but way better than my initial implementation.
I had a less generic solution in AbstractJavaCodeGen.postProcessOperationsWithModels() using OperationsMap.getImports() (ouch)


By the way if you still have token to spare, I'd like to know why we have `class Circle extends Shape implements Shape` (see #21801)
The handling of inheritance is ***very*** complex

## Comment by Mattias-Sehlstedt on 2026-07-13

I would assume that the `class Circle extends Shape implements Shape` comes from the fact that the generator by default creates an `extends` relation when it sees a single parent relation through an `allOf`. This relation is later changed due to `useOneOfInterfaces` being true, which will make it so that the parent is instead made into an interface (which replaces the standard class since there is a collision?), but this change in type does not properly clear `Shape` from being a parent class in `Circle`. And thus an incorrect type hierarchy.
