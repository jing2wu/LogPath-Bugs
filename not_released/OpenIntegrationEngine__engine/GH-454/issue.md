# [BUG] Oracle MirthDB does not seem to store transformed or encoded content

- Issue: https://github.com/OpenIntegrationEngine/engine/issues/454
- Opened by mgaffigan on 2026-09-19, closed on 2026-09-24
- Labels: bug
- Fix commit: 864ede756b0d99f061f8778ba209adf3f2600066

## Report

Repro:
* Configure mirthdb to live in oracle
* Send a message
* Retrieve the message

Expected:
* Source Encoded and transformed content are available

Actual:
https://github.com/OpenIntegrationEngine/engine/actions/runs/35471826818
```text
   [0] Source status=TRANSFORMED
         raw="OIE,Awesome\n"
         sourceMap={batchSequenceId=1, batchId=1, destinationSet=[1], batchComplete=false}
         connectorMap={}
         metaDataMap={}
   [1] Destination 1 status=SENT
         encoded="<delimited><row><Name>OIE</Name><Description>Awesome</Description></row></delimited>"
         sent="<com.mirth.connect.connectors.vm.VmDispatcherProperties version="4.6.0">\n  <pluginProperties/>\n  <destinationConnectorProperties version="4.6.0">\n    <queueEnabled>false</queueEnabled>\n    <sendFirst>false</sendFirst>\n    <retryIntervalMillis>10000</retryIntervalMillis>\n    <regenerateTemplate>false</regenerateTemplate>\n    <retryCount>0</retryCount>\n    <rotate>false</rotate>\n    <includeFilterTransformer>false</includeFilterTransformer>\n    <threadCount>1</threadCount>\n    <threadAssignmentVariable></threadAssignmentVariable>\n    <validateResponse>false</validateResponse>\n    <resourceIds class="linked-hash-map">\n      <entry>\n        <string>Default Resource</string>\n        <string>[Default Resource]</string>\n      </entry>\n    </resourceIds>\n    <queueBufferSize>1000</queueBufferSize>\n    <reattachAttachments>true</reattachAttachments>\n  </destinationConnectorProperties>\n  <channelId>none</channelId>\n  <channelTemplate>&lt;delimited&gt;&lt;row&gt;&lt;Name&gt;OIE&lt;/Name&gt;&lt;Description&gt;Awesome&lt;/Description&gt;&lt;/row&gt;&lt;/delimited&gt;</channelTemplate>\n  <mapVariables/>\n</com.mirth.connect.connectors.vm.VmDispatcherProperties>"
         response="<response>\n  <status>SENT</status>\n  <message></message>\n  <statusMessage>Message routed successfully to channel id: none</statusMessage>\n</response>"
         sourceMap={batchSequenceId=1, batchId=1, destinationSet=[1], batchComplete=false}
         connectorMap={}
         metaDataMap={}
```

This is not reproducible on Derby, SQL Server, MySQL, nor Postgres.

## Comment by mgaffigan on 2026-09-19

Clanker diagnosis:

> Source processed-raw/transformed/encoded are written through the JDBC batch path in [Channel.java:1734-1751](vscode-webview://0i01bk2h66hjhfh4puherkt458dqik8ude3r6eakpcpul0i16gtm/donkey/src/main/java/com/mirth/connect/donkey/server/channel/Channel.java#L1734-L1751) — several dao.batchInsertMessageContent(...) calls followed by one dao.executeBatchInsertMessageContent(...).
> 
> [JdbcDao.batchInsertMessageContent](vscode-webview://0i01bk2h66hjhfh4puherkt458dqik8ude3r6eakpcpul0i16gtm/donkey/src/main/java/com/mirth/connect/donkey/server/data/jdbc/JdbcDao.java#L211-L243) grabs the cached PreparedStatement, calls addBatch(), and then in its finally calls closeDatabaseObjectIfNeeded(statement).
> 
> In the base class that's a no-op ([JdbcDao.java:2510](vscode-webview://0i01bk2h66hjhfh4puherkt458dqik8ude3r6eakpcpul0i16gtm/donkey/src/main/java/com/mirth/connect/donkey/server/data/jdbc/JdbcDao.java#L2510)), so the statement stays open in [CachedPreparedStatementSource](vscode-webview://0i01bk2h66hjhfh4puherkt458dqik8ude3r6eakpcpul0i16gtm/donkey/src/main/java/com/mirth/connect/donkey/server/data/jdbc/CachedPreparedStatementSource.java) and the batch accumulates. Derby/Postgres/MySQL/SQL Server all work.
> [OracleJdbcDao](vscode-webview://0i01bk2h66hjhfh4puherkt458dqik8ude3r6eakpcpul0i16gtm/donkey/src/main/java/com/mirth/connect/donkey/server/data/jdbc/OracleJdbcDao.java#L28-L35) overrides it to actually close Statements.
> So on Oracle each addBatch() is immediately thrown away with the statement, the cache sees statement.isClosed() and hands out a fresh one next time, and executeBatchInsertMessageContent ends up calling executeBatch() on a brand-new, empty statement. Zero rows inserted, no exception.
> 
> This isn't batch-message-specific — it's the normal source path, so every message on Oracle loses its source transformed/encoded content. It's been that way since the upstream closeDatabaseObjectIfNeeded refactor (caad0677c); nothing before [120-delimited-batch](vscode-webview://0i01bk2h66hjhfh4puherkt458dqik8ude3r6eakpcpul0i16gtm/ci/tests/120-delimited-batch/channels/01-csv/messages/01-batch/01/source_transformed) asserted source transformed content, so CI never caught it.
