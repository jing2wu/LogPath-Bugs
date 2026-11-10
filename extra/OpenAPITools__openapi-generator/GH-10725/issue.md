# [BUG] [Core] ByteArray is marked as String at the same time

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/10725
- Opened by ityuhui on 2021-10-28, closed on 2021-11-01
- Labels: Issue: Bug
- Fix commit: fe90d9c42606ff19abc53e22408bb9460fe6e122

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

Hi @wing328 

I think some recent change of `openapi-generator core` breaks a behavior:  

e.g.
```
        "data": {
          "additionalProperties": {
            "format": "byte",
            "type": "string"
          },
```

At before (on September 16, 2021), the `data` will be marked as "isString" : false, "isByteArray" : true,
but today I found it will be marked as "isString" : true, "isByteArray" : true,

Could you please give me some suggestions/clues about this problem ? Thanks.

Involve @zhemant 

##### openapi-generator version

<!-- which version of openapi-generator are you using, is it a regression? -->
master

##### OpenAPI declaration file content or url

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

```shell
java -DdebugModels -jar modules/openapi-generator-cli/target/openapi-generator-cli.jar generate -i /path/swagger.json  -g c    -o ../output --skip-validate-spec > log.txt
```
<!-- 
    Prefer CLI steps, including the language, libraries and various options. 
    Providing config-based settings allows for simpler testing across CLI and plugins. 
    For examples, see https://github.com/OpenAPITools/openapi-generator/tree/master/bin/configs
-->



##### Steps to reproduce

<!-- unambiguous set of steps to reproduce the bug.-->

##### Related issues/PRs

<!-- has a similar issue/PR been reported/opened before? Please do a search in https://github.com/openapitools/openapi-generator/issues?utf8=%E2%9C%93&q=is%3Aissue%20 -->

https://github.com/OpenAPITools/openapi-generator/pull/10034

##### Suggest a fix

<!-- if you can't fix the bug yourself, perhaps you can point to what might be
  causing the problem (line of code or commit), or simply make a suggestion -->

## Comment by wing328 on 2021-10-30

Can you please do a `git bisect` to identify the commit causing the issue?

## Comment by ityuhui on 2021-11-01

Thank you @wing328 . It's a good idea !

I found the commit(https://github.com/OpenAPITools/openapi-generator/pull/10334/files) that caused this issue. And can succeed to fix it by https://github.com/OpenAPITools/openapi-generator/pull/10334/files#r739936935

Could you and @spacether @agilob @therve check my fix solution ? Or may I submit a PR directly for your review ?

## Comment by spacether on 2021-11-01

Can you please submit a PR for review?

## Comment by ityuhui on 2021-11-01

> Can you please submit a PR for review?

Sure.
