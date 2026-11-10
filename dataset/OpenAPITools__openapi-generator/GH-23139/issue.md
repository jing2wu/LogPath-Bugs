# [BUG,Java,feign-hc5] templateResourcePath / templateDir is overwritten by feign-hc5 library in processOpts()

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/23139
- Opened by BartPraats on 2026-03-05, closed on 2026-03-16
- Labels: Issue: Bug
- Fix commit: 1d3ef5ca89aa9f462fe27c20cee8c6dbcbb9f70e

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [x] Have you tested with the latest master to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?

##### Description

When using the `java` generator with `library=feign-hc5`, any user-provided `templateResourcePath` (or `templateDir` / `-t`) is silently ignored. The same configuration works correctly when using `library=feign`.

The root cause is in `JavaClientCodegen.processOpts()`, where the `feign-hc5` branch unconditionally overwrites the template directory:

```java
} else if (isLibrary(FEIGN_HC5)) {
    additionalProperties.put("feign-hc5", "true");
    setTemplateDir(FEIGN);   // Overwrites any user-provided templateDir/templateResourcePath
    setLibrary(FEIGN);
}
```

https://github.com/OpenAPITools/openapi-generator/blob/e6304a8db2930fd3dd54a22dd220ac3bfc69e03f/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/JavaClientCodegen.java#L842-L844

The `setTemplateDir(FEIGN)` call runs **after** the user's `templateResourcePath`/`templateDir` has already been set on the configurator, so it unconditionally replaces the user's custom template path with `"feign"`. This means any custom templates the user provides are never picked up.

With `library=feign`, the `if (isLibrary(FEIGN))` branch only sets `additionalProperties.put("feign-okhttp", "true")` and does **not** call `setTemplateDir()`, so the user's custom template path is preserved.

##### openapi-generator version

Latest master (commit `e6304a8db2930fd3dd54a22dd220ac3bfc69e03f`). The issue has existed since `feign-hc5` was introduced.

##### OpenAPI declaration file content or url

Any valid OpenAPI spec will reproduce this. For example, the petstore spec:

```yaml
openapi: "3.0.0"
info:
  title: Sample API
  version: "1.0.0"
paths:
  /pets:
    get:
      operationId: listPets
      summary: List all pets
      responses:
        '200':
          description: A list of pets
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Pet'
components:
  schemas:
    Pet:
      type: object
      properties:
        id:
          type: integer
          format: int64
        name:
          type: string
```

##### Generation Details

**Maven plugin example (reproduces the bug):**

```xml
<plugin>
    <groupId>org.openapitools</groupId>
    <artifactId>openapi-generator-maven-plugin</artifactId>
    <configuration>
        <inputSpec>${project.basedir}/src/main/resources/api.yaml</inputSpec>
        <generatorName>java</generatorName>
        <library>feign-hc5</library>
        <templateResourcePath>my-custom-templates/Java</templateResourcePath>
    </configuration>
</plugin>
```

**CLI equivalent:**

```bash
openapi-generator-cli generate \
  -g java \
  --library feign-hc5 \
  -t my-custom-templates/Java \
  -i api.yaml \
  -o output
```

##### Steps to reproduce

1. Create a custom template directory (e.g. `my-custom-templates/Java/libraries/feign/`) with a modified template file (e.g. a customized `api.mustache`).
2. Configure the generator with `generatorName=java`, `library=feign-hc5`, and `templateResourcePath` (or `-t`) pointing to `my-custom-templates/Java`.
3. Run the generator.
4. **Observe:** The custom templates are ignored; the built-in embedded templates are used instead.
5. Change the library to `feign` (keeping everything else the same).
6. Run the generator again.
7. **Observe:** The custom templates are now correctly picked up and used.

**Actual output:** With `feign-hc5`, the generator uses the built-in embedded templates, ignoring the user-provided `templateResourcePath`/`templateDir`.

**Expected output:** With `feign-hc5`, the generator should respect the user-provided `templateResourcePath`/`templateDir` and use custom templates, just as it does with the `feign` library.

##### Related issues/PRs

No directly related issues found.

##### Suggest a fix

The fix should be in [`JavaClientCodegen.java` at line 842-844](https://github.com/OpenAPITools/openapi-generator/blob/e6304a8db2930fd3dd54a22dd220ac3bfc69e03f/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/JavaClientCodegen.java#L842-L844).

The `feign-hc5` branch should **not** call `setTemplateDir(FEIGN)` unconditionally. Instead, it should only set the template directory if the user has not already provided a custom one. For example:

```java
} else if (isLibrary(FEIGN_HC5)) {
    additionalProperties.put("feign-hc5", "true");
    // Only override templateDir if no custom template directory was provided by the user
    if (!isUserProvidedTemplateDir()) {
        setTemplateDir(FEIGN);
    }
    setLibrary(FEIGN);
}
```

Alternatively, the `feign-hc5` library could be restructured to avoid calling `setTemplateDir()` entirely — for instance, by creating a `libraries/feign-hc5/` resource directory (even if it just symlinks or delegates to the `feign` templates), so the standard library template resolution mechanism works without needing to override the template directory at the code level.

## Comment by wing328 on 2026-03-05

can you please file a PR with the suggested fix when you've time? 🙏

## Comment by BartPraats on 2026-03-09

Sure, but can you (or someone) tell me what the preferred solution is? Add the if (!isUserProvidedTemplateDir()) condition or add the feign-hc5 resource dir?
