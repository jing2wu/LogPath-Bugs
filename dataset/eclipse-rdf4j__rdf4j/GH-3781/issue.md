# Create/update namespace endpoint does not validate the prefix and the URI

- Issue: https://github.com/eclipse-rdf4j/rdf4j/issues/3781
- Opened by nikolaykolev on 2022-04-08, closed on 2022-11-29
- Labels: 🐞 bug
- Fix commit: a08dc48d71f4f8f429ad9defdcfa634f3f6cf5e2

## Report

### Current Behavior

I can create/update a prefix with invalid prefix and URI, there's no validation in the endpoint.

### Expected Behavior

There should be a validation of the URI at least, I'm not sure about the prefix, but I guess creating a prefix with a space or < > in it should not be allowed as well.

### Steps To Reproduce

1. Execute the following:
curl 'http://localhost:7222/repositories/x/namespaces/asd%20c' -X 'PUT' --data-raw 'http://xxx.com'
2. The namespace is created successfully although the prefix has a space in it (asd c)

1. Execute the following
curl 'http://localhost:7222/repositories/x/namespaces/asd' -X 'PUT' --data-raw 'httpxxxcom'
2. The namespace is created with URI httpxxxcom

### Version

4.0.0-M2

### Are you interested in contributing a solution yourself?

_No response_

### Anything else?

_No response_

## Comment by damyan-ognyanov on 2022-11-22

There is a regression in the `NamespaceController` introduced with the previous fix. The controller accepts invalid prefixes like `22` or `2abc` but reject some valid prefixes, like `abc-de` or `abc.de`
