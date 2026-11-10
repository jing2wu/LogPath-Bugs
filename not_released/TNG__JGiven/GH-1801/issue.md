# IndexOutOfBoundsException when injecting a null value in the second test case using DataProvider on a ParameterizedTest

- Issue: https://github.com/TNG/JGiven/issues/1801
- Opened by sebphil on 2024-12-09, closed on 2024-12-13
- Labels: bug, waiting for additional input
- Fix commit: f38d8b52e321f09d90a4b3d58d28aef2783db870

## Report

A parameterized test with a null value in its second test case, such as this one:
```java
@ParameterizedTest
@DataProvider({
    "data1, data2",
    "null, data2"
})
public void test(String param1, String param2) {
    ...
}
```
which worked just fine with jgiven 1.3.1, now fails using jgiven 2.0.0 with the following exception:
```
java.lang.IndexOutOfBoundsException: Index 0 out of bounds for length 0
	at java.base/jdk.internal.util.Preconditions.outOfBounds(Preconditions.java:100)
	at java.base/jdk.internal.util.Preconditions.outOfBoundsCheckIndex(Preconditions.java:106)
	at java.base/jdk.internal.util.Preconditions.checkIndex(Preconditions.java:302)
	at java.base/java.util.Objects.checkIndex(Objects.java:385)
	at java.base/java.util.ArrayList.get(ArrayList.java:427)
	at java.base/java.util.Collections$UnmodifiableList.get(Collections.java:1501)
	at com.tngtech.jgiven.report.analysis.CaseArgumentAnalyser.findArgumentNames(CaseArgumentAnalyser.java:114)
	at com.tngtech.jgiven.report.analysis.CaseArgumentAnalyser.analyze(CaseArgumentAnalyser.java:69)
	at com.tngtech.jgiven.report.analysis.CaseArgumentAnalyser.analyze(CaseArgumentAnalyser.java:32)
	at com.tngtech.jgiven.report.impl.CommonReportHelper.finishReport(CommonReportHelper.java:26)
	at com.tngtech.jgiven.junit5.JGivenExtension.afterAll(JGivenExtension.java:75)
	at java.base/java.util.ArrayList.forEach(ArrayList.java:1596)
```
Note that it fails only when the test case containing the null value comes after a test case containing only non-null values. Also note that the position of the null value does not change anything, `"data1, null"` also fails when put after `"data1, data2"` but not when it comes first.

## Comment by l-1squared on 2024-12-12

I'm a bit confused by your test setup. You seem to be using JUnit5 with a JUnit5 parameterized annotation, but you seem to giving a `com.tngtech.dataprovider.Dataprovider` annotation instead of the JUnit5 `@ValueSource` or `@MethodSource`

I honestly am surprised that this worked in the first place.

## Comment by sebphil on 2024-12-13

This must be a relic from when I used JUnit4, see https://jgiven.org/userguide/#_parameterized_scenarios

I switched to the JUnit5 `@CsvSource` instead of `@DataProvider`, but I'm still having the same exact exception.

Note that each individual test succeeds, then the exception occurs after all the tests from the test class have finished running and JUnit5 then considers the entire test class failed.

## Comment by l-1squared on 2024-12-13

Found the issue. I had to rewrite how we grab Args from JUnit 5 and made the error of using `List.of` instead of `Arrays.asList`...
The former unfortunately does not support `null` inputs.

I'm preparing a fix
