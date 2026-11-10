# [BUG] [Python-fastapi] File input incorrectly generated with FastAPI Form

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/20115
- Opened by reyescabello on 2024-11-15, closed on 2026-05-17
- Labels: Issue: Bug
- Fix commit: 179acc91ea700eb3f5ba3bff18cb2a63d5c1100e

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
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

When generating the specified content in the OpenAPI file, the endpoint that receives a file generates an input of type string in the generated Swagger UI. This happens because the generated FastAPI endpoint uses a Form.

We compared this case with another application using the same file, where the input is correctly generated as a file upload field.

##### openapi-generator version

<!-- which version of openapi-generator are you using, is it a regression? -->

v7.9.0

##### OpenAPI declaration file content or url

https://gist.github.com/reyescabello/6cd965708fd0b03e8eadb9f3c0c0a899#file-query_param_example-yml

##### Generation Details

Generated with jar:

java -jar openapi-generator-cli.jar generate -i openapi.yml -g python-fastapi -o openapi_server

##### Steps to reproduce
When generating the specified content in the OpenAPI file, the endpoint that includes the file looks like this:
```python
async def upload_post(
    file: str = Form(None, description=""),
) -> None:
    
    return await BaseExampleApi.subclasses[0]().upload_post(file)
```
And this is what it looks like in swagger.

![image](https://github.com/user-attachments/assets/db311fbd-1797-4ae2-b6cd-c4d2cbe55a2a)

The expected code is something like this:

```python
async def upload_post(
    file: UploadFile,
) -> None:
    
    return await BaseExampleApi.subclasses[0]().upload_post(file)
```

##### Related issues/PRs

<!-- has a similar issue/PR been reported/opened before? Please do a search in https://github.com/openapitools/openapi-generator/issues?utf8=%E2%9C%93&q=is%3Aissue%20 -->

##### Suggest a fix

<!-- if you can't fix the bug yourself, perhaps you can point to what might be
  causing the problem (line of code or commit), or simply make a suggestion -->

## Comment by hegerdes on 2025-02-27

This can also happen when outputting a file/binary from an api response.

## Comment by ampedandwired on 2025-03-13

I'm also having a lot of trouble making file uploads work with python-fastapi as it stands. I'm finding when generating an API with something like this:

```yaml
requestBody:
  content:
    multipart/form-data:
      schema:
        type: object
        properties:
          data:
            type: array
            items:
              type: string
              format: binary
```

I'm ending up with the `data` param defined like this in `default_api.py`:

```python
data: Optional[List[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]]] = Form(None, description=""),
```

This just doesn't seem to work (`data` is always `None`). The following code works though
```python
data: Optional[List[UploadFile]] = File(None, description=""),
```

## Comment by sagarjain13 on 2025-04-04

Facing the same issue:

```
name: str = Form(None, description="")
file: str = Form(None, description="The file to be uploaded")
```

above code auto-generates when using 
```
      requestBody:
        description: Create a new group for a single satellite or a group for different types of satellites
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                name:
                  type: string
                file:
                  type: string
                  format: binary
                  description: "The file to be uploaded"
        required: true
```

## Comment by DGV1995 on 2025-05-07

Any news about this bug?

## Comment by tz-reinberger on 2026-03-03

I can confirm the changes from `https://github.com/fastapi/fastapi/pull/14953` (FastAPI version 0.129.1 and newer) break the `python` client generator.
The change from the schema `{"type": "string", "format": "binary"}` to `{"type": "string", "contentMediaType": "application/octet-stream"}` broke it.
This workaround reverts the change for better compatibility:
```
class CompatibleUploadFile(UploadFile):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: Any) -> dict[str, Any]:
        return {"type": "string", "format": "binary"}
```
