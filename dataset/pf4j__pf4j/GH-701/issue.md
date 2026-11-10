# The plugins attribute of an inherited Extension annotation does not reach the subclass

- Issue: https://github.com/pf4j/pf4j/issues/701
- Opened by decebals on 2026-09-20, closed on 2026-10-16
- Labels: bug
- Fix commit: 6e1bdbf715e1f99c00361a2360e53b4bf7b6fc4f

## Report

`AbstractExtensionFinder.find` checks the plugins an extension requires before loading its class, and reads them with asm so that a class whose optional dependencies are missing is never loaded:

```java
ExtensionInfo extensionInfo = getExtensionInfo(className, classLoader);
...
for (String requiredPluginId : extensionInfo.getPlugins()) {
```

`ExtensionVisitor` reads the annotation of the class it is given and does not walk the hierarchy. `@Extension` is `@Inherited`, so a class that extends an annotated one is registered as an extension without carrying the annotation itself, and its bytecode holds nothing to read. A base annotated with `@Extension(ordinal = 7, plugins = "foo")` and a child that only extends it:

```
BASE  plugins=[foo] ordinal=7
CHILD plugins=[]    ordinal=0
CHILD reflection ordinal=7
```

The child is not filtered, so it is loaded although `foo` is missing, which is the `NoClassDefFoundError` the check exists to prevent. The third line is the asymmetry. `createExtensionWrapper` reads the ordinal with core reflection, which honours `@Inherited`, so that attribute does reach the child while `plugins` does not.

Nothing recent caused this, it has been so since the check arrived with the optional dependencies. What changed is that #697 states the inheritance in the javadoc of `Extension`, so the pattern is supported rather than accidental and more people will meet the hole. The check is not a corner nobody reaches either, it enables itself as soon as one started plugin declares an optional dependency.

`ExtensionInfo.load` could follow the hierarchy in bytecode. `ExtensionVisitor` records whether it found the annotation, and when it did not, the reader moves to the `superName` of the class and reads that one with the same class loader. It is one more resource lookup for a class without its own annotation, and the result is already cached per class name in `AbstractExtensionFinder.extensionInfos`.

`points()` is not inherited either, for a different reason, `Element.getAnnotationMirrors` returns only the annotations directly present. That one should stay as it is. It is an explicit override written on one class, and a child implementing an extension point of its own would be silenced by a `points` written on its base. It belongs in the javadoc, not in the code.
