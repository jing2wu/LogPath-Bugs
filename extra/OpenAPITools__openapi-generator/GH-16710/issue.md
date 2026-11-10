# [BUG] [Java] schema with oneOfs will generated model-code where first entry will match all others

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/16710
- Opened by skwakman on 2023-10-03, closed on 2023-11-07
- Labels: Issue: Bug
- Fix commit: c301004b7e5956f4bdaab2dfc9a57ade45fddbd8

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

Given an OpenAPI schema containing a component with several oneOf's, in which each oneOf entry has a unique 'type' value. Here's a partial example:
```json
{
  "components": {
    "schemas": {
      "ResponseContent": {
        "discriminator": {
          "propertyName": "type"
        },
        "oneOf": [
          {
            "$ref": "#/components/schemas/Title"
          },
          {
            "$ref": "#/components/schemas/Subtitle"
          },
          {
            "$ref": "#/components/schemas/Paragraph"
          }
        ]
      },
      "Title": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": [
              "title"
            ]
          }
        }
      },
      "Subtitle": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": [
              "subtitle"
            ]
          }
        }
      },
      "Paragraph": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": [
              "paragraph"
            ]
          }
        }
      }
    }
  }
}
```

Using the 7.0.1 java generator, the above schema will generate this Title model:
```java
public class Title {
  public enum TypeEnum {
    TITLE("title"),
    
    SUBTITLE("subtitle"),
    
    PARAGRAPH("paragraph");

// ...
public static TypeEnum fromValue(String value) {
      for (TypeEnum b : TypeEnum.values()) {
        if (b.value.equals(value)) {
          return b;
        }
      }
      throw new IllegalArgumentException("Unexpected value '" + value + "'");
    }
}
```
This indicates that the 7.0.1 java generator generates model code in which the first entry in the oneOf will match all the other entries. In the above case, the generated `Title` class matches with the typeEnum of `title`, `subtitle` and `paragraph`. This will cause the model to never be able to deserialize properly, as there are multiple options to deserialize json with `type: 'subtitle'` (because both Title and Subtitle classes match will it).

This did work properly in openapi-generator 6.6.0.

##### openapi-generator version

Issue observed in 7.0.1. It worked properly in 6.6.0.

##### OpenAPI declaration file content or url

See https://github.com/skwakman/openapi-generator-java-issue/blob/main/src/main/resources/example-schema.json . 

##### Generation Details

See https://github.com/skwakman/openapi-generator-java-issue/blob/main/build.gradle.kts

##### Steps to reproduce

I've made an example project illustrating the issue.

1. Check out https://github.com/skwakman/openapi-generator-java-issue
2. run `./gradlew openApiGenerate`
3. See the generated code for `Title` in `build/generate-resources/main/src/main/java/com/example/api/model/Title.java`. Its 'TypeEnum' matches with all the type values of the other components. The code for the other components (for instance in build/generate-resources/main/src/main/java/com/example/api/model/Subtitle.java) show that they only match for their specific type value.
4. Run the project's Main class in `src/main/java` to see what problem this causes: Jackson is not able to deserialize a Subtitle, because both Title and Subtitle classes match.

Change the version of openapi-generator in `build.gradle.kts` to 6.6.0, run `./gradlew clean` and run steps 2-4 again. The `Title` class will contain the correct TypeEnum values.

##### Suggest a fix

There's probably a bug somewhere in the java generator, introduced since 7.0.1.

## Comment by wing328 on 2023-10-05

> There's probably a bug somewhere in the java generator, introduced since 7.0.1.

I wonder if you can do a `git bisect` to identify the commit causing the issue.

## Comment by skwakman on 2023-10-05

@wing328 this bug was introduced in this commit: https://github.com/OpenAPITools/openapi-generator/commit/1561c339665212757799d1802f3c156b797360fd .
The issue seems to be originating from the `mergeProperties` method introduced in this commit. I'm not entirely sure what's going on.. maybe the problem is that this new method is applied to all oneOf situations, where it should only apply to oneOf's inside `included.array.items`?

## Comment by wing328 on 2023-11-05

cc @l3ender author of https://github.com/OpenAPITools/openapi-generator/commit/1561c339665212757799d1802f3c156b797360fd

@martin-mfg just filed a fix. I'll test and merge later this coming week. Thanks @martin-mfg for the PR.
