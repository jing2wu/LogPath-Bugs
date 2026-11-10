# Exclude "followed" leagues

- Issue: https://github.com/axel3rd/mpg-coach-bot/issues/255
- Opened by axel3rd on 2023-08-10, closed on 2023-08-10
- Labels: bug
- Fix commit: e59df0baf4cdc27e11ca4a63f45550c5f356c524

## Report

When some leagues are "followed", crash with:

```
java.lang.UnsupportedOperationException: League id 'null' should start with 'mpg_division_'
	at org.blondin.mpg.root.MpgClient.getDivision(MpgClient.java:69)
	at org.blondin.mpg.Main.processGames(Main.java:181)
	at org.blondin.mpg.Main.processLeague(Main.java:122)
	at org.blondin.mpg.Main.process(Main.java:82)
```

=> As some other league state (*terminated*, ...) this kind of league should be "excluded" (transparency, no log displayed).

## Comment by mansuydejean on 2023-08-10

Excellent! Merci

## Comment by axel3rd on 2023-08-10

👍.

11-SNAPSHOT générée !
Je ferai une release la semaine prochaine pendant mes vacances après une
première journée d'usage ce weekend pour vérifier que tout se passe bien.
(Genre la "super league" je sais plus si c'est correctement exclu comme la
league des champions)

Le jeu. 10 août 2023 à 14:39, Mansuy Dejean ***@***.***> a
écrit :

> Excellent! Merci
>
> —
> Reply to this email directly, view it on GitHub
> <https://github.com/axel3rd/mpg-coach-bot/issues/255#issuecomment-1673140915>,
> or unsubscribe
> <https://github.com/notifications/unsubscribe-auth/AAWHBOMOVIFPW3ODYM546S3XUTI67ANCNFSM6AAAAAA3LG4GZ4>
> .
> You are receiving this because you modified the open/close state.Message
> ID: ***@***.***>
>


-- 
Alix Lourme
