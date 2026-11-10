# FedX does not correctly reduce federation members, when the query contains a FROM clause

- Issue: https://github.com/eclipse-rdf4j/rdf4j/issues/5030
- Opened by aschwarte10 on 2024-06-14, closed on 2024-06-17
- Labels: 🐞 bug, 📦 fedx
- Fix commit: 6413b023475b869fcd9e20ec6baf22acea9c5701

## Report

### Current Behavior

FedX supports interpret the Dataset being defined on the query: if it is of type `FedXDataset`, the  federation is reduced to the members defined by `FedXDataset#getEndpoints()`.

This is a nice means to evaluate a query on a subset of the federation and is generally working fine.

When the query contains a FROM clause, however, the externally passed `Dataset` is wrapped into a `FallbackDataset` (which internally keeps the FedXDataset as primary one.


### Expected Behavior

The federation engine correctly respects an externally passed `FedXDataset`to reduce the federation

### Steps To Reproduce

See test case in the provided PR

### Version

4.8.12

### Are you interested in contributing a solution yourself?

Yes

### Anything else?

Would like to see this merged still as part of 5.0
