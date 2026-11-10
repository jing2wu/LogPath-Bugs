# [BUG] [ExampleGenerator] Generated examples from String type with `date` format are in the wrong format (extra T00:00:00.000+00:00)

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/17494
- Opened by acouvreur on 2023-12-29, closed on 2024-01-10
- Labels: Issue: Bug
- Fix commit: 9b62b9bb057dccfdc27555323d8b56a4c7fb5b34

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

When providing an example to a type `string` property with format `date`, the generated example is in the wrong format.

__Current _(undesired)_ behavior:__

Consider the following schema:
```yaml
components:
  schemas:
    DateSchema:
      type: object
      properties:
        date_with_example:
          type: string
          format: date
          example: 2024-01-01
        date_without_example:
          type: string
          format: date
```

I'd expect the generated example to look like:

```json
{
  "date_with_example" : "2024-01-01",
  "date_without_example" : "2000-01-23"
}
```

However, it currently generates the following:
```json
{
  "date_with_example" : "2024-01-01T00:00:00.000+00:00",
  "date_without_example" : "2000-01-23"
}
```

*Note: the date without example refers to the current behavior in using a default predetermined value:*

https://github.com/OpenAPITools/openapi-generator/blob/a5d3fb4f601e4bced19f39cb6d82799a71531282/modules/openapi-generator/src/main/java/org/openapitools/codegen/examples/ExampleGenerator.java#L254C10-L255

__Why is this behavior happening?__

This issue is happening because how swagger-core is handling `DateSchema` classes.

As you can see, this PR tried to solve the issue directely in swagger-core: https://github.com/swagger-api/swagger-core/pull/4046

So what's happening is that the model for a date format resolves to a `DateSchema` which gets parsed as a `java.util.Date` and gets printed using it's `toString()` method.

![image](https://github.com/OpenAPITools/openapi-generator/assets/22034450/ceef7059-b90f-4e16-91bb-7e07a90c328a)


##### openapi-generator version

master a5d3fb4f601e4bced19f39cb6d82799a71531282

##### OpenAPI declaration file content or url

```yaml
openapi: 3.0.2
info:
  version: 1.0.0
  title: OpenAPI Petstore
  license:
    name: Apache-2.0
paths:
  /generate_from_response_schema_with_date_format:
    get:
      operationId: generateFromResponseSchemaWithDateFormat
      responses:
        '200':
          description: successful operation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DateSchema'
components:
  schemas:
    DateSchema:
      type: object
      properties:
        date_with_example:
          type: string
          format: date
          example: 2024-01-01
        date_without_example:
          type: string
          format: date
```

##### Generation Details

Running `ExampleGeneratorTest.java`

##### Steps to reproduce

Apply the following patch which adds the test case for example generation on date format.

```patch
Subject: [PATCH] Add failing test case to ExampleGenerator for date format
---
Index: modules/openapi-generator/src/test/resources/3_0/example_generator_test.yaml
IDEA additional info:
Subsystem: com.intellij.openapi.diff.impl.patch.CharsetEP
<+>UTF-8
===================================================================
diff --git a/modules/openapi-generator/src/test/resources/3_0/example_generator_test.yaml b/modules/openapi-generator/src/test/resources/3_0/example_generator_test.yaml
--- a/modules/openapi-generator/src/test/resources/3_0/example_generator_test.yaml	(revision a5d3fb4f601e4bced19f39cb6d82799a71531282)
+++ b/modules/openapi-generator/src/test/resources/3_0/example_generator_test.yaml	(date 1703871594752)
@@ -26,6 +26,16 @@
               schema:
                 type: string
                 example: primitive type example value
+  /generate_from_response_schema_with_date_format:
+    get:
+      operationId: generateFromResponseSchemaWithDateFormat
+      responses:
+        '200':
+          description: successful operation
+          content:
+            application/json:
+              schema:
+                $ref: '#/components/schemas/DateSchema'
   /generate_from_response_schema_with_array_of_model:
     get:
       operationId: generateFromResponseSchemaWithArrayOfModel
@@ -63,6 +73,16 @@
                 $ref: '#/components/schemas/ExampleSchema'
 components:
   schemas:
+    DateSchema:
+      type: object
+      properties:
+        date_with_example:
+          type: string
+          format: date
+          example: 2024-01-01
+        date_without_example:
+          type: string
+          format: date
     StringSchema:
       type: string
       example: string schema example value
Index: modules/openapi-generator/src/test/java/org/openapitools/codegen/ExampleGeneratorTest.java
IDEA additional info:
Subsystem: com.intellij.openapi.diff.impl.patch.CharsetEP
<+>UTF-8
===================================================================
diff --git a/modules/openapi-generator/src/test/java/org/openapitools/codegen/ExampleGeneratorTest.java b/modules/openapi-generator/src/test/java/org/openapitools/codegen/ExampleGeneratorTest.java
--- a/modules/openapi-generator/src/test/java/org/openapitools/codegen/ExampleGeneratorTest.java	(revision a5d3fb4f601e4bced19f39cb6d82799a71531282)
+++ b/modules/openapi-generator/src/test/java/org/openapitools/codegen/ExampleGeneratorTest.java	(date 1703871597569)
@@ -39,6 +39,35 @@
         assertEquals("200", examples.get(0).get("statusCode"));
     }
 
+    @Test
+    public void generateFromResponseSchemaWithDateFormat() {
+        OpenAPI openAPI = TestUtils.parseFlattenSpec("src/test/resources/3_0/example_generator_test.yaml");
+
+        new InlineModelResolver().flatten(openAPI);
+
+        ExampleGenerator exampleGenerator = new ExampleGenerator(openAPI.getComponents().getSchemas(), openAPI);
+        Set<String> mediaTypeKeys = new TreeSet<>();
+        mediaTypeKeys.add("application/json");
+        List<Map<String, String>> examples = exampleGenerator.generateFromResponseSchema(
+                "200",
+                openAPI
+                        .getPaths()
+                        .get("/generate_from_response_schema_with_date_format")
+                        .getGet()
+                        .getResponses()
+                        .get("200")
+                        .getContent()
+                        .get("application/json")
+                        .getSchema(),
+                mediaTypeKeys
+        );
+
+        assertEquals(1, examples.size());
+        assertEquals("application/json", examples.get(0).get("contentType"));
+        assertEquals(String.format(Locale.ROOT, "{%n  \"date_with_example\" : \"2024-01-01\",%n  \"date_without_example\" : \"2000-01-23\"%n}"), examples.get(0).get("example"));
+        assertEquals("200", examples.get(0).get("statusCode"));
+    }
+
     @Test
     public void generateFromResponseSchemaWithNoExample() {
         OpenAPI openAPI = TestUtils.parseFlattenSpec("src/test/resources/3_0/example_generator_test.yaml");

```

##### Related issues/PRs

https://github.com/swagger-api/swagger-core/pull/4046
https://github.com/OpenAPITools/openapi-generator/issues/15342
