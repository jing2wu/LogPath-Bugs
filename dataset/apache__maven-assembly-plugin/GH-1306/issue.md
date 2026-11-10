# In multi-module project: "Artifact is present in the local repository, but cached from a remote repository ID that is unavailable in current build context"

- Issue: https://github.com/apache/maven-assembly-plugin/issues/1306
- Opened by unv-unv on 2026-04-30, closed on 2026-08-25
- Labels: bug
- Fix commit: 6f86f52782c98aefa9abc128362951d97798b503

## Report

### Affected version

3.8.0

### Bug description

When building a multi-module project using maven-assembly-plugin, the build repeatedly prints warnings for dependencies from a repository defined in the parent POM (which contains artifacts not present in the Maven Central). The warning message is:

```
[INFO] Artifact <groupId>:<artifactId>:pom:<version> is present in the local repository, but cached from a remote repository ID that is unavailable in current build context, verifying that is downloadable from [central (https://repo.maven.apache.org/maven2, default, releases)]
```

This occurs even though all artifacts are successfully resolved during the main build phase and are present in the local cache.

It appears the plugin ignores the project's repositories configuration. This leads to dozens of warnings, slowing down the build.

The root cause seems similar to the previously resolved issue MASSEMBLY-855. The problem is that the plugin's internal DefaultDependencyResolver does not properly inherit the session's repository list when executed from a child module in a reactor build.

I attached test multi-module project which represents this issue.

[test.zip](https://github.com/user-attachments/files/27264710/test.zip)

## Comment by OpenPj on 2026-05-12

I have the same issue in the Apache ManifoldCF project, creating a new Maven Assembly file it seems that the unique Maven dependency related to an external repository is returning the same message in the log

## Comment by cstamas on 2026-05-12

The message "present in the local repository, but cached from a remote repository ID that is unavailable in current build context" means exactly that: file is there, but Maven cannot correlate whether it should be available in current build context or not.

This line looks sus: https://github.com/apache/maven-assembly-plugin/blob/a506506dfc8db403443e749451cdf537b332c8ea/src/main/java/org/apache/maven/plugins/assembly/artifact/DefaultDependencyResolver.java#L234

From which remote repository should the artifact in question be resolved, and, how is it defined for you?

## Comment by OpenPj on 2026-05-12

In my case I defined a remote repository in one of the Maven sub modules

## Comment by cstamas on 2026-05-12

And is it the same module where m-assembly-p runs as well?

## Comment by OpenPj on 2026-05-12

Nope, the distribution sub-module includes the assembly file and the message is related to a dependency defined in another sub-module.

## Comment by cstamas on 2026-05-12

Can you try (for testing sake) one of these -- assuming you have a "reproducer" in form of your project:
* "lift" repo definition to some common parent POM (where it is now and where m-assembly-p runs)
* "copy" the repo definition to module where m-assembly-p runs too?

Just to see is my hint right or wrong?

## Comment by alexisNizardSymphony on 2026-07-12

Hello, any updates for this issue ?
