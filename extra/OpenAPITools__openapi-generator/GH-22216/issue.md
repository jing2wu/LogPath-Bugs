# [BUG] [Kotlin] overriden variables are not generated with 'override' keyword

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/22216
- Opened by Sylvain-maillard on 2025-10-23, closed on 2026-07-20
- Labels: Issue: Bug
- Fix commit: f861dffde39d4539a637fd20378e4d8eb635249d

## Report

#### Bug Report Checklist

- [X] Have you provided a full/minimal spec to reproduce the issue?
- [X] Have you validated the input using an OpenAPI validator?
- [X] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [X] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. E.g.:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

<!-- describe what is the question, suggestion or issue and why this is a problem for you. -->

- Given a openapi spec containing a Schema (Car) that inherits from another (Vehicle) using `discriminator` and `allOf`, 
- and the Schema `Vehicle` define a property "x" of type "object", 
- and the Schéma `Car` redefining the property by specializing the type to "string"
- when I generate the code, then the class `Car` won't compile because the redefined var `x` does not have the modifier `override`. 

I expect the attributes of `Car` to have the override keyword as it is valid in kotlin to do that.

##### openapi-generator version

<!-- which version of openapi-generator are you using, is it a regression? -->
Tested on latest v7.17.0-SNAPSHOT.

##### OpenAPI declaration file content or url

see https://gist.github.com/Sylvain-maillard/fe3d0e25d4b21e6acfee8b0544da12e8

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
Issue was reproduce using docker without specific parameters except the `kotlin` generator.

```bash
docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate -i /local/issue.yaml -g kotlin -o /local/generated
```

##### Steps to reproduce

<!-- unambiguous set of steps to reproduce the bug.-->
- generate the kotlin code using the provided yaml 
- the overriden attributes of class `Car` misses the `override` keyword.

##### Related issues/PRs

<!-- has a similar issue/PR been reported/opened before? Please do a search in https://github.com/openapitools/openapi-generator/issues?utf8=%E2%9C%93&q=is%3Aissue%20 -->

##### Suggest a fix

<!-- if you can't fix the bug yourself, perhaps you can point to what might be
  causing the problem (line of code or commit), or simply make a suggestion -->
I'have found a quick and dirty fix that rely on rescanning all schemas, looking for duplicate vars on each parents. 

I've added the code in `org.openapitools.codegen.languages.AbstractKotlinCodegen#postProcessAllModels` 

It's probably better to fix the issue when the `CodegenProperty` instances are created, but I didn't have time to dig in that.
