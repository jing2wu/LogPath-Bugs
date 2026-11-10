# api allows creation of namespaces with dot

- Issue: https://github.com/michelin/ns4kafka/issues/359
- Opened by piif on 2024-01-26, closed on 2024-01-31
- Labels: bug
- Fix commit: 53e3d071addd8350ccfd736f7346752c975076ac

## Report

## Describe the bug
`kafkactl apply` allows to create a namespace whose name contains a dot, but forbids to use it.

## To Reproduce

1. Create a .yml resource file with
```
apiVersion: v1
kind: Namespace
metadata:
  name: exam.ple
spec:
  kafkaUser: ....
```
2. Apply the resource : creation is accepted
`Namespace "exam.ple" created.`
3. Get the namespaces : namespace is listed

4. Get topics inside this resource : `kafkactl -n exam.ple get topics`
  -> message `Failed because resource forbidden (403).`

## Expected behavior
As this name is invalid, creation should be rejected.

Or dots in names should be accepted, but I suppose it's not because of the confusion it implies (impossible to know if `a.b.c` is topic `c` in namespace `a.b` or topic `b.c` in namespace `a`

## Environment (please complete the following information):
Kafkactl 1.11.3 + ns4kafka 1.11.8

## Comment by loicgreffier on 2024-01-29

Related to security rules denying special chars: https://github.com/michelin/ns4kafka/blob/4c23eedddd66909cfd6d1db111ddcb30d2b00b0d/src/main/java/com/michelin/ns4kafka/security/ResourceBasedSecurityRule.java#L33

Going to do additional tests, but "." in namespace names should not be an issue

## Comment by piif on 2024-01-31

I made a test with a dot added in the regex, and everything seems ok for my use case.

## Comment by jchanaud on 2024-02-01

This makes me realize there's a bug on topic ownership ACL here : https://github.com/michelin/ns4kafka/blob/master/src/main/java/com/michelin/ns4kafka/services/AccessControlEntryService.java#L106
Ns4kafka lets platform teams grant ownership on 2 distinct prefixes (say `my.namespace-` and `my_namespace-`). But for Kafka, this is a conflict. https://github.com/apache/kafka/blob/trunk/clients/src/main/java/org/apache/kafka/common/internals/Topic.java#L108-L110

Unrelated to this PR, the bug was always there. Doesn't sound too critical @loicgreffier

## Comment by loicgreffier on 2024-02-05

Addressing it in #367
