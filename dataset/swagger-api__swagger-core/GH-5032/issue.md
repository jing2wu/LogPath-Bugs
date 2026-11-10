# [Bug]: @NotEmpty and @NotBlank validation annotations ignored when combined with @Schema(requiredMode = ...)

- Issue: https://github.com/swagger-api/swagger-core/issues/5032
- Opened by burneyy on 2026-01-06, closed on 2026-01-08
- Labels: Bug
- Fix commit: 1dafa44cc59c44595f5de6f6648fbfa92924a1b9

## Report

## Description of the problem/issue

When a field is annotated with both a Bean Validation annotation (`@NotEmpty` or `@NotBlank`) and `@Schema(requiredMode = ...)`, the validation constraints are not reflected in the generated OpenAPI schema:

- `@NotEmpty` on collections should generate `minItems: 1`
- `@NotBlank` on strings should generate `minLength: 1`

This works correctly when:
- Only the validation annotation is present (no `@Schema`)
- `@Schema` is present but without `requiredMode` (e.g., only `description`)

This is broken when:
- `@Schema(requiredMode = REQUIRED)` is combined with the validation annotation
- `@Schema(requiredMode = NOT_REQUIRED)` is combined with the validation annotation

## Affected Version

- **Broken in:** 2.2.41 ❌ 
- **Works in:** 2.2.40 ✅ 

## Steps to Reproduce

```Java
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import java.util.Set;

public class ParentDto {
    // ❌ BUG: minItems is null (should be 1)
    @NotEmpty
    @Schema(requiredMode = Schema.RequiredMode.REQUIRED)
    public Set<String> requiredItems;

    // ✅ WORKS: minItems is 1
    @NotEmpty
    public Set<String> optionalItems;

    // ❌ BUG: minItems is null (should be 1)
    @NotEmpty
    @Schema(requiredMode = Schema.RequiredMode.NOT_REQUIRED)
    public Set<String> nonRequiredItems;

    // ✅ WORKS: minItems is 1
    @NotEmpty
    @Schema(description = "Items with description only")
    public Set<String> itemsWithDescription;

    // ❌ BUG: minLength is null (should be 1)
    @NotBlank
    @Schema(requiredMode = Schema.RequiredMode.REQUIRED)
    public String requiredString;

    // ✅ WORKS: minLength is 1
    @NotBlank
    public String optionalString;

    // ❌ BUG: minLength is null (should be 1)
    @NotBlank
    @Schema(requiredMode = Schema.RequiredMode.NOT_REQUIRED)
    public String nonRequiredString;

    // ✅ WORKS: minLength is 1
    @NotBlank
    @Schema(description = "String with description only")
    public String stringWithDescription;
}
```

## Expected Behavior

| Field | Annotations | Expected `minItems`/`minLength` |
|-------|-------------|--------------------------------|
| `requiredItems` | `@NotEmpty` + `@Schema(requiredMode=REQUIRED)` | `1` |
| `optionalItems` | `@NotEmpty` | `1` |
| `nonRequiredItems` | `@NotEmpty` + `@Schema(requiredMode=NOT_REQUIRED)` | `1` |
| `itemsWithDescription` | `@NotEmpty` + `@Schema(description=...)` | `1` |
| `requiredString` | `@NotBlank` + `@Schema(requiredMode=REQUIRED)` | `1` |
| `optionalString` | `@NotBlank` | `1` |
| `nonRequiredString` | `@NotBlank` + `@Schema(requiredMode=NOT_REQUIRED)` | `1` |
| `stringWithDescription` | `@NotBlank` + `@Schema(description=...)` | `1` |

## Actual Behavior

| Field | Annotations | Actual `minItems`/`minLength` | Status |
|-------|-------------|------------------------------|--------|
| `requiredItems` | `@NotEmpty` + `@Schema(requiredMode=REQUIRED)` | `null` | ❌ |
| `optionalItems` | `@NotEmpty` | `1` | ✅ |
| `nonRequiredItems` | `@NotEmpty` + `@Schema(requiredMode=NOT_REQUIRED)` | `null` | ❌ |
| `itemsWithDescription` | `@NotEmpty` + `@Schema(description=...)` | `1` | ✅ |
| `requiredString` | `@NotBlank` + `@Schema(requiredMode=REQUIRED)` | `null` | ❌ |
| `optionalString` | `@NotBlank` | `1` | ✅ |
| `nonRequiredString` | `@NotBlank` + `@Schema(requiredMode=NOT_REQUIRED)` | `null` | ❌ |
| `stringWithDescription` | `@NotBlank` + `@Schema(description=...)` | `1` | ✅ |

<!-- What actually happened instead? -->


## Additional Context

- Possibly introduced by https://github.com/swagger-api/swagger-core/pull/4968 ❓ 
- Suggested fix: https://github.com/swagger-api/swagger-core/pull/5033

## Checklist

- [x] I have searched the [existing issues](https://github.com/swagger-api/swagger-core/issues) and this is not a duplicate.
- [x] I have provided sufficient information for maintainers to reproduce the issue.

## Comment by Mattias-Sehlstedt on 2026-01-07

Thanks for identifying the issue and suggesting a fix. I am affected since this is used by [springdoc-openapi](https://github.com/springdoc/springdoc-openapi). If one wants to see how this affects specifications it is quite visible when springdoc did their [version bump](https://github.com/springdoc/springdoc-openapi/commit/615edaed41096ffa529361b7f0f1fef65290b9e3).

## Comment by daniel-kmiecik on 2026-01-08

@burneyy well-described bug. Good solution. Thanks for your contribution! The fix will be implemented in the next release.
