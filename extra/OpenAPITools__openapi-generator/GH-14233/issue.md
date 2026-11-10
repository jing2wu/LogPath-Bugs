# [BUG]  Java Feign multiple Accept header values not working

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/14233
- Opened by prousseau-korem on 2022-12-09, closed on 2024-01-12
- Labels: Issue: Bug
- Fix commit: e384201416f48a79e7f640e5f00b57ecb7fff07b

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [ ] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. Eg:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

If the response contains multiple content-type, the accept header only contain json

##### openapi-generator version

Docker image: openapitools/openapi-generator-cli:v6.2.1

##### OpenAPI declaration file content or url

```json
{
  "openapi": "3.0.2",
  "info": {
    "title": "Api",
    "version": "0.0.0-dev"
  },
  "paths": {
    "/api/download": {
      "post": {
        "summary": "download",
        "operationId": "download",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/zip": {
                "schema": {
                  "type": "string",
                  "format": "binary"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "HTTPValidationError": {
        "title": "HTTPValidationError",
        "type": "object",
        "properties": {
          "detail": {
            "title": "Detail",
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/ValidationError"
            }
          }
        }
      },
      "ValidationError": {
        "title": "ValidationError",
        "required": [
          "loc",
          "msg",
          "type"
        ],
        "type": "object",
        "properties": {
          "loc": {
            "title": "Location",
            "type": "array",
            "items": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "integer"
                }
              ]
            }
          },
          "msg": {
            "title": "Message",
            "type": "string"
          },
          "type": {
            "title": "Error Type",
            "type": "string"
          }
        }
      }
    }
  }
}
```

##### Generation Details
The accept header should contain both content-type application/zip and application/json
```
@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2022-12-09T16:10:10.855650Z[Etc/UTC]")
public interface DefaultApi extends ApiClient.Api {


  /**
   * download
   * 
   * @return File
   */
  @RequestLine("POST /api/download")
  @Headers({
    "Accept: application/json",
  })
  File download();

  /**
   * download
   * Similar to <code>download</code> but it also returns the http response headers .
   * 
   * @return A ApiResponse that wraps the response boyd and the http headers.
   */
  @RequestLine("POST /api/download")
  @Headers({
    "Accept: application/json",
  })
  ApiResponse<File> downloadWithHttpInfo();
}
```
##### Steps to reproduce

Command to reproduce to bug: `generate -i /out/openapi.json -g java --library feign --additional-properties=serializationLibrary=jackson -o /out/client`

##### Related issues/PRs

https://github.com/OpenAPITools/openapi-generator/issues/728

##### Suggest a fix

The accept header whould contain both content-type 
Should use https://developer.mozilla.org/en-US/docs/Glossary/Quality_values

## Comment by Breus on 2023-04-14

In the latest version (6.5.0) this issue still persists

## Comment by wing328 on 2023-04-15

Please feel free to submit a PR to fix the issue or kindly sponsor the community to fix it.

## Comment by Breus on 2023-04-17

@wing328 I debugged the issue and opened [this PR](https://github.com/OpenAPITools/openapi-generator/pull/15245). Curious to hear your thoughts on it!

## Comment by WannabeSoftwareEngineer on 2024-01-11

Issue still present in version 6.6.0
