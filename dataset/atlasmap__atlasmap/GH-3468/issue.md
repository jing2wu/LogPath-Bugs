# [BUG] No collection suffix in the path for XML field

- Issue: https://github.com/atlasmap/atlasmap/issues/3468
- Opened by igarashitm on 2021-11-10, closed on 2021-11-11
- Labels: group/runtime, cat/bug
- Fix commit: 15d9e76f743ce67438316e28bf3c7d6a79a50513

## Report

**Describe the bug**
<!--
A clear and concise description of what the bug is. The more info is provided, the more likely we can fix it earlier.
-->
UI doesn't put collection suffix like `<>` or `[]` into field path, causes the mapping to fail. Since UI is showing `emplyee` parent field with a collection icon, the issue would be in the serializer.

**Attach .adm file and source document examples**
<!--
The .adm archive file you can export from AtlasMap UI contains all metadata to reproduce your mapping. Also don't forget to provide source document examples to reproduce the runtime behavior exactly what you see.
 -->
[atlasmap-mapping.adm.zip](https://github.com/atlasmap/atlasmap/files/7514053/atlasmap-mapping.adm.zip) 
[employee.xsd.txt](https://github.com/atlasmap/atlasmap/files/7514116/employee.xsd.txt)

**Attach debug logs**
<!--
If it's a design time issue, attach a backend log with debug enabled
`java -Dlogging.level.io.atlasmap=debug -jar atlasmap-standalone.jar`
or for runtime issue, set the log level for `io.atlasmap` package to debug in your log4j config
 -->
```json
{
  "AtlasMapping" : {
    "jsonType" : "io.atlasmap.v2.AtlasMapping",
    "dataSource" : [ {
      "jsonType" : "io.atlasmap.xml.v2.XmlDataSource",
      "id" : "employee-f20432b0-cca9-4516-be35-334586b5cbc7",
      "name" : "employee",
      "description" : "Source document employee type: XSD",
      "uri" : "atlas:xml:employee-f20432b0-cca9-4516-be35-334586b5cbc7",
      "dataSourceType" : "SOURCE",
      "xmlNamespaces" : {
        "xmlNamespace" : [ ]
      }
    }, {
      "jsonType" : "io.atlasmap.xml.v2.XmlDataSource",
      "id" : "employee-59fd0670-26de-4683-8563-e05a34e8f383",
      "name" : "employee",
      "description" : "Target document employee type: XSD",
      "uri" : "atlas:xml:employee-59fd0670-26de-4683-8563-e05a34e8f383",
      "dataSourceType" : "TARGET",
      "xmlNamespaces" : {
        "xmlNamespace" : [ ]
      }
    } ],
    "mappings" : {
      "mapping" : [ {
        "jsonType" : "io.atlasmap.v2.Mapping",
        "inputFieldGroup" : {
          "jsonType" : "io.atlasmap.v2.FieldGroup",
          "actions" : [ ],
          "field" : [ {
            "jsonType" : "io.atlasmap.xml.v2.XmlField",
            "docId" : "employee-f20432b0-cca9-4516-be35-334586b5cbc7",
            "path" : "/employees/employee/@id",
            "fieldType" : "STRING",
            "name" : "id",
            "userCreated" : false,
            "attribute" : true
          } ]
        },
        "inputField" : [ ],
        "outputField" : [ {
          "jsonType" : "io.atlasmap.xml.v2.XmlField",
          "docId" : "employee-59fd0670-26de-4683-8563-e05a34e8f383",
          "path" : "/employees/employee/@id",
          "fieldType" : "STRING",
          "name" : "id",
          "userCreated" : false,
          "attribute" : true
        } ],
        "id" : "mapping.205273"
      }, {
        "jsonType" : "io.atlasmap.v2.Mapping",
        "inputFieldGroup" : {
          "jsonType" : "io.atlasmap.v2.FieldGroup",
          "actions" : [ ],
          "field" : [ {
            "jsonType" : "io.atlasmap.xml.v2.XmlField",
            "docId" : "employee-f20432b0-cca9-4516-be35-334586b5cbc7",
            "path" : "/employees/employee/building",
            "fieldType" : "INTEGER",
            "name" : "building",
            "userCreated" : false,
            "attribute" : false
          } ]
        },
        "inputField" : [ ],
        "outputField" : [ {
          "jsonType" : "io.atlasmap.xml.v2.XmlField",
          "docId" : "employee-59fd0670-26de-4683-8563-e05a34e8f383",
          "path" : "/employees/employee/building",
          "fieldType" : "INTEGER",
          "name" : "building",
          "userCreated" : false,
          "attribute" : false
        } ],
        "id" : "mapping.571720"
      } ]
    },
    "lookupTables" : {
      "lookupTable" : [ ]
    },
    "constants" : {
      "constant" : [ ]
    },
    "properties" : {
      "property" : [ ]
    },
    "name" : "UI.0"
  }
}
``` 
**To Reproduce**
<!--
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error
-->
1. Import employee.xsd as a source document schema as well as a target document schema
2. Create a mapping, e.g. `/employees/employee<>/building` to `/employees/employee<>/building`
3. Check the mapping definition JSON and see employee doesn't have a collection suffix
 
**Expected behavior**
<!--
A clear and concise description of what you expected to happen.
-->
employee should be shown as `employee<>` in the path

**Screenshots**
<!--
If applicable, add screenshots to help explain your problem.
-->
![Screenshot from 2021-11-10 10-41-25](https://user-images.githubusercontent.com/265462/141148578-b9b07c62-0cf8-461a-bb57-dc8e72819d04.png)

## Comment by igarashitm on 2021-11-11

@pleacu it seems to be a runtime issue, XML schema inspection doesn't put the collection suffix in the path, this expectation is obviously wrong
https://github.com/atlasmap/atlasmap/blob/a7da120f2ae9bc176782c3d86046442e58138bbd/lib/modules/xml/core/src/test/java/io/atlasmap/xml/inspect/XmlSchemaInspectionTest.java#L301

do you want me to take over?

## Comment by pleacu on 2021-11-11

Sure - I just came to that conclusion - thkx!
