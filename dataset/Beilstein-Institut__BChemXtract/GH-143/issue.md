# fix: java.lang.NullPointerException: Cannot invoke "org.openscience.cdk.interfaces.IAtom.setIsAromatic(boolean)" because the return value of "org.openscience.cdk.interfaces.IBond.getEnd()" is null

- Issue: https://github.com/Beilstein-Institut/BChemXtract/issues/143
- Opened by mnietfeld on 2026-09-10, closed on 2026-09-14
- Labels: bug
- Fix commit: 865068cead7fdd8800d4fad6e12434a6ed05dc02

## Report

### Summary

Exception in thread "main" java.lang.NullPointerException: Cannot invoke "org.openscience.cdk.interfaces.IAtom.setIsAromatic(boolean)" because the return value of "org.openscience.cdk.interfaces.IBond.getEnd()" is null
	at org.beilstein.chemxtract.converter.BondConverter.convert(BondConverter.java:116)
	at org.beilstein.chemxtract.converter.FragmentConverter.convert(FragmentConverter.java:161)
	at org.beilstein.chemxtract.converter.FragmentConverter.convert(FragmentConverter.java:119)
	at org.beilstein.chemxtract.xtractor.SubstanceXtractor.xtractSubstances(SubstanceXtractor.java:299)
	at org.beilstein.chemxtract.xtractor.SubstanceXtractor.xtract(SubstanceXtractor.java:125)
	at org.beilstein.chemxtract.xtractor.SubstanceXtractor.xtractUnique(SubstanceXtractor.java:211)
	at org.beilstein.boa.tools.cheminf.ExtractSubstances.processChemdraw(ExtractSubstances.java:160)
	at org.beilstein.boa.tools.cheminf.ExtractSubstances.main(ExtractSubstances.java:83)


### Steps to reproduce

java -cp boa-tools/target/boa-tools-5.15-RC3-jar-with-dependencies.jar org.beilstein.boa.tools.cheminf.ExtractSubstances /home/markus/data/cdx/Volume_8/8-147-Hanson/m2490959-i1.cdx

### Expected behavior

no exception ;)

### Actual behavior

NPE

### BChemXtract version

1.4.1

### Java version

Java 17

### Operating system

Ubuntu 24

### Additional context

_No response_

## Comment by fbaensch-beilstein on 2026-09-14

Root-caused and fixed.

**Cause.** This drawing contains a grid of unlabelled stub bonds: two long horizontal bonds at y=73 and y=85 spanning x=164..210, and three vertical bonds at x=175/187/198 spanning y=55..100. Each vertical genuinely crosses *both* horizontals, and the two horizontals belong to *different* fragments.

`AttachmentHandler.normalizeVariableAttachmentBonds` collects the position-variation candidates from the endpoints of every crossed bond (four atoms, two per fragment), but folds the substituent into a single scaffold — the first fragment containing any candidate. The other fragment is never merged, so `expandVariableAttachments` enumerates variants that bond the substituent to an atom the variant does not contain. `BondConverter` then looks that atom up in the atom map, gets `null`, and dereferences it — the reported NPE.

**Fix.**
1. Candidates are limited to the scaffold the substituent actually moves into; a crossing whose candidates all live elsewhere contributes none.
2. `BondConverter.convert` now reports a bond whose endpoint has no converted atom instead of dereferencing it, so any future dangling bond is a logged skip rather than a crash.

The file now extracts cleanly; the drawn structures are unchanged (`UXNBGVUKBFZULV`, `ANVCWQKIKMBTSL`, `MTGOGSQUOYTZNN`, `JTEYFTMDXBRRJY`, `DSOBKSCOEWTDIZ`, …).

PRs: #152 (`main`) and #153 (backport onto `release/1.4.x`, where 1.4.1 was released from).

One thing not fixed here: the grid of unlabelled stub bonds is a drawing artifact rather than chemistry, and still yields junk substances of its own (`OTMSDBZUPAUEDD` ethane plus three radicals). Same class as the known overlapping-drawings case in m28096433-4 — reported, not fixed in passing.

## Comment by fbaensch-beilstein on 2026-09-14

Follow-up on the drawing-artifact note above — not part of this issue's fix, but it came out of the same analysis.

Investigating the related overlapping-drawings case (`volumeTest/vol20Test/m28096433-4.cdx`) showed the same heuristic failing in the opposite direction. That file contains two pairs of large components, each pair occupying the same page area, with nearly every bond of one crossing a bond of the other (49 of 52, and 34 of 35). Every crossing passes the geometry test and every terminal atom is a degree-one free end, so `normalizeVariableAttachmentBonds` merged each pair and read one position-variation junction per terminal atom — 10 junctions / 9,843,750 combinations, and 6 junctions / 2,160. Both exceed `MAX_VARIANTS`, so the merged fragments were dropped silently and 179 atoms of drawing never reached conversion.

A fragment whose bonds mostly cross another fragment is a second drawing, not a substituent attaching to one, and is now left where it was drawn. Threshold calibrated against every merge the heuristic performs across the fixture corpus: 145 of 159 real merges carry exactly one crossing bond, none more than three, against 34 and 49 for these two. The corpus diff removes exactly those two merges and changes nothing else.

PRs: #154 (`main`) and #155 (backport onto `release/1.4.x`).

These do not affect the NPE this issue reports — that fix is #152 / #153.

## Comment by fbaensch-beilstein on 2026-09-14

Status update on the follow-up PRs.

#152 and #153 (the NPE fix this issue reports) are merged.

#154 and #155 (the overlapping-drawings guard) needed a rebase afterwards — both touch `normalizeVariableAttachmentBonds`, so merging the first pair put them in conflict and GitHub scheduled no checks while they were conflicting. The conflict was mechanical: `atomsIn(...)` and `crossingBondCount(...)` land next to each other, and the two new unit tests are adjacent; both helpers and both tests are kept.

Rebased and green:

- #154 (`main`) — 12/12 checks pass; awaiting review approval.
- #155 (`release/1.4.x`) — 13/13 checks pass, mergeable and clean.

`mvn -B verify` on each branch: 390 tests, 0 failures, volume tests included, Spotless clean.
