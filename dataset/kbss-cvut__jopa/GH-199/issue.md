# jopa-maven-plugin: Some code generation issues with ODRL 2.2 ontology

- Issue: https://github.com/kbss-cvut/jopa/issues/199
- Opened by JensPiegsa on 2023-09-07, closed on 2023-09-14
- Labels: bug
- Fix commit: 019d3fe4525e50df2b94f1980c32eea8b456e636

## Report

I've been exploring the `jopa-maven-plugin:1.1.1` for class generation with the ODRL 2.2 ontology and observed some quirks. I ran `jopa:owl2java-transform` with the following configuration:

```xml
<plugin>
  <groupId>cz.cvut.kbss.jopa</groupId>
  <artifactId>jopa-maven-plugin</artifactId>
  <version>${jopa-version}</version>
  <configuration>
    <output-directory>${basedir}/src/main/java</output-directory>
    <package>rdf.entity</package>
    <ontology-iri>https://www.w3.org/ns/odrl/2/ODRL22.ttl</ontology-iri>
    <prefer-multilingual-strings>true</prefer-multilingual-strings>
  </configuration>
</plugin>
```
While a majority of the generated code looks good, I've spotted some defects, which may be due to the configuration, ontology itself, OWL2Java, or possibly conceptual limitations. (The generated code can easily be fixed manually, though.)

1. Cyclic Inheritance

    - in the 'rdf.entity.model.Action' class: `public class Action extends Action`
    
2. Duplicate Definitions

    - the `toString()` method is generated multiple times in the following classes:
        - `rdf.entity.model.Agent`
        - `rdf.entity.model.Organization`
        - `rdf.entity.model.Person`
    - additionally, all attributes and other accessor methods are also duplicated or tripled in these classes, e.g.,  tripled too (`id`, `id1`, `id2`, `name`, `name1`, `name2`, ...)

Please let me know if I can assist further or provide any other details.

## Comment by ledsoft on 2023-09-11

Hi Jens,
sorry for the late response. I quickly went through the ontology you reference and it seems to me the issue is that there is a class Action in the base namespace (`odrl`) which is a subclass of `scheme:Action`. This apparently confuses OWL2Java and it is unable to differentiate the two classes.
I am filing it as a bug and will take a look at it later. Thanks for reporting it.

## Comment by JensPiegsa on 2023-09-11

Hi Martin,

Thanks for digging into it, that sounds very likely.

Cheers,
Jens

## Comment by ledsoft on 2023-09-14

So the current fix appends `_A` (repeatedly, if necessary) to the class name until it is unique. It is not a very nice solution, but a more complex solution is already proposed in #85 and will likely cause breaking changes, so it is slated for 2.0.0.
