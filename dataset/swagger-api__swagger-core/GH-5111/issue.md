# [Bug]: A Java raw Object is always resolved to OAS 3.1 object

- Issue: https://github.com/swagger-api/swagger-core/issues/5111
- Opened by Mattias-Sehlstedt on 2026-04-04, closed on 2026-04-14
- Labels: Bug
- Fix commit: a25200409e5ffca7ddf662e81ceb47690d8f8db3

## Report

## Description of the problem/issue

<!--
Provide a clear and concise description of the problem.
To help us understand the issue better, consider including:
- What are you trying to achieve using swagger-core?
- Are specific annotations not behaving as expected? (e.g., @Schema, @Parameter, @Operation)
- Are generated OpenAPI specs missing information or incorrect?
- Are you using swagger-core with JAX-RS, Spring, or another framework?
- Did this issue affect code generation (e.g., Swagger Codegen/OpenAPI Generator)?
-->

With PR https://github.com/swagger-api/swagger-core/pull/5034 the default behavior of how a Java `Object` for OAS 3.1 is resolved was changed from being an empty type definition to always being type `object`. This can cause incorrect schema generation, since `Object` is not necessary a JSON-object (e.g., "string" is a valid Java `Object`, but not a valid JSON-object).

The interpretation of a Java `Object` should instead be tied to `explicit-object-schema`, which was introduced and described in https://github.com/swagger-api/swagger-core/pull/4868. It also correctly states that this behavior should be an explicit opt-in (and also highlights that the current behavior of 3.0 is incorrect, but that it is kept/not corrected due to backwards compatibility concerns).

## Affected Version

<!-- What version of swagger-core are you using? -->
2.2.45

<!-- Can you identify when the issue was introduced?
If yes, please provide the earliest version you know the bug exists in. -->
Earliest version the bug appears in (if known):  
2.2.44

## Steps to Reproduce

<!-- Provide a step-by-step list on how to reproduce the issue.
Include any relevant OpenAPI definitions, configuration, or code snippets. -->

Have a class that have a property with type `Object`. E.g. 
```java
private static class PojoUsingObjectField {
  private Object myField;

  public Object getMyField() {
    return myField;
  }

  public void setMyField(Object myField) {
    this.myField = myField;
  }
}
```

## Expected Behavior

<!-- What should have happened? -->
A Java Object should be resolved to an empty type.

## Actual Behavior

<!-- What actually happened instead? -->
A Java Object is resolved to type `object`.

## Logs / Stack Traces

<!-- Paste relevant log output or error messages, if any. -->

## Additional Context

<!-- Add any other context, links, or screenshots about the problem here. -->

## Checklist

- [x] I have searched the [existing issues](https://github.com/swagger-api/swagger-core/issues) and this is not a duplicate.
- [x] I have provided sufficient information for maintainers to reproduce the issue.
