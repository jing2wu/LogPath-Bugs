# [Bug]: The OAS 3.1 is missing information from the @ArraysSchema.arraySchema

- Issue: https://github.com/swagger-api/swagger-core/issues/5012
- Opened by martin-rais-brcm on 2025-11-04, closed on 2026-02-13
- Labels: Bug
- Fix commit: 75b8a35a59646517ea3e94613a39d47b81a9851e

## Report

The OAS 3.1 is missing information from the @ArraysSchema.arraySchema

## Description of the problem/issue
We are using the springdoc with the swagger-core dependency. Once we switched from the OpenApi 3.0 to 3.1 some @Schema information defined in the @ArraySchema.arraySchema do not generate into the OpenApi JSON spec. So far, we've found that following properties are not generated:

 - readOnly
 - accessMode
 - examples

There might be more of them.

## Affected Version

2.2.40

Earliest version the bug appears in (if known): we found it in 2.2.36.

## Steps to Reproduce

Use this POJO model with a collection property, while generating OAS 3.1:

``` java
@Getter
@Setter
public final class MyModel {

  @ArraySchema(
      arraySchema = @Schema(
          deprecated = true,
          accessMode = AccessMode.READ_ONLY,
          description = "collection description",
          examples = "John"),
      schema = @Schema(
          description = "item description",
          examples = "Jason"))
  private List<String> names;
}
```

## Expected Behavior

The OAS 3.1 should contain this definition:

```json
"org.example.MyModel": {
  "type": "object",
  "properties": {
    "names": {
      "type": "array",
      "description": "collection description",
      "deprecated" : true,
      "readOnly" : true,
      "examples" : [
        "John"
      ],
      "items": {
        "type": "string",
        "description": "item description",
        "examples": [
          "Jason"
        ]
      }
    }
  }
}
```

## Actual Behavior

Some fields from the `arraySchema` are missing in the generated model.
See that `description` attribute is present, while `deprecated`, `examples` and `readOnly`
are missing.

```json
"org.example.MyModel": {
  "type": "object",
  "properties": {
    "names": {
      "type": "array",
      "description": "collection description",
      "items": {
        "type": "string",
        "description": "item description",
        "examples": [
          "Jason"
        ]
      }
    }
  }
}
```

## Logs / Stack Traces

N/A.

## Additional Context

Switching springdoc back to version 3.0, and replacing `examples` with `example` in the POJO, the missing fields are present in the generated model.

## Checklist

- [x] I have searched the [existing issues](https://github.com/swagger-api/swagger-core/issues) and this is not a duplicate.
- [x] I have provided sufficient information for maintainers to reproduce the issue.

## Comment by Mattias-Sehlstedt on 2026-02-01

The incorrect behavior stem from the fact that the annotations are initially dropped in the model construction since the specification target is 3.1. (and it thus allows for siblings), and that the arraySchema is calculated at a later point [here](https://github.com/swagger-api/swagger-core/blob/master/modules/swagger-core/src/main/java/io/swagger/v3/core/util/AnnotationsUtils.java#L557-L563) where it does not take into consideration all possible `properties` (so hence why `deprecated` and `accessMode` are not properly present).

One solution is to simply add so that metadata is forwarded properly in this location, but I believe that the annotations being dropped too early (and re-added later) is a bit counterintuitive and something that might be suitable for a reconstruction.

## Comment by ewaostrowska on 2026-02-13

Hi! The [fix](fix: add missing @ArraysSchema.arraySchema properties #5049)https://github.com/swagger-api/swagger-core/pull/5049 for this issue has been just merged and will be part of the next release. Thank you for your contribution :)
