# [Bug]: RequiredMode.NOT_REQUIRED is not respected by properties annotated with @NotBlank and @NotEmpty

- Issue: https://github.com/swagger-api/swagger-core/issues/4967
- Opened by AnderData on 2025-09-09, closed on 2025-11-17
- Labels: Bug
- Fix commit: 23d2971e6f9d2b765615efd874185f1501532f57

## Report

## Description of the problem/issue

Using `RequiredMode.NOT_REQUIRED` does not correctly override the inferred requirement of fields annotationed with `@NotBlank` or `@NotEmpty`.

For example, these two fields are currently incorrectly marked as required in the generated OpenAPI file:

```java
public class Sample {
  @Schema(requiredMode = RequiredMode.NOT_REQUIRED)
  @NotBlank String exampleString;

  @Schema(requiredMode = RequiredMode.NOT_REQUIRED)
  @NotEmpty List<String> exampleList;
}
```

Before https://github.com/swagger-api/swagger-core/issues/4862 these fields were correctly being overridden to be not required.

I was able to confirm the before/after behavior by adding those two fields to the file:
`swagger-core/src/test/java/io/swagger/v3/core/oas/models/RequiredFields.java`
and the associated unit test `testRequiredProperty()` in:
`modules/swagger-core/src/test/java/io/swagger/v3/core/converting/override/ModelPropertyOverrideTest.java`

## Affected Version

Started in 2.2.30
Introduced by #4862 

## Steps to Reproduce

Can be completely reproduced by updating the `swagger-core/src/test/java/io/swagger/v3/core/oas/models/RequiredFields.java` and add two additional fields as described above in the `Sample` class.

## Expected Behavior

Fields annotated by `@NotBlank` or `@NotEmpty` should be not required in the openapi doc if also annotated by `@Schema(requiredMode = RequiredMode.NOT_REQUIRED)`.

## Actual Behavior

Fields annotated by `@NotBlank` or `@NotEmpty` are always required in the openapi regardless of `@Schema` annotation configuration.

## Checklist

- [X] I have searched the [existing issues](https://github.com/swagger-api/swagger-core/issues) and this is not a duplicate.
- [X] I have provided sufficient information for maintainers to reproduce the issue.
