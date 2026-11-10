# [BUG,MULTIPLE,OAS 3.1] Nullable map with additionalProperties type null breaks codegen (Null/ModelNull) with NORMALIZE_31SPEC (7.17+)

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/23945
- Opened by cassdeckard on 2026-06-04, closed on 2026-07-14
- Labels: Issue: Bug
- Fix commit: 82f86114ec786434d3d397d339d98ae67275ee5b

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an [OpenAPI validator](https://apidevtools.org/swagger-parser/online/)?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?

##### Description

With `--openapi-normalizer NORMALIZE_31SPEC=true`, nullable object maps whose **`additionalProperties`** value schema still contains JSON Schema **`null`** are not normalized to usable value types. Generators emit **`Null`** / **`ModelNull`** (or similar) instead of `object` / `List<...>`, which breaks compilation or codegen.

The minimal repro includes **two** value-schema shapes on nullable maps (`type: [object, null]`):

1. **`stringMap`** — `additionalProperties: { type: "null" }`
2. **`errorsByKey`** — `additionalProperties: { type: [array, "null"], items: { ... } }`

This is **not** the same as [#20213](https://github.com/OpenAPITools/openapi-generator/issues/20213), which covers `additionalProperties: false` on a closed object with nullable **properties** (`anyOf` + `null`). Here each failing field **is** the map, and the bug is in the **value** schema under `additionalProperties`.

**Actual vs expected (csharp, primary):**

| Property | Actual | Expected |
|----------|--------|----------|
| `stringMap` | `Dictionary<string, Null>` | `Dictionary<string, object>` (nullable if appropriate) |
| `errorsByKey` | `Dictionary<string, List<...>>` with invalid `Null` in the value type | `Dictionary<string, List<ErrorEntry>>` (nullable if appropriate) |
| **Build** | **CS0246** — `Null` type not found | Successful compile |

The [csharp generator docs](https://github.com/OpenAPITools/openapi-generator/blob/master/docs/generators/csharp.md) list **Null** as **unsupported** for OAS3.

**Multi-generator results (same minimal spec):**

| Generator | `map` output (summary) | Failure mode |
|-----------|------------------------|--------------|
| **csharp** | `stringMap` → `Dictionary<string, Null>`; `errorsByKey` often still involves invalid null handling | `dotnet build` → **CS0246** |
| **typescript-axios** | `{ [key: string]: Null }` | Invalid TS type (no `Null` definition) |
| **java** | `Map<String, ModelNull>` | Imports **`ModelNull`** but **no `ModelNull.java`** generated |
| **python** | — | **Codegen exception**: `Codegen Property not yet supported in getPydanticType` (`isNull=true`) |
| **rust** | `HashMap<String, models::Null>` | **`models::Null`** model not generated |
| **php** | `array<string,Null>` | References non-existent **`Null`** type |
| **go** | `map[string]nil` | **`nil` used as type name** (invalid / non-idiomatic) |

##### openapi-generator version

7.17.0 

##### OpenAPI declaration file content or url

```yaml
openapi: 3.1.1
info:
  title: Repro
  version: 1.0.0
paths:
  /x:
    get:
      responses:
        "200":
          content:
            application/json:
              schema:
                type: object
                properties:
                  stringMap:
                    type: [object, "null"]
                    additionalProperties:
                      type: "null"
                  errorsByKey:
                    type: [object, "null"]
                    additionalProperties:
                      type: [array, "null"]
                      items:
                        type: object
                        properties:
                          code:
                            type: string
                        additionalProperties: false
```

##### Generation Details

```bash
docker pull openapitools/openapi-generator-cli:latest
docker run --rm \
  -v "$(pwd)/oas31-nullable-map-additionalProperties-null.yaml:/spec.yaml:ro" \
  -v "$(pwd)/out-csharp-latest:/out" \
  openapitools/openapi-generator-cli:latest generate \
  -g csharp -i /spec.yaml -o /out \
  -p targetFramework=net8.0,library=httpclient \
  --skip-validate-spec \
  --openapi-normalizer NORMALIZE_31SPEC=true
docker run --rm openapitools/openapi-generator-cli:latest version
# 7.23.0-SNAPSHOT
dotnet build out-csharp-latest -c Release
# Still fails: CS0246 for type 'Null'
```

##### Steps to reproduce

1. Save the minimal spec above as `oas31-nullable-map-additionalProperties-null.yaml`.
2. Validate the file with an OpenAPI validator (e.g. [swagger-parser online](https://apidevtools.org/swagger-parser/online/)).
3. Generate a csharp client with `NORMALIZE_31SPEC=true` (release 7.17.0 or latest Docker image per FAQ).
4. Run `dotnet build` on the generated project.
5. Observe **CS0246**: `The type or namespace name 'Null' could not be found` (at minimum on `stringMap`; build fails before a usable client is produced).
6. (Optional) Repeat step 3 with `typescript-axios`, `java`, `python`, etc. to see the multi-generator table above.

**Generated csharp snippet (`XGet200Response.cs`):**

```csharp
public XGet200Response(
    Dictionary<string, Null> stringMap = default,
    Dictionary<string, List<XGet200ResponseErrorsByKeyValueInner>> errorsByKey = default)
{
    this.StringMap = stringMap;
    this.ErrorsByKey = errorsByKey;
}

public Dictionary<string, Null> StringMap { get; set; }
```

##### Related issues/PRs

- [#20213](https://github.com/OpenAPITools/openapi-generator/issues/20213) — 3.1 + `additionalProperties: false` + nullable properties (different schema shape; not a duplicate)
- [PR #22056](https://github.com/OpenAPITools/openapi-generator/pull/22056) — 7.17 additionalProperties normalizer fix (partial; does not cover `additionalProperties` **value** `type: "null"`)
- [PR #15698](https://github.com/OpenAPITools/openapi-generator/pull/15698) — normalizer null in oneOf/anyOf

##### Suggest a fix

Handle this in the **OpenAPI normalizer** when `NORMALIZE_31SPEC` is enabled (same layer as other 3.1 null rewrites), **before** language generators run.

`NORMALIZE_31SPEC` already rewrites many `type: [T, "null"]` unions on ordinary fields to `type: T` + `nullable: true`. Extend that to **`null` inside `additionalProperties` on nullable maps** (`type: [object, null]`), for example:

| Variant in repro | Rewrite toward (OAS 3.0-style) |
|------------------|----------------------------------|
| `additionalProperties: { type: "null" }` | `type: object`, `nullable: true` |
| `additionalProperties: { type: [array, "null"], items: ... }` | `type: array`, `nullable: true`, keep `items` |

Map values should then codegen as normal `object` / `array` types (e.g. `Dictionary<string, object>` in csharp), not fictional types such as `Null` or `ModelNull`.

This is a **remaining gap** after [PR #22056](https://github.com/OpenAPITools/openapi-generator/pull/22056), which fixed 3.1 mishandling of `additionalProperties: **false**` on closed objects—not nullable maps whose **value** schema still contains JSON Schema `null`.
