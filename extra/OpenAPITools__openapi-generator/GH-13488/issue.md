# [BUG] @RequestMapping annotation not allowed on @FeignClient interfaces

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/13488
- Opened by cTAbdIsi on 2022-09-21, closed on 2023-01-15
- Labels: Issue: Bug
- Fix commit: b2280e23f7d537d6d0f1f09b23124249aed2f661

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [x] Have you validated the input using an OpenAPI validator ([example](https://apidevtools.org/swagger-parser/online/))?
- [ ] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

<!--
Please follow the issue template below for bug reports.
Also please indicate in the issue title which language/library is concerned. Eg:  [BUG,JAVA] Bug generating foo with bar 
-->

##### Description

Code generation with plugin failed with error `@RequestMapping annotation not allowed on @FeignClient interfaces` after update to 6.1.0

##### openapi-generator version

6.1.0

##### Generation Details

This is our configuration for the maven plugin:
```yaml
<plugin>
    <groupId>org.openapitools</groupId>
    <artifactId>openapi-generator-maven-plugin</artifactId>
    <version>${openapi-generator-maven-plugin.version}</version>
    <configuration>
        <configOptions>
            <dateLibrary>java8</dateLibrary>
            <disableHtmlEscaping>true</disableHtmlEscaping>
            <hateoas>false</hateoas>
            <hideGenerationTimestamp>true</hideGenerationTimestamp>
            <interfaceOnly>true</interfaceOnly>
            <sourceFolder>models</sourceFolder>
            <useTags>true</useTags>
        </configOptions>
        <generateModels>true</generateModels>
        <generatorName>spring</generatorName>
        <library>spring-cloud</library>
        <skipIfSpecIsUnchanged>true</skipIfSpecIsUnchanged>
    </configuration>
    <executions>
        <execution>
            <id>generate-api</id>
            <goals>
                <goal>generate</goal>
            </goals>
            <configuration>
                <apiPackage>${project.groupId}.${project.artifactId}.api.v1</apiPackage>
                <inputSpec>${project.basedir}/docs/openapi.yaml</inputSpec>
                <modelPackage>${project.groupId}.${project.artifactId}.api.v1.model</modelPackage>
                <modelNameSuffix>ApiV1</modelNameSuffix>
            </configuration>
        </execution>
    </executions>
</plugin>
```
In openapi-generator version < 6.1.0, the plugin generate following code:

```java
@Generated(value = "org.openapitools.codegen.languages.SpringCodegen")
@Validated
@Tag(name = "Test")
public interface TestApi {
...
}
```

This is the result after updating to 6.1.0+.

```java
@Generated(value = "org.openapitools.codegen.languages.SpringCodegen")
@Validated
@Tag(name = "Test")
@RequestMapping("${openapi.localServices.base-path:/test/v1}")
public interface TestApi {
```

We use this interface to setup the feign clients like this:
```java
@FeignClient(name = "test",
             url = "${sdu.test.url:}",
             configuration = {TestApiConfig.class, ApiClientConfig.class})
public interface TestApiClient extends TestApi {
}
```

##### Steps to reproduce

<!-- unambiguous set of steps to reproduce the bug.-->

##### Related issues/PRs

<!-- has a similar issue/PR been reported/opened before? Please do a search in https://github.com/openapitools/openapi-generator/issues?utf8=%E2%9C%93&q=is%3Aissue%20 -->

##### Suggest a fix

<!-- if you can't fix the bug yourself, perhaps you can point to what might be
  causing the problem (line of code or commit), or simply make a suggestion -->

## Comment by dersvenhesse on 2022-09-22

The related change is probably https://github.com/OpenAPITools/openapi-generator/pull/10573 where `@RequestMapping` was moved from the controller to the interface.

## Comment by MelleD on 2022-09-27

@RomainPruvostMHH and @welshm could you please habe look and revert this change?

## Comment by welshm on 2022-09-28

> @RomainPruvostMHH and @welshm could you please habe look and revert this change?

I can try to take a look at this today or tomorrow

## Comment by MelleD on 2022-09-28

@welshm i commented the issue in der merged PR modules/openapi-generator/src/main/resources/JavaSpring/api.mustache

Not sure if we have a condition, that we know that we use Feign on this time and can add @RequestMapping just if we don't use Feign.

## Comment by welshm on 2022-09-28

> @welshm i commented the issue in der merged PR modules/openapi-generator/src/main/resources/JavaSpring/api.mustache
> 
> Not sure if we have a condition, that we know that we use Feign on this time and can add @RequestMapping just if we don't use Feign.

I think we have a condition to check (because it exists in other `.mustache`) but I will verify and post back here

## Comment by MelleD on 2022-09-28

> > @welshm i commented the issue in der merged PR modules/openapi-generator/src/main/resources/JavaSpring/api.mustache
> > Not sure if we have a condition, that we know that we use Feign on this time and can add @RequestMapping just if we don't use Feign.
> 
> I think we have a condition to check (because it exists in other `.mustache`) but I will verify and post back here

Ah nice, then i think it's an easy fix. Maybe i can look into it tomorrow

## Comment by MelleD on 2022-09-28

@welshm found no condition. Thought `{{^useSpringCloudClient}}` could work, but did not find where this condition is set.

Tested it with

```
   @Test
   public void testNoRequestMappingAnnotation() throws IOException {
      final SpringCodegen codegen = new SpringCodegen();
      codegen.setLibrary( "spring-cloud" );

      final Map<String, File> files = generateFiles( codegen, "src/test/resources/2_0/petstore.yaml" );

      // Check that the @RequestMapping annotation is not generated in the Api file
      final File petApiFile = files.get( "PetApi.java" );
      JavaFileAssert.assertThat( petApiFile ).assertTypeAnnotations().hasSize( 3 ).containsWithName( "Validated" )
            .containsWithName( "Generated" ).containsWithName( "Tag" );

   }
```

## Comment by MelleD on 2022-09-28

@welshm created a new boolean for the feign client:
https://github.com/OpenAPITools/openapi-generator/pull/13546

If this is okay, i would adapt the other test(s)

## Comment by DarrMirr on 2022-10-06

Please, fix this bug, because Spring Framework expects annotation `@RequestMapping` on type-level and start to register request mapping for such class. Such bug make impossible to use Feign client due to ambiguous mapping.

Here is code sample from Spring source code :
```Java
public class RequestMappingHandlerMapping extends RequestMappingInfoHandlerMapping
		implements MatchableHandlerMapping, EmbeddedValueResolverAware {

	/**
	 * {@inheritDoc}
	 * <p>Expects a handler to have either a type-level @{@link Controller}
	 * annotation or a type-level @{@link RequestMapping} annotation.
	 */
	@Override
	protected boolean isHandler(Class<?> beanType) {
		return (AnnotatedElementUtils.hasAnnotation(beanType, Controller.class) ||
				AnnotatedElementUtils.hasAnnotation(beanType, RequestMapping.class));
	}
}
```

## Comment by welshm on 2022-10-06

> Please, fix this bug, because Spring Framework expects annotation `@RequestMapping` on type-level and start to register request mapping for such class. Such bug make impossible to use Feign client due to ambiguous mapping.
> 
> Here is code sample from Spring source code :
> 
> ```java
> public class RequestMappingHandlerMapping extends RequestMappingInfoHandlerMapping
> 		implements MatchableHandlerMapping, EmbeddedValueResolverAware {
> 
> 	/**
> 	 * {@inheritDoc}
> 	 * <p>Expects a handler to have either a type-level @{@link Controller}
> 	 * annotation or a type-level @{@link RequestMapping} annotation.
> 	 */
> 	@Override
> 	protected boolean isHandler(Class<?> beanType) {
> 		return (AnnotatedElementUtils.hasAnnotation(beanType, Controller.class) ||
> 				AnnotatedElementUtils.hasAnnotation(beanType, RequestMapping.class));
> 	}
> }
> ```

Are you suggesting that the annotation should be on the controller implementation as opposed to the interface?

Can you take a look at the output from https://github.com/OpenAPITools/openapi-generator/pull/13546 and see if that is what you'd expect? That will remove the annotation from the interface, but does not re-add it to the controller.

## Comment by DarrMirr on 2022-10-10

Hello @welshm. Thank you for response and link to [#13546](https://github.com/OpenAPITools/openapi-generator/pull/13546). I think it solve this issue.

## Comment by vvinod1310 on 2022-10-31

Hello,

May I know when this fix would be released? 

Thank you!

## Comment by borsch on 2023-01-13

@vvinod1310 this is part of 6.2.1

## Comment by ctbarnev on 2023-06-22

Is anyone else encountering this bug when using the Kotlin-Spring generator with library spring-cloud? 

We're using openapi-generator version: 6.6.0

Our generated interface:
```
@Validated
@RequestMapping("\${api.base-path:/api/test/v1}")
interface TestApi {
```

The generated FeignClient:
```
@FeignClient(
    name="Test",
    url="\${test.url:http://localhost/api/test/v1}", 
    configuration = [ClientConfiguration::class]
)
interface TestApiClient : TestApi
```

Then when running our application we encounter the same exception: 
`@RequestMapping annotation not allowed on @FeignClient interfaces`

Think the fix made in this [pull request](https://github.com/OpenAPITools/openapi-generator/pull/13546) should also be implemented in the Kotlin-Spring generator right? Or am I missing something?

## Comment by ctbarnev on 2023-06-23

I created a [MR](https://github.com/OpenAPITools/openapi-generator/pull/15898) to fix this issue also for the Kotlin-Spring generator, hopefully someone can have a look?
