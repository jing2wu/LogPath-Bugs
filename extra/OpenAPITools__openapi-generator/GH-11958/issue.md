# [BUG] python generates wrong model name and model file name

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/11958
- Opened by chanjarster on 2022-03-24, closed on 2022-04-02
- Labels: Client: Python, Issue: Bug
- Fix commit: 41451ff5ee33257aeaf1a4abfed9f6ae861dd982

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

oas.yaml ( notice with multiple `allOf` and with a CJK title):

```yaml
openapi: 3.0.2
info:
  title: foo
  version: v1
  description: 'foo'
servers:
  - url: 'foo.com'
    description: 'foo'
tags:
  - name: foo
    description: 'foo'

paths:
  
  '/foos':
    get:
      summary: foo list
      operationId: foo-list
      tags:
        - foo
      responses:
        '200':
          description: good
 
components:

  schemas:
  
    Bar:
      allOf:
      - type: object
        title: 中文
        properties:
          data:
            type: object
      - type: object
        title: 中文
        properties:
          data2:
            type: object
```

config.yaml:

```yaml
projectName: foo
packageName: foo
packageVersion: "1.0"
```

##### openapi-generator version

<!-- which version of openapi-generator are you using, is it a regression? -->

5.4.0

##### OpenAPI declaration file content or url

see above

##### Generation Details

<!-- 
    Prefer CLI steps, including the language, libraries and various options. 
    Providing config-based settings allows for simpler testing across CLI and plugins. 
    For examples, see https://github.com/OpenAPITools/openapi-generator/tree/master/bin/configs
-->

##### Steps to reproduce

```bash
openapi-generator-cli  generate \
  --generator-name python \
  --config config.yaml \
  --output output \
  --input-spec oas.yaml 
```

got model file:

```
├── model
│   ├── 1.py
│   ├── __init__.py
│   └── bar.py
```

Look at file `1.py`, should be `model_1.py`.

It's content also has problem:

```python
class 1(ModelNormal):
```

Not a valid class name.

##### Related issues/PRs

<!-- has a similar issue/PR been reported/opened before? Please do a search in https://github.com/openapitools/openapi-generator/issues?utf8=%E2%9C%93&q=is%3Aissue%20 -->

##### Suggest a fix

<!-- if you can't fix the bug yourself, perhaps you can point to what might be
  causing the problem (line of code or commit), or simply make a suggestion -->
