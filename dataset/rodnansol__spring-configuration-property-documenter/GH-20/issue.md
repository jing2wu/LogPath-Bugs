# Null Pointer Exception in the MetadataReader when a property group is not having any property

- Issue: https://github.com/rodnansol/spring-configuration-property-documenter/issues/20
- Opened by nandorholozsnyak on 2023-01-15, closed on 2023-01-15
- Labels: bug
- Fix commit: bf33575b5c1d5bb20ba5d8ee0554cbaa7b12d8d8

## Report

**Describe the bug**
A Null Pointer Exception occurs in the MetadataReader when a property group is not having any property.

It happens in this method call: `org.rodnansol.core.generator.reader.MetadataReader#setProperties˙

**To Reproduce**
Steps to reproduce the behavior:
1. Create any empty class that is annotated with the ConfigurationProperties annotation.
2. Run the Maven plugin

**Expected behavior**
It should not thrown a null pointer exception if the group is not having any property.

**Additional context**
It would be good for the end users to see a log message about that the class is either empty or the existing properties are not having accessory methods.
