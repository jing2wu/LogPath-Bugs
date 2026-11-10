# Possible bug with aggregates and fts (solr) search.

- Issue: https://github.com/eclipse-rdf4j/rdf4j/issues/5310
- Opened by nguyenm100 on 2025-04-17, closed on 2025-06-23
- Labels: 🐞 bug
- Fix commit: 433cddc556b0bf0ca4efd133bf8bbaa0c63b4a1e

## Report

### Current Behavior

Putting this out early in case in jogs anyone's memory.  I don't have a solid case right now but will update as we go. But running this query sometimes produces an error (works other times so not sure if it's data related).  Any tips on how or where to debug would be grateful.

    PREFIX search: <http://www.openrdf.org/contrib/lucenesail#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>
    prefix owl: <http://www.w3.org/2002/07/owl#>

    SELECT ?subj (MAX(?score) as ?score) ?definition ?label ?type ?graph WHERE {
      VALUES ?graph { /* bunch of graph iris */ }

      GRAPH ?graph {
        ?subj search:matches [
          search:score ?score ;
          search:property rdfs:label ;
          search:snippet ?snippet ;
          search:query "*debu*" ;
        ]

        optional {
          ?subj skos:definition ?definition .
        }

        optional {
          ?subj skos:prefLabel ?label .
        }

        optional {
          ?subj rdfs:isDefinedBy ?modelIRI .
        }

        ?subj rdf:type ?type .
      }
    }
    GROUP BY ?subj ?label ?type ?definition ?graph
    ORDER BY DESC(?score)

(sometimes) gives the stack:

```
requestId=04b77fb7-8153-4233-bfab-49b22275b37c Query evaluation exception caught
org.eclipse.rdf4j.query.QueryEvaluationException: Unsupported value expr type: class org.eclipse.rdf4j.query.algebra.Max
	at org.eclipse.rdf4j.query.algebra.evaluation.impl.DefaultEvaluationStrategy.precompile(DefaultEvaluationStrategy.java:907)
	at org.eclipse.rdf4j.query.algebra.evaluation.optimizer.ConstantOptimizer$ConstantVisitor.meetUnaryValueOperator(ConstantOptimizer.java:228)
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:364)
	at org.eclipse.rdf4j.query.algebra.Max.visit(Max.java:28)
	at org.eclipse.rdf4j.query.algebra.GroupElem.visitChildren(GroupElem.java:69)
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:269)
	at org.eclipse.rdf4j.query.algebra.GroupElem.visit(GroupElem.java:64)
	at org.eclipse.rdf4j.query.algebra.Group.visitChildren(Group.java:141)
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meetUnaryTupleOperator(AbstractSimpleQueryModelVisitor.java:595)
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:259)
	at org.eclipse.rdf4j.query.algebra.Group.visit(Group.java:133)
	at org.eclipse.rdf4j.query.algebra.UnaryTupleOperator.visitChildren(UnaryTupleOperator.java:72)
	at org.eclipse.rdf4j.query.algebra.Extension.visitChildren(Extension.java:99)
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meetUnaryTupleOperator(AbstractSimpleQueryModelVisitor.java:595)
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:234)
	at org.eclipse.rdf4j.query.algebra.Extension.visit(Extension.java:94)
	at org.eclipse.rdf4j.query.algebra.UnaryTupleOperator.visitChildren(UnaryTupleOperator.java:72)
	at org.eclipse.rdf4j.query.algebra.Order.visitChildren(Order.java:90)
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meetUnaryTupleOperator(AbstractSimpleQueryModelVisitor.java:595)
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:404)
	at org.eclipse.rdf4j.query.algebra.Order.visit(Order.java:81)
	at org.eclipse.rdf4j.query.algebra.UnaryTupleOperator.visitChildren(UnaryTupleOperator.java:72)
	at org.eclipse.rdf4j.query.algebra.Projection.visitChildren(Projection.java:86)
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meetUnaryTupleOperator(AbstractSimpleQueryModelVisitor.java:595)
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:414)
	at org.eclipse.rdf4j.query.algebra.Projection.visit(Projection.java:80)
	at org.eclipse.rdf4j.query.algebra.UnaryTupleOperator.visitChildren(UnaryTupleOperator.java:72)
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:430)
	at org.eclipse.rdf4j.query.algebra.QueryRoot.visit(QueryRoot.java:41)
	at org.eclipse.rdf4j.query.algebra.evaluation.optimizer.ConstantOptimizer.optimize(ConstantOptimizer.java:77)
	at org.eclipse.rdf4j.query.algebra.evaluation.impl.DefaultEvaluationStrategy.optimize(DefaultEvaluationStrategy.java:330)
	at org.eclipse.rdf4j.sail.base.SailSourceConnection.evaluateInternal(SailSourceConnection.java:251)
	at org.eclipse.rdf4j.sail.lmdb.LmdbStoreConnection.evaluateInternal(LmdbStoreConnection.java:137)
	at org.eclipse.rdf4j.sail.helpers.AbstractSailConnection.evaluate(AbstractSailConnection.java:333)
	at org.eclipse.rdf4j.sail.helpers.SailConnectionWrapper.evaluate(SailConnectionWrapper.java:115)
	/* SNIP */
	at org.eclipse.rdf4j.sail.helpers.AbstractSailConnection.evaluate(AbstractSailConnection.java:333)
	at org.eclipse.rdf4j.sail.helpers.SailConnectionWrapper.evaluate(SailConnectionWrapper.java:115)
	at org.eclipse.rdf4j.sail.lucene.LuceneSailConnection.evaluateInternal(LuceneSailConnection.java:473)
	at org.eclipse.rdf4j.sail.lucene.LuceneSailConnection.evaluate(LuceneSailConnection.java:406)
	at org.eclipse.rdf4j.repository.sail.SailTupleQuery.evaluate(SailTupleQuery.java:52)
	at org.eclipse.rdf4j.http.server.repository.handler.DefaultQueryRequestHandler.evaluateQuery(DefaultQueryRequestHandler.java:102)
	at org.eclipse.rdf4j.http.server.repository.handler.DefaultQueryRequestHandler.evaluateQuery(DefaultQueryRequestHandler.java:81)
	at org.eclipse.rdf4j.http.server.repository.handler.AbstractQueryRequestHandler.handleQueryRequest(AbstractQueryRequestHandler.java:82)
	at org.eclipse.rdf4j.http.server.repository.AbstractRepositoryController.handleRequestInternal(AbstractRepositoryController.java:53)
	at org.springframework.web.servlet.mvc.AbstractController.handleRequest(AbstractController.java:177)
	at org.springframework.web.servlet.mvc.SimpleControllerHandlerAdapter.handle(SimpleControllerHandlerAdapter.java:51)
	at org.springframework.web.servlet.DispatcherServlet.doDispatch(DispatcherServlet.java:1072)
	at org.springframework.web.servlet.DispatcherServlet.doService(DispatcherServlet.java:965)
	at org.springframework.web.servlet.FrameworkServlet.processRequest(FrameworkServlet.java:1006)
	at org.springframework.web.servlet.FrameworkServlet.doPost(FrameworkServlet.java:909)
	at javax.servlet.http.HttpServlet.service(HttpServlet.java:681)
	at org.springframework.web.servlet.FrameworkServlet.service(FrameworkServlet.java:883)
	at javax.servlet.http.HttpServlet.service(HttpServlet.java:764)
	at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:227)
	at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:162)
	at org.apache.tomcat.websocket.server.WsFilter.doFilter(WsFilter.java:53)
	at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:189)
	at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:162)
	at com.github.ziplet.filter.compression.CompressingFilter.doFilter(CompressingFilter.java:263)
	at org.apache.catalina.core.ApplicationFilterChain.internalDoFilter(ApplicationFilterChain.java:189)
	at org.apache.catalina.core.ApplicationFilterChain.doFilter(ApplicationFilterChain.java:162)
	at org.apache.catalina.core.StandardWrapperValve.invoke(StandardWrapperValve.java:197)
	at org.apache.catalina.core.StandardContextValve.invoke(StandardContextValve.java:97)
	at org.apache.catalina.authenticator.AuthenticatorBase.invoke(AuthenticatorBase.java:541)
	at org.apache.catalina.core.StandardHostValve.invoke(StandardHostValve.java:135)
	at org.apache.catalina.valves.ErrorReportValve.invoke(ErrorReportValve.java:92)
	at org.apache.catalina.valves.HealthCheckValve.invoke(HealthCheckValve.java:102)
	at org.apache.catalina.valves.AbstractAccessLogValve.invoke(AbstractAccessLogValve.java:687)
	at org.apache.catalina.core.StandardEngineValve.invoke(StandardEngineValve.java:78)
	at org.apache.catalina.connector.CoyoteAdapter.service(CoyoteAdapter.java:360)
	at org.apache.coyote.http11.Http11Processor.service(Http11Processor.java:399)
	at org.apache.coyote.AbstractProcessorLight.process(AbstractProcessorLight.java:65)
	at org.apache.coyote.AbstractProtocol$ConnectionHandler.process(AbstractProtocol.java:890)
	at org.apache.tomcat.util.net.NioEndpoint$SocketProcessor.doRun(NioEndpoint.java:1787)
	at org.apache.tomcat.util.net.SocketProcessorBase.run(SocketProcessorBase.java:49)
	at org.apache.tomcat.util.threads.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1191)
	at org.apache.tomcat.util.threads.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:659)
	at org.apache.tomcat.util.threads.TaskThread$WrappingRunnable.run(TaskThread.java:61)
	at java.base/java.lang.Thread.run(Thread.java:840)
```

### Expected Behavior

no error

### Steps To Reproduce

will try and find a repro case.

### Version

5.0.3

### Are you interested in contributing a solution yourself?

Perhaps?

### Anything else?

_No response_

## Comment by hmottestad on 2025-04-18

ConstantOptimizer seems to encounter a MAX(...) function and thinks it's a constant. Not sure why, but might be that you are adding something invalid inside the VALUES clause. That would be my first guess.

## Comment by hmottestad on 2025-04-18

You also have `(MAX(?score) as ?score)`. Might be better to use two different variables. Maybe the constant optimizer is able to optimise the ?score variable, but doesn't know what to do when the variable is used on both sides of an effective bind.

## Comment by nguyenm100 on 2025-04-18

what's odd is that it only happens some times. one of my guys just stripped out everything in the sparql but the original select, search query, and group and ran it repeatedly 200 times and it happened on the 92nd call. race condition and/or state bug would be my guess. will see if we can repo off local lucene instead of solr.

## Comment by hmottestad on 2025-04-18

Still happening when you remove the max() function or when you use two different variable names in the projection?

## Comment by odysa on 2025-04-21

I tried `(MAX(?score) as ?score1). This issue still happened.
```sparql
PREFIX search: <http://www.openrdf.org/contrib/lucenesail#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subj (MAX(?score) as ?scoreabcd)
  WHERE {
  ?subj search:matches [
	      search:query "*Inti*";
	      search:property rdfs:label;
	      search:score ?score;
	      search:snippet ?snippet
     ]
}
GROUP BY ?subj
```
I am trying to create a minimal reproducible example.

## Comment by odysa on 2025-04-23

Hello @hmottestad, I am able to reproduce it.

1. Use `MAX` or `MIN` in the search query
2. Use `TupleFunctionEvaluationMode.NATIVE` or `TupleFunctionEvaluationMode.SERVICE`. But using `TRIPLE_SOURCE` is ok
3. There's only 1 triple in the result. No issue happened if there're more than 1 triple.

Maybe it's a corner case of applying `MAX` or `MIN` to one single triple under certain evaluationMode?

```java

class Main {

	public static void main(final String[] args) {
		// see https://github.com/eclipse-rdf4j/rdf4j/tree/main/compliance/solr
		System.setProperty(
				"solr.solr.home", "<your-path-to-embedded-solr>");

		MemoryStore memoryStore = new MemoryStore();
		LuceneSail lucenesail = new LuceneSail();

		lucenesail.setParameter(LuceneSail.INDEX_CLASS_KEY, SolrIndex.class.getName());
		lucenesail.setParameter(SolrIndex.SERVER_KEY, "embedded:");

		lucenesail.setBaseSail(memoryStore);
		// have issue
		lucenesail.setEvaluationMode(TupleFunctionEvaluationMode.NATIVE);

		// have issue
		// lucenesail.setEvaluationMode(TupleFunctionEvaluationMode.SERVICE);

		// NO issue. Working Properly
		// lucenesail.setEvaluationMode(TupleFunctionEvaluationMode.TRIPLE_SOURCE);

		SailRepository repo = new SailRepository(lucenesail);

		repo.init();

		try (RepositoryConnection con = repo.getConnection()) {
			con.begin();
			final Resource subject = Values.iri(RDF.NAMESPACE, "subject1");
			final Literal object = Values.literal("object1");
			con.add(subject, RDFS.LABEL, object);

			// If there are 2 triples, no issue. Only happen when there is only one triple
//			final Resource subject2 = Values.iri(RDF.NAMESPACE, "subject2");
//			final Literal object2 = Values.literal("object2");
//			con.add(subject2, RDFS.LABEL, object2);

			con.commit();
		}

		List<BindingSet> results;

		try (RepositoryConnection con = repo.getConnection()) {
			TupleQuery tq = con.prepareTupleQuery(QueryLanguage.SPARQL, SEARCH_QUERY);
			results = QueryResults.asList(tq.evaluate());
		}
		System.out.println(results);
	}

	private static String SEARCH_QUERY =
			"""
					PREFIX search: <http://www.openrdf.org/contrib/lucenesail#>
					PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
					
					SELECT ?subj (MAX(?score) as ?score)
					  WHERE {
					  ?subj search:matches [
							  search:query "*object*";
							  search:property rdfs:label;
							  search:score ?score;
							  search:snippet ?snippet
						 ]
					}
					GROUP BY ?subj
					""";
}
```

```bash
891 [main] ERROR org.eclipse.rdf4j.query.algebra.evaluation.optimizer.ConstantOptimizer - Query evaluation exception caught
org.eclipse.rdf4j.query.QueryEvaluationException: Unsupported value expr type: class org.eclipse.rdf4j.query.algebra.Min
	at org.eclipse.rdf4j.query.algebra.evaluation.impl.DefaultEvaluationStrategy.precompile(DefaultEvaluationStrategy.java:907) ~[rdf4j-queryalgebra-evaluation-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.evaluation.optimizer.ConstantOptimizer$ConstantVisitor.meetUnaryValueOperator(ConstantOptimizer.java:228) ~[rdf4j-queryalgebra-evaluation-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:369) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.Min.visit(Min.java:28) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.GroupElem.visitChildren(GroupElem.java:69) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:269) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.GroupElem.visit(GroupElem.java:64) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.Group.visitChildren(Group.java:141) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meetUnaryTupleOperator(AbstractSimpleQueryModelVisitor.java:595) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:259) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.Group.visit(Group.java:133) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.UnaryTupleOperator.visitChildren(UnaryTupleOperator.java:72) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.Extension.visitChildren(Extension.java:99) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meetUnaryTupleOperator(AbstractSimpleQueryModelVisitor.java:595) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:234) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.Extension.visit(Extension.java:94) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.UnaryTupleOperator.visitChildren(UnaryTupleOperator.java:72) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.Projection.visitChildren(Projection.java:86) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meetUnaryTupleOperator(AbstractSimpleQueryModelVisitor.java:595) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:414) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.Projection.visit(Projection.java:80) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.UnaryTupleOperator.visitChildren(UnaryTupleOperator.java:72) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.helpers.AbstractSimpleQueryModelVisitor.meet(AbstractSimpleQueryModelVisitor.java:430) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.QueryRoot.visit(QueryRoot.java:41) ~[rdf4j-queryalgebra-model-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.evaluation.optimizer.ConstantOptimizer.optimize(ConstantOptimizer.java:77) ~[rdf4j-queryalgebra-evaluation-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.query.algebra.evaluation.impl.DefaultEvaluationStrategy.optimize(DefaultEvaluationStrategy.java:330) ~[rdf4j-queryalgebra-evaluation-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.sail.base.SailSourceConnection.evaluateInternal(SailSourceConnection.java:251) ~[rdf4j-sail-base-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.sail.helpers.AbstractSailConnection.evaluate(AbstractSailConnection.java:333) ~[rdf4j-sail-api-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.sail.helpers.SailConnectionWrapper.evaluate(SailConnectionWrapper.java:115) ~[rdf4j-sail-api-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.sail.lucene.LuceneSailConnection.evaluateInternal(LuceneSailConnection.java:473) ~[rdf4j-sail-lucene-api-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.sail.lucene.LuceneSailConnection.evaluate(LuceneSailConnection.java:406) ~[rdf4j-sail-lucene-api-5.0.3.jar:5.0.3]
	at org.eclipse.rdf4j.repository.sail.SailTupleQuery.evaluate(SailTupleQuery.java:52) ~[rdf4j-repository-sail-5.0.3.jar:5.0.3]
	at org.example.Main.main(Main.java:60) ~[classes/:?]

```

## Comment by odysa on 2025-04-23

Under `TRIPLE_SOURCE` mode, `LuceneSaiConnection` uses the `TupleFunctionEvaluationStrategy` while others modes use the `DefaultEvaluationStrategy`
https://github.com/eclipse-rdf4j/rdf4j/blob/b33d91485502d2f5266916c0581960e41b8f28b5/core/sail/lucene-api/src/main/java/org/eclipse/rdf4j/sail/lucene/LuceneSailConnection.java#L445

But `TupleFunctionEvaluationStrategy` has deprecated since 4.3.0.
```java
/**
 * An {@link EvaluationStrategy} that has support for {@link TupleFunction}s.
 *
 * @deprecated since 4.3.0. Use {@link DefaultEvaluationStrategy} instead.
 */
```

## Comment by odysa on 2025-04-23

Hello @hmottestad, I found the root cause.

In `ConstantOptimizer`, it precompiles and evaluates the constant value in the value expression.
https://github.com/eclipse-rdf4j/rdf4j/blob/b33d91485502d2f5266916c0581960e41b8f28b5/core/queryalgebra/evaluation/src/main/java/org/eclipse/rdf4j/query/algebra/evaluation/optimizer/ConstantOptimizer.java#L223-L229

The example query meets the condition if `isConstant`  because the `MAX` expr has a numerical literal value
https://github.com/eclipse-rdf4j/rdf4j/blob/b33d91485502d2f5266916c0581960e41b8f28b5/core/queryalgebra/evaluation/src/main/java/org/eclipse/rdf4j/query/algebra/evaluation/optimizer/ConstantOptimizer.java#L346-L348


![Image](https://github.com/user-attachments/assets/1ca2c358-1a63-4cd4-a8ae-69477662e3bb)

The `precompile` in `DefaultEvaluationStrategy` does not handle the cases of `MAX`(and other aggregate expr).
It will throw an exception of `unspported expr type ...`
https://github.com/eclipse-rdf4j/rdf4j/blob/b33d91485502d2f5266916c0581960e41b8f28b5/core/queryalgebra/evaluation/src/main/java/org/eclipse/rdf4j/query/algebra/evaluation/impl/DefaultEvaluationStrategy.java#L834-L840

The literal value in `MAX` is from the `BindingSetAssignmentVisitor`, which replaces the `?score` with the literal.
https://github.com/eclipse-rdf4j/rdf4j/blob/b33d91485502d2f5266916c0581960e41b8f28b5/core/queryalgebra/evaluation/src/main/java/org/eclipse/rdf4j/query/algebra/evaluation/optimizer/BindingSetAssignmentInlinerOptimizer.java#L57-L63

However, if there are more than 1 triple, the `biningSet` in `BindingSetAssignmentVisitor` will be `null`. It's because if the `bsa.getBindingSets` has the size  > 1, the `bindingSet` will not be assigned.
https://github.com/eclipse-rdf4j/rdf4j/blob/b33d91485502d2f5266916c0581960e41b8f28b5/core/queryalgebra/evaluation/src/main/java/org/eclipse/rdf4j/query/algebra/evaluation/optimizer/BindingSetAssignmentInlinerOptimizer.java#L46-L54

Therefore, it does not hit the if clause, and the value in `MAX` will be null. The `precompile` mentioned above will be skipped. As a result, no exception will be thrown if there are more than 1 triples.
https://github.com/eclipse-rdf4j/rdf4j/blob/b33d91485502d2f5266916c0581960e41b8f28b5/core/queryalgebra/evaluation/src/main/java/org/eclipse/rdf4j/query/algebra/evaluation/optimizer/BindingSetAssignmentInlinerOptimizer.java#L59

## Comment by odysa on 2025-04-23

BTW, to easily reproduce it, you may the below test case to https://github.com/eclipse-rdf4j/rdf4j/blob/b33d91485502d2f5266916c0581960e41b8f28b5/testsuites/lucene/src/main/java/org/eclipse/testsuite/rdf4j/sail/lucene/AbstractLuceneSailTest.java#L71
```java
@Test
public void testMaxFunction(){
	StringBuffer buffer = new StringBuffer();
	buffer.append("PREFIX search: <http://www.openrdf.org/contrib/lucenesail#>\n");
	buffer.append("SELECT ?subj (MAX(?score) as ?score)\n");
	buffer.append("WHERE {\n");
	buffer.append("  ?subj search:matches [\n");
	buffer.append("    search:query \"must_be_unique*\";\n");
	buffer.append("    search:property <urn:predicate1> ;\n");
	buffer.append("    search:score ?score;\n");
	buffer.append("    search:snippet ?snippet\n");
	buffer.append("  ]\n");
	buffer.append("}\n");
	buffer.append("GROUP BY ?subj\n");
	String q = buffer.toString();

	
	sail.setEvaluationMode(TupleFunctionEvaluationMode.NATIVE);
	configure(sail);

	List<BindingSet> results;
	try (RepositoryConnection connection = repository.getConnection()){
		connection.begin();
		connection.add(SUBJECT_3, PREDICATE_1, vf.createLiteral("must_be_unique"));
		connection.commit();
	}
	try (RepositoryConnection connection = repository.getConnection()) {
		TupleQuery query = connection.prepareTupleQuery(q);
		results = QueryResults.asList(query.evaluate());
	}
	assertEquals(1, results.size());
}
```
Expected to see the error in the std. `QueryEvaluationException` is caught and handled by logging. Is there any way to make this test case fail?
```
org.eclipse.rdf4j.query.QueryEvaluationException: Unsupported value expr type: class org.eclipse.rdf4j.query.algebra.Max
```

## Comment by odysa on 2025-04-23

Maybe we can fix it by checking whether the parent node is a `GroupElem` because we cannot replace the child of `GroupElem` with a `ValueConstant`. The `GroupElem` requires children nodes to be `AggregateOperator`
```java
boolean parentIsGroup = unaryValueOp.getParentNode() instanceof GroupElem;
if (!parentIsGroup && isConstant(unaryValueOp.getArg())) {
	try {
		Value value = strategy.precompile(unaryValueOp, context).evaluate(EmptyBindingSet.getInstance());
		unaryValueOp.replaceWith(new ValueConstant(value));
```

## Comment by JervenBolleman on 2025-04-23

@odysa maybe we should implement a specific constant visitor method for the GroupElem types. Where we can implement a specific logic for constants.

## Comment by odysa on 2025-04-23

@JervenBolleman 
Can we add an extra field in the `GroupElem` to allow it hold a `ValueConstant`?
```java
public class GroupElem extends AbstractQueryModelNode {
	private AggregateOperator operator;
	private ValueConstant valueConstant;

	@Override
	public <X extends Exception> void visitChildren(QueryModelVisitor<X> visitor) throws X {
		if(valueConstant != null) {
			valueConstant.visit(visitor);
			return;
		}
		operator.visit(visitor);
	}
	
	@Override
	public void replaceChildNode(QueryModelNode current, QueryModelNode replacement) {
	if (operator == current) {
		replacement.setParentNode(this);
		if (replacement instanceof ValueConstant) {
			valueConstant = (ValueConstant) replacement;
		} else if (replacement instanceof AggregateOperator) {
			operator = (AggregateOperator) replacement;
		}
	}
}
```

In the method of `precompile` in `DefaultEvaluationStrategy`
```java
else if (expr instanceof AbstractAggregateOperator) {
	final Var var = (Var)((AbstractAggregateOperator) expr).getArg();
	return prepare(var, context);
} else if (expr == null) {
	throw new IllegalArgumentException("expr must not be null");
} 
```

## Comment by JervenBolleman on 2025-04-24

@odysa I was wondering if instead we should make a new ConstantAggregateOperator instead? Then we might be able to skip a lot of work in the GroupIterator.


Test case to add into the ConstantOptimizerTest

```java
	@Test
	public void testAggregateOptimization() throws RDF4JException {
		String query = "prefix ex: <ex:>" + "select (max(1) AS ?a) \n " + "where {\n" + "?x a ?z \n"
				+ "}";

		ParsedQuery pq = QueryParserUtil.parseQuery(QueryLanguage.SPARQL, query, null);
		EvaluationStrategy strategy = new DefaultEvaluationStrategy(new EmptyTripleSource(), null);
		TupleExpr original = pq.getTupleExpr();

		final AlgebraFinder finder = new AlgebraFinder();
		original.visit(finder);
		assertTrue(finder.groupElemFound);

		// reset for re-use on optimized query
		finder.reset();

		QueryBindingSet constants = new QueryBindingSet();
		constants.addBinding("x", SimpleValueFactory.getInstance().createLiteral("foo"));
		constants.addBinding("z", SimpleValueFactory.getInstance().createLiteral("bar"));

		TupleExpr optimized = optimize(pq.getTupleExpr().clone(), constants, strategy);

		optimized.visit(finder);
		assertThat(finder.functionCallFound).isFalse();

		CloseableIteration<BindingSet> result = strategy.precompile(optimized)
				.evaluate(
						new EmptyBindingSet());
		assertNotNull(result);
		assertTrue(result.hasNext());
		BindingSet bindings = result.next();
		assertTrue(bindings.hasBinding("a"));
		assertEquals(1, ((Literal) bindings.getBinding("a").getValue()).intValue());
	}
```

Then add


```java
	@Override
		public void meet(Avg node) throws RuntimeException {
			optimizeUnaryValueExpr(node);
		}

		@Override
		public void meet(Max node) throws RuntimeException {
			optimizeUnaryValueExpr(node);
		}

		private void optimizeUnaryValueExpr(UnaryValueOperator node) {
			if (isConstant(node.getArg())) {
				QueryModelNode parent = node.getParentNode();
				if (parent instanceof GroupElem) {
					GroupElem ge = (GroupElem) parent;
					ge.setOperator(new ConstantAggregateOperator(node.getArg()));
				} else if (parent instanceof ExtensionElem) {
					ExtensionElem ee = (ExtensionElem) parent;
					ee.replaceChildNode(node, node.getArg());
				}
			}
		}

		@Override
		public void meet(Min node) throws RuntimeException {
			optimizeUnaryValueExpr(node);
		}

		@Override
		public void meet(Sample node) throws RuntimeException {
			optimizeUnaryValueExpr(node);
		}

		@Override
		public void meet(Sum node) throws RuntimeException {
			optimizeUnaryValueExpr(node);
		}
```

to the ConstantVisitor. 

Which is enough to pass that specific test, but unlikely to fix all issues.

## Comment by JervenBolleman on 2025-04-24

@odysa I made a branch with my current thoughts roughly implemented. What do you think?

## Comment by odysa on 2025-04-29

@JervenBolleman My only concern about this approach is that `optimize` becomes `tryOptimize`. We allow the `ConsantOptimizer` to fail and do nothing. If you believe it's ok for optimizers, we can try this solution.

## Comment by JervenBolleman on 2025-04-30

@odysa optimize is always a try. Mostly, the `optimize` should not produce
a non SPARQL algebra that breaks expectations downstream. When moving to
java 17 we can introduce some sealed classes and tighten this up.
Especially as this might be expanded again into an actual SPARQL query when
generating a SERVICE call. It especially should not leave a TupleExpr in a
broken state.


On Tue, Apr 29, 2025 at 7:07 PM Chengxu Bian ***@***.***>
wrote:

> *odysa* left a comment (eclipse-rdf4j/rdf4j#5310)
> <https://github.com/eclipse-rdf4j/rdf4j/issues/5310#issuecomment-2839614747>
>
> @JervenBolleman <https://github.com/JervenBolleman> My only concern about
> this approach is that optimize becomes tryOptimize. We allow the
> ConsantOptimizer to fail and do nothing. If you believe it's ok for
> optimizers, we can try this solution.
>
> —
> Reply to this email directly, view it on GitHub
> <https://github.com/eclipse-rdf4j/rdf4j/issues/5310#issuecomment-2839614747>,
> or unsubscribe
> <https://github.com/notifications/unsubscribe-auth/AAHQYFNGSKHMXRMYLKPWSG3236WTJAVCNFSM6AAAAAB3LW5JEOVHI2DSMVQWIX3LMV43OSLTON2WKQ3PNVWWK3TUHMZDQMZZGYYTINZUG4>
> .
> You are receiving this because you were mentioned.Message ID:
> ***@***.***>
>


-- 
Jerven Bolleman
***@***.***

## Comment by odysa on 2025-05-29

Could someone please assign this to me? We're currently blocked by this bug, even after trying the temporary fix.

## Comment by JervenBolleman on 2025-05-30

> Could someone please assign this to me? We're currently blocked by this bug, even after trying the temporary fix.

@odysa I would be happy to see a different pull requests? does the optimizer change I propose not work for you?

## Comment by odysa on 2025-05-31

Hi @JervenBolleman ,

Sorry, I may be misunderstanding where things currently stand, so I wanted to clarify:

Do you already have a PR in flight?

Or were you waiting on more input from my side?

## Comment by JervenBolleman on 2025-06-05

@odysa the error was deeper, and not actually in the query optimizer for this case. I think I have  a fix, but changes the explanations printed out (not showing QueryRoot right now). Once those i fix those then my [draft pull request](https://github.com/eclipse-rdf4j/rdf4j/pull/5344) can be reviewed.

## Comment by odysa on 2025-06-06

Thank you @JervenBolleman , I’ll need a few days to go through

## Comment by JervenBolleman on 2025-06-06

@odysa a quick workaround might be to make sure that in the GroupIterator: when precompiling a max operator etc call this on the argument not on the aggregate operator itself.

## Comment by JervenBolleman on 2025-06-12

Ok @odysa my thinking was completely wrong. The error was in how empty results interacted with group by or agregate constants. I think it is fixed in https://github.com/eclipse-rdf4j/rdf4j/pull/5351, but I did not run the complete test suite yet.
