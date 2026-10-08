# Kostenmodell: Ergebnisse

Erzeugt von `scripts/modell.py` aus `data/annahmen.csv`. Beträge in EUR, Tokens umgerechnet mit 1,1177 USD/EUR. Rechenweg von Hand: [docs/RECHENWEG.md](../docs/RECHENWEG.md).

## Szenarien

| Szenario | Freigabe | Übergabe | min/Freigabe | min/Übergabe |
|---|---|---|---|---|
| optimistisch | 10 % | 15 % | 1 | 6 |
| mittel | 15 % | 30 % | 2 | 8 |
| pessimistisch | 20 % | 50 % | 4 | 10 |

## Kosten je Ticket (EUR)

| Szenario | Tickets/Monat | Tokens | Hosting variabel | Freigabe | Übergabe | **variabel** | Fix je Ticket | **mit Agent** | **ohne Agent** | **Ersparnis** |
|---|---|---|---|---|---|---|---|---|---|---|
| optimistisch | 1.000 | 0,0285 | 0,0011 | 0,0442 | 0,3978 | **0,4716** | 0,0027 | **0,4743** | **3,5360** | **3,0617** |
| optimistisch | 10.000 | 0,0285 | 0,0011 | 0,0442 | 0,3978 | **0,4716** | 0,0003 | **0,4719** | **3,5360** | **3,0641** |
| optimistisch | 100.000 | 0,0285 | 0,0011 | 0,0442 | 0,3978 | **0,4716** | 0,0000 | **0,4716** | **3,5360** | **3,0644** |
| mittel | 1.000 | 0,0287 | 0,0011 | 0,1326 | 1,0608 | **1,2232** | 0,0027 | **1,2259** | **3,5360** | **2,3101** |
| mittel | 10.000 | 0,0287 | 0,0011 | 0,1326 | 1,0608 | **1,2232** | 0,0003 | **1,2235** | **3,5360** | **2,3125** |
| mittel | 100.000 | 0,0287 | 0,0011 | 0,1326 | 1,0608 | **1,2232** | 0,0000 | **1,2233** | **3,5360** | **2,3127** |
| pessimistisch | 1.000 | 0,0289 | 0,0011 | 0,3536 | 2,2100 | **2,5936** | 0,0027 | **2,5963** | **3,5360** | **0,9397** |
| pessimistisch | 10.000 | 0,0289 | 0,0011 | 0,3536 | 2,2100 | **2,5936** | 0,0003 | **2,5939** | **3,5360** | **0,9421** |
| pessimistisch | 100.000 | 0,0289 | 0,0011 | 0,3536 | 2,2100 | **2,5936** | 0,0000 | **2,5937** | **3,5360** | **0,9423** |

## Kosten je Monat (EUR)

| Szenario | Tickets/Monat | ohne Agent | mit Agent | davon variabel | davon fix | Ersparnis | Ersparnis in % |
|---|---|---|---|---|---|---|---|
| optimistisch | 1.000 | 3.536,00 | 474,28 | 471,61 | 2,67 | 3.061,72 | 86,6 % |
| optimistisch | 10.000 | 35.360,00 | 4.718,78 | 4.716,11 | 2,67 | 30.641,22 | 86,7 % |
| optimistisch | 100.000 | 353.600,00 | 47.163,74 | 47.161,07 | 2,67 | 306.436,26 | 86,7 % |
| mittel | 1.000 | 3.536,00 | 1.225,90 | 1.223,23 | 2,67 | 2.310,10 | 65,3 % |
| mittel | 10.000 | 35.360,00 | 12.234,94 | 12.232,27 | 2,67 | 23.125,06 | 65,4 % |
| mittel | 100.000 | 353.600,00 | 122.325,35 | 122.322,68 | 2,67 | 231.274,65 | 65,4 % |
| pessimistisch | 1.000 | 3.536,00 | 2.596,31 | 2.593,64 | 2,67 | 939,69 | 26,6 % |
| pessimistisch | 10.000 | 35.360,00 | 25.939,10 | 25.936,43 | 2,67 | 9.420,90 | 26,6 % |
| pessimistisch | 100.000 | 353.600,00 | 259.366,95 | 259.364,28 | 2,67 | 94.233,05 | 26,6 % |

## Kipppunkt: Übergabequote, ab der der Agent nicht mehr günstiger ist

Freigabe-Anteil und Minuten bleiben je Szenario fest, nur die Übergabequote wandert. Möglich sind höchstens 100 % minus Freigabe-Anteil. 10.000 Tickets/Monat.

| Szenario | Mensch allein 5 min | **8 min (mittel)** | 14,4 min | Übergabequote des Szenarios |
|---|---|---|---|---|
| optimistisch | 81 % | **kein (> 90 %)** | kein (> 90 %) | 15 % |
| mittel | 58 % | **kein (> 85 %)** | kein (> 85 %) | 30 % |
| pessimistisch | 41 % | **71 %** | kein (> 80 %) | 50 % |

Die Personalkosten je Minute verschieben den Kipppunkt kaum: Tokens und Hosting zusammen kosten je Ticket so viel wie wenige Sekunden Arbeitszeit. Entscheidend ist das Verhältnis Minuten je Übergabe zu Minuten ohne Agent.

## Option „Doppelbuchung automatisch erstatten“: Erwartungswert je Fall

Gespart je Fall: 2 min Freigabe × 0,4420 EUR/min + Haiku-Antwort 0,0043 EUR = **0,8883 EUR**. Erwarteter Verlust je Fall: Fehlerquote × Betrag. Netto = gespart − Verlust.

| Fehlerquote | Verlust bei 6,99 EUR | Netto bei 6,99 EUR | Verlust bei 59 EUR | Netto bei 59 EUR |
|---|---|---|---|---|
| 0,5 % | 0,0350 | 0,8534 | 0,2950 | 0,5933 |
| 1,0 % | 0,0699 | 0,8184 | 0,5900 | 0,2983 |
| 5,0 % | 0,3495 | 0,5388 | 2,9500 | -2,0617 |

Gewinnschwelle (Fehlerquote, bei der Netto = 0), je nach Minuten je Freigabe:

| min/Freigabe | gespart je Fall | Schwelle bei 6,99 EUR | Schwelle bei 59 EUR |
|---|---|---|---|
| 1 | 0,4463 | 6,4 % | 0,8 % |
| 2 | 0,8883 | 12,7 % | 1,5 % |
| 4 | 1,7723 | 25,4 % | 3,0 % |
