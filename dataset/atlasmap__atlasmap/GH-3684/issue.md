# [BUG] Circular dependency problem for using  '/inspect'  with JSON schema

- Issue: https://github.com/atlasmap/atlasmap/issues/3684
- Opened by pandora2333 on 2022-01-21, closed on 2022-01-22
- Labels: group/runtime, cat/bug
- Fix commit: 83b40e6e3efa4acd44ca55758000ec91ce4f642c

## Report

**Describe the bug**
use /inspect for json schema，it causes a Circular dependency problem

**Attach .adm file and source document examples**
a json schema file:
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "Request",
    "title": "入参模型",
    "type": "object",
    "properties": {
        "request": {
            "title": "1",
            "$ref": "#/definitions/person",
            "examples": [
                ""
            ]
        },
        "what": {
            "title": "2",
            "type": "string",
            "examples": [
                ""
            ]
        }
    },
    "requiredProperties": [
        "what"
    ],
    "definitions": {
        "person": {
            "$id": "person",
            "title": "person",
            "type": "object",
            "properties": {
                "name": {
                    "title": "姓名",
                    "type": "string",
                    "examples": [
                        ""
                    ]
                },
                "sex": {
                    "title": "性别",
                    "type": "integer",
                    "format": "int32",
                    "examples": [
                        ""
                    ]
                },
                "age": {
                    "title": "年龄",
                    "type": "integer",
                    "format": "int32",
                    "examples": [
                        ""
                    ]
                },
                "xiaji": {
                    "title": "下级",
                    "$ref": "#/definitions/person",
                    "examples": [
                        ""
                    ]
                }
            },
            "requiredProperties": []
        }
    }
}
```
 
**Attach debug logs**
stack overflow Exception
**To Reproduce**
input the json file as json schema

## Comment by igarashitm on 2022-01-21

Although the infinite loop will be fixed, recursive object support is not yet implemented - https://github.com/atlasmap/atlasmap/issues/255

It will be grayed out in the meantime.
