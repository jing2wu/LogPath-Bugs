# Map additionalProperties sometimes missing with interface value

- Issue: https://github.com/victools/jsonschema-generator/issues/261
- Opened by dloibl on 2022-06-22, closed on 2022-06-24
- Labels: bug
- Fix commit: 7db0d1acbf48738ec207a3c580c3505dc8bb1c86

## Report

Hi,

I have an issue with Maps wit Option.MAP_VALUES_AS_ADDITIONAL_PROPERTIES, when the Map Value type is 
not a concrete class. In my case we use a custom subTypeResolver picking the concrete implementation from @JsonDeserialize or @JsonSerialize annotations. Using the concrete Impl (Map<String, BImpl>) works as expected.
Is there something I miss, or should the AdditionalPropertiesModule use the subTypeResolver as expected?

```java
@JsonSerialize(as = AImpl.class)
public interface A {
    Map<String, B> getMap(); 
}

@JsonSerialize(as = BImpl.class)
public interface B {
    String getName();
}
```

**Outcome**:
```json
"map" : {
  "type" : "object",
  "additionalProperties" : { }
},
``` 
**Expected**:
```json
"map" : {
  "type" : "object",
  "additionalProperties" : { 
     "name": { "type": "string"}
   }
}
```

## Comment by CarstenEnglert on 2022-06-23

Hi @dloibl,

Thanks for reporting the bug.
I can reproduce the issue and see that it works correctly when `Option.DEFINITIONS_FOR_ALL_OBJECTS` or `Option.INLINE_ALL_SCHEMAS` is enabled.
I'll have to investigate further how to fix this properly.

## Comment by CarstenEnglert on 2022-06-24

Hi @dloibl,

I'm happy to let you know that this is now fixed in the release [v4.25.0](https://github.com/victools/jsonschema-generator/releases/tag/v4.25.0).

For completeness' sake though, the expected output in your given example would look like this:
```json
"map" : {
  "type" : "object",
  "additionalProperties" : {
    "type": "object",
    "properties": {
      "name": { "type": "string"}
    }
  }
}
```
