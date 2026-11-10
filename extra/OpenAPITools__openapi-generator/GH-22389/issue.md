# [BUG,Go] Missing imports for array of files and date-time parameters

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/22389
- Opened by ricardo-grande on 2025-11-19, closed on 2025-12-17
- Labels: Issue: Bug
- Fix commit: e1edb9e64571c2cbc4ad419573a0ecfd5af15b8d

## Report

#### Bug Report Checklist

- [X] Have you provided a full/minimal spec to reproduce the issue?
- [X] Have you validated the input using an OpenAPI validator?
- [X] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [X] Have you searched for related issues/PRs?
- [X] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

When generating Go client code for an endpoint that accepts an array of binary files (e.g., `type: array, items: {type: string, format: binary}`), the generator fails to add the `import "os"` statement to the generated API file, even though the parameter type is `[]*os.File`. This results in a compilation error in the generated Go code.

The same issue affects array parameters with `format: date-time`, where the `import "time"` statement is missing.

##### openapi-generator version

7.18.0-SNAPSHOT (master branch as of November 19, 2025)

##### OpenAPI declaration file content or url

```yaml
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths:
  '/upload':
    post:
      operationId: uploadFiles
      requestBody:
        required: true
        content:
          multipart/mixed:
            schema:
              type: object
              properties:
                files:
                  type: array
                  items:
                    type: string
                    format: binary
      responses:
        '200':
          description: Success
  '/events':
    get:
      operationId: getEvents
      parameters:
        - name: timestamps
          in: query
          schema:
            type: array
            items:
              type: string
              format: date-time
      responses:
        '200':
          description: Success
```

##### Generation Details

```bash
openapi-generator-cli generate \
    --additional-properties packageName=client \
    --additional-properties withGoCodegenComment=true \
    -i test-binary-array.yaml \
    -g go \
    -o ./generated
```

##### Steps to reproduce

1. Create an OpenAPI spec with an endpoint that has an array parameter with `format: binary` (see example above)
2. Generate Go client code using the `go` generator
3. Check the generated API file (e.g., `api_default.go`) - notice it's missing `import "os"`
4. Try to compile the generated code:
   ```bash
   cd generated
   go build
   ```
5. Compilation fails with error: 
```
./api_default.go:29:16: undefined: time
./api_default.go:32:54: undefined: time
./api_default.go:132:11: undefined: os
./api_default.go:135:47: undefined: os
```

##### Related issues/PRs

Issues containing `os.File`: 
https://github.com/OpenAPITools/openapi-generator/search?q=os.File&type=Issues

Open issues are very old, some might apply, but are very outdated. 

Similar issues may exist for other array-based type mappings

##### Suggest a fix

**Root Cause:**
In `AbstractGoCodegen.java`, the methods `postProcessOperationsWithModels()` and `postProcessWebhooksWithModels()` only check if `param.dataType` equals `"*os.File"` or `"time.Time"`. This works for single file/datetime parameters but fails for arrays.

For array parameters:
- Single file: `param.dataType = "*os.File"` ✓
- Array of files: `param.dataType = "[]*os.File"`, but `param.items.dataType = "*os.File"` ✗

**Solution:**
The import detection logic needs to also check `param.items.dataType` for array parameters, similar to how it's already correctly implemented in `postProcessModels()` for model properties.

**Required changes in `AbstractGoCodegen.java`:**

1. In `postProcessOperationsWithModels()` method (~line 550):
```java
// OLD CODE:
if (!addedOSImport && "*os.File".equals(param.dataType)) {
    imports.add(createMapping("import", "os"));
    addedOSImport = true;
}

if (!addedTimeImport && "time.Time".equals(param.dataType)) {
    imports.add(createMapping("import", "time"));
    addedTimeImport = true;
}

// NEW CODE:
if (!addedOSImport && ("*os.File".equals(param.dataType) ||
        (param.items != null && "*os.File".equals(param.items.dataType)))) {
    imports.add(createMapping("import", "os"));
    addedOSImport = true;
}

if (!addedTimeImport && ("time.Time".equals(param.dataType) ||
        (param.items != null && "time.Time".equals(param.items.dataType)))) {
    imports.add(createMapping("import", "time"));
    addedTimeImport = true;
}
```

2. In `postProcessWebhooksWithModels()` method (~line 651): Apply the same change

**Why this works:**
- For single parameters, `param.dataType` is checked directly
- For array parameters, `param.items` contains the element type information
- This aligns with the existing correct implementation in `postProcessModels()` (line ~780)

I will provide a PR with the fix

## Comment by ricardo-grande on 2025-11-26

@antihax @grokify @kemokemo @jirikuncar @ph4r5h4d @lwj5 
Hi guys, I am mentioning you since you are listed as part of the Go committee in this project. Could you please take a look a this bug and determine if it is worth fixing and if the fix is worth merging? Thank you so much in advance!!!
