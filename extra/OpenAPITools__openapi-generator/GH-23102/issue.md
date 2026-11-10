# [BUG] [Python] OpenAPI code generator ignores pattern constraint on array items

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/23102
- Opened by claudiadpp on 2026-03-03, closed on 2026-05-14
- Labels: Issue: Bug
- Fix commit: 397645c2cf5065e566898650b899ffcef5d8fee6

## Report

#### Bug Report Checklist

- [ ] Have you provided a full/minimal spec to reproduce the issue?
- [ ] Have you validated the input using an OpenAPI validator?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. E.g.:  [BUG,JAVA] Bug generating foo with bar 
-->

#### Description

The Python OpenAPI code generator does not generate `field_validator` methods for pattern constraints defined at the items level of array properties. It only generates pattern validators for top-level string properties.

When an OpenAPI spec defined an array property like this: 
```yml
tags:
  type: array
  maxItems: 50
  items:
    type: string
    maxLength: 128
    pattern: "^[A-Z0-9_\\- ]+$"
```

The generator correctly applies `maxLength` on each item via `Annotated[str, Field(strict=True, max_length=128)]` and `maxItems` on the array via `Field(max_length=50)`, but silently ignores the pattern constraint on the items.


##### Generated output (current, incorrect)
```python
tags: Optional[Annotated[List[Annotated[str, Field(strict=True, max_length=128)]], Field(max_length=50)]] = Field(default=None)
```

No `field_validator` is generated for the pattern on the items. There is no validation whatsoever that each string in the array matches `^[A-Z0-9_\\- ]+$`.


#### Expected output (correct)
The generator should produce a `field_validator` (or equivalent Annotated constraint) that validates each item in the array against the pattern regex. For example:

```python
tags: Optional[Annotated[List[Annotated[str, Field(strict=True, max_length=128)]], Field(max_length=50)]] = Field(default=None)

@field_validator('tags')
@classmethod
def tags_validate_items_pattern(cls, value):
    """Validates the regular expression on each item"""
    if value is None:
        return value
    pattern = r"^[A-Z0-9_\- ]+$"
    for i, item in enumerate(value):
        if not re.match(pattern, item):
            raise ValueError(
                f"Item at index {i} ('{item}') must validate the regular expression {pattern}"
            )
    return value
```

#### Contrast with top-level `pattern` (works correctly)
For a non-array string property with `pattern`, the generator does produce a validator. For example, `name` with `pattern: "^.*$"` correctly generates:

```python
@field_validator('name')
def name_validate_regular_expression(cls, value):
    """Validates the regular expression"""
    if not re.match(r"^.*$", value):
        raise ValueError(r"must validate the regular expression /^.*$/")
    return value
```

This confirms the generator has the capability to produce pattern validators, but the logic is only triggered for top-level string properties, not for items within arrays.

#### Defining it with $ref
I also tried modifying API and include this as a $ref 
```yml
Tags:
  type: string
  maxLength: 128
  pattern: "^[A-Z0-9_\\- ]+$"

....

tags:
  type: array
  maxItems: 50
  items:
    $ref: "#/components/schemas/Tags"
```

but this still does not generate a `field_validator` for the regex pattern.

#### openapi-generator version

openapi-generator version 7.19.0
generator: python-fastapi (pydantic v2)

## Comment by evelynegroen on 2026-03-19

Can confirm the same behaviour for 7.20
