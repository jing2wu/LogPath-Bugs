# [Bug]:NacosSkillRepository 框架层 bug，3 层叠加，ai分析对吗？

- Issue: https://github.com/agentscope-ai/agentscope-java/issues/1339
- Opened by rogerlmj123 on 2026-05-05, closed on 2026-09-01
- Labels: bug, area/ext/integration
- Fix commit: 9afbe5f9dc345f9320fe32dc4d7062e2058a0794

## Report

问题根因（框架层 bug，3 层叠加）：问题根因（框架层 bug，3 层叠加）：
1、NacosSkillRepository 构造函数 将空 namespace 映射为 "public"，然后 source = "nacos:" + namespaceId → "nacos:public"
2、AgentSkill.getSkillId() = name + "_" + source → order-query-skill_nacos:public
3、SkillBox.uploadSkillFiles() 用 Path.resolve(skillId) → Windows 上 : 是非法路径字符 → InvalidPathException


这与技能名称无关，是框架 NacosSkillRepository 内部对所有 namespace 都会拼接 nacos:{namespaceId} 的固有问题。即使 namespace 配为空字符串，框架也会转为 "public"。

skill从nacos加载过程，ide用的windows。是上面分析问题吗？
————————————————————————————-错误信息如下:
java.nio.file.InvalidPathException: Illegal char <:> at index 23: order-query-skill_nacos:public

	at java.base/sun.nio.fs.WindowsPathParser.normalize(WindowsPathParser.java:204) ~[na:na]

	at java.base/sun.nio.fs.WindowsPathParser.parse(WindowsPathParser.java:175) ~[na:na]

	at java.base/sun.nio.fs.WindowsPathParser.parse(WindowsPathParser.java:77) ~[na:na]

	at java.base/sun.nio.fs.WindowsPath.parse(WindowsPath.java:92) ~[na:na]

	at java.base/sun.nio.fs.WindowsFileSystem.getPath(WindowsFileSystem.java:231) ~[na:na]

	at java.base/java.nio.file.Path.resolve(Path.java:516) ~[na:na]

	at io.agentscope.core.skill.SkillBox.uploadSkillFiles(SkillBox.java:737) ~[agentscope-core-1.0.11.jar:na]

	at io.agentscope.core.ReActAgent$Builder.configureSkillBox(ReActAgent.java:1737) ~[agentscope-core-1.0.11.jar:na]

	at io.agentscope.core.ReActAgent$Builder.build(ReActAgent.java:1567) ~[agentscope-core-1.0.11.jar:na]

	at com.agent.scope.mall.agent.BaseAgent.buildAgent(BaseAgent.java:315) ~[classes/:na]

## Comment by fang-tech on 2026-05-08

You can solve this problem by extending the NacosSkillRepository class and overriding the getSource() method. (你可以通过extend NacosSkillRepository override getSource()方法来暂时解决这个问题, 这个问题我会在这个版本修复)
