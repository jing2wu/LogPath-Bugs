# ExpressionParser: hasArgs compares argsStart with 1 instead of -1

- Issue: https://github.com/microcks/microcks/issues/2350
- Opened by prasu-baran on 2026-10-03, closed on 2026-10-20
- Labels: kind/bug, component/mocks
- Fix commit: 2f112b5fef60f6ba04972b69706fb57e681b7f80

## Report

### Describe the bug

In ExpressionParser.doParseSimpleExpression:

    boolean hasArgs = (argsStart != 1 && argsEnd != -1 && argsStart < argsEnd);

argsStart comes from indexOf('('), so "not found" is -1, not 1. It looks like a typo. Two effects:

1. "(" at index 1 is never treated as a function call, so `{{ f() }}` with a function named "f" is parsed as a variable reference.
2. A ")" without "(" makes hasArgs true, so `{{ request.body/a) }}` throws:
   StringIndexOutOfBoundsException: Range [0, -1) out of bounds for length 15

### Expected behavior

1. `{{ f() }}` is parsed as a FunctionExpression.
2. `{{ request.body/a) }}` does not throw.

### Actual behavior

1. `{{ f() }}` becomes a VariableReferenceExpression.
2. `{{ request.body/a) }}` throws StringIndexOutOfBoundsException.

### How to Reproduce?

Reproducer:

    EvaluationContext context = new EvaluationContext();
    context.registerFunction("f", UUIDELFunction.class);
    ExpressionParser.parseExpressions("{{ f() }}", context, "{{", "}}");
    // VariableReferenceExpression instead of FunctionExpression

    context.setVariable("request", new EvaluableRequest("{\"a\": \"v\"}", null));
    ExpressionParser.parseExpressions("{{ request.body/a) }}", context, "{{", "}}");
    // throws StringIndexOutOfBoundsException

Resources to reproduce the behavior:
1. Add the snippets above as tests in commons/util-el ExpressionParserTest
2. Run `mvn -pl commons/util-el -am test`
3. Both fail on master

Changing `argsStart != 1` to `argsStart != -1` fixes both, and the existing util-el tests still pass. I can open a PR if you think it's worth fixing.

### Microcks version or git rev

git rev: master at 7d98fe46

### Install method (`docker-compose`, `helm chart`, `operator`, `docker-desktop extension`,...)

built from source (Maven)

### Additional information

Java 25.0.4.1, Maven 3.9.9, Windows 11

## Comment by VelpulaGangavardhan on 2026-10-03

Hi @prasu-baran, I'd like to work on this issue as my first contribution to Microcks.  
I’ll first reproduce the issue by adding the suggested regression tests, then make the minimal fix and run the relevant Maven tests.  
If that's okay, I'll proceed with a PR.

## Comment by lbroudoux on 2026-10-16

Hey @prasu-baran , that's a good catch! You're actually correct! 
Do you want to propose a PR on this one?

## Comment by prasu-baran on 2026-10-17

Yes I will be happy to raise a PR on this issue.
