# [doc] When a rule's description has a link to another rule in the exact wrong position, the doc generation crashes

- Issue: https://github.com/pmd/pmd/issues/6961
- Opened by UncleOwen on 2026-08-09, closed on 2026-09-05
- Labels: a:bug, in:documentation, in:pmd-internals
- Fix commit: a24c49986ee429e4907a182383f5902a5f816694

## Report

**Affects PMD Version:** 7.27.0-SNAPSHOT

**Description:**

See https://github.com/pmd/pmd/actions/runs/31322495756/job/93268032541 and https://github.com/Will-6543/pmd/blob/165fbb9e400dde579ed2756393ff518c6788de61/pmd-java/src/main/resources/category/java/codestyle.xml#L982.

The description of the new rule starts with
```
**Note**: This rule goes against virtually all Java style guidelines. See {% rule VariableDeclarationUsageDistance %} for an alternative.
```

When generating the rules index, RuleDocGenerator.java turns this into
```markdown
*   [LocalVariableDeclarationShouldBeAtStartOfBlock](pmd_rules_java_codestyle.html#localvariabledeclarationshouldbeatstartofblock): Note: This rule goes against virtually all Java style guidelines. See {% rule VariableDeclaration...
```
(look at the end of the line)

This causes RuleTagChecker to choke with
```
java.lang.StringIndexOutOfBoundsException: Index 232 out of bounds for length 232
    at jdk.internal.util.Preconditions$1.apply (Preconditions.java:55)
    at jdk.internal.util.Preconditions$1.apply (Preconditions.java:52)
    at jdk.internal.util.Preconditions$4.apply (Preconditions.java:213)
    at jdk.internal.util.Preconditions$4.apply (Preconditions.java:210)
    at jdk.internal.util.Preconditions.outOfBounds (Preconditions.java:98)
    at jdk.internal.util.Preconditions.outOfBoundsCheckIndex (Preconditions.java:106)
    at jdk.internal.util.Preconditions.checkIndex (Preconditions.java:302)
    at java.lang.String.checkIndex (String.java:4822)
    at java.lang.StringLatin1.charAt (StringLatin1.java:46)
    at java.lang.String.charAt (String.java:1544)
    at net.sourceforge.pmd.doc.internal.RuleTagChecker.checkFile (RuleTagChecker.java:76)
    at net.sourceforge.pmd.doc.internal.RuleTagChecker.access$000 (RuleTagChecker.java:29)
    at net.sourceforge.pmd.doc.internal.RuleTagChecker$1.visitFile (RuleTagChecker.java:56)
    at net.sourceforge.pmd.doc.internal.RuleTagChecker$1.visitFile (RuleTagChecker.java:53)
    at java.nio.file.Files.walkFileTree (Files.java:2799)
    at java.nio.file.Files.walkFileTree (Files.java:2870)
    at net.sourceforge.pmd.doc.internal.RuleTagChecker.check (RuleTagChecker.java:53)
    at net.sourceforge.pmd.doc.internal.RuleTagChecker.main (RuleTagChecker.java:142)
    at jdk.internal.reflect.DirectMethodHandleAccessor.invoke (DirectMethodHandleAccessor.java:103)
    at java.lang.reflect.Method.invoke (Method.java:580)
    at org.codehaus.mojo.exec.AbstractExecJavaBase.executeMainMethod (AbstractExecJavaBase.java:402)
    at org.codehaus.mojo.exec.ExecJavaMojo.executeMainMethod (ExecJavaMojo.java:142)
    at org.codehaus.mojo.exec.AbstractExecJavaBase.doExecClassLoader (AbstractExecJavaBase.java:377)
    at org.codehaus.mojo.exec.AbstractExecJavaBase.lambda$execute$0 (AbstractExecJavaBase.java:287)
    at java.lang.Thread.run (Thread.java:1583)
```

IMHO, there are three things that should be fixed:
* RuleDocGenerator should strip all markdown from the rule description when creating the summary page (that's already partially there at lines 336ff, but needs to strip links as well)
* RuleTagChecker needs to detect missing closing tags (`%}`) and not choke on them
* Exceptions in RuleTagChecker should include filename and line (the StringIndexOutOfBoundsException contains the column, which on it's own is useless)
