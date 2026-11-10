# [BUG,java] OAS 3.1 "type: string" schema with plain-string oneOf branches no longer collapses to String, generates useless wrapper model (regression since 7.21.0)

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/24574
- Opened by phusu on 2026-08-03, closed on 2026-08-13
- Labels: Issue: Bug
- Fix commit: 66f697325c1273ce1aa26813afd286a984acdb49

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue? Yes, see below
- [x] Have you validated the input using an OpenAPI validator?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?  Yes — reproduced on master @ commit  0ef5eb07  (2026-08-03)
- [x] Have you searched for related issues/PRs? (found the causing PR, no existing duplicate report)
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

For an OpenAPI 3.1 schema where a property (or array `items`) declares `type: string` and a sibling `oneOf` whose branches are themselves all plain `type: string` schemas differentiated only by `pattern` / `description` (no `const`, no discriminator, not modeling an enum) — the generator used to collapse this to a plain `String` type. Since 7.21.0 it instead generates an empty, useless wrapper model class for the `oneOf`, and uses that model type as the property/parameter type instead of `String`.

This breaks compiling client code that calls the generated API with normal `String` / `List<String>`  values, since the parameter type is now an unrelated composed-schema class with no way to construct it from a `String`.

Example generated (broken) parameter:
```java
public List<String> listWidgets(List<ListWidgetsIdsParameterInner> ids) throws RestClientException {
```

`ListWidgetsIdsParameterInner` is an entirely empty class (no fields, no constructors accepting a value) — there is no way to obtain an instance of it from application code.


##### openapi-generator version

Confirmed present in 7.21.0 through 7.24.0 (latest release). Last known-good version: 7.20.0.

##### OpenAPI declaration file content or url
```yaml
openapi: 3.1.0
info:
  title: OneOf Regression Sample
  version: 1.0.0
paths:
  /widgets:
    get:
      operationId: listWidgets
      parameters:
        - name: ids
          in: query
          required: true
          explode: false
          schema:
            type: array
            items:
              type: string
              oneOf:
                - type: string
                  description: Numeric identifier
                  pattern: '^\d+$'
                - type: string
                  description: UUID identifier
                  pattern: '^[0-9a-f-]{36}$'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  type: string
```

##### Generation Details

```
java -jar openapi-generator-cli-7.24.0.jar generate \
  -i spec.yaml -g java --library resttemplate \
  --skip-validate-spec -o out
```

Reproduces with the default `java` generator (`resttemplate` library); likely affects all generators since the defect is in the shared `OpenAPINormalizer`, not generator-specific code.

##### Steps to reproduce

1. Save the spec above as `spec.yaml`.
2. Run the generation command above with openapi-generator 7.20.0 → `listWidgets(List<String> ids)` (correct).
3. Run the same command with 7.21.0+ → `listWidgets(List<ListWidgetsIdsParameterInner> ids`)  where `ListWidgetsIdsParameterInner` is an empty class (incorrect regression).

##### Related issues/PRs

The regression was introduced by commit [905b9301](https://github.com/OpenAPITools/openapi-generator/commit/905b9301) / PR #22573 ("fix #22571 (OpenAPINormalizer): Removed reset of OAS content"), first released in 7.21.0. In `OpenAPINormalizer.processSimplifyOneOf`:

```java
if (ModelUtils.isIntegerSchema(schema) || ModelUtils.isNumberSchema(schema) || ModelUtils.isStringSchema(schema)) {
    if (schema.getSpecVersion().equals(SpecVersion.V30)) {
        schema.setOneOf(null);
    } //else {
        // TODO convert oneOf const/deprecated to enum
    // }
}
```

PR #22573 intentionally stopped clearing `oneOf` for OAS 3.1 schemas so that `const`-based enum branches (and their per-branch `deprecated` metadata) aren't discarded — that part is legitimate. However, the fix is unconditional on spec version and doesn't check whether the `oneOf` branches actually represent an enum (via `const`)/discriminator. As a side effect, it also now preserves non-enum, plain-string `oneOf` unions (e.g., alternative regex patterns for the same string type), which previously collapsed correctly to `String` under 7.20.0.

##### Suggest a fix

In `processSimplifyOneOf`, only skip resetting `oneOf` for OAS 3.1 when the branches actually encode enum/const semantics (e.g., each branch has `const` or is otherwise used for a discriminator), instead of skipping for all OAS 3.1 string/number/integer schemas.

## Comment by wing328 on 2026-08-03

thanks for reporting the issue

can you please file a PR with the suggested fix when you've time?

cc @JPPortier (author of #22573)
