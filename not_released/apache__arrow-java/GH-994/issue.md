# [FlightSQL,JDBC] NullPointerException in DatabaseMetadata methods when SqlInfo is unavailable

- Issue: https://github.com/apache/arrow-java/issues/994
- Opened by merzbird on 2026-01-29, closed on 2026-03-11
- Labels: Type: bug
- Fix commit: bdec833fb69f945db9f3c767715c93d09214f2b5

## Report

## Describe the bug

Multiple DatabaseMetadata methods in the Arrow Flight SQL JDBC driver throw `NullPointerException` when the server doesn't provide certain SqlInfo values. The `ArrowDatabaseMetadata.getSqlInfoAndCacheIfCacheIsEmpty()` method returns `null`, but calling code doesn't handle null defensively before invoking methods like `.intValue()`, `.booleanValue()`, or `.isEmpty()`.

## Affected Methods

All 68+ DatabaseMetadata methods that rely on `getSqlInfoAndCacheIfCacheIsEmpty()` are affected, including:

### Integer-returning methods (20 methods)
- `getMaxBinaryLiteralLength()`
- `getMaxCharLiteralLength()`
- `getMaxColumnNameLength()`
- `getMaxColumnsInGroupBy()`
- `getMaxColumnsInIndex()`
- `getMaxColumnsInOrderBy()`
- `getMaxColumnsInSelect()`
- `getMaxColumnsInTable()`
- `getMaxConnections()`
- `getMaxCursorNameLength()`
- `getMaxIndexLength()`
- `getMaxSchemaNameLength()`
- `getMaxProcedureNameLength()`
- `getMaxCatalogNameLength()`
- `getMaxRowSize()`
- `getMaxStatementLength()`
- `getMaxStatements()`
- `getMaxTableNameLength()`
- `getMaxTablesInSelect()`
- `getMaxUserNameLength()`

### Boolean-returning methods (30 methods)
- `supportsColumnAliasing()`
- `nullPlusNonNullIsNull()`
- `supportsTableCorrelationNames()`
- `supportsDifferentTableCorrelationNames()`
- `supportsExpressionsInOrderBy()`
- `supportsOrderByUnrelated()`
- `supportsLikeEscapeClause()`
- `supportsNonNullableColumns()`
- `supportsIntegrityEnhancementFacility()`
- `isCatalogAtStart()`
- `supportsSelectForUpdate()`
- `supportsStoredProcedures()`
- `supportsCorrelatedSubqueries()`
- `doesMaxRowSizeIncludeBlobs()`
- `supportsTransactions()`
- `dataDefinitionCausesTransactionCommit()`
- `dataDefinitionIgnoredInTransactions()`
- `supportsBatchUpdates()`
- `supportsSavepoints()`
- `supportsNamedParameters()`
- `locatorsUpdateCopy()`
- `supportsStoredFunctionsUsingCallSyntax()`

### Support level methods (18 methods)
- `getDefaultTransactionIsolation()`
- `supportsGroupBy()`
- `supportsGroupByUnrelated()`
- `supportsMinimumSQLGrammar()`
- `supportsCoreSQLGrammar()`
- `supportsExtendedSQLGrammar()`
- `supportsANSI92EntryLevelSQL()`
- `supportsANSI92IntermediateSQL()`
- `supportsANSI92FullSQL()`
- `supportsOuterJoins()`
- `supportsFullOuterJoins()`
- `supportsLimitedOuterJoins()`
- `supportsSchemasInProcedureCalls()`
- `supportsSchemasInIndexDefinitions()`
- `supportsSchemasInPrivilegeDefinitions()`
- `supportsCatalogsInIndexDefinitions()`
- `supportsCatalogsInPrivilegeDefinitions()`
- `supportsPositionedDelete()`
- `supportsPositionedUpdate()`
- `supportsSubqueriesInComparisons()`
- `supportsSubqueriesInExists()`
- `supportsSubqueriesInIns()`
- `supportsSubqueriesInQuantifieds()`
- `supportsUnion()`
- `supportsUnionAll()`

### Map-returning methods
- `supportsConvert()`

## Component(s)

- FlightSQL
- JDBC

## To Reproduce

```java
import java.sql.*;
import java.util.Properties;

public class DatabaseMetadataTest {
    public static void main(String[] args) throws SQLException {
        String url = "jdbc:arrow-flight-sql://...";
        Properties props = new Properties();
        Driver driver = DriverManager.getDriver(url);
        try (Connection conn = driver.connect(url, props)) {
            DatabaseMetaData metaData = conn.getMetaData();

            // All of these throw NullPointerException
            System.out.println(metaData.getMaxBinaryLiteralLength());
            System.out.println(metaData.supportsTransactions());
            System.out.println(metaData.supportsGroupBy());
        }
    }
}
```

### Error Output

```
Exception in thread "main" java.lang.NullPointerException: Cannot invoke "java.lang.Long.intValue()"
because the return value of "org.apache.arrow.driver.jdbc.ArrowDatabaseMetadata.getSqlInfoAndCacheIfCacheIsEmpty
(org.apache.arrow.driver.jdbc.shaded.org.apache.arrow.flight.sql.impl.FlightSql$SqlInfo, java.lang.Class)" is null
	at org.apache.arrow.driver.jdbc.ArrowDatabaseMetadata.getMaxBinaryLiteralLength(ArrowDatabaseMetadata.java:xxx)
```

## Expected behavior

1. **Option A:** Return sensible defaults when SqlInfo is unavailable:
   - Integer methods: return `0` (as per JDBC spec for "no limit" or "unknown")
   - Boolean methods: return `false` (conservative/safe default)
   - Support level methods: return appropriate default enums
   - Map methods: return empty map

2. **Option B:** Throw `SQLException` with a descriptive message indicating the server doesn't support the requested SqlInfo

3. Methods should NOT throw unchecked `NullPointerException` - this violates JDBC contracts and the principle of least surprise

## Environment

**Arrow Version:**
- 18.3.0

**Java Version:**
- Java 11+

**OS:**
- All platforms

### JDBC Specification Reference

Per JDBC 4.3 specification:
- Methods returning int should return 0 when the limit is unknown or there is no limit
- Methods returning boolean should return false for unsupported features
- Methods should throw SQLException for errors, not unchecked exceptions

## Comment by ennuite on 2026-01-30

Hi! I will look into fixing this in the next couple of days. Will let you know once I open a PR. Thank you for the thorough bug report.

## Comment by ennuite on 2026-02-02

@merzbird I created a PR. Let me know if you agree with the fix, I return sensible values like you suggest, and for classes for which no known decent defaults are know, I throw a SQLException. All current call sites are covered with defaults. The exception is a guard rail for future additions.

Also, feel free to ping me on any new issues you create, especially concerning Flight or JDBC. I regularly monitor the issues, but it might skip me.

## Comment by merzbird on 2026-02-02

@ennuite Thanks for the swift response!

It is a nice and simple solution to default to `false`/`0` when SqlInfo is absent, but I have doubts that it is always the best - e.g., Avatica (which AvaticaDatabaseMetaData arrow's impl is based on) uses different values as defaults: `supportsGroupBy` is `true`, but `supportsStoredProcedures` is `false`. I don't know, maybe there are some strong reasons to prefer that approach. 

But for simplicity's sake and conformance with JDBC spec, your PR definitely looks good to me.

## Comment by ennuite on 2026-02-02

@merzbird I had similar thoughts regarding the boolean values. For the integers, it is specified that 0 also serves as unknown so I think it's fine, but the JDBC spec does not say the same for boolean values. I considered throwing a checked exception instead of returning false, but I'm under the impression that this could hinder common usage of this API.
