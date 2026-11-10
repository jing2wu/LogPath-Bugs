# Under mvnd, a build in a second clone reuses the first clone's repository and finds no changes

- Issue: https://github.com/gitflow-incremental-builder/gitflow-incremental-builder/issues/1256
- Opened by chrned on 2026-10-16, closed on 2026-10-16
- Labels: bug
- Fix commit: e142ca21e67e6225de13d9e858daf85ee8b34ebc

## Report

When one mvnd daemon runs a build in one git clone and then a build in another clone, GIB in the second build reads the first clone's repository. The second build sees none of its own changes. With `gib.buildAllIfNoChanges=false` it builds nothing and exits 0.

### Steps to reproduce

1. Create a multi-module project with two modules, `lib` and `other`. Load GIB 4.8.0 from `.mvn/extensions.xml`, and commit everything on `main`.
2. Clone the project twice, into `a` and `b`.
3. In `a`, create a branch that changes a source file in `lib`, and commit.
4. In `b`, create a branch that changes a source file in `other`, and commit.
5. With the same daemon, run in `a` and then in `b`:
   ```
   mvnd -B validate -Dgib.referenceBranch=refs/heads/main -Dgib.uncommitted=false -Dgib.untracked=false -Dgib.buildAllIfNoChanges=false
   ```

### Expected

The build in `b` reports `other` as changed and builds it.

### Actual

The build in `a` is correct. The build in `b` reports no changed modules, builds nothing, and exits 0. Running `mvnd --stop` before the build in `b` gives the expected result.

### Versions

- gitflow-incremental-builder 4.8.0
- mvnd 1.0.6 (darwin-aarch64), embedding Maven 3.9.16
- JDK 25.0.3 (Amazon Corretto)
- macOS 26.5.2, aarch64

### Cause

`GitProvider` is a `@Singleton` that caches its `Git` instance in a field ([GitProvider.java#L29](https://github.com/gitflow-incremental-builder/gitflow-incremental-builder/blob/v4.8.0/src/main/java/io/github/gitflowincrementalbuilder/jgit/GitProvider.java#L29)) and creates it only when the field is null ([#L37-L46](https://github.com/gitflow-incremental-builder/gitflow-incremental-builder/blob/v4.8.0/src/main/java/io/github/gitflowincrementalbuilder/jgit/GitProvider.java#L37-L46)). `MavenLifecycleParticipant` calls `close()` after each build ([MavenLifecycleParticipant.java#L66](https://github.com/gitflow-incremental-builder/gitflow-incremental-builder/blob/v4.8.0/src/main/java/io/github/gitflowincrementalbuilder/MavenLifecycleParticipant.java#L66)). `close()` closes the repository but keeps the field ([GitProvider.java#L60-L65](https://github.com/gitflow-incremental-builder/gitflow-incremental-builder/blob/v4.8.0/src/main/java/io/github/gitflowincrementalbuilder/jgit/GitProvider.java#L60-L65)). An mvnd daemon keeps the extension loaded between builds, so the next build gets the previous build's repository.

A build in the same clone is unaffected, because it reads the same repository.

## Comment by famod on 2026-10-16

@chrned I suppose you would appreciate a timely release with this fix? ;-)

## Comment by chrned on 2026-10-16

If possible, that would be great, yes :)

## Comment by famod on 2026-10-16

Here it is: https://github.com/gitflow-incremental-builder/gitflow-incremental-builder/releases/tag/v4.8.1

## Comment by chrned on 2026-10-17

Thanks :)
