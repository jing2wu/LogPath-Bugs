# An unknown split method silently falls back to newline splitting

- Issue: https://github.com/philterd/phileas/issues/392
- Opened by jzonthemtn on 2026-09-15, closed on 2026-10-21
- Labels: bug, testing, java, phisql
- Fix commit: 37d576b335a6650623f187edc1f2f51f102faefc

## Report

## Description

`SplitFactory.getSplitService` recognises `newline`, `width` and `characters`, and returns newline
splitting for anything else:

```java
LOGGER.warn("No matching split service found for {}. Defaulting to newline split service.", method);
return new NewLineSplitService();
```

A policy naming a method that does not exist is therefore split by a method it did not ask for. The
warning makes it discoverable in a log, which is more than the .NET port managed, but nothing reaches
the caller and the document is still filtered with the wrong splitter.

The specification's own example trips this. `spec/v1.2.0/examples/splitting-overlap.json` asks for
`"method": "character"`, singular, and the PhiSQL source it compiles from writes the same:

```sql
CONFIGURE SPLITTING (enabled = TRUE, threshold = 10000, method = 'character', overlap = 200);
```

So the name is not a typo in one JSON file; it is what the language surface uses in the example. The
effect measured in the .NET port, on a 17 KB document with no newlines: the policy produced one piece
rather than splitting, and the `overlap: 200` it configured did nothing at all.

Nothing catches it at any layer. The schema declares `method` as
`{"type": "string", "default": "newline"}` with no `enum`, so validation cannot reject an unknown
name either.

## Suggested resolution

`philterd/phileas-dotnet#105` implements this; the reasoning transfers directly.

- Accept `character` as an alias for `characters`, so the specification's example behaves as written.
- Raise on an unrecognised name instead of falling back, matching how `IdentifierValidators` in this
  same codebase already treats an unknown validator: a policy should never quietly get behaviour it
  did not ask for.
- Resolve the method whenever splitting is enabled, not only once a document exceeds the threshold.
  This was worth doing in the .NET port: without it the error lies dormant until a document large
  enough to split finally arrives, so a policy can be wrong for a long time before anything says so.

The missing `enum` belongs upstream in `philterd/phisql`, so the name can be rejected at validation
rather than at filter construction. Worth raising there separately, along with whether the spec
standardises on the singular or the plural.

## Acceptance criteria

- [ ] `character` resolves to the character-count splitter, so
      `spec/v1.2.0/examples/splitting-overlap.json` splits as it asks to.
- [ ] An unrecognised split method raises rather than falling back to newline splitting, and the
      message names the methods that are available.
- [ ] The method is resolved whenever splitting is enabled, so a name the policy got wrong surfaces
      on the first document rather than on the first large one.
- [ ] A test asserts each accepted name, including the alias and case-insensitivity, resolves to the
      expected service.
- [ ] A test asserts an unknown name raises, and that it is ignored when splitting is disabled.
- [ ] Documentation lists the accepted method names.
- [ ] `RELEASE_NOTES.md` records the change, since a policy that relied on the silent fallback will
      now fail when it filters.

## Related

- `philterd/phileas-dotnet#105` is the same defect in the .NET port, with a working implementation.
