# issue 4531 slice 19: PublishingShell item publish history

- Issue: https://github.com/intersoftdatalabs-in/percussioncms/issues/4740
- Opened by natechadwick-intsof on 2026-09-22, closed on 2026-09-22
- Labels: enhancement, 8.2, ui, operator:grok, operator:night-issue-prs, p2, model:grok-4.6
- Fix commit: 987c340caa044e6a867f2b0510fdfa80c0f2ec31

## Report

Parent: #4531

## Slice goal
Show **item publishing history** for a selected content item inside PublishingShell (ITM-06). Operators see recent publish/unpublish attempts (status, edition or site, time) without the legacy jQuery item publisher. Map 400/403/404.

## Out of scope
Schedule dates (sibling). Takedown/unpublish write (sibling). Full or incremental site publish (already shipped). qa-task #1371. JSF page deletes.

## Acceptance criteria
- [ ] PublishingShell shows item publish history for a selected item
- [ ] 400/403/404 mapped in the UI
- [ ] Playwright surface-filtered spec under modules/perc-qa-automation
- [ ] product-docs/8.2 updated for the history panel
- [ ] Update parent #4531 Agent progress section

## Change class
One vertical user-visible increment (REST + sitemanage + WebUI + Playwright + product-docs as needed). Do not split layers.

H2 QA: perc-devctl qa-up → qa-health → TEST_CMS_URL → npm run test:surface → qa-down.

Leave unassigned. Do not add In Progress.

> Co-Authored by Grok Build 1.0.40 using grok-4.6 with agent night-issue-prs-triage.
