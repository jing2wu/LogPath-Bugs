# Service enhancer queries violate the specification

- Issue: https://github.com/apache/jena/issues/2992
- Opened by galgonek on 2025-02-05, closed on 2025-02-06
- Labels: bug
- Fix commit: ac26a8ad9a61cbf7b100526cdc11c662bedad4cb

## Report

### Version

5.3.0

### What happened?

I used the service enhancer plugin and executed the following query:

```sparql
PREFIX sachem: <http://bioinfo.uochb.cas.cz/rdf/v1.0/sachem#>

SELECT * WHERE {  
  VALUES ?STRUCTURE { "[He]" "[Ar]" }
  SERVICE <loop:bulk+5:https://idsm.elixir-czech.cz/sparql/endpoint/chebi> {
    ?COMPOUND sachem:substructureSearch [ sachem:query ?STRUCTURE ]
  }
}
```

After running this query, the following query is sent to the specified endpoint:

```
SELECT  *
WHERE
  {   { ?COMPOUND  <http://bioinfo.uochb.cas.cz/rdf/v1.0/sachem#substructureSearch>  _:b0 .
        _:b0      <http://bioinfo.uochb.cas.cz/rdf/v1.0/sachem#query>  "[He]"
        BIND(0 AS ?__idx__)
      }
    UNION
      {   { ?COMPOUND  <http://bioinfo.uochb.cas.cz/rdf/v1.0/sachem#substructureSearch>  _:b0 .
            _:b0      <http://bioinfo.uochb.cas.cz/rdf/v1.0/sachem#query>  "[Ar]"
            BIND(1 AS ?__idx__)
          }
        UNION
          { BIND(1000000000 AS ?__idx__) }
      }
  }
ORDER BY ASC(?__idx__)
```

I believe that this generated query violates the SPARQL specification. According to the [specification](https://www.w3.org/TR/sparql11-query/#bgpBNodeLabels), _when using blank nodes of the form \_:abc,  labels for blank nodes are scoped to the basic graph pattern. A label can be used in only a single basic graph pattern in any query._ However, the generated query uses the label `_:b0` in two separate basic graph patterns, which, in my opinion, contradicts this rule.

### Relevant output and stacktrace

```shell

```

### Are you interested in making a pull request?

None

## Comment by afs on 2025-02-05

https://www.sparql.org/query-validator.html (which is the Jena 5.3.0 parser) agrees:

```
Line 8, column 93: Blank node label reuse not allowed at this point: _:b0
```

## Comment by Aklakan on 2025-02-05

Mhm, the code takes the original query's service op (algebra form of the graph pattern) and creates a union from the substituted ops. The procedure needs to be extended to rename the blank nodes for each union member.

## Comment by Aklakan on 2025-02-06

I opened a PR with a fix which has the reported example as a test case.
