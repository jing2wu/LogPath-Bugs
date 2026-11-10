# ClasspathResourceResolver unable to resolve from nested jar

- Issue: https://github.com/citrusframework/citrus/issues/1094
- Opened by tschlat on 2024-01-16, closed on 2024-01-16
- Labels: bug, prio-high
- Fix commit: 902df4f0a3a68c09b7945bfb2c1a638d2923ede2

## Report

**Citrus Version**
4.x-SNAPSHOT with Spring-Boot 3.2


**Expected behavior**
The ClasspathResourceResolver should be able to resolve resources from nested jars. Specifically, the `org.citrusframework.spi.TypeResolver`, which is responsible for resolving classpath resource mappings, is failing to resolve these mappings. For example, it should be able to resolve resources located in `citrus-validation-json-4.x/META-INF/citrus/variable/extractor/segment/`.

**Actual behavior**
The ClasspathResourceResolver is unable to resolve these resource mappings when packed into a `Spring Boot` jar archive. In this case, the containing jar is nested within the `Spring Boot` executable jar. It appears that there has been a change in the representation of nested jar URLs from:

`jar:file:/C:/work/IdeaProjects/myProject/target/myproject-1.0.0-SNAPSHOT-executable.jar!/BOOT-INF/lib/citrus-validation-json-4.0.2.jar!/META-INF/citrus/variable/extractor/segment/`
to
`jar:nested:/C:/work/IdeaProjects/myProject/target/myproject-1.0.0-SNAPSHOT-executable.jar!/BOOT-INF/lib/citrus-validation-json-4.0.2.jar!/META-INF/citrus/variable/extractor/segment/`

And `jar:nested` is not properly handled by the Citrus ClasspathResourceResolver.

This change in `Spring Boot` from `3.1.x` to `3.2.x` aligns with the documentation:

[Spring Boot 3.1.x Documentation](https://docs.spring.io/spring-boot/docs/3.1.x/reference/htmlsingle/#appendix.executable-jar.jarfile-class.compatibility)
[Spring Boot 3.2.x Documentation](https://docs.spring.io/spring-boot/docs/3.2.x/reference/htmlsingle/#appendix.executable-jar.jarfile-class.compatibility)

## Comment by bbortt on 2024-01-16

@christophd detected by @postfinance in (company-internal) release candidate for 4.1.0. should be fixed before the release, I think.

## Comment by bbortt on 2024-01-16

is also mentioned in the release notes.. advantage of those who can read.. (note to myself) 😉 

https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.2-Release-Notes#nested-jar-support
