# [Bug,HTTP] Query parameters are not sent with DELETE requests

- Issue: https://github.com/apache/dolphinscheduler/issues/18696
- Opened by ThreeFire1 on 2026-10-12, closed on 2026-10-15
- Labels: bug, backend
- Fix commit: c366e26217d589378eaa98b64f9b29808927a662

## Report

### Search before asking

- [x] I had searched in the [issues](https://github.com/apache/dolphinscheduler/issues?q=is%3Aissue) and found no similar issues.


### What happened

When testing an HTTP task on 3.4.3, I noticed that parameters added under HTTP Parameters are not sent when the request method is DELETE.

For example, with URL /capture?existing=1 and a separate parameter jobId=42 (type PARAMETER), the server receives:
`DELETE /capture?existing=1`

The jobId parameter is missing. Switching to GET sends it correctly. Adding jobId=42 directly to the URL also works with DELETE.

### What you expected to happen

The server should receive both parameters:
`DELETE /capture?existing=1&jobId=42`

The [HTTP task docs](https://github.com/apache/dolphinscheduler/blob/043060b0587842ab2d7815048a6bc8534dad7ab3/docs/docs/en/guide/task/http.md) describe HTTP Parameters as GET/DELETE request parameters.

### How to reproduce

1. Use a test HTTP endpoint that logs incoming requests and returns 200.
2. Create an HTTP task with method DELETE and URL `http://<host>:<port>/capture?existing=1`.
3. Add an HTTP parameter: name jobId, type PARAMETER, value 42.
4. Save and run the workflow, then check the endpoint's log. The request contains existing=1 but no jobId.

### Anything else

HttpTask.sendDeleteRequest() does not pass the configured query parameters to OkHttpUtils.delete(). The GET path passes them to OkHttpUtils.get().
I also reproduced this in a unit test on dev commit 043060b0587842ab2d7815048a6bc8534dad7ab3.

### Version

3.4.3

### Are you willing to submit PR?

- [x] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's [Code of Conduct](https://www.apache.org/foundation/policies/conduct)

## Comment by kittimzhe on 2026-10-14

Confirmed the mechanism — `HttpTask#sendDeleteRequest` (dolphinscheduler-task-http/.../HttpTask.java:193-203) never collects the request parameters at all:

```java
private OkHttpResponse sendDeleteRequest() {
    ...
    OkHttpResponse okHttpResponse = OkHttpUtils.delete(httpParameters.getUrl(), okHttpRequestHeaders,
            httpParameters.getConnectTimeout(), ...);
```

Compare `sendGetRequest` (:149-158), which passes `getRequestParams()` through to `OkHttpUtils.get`, where `addUrlParams` appends them to the URL. The `delete` overloads (`OkHttpUtils.java:249-279`) take no parameter map, so PARAMETER-typed HTTP Parameters are silently dropped for DELETE — matching your repro (`DELETE /capture?existing=1` with `jobId` lost, while GET sends it).

Claiming this. Fix shape: a `delete` overload that accepts the parameter map and runs it through the same `addUrlParams` the GET path uses, plus `sendDeleteRequest` collecting `getRequestParams()` like GET does — so `DELETE /capture?existing=1` + `jobId=42` sends `?existing=1&jobId=42`, consistent with the HTTP task docs describing the parameters as GET/DELETE request parameters.
