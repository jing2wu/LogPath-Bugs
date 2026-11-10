# Follow-ups from #487: the ended-order phrase ahead of its drug, and the unpinned multi-name combination walk

- Issue: https://github.com/openmrs/openmrs-module-chartsearchai/issues/489
- Opened by dkayiwa on 2026-09-23, closed on 2026-09-23
- Labels: none
- Fix commit: fd24ea36368758245d3b87668ce276528e1c5b88

## Report

Two follow-ups from the final review round of #487 (issue 482 item 1). Neither blocked merging.

1. **A phrase ahead of the drug it is about still reads as this drug's end.** When no drug is named before an occurrence of "no longer in force", `DrugSafetyValidator.isAboutTheEndedOrderDrug` falls back to the old sentence rule. So *"The order no longer in force is her isoniazid; rifampicin interacts with nevirapine."* counts as stating rifampicin's end, and the module appends nothing about rifampicin. That errs toward silence, and ADR Decision 110's first residue records it.
   - **Proposed fix:** in that fallback, take the drug named nearest *after* the phrase, with a tie going to this drug.
   - **Checked in review:** the reviewer mutated the code this way. The phrase-first probe then read as not stated, and `LlmInferenceServiceEndedOrderStatementContextTest` and `EndedOrderFindingReferentTest` stayed green.
   - **If adopted:** remove that entry from the residue, and change the README `aboutAnEndedOrder` row to match.
2. **The combination-name walk past the first joined name is unpinned.** In `isAboutTheEndedOrderDrug`, the step that keeps walking through a combination name (`other = before; mine = mineBefore;`) is what lets a name of three or more constituents count for this drug when the drug is not next to the last name, e.g. `isoniazid / pyrazinamide / rifampin`, which is an alias on the shipped Rifampicin row.
   - **Checked in review:** short-circuiting that step left the suite green.
   - **If it is dropped:** such a name would get the sentence appended, so it would be said twice, which is the safe direction.
   - **Fix:** add one three-name case to `aPhraseAfterACombinationNameIncludingThisDrugStatesIt`.
