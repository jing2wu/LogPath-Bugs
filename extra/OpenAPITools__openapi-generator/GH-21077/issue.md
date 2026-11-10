# [BUG] [GOLANG] Generating client with array query parameters with defaults

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/21077
- Opened by gwd on 2025-04-11, closed on 2025-10-27
- Labels: Issue: Bug
- Fix commit: a4d05b38f57b13c1fb0b6581fb812dee69afa546

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [ ] Have you validated the input using an OpenAPI validator ([example](https://apitools.dev/swagger-parser/online/))?
- [ ] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?

##### Description

I've got some query parameters that are arrays of strings, and have default values listed:

```json
         {
            "description": "Data to include in response",
            "explode": false,
            "in": "query",
            "name": "include",
            "schema": {
              "default": [
                "userstats"
              ],
              "description": "Data to include in response",
              "items": {
                "enum": [
                  "word",
                  "userstats"
                ],
                "type": "string"
              },
              "type": [
                "array",
                "null"
              ]
            }
          }
```

```json
        {
            "description": "Data to include in response.  'analysis' requires a userid to be specified.",
            "explode": false,
            "in": "query",
            "name": "include",
            "schema": {
              "default": [
                "title",
                "text"
              ],
              "description": "Data to include in response.  'analysis' requires a userid to be specified.",
              "items": {
                "enum": [
                  "cguid",
                  "title",
                  "text",
                  "analysis"
                ],
                "type": "string"
              },
              "type": [
                "array",
                "null"
              ]
            }
          },
 ```

I would think "default values" means "values that the server will use if nothing is provided"; but the generator seems to try to fill in these values.  Unfortunately it generates syntactically invalid Go code:

```go
	if r.include != nil {
		parameterAddToHeaderOrQuery(localVarQueryParams, "include", r.include, "form", "csv")
	} else {
		var defaultValue []string = [userstats] // BUG: Should be {"userstats"}
		r.include = &defaultValue
	}
```

```go
	if r.include != nil {
		parameterAddToHeaderOrQuery(localVarQueryParams, "include", r.include, "form", "csv")
	} else {
		var defaultValue []string = ["title","text"] // BUG: Should be {"title","text"}
		r.include = &defaultValue
	}
```

##### openapi-generator version

```
$ openapi-generator version
7.12.0
```

##### OpenAPI declaration file content or url

https://api-dev.laleolanguage.com/openapi.json

##### Generation Details

```
openapi-generator generate -i https://api-dev.laleolanguage.com/openapi.json -g go -o apiclient
```

##### Steps to reproduce

Run the above command; the resulting code will not compile.

## Comment by jedkass on 2025-05-18

@gwd Having the same issue! Have you found a workaround? Do you know if an earlier version doesn't have this issue?

## Comment by gwd on 2025-05-19

@jedkass My workaround was just to document the default values in the documentation, rather than specifying them in the spec.  Nor have I tried it against `master` or any other version, so don't know if it's ever worked.

Hopefully someday I'll have time to come back and submit a PR that will include a test and a fix, but just not a priority at the minute.

## Comment by ranjanprasad1996 on 2025-06-29

@gwd Facing the same issue. Any timeline on when this will be fixed?

The spec is usually generated automatically through FastAPI, so manually editing would be difficult
