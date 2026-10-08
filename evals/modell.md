# Kostenmodell: Ergebnisse

Erzeugt von `scripts/modell.py` aus `data/annahmen.csv`. Beträge in EUR, Tokens umgerechnet mit 1,1177 USD/EUR. Rechenweg von Hand: [docs/RECHENWEG.md](../docs/RECHENWEG.md).

## Szenarien

| Szenario | Freigabe | Übergabe | autonom | Nacharbeit (der autonomen) | min/Freigabe | Faktor Übergabe | min/Übergabe |
|---|---|---|---|---|---|---|---|
| optimistisch | 10 % | 15 % | 75 % | 5 % | 1 | 1,0 | 8,0 |
| mittel | 15 % | 30 % | 55 % | 14 % | 2 | 1,1 | 8,8 |
| pessimistisch | 20 % | 50 % | 30 % | 20 % | 4 | 1,3 | 10,4 |

## Kosten je Ticket (EUR)

| Szenario | Tickets/Monat | Tokens | Hosting variabel | Freigabe | Übergabe | Nacharbeit | **variabel** | Fix je Ticket | **mit Agent** | **ohne Agent** | **Ersparnis** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| optimistisch | 1.000 | 0,0285 | 0,0011 | 0,0442 | 0,5304 | 0,1326 | **0,7368** | 0,0027 | **0,7395** | **3,5360** | **2,7965** |
| optimistisch | 10.000 | 0,0285 | 0,0011 | 0,0442 | 0,5304 | 0,1326 | **0,7368** | 0,0003 | **0,7371** | **3,5360** | **2,7989** |
| optimistisch | 100.000 | 0,0285 | 0,0011 | 0,0442 | 0,5304 | 0,1326 | **0,7368** | 0,0000 | **0,7368** | **3,5360** | **2,7992** |
| mittel | 1.000 | 0,0287 | 0,0011 | 0,1326 | 1,1669 | 0,2723 | **1,6016** | 0,0027 | **1,6042** | **3,5360** | **1,9318** |
| mittel | 10.000 | 0,0287 | 0,0011 | 0,1326 | 1,1669 | 0,2723 | **1,6016** | 0,0003 | **1,6018** | **3,5360** | **1,9342** |
| mittel | 100.000 | 0,0287 | 0,0011 | 0,1326 | 1,1669 | 0,2723 | **1,6016** | 0,0000 | **1,6016** | **3,5360** | **1,9344** |
| pessimistisch | 1.000 | 0,0289 | 0,0011 | 0,3536 | 2,2984 | 0,2122 | **2,8942** | 0,0027 | **2,8969** | **3,5360** | **0,6391** |
| pessimistisch | 10.000 | 0,0289 | 0,0011 | 0,3536 | 2,2984 | 0,2122 | **2,8942** | 0,0003 | **2,8945** | **3,5360** | **0,6415** |
| pessimistisch | 100.000 | 0,0289 | 0,0011 | 0,3536 | 2,2984 | 0,2122 | **2,8942** | 0,0000 | **2,8942** | **3,5360** | **0,6418** |

## Kosten je Monat (EUR)

| Szenario | Tickets/Monat | ohne Agent | mit Agent | davon variabel | davon fix | Ersparnis | Ersparnis in % |
|---|---|---|---|---|---|---|---|
| optimistisch | 1.000 | 3.536,00 | 739,48 | 736,81 | 2,67 | 2.796,52 | 79,1 % |
| optimistisch | 10.000 | 35.360,00 | 7.370,78 | 7.368,11 | 2,67 | 27.989,22 | 79,2 % |
| optimistisch | 100.000 | 353.600,00 | 73.683,74 | 73.681,07 | 2,67 | 279.916,26 | 79,2 % |
| mittel | 1.000 | 3.536,00 | 1.604,25 | 1.601,58 | 2,67 | 1.931,75 | 54,6 % |
| mittel | 10.000 | 35.360,00 | 16.018,46 | 16.015,79 | 2,67 | 19.341,54 | 54,7 % |
| mittel | 100.000 | 353.600,00 | 160.160,55 | 160.157,88 | 2,67 | 193.439,45 | 54,7 % |
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

Szenario mittel, 10.000 Tickets/Monat, Ersparnis je Ticket 1,9342 EUR. Je Zeile wandert genau eine Annahme von niedrig auf hoch, alle anderen bleiben auf mittel. Diagramm: [docs/tornado.svg](../docs/tornado.svg).

| Rang | Annahme | niedrig … hoch | Ersparnis bei niedrig | Ersparnis bei hoch | Ausschlag |
|---|---|---|---|---|---|
| 1 | Minuten ohne Agent (`min_ohne_agent`) | 5 … 14,4 | 1,1478 | 3,6116 | 2,4638 |
| 2 | Personalkosten je Minute (`eur_je_minute`) | 0,37 … 0,75 | 1,6053 | 3,3029 | 1,6976 |
| 3 | Übergabequote (`anteil_uebergabe`) | 0,15 … 0,50 | 2,4433 | 1,2552 | 1,1881 |
| 4 | Faktor Minuten je Übergabe (`faktor_uebergabe`) | 1 … 1,3 | 2,0402 | 1,7220 | 0,3182 |
| 5 | Anteil Nacharbeit (`anteil_nacharbeit`) | 0,05 … 0,20 | 2,1092 | 1,8175 | 0,2917 |
| 6 | Minuten je Freigabe (`min_freigabe`) | 1 … 4 | 2,0005 | 1,8016 | 0,1989 |
| 7 | Freigabe-Anteil (`anteil_freigabe`) | 0,10 … 0,20 | 1,9538 | 1,9145 | 0,0393 |
| 8 | Auslastung Cloud Run (`auslastung`) | 1 … 0,25 | 1,9347 | 1,9330 | 0,0017 |

## Reparatur-Kandidat T04: Frist im Werkzeug berechnen

Szenario mittel, 10.000 Tickets/Monat. Ohne T04 hätte der deployte Agent 1 von 26 autonomen Läufen mit falscher Kernaussage (3,9 % statt 14 %). Repariert bekäme T04 eine Empfehlung, also eine Freigabe: 10,3 % der autonomen Tickets (5,7 % aller Tickets) wandern von autonom zu Freigabe.

| Variante | Freigabe | Nacharbeit | Nacharbeit je Ticket | Freigabe je Ticket | mit Agent je Ticket | Monat mit Agent | **Ersparnis gegenüber heute / Monat** |
|---|---|---|---|---|---|---|---|
| heute (T04-Fehler drin) | 15,0 % | 14,0 % | 0,2723 | 0,1326 | 1,6018 | 16.018,46 | **0,00** |
| nur Nacharbeit sinkt | 15,0 % | 3,9 % | 0,0749 | 0,1326 | 1,4044 | 14.044,49 | **1.973,97** |
| Nacharbeit sinkt, T04 wird Freigabe | 20,7 % | 3,9 % | 0,0671 | 0,1829 | 1,4472 | 14.472,25 | **1.546,20** |

Die Erstattungen selbst sind nicht eingerechnet: Auf sie hat die Kundin Anspruch, ein Mensch ohne Agent würde sie ebenso auszahlen. Basis sind 29 autonome Goldset-Läufe, das ist eine Größenordnung, keine Prognose.

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
