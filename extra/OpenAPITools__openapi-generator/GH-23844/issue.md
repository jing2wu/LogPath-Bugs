# [BUG,Go] enumUnknownDefaultCase generates colliding UNKNOWN_DEFAULT_OPEN_API constants when enumClassPrefix=false

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/23844
- Opened by TyphonHill on 2026-05-21, closed on 2026-06-01
- Labels: Issue: Bug
- Fix commit: 50440611d576f89ec8baa08de22c25b0a8ad358f

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?

##### Description

When using `enumUnknownDefaultCase=true` with the Go generator and `enumClassPrefix=false` (the default), every generated enum type emits a bare `UNKNOWN_DEFAULT_OPEN_API` constant. Since all enum models live in the same Go package, this causes a compilation error:

```
UNKNOWN_DEFAULT_OPEN_API redeclared in this block
        model_status_a.go:XX: other declaration of UNKNOWN_DEFAULT_OPEN_API
```

The sentinel constant is added as an `enumVar` and rendered through the same template path as regular constants:

```mustache
{{#enumClassPrefix}}{{{classname.toUpperCase}}}_{{/enumClassPrefix}}{{name}}
```

When `enumClassPrefix=false`, no prefix is applied, so every enum gets an identical `UNKNOWN_DEFAULT_OPEN_API` constant.

Setting `enumClassPrefix=true` fixes the collision but renames **all** existing enum constants (e.g. `ProvisionHalted` becomes `MODELPROVISIONSTAGEVALUE_ProvisionHalted`), which is a breaking change for consumers.

##### openapi-generator version

7.22.0 (not a regression — this is the first release with Go support for `enumUnknownDefaultCase`, introduced by PR #23417)

##### OpenAPI declaration file content or url

```yaml
openapi: 3.0.1
info:
  version: 1.0.0
  title: Test API
paths: {}
components:
  schemas:
    StatusA:
      type: string
      enum:
        - active
        - inactive
    StatusB:
      type: string
      enum:
        - pending
        - completed
```

##### Generation Details

```bash
openapi-generator-cli generate \
  -i spec.yaml \
  -g go \
  --additional-properties enumUnknownDefaultCase=true \
  --package-name myapi
```

##### Steps to reproduce

1. Generate a Go client with the above spec and `enumUnknownDefaultCase=true` (without `enumClassPrefix=true`)
2. Attempt to compile the generated code: `go build ./...`
3. Observe: `UNKNOWN_DEFAULT_OPEN_API redeclared in this block`

##### Related issues/PRs

- PR #23417 introduced `enumUnknownDefaultCase` for Go
- Issue #18747 tracked the original missing feature

##### Suggest a fix

The sentinel constant should be unique per enum type when `enumClassPrefix=false`. The template could unconditionally prefix the sentinel with the classname, e.g.:

```mustache
{{{classname}}}UnknownDefaultOpenApi {{{classname}}} = "unknown_default_open_api"
```

This would generate `StatusAUnknownDefaultOpenApi`, `StatusBUnknownDefaultOpenApi`, etc. — unique names without requiring `enumClassPrefix=true` and without renaming existing constants.

## Comment by wing328 on 2026-06-01

thanks @SJvaca30 for the PR fixing the issue

@TyphonHill please pull the latest master to give it a try
