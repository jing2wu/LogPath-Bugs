# FedX: optimizer does not insert (external) bindings prior to source selection

- Issue: https://github.com/eclipse-rdf4j/rdf4j/issues/5227
- Opened by aschwarte10 on 2025-01-13, closed on 2025-01-24
- Labels: 🐞 bug, 📦 fedx
- Fix commit: 98d8944c3132f9df031aa80b82df2d9e8595a0e0

## Report

### Current Behavior

The FedX Optimizer is missing to inject bindings (e.g. from Query#setBinding()) into the statement patterns.

This can cause poor behavior in caching.

### Expected Behavior

FedX injects bindings properly

### Steps To Reproduce

```
TupleQuery tq = conn.prepareTupleQuery("SELECT * WHERE { ?subject a ?type }");
tq.setBinding("subject", subjectIri);
```

Inspect the query plan during optimization

### Version

5.1.0

### Are you interested in contributing a solution yourself?

Yes

### Anything else?

_No response_
