# [core] PMDConfiguration - "Can't mix setClasspath with getAuxClasspath!"

- Issue: https://github.com/pmd/pmd/issues/7013
- Opened by AB-xdev on 2026-08-31, closed on 2026-09-03
- Labels: a:bug
- Fix commit: 65dca5ed07186213bda4df65a6fae0ce31feaa46

## Report

**Affects PMD Version:** 

7.27.0

**Description:**

Call `PMDConfiguration#setClassLoader` and do an analysis `PmdAnalysis.create(pmdConfig)` → Crashes

**Exception Stacktrace:**

```
2026-08-31 09:20:49,922 [  94383] SEVERE - #software.xdev.pmd.annotator.PMDExternalLanguageAnnotator - Failed to annotate
java.lang.IllegalStateException: Can't mix setClasspath with getAuxClasspath!
	at net.sourceforge.pmd.PMDConfiguration.getAuxClasspath(PMDConfiguration.java:353)
	at net.sourceforge.pmd.PmdAnalysis.create(PmdAnalysis.java:221)
	at software.xdev.pmd.analysis.PMDAnalyzer.analyzeInternal(PMDAnalyzer.java:203)
        ...
```

**Code Sample demonstrating the issue:**

See above

**Steps to reproduce:**

See above

**Running PMD through:** *Other*

## Comment by UncleOwen on 2026-08-31

Can't reproduce. The following test is green.

```java
    @Test
    void testCreateConfigWithCustomClasspath() {
        PMDConfiguration config = new PMDConfiguration();
        config.setClassLoader(this.getClass().getClassLoader());

        assertDoesNotThrow(() -> PmdAnalysis.create(config));
    }
```

## Comment by AB-xdev on 2026-08-31

@UncleOwen Is this test executed using a `JvmLanguagePropertyBundle`? You probably need to configure a language like Java because otherwise the condition might not be triggered - at least as far as I have seen in the code...

## Comment by UncleOwen on 2026-08-31

Ah, I took your problem description a bit too literal. Now I can reproduce.
```java
    @Test
    void testCreateConfigWithCustomClasspath() {
        LanguageRegistry registry = new LanguageRegistry(setOf(new FakeJvmLanguageModule()));
        PMDConfiguration config = new PMDConfiguration(registry);
        config.setClassLoader(this.getClass().getClassLoader());

        assertDoesNotThrow(() -> PmdAnalysis.create(config));
    }

    private static class FakeJvmLanguageModule extends DummyLanguageModule {
        @Override
        public LanguagePropertyBundle newPropertyBundle() {
            return new JvmLanguagePropertyBundle(this);
        }
    }
```
