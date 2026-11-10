# [BUG] AllOf in openapi file causing generator stackoverflow 

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/12929
- Opened by jzendle on 2022-07-19, closed on 2023-07-06
- Labels: Issue: Bug
- Fix commit: 965eb2a02fd23f52d1d931b1684f56cc51553f7d

## Report

#### Bug Report Checklist

- [ yes] Have you provided a full/minimal spec to reproduce the issue?

attached test.yaml.txt


openapi-generator generate -g java -i  test.yaml 

- [ yes] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?

validated but with circular reference

- [ ] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?

yes 
 $ openapi-generator --version
  openapi-generator-cli 6.1.0-SNAPSHOT
  commit : 5fb40e5
  built  : 2022-07-15T17:39:40Z
  source : https://github.com/openapitools/openapi-generator
  docs   : https://openapi-generator.tech/


- [ ] Have you searched for related issues/PRs?

yes

- [ ] What's the actual output vs expected output?

actual: stackoverflow 

expected:   generated code



- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. Eg:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

<!-- describe what is the question, suggestion or issue and why this is a problem for you. -->

##### openapi-generator version

<!-- which version of openapi-generator are you using, is it a regression? -->

6.0.1   - don't know if its a regression


##### OpenAPI declaration file content or url


attached

##### Generation Details

openapi-generator generate -g java -i  test.yaml 






[test.yaml.txt](https://github.com/OpenAPITools/openapi-generator/files/9142316/test.yaml.txt)

## Comment by programista-zacny on 2022-07-27

The same for:
API spec: `https://api.hubapi.com/api-catalog-public/v1/apis/marketing/v3/forms`
[Validator](https://apitools.dev/swagger-parser/online/): `This API is valid, but it cannot be shown because it contains circular references`
Configuration:
```
			<plugin>
				<groupId>org.openapitools</groupId>
				<artifactId>openapi-generator-maven-plugin</artifactId>
				<!-- RELEASE_VERSION -->
				<version>6.0.1</version>
				<!-- /RELEASE_VERSION -->
				<executions>
					<execution>
						<goals>
							<goal>generate</goal>
						</goals>
						<configuration>
							<inputSpec>https://api.hubapi.com/api-catalog-public/v1/apis/marketing/v3/forms</inputSpec>
							<generatorName>java</generatorName>
							<configOptions>
								<sourceFolder>src/gen/java/main</sourceFolder>
							</configOptions>
						</configuration>
					</execution>
				</executions>
			</plugin>
```
Build log:
```
[...]
constituent[40]: file:/C:/Users/jacek/dev/apache-maven-3.8.6/lib/wagon-provider-api-3.5.1.jar
---------------------------------------------------
Exception in thread "main" java.lang.StackOverflowError
        at java.base/java.lang.StringLatin1.replace(StringLatin1.java:344)
        at java.base/java.lang.String.replace(String.java:2970)
        at org.openapitools.codegen.utils.ModelUtils.getSimpleRef(ModelUtils.java:406)
        at org.openapitools.codegen.utils.ModelUtils.getReferencedSchema(ModelUtils.java:867)
        at org.openapitools.codegen.DefaultCodegen.recursiveGetDiscriminator(DefaultCodegen.java:3074)
        at org.openapitools.codegen.DefaultCodegen.recursiveGetDiscriminator(DefaultCodegen.java:3108)
        at org.openapitools.codegen.DefaultCodegen.recursiveGetDiscriminator(DefaultCodegen.java:3089)
        at org.openapitools.codegen.DefaultCodegen.recursiveGetDiscriminator(DefaultCodegen.java:3108)
        at org.openapitools.codegen.DefaultCodegen.recursiveGetDiscriminator(DefaultCodegen.java:3089)
        at org.openapitools.codegen.DefaultCodegen.recursiveGetDiscriminator(DefaultCodegen.java:3108)
        at org.openapitools.codegen.DefaultCodegen.recursiveGetDiscriminator(DefaultCodegen.java:3089)
[...]
```

## Comment by dfjmax on 2023-06-29

I'm having this same issue, is there any workaround to make this work?

## Comment by wing328 on 2023-07-05

Filed https://github.com/OpenAPITools/openapi-generator/pull/16008 to fix it. Added tests
