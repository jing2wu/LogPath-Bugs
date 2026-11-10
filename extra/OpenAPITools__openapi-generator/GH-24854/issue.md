# [BUG] [cpp-httplib-server] Primitive and binary response types incorrectly generated as models

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/24854
- Opened by tito97sp on 2026-09-03, closed on 2026-10-19
- Labels: Issue: Bug
- Fix commit: 67df0397c1612705d081b2f297ac0c5d9069638a

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [ ] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

The `cpp-httplib-server` generator incorrectly generates or references model headers for OpenAPI primitive/built-in types.

In particular, responses using primitive `string` or binary/file schemas can result in generated code containing invalid model includes such as:

```cpp
#include "model/String.h"
```

or:

```cpp
#include "model/File.h"
```

These models are not defined in the OpenAPI specification and should not be generated.

For example, a response defined as:

```yaml
content:
  text/plain:
    schema:
      type: string
```

should be mapped to the corresponding C++ primitive type, such as `std::string`, rather than a generated `String` model.

Similarly, a binary response such as:

```yaml
content:
  application/octet-stream:
    schema:
      type: string
      format: binary
```

should be mapped to the generator's appropriate binary/file representation rather than resulting in a reference to a non-existent `model/File.h`.

This makes the generated server code fail to compile because the referenced model headers do not exist.

##### openapi-generator version

OpenAPI Generator: `7.25.0`

Generator:

```text
cpp-httplib-server
```

OpenAPI version:

```text
3.1.0
```

##### OpenAPI declaration file content or url

Minimal reproducible specification:

```yaml
openapi: 3.1.0

info:
  title: Primitive Response Test
  version: 1.0.0

paths:

  /text:
    get:
      operationId: getText
      responses:
        '200':
          description: Successful response
          content:
            text/plain:
              schema:
                type: string

  /file:
    get:
      operationId: getFile
      responses:
        '200':
          description: Binary response
          content:
            application/octet-stream:
              schema:
                type: string
                format: binary
```

##### Generation Details

Generator:

```text
cpp-httplib-server
```

Example CLI command:

```bash
docker run --rm \
    --user "$(id -u):$(id -g)" \
    -v "$SCRIPT_DIR:/local" \
    openapitools/openapi-generator-cli:v7.25.0 \
    generate \
    -i /local/v1.0/vsat_endpoint_v1.json \
    -g cpp-httplib-server \
    -o /local/generated/generated_api_server_cpp_httplib 
```

##### Steps to reproduce

1. Create the `openapi.yaml` shown above.
2. Generate the server using:

```bash
    --user "$(id -u):$(id -g)" \
    -v "$SCRIPT_DIR:/local" \
    openapitools/openapi-generator-cli:v7.25.0 \
    generate \
    -i /local/v1.0/vsat_endpoint_v1.json \
    -g cpp-httplib-server \
    -o /local/generated/generated_api_server_cpp_httplib 
```

3. Inspect the generated C++ source code.
4. The generated code contains references to model headers for primitive/built-in types, for example:

```cpp
#include "model/String.h"
```

and:

```cpp
#include "model/File.h"
```

5. These headers are not present in the generated project.
6. Compilation therefore fails because the generated code references non-existent model classes.

##### Actual output vs expected output

**Actual:**

The generator generates/references model classes for primitive or built-in OpenAPI types.

Examples include:

```cpp
#include "model/String.h"
```

and:

```cpp
#include "model/File.h"
```

However, the OpenAPI specification does not define `String` or `File` as schemas.

As a result, the generated C++ server code contains references to non-existent headers/classes and does not compile.

**Expected:**

Primitive and built-in OpenAPI types should be mapped to their corresponding C++ representations without generating model classes.

For example:

```yaml
schema:
  type: string
```

should resolve to something equivalent to:

```cpp
std::string
```

and:

```yaml
schema:
  type: string
  format: binary
```

should resolve to the generator's appropriate binary/file representation without creating or referencing:

```cpp
model/File.h
```

No `String.h` or `File.h` model should be generated or referenced unless the user explicitly defines corresponding schemas in the OpenAPI document.

##### Related issues/PRs

I have not yet identified a related issue or PR specifically covering primitive `string` and `binary/file` response schemas in the `cpp-httplib-server` generator.

##### Suggest a fix

The generator should correctly distinguish between:

1. Primitive OpenAPI types (`string`, `integer`, `number`, `boolean`, etc.)
2. OpenAPI formatted primitive types such as `string/binary`
3. User-defined schemas/models

Primitive types should be resolved directly to their corresponding C++ types rather than being passed through the model generation mechanism.

In particular:

```yaml
type: string
```

should resolve to the generator's C++ string type, and:

```yaml
type: string
format: binary
```

should resolve to the appropriate binary representation.

The response type resolution and model/include generation logic should avoid producing model references such as:

```cpp
#include "model/String.h"
#include "model/File.h"
```

when the corresponding types originate from primitive OpenAPI schemas rather than user-defined models.
