# [BUG,Python] Header parameter with content: application/json is not JSON serialized

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/25067
- Opened by AndreyVMarkelov on 2026-09-30, closed on 2026-10-04
- Labels: Issue: Bug
- Fix commit: a5e4173d6caa3c24affa52dd71135e96a0bb049e

## Report

#### Bug Report Checklist

-   [x] Have you provided a full/minimal spec to reproduce the issue?
-   [ ] Have you validated the input using an OpenAPI validator?
-   [x] Have you [tested with the latest
    master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator)
    to confirm the issue still exists?
-   [x] Have you searched for related issues/PRs?
-   [x] What's the actual output vs expected output?
-   [ ] \[Optional\] Sponsorship to speed up the bug fix or feature
    request
    ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

The Python client generator does not JSON-serialize header parameters
defined using `content: application/json`.

For a header parameter backed by an object schema, the generated client
assigns the model directly to the header:

``` python
_header_params['X-Json-Arg'] = x_json_arg
```

`ApiClient.sanitize_for_serialization()` later converts the model to a
Python `dict`, but that value is not JSON-encoded before it is used as
an HTTP header value.

As a result, a parameter declared with `content: application/json` does
not produce the JSON string required by the OpenAPI declaration.

Regular schema-based header parameters should keep their existing
behavior.

##### openapi-generator version

`7.26.0-SNAPSHOT`

Reproduced against the latest `master`.

##### OpenAPI declaration file content or url

Minimal repro:

``` yaml
openapi: 3.1.0
info:
  title: JSON header content test
  version: 1.0.0
paths:
  /test:
    post:
      operationId: testJsonHeader
      parameters:
        - name: X-Json-Arg
          in: header
          required: true
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HeaderArg'
        - name: X-Plain-Arg
          in: header
          required: false
          schema:
            type: string
      responses:
        '204':
          description: No content
components:
  schemas:
    HeaderArg:
      type: object
      properties:
        path:
          type: string
        recursive:
          type: boolean
```

##### Generation Details

Generator: `python`

``` bash
java -jar modules/openapi-generator-cli/target/openapi-generator-cli.jar generate \
  -i /tmp/json-header-content.yaml \
  -g python \
  -o /tmp/python-json-header
```

##### Steps to reproduce

1.  Build the current `master`.
2.  Save the OpenAPI document above as `/tmp/json-header-content.yaml`.
3.  Generate a Python client using the command above.
4.  Inspect `openapi_client/api/default_api.py`.

Actual generated code:

``` python
if x_json_arg is not None:
    _header_params['X-Json-Arg'] = x_json_arg
```

Expected behavior:

``` python
if x_json_arg is not None:
    _header_params['X-Json-Arg'] = json.dumps(
        self.api_client.sanitize_for_serialization(x_json_arg)
    )
```

The regular header should remain unchanged:

``` python
_header_params['X-Plain-Arg'] = x_plain_arg
```

##### Related issues/PRs

Related Java generator issue/PR: #25056

This is the equivalent problem in the Python client generator.

##### Suggest a fix

`CodegenParameter.contentType` is populated for parameters defined using
`content`, so the Python generator can detect JSON header parameters
during parameter post-processing.

A possible fix is to: - mark header parameters whose `contentType` is
JSON; - JSON-encode only those values in `python/api.mustache`; -
preserve the existing behavior for ordinary header parameters.
