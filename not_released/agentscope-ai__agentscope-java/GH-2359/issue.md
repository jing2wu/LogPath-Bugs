# [Bug]:连续会话压缩时会过滤上一轮摘要，导致原始用户意图丢失

- Issue: https://github.com/agentscope-ai/agentscope-java/issues/2359
- Opened by CyberXavier on 2026-07-22, closed on 2026-07-24
- Labels: bug
- Fix commit: 17fee94f4fc3bf308903785d99eaaec9c20325b1

## Report

### 问题描述

`ConversationCompactor` 在进行第二次及后续会话压缩时，会先从待总结的消息前缀中删除上一轮压缩生成的 `__compaction_summary__` 消息，然后再调用模型生成新摘要。

这会导致链式压缩无法继承上一轮摘要中的原始用户意图。经过多轮压缩后，会话目标会逐渐漂移；在特定切割情况下，待总结前缀甚至会变成空列表，最终生成：

```text
No previous conversation history.
```

此时原始用户请求会从模型上下文中完全消失。

### 影响版本

已确认以下版本存在该问题：

```text
AgentScope Java v2.0.0
```

当前 `main` 分支的 `2.0.1-SNAPSHOT` 中相关实现也仍然存在。

### 相关代码

文件：

```text
agentscope-harness/src/main/java/io/agentscope/harness/agent/memory/compaction/ConversationCompactor.java
```

当前实现先切分前缀和尾部，然后立即过滤旧摘要：

```java
List<Msg> prefix =
        filterSummaryMessages(new ArrayList<>(messages.subList(0, cutoff)));
List<Msg> tail = new ArrayList<>(messages.subList(cutoff, messages.size()));
```

后续摘要生成直接使用已经过滤后的 `prefix`：

```java
summarizePrefix(prefix, config)
```

过滤逻辑为：

```java
static List<Msg> filterSummaryMessages(List<Msg> messages) {
    return messages.stream()
            .filter(m -> !SUMMARY_MSG_NAME.equals(m.getName()))
            .collect(Collectors.toList());
}
```

而压缩摘要本身使用以下标识：

```java
public static final String SUMMARY_MSG_NAME = "__compaction_summary__";
```

因此，上一轮摘要不会参与下一轮摘要生成。

### 复现过程

假设第一次压缩后，工作上下文为：

```text
USER name=__compaction_summary__
  SESSION INTENT：判断小程序展示的号源是否实时

ASSISTANT
  继续读取排班组件

TOOL
  排班组件源码
```

继续执行工具调用后，再次达到压缩阈值：

```text
USER name=__compaction_summary__
  SESSION INTENT：判断小程序展示的号源是否实时

ASSISTANT
  继续读取排班组件

TOOL
  排班组件源码

ASSISTANT
  继续读取预约详情页

TOOL
  预约详情页源码
```

如果第二次压缩的 `prefix` 包含上一轮摘要，`filterSummaryMessages()` 会将摘要删除。

新摘要模型只能看到最近的工具调用，因此会话目标可能从：

```text
判断小程序展示的号源是否实时
```

漂移成：

```text
分析预约详情页的代码结构
```

如果待压缩的 `prefix` 中只有上一轮摘要，过滤后 `prefix` 为空，`summarizePrefix()` 会返回：

```java
if (prefix.isEmpty()) {
    return Mono.just("No previous conversation history.");
}
```

原始会话目标会因此完全丢失。

### 实际结果

连续压缩后可能出现：

1. 原始用户请求不再出现在模型上下文中；
2. `SESSION INTENT` 逐轮漂移到最近的工具调用；
3. 摘要变成 `No previous conversation history.`；
4. Agent 最终回答最近读取的文件内容，而不是用户最初的问题。

## Comment by oss-maintainer on 2026-07-23

**Issue Evaluation**

Category: `bug` | Status: **Triaged**

Thank you for reporting this issue. It has been classified as a potential bug.

**Next steps:**
- The issue will be verified against the current codebase
- If confirmed, an automated fix proposal may be generated
- Community feedback is welcome

---
*Automated triage by github-manager-bot*
