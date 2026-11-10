# [Bug]: @Schema with format = "uri-reference" on java.net.URI field resolves to format: uri when using ModelConverters

- Issue: https://github.com/swagger-api/swagger-core/issues/5185
- Opened by VadimKobyakov on 2026-05-28, closed on 2026-07-20
- Labels: Bug, backlog
- Fix commit: 6f799eedee6110b7deb82cd093b663db14d06654

## Report

## Description of the problem/issue

When annotating a field of the class java.net.URI with `@Schema(format="uri-reference")` and then resolving the class to which this field belongs by using ModelConverters.getInstance().read() or any of the read methods (Note: not using the openApi31 option) then the output ResolvedSchema or similar will map it to format: uri.

This can cause Open Api linters to throw warnings or errors when combined with an example field of a non-absolute URI (which is allowed by uri-reference, but not uri)

## Affected Version

2.2.47

Earliest version the bug appears in (if known):  
2.0.3

## Steps to Reproduce

<!-- Provide a step-by-step list on how to reproduce the issue.
Include any relevant OpenAPI definitions, configuration, or code snippets. -->

1. Create any dummy class for testing.
2. Create a field of java.net.URI and annotate it with `@Schema(format="uri-reference")`
3. Resolve it to a Schema or similar
4. Read the format of your field property

Example:
```java
//Step 1
private class UriExample{
     //Step 2
     @io.swagger.v3.oas.annotations.media.Schema(format = "uri-reference")
     public URI uriReferenceValue;
}
//Step 3
final ResolvedSchema model = ModelConverters.getInstance().readAllAsResolvedSchema(UriExample.class);
//Step 4
System.out.println(((Schema)model.schema.getProperties().get("uriReferenceValue")).getFormat());
```
The printed output will be "uri", not "uri-reference"

## Expected Behavior

uri-reference is a valid format specified by OpenApi (see [OpenApi Format Registry](https://spec.openapis.org/registry/format/uri-reference.html)) 
The functionality specified by uri-reference and [RFC 3986 Section 4](https://www.rfc-editor.org/info/rfc3986/#section-4) is also supported by [java.net.URI](https://docs.oracle.com/javase/8/docs/api/java/net/URI.html#:~:text=URI%20syntax%20and%20components). Therefore, as it is valid to set a URI field to a non-absolute URI, we expect it to map correctly in the OpenApiSpec when declaring the format to explicitly use uri-reference.

Additionally, the documentation for `@Schema` claims that format `Provides an optional override for the format.`.
Therefore it is expected that
 `@Schema(format="uri-reference") URI myUri ` 
maps to
```yaml
myUri:
  type: string
  format: uri-reference
```
when resolving with ModelConverters.

## Actual Behavior

<!-- What actually happened instead? -->
When using the aforementioned setup and reading such a field with ModelConverters.getInstance(), the Resolved Schema gets assigned the format uri instead of the custom override

## Cause

The bug is caused in `io.swagger.v3.core.util.PrimitiveType.` at the method `fromTypeAndFormat(Type type, String format)` (line 446)

```java
public static PrimitiveType fromTypeAndFormat(Type type, String format) {
        final Class<?> raw = TypeFactory.defaultInstance().constructType(type).getRawClass();
        final Collection<PrimitiveType> keys = MULTI_KEY_CLASSES.get(raw);
        if (keys == null || keys.isEmpty() || StringUtils.isBlank(format)) {
            return fromType(type);
        } else {
            return keys
                .stream()
                .filter(t -> t.getCommonName().equalsIgnoreCase(format))
                .findAny()
                .orElse(null);
        }
    }
```
The method gets a raw Class from the type, which happens to be java.net.URI. It then searches for this raw Type in MULTI_KEY_CLASSES, a map containing enum-entries of the same class but different formats. As there is no URI in this Map, keys becomes null and `fromType(type)` is invoked. This in turn ignores the format and resolves the OpenApi Format from java.net.URI directly, which happens to be 
```yaml
myUri:
  type: string
  format: uri
```

## Suggested Fix
Introduce a new PrimitiveType entry `URI_REFERENCE` that handles "uri-reference" explcitly 

```java
URI_REFERENCE(java.net.URI.class, "uri-reference") {
        @Override
        public Schema createProperty() {
            return new StringSchema().format("uri-reference");
        }
        @Override
        public Schema createProperty31() {
            return new JsonSchema().typesItem("string").format("uri-reference");
        }
    },

```
and add both URI and URI_REFERENCE to MULTI_KEY_CLASSES.
```java
addMultiKeys(multiKeyClasses, URI, java.net.URI.class);
addMultiKeys(multiKeyClasses, URI_REFERENCE, java.net.URI.class);
```

**I can provide a PR with the fix with tests** (I have already created a local branch and can push it)

## Checklist

- [x] I have searched the [existing issues](https://github.com/swagger-api/swagger-core/issues) and this is not a duplicate.
- [x] I have provided sufficient information for maintainers to reproduce the issue.
