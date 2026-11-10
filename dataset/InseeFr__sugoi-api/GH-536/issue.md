# :bug: Unable to erase a field

- Issue: https://github.com/InseeFr/sugoi-api/issues/536
- Opened by clement-dufaure on 2021-11-29, closed on 2021-12-02
- Labels: bug
- Fix commit: def2fed2581f488b37246e53e77eff1ac89a99ad

## Report

If the value empty ("") is given to an attribute, the new value "" is not accepted (set "" or delete attribute), and the value remains the old value
