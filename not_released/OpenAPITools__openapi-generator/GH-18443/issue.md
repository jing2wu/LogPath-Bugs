# [BUG] [ExampleGenerator] Generated examples from nested composed schema types are missing (allOf of allOf)

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/18443
- Opened by phpinhei-te on 2024-04-20, closed on 2024-04-30
- Labels: Issue: Bug
- Fix commit: e36172090e4ed7c0658ec181a8217f392068c909

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))


##### Description

Nested composed schemas are missing generated examples for child schema types, only the parent schema examples get generated while child examples are ignored.

##### openapi-generator version

v7.5.0 and master [93f4323](https://github.com/OpenAPITools/openapi-generator/commit/93f43233645bdb57a0f57417955069b5a3dd6ae1)

##### OpenAPI declaration file content or url

While generating examples for `ExampleAllOfParentSchema` schema:
```yaml
components:
  schemas:
    ExampleSchema:
      type: object
      properties:
        example_schema_property:
          type: string
          example: example schema property value
    ExampleAllOfSchema:
      type: object
      allOf:
        - $ref: '#/components/schemas/ExampleSchema'
        - type: object
          properties:
            example_schema_property_composed:
              type: string
              example: example schema property value composed
    ExampleAllOfParentSchema:
      type: object
      allOf:
        - $ref: '#/components/schemas/ExampleAllOfSchema'
        - type: object
          properties:
            example_schema_property_composed_parent:
              type: string
              example: example schema property value composed parent
```

It is expected to have the following generated example:
```json
{
  "example_schema_property_composed_parent" : "example schema property value composed parent",
  "example_schema_property_composed" : "example schema property value composed",
  "example_schema_property" : "example schema property value"
}
```

However, `ExampleGenerator` provides the following:
```json
{
  "example_schema_property_composed_parent" : "example schema property value composed parent"
}
```

##### Generation Details
N/A

##### Steps to reproduce

Added new example to `example_generator_test.yaml`:
```diff
Index: modules/openapi-generator/src/test/resources/3_0/example_generator_test.yaml
IDEA additional info:
Subsystem: com.intellij.openapi.diff.impl.patch.CharsetEP
<+>UTF-8
===================================================================
diff --git a/modules/openapi-generator/src/test/resources/3_0/example_generator_test.yaml b/modules/openapi-generator/src/test/resources/3_0/example_generator_test.yaml
--- a/modules/openapi-generator/src/test/resources/3_0/example_generator_test.yaml	(revision 93f43233645bdb57a0f57417955069b5a3dd6ae1)
+++ b/modules/openapi-generator/src/test/resources/3_0/example_generator_test.yaml	(date 1713610291806)
@@ -81,6 +81,21 @@
             application/json:
               schema:
                 $ref: '#/components/schemas/ExampleAllOfSchema'
+  /generate_from_response_schema_with_array_of_allOf_composed_model:
+    get:
+      operationId: generateFromResponseSchemaWithAllOfModel
+      responses:
+        '200':
+          description: successful operation
+          content:
+            application/json:
+              schema:
+#                type: object
+#                properties:
+#                  schemas:
+#                type: array
+#                items:
+                $ref: '#/components/schemas/ExampleAllOfParentSchema'
   /generate_from_response_schema_with_anyOf_composed_model:
     get:
       operationId: generateFromResponseSchemaWithAnyOfModel
@@ -131,6 +146,15 @@
             example_schema_property_composed:
               type: string
               example: example schema property value composed
+    ExampleAllOfParentSchema:
+      type: object
+      allOf:
+        - $ref: '#/components/schemas/ExampleAllOfSchema'
+        - type: object
+          properties:
+            example_schema_property_composed_parent:
+              type: string
+              example: example schema property value composed parent
     ExampleAnyOfSchema:
       type: object
       anyOf:

```

Included unit test to `ExampleGeneratorTest.java` to test scenario:
```diff
Index: modules/openapi-generator/src/test/java/org/openapitools/codegen/ExampleGeneratorTest.java
IDEA additional info:
Subsystem: com.intellij.openapi.diff.impl.patch.CharsetEP
<+>UTF-8
===================================================================
diff --git a/modules/openapi-generator/src/test/java/org/openapitools/codegen/ExampleGeneratorTest.java b/modules/openapi-generator/src/test/java/org/openapitools/codegen/ExampleGeneratorTest.java
--- a/modules/openapi-generator/src/test/java/org/openapitools/codegen/ExampleGeneratorTest.java	(revision 93f43233645bdb57a0f57417955069b5a3dd6ae1)
+++ b/modules/openapi-generator/src/test/java/org/openapitools/codegen/ExampleGeneratorTest.java	(date 1713612240848)
@@ -210,6 +210,39 @@
         assertEquals("200", examples.get(0).get("statusCode"));
     }
 
+    @Test
+    public void generateFromResponseSchemaWithArrayAllOfComposedModel() {
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
+                        .get("/generate_from_response_schema_with_array_of_allOf_composed_model")
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
+        assertEquals(String.format(Locale.ROOT, "{\n" +
+                                                "  \"example_schema_property_composed_parent\" : \"example schema property value composed parent\",\n" +
+                                                "  \"example_schema_property_composed\" : \"example schema property value composed\",\n" +
+                                                "  \"example_schema_property\" : \"example schema property value\"\n" +
+                                                "}"), examples.get(0).get("example"));
+        assertEquals("200", examples.get(0).get("statusCode"));
+    }
+
     @Test
     public void generateFromResponseSchemaWithOneOfComposedModel() {
         OpenAPI openAPI = TestUtils.parseFlattenSpec("src/test/resources/3_0/example_generator_test.yaml");
```

##### Related issues/PRs

Simular to this:
https://github.com/OpenAPITools/openapi-generator/issues/17497
Seems like an edge case from the added implementation

##### Suggest a fix

Didn't go into detail yet, but most likely `ExampleGenerator:373` needs to consider the resolved schema to have `allOf/anyOf/oneOf`:
```java
        } else if (ModelUtils.isAllOf(schema) || ModelUtils.isAllOfWithProperties(schema)) {
            LOGGER.debug("Resolving allOf model '{}' to example", name);
            List<Schema> interfaces = schema.getAllOf();
            for (Schema composed : interfaces) {
                traverseSchemaProperties(mediaType, composed, processedModels, values);
                if (composed.get$ref() != null) {
                    String ref = ModelUtils.getSimpleRef(composed.get$ref());
                    Schema resolved = ModelUtils.getSchema(openAPI, ref);
                    if (resolved != null) {
                        traverseSchemaProperties(mediaType, resolved, processedModels, values);
                    }
                }
            }
            schema.setExample(values);
            return schema.getExample();
        }
```

If I have sometime during the week I will try to solve it myself.
