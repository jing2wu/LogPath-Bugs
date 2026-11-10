# [BUG,JAVA] Client files generated for object with multiple `oneOf` items only have last entry

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/12545
- Opened by l3ender on 2022-06-06, closed on 2023-05-31
- Labels: Issue: Bug
- Fix commit: 1561c339665212757799d1802f3c156b797360fd

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [x] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

When generating Java client files from a spec which includes multiple `oneOf` entries, only the last entry in the `oneOf` list is used.

The generated class for contains an enum of only the last entry in `oneOf` list:

```java
public class BuildsResponseIncludedInner {
  public enum TypeEnum {
    BUILDICONS("buildIcons"); // <----- only single enum present (last entry in `oneOf` list from spec)
    // ...
  }
}
```

##### openapi-generator version

I am seeing the issue on latest stable version as well as 7.0.0-SNAPSHOT and on the latest of master.

##### OpenAPI declaration file content or url

I am working with the Apple App Store Connect API. The full specification (can be downloaded [here](https://developer.apple.com/documentation/appstoreconnectapi)) is quite large, so I have stripped out unused APIs and am using this trimmed spec file: [app_store_connect_api_1.8_openapi-trimmed.json.txt](https://github.com/OpenAPITools/openapi-generator/files/8848342/app_store_connect_api_1.8_openapi-trimmed.json.txt)

The relevant section starts at line 4806:

```json
      "BuildsResponse" : {
        "type" : "object",
        "title" : "BuildsResponse",
        "properties" : {
          "data" : {
            "type" : "array",
            "items" : {
              "$ref" : "#/components/schemas/Build"
            }
          },
          "included" : {
            "type" : "array",
            "items" : {
              "oneOf" : [ {
                "$ref" : "#/components/schemas/PrereleaseVersion"
              }, {
                "$ref" : "#/components/schemas/BetaGroup"
              }, {
                "$ref" : "#/components/schemas/BetaBuildLocalization"
              }, {
                "$ref" : "#/components/schemas/AppEncryptionDeclaration"
              }, {
                "$ref" : "#/components/schemas/BetaAppReviewSubmission"
              }, {
                "$ref" : "#/components/schemas/App"
              }, {
                "$ref" : "#/components/schemas/BuildBetaDetail"
              }, {
                "$ref" : "#/components/schemas/AppStoreVersion"
              }, {
                "$ref" : "#/components/schemas/BuildIcon"
              }, {
                "$ref" : "#/components/schemas/BuildBundle"
              } ]
            }
          },
```

##### Generation Details

Generation command:

```bash
java -jar ~/Desktop/openapi-generator-cli-7.0.0-20220526.055920-1.jar generate -g java -c src/main/resources/openapi-config.json -i src/main/resources/app_store_connect_api_1.8_openapi-trimmed.json
```

Config file used:
```json
{
	"groupId": "com.apple",
	"artifactId": "appstoreconnect",
	"artifactVersion": "1.8.0",
	"artifactDescription": "App Store Connect API",
	"artifactUrl": "https://developer.apple.com/documentation/appstoreconnectapi",
	"invokerPackage": "com.apple.appstoreconnect",
	"apiPackage": "com.apple.appstoreconnect.api",
	"modelPackage": "com.apple.appstoreconnect.model",
	"library": "apache-httpclient"
}

```

##### Steps to reproduce

1. Download above trimmed API spec and create config json matching above.
2. Run command generation
3. Observe generated BuildsResponseIncludedInner.java class.

##### Related issues/PRs

https://github.com/OpenAPITools/openapi-generator/issues/9241 may be related (unsure).

##### Suggest a fix

All `oneOf` items should be used as valid types for the generated classes.

## Comment by onurkybsi on 2022-08-23

Hi! The fix is ready ? I've been waiting for this fix for a while. Thanks!
