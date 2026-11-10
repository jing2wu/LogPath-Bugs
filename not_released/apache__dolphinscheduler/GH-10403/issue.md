# [Bug] [dolphinscheduler-spi] JSONUtils parse LocalDateTime error

- Issue: https://github.com/apache/dolphinscheduler/issues/10403
- Opened by HomminLee on 2022-06-10, closed on 2022-06-27
- Labels: bug, backend
- Fix commit: dafed572d17cd08dae1c1decf389f0dd4241fdf7

## Report

### Search before asking

- [X] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

When I try to set Custom Parameters of SQL Task Node with OUT type, I get such error msg:

```
[ERROR] 2022-06-10 09:32:40.206 +0000 org.apache.dolphinscheduler.spi.utils.JSONUtils:[215] - json to map exception!
com.fasterxml.jackson.databind.exc.MismatchedInputException: Cannot deserialize instance of `java.lang.String` out of START_OBJECT token
 at [Source: (String)"{"id":1,"code":5791423019648,"name":"cat","version":1,"description":"","project_code":5791415412992,"release_state":1,"user_id":1,"global_params":"[]","flag":1,"locations":"[{\"taskCode\":5791416706432,\"x\":-5.5,\"y\":147.5}]","warning_group_id":null,"timeout":0,"tenant_id":-1,"execution_type":0,"create_time":{},"update_time":{}}"; line: 1, column: 313] (through reference chain: java.util.LinkedHashMap["create_time"])
        at com.fasterxml.jackson.databind.exc.MismatchedInputException.from(MismatchedInputException.java:59)
        at com.fasterxml.jackson.databind.DeserializationContext.reportInputMismatch(DeserializationContext.java:1445)
        at com.fasterxml.jackson.databind.DeserializationContext.handleUnexpectedToken(DeserializationContext.java:1219)
        at com.fasterxml.jackson.databind.DeserializationContext.handleUnexpectedToken(DeserializationContext.java:1129)
```

In msg, `create_time` had wrong value `{}`. Thought debug, I found sql task Convert datatime to LocalDateTime. And then, JSONUtils parse this LocalDateTime object to `{}`.

I write test case, this situation is reproduced:

```
    @Test
    public void localDateTimeToString() {
        TimeZone.setDefault(TimeZone.getTimeZone("Asia/Shanghai"));
        String time = "2022-02-22 13:38:24";
        Date date = DateUtils.stringToDate(time);
        LocalDateTime localDateTime = LocalDateTime.ofInstant(date.toInstant(), ZoneId.systemDefault());
        String json = JSONUtils.toJsonString(localDateTime);
        // console print:  {}
        System.out.println(json);
        Assert.assertEquals(json, "\"" + time + "\"");
    }
```



### What you expected to happen

JSONUtils parse LocalDateTime object to correct value.

### How to reproduce

Run the above test case.

### Anything else

_No response_

### Version

3.0.0-beta-1

### Are you willing to submit PR?

- [X] Yes I am willing to submit a PR!

### Code of Conduct

- [X] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)

## Comment by github-actions[bot] on 2022-06-10

Thank you for your feedback, we have received your issue, Please wait patiently for a reply.
* In order for us to understand your request as soon as possible, please provide detailed information、version or pictures.
* If you haven't received a reply for a long time, you can [join our slack](https://s.apache.org/dolphinscheduler-slack) and send your question to channel `#troubleshooting`
