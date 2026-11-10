# BUG properties of type Object do not have any type information when generating open api 3.1.0

- Issue: https://github.com/swagger-api/swagger-core/issues/4682
- Opened by Lorenzo-Bracci on 2024-06-03, closed on 2026-02-19
- Labels: Bug, P2, pull-request-welcome, backlog
- Fix commit: fe918cc9a1294c52116c1158acf2f6540657c812

## Report

## Problem
When generating OpenAPI 3.1.0 spec, properties with the java type `Object` do not have any type information in the generated open api but are instead empty. As an example assume the following java model:
```
private static class PojoUsingObjectField {
        private Object myField;

        public Object getMyField() {
            return myField;
        }

        public void setMyField(Object myField) {
            this.myField = myField;
        }
}
```
When generating open api for 3.0.1 the generated model would be:
```
PojoUsingObjectField:
  type: object
  properties:
    myField:
      type: object
```
But when generating open api 3.1.0 the generated model is:
```
PojoUsingObjectField:
  type: object
  properties:
    myField: {}
```

## Expected behaviour 
Same as in open api 3.0.1, properties have a `type` field with value `object`.

## Reproducer
The issues is reproduced in the following test (note that the test is successful if the model resolvers generate OAS3.0.1 instead):

```
    @Test(description = "Shows that type information in properties using a raw Object is lost when using oas 3.1.0")
    public void testModelUsingObjectTypedPropertyLosesTypeInformationForOas31() {

        String expectedYaml = "PojoUsingObjectField:\n" +
                "  type: object\n" +
                "  properties:\n" +
                "    myField:\n" +
                "      type: object";

        Map<String, io.swagger.v3.oas.models.media.Schema> stringSchemaMap = ModelConverters.getInstance(true).readAll(PojoUsingObjectField.class);
        // fails as the type: object will not be added for oas 3.1.0, instead we will have "myField: {}"
        SerializationMatchers.assertEqualsToYaml31(stringSchemaMap, expectedYaml);
    }

    private static class PojoUsingObjectField {
        private Object myField;

        public Object getMyField() {
            return myField;
        }

        public void setMyField(Object myField) {
            this.myField = myField;
        }
    }
```

## Investigation 

Looking at the `ModelResolver` code, it seems that the issue is the following: the model for a property with java type `Object` is generated using `PrimitiveType.OBJECT#createProperty` which creates a `io.swagger.v3.oas.models.media.Schema` with `type` set to `object` (i.e using oas 3.0.1 representation). Nevertheless in `ModelResolver#717` we clone this representation before further processing and because cloning is done by serializing and then deserializing using the jackson settings for oas 3.1.0 (which expects the property `types` to be used instead of `type`) this information is lost and the cloned schema has neither `type` nor `types` set

## Comment by YousefHaggy on 2024-11-22

Observing the same behavior, were you able to figure out a work around?

## Comment by JanMosigItemis on 2025-01-08

Hello everyone,

we recently switched to latest Spring Doc which comes with OpenAPI 3.1. by default and encountered a similar behavior. Digging into things, I found https://github.com/swagger-api/swagger-core/blob/1eb2774bb99dbf841cfb0c08f6baa44e4a7d1fee/modules/swagger-models/src/main/java/io/swagger/v3/oas/models/media/Schema.java#L2155

I suspect, the serialization uses toString und therefore omits "type" in 3.1. in favor of "types".

However, having read the spec, I do not understand, why "type" is omitted. Imo using "type" is perfectly fine, i. e. the toString method should include it.

Any thoughts on this?

## Comment by asperan on 2025-12-22

Hi, sorry for reviving this issue. I have the same problem, is there any work in progress?

## Comment by xeulbn on 2026-01-10

Hi,

I was able to reproduce this issue locally using the latest swagger-core.

I verified this locally with a minimal reproduction similar to the one described above and confirmed that
when using OAS 3.1 serialization, a property of raw Java type `Object` is rendered as `{}`,
while the same model produces `type: object` correctly under OAS 3.0.x.

From debugging, it seems that `PrimitiveType.OBJECT` only sets `schema.type = "object"`,
but in OAS 3.1 the serializer relies on `schema.types` (JSON Schema style).
As a result, during the clone / serialization process, the type information is lost.

I’m currently looking into a fix, possibly by synchronizing `type` → `types`
(either in `Schema#setType` or during model resolution for OAS 3.1).

If no one is currently working on this, would it be okay if I try to take a stab at this issue?

## Comment by daniel-kmiecik on 2026-02-19

The PR submitted by @xeulbn  has been successfully merged. The contribution updates the model resolution logic so that for raw Object properties the schema correctly includes type: object under OpenAPI 3.1.0. The fix will be available from the next release. Thanks again @xeulbn for your contribution!
