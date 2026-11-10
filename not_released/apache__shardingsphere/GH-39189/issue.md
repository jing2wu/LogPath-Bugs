# Hibernate fails with "Operation not allowed after ResultSet closed" when using ShardingSphere JDBC

- Issue: https://github.com/apache/shardingsphere/issues/39189
- Opened by Nilesh18398 on 2026-07-20, closed on 2026-09-04
- Labels: type: bug, in: JDBC
- Fix commit: f785509568ad93706a675d16c4355def9a391648

## Report

# Bug: Hibernate fails with "Operation not allowed after ResultSet closed" when using ShardingSphere JDBC

## Description

The application fails when executing a Spring Data JPA repository query. Hibernate throws a `JpaSystemException` while extracting data from the JDBC `ResultSet`.

The failing repository method:

```java
findByAssignedUserId
```

Error:

```
org.springframework.orm.jpa.JpaSystemException:
Could not extract column [1] from JDBC ResultSet
[Operation not allowed after ResultSet closed]
```

Root cause:

```
java.sql.SQLException: Operation not allowed after ResultSet closed
```

## Environment

- Spring Framework: 7.0.8
- Spring Data JPA: 4.0.6
- Hibernate ORM: 7.2.19.Final
- MySQL Connector/J: 9.7.0
- HikariCP: 7.0.2
- ShardingSphere JDBC: 5.5.3
- Database: MySQL
- Java: 21

## Stack Trace

```
Caused by: java.sql.SQLException:
Operation not allowed after ResultSet closed

at com.mysql.cj.jdbc.result.ResultSetImpl.checkClosed(ResultSetImpl.java:494)
at com.mysql.cj.jdbc.result.ResultSetImpl.getObject(ResultSetImpl.java:1280)
at com.mysql.cj.jdbc.result.ResultSetImpl.getLong(ResultSetImpl.java:882)
at com.zaxxer.hikari.pool.HikariProxyResultSet.getLong(HikariProxyResultSet.java:...)
at org.apache.shardingsphere.infra.executor.sql.execute.result.query.impl.driver.jdbc.type.stream.JDBCStreamQueryResult.getValue(JDBCStreamQueryResult.java:82)
at org.apache.shardingsphere.infra.merge.result.impl.stream.StreamMergedResult.getValue(StreamMergedResult.java:47)
at org.apache.shardingsphere.driver.jdbc.core.resultset.ShardingSphereResultSet.getLong(ShardingSphereResultSet.java:134)
at org.hibernate.type.descriptor.jdbc.BigIntJdbcType$2.doExtract(BigIntJdbcType.java:76)
```

## Steps to Reproduce

1. Configure a Spring Boot application with:
   - Spring Data JPA
   - Hibernate 7.2.x
   - ShardingSphere JDBC 5.5.3
   - MySQL Connector/J 9.7.0

2. Execute a repository query:

```java
List<Entity> findByAssignedUserId(Long assignedUserId);
```

3. Hibernate fails while hydrating the entity result.

## Expected Behavior

Hibernate should successfully read all columns from the JDBC `ResultSet`.

The `ResultSet` should remain open until Hibernate completes processing the query result.

## Actual Behavior

The JDBC `ResultSet` is closed before Hibernate finishes reading data:

```
ResultSet closed
        ↓
Hibernate tries to extract column value
        ↓
SQLException:
Operation not allowed after ResultSet closed
```

## Analysis

The failure appears to occur inside ShardingSphere JDBC streaming result handling:

```
org.apache.shardingsphere.infra.executor.sql.execute.result.query.impl.driver.jdbc.type.stream.JDBCStreamQueryResult
```

Possible compatibility issue between:

- Hibernate 7.2.x result processing
- ShardingSphere JDBC streaming merge implementation
- MySQL Connector/J 9.7 ResultSet lifecycle handling

## Additional Information

The exception happens during Hibernate entity loading:

```
EntitySelectFetchInitializer.resolveInstance
```

The application does not manually close the `ResultSet`.

## Request

Please investigate whether ShardingSphere JDBC 5.5.3 is fully compatible with Hibernate 7.2.x.

The ResultSet lifecycle should be reviewed to ensure the underlying JDBC ResultSet is not closed before Hibernate completes entity hydration.

## Comment by Nilesh18398 on 2026-07-20

ShardingSphere JDBC 5.5.2 it is not throwing this error

## Comment by terrymanu on 2026-07-23

Hi @Nilesh18398, thanks for reporting this. This looks like a bug—a ShardingSphere-JDBC 5.5.3 JDBC resource-lifecycle regression—not evidence that Hibernate 7.2.x is generally unsupported. The reported 5.5.2/5.5.3 difference aligns with a lifecycle change introduced in 5.5.3, although we still need a minimal reproducer to confirm the exact close sequence.

PR [#35834](https://github.com/apache/shardingsphere/pull/35834) made `AbstractStatementAdapter#close` clear the logical connection’s cached physical connections in auto-commit mode. `DriverDatabaseConnectionManager#clearCachedConnections` closes every cached physical connection. If Hibernate performs a secondary or nested select while an outer result set is still being hydrated, closing the completed inner statement can therefore invalidate the outer result set. `JDBCStreamQueryResult#getValue` is where the closed result set is detected; it does not appear to be the component that closes it.

Please provide:

- A minimal runnable reproducer, including entity relationships and the generated primary/secondary SQL.
- The ShardingSphere configuration, MySQL server version, governance mode, and relevant properties such as `max-connections-size-per-query`.
- Whether the query runs inside a Spring transaction, the effective `Connection#getAutoCommit()` value, and the complete stack trace/SQL log.

I suggest labeling this as `type: bug` and `in: JDBC` and keeping it open. The fix should preserve #35834’s timely connection-release goal while preventing one statement from closing physical connections that still back another live result set. It should include a focused multi-statement lifecycle regression test.

The reply above is based on the analysis below; the detailed reasoning is kept here for reference and follow-up contributors.

### Problem Understanding

- **Issue:** ShardingSphere-JDBC 5.5.3 returns a `ResultSet` that is already closed when Hibernate reads column 1 during entity hydration.
- **Topology:** ShardingSphere-JDBC; MySQL; Standalone/Cluster and registry/config center are not specified.
- **Observed Evidence:** `OBS-1` through `OBS-7`.
- **OBS-1:** The [issue](https://github.com/apache/shardingsphere/issues/39189) reports ShardingSphere-JDBC 5.5.3, MySQL Connector/J 9.7.0, Hibernate 7.2.19.Final, and a stack through `JDBCStreamQueryResult#getValue`, `StreamMergedResult#getValue`, and `ShardingSphereResultSet#getLong`. The [follow-up](https://github.com/apache/shardingsphere/issues/39189#issuecomment-5020324089) says 5.5.2 does not fail.
- **OBS-2:** The [ShardingSphere 5.5.3 overview](https://shardingsphere.apache.org/document/5.5.3/en/overview/) describes ShardingSphere-JDBC as JDBC/ORM compatible and explicitly lists JPA, Hibernate, HikariCP, and MySQL.
- **OBS-3:** In 5.5.2, [`AbstractStatementAdapter#close`](https://github.com/apache/shardingsphere/blob/5.5.2/jdbc/src/main/java/org/apache/shardingsphere/driver/jdbc/adapter/AbstractStatementAdapter.java#L213-L225) closes the current statement’s routed statements and statement manager but does not clear all cached physical connections.
- **OBS-4:** PR [#35834](https://github.com/apache/shardingsphere/pull/35834), merged as `dd423282fa4e8dd597584cd4f0886b320d55d3a3` for milestone 5.5.3, added [`handleAutoCommitAfterExecution`](https://github.com/apache/shardingsphere/blob/5.5.3/jdbc/src/main/java/org/apache/shardingsphere/driver/jdbc/adapter/AbstractStatementAdapter.java#L65-L68) and invokes it from [`AbstractStatementAdapter#close`](https://github.com/apache/shardingsphere/blob/5.5.3/jdbc/src/main/java/org/apache/shardingsphere/driver/jdbc/adapter/AbstractStatementAdapter.java#L228-L242).
- **OBS-5:** In 5.5.3, [`DriverDatabaseConnectionManager#clearCachedConnections`](https://github.com/apache/shardingsphere/blob/5.5.3/jdbc/src/main/java/org/apache/shardingsphere/driver/jdbc/core/connection/DriverDatabaseConnectionManager.java#L117-L122) closes every connection in the logical connection’s `cachedConnections` collection.
- **OBS-6:** PR #35834 did not add unit tests for this behavior, and the same clear-on-statement-close semantics remain in [`AbstractStatementAdapter`](https://github.com/apache/shardingsphere/blob/master/jdbc/src/main/java/org/apache/shardingsphere/driver/jdbc/adapter/AbstractStatementAdapter.java#L69-L72) on current master.
- **OBS-7:** [#33363](https://github.com/apache/shardingsphere/issues/33363) and its fix [#35206](https://github.com/apache/shardingsphere/pull/35206) use the same exception text but concern concurrent SQL federation and fail at `JDBCStreamQueryResult#next` inside the federation engine. #39189 fails at `getValue/getLong` after the result has reached Hibernate, so the call paths and trigger conditions differ.

### Root Cause

- **Observation:** A physical MySQL `ResultSet` is closed before Hibernate finishes reading it (`OBS-1`).
- **Observation:** The behavior begins with 5.5.3, which introduced a statement-close path that closes all physical connections cached by the logical ShardingSphere connection (`OBS-3`, `OBS-4`, `OBS-5`).
- **Inference (`INF-1`, from `OBS-1`, `OBS-3`–`OBS-5`):** A completed secondary or nested statement is likely closed while Hibernate still owns an outer result set. In auto-commit mode, that statement close clears the shared physical-connection cache and invalidates the outer result set.
- **Inference (`INF-2`, from `OBS-1`, `OBS-4`, `OBS-5`):** `JDBCStreamQueryResult#getValue` is the failure-observation point, not the likely lifecycle owner responsible for the premature close.
- **Inference (`INF-3`, from `OBS-1`, `OBS-7`):** This is not a duplicate of #33363/#35206; the shared exception text represents a different root-cause chain.
- **Confidence:** Medium. The version delta and code path align strongly, but the issue lacks the generated SQL, configuration, transaction/auto-commit state, and a deterministic reproducer.

### Problem Analysis

- **Issue Type:** Bug (`OBS-1`–`OBS-6`, `INF-1`).
- **Evidence:** The documented ORM compatibility contract conflicts with a 5.5.3-only resource-lifecycle change capable of invalidating a live result set (`OBS-1`–`OBS-5`).
- **Duplicate Check:** Not a duplicate of #33363/#35206 because the affected execution phase and call path differ (`OBS-7`, `INF-3`).
- **Compatibility Checklist:** Behavior affected; Config, API-SPI, and SQL contracts should remain unchanged.

### Code-Level Design Suggestions

- **Affected Modules:** `jdbc`; `infra/executor` is the failure surface but is not currently the likely close owner (`INF-1`, `INF-2`).
- **Key Classes:** `AbstractStatementAdapter`, `DriverDatabaseConnectionManager`, `ShardingSphereConnection`, `ShardingSpherePreparedStatement`, and `ShardingSphereResultSet`.
- **Required Test Scope:** Under auto-commit, keep an outer result set open, execute and close a second statement on the same logical connection, then verify that the outer result set remains readable. Also verify that physical connections are released after the last owning statement/result set closes, preserving #35834’s resource-release objective.
- **Rollback Hint:** Removing clear-on-any-statement-close would avoid the premature close but could reintroduce #35123’s connection-retention problem. Prefer ownership-aware or last-live-resource release.

### Problem Conclusion

- **Evidence Confidence:** Medium (`OBS-1`–`OBS-7`, `INF-1`–`INF-3`).
- **Severity:** S2—specific ORM/nested-result scenarios are blocked, without evidence of data corruption or a system-wide outage (`OBS-1`, `INF-1`).
- **Impact Scope:** ShardingSphere-JDBC resource lifecycle; observed on MySQL and potentially cross-database because the close-all behavior is database-independent (`OBS-1`, `OBS-5`, `INF-1`).
- **Topology:** JDBC + Standalone/Cluster unknown; registry/config center unknown and not material to the preliminary lifecycle classification (`OBS-1`).
- **Issue Type:** Bug (`OBS-1`–`OBS-6`, `INF-1`).
- **Recommended Labels:** `type: bug`, `in: JDBC` (`OBS-4`, `OBS-5`, `INF-1`).
- **Next Action:** Keep the issue open, obtain the minimal reproducer and auto-commit/transaction evidence, then implement ownership-aware physical-connection release with focused regression coverage (`OBS-1`, `OBS-4`–`OBS-6`, `INF-1`).
- **Compatibility:** Behavior fix only; no intended Config, API-SPI, or SQL change (`OBS-2`, `INF-1`).
- **Regression Scope:** Auto-commit ShardingSphere-JDBC flows with overlapping or nested statements/result sets on one logical connection (`OBS-4`, `OBS-5`, `INF-1`).

## Comment by Nilesh18398 on 2026-07-23

I created a small sample setup with the same configuration, and it works as expected. However, when I use the same configuration in my actual project, it does not work.

I'm attaching the full logs, configuration, and dependencies.

[Details](https://gist.github.com/Nilesh18398/fcba76653240e6a9c246fec369246679)

with spring boot 4.0.7 and java 21.

one more observation 
if i add   @Transactional(readOnly = true) then it is working as expected. with sharding sphere v5.5.2 without this annotation it is working. now i am not sure how many api are failing and at how many places i have to add this tag. (the function is only getting value from db, its a get api)

## Comment by AryamannSingh7 on 2026-07-28

I have a minimal reproducer for this, and I think it explains why @Nilesh18398 couldn't shrink it — the bug has nothing to do with Hibernate. Hibernate just happens to produce the access pattern that triggers it, so trying to reduce it *through* JPA hides the actual cause.

It reproduces with plain JDBC and two statements on one connection:

```java
try (Connection connection = DriverManager.getConnection("jdbc:shardingsphere:classpath:config/driver/driver-fixture-h2-mysql.yaml")) {
    try (Statement statement = connection.createStatement()) {
        statement.execute("DROP TABLE IF EXISTS t_order");
        statement.execute("CREATE TABLE t_order (order_id INT PRIMARY KEY, user_id INT)");
        statement.execute("INSERT INTO t_order (order_id, user_id) VALUES (1, 101), (2, 102)");
    }
    assertTrue(connection.getAutoCommit());
    try (Statement queryStatement = connection.createStatement()) {
        ResultSet resultSet = queryStatement.executeQuery("SELECT order_id, user_id FROM t_order ORDER BY order_id");
        assertTrue(resultSet.next());
        assertThat(resultSet.getInt(1), is(1));
        // secondary statement executed and closed while the outer result set is still live
        try (
                Statement secondaryStatement = connection.createStatement();
                ResultSet secondaryResultSet = secondaryStatement.executeQuery("SELECT COUNT(1) FROM t_order")) {
            assertTrue(secondaryResultSet.next());
        }
        assertThat(resultSet.getInt(2), is(101)); // throws
    }
}
```

That lands on the same path as the original report:

```
JDBCStreamQueryResult.getValue:80 -> StreamMergedResult.getValue:47 -> ShardingSphereResultSet.getInt:134
```

### Why it happens

This matches your read in `OBS-4`/`OBS-5`. `AbstractStatementAdapter#close` calls `safeCloseAndUnregisterStatementManager`, which ends in `handleAutoCommitAfterExecution` -> `DriverDatabaseConnectionManager#clearCachedConnections()`. That closes *every* connection in `cachedConnections`, and that Multimap is owned by the logical connection and shared by all of its statements. A `StatementManager` is created per `Statement` (`ShardingSphereStatement:104`), so closing the secondary statement closes the physical connections still backing the outer statement's open `ResultSet`.

The `connection.getAutoCommit()` gate on that call accounts for both of the reporter's observations:

- **5.5.2 works** — the path didn't exist before #35834.
- **`@Transactional(readOnly = true)` works** — inside a Spring transaction `autoCommit` is false, so the clear never runs. It isn't a fix, it just avoids the gate.

Worth noting `StatementManager#close` only closes its own cached physical statements and never connections, so `clearCachedConnections()` is the only path that can close a connection on statement close.

### Proposed fix

`unregisterStatementManager` already runs immediately before the auto-commit handling, so at that point a non-empty registry means another statement is still open:

```java
protected final void handleAutoCommitAfterExecution(final ShardingSphereConnection connection) throws SQLException {
    if (connection.getAutoCommit() && !connection.hasRegisteredStatementManagers()) {
        connection.getDatabaseConnectionManager().clearCachedConnections();
    }
}
```

with a small `hasRegisteredStatementManagers()` on `ShardingSphereConnection`. This keeps #35834's timely-release behaviour — the last statement to close still releases everything — and only skips the clear while another statement is genuinely live. +68/-1 across 3 files.

I've verified it both ways locally, since I wanted to be sure it narrows the release rather than disabling it. Alongside the regression test I added a second test asserting `cachedConnections` *is* empty once the last statement closes. On unmodified master the reproducer fails and that second test passes; with the fix both pass. Full `jdbc` module is 1211 tests green, `spotless:check` and `checkstyle:check` clean.

Two things I'd like your call on before I raise a PR:

1. Is `ShardingSphereDriverTest` the right home for these, or would you prefer a dedicated multi-statement lifecycle test class as you suggested?
2. Using open statements as the proxy for "a result set may still be live" is deliberately conservative — a statement left open without a live result set will now hold its connections until it closes. Tracking open result sets directly would be tighter but a good deal more invasive. Happy to go that way instead if you'd rather.

Also glad to add an E2E case if you want this covered beyond the unit level.
