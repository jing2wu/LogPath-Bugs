# [BUG,JAVA] Compilation error for a `Map<String, Set<InnerEnum>>` due to incompatible types

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/19393
- Opened by Bragolgirith on 2024-08-19, closed on 2024-11-24
- Labels: Issue: Bug
- Fix commit: 8ce332a540f3ece6779bd90d01c73223f5c8edde

## Report

##### Description

I have the following schema that describes the different roles an employee can have in different projects as a map of collection of enum, e.g.:

```yaml
    Employee:
      type: object
      properties:
        projectRoles:
          type: object
          additionalProperties:
            uniqueItems: true
            type: array
            items:
              type: string
              enum:
                - DEVELOPER
                - TESTER
                - OWNER
```

This works correctly with most generators, however the `java` generator seems to have some trouble with it and generates an invalid `Employee.java class`:

```java
public class Employee {

  // ... truncated

  // This should be Map<String, Set<InnerEnum>> instead
  private Map<String, Set<String>> projectRoles = new HashMap<>();

  // ... truncated

  public Employee putProjectRolesItem(String key, Set<InnerEnum> projectRolesItem) {
    if (this.projectRoles == null) {
      this.projectRoles = new HashMap<>();
    }
    this.projectRoles.put(key, projectRolesItem); // Compiler error here due to the mismatching types
    return this;
  }
}
```

The compiler error is as follows

```
incompatible types: java.util.Set<org.openapitools.client.model.Employee.InnerEnum> cannot be converted to java.util.Set<java.lang.String>
```

Note that the issue only occurs for inline enums (i.e. `InnerEnum`s); enum references work as expected.

##### openapi-generator version

Tested using `openapi-generator` version 7.8.0.

##### OpenAPI declaration file content

A gist with a minimal OpenAPI spec file to reproduce the issue can be found [here](https://gist.github.com/Bragolgirith/5161e67882e5c4b39b8b07b3990e38cd).

##### Generation Details

I'm generating the Java client using the `openapi-generator-maven-plugin` as follows:

```xml
<plugin>
    <groupId>org.openapitools</groupId>
    <artifactId>openapi-generator-maven-plugin</artifactId>
    <version>7.8.0</version>
    <executions>
        <execution>
            <phase>generate-sources</phase>
            <goals>
                <goal>generate</goal>
            </goals>
            <configuration>
                <inputSpec>
                    ${project.basedir}/src/main/resources/employee-api.json
                </inputSpec>
                <generatorName>java</generatorName>
                <library>webclient</library>
                <generateModels>true</generateModels>
                <generateModelTests>false</generateModelTests>
                <generateApiTests>false</generateApiTests>
                <configOptions>
                    <useJakartaEe>true</useJakartaEe>
                </configOptions>
            </configuration>
        </execution>
    </executions>
</plugin>
```

##### Steps to reproduce

1. Generate a Java client using the provided OpenAPI spec file
2. Try to compile the generated client

## Comment by Bragolgirith on 2024-08-20

I think the problem is in the `DefaultCodegen#updateDataTypeWithEnumForMap` method, on line [4278](https://github.com/OpenAPITools/openapi-generator/blob/c2472b03b63fa61a3d7e5b086f36c1bd48d0ee4c/modules/openapi-generator/src/main/java/org/openapitools/codegen/DefaultCodegen.java#L4278):

```java
property.datatypeWithEnum = property.datatypeWithEnum.replace(", " + baseItem.baseType, ", " + toEnumName(baseItem));
```

This will correctly replace a non-parameterized inner value type, e.g. `String`:

* `Map<String, String>` -> `Map<String, InnerEnum>`

but it will fail to replace a parameterized inner value type, e.g. `Set<String>`:

* `Map<String, Set<String>>` -> `Map<String, Set<InnerEnum>>`

as it will try to match the pattern `", String"` which doesn't exist in the second example.

One (naive) idea could be to simply use the following replacement instead, which should work with both parameterized and non-parameterized value types:

```java
property.datatypeWithEnum = property.datatypeWithEnum.replace(baseItem.baseType + ">", toEnumName(baseItem) + ">")
```
