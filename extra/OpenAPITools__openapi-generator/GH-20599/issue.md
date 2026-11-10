# [BUG] [GO] Unused imports "fmt" and "bytes" when generateMarshalJSON=false and generateUnmarshalJSON=false

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/20599
- Opened by raphoester on 2025-02-05, closed on 2025-12-10
- Labels: Issue: Bug
- Fix commit: 8f8001ea1a386e9c9474b000df503039c8b79701

## Report

##### Description

The bug happens when running the Go generation with both generateUnmarshalJSON and generateMarshalJSON flags set to false.

Some of the resulting model files contain unused imports to `bytes` and `fmt`. 
Unused imports are disallowed by the Go language, which results in the client being unable to compile

##### openapi-generator version

Version : openapi-generator-cli 7.12.0-SNAPSHOT
Commit : 9a9c108
Built: -999999999-01-01T00:00:00+18:00

##### OpenAPI declaration file content or url

https://api.reepay.com/openapi.json

##### Generation Details

```
docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate \
		-i <ref> \
		-g go \
		-o /local/out \
		--additional-properties=generateMarshalJSON=false,generateUnmarshalJSON=false
```

##### Steps to reproduce

command above on any valid input 

##### Related issues/PRs

-
##### Suggest a fix

I guess checking for unused imports after the generation, and then deleting them should do it

## Comment by raphoester on 2025-02-05

I have found a temporary fix : run `goimports -w .` to fix the broken imports. 
But ideally the broken imports should not be in the generated files in the first place
