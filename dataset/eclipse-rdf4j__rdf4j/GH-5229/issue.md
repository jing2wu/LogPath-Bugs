# FedX: left bind join (i.e. OPTIONAL) may produce incorrect results for a single left bindingset as input

- Issue: https://github.com/eclipse-rdf4j/rdf4j/issues/5229
- Opened by aschwarte10 on 2025-01-15, closed on 2025-01-22
- Labels: 🐞 bug, 📦 fedx
- Fix commit: af17bfaa53e8c318a3aea091a6520f87e0f42971

## Report

### Current Behavior

It can happen that the left bind join, where the left argument produces a single bindingset, can cause an incorrect (empty) result. The situation can occur for advanced source selection cases.

### Expected Behavior

The federation engine correctly evaluates OPTIONAL clauses. For the concrete case a non-empty result is expected

### Steps To Reproduce

Unit test reproducing the issue

```
@ParameterizedTest
	@ValueSource(booleans = { true, false })
	public void test_leftBindJoin_emptyLeftArgumentAsExclusiveGroup(boolean bindLeftJoinOptimizationEnabled)
			throws Exception {

		var endpoints = prepareTest(
				Arrays.asList("/tests/basic/data_emptyStore.ttl", "/tests/basic/data_emptyStore.ttl"));

		Repository repo1 = getRepository(1);
		Repository repo2 = getRepository(2);

		Repository fedxRepo = fedxRule.getRepository();

		fedxRule.setConfig(config -> {
			config.withBoundJoinBlockSize(10);
			config.withEnableOptionalAsBindJoin(bindLeftJoinOptimizationEnabled);
		});

		// add a person
		try (RepositoryConnection conn = repo1.getConnection()) {
			var p = Values.iri("http://ex.com/p1");
			var otherP = Values.iri("http://other.com/p1");
			conn.add(p, OWL.SAMEAS, otherP);
		}

		// add name for person 1
		try (RepositoryConnection conn = repo2.getConnection()) {
			var otherP = Values.iri("http://other.com/p1");
			conn.add(otherP, FOAF.NAME, Values.literal("Person 1"));
		}

		// mark that repo2 for some reason has foaf:age statements (e.g. old cache entry)
		Endpoint repo2Endpoint = endpoints.get(1);
		federationContext().getSourceSelectionCache()
				.updateInformation(new SubQuery(null, FOAF.AGE, null), repo2Endpoint, true);

		fedxRule.enableDebug();

		try {
			// run query which joins results from multiple repos
			// the age does not exist for any person
			try (RepositoryConnection conn = fedxRepo.getConnection()) {
				String query = "PREFIX foaf: <http://xmlns.com/foaf/0.1/> " +
						"SELECT * WHERE { "
						+ " ?person owl:sameAs ?otherPerson . "
						+ " OPTIONAL { ?otherPerson foaf:age ?age .  } " // age does not exist, however is marked as
																			// ExclusiveStatement
						+ "}";

				TupleQuery tupleQuery = conn.prepareTupleQuery(query);
				try (TupleQueryResult tqr = tupleQuery.evaluate()) {
					var bindings = Iterations.asList(tqr);

					Assertions.assertEquals(1, bindings.size());

					for (int i = 1; i <= 1; i++) {
						var p = Values.iri("http://ex.com/p" + i);
						var otherP = Values.iri("http://other.com/p" + i);

						// find the bindingset for the person in the unordered result
						BindingSet bs = bindings.stream()
								.filter(b -> b.getValue("person").equals(p))
								.findFirst()
								.orElseThrow();

						Assertions.assertEquals(otherP, bs.getValue("otherPerson"));

						Assertions.assertEquals(otherP, bs.getValue("otherPerson"));
						Assertions.assertFalse(bs.hasBinding("age"));
					}
				}
			}

		} finally {
			fedxRepo.shutDown();
		}
	}
```

### Version

5.1.0

### Are you interested in contributing a solution yourself?

Yes

### Anything else?

_No response_
