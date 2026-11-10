# The question-pair arm claims interactionPairs for a question naming ONE substance with route/formulation rows, publishing a structurally-guaranteed zero over the drug-in-play arm's real pairs

- Issue: https://github.com/openmrs/openmrs-module-chartsearchai/issues/433
- Opened by dkayiwa on 2026-09-15, closed on 2026-09-24
- Labels: none
- Fix commit: e0492bb9ae267465be92978f1e4182d1a8f3b64c

## Report

Measured on the local 3.7.1 standalone at `main` @ `3a4cc1af` while answering an unrelated question about a patient's aspirin safety.

**This is not a defect against the published contract.** `PairChipExtent`'s class javadoc documents this shape and uses this very example — `Dexamethasone` beside `Dexamethasone (ophthalmic)` — and states the consequence plainly: "a response CAN carry an above-floor interaction chip beside `found: 0` … a client must not read it as a count of the chips beside it." `README.md` binds clients the same way ("not always the check that raised the chips beside it"), and `PairChipExtentContextTest.aPairwiseArmsStatementIsNotDisplacedByTheDrugInPlayScreen` pins it. So this is filed as a proposed **narrowing** of which arm may claim the field, not as a bug against the current one.

## What

`DrugSafetyValidator.addQuestionPairInteractions` gates on `questionDrugs.size() < 2 → return null` — "one drug is not a pair". Its population is pairs among the question's *own* resolved entries.

On the shipped DDInter knowledge base a question naming **one** substance can resolve to several entries, because the dataset files route and formulation rows separately. `Is dexamethasone safe for her?` resolves four: `Dexamethasone`, `Dexamethasone (nasal)`, `Dexamethasone (ophthalmic)`, `Dexamethasone (topical)`. All four are one substance, so no pair of them can interact — the arm enumerates a population that cannot contain a pair, finds none, cedes none, and takes the retained branch: `return PairChipExtent.of(0, 0)`.

Having **stated** an extent it makes `pairExtent != null`, so `validate`'s #356 fallback (`pairExtent == null && questionDrugScreened && hasActiveMedicationRecords(context)`) never fires, and the drug-in-play arm's real pairs never reach the field.

The dataset itself asserts that this population is empty. `/chartsearchai/drugreferencestatus` reports, from its own load findings, rule `self-paired-interaction-rows`, remedy `dropped`, 28 occurrences: "28 interaction row(s) pair a drug with itself or with another route/formulation row of the same substance, and a drug cannot interact with itself, so they were dropped."

## Measured

Live, patient `dc8560c9-6d2b-45bf-861c-8fcf562ec9b1` (Sarah Taylor, `10000TA`, nine active drug orders), `POST /chartsearchai/search`, `searchMode=full-chart`. Figures are the response's own `interactionPairs` key and the chips beside it:

| question | `interactionPairs` | chips raised | audit |
|---|---|---|---|
| `Is aspirin safe for her?` | `{found: 9, reported: 9}` | 4 rule chips, 9 `namedPartners` | 11249, 11250 |
| `Is warfarin safe for her?` | `{found: 9, reported: 9}` | 4 rule chips, 9 `namedPartners` | 11253 |
| `Is dexamethasone safe for her?` | **`{found: 0, reported: 0}`** | 1 rule chip (Moderate, 3 `namedPartners`) + 4 class-only + 2 contraindication | 11251 |
| `Is betamethasone safe for her?` | **`{found: 0, reported: 0}`** | 1 rule chip (Moderate, 3 `namedPartners`) + 5 class-only + 2 contraindication | 11252 |

The dexamethasone answer states and cites that interaction, so the zero sits beside prose asserting it:

> No — Dexamethasone should not be given: the patient has a recorded allergy to Dexamethasone [354], there is a possible cross-reactivity with the patient's allergy to Hydrocortisone (ophthalmic) [355], and it interacts with active orders Celecoxib, Diclofenac and Ibuprofen, which is a Moderate risk for serious gastrointestinal (GI) toxicity [356].

Betamethasone is the control for "the subject is itself one of her active orders": she is prescribed dexamethasone and not betamethasone, and both publish the zero, so that is not the cause.

The resolution counts come from driving the real `DrugReferenceService.findImpliedByQuery` — the method `DrugSafetyValidator` builds `questionDrugs` from, and so the gate's actual input — through a throwaway `BaseModuleContextSensitiveTest` against the shipped knowledge base (`getLoadStatus().getEntryCount()` = 2283), reporting `DrugReference.substanceGroupKey()` over what it returned:

| question | resolved entries | distinct substance keys |
|---|---|---|
| `Is aspirin safe for her?` | 1 — `Acetylsalicylic acid` | 1 |
| `Is warfarin safe for her?` | 1 — `Warfarin` | 1 |
| `Is dexamethasone safe for her?` | 4 — systemic, nasal, ophthalmic, topical | **1** |
| `Is betamethasone safe for her?` | 2 — systemic, topical | **1** |
| `Do clarithromycin and warfarin interact?` | 2 | 2 |

A prior attempt to measure this by scanning the knowledge-base JSON's `name` field reported one row per drug and was wrong — the production resolver pulls in the whole route/formulation family. Recording that because it is the failure the root `CLAUDE.md` rule against re-expressing a production predicate predicts: the scan agreed with production on aspirin and warfarin and disagreed in exactly the tail under investigation.

## Why it matters

The retained branch's justification is that its zero is a measurement: "this pair list is complete, and a caller that heard nothing could not tell that from an arm that never ran". That reasoning holds for a question whose resolved entries are genuinely different substances that the data relates no pair between. It does not hold when every resolved entry is **one** substance: there the zero is structurally unreachable-from-nonzero, carries no information about the chart or the dataset, and displaces an arm that had pairs to report. A client rendering the field as `README` instructs shows "0 of 0 interaction pairs" above a Moderate finding the same response states and cites — the same reader-facing outcome #336 and #370 were filed for, arrived at down a different branch.

## The fix

Extend the arm's own entry gate from "one drug is not a pair" to "several rows of one drug are not a pair either": where `questionDrugs` has two or more entries that all share one `DrugReference.substanceGroupKey()`, return `null` rather than `PairChipExtent.of(0, 0)`. The arm then has no bounded list it could describe — the same reasoning already applied to the cede branch in #336 and to the screening arm in #370 — and `validate`'s #356 fallback hands the field to the drug-in-play arm, which reported the pairs.

Scoped so it cannot swallow a real pairwise statement: the narrowing requires *all* entries to share one key, so `Do clarithromycin and warfarin interact?` (two entries, two keys, measured above) keeps the field and `aPairwiseArmsStatementIsNotDisplacedByTheDrugInPlayScreen` stays green. It is also distinct from the retained branch it leaves in place — "enumerated pairs and related none of them" is still a measurement and still states its zero.

Worth pinning with a case in `PairChipExtentContextTest` over a multi-row single substance. The fixture is already there and already exercised: `DrugReferenceTestSupport.DDI_ROUTE_VARIANTS` (`chartsearchai-test/ddi-route-variants.json`) carries all four dexamethasone rows, and `aClinicalPairOneEntryPairCollectedAndAnotherCededStatesWhatTheChartArmReported` already drives a dexamethasone question over it — but with voxelotor named too, so that question resolves two substance keys and is not this shape. A single-substance question over the same fixture is the missing case.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
