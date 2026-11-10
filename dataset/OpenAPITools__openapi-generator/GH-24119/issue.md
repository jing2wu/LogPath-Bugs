# [BUG,AsciiDoc] Pipe Characters in patterns break table layout

- Issue: https://github.com/OpenAPITools/openapi-generator/issues/24119
- Opened by ben-GDV on 2026-06-24, closed on 2026-07-02
- Labels: Issue: Bug
- Fix commit: 2f5bf0e61a96144107cfe1747ff683f4bd584259

## Report

#### Bug Report Checklist

- [x] Have you provided a full/minimal spec to reproduce the issue?
- [ ] Have you validated the input using an OpenAPI validator?
- [ ] Have you [tested with the latest master](https://github.com/OpenAPITools/openapi-generator/wiki/FAQ#how-to-test-with-the-latest-master-of-openapi-generator) to confirm the issue still exists?
- [x] Have you searched for related issues/PRs?
- [x] What's the actual output vs expected output?
- [ ] [Optional] Sponsorship to speed up the bug fix or feature request ([example](https://github.com/OpenAPITools/openapi-generator/issues/6178))

##### Description

Regexp patterns can contain "|" (Pipe Characters), which denotes the Union of two Regexps.
However, when using a Pipe in a pattern and using the OpenAPI AsciiDoc generator to generate AsciiDoc from the OpenAPI specification, then the Pipe character is not escaped and consequently interpreted by AsciiDoc as the table cell delimiter, which breaks the layout of the table of all fields in an object.

##### openapi-generator version

I am using version 7.12.0 of the openapi-generator-maven-plugin.

##### OpenAPI declaration file content or url

This snippet can be placed in any object's properties-list to reproduce the issue:
```yaml
        field
          type: string
          pattern: "^([0-9A-Z]{3})|([0-9A-Z]{5})$"`
```

##### Generation Details

language: OpenAPI YAML
Open API version: 3.0.3

##### Steps to reproduce

In maven's pom.xml file, the generator plugin has the following execution:

`                   <execution>
                        <id>generate-asciidoc</id>
                        <goals>
                            <goal>generate</goal>
                        </goals>
                        <configuration>
                            <generatorName>asciidoc</generatorName>
                            <inputSpec>${project.basedir}/src/main/resources/openapi.yml</inputSpec>                             <templateDirectory>${project.basedir}/src/main/resources/_templates/asciidoc</templateDirectory>
                            <output>${project.build.directory}/generated-sources/openapi/</output>
                            <configOptions>
                                <resolveRefs>true</resolveRefs>
                                <apiDocs>true</apiDocs>
                                <modelDocs>true</modelDocs>
                            </configOptions>
                        </configuration>
                    </execution>`

when I run `mvn generate`, Maven uses the openapi-asciidoc-generator to produce AsciiDoc files. However, in these files, the pipe character in the pattern is not escaped which breaks the table laypit when I use asciiDoc to turn them into HTML.

##### Related issues/PRs

I did not find any.

##### Suggest a fix

the pipe character must be escapted with a "\" (backslash character). This allows AsciiDoc to interpret it correctly and to properly render the table.
