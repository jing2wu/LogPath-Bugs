# ossIndexRemoteErrorWarnOnly is true but maven is stopping for oss index access errors (HttpResponseException: status code: 407, reason phrase: Proxy Authorization Required)

- Issue: https://github.com/dependency-check/DependencyCheck/issues/7976
- Opened by stefano-1973 on 2025-09-25, closed on 2025-09-27
- Labels: bug
- Fix commit: eaa76f9cc425cfb099b327e568cf396ff6e2b5f4

## Report

I have setted 
`<ossIndexWarnOnlyOnRemoteErrors>true</ossIndexWarnOnlyOnRemoteErrors> `
(and also ossIndexUsername and ossIndexPassword) but the maven build stopped (_Finished: FAILURE_) with a connection ERROR, when I'm expecting only a warning.
Am I misundestanding something?


**Version of dependency-check used**
maven dependency check:
```
<groupId>org.owasp</groupId>
<artifactId>dependency-check-maven</artifactId>
<version>12.1.6</version>
```


**Log file**
[ERROR] Failed to execute goal org.owasp:dependency-check-maven:12.1.6:check (default) on project xxxx: One or more exceptions occurred during dependency-check analysis: One or more exceptions occurred during analysis:
[ERROR] AnalysisException: Failed to request component-reports
[ERROR] caused by DownloadFailedException: https://ossindex.sonatype.org/api/v3/component-report - Server status: 407 - Server reason: Proxy Authorization Required
[ERROR] caused by HttpResponseException: status code: 407, reason phrase: Proxy Authorization Required
.................................
[ERROR] -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoExecutionException
[ERROR] 
[ERROR] After correcting the problems, you can resume the build with the command
[ERROR]   mvn <goals> -rf   xxxxxxxx
........
Finished: FAILURE
