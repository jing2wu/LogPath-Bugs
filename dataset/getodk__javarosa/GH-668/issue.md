# xforms-value-changed events fired before dependent calculations are recomputed

- Issue: https://github.com/getodk/javarosa/issues/668
- Opened by lognaturel on 2022-04-11, closed on 2022-05-06
- Labels: bug
- Fix commit: 3b174cac08484eb9dbbe8aa36b3d997c41ee5d04

## Report

Currently `xforms-value-changed` events are fired before dependent calculations are recomputed. This means that if you have `fieldA` which is user-entered, then `calcA` which produces a value based on `fieldA`, it's not possible to have a `setvalue` action triggered by `fieldA` which uses `calcA`: `calcA` will not be updated yet.

For a practical example, see [this form](https://docs.google.com/spreadsheets/d/1ZFE7aLMrQ7FJ8kjH1oN-41p8EsYGTA4Rpo82RFGl92k/edit#gid=0). For the two `text` fields we'd like to use the calculate values but we can't because of this bug.
