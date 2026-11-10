# Connector Deployment Null Pointer

- Issue: https://github.com/kafka-ops/julie/issues/378
- Opened by Fobhep on 2021-11-04, closed on 2021-11-12
- Labels: bug
- Fix commit: 365b42699760d9a1eaf0e871b28d613bd09e56d8

## Report

Trying to deploy 2 connectors in 2 connect clusters.

This is an excerpt form the julie-props file:

``` 
bootstrap.servers=group0-broker3:9094,group0-broker1:9094,group0-broker2:9094
security.protocol=SSL
ssl.keystore.location=client1-keystore.jks
ssl.keystore.password=password
ssl.key.password=password
ssl.truststore.location=client1-truststore.jks
ssl.truststore.password=password


topology.builder.access.control.class = com.purbon.kafka.topology.roles.RBACProvider

schema.registry.url=https://group0-schemareg:8081
topology.builder.mds.ksqldb.cluster.id=""
topology.builder.mds.server=https://group0-broker3:8090
topology.builder.mds.user=user1
topology.builder.mds.password=****
topology.builder.mds.kafka.cluster.id=MTCzrgiZR4Kised0g0TF0Q
topology.builder.mds.kafka.connect.cluster.id=connect-cluster
topology.builder.mds.schema.registry.cluster.id=schema-registry

platform.servers.connect.0=connect1:https://group0-connectschema1.kafka:8083
platform.servers.basic.auth.0=connect1@user1:****

platform.servers.connect.1=connect2:https://group0-connectschema2.kafka:8083
platform.servers.basic.auth.1=connect2@user1:***

topology.state.cluster.enabled=true

```
Please note that I can easily curl `https://group0-connectschema1.kafka:8083/connectors` by using the provided username and password.


This is my descriptor.yaml
```
---
context: "context"
source: "src"
projects:
  - name: "connect"
    connectors:
      artefacts:
        - path: "connectors/connector1.json"
          server: "connect1"
          name: "creditcard"
        - path: "connectors/connector2.json"
          server: "connect2"
          name: "product"
    topics:
      - name: creditcard
      - name: product
```

Julie results in the following error:
```
[~/julie] 23s $ julie-ops --brokers broker1:9094 --clientConfig julie.properties --topology testcases/
log4j:WARN No appenders could be found for logger (org.apache.kafka.clients.admin.AdminClientConfig).
log4j:WARN Please initialize the log4j system properly.
log4j:WARN See http://logging.apache.org/log4j/1.2/faq.html#noconfig for more info.
Exception in thread "main" java.lang.NullPointerException
        at com.purbon.kafka.topology.AccessControlManager.buildProjectActions(AccessControlManager.java:132)
        at com.purbon.kafka.topology.AccessControlManager.apply(AccessControlManager.java:80)
        at com.purbon.kafka.topology.JulieOps.run(JulieOps.java:236)
        at com.purbon.kafka.topology.JulieOps.run(JulieOps.java:265)
        at com.purbon.kafka.topology.CommandLineInterface.processTopology(CommandLineInterface.java:207)
        at com.purbon.kafka.topology.CommandLineInterface.run(CommandLineInterface.java:156)
        at com.purbon.kafka.topology.CommandLineInterface.main(CommandLineInterface.java:146)
```

## Comment by purbon on 2021-11-12

Hi @Fobhep , the issue you're seeing here is because of missing access_control field in the topology.

Try something like this:

```yaml
context: "context"
projects:
  - name: "projectA"
    connectors:
      artifacts:
        - path: "connectors/source-jdbc.json"
          server: "connect"
          name: "source-jdbc"
        - path: "connectors/sink-jdbc.json"
          server: "connect1"
          name: "sink-jdbc"
      access_control:
```

that is going to certainly not have this issue.

We should certainly make this field better handled in the serdes process.

## Comment by Fobhep on 2021-11-15

@purbon thanks for the quick response
