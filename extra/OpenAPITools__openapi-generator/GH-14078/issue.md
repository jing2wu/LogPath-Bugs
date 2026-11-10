# [BUG,Python] additionalProperties sometimes breaks

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/14078
- Opened by Poolmann on 2022-11-21, closed on 2022-11-23
- Labels: Client: Python, Issue: Bug
- Fix commit: 3eb90a69e637bd7bf00bcc76aec72716f5ea2b54

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [ ] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. Eg:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

<!-- describe what is the question, suggestion or issue and why this is a problem for you. -->

When using an SchemaObject, that contains the `additionalProperties` attribute with `type: object`, I get the error: 
`AttributeError: type object 'MetaOapg' has no attribute 'additional_properties'`.

As I have tested this, I have come to the conclusion that this only occurs, when there are other Schemas with `additionalProperties` defined.

##### openapi-generator version

<!-- which version of openapi-generator are you using, is it a regression? -->

Version 6.3.0 Python

##### OpenAPI declaration file content or url

This my minimal Example to reproduce the bug
```yaml
openapi: 3.0.0
info:
  version: 1.0.0
  title: issue 13997 spec
  license:
    name: Apache-2.0
    url: 'https://www.apache.org/licenses/LICENSE-2.0.html'
servers: []
tags: []
paths: {}
components:
  schemas:
    Event:
      type: object
      required:
        - apiVersion
        - modules
      properties:
        apiVersion:
          type: string
        timeout:
          type: integer
          format: int32
          example: 10000
        modules:
          type: object
          additionalProperties:
            type: object
    UploadEvent:
      type: object
      properties:
        uploadId:
          type: string
          example: "6Ms5S3"
        result:
          type: object
          additionalProperties:
            type: array
            items:
              type: object
```
**And for some reason this works (without the second event):**
```yaml
openapi: 3.0.0
info:
  version: 1.0.0
  title: issue 13997 spec
  license:
    name: Apache-2.0
    url: 'https://www.apache.org/licenses/LICENSE-2.0.html'
servers: []
tags: []
paths: {}
components:
  schemas:
    Event:
      type: object
      required:
        - apiVersion
        - modules
      properties:
        apiVersion:
          type: string
        timeout:
          type: integer
          format: int32
          example: 10000
        modules:
          type: object
          additionalProperties:
            type: object
```
##### Generation Details

<!-- 
    Prefer CLI steps, including the language, libraries and various options. 
    Providing config-based settings allows for simpler testing across CLI and plugins. 
    For examples, see https://github.com/OpenAPITools/openapi-generator/tree/master/bin/configs
-->

`java -jar openapi-generator-cli-6.3.0.jar generate -i additional.yaml -g python`

##### Steps to reproduce

<!-- unambiguous set of steps to reproduce the bug.-->

Generate with specified yaml file above and try to import Event like: `from openapi_client.model.event import Event`

##### Complete Stacktrace
```
Traceback (most recent call last):
  File "sample.py", line 2, in <module>
    from devaice_web_api_client.model.event import Event
  File "/home/user/.local/lib/python3.8/site-packages/openapi_client/model/event.py", line 26, in <module>
    class Event(
  File "/home/user/.local/lib/python3.8/site-packages/openapi_client/model/event.py", line 36, in Event
    class MetaOapg:
  File "/home/user/.local/lib/python3.8/site-packages/openapi_client/model/event.py", line 42, in MetaOapg
    class properties:
  File "/home/user/.local/lib/python3.8/site-packages/openapi_client/model/event.py", line 46, in properties
    class modules(
  File "/home/user/.local/lib/python3.8/site-packages/openapi_client/model/event.py", line 65, in modules
    **kwargs: typing.Union[MetaOapg.additional_properties, dict, frozendict.frozendict, ],
AttributeError: type object 'MetaOapg' has no attribute 'additional_properties'

```

## Comment by spacether on 2022-11-23

This issue was fixed in the new repo that hosts the python generator: https://github.com/openapi-json-schema-tools/openapi-json-schema-generator/pull/93

Soon I will merge a fix into this repo too.

## Comment by spacether on 2022-11-23

@Poolmann fixed!

## Comment by Poolmann on 2022-11-23

@spacether Thx, works now!
