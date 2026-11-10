# Sending an empty SPARQL update with application/sparql-update leads to NPE

- Issue: https://github.com/eclipse-rdf4j/rdf4j/issues/3624
- Opened by avataar on 2022-01-20, closed on 2022-01-30
- Labels: 🐞 bug
- Fix commit: c5341de15796189857fdc2e6937cae522a423819

## Report

### Current Behavior

Sending an empty SPARQL update using application/sparql-update and bare SPARQL in the body like this:
```
curl -X POST http://lom.local:7200/repositories/testo/statements -H 'content-type: application/sparql-update' -d ''
```
results in an NPE in StatementsController.

Sending an empty SPARQL update using application/x-www-form-urlencoded and SPARQL via the update parameter seemingly works (no errors, no side effects):
```
curl -X POST http://lom.local:7200/repositories/testo/statements -H 'content-type: application/x-www-form-urlencoded' -d 'update='
```

### Expected Behavior

Both of these should behave identically. The current implementation parses an empty update as a valid ParsedUpdate with zero expressions. I don't believe there are any valid use cases where empty updates should be considered or executed and a more sensible behaviour would be to throw an error.

### Steps To Reproduce

_No response_

### Version

3.7.4

### Are you interested in contributing a solution yourself?

Yes

### Anything else?

_No response_
