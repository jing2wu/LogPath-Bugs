# PatternInstanceofExpression is not handled: "instanceof" keyword is dropped and an ERROR is logged

- Issue: https://github.com/kusumotolab/FinerGit/issues/152
- Opened by YoshikiHigo on 2026-09-06, closed on 2026-09-07
- Labels: bug
- Fix commit: d55a3d53558dfee5a43b7c97f4911f514c47b8a9

## Report

## Summary
`PatternInstanceofExpression` (pattern matching for `instanceof`, Java 16+) is not handled. The visitor falls back to `super.visit(node)`, which visits the operand and the pattern but never emits the `instanceof` keyword. An ERROR is logged for every occurrence.

## Observed
Input:
```java
if (o instanceof String s && !s.isEmpty()) { }
```
Tokens in the generated `.mjava` file:
```
if ( o String s && ! s . isEmpty ( ) ) { }
```
Log:
```
[ERROR] JavaFileVisitor - JavaFileVisitor#visit(PatternInstanceofExpression) is not implemented yet.
```

## Cause
[JavaFileVisitor.java#L1729-L1732](https://github.com/kusumotolab/FinerGit/blob/79f9745ec8cad1521db10f2e9e7d7aa3fea6b734/src/main/java/finergit/ast/JavaFileVisitor.java#L1729-L1732).

## Suggested fix
```java
node.getLeftOperand().accept(this);
this.addToPeekModule(new INSTANCEOF());
node.getPattern().accept(this); // TypePattern / RecordPattern are already handled
return false;
```

Verified on 79f9745 (Windows 11, JDK 25).
