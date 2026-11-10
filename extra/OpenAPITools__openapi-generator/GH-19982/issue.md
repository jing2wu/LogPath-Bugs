# [BUG] Kotlin generator won't resolve $ref in responses and return Kotlin.Any

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/19982
- Opened by Kuchteq on 2024-10-27, closed on 2024-10-30
- Labels: Issue: Bug
- Fix commit: cbc64e86d33d5a2e1a3736b2d6fd8caadb665ac2

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
A sample yaml file whose response won't be turned into a type and instead, its client type will be Any:
```
openapi: 3.1.0
info:
  title: Bug Report API
  version: 1.0.0

paths:
  /bug-report:
    post:
      summary: Submit a bug report
      operationId: submitBugReport
      responses:
        '200':
          $ref: '#/components/responses/BugReportResponse'

components:
  responses:
    BugReportResponse:
      description: This should be generated
      content:
        application/json:
          schema:
            type: object
            properties:
              id:
                type: integer
              status:
                type: string
```
This on the other hand, will resolve as expected:

```
openapi: 3.1.0
info:
  title: Bug Report API
  version: 1.0.0

paths:
  /bug-report:
    post:
      summary: Submit a bug report
      operationId: submitBugReport
      responses:
        '200':
          description: Bug report successfully submitted
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BugReportResponse'

components:
  schemas:
    BugReportResponse:
      type: object
      properties:
        id:
          type: string
        status:
          type: string
```
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
First spec's output where the type cannot be determined:
```
    /**
     * Submit a bug report
     * 
     * @return void
     * @throws IllegalStateException If the request is not correctly configured
     * @throws IOException Rethrows the OkHttp execute method exception
     * @throws UnsupportedOperationException If the API returns an informational or redirection response
     * @throws ClientException If the API returns a client error response
     * @throws ServerException If the API returns a server error response
     */
    @Throws(IllegalStateException::class, IOException::class, UnsupportedOperationException::class, ClientException::class, ServerException::class)
    fun submitBugReport() : Unit {

```
Second spec where the type is correctly inferred:
```
    /**
     * Submit a bug report
     * 
     * @return BugReportResponse or null
     * @throws IllegalStateException If the request is not correctly configured
     * @throws IOException Rethrows the OkHttp execute method exception
     * @throws UnsupportedOperationException If the API returns an informational or redirection response
     * @throws ClientException If the API returns a client error response
     * @throws ServerException If the API returns a server error response
     */
    @Suppress("UNCHECKED_CAST")
    @Throws(IllegalStateException::class, IOException::class, UnsupportedOperationException::class, ClientException::class, ServerException::class)
    fun submitBugReport() : BugReportResponse? {
```
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. Eg:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

<!-- describe what is the question, suggestion or issue and why this is a problem for you. -->

##### openapi-generator version

<!-- which version of openapi-generator are you using, is it a regression? -->

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

openapi-generator-cli generate -i spec.yml -g kotlin -o gen --library jvm-okhttp4

## Comment by wing328 on 2024-10-28

```
components:
  responses:
    BugReportResponse:
      description: Bug report successfully submitted
      content:
        application/json:
          example:
            id: "12345"
            status: "submitted"

```

this doesn't contain the schema (compared with second one you provided that works)

## Comment by Kuchteq on 2024-10-28

Apologies, I've now corrected the example. I've also discovered that the generation works as expected if I specify the schema to be 3.0.3

## Comment by wing328 on 2024-10-28

can you please test with the latest master?

i did merge a PR related to how response reference is handled.

https://oss.sonatype.org/content/repositories/snapshots/org/openapitools/openapi-generator-cli/7.10.0-SNAPSHOT/

## Comment by Kuchteq on 2024-10-28

Tested it by building straight off master and the client's type still gets generated as Any, with the difference now that the models actually get generated in the models directory so there is improvement.

## Comment by wing328 on 2024-10-29

@Kuchteq thanks for the details.

I've filed #19992 to fix the issue.
