# Kostenmodell: Ergebnisse

Erzeugt von `scripts/modell.py` aus `data/annahmen.csv`. Beträge in EUR, Tokens umgerechnet mit 1,1177 USD/EUR. Rechenweg von Hand: [docs/RECHENWEG.md](../docs/RECHENWEG.md).

## Szenarien

| Szenario | Freigabe | Übergabe | autonom | Nacharbeit (der autonomen) | min/Freigabe | Faktor Übergabe | min/Übergabe |
|---|---|---|---|---|---|---|---|
| optimistisch | 10 % | 15 % | 75 % | 5 % | 1 | 1,0 | 8,0 |
| mittel | 15 % | 30 % | 55 % | 10 % | 2 | 1,1 | 8,8 |
| pessimistisch | 20 % | 50 % | 30 % | 20 % | 4 | 1,3 | 10,4 |

## Kosten je Ticket (EUR)

| Szenario | Tickets/Monat | Tokens | Hosting variabel | Freigabe | Übergabe | Nacharbeit | **variabel** | Fix je Ticket | **mit Agent** | **ohne Agent** | **Ersparnis** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| optimistisch | 1.000 | 0,0285 | 0,0011 | 0,0442 | 0,5304 | 0,1326 | **0,7368** | 0,0027 | **0,7395** | **3,5360** | **2,7965** |
| optimistisch | 10.000 | 0,0285 | 0,0011 | 0,0442 | 0,5304 | 0,1326 | **0,7368** | 0,0003 | **0,7371** | **3,5360** | **2,7989** |
| optimistisch | 100.000 | 0,0285 | 0,0011 | 0,0442 | 0,5304 | 0,1326 | **0,7368** | 0,0000 | **0,7368** | **3,5360** | **2,7992** |
| mittel | 1.000 | 0,0287 | 0,0011 | 0,1326 | 1,1669 | 0,1945 | **1,5238** | 0,0027 | **1,5265** | **3,5360** | **2,0095** |
| mittel | 10.000 | 0,0287 | 0,0011 | 0,1326 | 1,1669 | 0,1945 | **1,5238** | 0,0003 | **1,5241** | **3,5360** | **2,0119** |
| mittel | 100.000 | 0,0287 | 0,0011 | 0,1326 | 1,1669 | 0,1945 | **1,5238** | 0,0000 | **1,5238** | **3,5360** | **2,0122** |
| pessimistisch | 1.000 | 0,0289 | 0,0011 | 0,3536 | 2,2984 | 0,2122 | **2,8942** | 0,0027 | **2,8969** | **3,5360** | **0,6391** |
| pessimistisch | 10.000 | 0,0289 | 0,0011 | 0,3536 | 2,2984 | 0,2122 | **2,8942** | 0,0003 | **2,8945** | **3,5360** | **0,6415** |
| pessimistisch | 100.000 | 0,0289 | 0,0011 | 0,3536 | 2,2984 | 0,2122 | **2,8942** | 0,0000 | **2,8942** | **3,5360** | **0,6418** |

## Kosten je Monat (EUR)

| Szenario | Tickets/Monat | ohne Agent | mit Agent | davon variabel | davon fix | Ersparnis | Ersparnis in % |
|---|---|---|---|---|---|---|---|
| optimistisch | 1.000 | 3.536,00 | 739,48 | 736,81 | 2,67 | 2.796,52 | 79,1 % |
| optimistisch | 10.000 | 35.360,00 | 7.370,78 | 7.368,11 | 2,67 | 27.989,22 | 79,2 % |
| optimistisch | 100.000 | 353.600,00 | 73.683,74 | 73.681,07 | 2,67 | 279.916,26 | 79,2 % |
| mittel | 1.000 | 3.536,00 | 1.526,46 | 1.523,79 | 2,67 | 2.009,54 | 56,8 % |
| mittel | 10.000 | 35.360,00 | 15.240,54 | 15.237,87 | 2,67 | 20.119,46 | 56,9 % |
| mittel | 100.000 | 353.600,00 | 152.381,35 | 152.378,68 | 2,67 | 201.218,65 | 56,9 % |
| pessimistisch | 1.000 | 3.536,00 | 2.896,87 | 2.894,20 | 2,67 | 639,13 | 18,1 % |
| pessimistisch | 10.000 | 35.360,00 | 28.944,70 | 28.942,03 | 2,67 | 6.415,30 | 18,1 % |
| pessimistisch | 100.000 | 353.600,00 | 289.422,95 | 289.420,28 | 2,67 | 64.177,05 | 18,1 % |

## Kipppunkt: Übergabequote, ab der der Agent nicht mehr günstiger ist

Freigabe-Anteil, Nacharbeit-Anteil und Faktor bleiben je Szenario fest, nur die Übergabequote wandert (die autonomen Tickets schrumpfen entsprechend). Möglich sind höchstens 100 % minus Freigabe-Anteil. Minuten je Übergabe wandern mit den Minuten ohne Agent. 10.000 Tickets/Monat.

| Szenario | Mensch allein 5 min | **8 min (mittel)** | 14,4 min | Übergabequote des Szenarios |
|---|---|---|---|---|
| optimistisch | kein (> 90 %) | **kein (> 90 %)** | kein (> 90 %) | 15 % |
| mittel | 84 % | **kein (> 85 %)** | kein (> 85 %) | 30 % |
| pessimistisch | 61 % | **66 %** | 71 % | 50 % |

Die Personalkosten je Minute verschieben den Kipppunkt kaum: Tokens und Hosting zusammen kosten je Ticket so viel wie wenige Sekunden Arbeitszeit. Entscheidend sind Faktor je Übergabe und Nacharbeit. Für die Höhe der Ersparnis zählen die Personalkosten dagegen voll, siehe Tornado.

## Sensitivität (Tornado)

Szenario mittel, 10.000 Tickets/Monat, Ersparnis je Ticket 2,0119 EUR. Je Zeile wandert genau eine Annahme von niedrig auf hoch, alle anderen bleiben auf mittel. Diagramm: [docs/tornado.svg](../docs/tornado.svg).

| Rang | Annahme | niedrig … hoch | Ersparnis bei niedrig | Ersparnis bei hoch | Ausschlag |
|---|---|---|---|---|---|
| 1 | Minuten ohne Agent (`min_ohne_agent`) | 5 … 14,4 | 1,1965 | 3,7517 | 2,5552 |
| 2 | Personalkosten je Minute (`eur_je_minute`) | 0,37 … 0,75 | 1,6701 | 3,4349 | 1,7648 |
| 3 | Übergabequote (`anteil_uebergabe`) | 0,15 … 0,50 | 2,5423 | 1,3047 | 1,2376 |
| 4 | Faktor Minuten je Übergabe (`faktor_uebergabe`) | 1 … 1,3 | 2,1180 | 1,7998 | 0,3182 |
| 5 | Anteil Nacharbeit (`anteil_nacharbeit`) | 0,05 … 0,20 | 2,1092 | 1,8175 | 0,2917 |
| 6 | Minuten je Freigabe (`min_freigabe`) | 1 … 4 | 2,0782 | 1,8793 | 0,1989 |
| 7 | Freigabe-Anteil (`anteil_freigabe`) | 0,10 … 0,20 | 2,0387 | 1,9852 | 0,0535 |
| 8 | Auslastung Cloud Run (`auslastung`) | 1 … 0,25 | 2,0125 | 2,0108 | 0,0017 |

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

### Wie viele fehlerfreie Fälle braucht „automatisch bis X EUR“? (Dreierregel)

Schwelle = gespart je Fall / X (der ungünstigste Betrag unter der Grenze). Nach der Dreierregel belegen n Fälle ohne Fehler eine Fehlerquote unter 3/n (95 %). Gebraucht werden also n = 3 / Schwelle fehlerfreie Fälle, aufgerundet. Bisher gemessen: 6 Doppelbuchungs-Läufe ohne falsche Erstattung (UC6 T01, T02), das belegt nur < 50 %.

| Grenze X | Schwelle (2 min) | **n fehlerfrei (2 min)** | n bei 1 / 2 / 4 min je Freigabe |
|---|---|---|---|
| bis 5 EUR | 17,8 % | **17** | 34 / 17 / 9 |
| bis 10 EUR | 8,9 % | **34** | 68 / 34 / 17 |
| bis 20 EUR | 4,4 % | **68** | 135 / 68 / 34 |
| bis 59 EUR | 1,5 % | **200** | 397 / 200 / 100 |
