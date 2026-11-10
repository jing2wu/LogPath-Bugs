# Verfall von Resturlaub pro Mitarbeitenden deaktivieren standardmäig aktiviert

- Issue: https://github.com/urlaubsverwaltung/urlaubsverwaltung/issues/4624
- Opened by derTobsch on 2024-04-22, closed on 2024-04-22
- Labels: type: bug, status: planned
- Fix commit: a48b1f066bdc80461a04d450abd3b58dc6bbe68d

## Report

Beim Anlegen eines neuen Mitarbeitenden, wird automatisch der individuelle Verfall von Resturlaub pro Mitarbeitenden aktiviert (#3081). 

Siehe dazu 

https://github.com/urlaubsverwaltung/urlaubsverwaltung/blob/main/src/main/java/org/synyx/urlaubsverwaltung/account/AccountInteractionServiceImpl.java#L60

und wurde mit

https://github.com/urlaubsverwaltung/urlaubsverwaltung/pull/3215/files#diff-03651dd19830d6444aa327e23bef9410020e565da00dfe67565959abc3663670R72

#3081 wohl aus versehen aktiviert.

Das Verhalten soll so geändert werden, dass bei Anlage einer neuen Person der individuelle Verfall von Resturlaub deaktiviert ist und die globale Einstellung gültig ist.
