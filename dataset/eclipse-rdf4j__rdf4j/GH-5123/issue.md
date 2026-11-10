# Attempting to add RDF* Data to a Native Repository Breaks the Repository

- Issue: https://github.com/eclipse-rdf4j/rdf4j/issues/5123
- Opened by mnmercer on 2024-09-12, closed on 2025-09-15
- Labels: 🐞 bug
- Fix commit: 52602440b9bbe92132eb1178ecd3fd4d88959fe2

## Report

### Current Behavior

After attempting to add Turtle-star data to a Native Repository, it unsurprisingly throws an error as it appears only MemoryStores have the experimental support for RDF* (correct me if I'm wrong). This is fine, however afterwards no other queries can be run against the Repository, effectively bricking it for an entire application.

### Expected Behavior

After the NativeStore rejects Turtle-star or TriG-star data with an appropriate exception, the Repository should still be usable.

### Steps To Reproduce

1. Run the following code and notice the exception thrown by the second `try` block
```java
String data = """
        @prefix ex: <http://example.org/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
                        
        # Basic triples
        ex:JohnDoe ex:worksAt ex:CompanyX .
                        
        # RDF* triples
        <<ex:JohnDoe ex:worksAt ex:CompanyX>> ex:since "2022-01-01"^^xsd:date .
        """;
File dataDir = Files.createTempDir();
Repository repo = new SailRepository(new NativeStore(dataDir));
try (RepositoryConnection conn = repo.getConnection()) {
    conn.add(new ByteArrayInputStream(data.getBytes()), null, RDFFormat.TURTLE);
} catch (Exception ex) {
    ex.printStackTrace();
}

try (RepositoryConnection conn = repo.getConnection(); RepositoryResult<Statement> result = conn.getStatements(null, null, null)) {
    result.forEach(System.out::println);
} finally {
    dataDir.delete();
}
```

### Version

5.0.2

### Are you interested in contributing a solution yourself?

No

### Anything else?

I first encountered the issue with version 4.3.7, but I confirmed the same issue occurs with 5.0.2.
The initial exception thrown when the data is rejected is `java.lang.IllegalArgumentException: value parameter should be a URI, BNode or Literal` with an additional exception of `java.lang.NullPointerException: Cannot invoke "org.eclipse.rdf4j.common.concurrent.locks.Lock.release()" because "this.txnLock" is null`. Then the second try block throws `java.lang.IllegalArgumentException: value parameter should be a URI, BNode or Literal` again.
