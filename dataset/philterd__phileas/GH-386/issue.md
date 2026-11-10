# Span offsets do not index into the input when splitting is enabled without an overlap

- Issue: https://github.com/philterd/phileas/issues/386
- Opened by jzonthemtn on 2026-09-12, closed on 2026-09-12
- Labels: bug
- Fix commit: cc1b5beb04e54581f4c6ba23a9ce786fde3dd440

## Report

When `config.splitting` is enabled and `overlap` is left at its default of `0`, the character
offsets returned for identified spans do not index into the input text. The span's `text` is
correct; `characterStart` and `characterEnd` are not.

`PlainTextFilterService` only takes the offset-carrying path when `overlap > 0`:

```java
final Optional<List<TextSplit>> overlapped = overlap > 0
        ? splitService.splitWithOverlap(input, overlap)
        : Optional.empty();
```

Otherwise the input is split into a `List<String>`, which carries no positions, and
`TextFilterResult.combine` shifts each piece's spans by the accumulated length of the *filtered*
text:

```java
documentOffset += pieceFilteredText.length();
```

The resulting offsets are positions in the redacted output, not the input. `AbstractSplitService.clean()`
also trims each piece and the pieces are rejoined with a single space, so the original newlines and
runs of spaces are lost.

## Example

A 2440 character document with 124 newlines, containing `JAMES SMITH` exactly once at offset 159.

```json
{"config": {"splitting": {"enabled": true, "threshold": 384, "method": "width"}}}
```

The span comes back as `text` = `JAMES SMITH`, `characterStart` = 157, `characterEnd` = 168, but
`input.substring(157, 168)` is `"\n JAMES SMI"`.

Over that document:

| Splitting | Spans | Offsets matching their own text |
|---|---|---|
| disabled | 18 | 18 |
| `width`, overlap `0` | 20 | 0 |
| `width`, overlap `32` | 22 | 22 |
| `newline`, overlap `0` | 20 | 0 |
| `newline`, overlap `32` | 23 | 23 |

Setting a non-zero `overlap` works around it. The default does not.

A document small enough to produce a single piece is unaffected, since `combine` never runs.

## Impact

Anything that uses span positions rather than the filtered text: reviewer tooling that highlights
spans, and the redaction ledger's `startPosition`. The filtered text itself is correct.

## Acceptance criteria

- [ ] With splitting enabled, `input.substring(characterStart, characterEnd)` equals the span's `text` for every applied and identified span.
- [ ] This holds for the default `overlap` of `0`, and for both the `width` and `newline` methods.
- [ ] Whitespace in the input is preserved in the filtered output when splitting is enabled.
- [ ] A test covers a document that splits into several pieces and contains newlines and runs of spaces, asserting offsets against the input for each method.
- [ ] A test covers a policy whose replacements change the text length, so drift introduced by redaction markers is caught.

## Comment by jzonthemtn on 2026-09-12

Worth noting for anyone picking this up: disabling splitting is not a safe workaround.

On the same document, turning splitting off left `JEFFREY S. WHITE` unredacted. Splitting finds it,
whatever the overlap:

| Splitting | Spans | Leaked |
|---|---|---|
| disabled | 18 | `JEFFREY S. WHITE` |
| `width`, overlap `0` | 20 | none |
| `width`, overlap `32` | 22 | none |
| `newline`, overlap `32` | 23 | none |

So the choice today is between a redaction miss and unusable offsets. Setting a non-zero `overlap`
avoids both, and produced no duplicate spans at the seams (22 spans at 22 distinct positions, 23 at
23).
