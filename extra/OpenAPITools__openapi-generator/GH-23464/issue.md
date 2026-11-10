# [BUG,scala-sttp,circe] Circe codecs do not preserve original JSON field names for non-camelCase properties

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/23464
- Opened by nikhilsu on 2026-04-07, closed on 2026-04-09
- Labels: Issue: Bug
- Fix commit: a79d60b3fb3712497ddd84852f45aa4140654b49

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apitools.dev/swagger-parser/online/))?
- [x] Have
  you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator)
  to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature
  request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

- When using the `scala-sttp` generator with `jsonLibrary=circe`, the generated code relies on circe's `AutoDerivation` to derive `Encoder`/`Decoder` instances. This derives codecs from Scala field names (camelCase), **not** the original JSON property names from the OpenAPI spec.
- Properties like `first-name` (kebab-case), `phone_number` (snake_case), or `ZipCode` (PascalCase) are converted to camelCase Scala fields (`firstName`, `phoneNumber`, `zipCode`). Circe's `AutoDerivation` then serializes/deserializes using these Scala field names instead of the original JSON names, breaking the wire contract.
- Additionally, `AutoDerivation` cannot derive codecs for `File` (from `format: binary`) or `Any` (from `type: object`),
causing compilation failures when those types appear in model properties.

##### openapi-generator version

7.22.0-SNAPSHOT (latest master as of 2026-04-07), also affects 7.21.0 and all prior versions with circe support.

##### OpenAPI declaration file content or url

```yaml
openapi: 3.0.0
info:
  title: Mixed Case Test
  version: 1.0.0
paths:
  /test:
    get:
      operationId: getTest
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MixedCaseModel'
components:
  schemas:
    MixedCaseModel:
      type: object
      properties:
        first-name:
          type: string
        phone_number:
          type: string
        lastName:
          type: string
        ZipCode:
          type: string
        address:
          type: string
    BinaryPayload:
      type: object
      properties:
        data:
          type: string
          format: binary
        metadata:
          type: object
```

Note: `format: binary` maps to `java.io.File` and `type: object` (without properties) maps to `Any` in the scala-sttp generator. Circe's `AutoDerivation` cannot derive codecs for either type, causing compilation failures.

##### Generation Details

```bash
$ openapi-generator-cli version
7.22.0-SNAPSHOT
```

```bash
$ openapi-generator-cli generate \
    -i mixed-case-fields.yaml \
    -g scala-sttp \
    -o /tmp/scala-sttp-circe-test \
    --additional-properties=jsonLibrary=circe
[main] INFO  o.o.codegen.DefaultGenerator - Generating with dryRun=false
[main] INFO  o.o.codegen.DefaultGenerator - OpenAPI Generator: scala-sttp (client)
[main] INFO  o.o.codegen.DefaultGenerator - Generator 'scala-sttp' is considered stable.
[main] INFO  o.o.c.languages.AbstractScalaCodegen - Environment variable SCALA_POST_PROCESS_FILE not defined so the Scala code may not be properly formatted. To define it, try 'export SCALA_POST_PROCESS_FILE=/usr/local/bin/scalafmt' (Linux/Mac)
[main] INFO  o.o.c.languages.AbstractScalaCodegen - NOTE: To enable file post-processing, 'enablePostProcessFile' must be set to `true` (--enable-post-process-file for CLI).
[main] INFO  o.o.codegen.TemplateManager - writing file /tmp/scala-sttp-circe-test/src/main/scala/org/openapitools/client/model/MixedCaseModel.scala
[main] INFO  o.o.codegen.TemplateManager - writing file /tmp/scala-sttp-circe-test/src/main/scala/org/openapitools/client/api/DefaultApi.scala
[main] INFO  o.o.codegen.TemplateManager - writing file /tmp/scala-sttp-circe-test/src/main/scala/org/openapitools/client/core/JsonSupport.scala
[main] INFO  o.o.codegen.TemplateManager - writing file /tmp/scala-sttp-circe-test/src/main/scala/org/openapitools/client/core/AdditionalTypeSerializers.scala
```

##### Steps to reproduce

1. Save the spec above as `mixed-case-fields.yaml`
2. Generate:
   ```bash
   openapi-generator-cli generate \
     -i mixed-case-fields.yaml \
     -g scala-sttp \
     -o /tmp/scala-sttp-circe-test \
     --additional-properties=jsonLibrary=circe
   ```
3. Inspect the generated `MixedCaseModel.scala` — there is no companion object with explicit encoder/decoder. The code
   relies on `AutoDerivation` which uses Scala field names on the wire.
4. Inspect `JsonSupport.scala`:
   ```scala
   object JsonSupport extends SttpCirceApi with AutoDerivation with DateSerializers with AdditionalTypeSerializers {
   ```
   `AutoDerivation` will ser/deserialize `phoneNumber` instead of the original `phone_number`, `firstName` instead of
   `first-name`, and `zipCode` instead of `ZipCode`.
5. Attempting to compile the generated project fails:
   ```
   [error] could not find implicit value for evidence parameter of type io.circe.Encoder[java.io.File]
   [error] could not find implicit value for evidence parameter of type io.circe.Encoder[Any]
   ```

**Actual wire behavior:**

```json
{
  "firstName": "John",
  "phoneNumber": "555-1234",
  "zipCode": "90210"
}
```

**Expected wire behavior (matching the spec):**

```json
{
  "first-name": "John",
  "phone_number": "555-1234",
  "ZipCode": "90210"
}
```

##### Related issues/PRs

- The `scala-http4s` generator already handles this correctly by generating explicit `Encoder`/`Decoder` instances using
  `baseName` in `model.mustache`
- The `scala-sttp4-jsoniter` generator handles this correctly using `@named("{{baseName}}")` annotations
- The `type: object` -> `Any` mapping also differs: `scala-http4s` maps it to `Json` (which has built-in circe codecs),
  while `scala-sttp` maps it to `Any` (which does not)
- Related issue for inline enum codecs not being generated: https://github.com/OpenAPITools/openapi-generator/pull/17697

##### Suggest a fix

1. **`model.mustache`**: For circe (`{{#circe}}`), generate a companion object with explicit `Encoder.instance`/
   `Decoder.instance` per model using `{{baseName}}` for JSON field names, following the `scala-http4s` pattern.
2. **`jsonSupport.mustache`**: Remove `AutoDerivation` mixin since explicit instances are now generated per model.
3. **`additionalTypeSerializers.mustache`**: Add circe `Encoder`/`Decoder` for `File` (delegating to `Array[Byte]`
   codec) and `Any` (delegating to `Json` codec).
4. **`ScalaSttpClientCodegen.java`**: Map `type: object` to `io.circe.Json` for circe (and `org.json4s.JValue` for
   json4s) instead of `Any`, matching `scala-http4s`.

I'm planning to submit a pull request with this fix.
