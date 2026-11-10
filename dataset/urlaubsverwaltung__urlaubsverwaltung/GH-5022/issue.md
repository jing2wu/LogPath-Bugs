# Krankmeldung: Verlängerungen können invalide Krankmeldungen erzeugen

- Issue: https://github.com/urlaubsverwaltung/urlaubsverwaltung/issues/5022
- Opened by grafjo on 2024-12-10, closed on 2024-12-13
- Labels: type: bug, topic: sick note, status: planned
- Fix commit: 86a85c321af32c69d6ef4a08f52336c56d721299

## Report

Durch das Beta-Feature "Benutzer können Krankmeldungen selbst eintragen" in den Einstellungen, siehe

![image](https://github.com/user-attachments/assets/4f99c07d-6296-4dc8-86a3-98bf6b5b2576)

kann es dazu führen, dass eine einzelne Krankmeldung zunächst mit einem halben Tag angelegt wird und man diesen dann um einen Tag verlängert, wird dieser fälschlicherweise um einen Tag erweitert und ist dann 1,5 Tage lang. Dies ist inkorrekt. In diesem Fall müssten zwei Krankmeldungen angelegt werden.


**Ein Symptom davon ist dann:**
Hat man eine Krankheit eingetragen, welche gegen die Validierung von Periode https://github.com/urlaubsverwaltung/urlaubsverwaltung/blob/main/src/main/java/org/synyx/urlaubsverwaltung/period/Period.java#L24 verstößt und diese im Ical Kalender enthalten ist, so ist es nicht mehr möglich den Ical Kalender abzurufen.

Im Hintergrund fliegt eine IllegalArgumentException, triggert den Error-Handler von Spring Boot und man wird zur Login-Seite geleitet.

Beispiel Sicknote aus der DB

| id | start_date  | end_date    | day_length |
|----|-------------|-------------|------------|
| 1  | 2024-12-02  | 2024-12-03  | NOON       |

## Comment by honnel on 2024-12-11

Dieser Zustand kann erreicht werden durch die Verlängerung einer Abwesenheit durch einen Benutzer, der bereits am Vortag (in diesem Fall nur einen halben Tag) abwesend war. Fachlich sollte eine Abwesenheit von 1,5 Tagen dabei rauskommen.
