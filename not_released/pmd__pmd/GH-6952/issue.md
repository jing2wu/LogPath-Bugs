# [core] Ruleset references that are relative to another ruleset cannot be resolved

- Issue: https://github.com/pmd/pmd/issues/6952
- Opened by lukasgraef on 2026-08-06, closed on 2026-08-11
- Labels: a:bug
- Fix commit: 3db1fe0ee1f99c7cca3978b14f66efc417a16d11

## Report

<!-- Please, prefix the report title with the language it applies to within brackets, such as [java] or [apex].
If not specific to a language, you can use [core]. -->

**Affects PMD Version:** 

7.26

**Description:**

PMD's RuleSetLoader can't resolve rule file references, if both these conditions are met:

- the referenced file is not on the classpath
- the referenced file's relative path cannot be resolved from the working dir

Consequence: Rule file references that are relative to the rule file from which they're referenced from cannot be resolved.
This mostly happens due to Gradle's usage of PMD (absolute path to main ruleset, running from another workdir), I still think it would be sensible to also resolve sibling rulesets.

This causes the bug described in https://github.com/gradle/gradle/issues/24885.

**Exception Stacktrace:**

From the testcase below:

```
net.sourceforge.pmd.lang.rule.RuleSetLoadException: Cannot load ruleset base.xml: Cannot resolve rule/ruleset reference 'base.xml'.  Make sure the resource is a valid file or URL and is on the CLASSPATH. Use --debug (or a fine log level) to see the current classpath.

	at net.sourceforge.pmd.lang.rule.RuleSetFactory.readDocument(RuleSetFactory.java:203)
	at net.sourceforge.pmd.lang.rule.RuleSetFactory.createRuleSet(RuleSetFactory.java:119)
	at net.sourceforge.pmd.lang.rule.RuleSetFactory.createRuleSet(RuleSetFactory.java:114)
	at net.sourceforge.pmd.lang.rule.RuleSetFactory.parseRuleSetReferenceNode(RuleSetFactory.java:389)
	at net.sourceforge.pmd.lang.rule.RuleSetFactory.parseRuleNode(RuleSetFactory.java:335)
	at net.sourceforge.pmd.lang.rule.RuleSetFactory.parseRulesetNode(RuleSetFactory.java:242)
	at net.sourceforge.pmd.lang.rule.RuleSetFactory.readDocument(RuleSetFactory.java:186)
	at net.sourceforge.pmd.lang.rule.RuleSetFactory.createRuleSet(RuleSetFactory.java:119)
	at net.sourceforge.pmd.lang.rule.RuleSetFactory.createRuleSet(RuleSetFactory.java:114)
	at net.sourceforge.pmd.lang.rule.RuleSetLoader.loadFromResource(RuleSetLoader.java:248)
	at net.sourceforge.pmd.lang.rule.RuleSetLoader.loadFromResource(RuleSetLoader.java:139)
	at net.sourceforge.pmd.lang.rule.RuleSetFactoryTest.testRefToSiblingRuleset(RuleSetFactoryTest.java:62)
Caused by: java.io.FileNotFoundException: Cannot resolve rule/ruleset reference 'base.xml'.  Make sure the resource is a valid file or URL and is on the CLASSPATH. Use --debug (or a fine log level) to see the current classpath.
	at net.sourceforge.pmd.lang.rule.internal.RuleSetReferenceId.notFoundException(RuleSetReferenceId.java:309)
	at net.sourceforge.pmd.lang.rule.internal.RuleSetReferenceId.getInputStream(RuleSetReferenceId.java:304)
	at net.sourceforge.pmd.lang.rule.RuleSetFactory.readDocument(RuleSetFactory.java:165)
```

**Code Sample demonstrating the issue:**

Add the following to net.sourceforge.pmd.lang.rule.RuleSetFactoryTest:

```java
@Test
void testRefToSiblingRuleset(@TempDir Path tempDir) throws IOException {
    write(tempDir.resolve("leaf.xml"), rulesetXml(dummyRule()));
    write(tempDir.resolve("base.xml"), rulesetXml(rulesetRef("leaf.xml")));
    write(tempDir.resolve("main.xml"), rulesetXml(rulesetRef("base.xml")));

    RuleSet rs = new RuleSetLoader().loadFromResource(tempDir.resolve("main.xml").toString());
    assertEquals(1, rs.size());
    assertNotNull(rs.getRuleByName("MockRuleName"));
}

private static void write(Path file, String content) throws IOException {
    Files.write(file, content.getBytes(StandardCharsets.UTF_8));
}
```

**Steps to reproduce:**

Run the (failing) test pasted above.

Alternatively, try the setup linked in the Gradle issue: https://github.com/lukelukes/gradle-pmd-bug

**Running PMD through:** *Gradle*

<!-- If relevant, also include your JDK and OS information, e.g. for ClassNotFoundException, LinkageError, reflection failures, etc. -->
