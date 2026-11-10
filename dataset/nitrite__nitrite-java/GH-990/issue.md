# bug: migration from 3.x to 4.x with MVStore module fails

- Issue: https://github.com/nitrite/nitrite-java/issues/990
- Opened by DarkAtra on 2024-06-28, closed on 2024-06-30
- Labels: bug
- Fix commit: 2e0b69e2fc7d9b72c66e63b479052211a8cb45c9

## Report

The wiki states that
> Nitrite will try to migrate your existing database to the latest version on the best effort basis without any guarantee provided you are using the MVStore module.

However, it seems like it fails to migrate document ids correctly. Version 3.x uses a Long to represent the internal document `_id`. In version 4.x this code changed to use a String instead. When using version 4.x to read a database that was created with version 3.x the following exception occurs when updating a document:

```
org.dizitart.no2.exceptions.InvalidIdException: Invalid _id found 21601262100400
```

Test case (includes a v3 database): https://github.com/DarkAtra/nitrite-java/blob/bug/id-migration-for-old-documents-fails/nitrite-mvstore-adapter/src/test/java/org/dizitart/no2/NitriteTest.java#L449-L479

Steps to reproduce:
* create a database with nitrite version 3.x
* create a collection with a single document
* update nitrite to version 4.x
* get the document from the collection and update any field
* invoke `update` to persist the changes
* you should now see the above exception

Is this expected? If so, what would be the best way for me to update existing documents so that they function correctly with version 4.x of nitrite?

## Comment by DarkAtra on 2024-06-29

This might do the trick:
```
Subject: [PATCH] bug: migration from 3.x to 4.x with MVStore module fails
---
Index: nitrite-mvstore-adapter/src/main/java/org/dizitart/no2/mvstore/compat/v1/UpgradeUtil.java
IDEA additional info:
Subsystem: com.intellij.openapi.diff.impl.patch.CharsetEP
<+>UTF-8
===================================================================
diff --git a/nitrite-mvstore-adapter/src/main/java/org/dizitart/no2/mvstore/compat/v1/UpgradeUtil.java b/nitrite-mvstore-adapter/src/main/java/org/dizitart/no2/mvstore/compat/v1/UpgradeUtil.java
--- a/nitrite-mvstore-adapter/src/main/java/org/dizitart/no2/mvstore/compat/v1/UpgradeUtil.java	(revision 03fd0f7cc41c6ba1f6cbf13a56ccbf08700a2b7d)
+++ b/nitrite-mvstore-adapter/src/main/java/org/dizitart/no2/mvstore/compat/v1/UpgradeUtil.java	(revision 9f1f34ecb9e3d48a68fb53c6be7da3f7eaaf20e9)
@@ -190,7 +190,13 @@
         Document document = Document.createDocument();
         for (Map.Entry<String, Object> entry : value.entrySet()) {
             Object val = entry.getValue();
-            Object migratedVal = migrateValue(val);
+
+            Object migratedVal;
+            if (DOC_ID.equals(entry.getKey())) {
+                migratedVal = Long.toString((long) val);
+            } else {
+                migratedVal = migrateValue(val);
+            }
             document.put(entry.getKey(), migratedVal);
         }
         return document;

```

## Comment by anidotnet on 2024-06-30

Thanks for reporting this issue and providing the solution as well. This fix will be in 4.3.0-SNAPSHOT in a while.
