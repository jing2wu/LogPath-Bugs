# [BUG] (Dart-Dio) import-mappings are ignored in some import statements

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/23558
- Opened by bw-flagship on 2026-04-15, closed on 2026-04-23
- Labels: Issue: Bug
- Fix commit: 388f031deaf7f9186b219960a1f76cf2dcfd34ea

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

`--import-mappings` in dart-dio only works partially. Model files that *reference* the mapped type get the correct custom import, but `serializers.dart` and the barrel file (`<pub>.dart`) always hardcode the `model/` path. The mapped model file itself is also still generated even though it shouldn't be.

I tried `--schema-mappings` and `--model-name-mappings` as well, same result.

We're currently working around this with `sed` + `rm` after generation, which works but is ugly.

##### openapi-generator version

7.17.0 (Homebrew), also reproduced on latest master.

##### OpenAPI declaration file content or url

```yaml
openapi: "3.1.0"
info:
  title: Example
  version: "1.0.0"
paths:
  /orders:
    get:
      operationId: getOrders
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/OrderOut"
components:
  schemas:
    Address:
      type: object
      required: [street, city]
      properties:
        street:
          type: string
        city:
          type: string
    OrderOut:
      type: object
      required: [id, shippingAddress]
      properties:
        id:
          type: integer
        shippingAddress:
          $ref: "#/components/schemas/Address"
```

##### Generation Details

```bash
openapi-generator generate \
  -i spec.yaml \
  -g dart-dio \
  -o out/ \
  --type-mappings "Address=CustomAddress" \
  --import-mappings "CustomAddress=package:my_api/src/custom_models/custom_address.dart"
```

##### Steps to reproduce

1. Save the spec above as `spec.yaml`.
2. Run the generation command.
3. Check the imports in the generated files:

`out/lib/src/model/order_out.dart` — works, picks up the custom path:
```dart
import 'package:my_api/src/custom_models/custom_address.dart';
```

`out/lib/src/serializers.dart` — ignores the mapping, uses the default `model/` path:
```dart
import 'package:my_api/src/model/custom_address.dart';
```

`out/lib/my_api.dart` (barrel) — same problem:
```dart
export 'package:my_api/src/model/custom_address.dart';
```

`out/lib/src/model/custom_address.dart` is also generated even though it should be skipped for import-mapped types.

##### Related issues/PRs

##### Suggest a fix

I traced this to two mustache templates that loop over all models and always emit `model/<classFilename>.dart`, without checking import mappings:

[`serializers.mustache`](https://github.com/OpenAPITools/openapi-generator/blob/master/modules/openapi-generator/src/main/resources/dart/libraries/dio/serialization/built_value/serializers.mustache):
```mustache
{{#models}}{{#model}}import 'package:{{pubName}}/{{sourceFolder}}/{{modelPackage}}/{{classFilename}}.dart';
{{/model}}{{/models}}
```

[`lib.mustache`](https://github.com/OpenAPITools/openapi-generator/blob/master/modules/openapi-generator/src/main/resources/dart/libraries/dio/lib.mustache):
```mustache
{{#models}}{{#model}}export 'package:{{pubName}}/{{sourceFolder}}/{{modelPackage}}/{{classFilename}}.dart';
{{/model}}{{/models}}
```

These need to skip (or redirect) import-mapped models. The generator should also suppress the model file for these types, similar to how it already skips free-form objects.
