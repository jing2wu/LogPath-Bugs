# Streams management requires both a read and write topic defined when using ACLs.

- Issue: https://github.com/kafka-ops/julie/issues/364
- Opened by gitfrog0 on 2021-10-25, closed on 2021-11-01
- Labels: bug
- Fix commit: c3b76b10fa66986adf983e455af8d9bf8a06e262

## Report

**Describe the bug**
Using the streams management, it is required to add a definition of at least one write topic and at least one read topic.  If not, a NullPointerException is thrown.

**To Reproduce**
Steps to reproduce the behavior:
1. Add a streams configuration, with a principal and applicationId, without any topics listed
2. Exception in thread "main" java.lang.NullPointerException
	at com.purbon.kafka.topology.roles.acls.AclsBindingsBuilder.streamsAppStream(AclsBindingsBuilder.java:236)

**Expected behavior**
Should be the same as adding a ksql definition.  A topic does not need to be listed.
The necessary ACLs are created for the application id.  A Topic ACL prefixed with applicationId with ALL operation.
A Group ACL prefixed with applicationId with READ operation.

**Additional context**
This will allow the streams application to receive proper ACLs for its internal topics, and also allow the input,output,intermdiate topics to be granted access via the topics definition.
Workaround is to add the streams application with the ksql definition.

## Comment by purbon on 2021-10-29

Hi @gitfrog0 thanks for your report. I do have however a few questions about it. Generally speaking a KStream application would always has an input (source) and a target topic (toTable or To). Do you seen any particular case when both are not required?

Thanks
