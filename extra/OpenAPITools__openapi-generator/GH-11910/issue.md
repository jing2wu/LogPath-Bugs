#  [BUG,kotlin,client,okhttp4] non-file parts are serialized as the string without Content-Type in multipart/form-data (variant of #7658 / #11289)

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/11910
- Opened by koscejev on 2022-03-18, closed on 2022-04-13
- Labels: Issue: Bug
- Fix commit: 7851dfe1488b026734c0930676c4c96251b419fd

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

Most of the investigation of this bug is based on code (including checking the latest master). The relevant code is still the same in latest master, so I didn't explicitly verify it.

I will provide PR with actual fix for at least the "okhttp4" and "okhttp3" libraries. The fix is verified on our project. Perhaps others can improve upon the fix to allow other libraries to handle this properly too.

##### openapi-generator version

5.4.0

##### OpenAPI declaration file content or url

Just for the reference, this is how our multipart request is defined (used to verify the fix). We don't actually have the `encoding` section, since it's supposed to default to "application/json" anyway, but I have verified it works with this section defined:

```yaml
requestBody:
  required: true
  content:
    multipart/form-data:
      schema:
        type: object
        required:
          - interaction
        properties:
          interaction:
            $ref: '#/components/schemas/InteractionWithRelatedDataDto'
          media:
            type: array
            items:
              type: string
              format: binary
      encoding:
        interaction:
          contentType: application/json
```

##### Generation Details

We're generating code using the following settings:
- skipFormModel = false
- library = jvm-okhttp4
- serializationLibrary = jackson
- enumPropertyNaming = UPPERCASE

##### Steps to reproduce

1. Generate client code based on OpenApi 3 spec with multipart request as defined above.
2. Send the corresponding request
3. Notice the request correctly has "Content-Type" header with value starting with "multipart/form-data"
4. Notice the request is incorrectly missing "Content-Type" header for all parts
5. Notice the request incorrectly contains the first part serialized via `toString()` instead of JSON

##### Related issues/PRs

PR: #11911
Related: #7658 and #11289
Also, #5284 is related, but seems to be outdated, since it works in 5.4.0 - maybe close it?

##### Suggest a fix

See PR above.
