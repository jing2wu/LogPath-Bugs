# Selection by identifier is broken in SOQL

- Issue: https://github.com/kbss-cvut/jopa/issues/407
- Opened by ledsoft on 2026-01-27, closed on 2026-01-28
- Labels: bug
- Fix commit: f27941e1ff2265cc0cf7fa4010c8af211cc37016

## Report

The SPARQL generated from the following query will not support setting parameters corresponding to the SOQL, because the variable will be named `?x`:

```
SELECT p.username FROM Person p WHERE p.uri = :personUri
```

Leads to this SPARQL:
```
SELECT ?username WHERE { 
  ?x a <http://krizik.felk.cvut.cz/ontologies/jopa/types#Person> . 
  ?x <http://krizik.felk.cvut.cz/ontologies/jopa/attributes#username> ?username . 
}
```
