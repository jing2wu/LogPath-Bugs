# [P0] SSRF 门闩未覆盖主出站路径：BaseAdapter → TracingWebClientFactory → WebClientPool 完全绕过校验

- Issue: https://github.com/Lincoln-cn/JAiRouter/issues/114
- Opened by Lincoln-cn on 2026-09-25, closed on 2026-09-25
- Labels: bug
- Fix commit: 042746bd8303b8fd8fd94d1e7ba5dd32c245e8e1

## Report

﻿## 严重级别
P0（确认）

## 类别
安全 / SSRF

## 位置
`src/main/java/org/unreal/modelrouter/router/adapter/BaseAdapter.java:97-108`、`monitor/tracing/client/TracingWebClientFactory.java:44-48`、`router/http/WebClientPool.java:72-108`、`config/core/helper/SsrfGuard.java`

## 证据
```java
// BaseAdapter.java:97-108 —— 主路径，直接调用追踪工厂，未做任何 SSRF 校验
private WebClient getWebClientForInstance(final ModelRouterProperties.ModelInstance instance) {
    String baseUrl = instance.getBaseUrl();
    try {
        var tracingFactory = ApplicationContextProvider.getBean(TracingWebClientFactory.class);
        return tracingFactory.createTracingWebClient(baseUrl);   // ← 无校验
    } catch (Exception e) {
        return ApplicationContextProvider.getBean(WebClientCacheManager.class)
                .getOrCreate(baseUrl);                            // ← 只有这条兜底路径才校验
    }
}
```
```java
// TracingWebClientFactory.java:44-48 —— 零校验转发
public WebClient createTracingWebClient(final String baseUrl) {
    return webClientPool.getOrCreate(baseUrl, builder -> builder.filter(tracingInterceptor));
}
```
```java
// WebClientCacheManager.java:40-42 —— R3-P0 的校验被放在了“兜底路径”里
// R3-P0：出站前校验，覆盖历史脏数据（云元数据等）
final String safeBaseUrl = SsrfGuard.validateOutboundBaseUrl(baseUrl);
```
`SsrfGuard.validateOutboundBaseUrl` 的全部调用点（grep 确认）只有：`ConfigSyncService:218/237`、`ServiceInstanceManager:103/147`（配置写入侧）、`AdapterTestService:48/102/178/202`（连通性测试侧）、`WebClientCacheManager:42`（兜底侧）。`WebClientPool` 与 `TracingWebClientFactory` 均无调用。

## 根因分析
Round 3 的 R3-P0 SSRF 修复把校验放在了 `WebClientCacheManager.createWebClient()`——也就是 `TracingWebClientFactory` 查不到 bean 时的**兜底分支**。而每个真实代理请求走的是 `BaseAdapter` 的**第一分支**（直接 `TracingWebClientFactory` → `WebClientPool`），该分支只做 `WebClient.builder().baseUrl(baseUrl)`，从不校验。因此 R3-P0 注释所声称的“覆盖历史脏数据”在热路径上并未生效：校验层次放错了位置（应在所有出站 WebClient 的唯一收敛点 `WebClientPool`）。

## 触发场景
任何一个未经过配置写入侧校验的 baseUrl 进入运行时即可命中，例如：(1) 直接改库 / 历史遗留脏数据（正是注释声称要覆盖的场景）；(2) DNS rebinding —— 配置写入时域名解析为正常 IP 通过校验，实际连接时重新解析到 169.254.169.254；(3) 任何绕过 `ServiceInstanceManager` / `ConfigSyncService` 的写入路径。

## 影响范围
命中云元数据（169.254.169.254、metadata.google.internal、fd00:ec2::/64）可窃取实例凭证（AWS/GCP/Azure IAM role token），并可横向探测内网。影响所有经过网关的流量。

## 修复建议
把校验下沉到唯一收敛点 `WebClientPool.createWebClient()`：在构造 WebClient 前调用 `SsrfGuard.validateOutboundBaseUrl(baseUrl)` 并用返回值作为 baseUrl。这样 `TracingWebClientFactory`、`WebClientCacheManager`、以及未来任何新增调用方都自动被覆盖，且缓存键也应使用规范化后的 URL，避免同一目标存在多个缓存项。注意 `UrlSecurityValidator` 依据既有设计**不封禁私网/回环**（仅拦链路本地与云元数据），因此该改动不会破坏“适配器测试访问内网 AI 服务”的既有用法。

## 验证方式
新增单测：对 `WebClientPool.getOrCreate("http://169.254.169.254")` 断言抛 `SecurityException`；对 `http://127.0.0.1:8080`、`http://10.0.0.1` 断言仍可创建（保持既有语义）。回归：`mvnw test`。

## 审计信息
- 审计轮次：Round 5（继 round1–round4 已合并修复之后的回归 + 补漏）
- 基线：`github/master` @ `fa7fdc99`
- 基线门闩：`mvnw test` → Tests run: 3682, Failures: 0, Errors: 0, Skipped: 7（BUILD SUCCESS）
- 复现前请确认该问题在基线提交上仍然存在
