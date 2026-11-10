# [BUG] [Go] `pattern` values containing control characters are copied raw into generated struct tags, producing invalid Go source (`illegal character NUL`)

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/25263
- Opened by Fyusel on 2026-10-15, closed on 2026-10-19
- Labels: Issue: Bug
- Fix commit: 27c33732efd3a759726643eeeb381cd175bc8768

## Report

#### Bug Report Checklist

- [X] Have you provided a full/minimal spec to reproduce the issue?
- [X] Have you validated the input using an OpenAPI validator?
- [X] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [X] Have you searched for related issues/PRs?
- [X] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://redirect.github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. E.g.:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

When a `string` property's `pattern` constraint contains a JSON `\u00XX`-style escape for a
C0/C1 control code point (e.g. to explicitly forbid control characters in a free-text field,
a common and legitimate validation use case), the Go client generator copies the **decoded**
pattern value directly into the generated `validate:"regexp=..."` struct tag without
re-escaping it for Go source syntax.

Go disallows a literal NUL character — and
most other control characters — anywhere in source code, including inside string and raw
(backtick) string literals, so the generated file fails to compile / fails `gofmt` with:

```
illegal character NUL
```

This is the same code path that was previously patched for two other unsafe characters:
backtick (fixed in #19358, closing #19102) and comma (fixed in #24349, closing #20079).

##### openapi-generator version

Reproduced end-to-end (actual Go codegen run + `gofmt`) against **v7.25.0**. The affected
code in `AbstractGoCodegen.java` in the latest release **v7.26.0** (2026-10-06) and on `master` as of 2026-10-14, so
this still affects the current release.


##### OpenAPI declaration file content

```yaml
openapi: 3.0.3
info:
  title: control-char-pattern-repro
  version: "1.0"
paths:
  /ping:
    get:
      operationId: ping
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/TestModel"
components:
  schemas:
    TestModel:
      type: object
      properties:
        key:
          type: string
          # NOTE: as written here, this YAML/JSON "\^@" is the standard (and only
          # valid) way to express the NUL code point in a JSON Schema pattern string.
          # It decodes to a literal control character when the spec is parsed.
          pattern: "^[^\^@-\^_]+$"
```

(equivalent minimal JSON spec, for convenience:)

```json
{
  "openapi": "3.0.3",
  "info": { "title": "control-char-pattern-repro", "version": "1.0" },
  "paths": {
    "/ping": {
      "get": {
        "operationId": "ping",
        "responses": {
          "200": {
            "description": "ok",
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/TestModel" }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "TestModel": {
        "type": "object",
        "properties": {
          "key": {
            "type": "string",
            "pattern": "^[^\^@-\^_]+$"
          }
        }
      }
    }
  }
}
```

##### Generation Details

```shell
openapi-generator-cli generate \
  -g go \
  --input-spec spec.json \
  --output out \
  --package-name testapi \
  --enable-post-process-file \
  --global-property apis,models,modelTests=true,modelDocs=false,apiDocs=false,supportingFiles,apiTests=false
```

##### Steps to reproduce

1. Run the command above against the spec.
2. Run `gofmt -l out/model_test_model.go` (or just try to `go build`).
3. Observe:
   ```
   out/model_test_model.go:22:82: illegal character NUL
   ```
##### Actual vs expected output

Generated struct field (actual — contains two raw, non-printable bytes: 0x00 and 0x1F,
shown below as `<NUL>`/`<US>` since they are not renderable in this markdown file):

```go
Key *string `json:"key,omitempty" validate:"regexp=^[^<NUL>-<US>]+$"`
```

Expected — the pattern's control-character escapes should be re-escaped as literal Go/regex
escape text when written into the struct tag, e.g.:

```go
Key *string `json:"key,omitempty" validate:"regexp=^[^\x00-\x1f]+$"`
```

(Go's own `regexp` package correctly understands `\x00`-style hex escapes inside the pattern
text, so this would both compile and preserve the original validation semantics.)

##### Related issues/PRs

- #19102 / #19358 — backtick in pattern breaks generated code (fixed, same code block)
- #20079 / #24349 — comma in pattern breaks `validate` tag syntax (fixed, same code block)
- #22101 — patterns containing escape sequences / character classes produce 4 consecutive
  backslashes instead of 1 (open, different symptom of the same "pattern isn't properly
  re-escaped for Go" root issue)
