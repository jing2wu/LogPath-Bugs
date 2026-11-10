# Don't throw error about label reference when CSV secondary instance is empty

- Issue: https://github.com/getodk/javarosa/issues/743
- Opened by lognaturel on 2024-02-01, closed on 2024-02-01
- Labels: bug
- Fix commit: f5012d9733b470ae140dbda6ba5fad516b45d326

## Report

#### Software versions 
JavaRosa v4.2.1

#### Problem description
`fi.getTemplatePath(itemset.labelRef)` in `FormInstanceParser` returns `null` when an external secondary instance is empty, leading to a parse exception with message `<label> node for itemset doesn't exist!`

#### Steps to reproduce the problem
Load a form with a select on an external secondary instance. In the external secondary instance, include the `name` and `label` columns in the header, but don't add any content rows.

#### Expected behavior
Either no check at all on this at parse time or no error in this case.

#### Other information 
Things you tried, stack traces, related issues, suggestions on how to fix it...
