# [BUG] [python] [server] [fastapi] Generates invalid typings for binary responses

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/20775
- Opened by hegerdes on 2025-03-03, closed on 2026-07-14
- Labels: Issue: Bug
- Fix commit: 80c08fa3dd27d4e43a6a1f72b3420e8f24b66de5

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apitools.dev/swagger-parser/online/))? - **NOTE**: The link is points to an unregistered domain
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. Eg:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

<!-- describe what is the question, suggestion or issue and why this is a problem for you. -->
When you use the python sever generation for fastapi and declare a binary output in your OpenAPI-Spec, the generator produces invalid type hints. There is no `file` type in python 3 AFAIK, and if there is the import is missing.

##### openapi-generator version
```
openapi-generator-cli 7.13.0-SNAPSHOT
  commit : 5cef080
  built  : -999999999-01-01T00:00:00+18:00
  source : https://github.com/openapitools/openapi-generator
  docs   : https://openapi-generator.tech/
```
<!-- which version of openapi-generator are you using, is it a regression? -->

##### OpenAPI declaration file content or url

```yaml
openapi: 3.1.3
info:
  title: File Demo - OpenAPI 3.0
  version: 0.0.1
servers:
  - url: http://localhost:8080

paths:
  /coverletter/{asset_id}:
    get:
      summary: Download a pdf
      operationId: download_pdf
      parameters:
        - name: asset_id
          in: path
          description: ID of asset to get
          required: true
          schema:
            type: string
      responses:
        "200":
          description: PDF binary
          content:
            application/pdf:
              schema:
                type: string
                format: binary
        "401":
          description: Authorization information is missing or invalid.
        "404":
          description: A document with the specified ID was not found.
```

<!-- if it is a bug, a json or yaml that produces it.
If you post the code inline, please wrap it with
```yaml
(here your code)
```
(for YAML code) or
```json
(here your code)
```
(for JSON code), so it becomes more readable. If it is longer than about ten lines,
please create a Gist (https://gist.github.com) or upload it somewhere else and
link it here.
  -->

##### Generation Details

<!-- 
    Prefer CLI steps, including the language, libraries and various options. 
    Providing config-based settings allows for simpler testing across CLI and plugins. 
    For examples, see https://github.com/OpenAPITools/openapi-generator/tree/master/bin/configs
-->

The code was generated with:
```bash
docker run --rm -it --user $(id -u $USER):$(id -g $USER) \
  -v ${PWD}:/local openapitools/openapi-generator-cli generate \
  -i /local/file-demo.yaml \
  -g python-fastapi \
  -o /local/demo/
```

##### Steps to reproduce

```bash
docker run --rm -it --user $(id -u $USER):$(id -g $USER) \
  -v ${PWD}:/local openapitools/openapi-generator-cli generate \
  -i /local/file-demo.yaml \
  -g python-fastapi \
  -o /local/demo/
cd demo
pip install -r requirements.txt
PYTHONPATH=src uvicorn openapi_server.main:app --host 0.0.0.0 --port 8080
```

<!-- unambiguous set of steps to reproduce the bug.-->

##### Related issues/PRs
**None**

<!-- has a similar issue/PR been reported/opened before? Please do a search in https://github.com/openapitools/openapi-generator/issues?utf8=%E2%9C%93&q=is%3Aissue%20 -->

##### Suggest a fix

<!-- if you can't fix the bug yourself, perhaps you can point to what might be
  causing the problem (line of code or commit), or simply make a suggestion -->

The python types are declared here: https://github.com/OpenAPITools/openapi-generator/blob/70df1170cca0292ca313f3562d38b0df443ca39b/modules/openapi-generator/src/main/java/org/openapitools/codegen/languages/AbstractPythonPydanticV1Codegen.java#L100-L101

But this might not be the right type for `file`. There is no `file` type in python (AFAIK), only a `File` type that is part of FastAPI, [see](https://fastapi.tiangolo.com/tutorial/request-forms-and-files/) or a `FileResponse` [see](https://fastapi.tiangolo.com/reference/responses/#starlette-responses)  

If the `File` type from FastApi is meant here, the first letter must be upper case and it is missing the import in 
https://github.com/OpenAPITools/openapi-generator/blob/70df1170cca0292ca313f3562d38b0df443ca39b/modules/openapi-generator/src/main/resources/python-fastapi/api.mustache#L10-L15

**Screenshot of the error:**
![Image](https://github.com/user-attachments/assets/4e61da99-1dd9-4849-a945-ff4f2663e2b4)

## Comment by VigneshVSV on 2025-10-31

Any updates?
