# [BUG,JAVA] Model generation of array with uniqueItems=true is not working

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/18102
- Opened by MelleD on 2024-03-14, closed on 2024-03-14
- Labels: Issue: Bug
- Fix commit: 5ed2283e019231d525dd51f46b60a7c9d0fa8947

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

Currently no more sets are generated if uniqueItems=true is set.

##### openapi-generator version

7.4.0/latest

##### OpenAPI declaration file content or url

If you post the code inline, please wrap it with
```yaml
        stringSet:
          type: array
          uniqueItems: true
          items:
            type: string
        stringDefaultSet:
          type: array
          uniqueItems: true
          default:
            - A
            - B
          items:
            type: string
        stringEmptyDefaultSet:
          type: array
          uniqueItems: true
          default: []
          items:
            type: string
```
Out put is

```java
  @Valid
  private List<String> stringSet = new ArrayList<>();

  @Valid
  private List<String> stringDefaultSet = new ArrayList<>(Arrays.asList("A", "B"));

  @Valid
  private List<String> stringEmptyDefaultSet = new ArrayList<>();
```

##### Generation Details

Spring Boot Cloud

##### Steps to reproduce
