# Extension#ordinal is never read by the ASM-based ExtensionInfo

- Issue: https://github.com/pf4j/pf4j/issues/670
- Opened by decebals on 2026-08-26, closed on 2026-08-26
- Labels: bug
- Fix commit: 47b006a0be8c3456073587b5d7306510424c3407

## Report

### Problem

`ExtensionVisitor` only overrides `visitArray(String)` and handles `"ordinal"` inside it. But `ordinal` is declared `int ordinal() default 0`, a scalar. ASM reports scalar annotation members through `AnnotationVisitor.visit(name, value)`, which is not overridden. The `"ordinal"` branch inside `visitArray` is therefore unreachable from real bytecode.

Result: `ExtensionInfo.getOrdinal()` always returns 0.

Verified with a class annotated `@Extension(ordinal = 5, plugins = {"alpha", "beta"}, points = {Greeter.class})`, read through `ExtensionInfo.load()`:

```
ordinal = 0        <-- expected 5
plugins = [alpha, beta]
points  = [Greeter]
```

### Impact

Low. `ExtensionInfo.getOrdinal()` has no production callers. Extension sorting uses `ExtensionWrapper.getOrdinal()`, which reads the annotation reflectively and is correct. So this is a public API method on an exported class returning wrong data, rather than a behavioural regression that users can observe.

### Why the tests don't catch it

`ExtensionVisitorTest.visitArrayShouldHandleOrdinalAttribute` calls `annotationVisitor.visitArray("ordinal")` directly, which is a call ASM never makes for a scalar member, so it asserts against a code path that is dead in practice. `ExtensionInfoTest` only asserts the default of 0, on a class that carries no `@Extension` annotation at all.

There is no end-to-end test that reads a genuinely annotated class and asserts the parsed values.

### Suggested fix

Handle `ordinal` in an overridden `visit(String, Object)` instead of `visitArray`, and add an end-to-end test over a real annotated fixture class covering all three members.

Related: #669 (same code, ASM version ceiling).
