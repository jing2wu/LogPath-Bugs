# Query syntax errors are not propagated to the client

- Issue: https://github.com/eclipse-rdf4j/rdf4j/issues/4073
- Opened by DenitsaStoianova on 2022-07-20, closed on 2022-07-24
- Labels: 🐞 bug
- Fix commit: 136844164c1ca154837d94c807b1b89abfeef0f0

## Report

### Current Behavior

Running a query with syntax errors through HTTPRepository will result in generic exception to be thrown. When transaction request is handled through TransactionController during query execution, wrapped exceptions are not checked and the client receives QueryInterruptedException instead of MalformedQueryException with the appropriate error message.

### Expected Behavior

When query with syntax error is executed, MalformedQueryException with descriptive message must be sent to the client.

### Steps To Reproduce

1. Connect to remote repository on server through HTTPRepository 
2. Execute some query with syntax errors:

```
		String testQuery = "#PREFIX ex: <http://example.com#>\n" +
				"select * where { \n" +
				"\t?s ex:data ?o .\n" +
				"}";

		try (RepositoryConnection connection = repository.getConnection()) {
			connection.begin();
			TupleQuery query = connection.prepareTupleQuery(testQuery);
			try (TupleQueryResult result = query.evaluate()) {
				// process query results
			}
			connection.commit();
		}
```
3. The following exception will be thrown:

```
Caused by: org.eclipse.rdf4j.query.QueryInterruptedException
	at org.eclipse.rdf4j.http.client.SPARQLProtocolSession.execute(SPARQLProtocolSession.java:1052)
	at org.eclipse.rdf4j.http.client.SPARQLProtocolSession.executeOK(SPARQLProtocolSession.java:1004)
	at org.eclipse.rdf4j.http.client.SPARQLProtocolSession.sendTupleQueryViaHttp(SPARQLProtocolSession.java:760)
	at org.eclipse.rdf4j.http.client.SPARQLProtocolSession.getBackgroundTupleQueryResult(SPARQLProtocolSession.java:655)
	at org.eclipse.rdf4j.http.client.SPARQLProtocolSession.sendTupleQuery(SPARQLProtocolSession.java:366)
	at org.eclipse.rdf4j.repository.http.HTTPTupleQuery.evaluate(HTTPTupleQuery.java:48)
```

4. While the server has more descriptive message:

`org.eclipse.rdf4j.http.server.ClientHTTPException: MALFORMED QUERY: org.eclipse.rdf4j.query.parser.sparql.ast.VisitorException: QName 'ex:data' uses an undefined prefix`


### Version

4.0.3

### Are you interested in contributing a solution yourself?

Yes

### Anything else?

_No response_
