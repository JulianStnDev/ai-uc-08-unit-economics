# Rechenweg von Hand: Szenario „mittel“, 10.000 Tickets im Monat

Jede Zeile lässt sich mit dem Taschenrechner nachprüfen. Die Eingaben stehen in [data/annahmen.csv](../data/annahmen.csv), das Skript [scripts/modell.py](../scripts/modell.py) rechnet dasselbe ohne Zwischenrundung. Zwischenergebnisse stehen hier mit 7 Nachkommastellen, das Endergebnis auf Cent gerundet.

## Eingaben

| Größe | Wert | Herkunft |
|---|---|---|
| Kurs | 1,1177 USD je EUR | EZB, 07.10.2026 |
| Agent je Ticket | 0,02804 USD | gemessen, UC6-Goldset, Mittel aus 45 Läufen |
| Haiku-Antwort je Freigabe | 0,00483 USD | gemessen, Live, Mittel aus 5 |
| Judge je Urteil | 0,01661 USD | gemessen, Live, Mittel aus 5 |
| Judge-Quote | 20 % | Konfiguration UC7 |
| Laufzeit je Ticket | 26,06 s | gemessen, Live, Mittel aus 13 |
| Auslastung der Instanz | 50 % | Annahme |
| Cloud Run Tier 2 | 0,0000216 USD je vCPU-s + 0,0000024 USD je GiB-s | Preisliste |
| Hosting fest | 2,67 EUR je Monat | Abrechnung: 0,89 EUR in 10 Tagen × 3 |
| Personal je Minute | 0,4420 EUR | 2.922 EUR × 12 × 1,21 / 1.600 h / 60 |
| Minuten ohne Agent | 8 min je Ticket | Annahme zwischen Branchenwerten |
| **Szenario mittel** | Freigabe 15 %, Übergabe 30 %, 2 min je Freigabe, Faktor Übergabe 1,1, Nacharbeit 10 % der autonomen Tickets | Szenario |

## Schritt 1: Personal je Minute

2.922 × 12 = 35.064 EUR Brutto im Jahr
35.064 × 1,21 = 42.427,44 EUR Arbeitgeberkosten im Jahr
42.427,44 / 1.600 = 26,5172 EUR je Stunde
26,5172 / 60 = 0,44195 EUR je Minute, **gerundet 0,4420 EUR** (mit diesem Wert rechnet alles Weitere)

## Schritt 2: Ohne Agent, je Ticket

8 min × 0,4420 EUR = **3,5360 EUR je Ticket**

## Schritt 3: Mit Agent, Tokens je Ticket (USD, dann EUR)

Jedes Ticket: Agent 0,02804 USD
Nur bei Freigabe (15 %): 0,15 × 0,00483 = 0,0007245 USD
Nur in der Judge-Stichprobe (20 %): 0,20 × 0,01661 = 0,0033220 USD
Summe: 0,02804 + 0,0007245 + 0,0033220 = 0,0320865 USD
In EUR: 0,0320865 / 1,1177 = **0,0287076 EUR**

## Schritt 4: Mit Agent, Hosting variabel je Ticket

Abgerechnete Instanzzeit je Ticket: 26,06 s / 0,5 = 52,12 s
Preis je Instanz-Sekunde (1 vCPU + 1 GiB): 0,0000216 + 0,0000024 = 0,0000240 USD
52,12 × 0,0000240 = 0,0012509 USD
In EUR: 0,0012509 / 1,1177 = **0,0011192 EUR**

## Schritt 5: Mit Agent, Menschenzeit je Ticket

Minuten je Übergabe: 8 min × 1,1 = 8,8 min
Anteil autonomer Tickets: 100 % − 15 % − 30 % = 55 %

Freigabe: 0,15 × 2 min × 0,4420 EUR = **0,1326000 EUR**
Übergabe: 0,30 × 8,8 min × 0,4420 EUR = **1,1668800 EUR**
Nacharbeit: 0,55 × 0,10 × 8 min × 0,4420 EUR = **0,1944800 EUR**

## Schritt 6: Mit Agent, variabel und fix je Ticket

Variabel: 0,0287076 + 0,0011192 + 0,1326000 + 1,1668800 + 0,1944800 = **1,5237868 EUR**
Fix: 2,67 EUR / 10.000 Tickets = **0,0002670 EUR**
Mit Agent gesamt: 1,5237868 + 0,0002670 = **1,5240538 EUR je Ticket**

## Schritt 7: Monat und Ersparnis

| | je Ticket | × 10.000 Tickets |
|---|---|---|
| Ohne Agent | 3,5360000 EUR | **35.360,00 EUR** |
| Mit Agent | 1,5240538 EUR | **15.240,54 EUR** |
| Ersparnis | 2,0119462 EUR | **20.119,46 EUR** |

Ersparnis in Prozent: 2,0119462 / 3,5360 = **56,9 %**

Woraus die Kosten mit Agent bestehen: Übergaben 1,1669 von 1,5241 EUR (76,6 %), Nacharbeit 12,8 %, Freigaben 8,7 %, Tokens 1,9 %, Hosting 0,1 %.

## Schritt 8: Kipppunkt im Szenario mittel

Gesucht ist die Übergabequote q, bei der mit Agent genauso viel kostet wie ohne. Steigt q, schrumpfen die autonomen Tickets und mit ihnen die Nacharbeit (1 − 0,15 − q).

Fester Teil (hängt nicht von q ab): 0,0287076 + 0,0011192 + 0,1326000 + 0,0002670 = 0,1626938 EUR
Nacharbeit bei q = 0: 0,85 × 0,10 × 8 × 0,4420 = 0,3005600 EUR
Ersparnis bei q = 0: 3,5360 − 0,1626938 − 0,3005600 = 3,0727462 EUR

Jeder Prozentpunkt mehr Übergabe kostet eine Übergabe und spart eine mögliche Nacharbeit:
8,8 × 0,4420 − 0,10 × 8 × 0,4420 = 3,8896 − 0,3536 = 3,5360 EUR je 100 % Übergabequote

q = 3,0727462 / 3,5360 = **86,9 %**

Weil 15 % der Tickets Freigaben sind, kann die Übergabequote höchstens 85 % erreichen. Im Szenario mittel gibt es also weiterhin **keinen Kipppunkt**, aber nur noch knapp (86,9 % gegen 85 %). Im pessimistischen Szenario liegt er bei **66 %** (Tabelle in [evals/modell.md](../evals/modell.md)).
