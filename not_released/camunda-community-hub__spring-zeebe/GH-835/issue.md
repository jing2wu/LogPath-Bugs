# [Connectors] Issue when using SimpleAuthentication with Operate

- Issue: https://github.com/camunda-community-hub/spring-zeebe/issues/835
- Opened by johnBgood on 2024-06-12, closed on 2024-06-12
- Labels: bug
- Fix commit: 59874c8dea55a36fa06cab3003c73c167a7f75b8

## Report

**Describe the bug**

Discussion [here](https://camunda.slack.com/archives/C02JLRNQQ05/p1717703404347039).

Operate (8.4.8, and anything newer than 8.5.2 ) enabled CRSF protection. This means there are multiple `Set-Cookie` headers (`OPERATE-SESSION`, and `OPERATE-X-CRSF-TOKEN`), which triggers an error in [SimpleAuthentication](https://github.com/camunda-community-hub/spring-zeebe/blob/main/camunda-sdk-java/java-common/src/main/java/io/camunda/common/auth/SimpleAuthentication.java#L46):

```java
                  if (cookieHeader.getValue().startsWith(cookiePrefix)) {
                    cookieCandidate = response.getHeader("Set-Cookie").getValue();
                    break;
                  }
```

**To Reproduce**

Use the docker compose files provided in camunda-platform, run the stack using `CAMUNDA_PLATFORM_VERSION=8.6.0-alpha2`. 
Try to start the connectors runtime => error when polling process definitions from Operate.

**Expected behavior**

Polling works without error.

**Log/Stacktrace**

<details><summary>Full Stacktrace</summary>
 <p>

```
2024-06-06T19:46:16.066Z ERROR 1 --- [   scheduling-1] i.c.c.r.i.i.ProcessDefinitionImporter    : Failed to import process definitions

java.lang.RuntimeException: Unable to authenticate
	at io.camunda.common.auth.SimpleAuthentication.retrieveToken(SimpleAuthentication.java:58)
	at io.camunda.common.auth.SimpleAuthentication.getTokenHeader(SimpleAuthentication.java:79)
	at io.camunda.common.http.DefaultHttpClient.retrieveToken(DefaultHttpClient.java:207)
	at io.camunda.common.http.DefaultHttpClient.post(DefaultHttpClient.java:148)
	at io.camunda.operate.CamundaOperateClient.searchProcessDefinitionResults(CamundaOperateClient.java:46)
	at io.camunda.connector.runtime.inbound.importer.ProcessDefinitionSearch.query(ProcessDefinitionSearch.java:72)
	at io.camunda.connector.runtime.inbound.importer.ProcessDefinitionImporter.scheduleImport(ProcessDefinitionImporter.java:55)
	at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(Unknown Source)
	at java.base/java.lang.reflect.Method.invoke(Unknown Source)
	at org.springframework.scheduling.support.ScheduledMethodRunnable.runInternal(ScheduledMethodRunnable.java:130)
	at org.springframework.scheduling.support.ScheduledMethodRunnable.lambda$run$2(ScheduledMethodRunnable.java:124)
	at io.micrometer.observation.Observation.observe(Observation.java:499)
	at org.springframework.scheduling.support.ScheduledMethodRunnable.run(ScheduledMethodRunnable.java:124)
	at org.springframework.scheduling.support.DelegatingErrorHandlingRunnable.run(DelegatingErrorHandlingRunnable.java:54)
	at java.base/java.util.concurrent.Executors$RunnableAdapter.call(Unknown Source)
	at java.base/java.util.concurrent.FutureTask.runAndReset(Unknown Source)
	at java.base/java.util.concurrent.ScheduledThreadPoolExecutor$ScheduledFutureTask.run(Unknown Source)
	at java.base/java.util.concurrent.ThreadPoolExecutor.runWorker(Unknown Source)
	at java.base/java.util.concurrent.ThreadPoolExecutor$Worker.run(Unknown Source)
	at java.base/java.lang.Thread.run(Unknown Source)
Caused by: org.apache.hc.client5.http.ClientProtocolException: null
	at org.apache.hc.client5.http.impl.classic.CloseableHttpClient.execute(CloseableHttpClient.java:261)
	at org.apache.hc.client5.http.impl.classic.CloseableHttpClient.execute(CloseableHttpClient.java:188)
	at org.apache.hc.client5.http.impl.classic.CloseableHttpClient.execute(CloseableHttpClient.java:162)
	at io.camunda.common.auth.SimpleAuthentication.retrieveToken(SimpleAuthentication.java:38)
	... 19 common frames omitted
Caused by: org.apache.hc.core5.http.ProtocolException: multiple 'Set-Cookie' headers found
	at org.apache.hc.core5.http.message.HeaderGroup.getHeader(HeaderGroup.java:267)
	at org.apache.hc.client5.http.impl.classic.CloseableHttpResponse.getHeader(CloseableHttpResponse.java:143)
	at io.camunda.common.auth.SimpleAuthentication.lambda$retrieveToken$0(SimpleAuthentication.java:46)
	at org.apache.hc.client5.http.impl.classic.CloseableHttpClient.execute(CloseableHttpClient.java:247)
	... 22 common frames omitted
```

</p>
</details>

**Environment:**
- Deployment: SM<!-- [SaaS or SM (Self Managed) and version] -->
