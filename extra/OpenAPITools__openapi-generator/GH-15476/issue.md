# [BUG,python-nextgen] Cannot handle query parameters with non-ref enums

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/15476
- Opened by robertschweizer on 2023-05-11, closed on 2023-07-13
- Labels: Client: Python, Issue: Bug
- Fix commit: 1531ad48d0f5ed03036d5253e60cd5077d0d90ad

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

https://github.com/OpenAPITools/openapi-generator/pull/15278 does not seem to work correctly.

The below schema creates the function signature, one of them an enum, the other a string:

```py
query_param_with_named_enum : QueryParamEnum, query_param_without_named_enum : StrictStr
```

But still tries to access both values with `.value`:

```py
        # process the query parameters
        _query_params = []
        if _params.get('query_param_with_named_enum') is not None:  # noqa: E501
            _query_params.append(('queryParamWithNamedEnum', _params['query_param_with_named_enum'].value))

        if _params.get('query_param_without_named_enum') is not None:  # noqa: E501
            _query_params.append(('queryParamWithoutNamedEnum', _params['query_param_without_named_enum'].value))
```

##### openapi-generator version

6.6.0

##### OpenAPI declaration file content or url

```yaml
openapi: 3.0.1
info:
  title: ""
  version: ""
paths:
  /test/endpoint:
    get:
      parameters:
        - name: queryParamWithNamedEnum
          in: query
          required: true
          schema:
            $ref: '#/components/schemas/QueryParamEnum'
        - name: queryParamWithoutNamedEnum
          in: query
          required: true
          schema:
            type: string
            enum:
              - ValueA
              - ValueB
      responses:
        200:
          description: OK
components:
  schemas:
    QueryParamEnum:
      type: string
      enum:
        - ValueC
        - ValueD
```

##### Related issues/PRs

https://github.com/OpenAPITools/openapi-generator/pull/15133
https://github.com/OpenAPITools/openapi-generator/pull/15278

##### Suggest a fix

Short-term: Do not use `.value` on raw string.

Long-term: Restrict the allowed values for non-ref enums somehow, maybe with a custom model or the [literal type](https://docs.pydantic.dev/latest/usage/types/#literal-type). This might be breaking for some users.

## Comment by dlange-hima on 2023-07-10

The big question is: Why is "isEnumRef" in the parsed Java-Model true if the enum is inline? I will try to understand and locate the source of this problem.. bear with me, because I haven't coded in Java in a long time ;)

## Comment by dlange-hima on 2023-07-10

Apparently there are three attributes:
`public boolean isEnum; // true if the enum is defined inline`
`public boolean isInnerEnum; // Enums declared inline will be located inside the generic model, changing how the enum is referenced in some cases.`
`private boolean isEnumRef; // true if it's a reference to an enum`

Currently 'queryParamWithNamedEnum' evaluates to isEnum = false , isInnerEnum = false and isEnumRef = true
Currently 'queryParamWithoutNamedEnum' evaluates to isEnum = true, isInnerEnum = true and isEnumRef = true

I think the problem is, that in DefaultCodegen.java between '//Inline enum case:' and '//Referenced enum case:' the result of getReferencedSchema is not checked wether or not a reference was actually resolved. This leads to every enum being treated as reference..
