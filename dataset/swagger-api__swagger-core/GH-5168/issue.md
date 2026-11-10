# [Bug]: Boolean example values are still serialized as strings (regression follow-up to   #5061 / PR #5062)

- Issue: https://github.com/swagger-api/swagger-core/issues/5168
- Opened by jang-namu on 2026-04-30, closed on 2026-05-08
- Labels: Bug, backlog
- Fix commit: 5239cae1ada50e3c9b78f0e5b3a9c170ec4ec273

## Report

## Description of the problem/issue

  PR #5062 (released in `v2.2.47`) fixed the regression reported in #5061 for `number` /
  `integer` example values. However, the same regression still affects **boolean** schemas:
  `@Schema(examples = {"true"})` on a `Boolean` field continues to be serialized as the JSON
  string `"true"` instead of the JSON boolean `true`.

  Root cause is in the helper introduced by #5062,
  `AnnotationsUtils.shouldUseNodeAsExample(JsonNode, Schema)`:

  ```java
  private static boolean shouldUseNodeAsExample(JsonNode node, Schema schemaObject) {
      if (node.isObject() || node.isArray()) {
          return true;
      }
      if (schemaObject != null && SchemaTypeUtils.isNumberSchema(schemaObject)) {
          return true;
      }
      if (schemaObject != null && SchemaTypeUtils.isStringSchema(schemaObject)) {
          return false;
      }
      return node.isNumber();
  }
  ```

  For a boolean schema the method falls through to `return node.isNumber()`, which is `false` for
   a `BooleanNode`. As a result `parseExamplesArray` adds the trimmed string instead of the
  parsed `JsonNode`, and the generated OpenAPI document contains a string example for a boolean
  property.

  ## Affected Version

  `2.2.47` – `2.2.49` (latest as of writing). Also reproduces through `springdoc-openapi 2.8.17`.

  ## Steps to Reproduce

  ```java
  public class User {
      @Schema(description = "Email verified", examples = {"true"})
      private Boolean verified;
  }
  ```

  Generate the OAS document.

  ## Expected Behavior

  ```yaml
  public class User {
      @Schema(description = "Email verified", examples = {"true"})
      private Boolean verified;
  }                                                                                                ```

  Generate the OAS document.
  ## Expected Behavior

  ```yaml
  verified:
    type: boolean
    examples:
      - true
  ```

  ## Actual Behavior

  ```yaml                                                                                          verified:
    type: boolean
    examples:                                                                                        
      - "true"
  ```

  ## Suggested Fix
  Extend `shouldUseNodeAsExample` to also return `true` when the schema is a boolean schema (or
  when `node.isBoolean()`), e.g.:
  ```java
  if (schemaObject != null && SchemaTypeUtils.isBooleanSchema(schemaObject)) {
      return true;
  }
  // ...                                                                                           
  return node.isNumber() || node.isBoolean();
  ```

## Comment by swapneswarsundarray on 2026-05-03

Hi maintainers,


I’d like to work on this fix. 
- extend shouldUseNodeAsExample for boolean schemas
- add a regression test for @Schema(examples = {"true"})

Please let me know if anyone is already working on this.

## Comment by daniel-kmiecik on 2026-05-04

Hi @swapneswarsundarray!
Community contributions are always welcome.
If you have an idea for a fix or would like to give it a shot with a PR, feel free to jump in. Every contribution helps move the project forward and is greatly appreciated!

## Comment by daniel-kmiecik on 2026-05-08

@jang-namu thanks for raising this issue!
@Mattias-Sehlstedt has prepared a fix, which will be included in the next release.
We really appreciate everyone’s engagement and contributions. Thank you all!

## Comment by Mattias-Sehlstedt on 2026-05-08

All credit to @jang-namu for their thorough cause analysis and suggestion. The change was basically the suggestion verbatim 🚀
