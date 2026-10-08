# Rechenweg Build vs. Buy von Hand: A (selbst betreiben) gegen C (unser Produkt), 10.000 Tickets im Monat

Sicht des Käufers FocusFlow. Jede Zeile lässt sich mit dem Taschenrechner nachprüfen. Eingaben: [data/annahmen.csv](../data/annahmen.csv), Skript: [scripts/build_buy.py](../scripts/build_buy.py). Alle Annahmen auf „mittel“.

Gezählt werden nur entscheidungsrelevante Kosten. Was in A und C gleich ist (Teamleitung, Helpdesk-Lizenzen für Menschen), fehlt. Die Minuten, die Menschen an Tickets arbeiten, sind drin. Bei A und C sind sie gleich, weil es derselbe Agent ist.

## Schritt 1: Personal an Tickets (A und C gleich)

Aus [RECHENWEG.md](RECHENWEG.md), Schritt 5: Freigabe 0,1326 + Übergabe 1,16688 + Nacharbeit 0,272272 = 1,571752 EUR je Ticket
× 10.000 = **15.717,52 EUR je Monat**

## Schritt 2: A, Technik

Tokens + Hosting variabel: 0,0298268 EUR × 10.000 = 298,27 EUR
Hosting fest (Abrechnung Cloud Run, Neon 0 EUR): 2,67 EUR
Technik A: 298,27 + 2,67 = **300,94 EUR**

## Schritt 3: A, interner Aufwand

Laufender Aufwand (TCO, Annahmen):

| Aufgabe | h je Monat |
|---|---|
| Goldset und Evals pflegen (UC2, UC4) | 8 |
| Judge betreiben und nachkalibrieren (UC7) | 4 |
| Sicherheit (UC6) | 6 |
| Betrieb inklusive Bereitschaft (UC7) | 16 |
| Modell- und SDK-Updates | 4 |
| Datenschutz | 3 |
| Regeln und Werkzeuge anpassen | 4 |
| **Summe** | **45** |

45 h × 58,50 EUR = 2.632,50 EUR

Bau, grob aus der Git-Historie: 8 aktive Tage × 8 h × Faktor 2 (Demo → Produktion) = 128 h
128 h × 58,50 EUR = 7.488,00 EUR, auf 24 Monate verteilt: 7.488 / 24 = 312,00 EUR

Interner Aufwand A: 2.632,50 + 312,00 = **2.944,50 EUR**

## Schritt 4: A gesamt

300,94 + 2.944,50 + 15.717,52 = **18.962,96 EUR je Monat**

## Schritt 5: C, Preis

Gelöste Tickets: (15 % + 55 % × 86 %) × 10.000 = 62,3 % × 10.000 = 6.230
Preis: 450 + 0,75 × 6.230 = 450 + 4.672,50 = **5.122,50 EUR**

## Schritt 6: C, interner Aufwand beim Käufer

Laufend: 2 h × 58,50 EUR = 117,00 EUR
Einrichtung: 16 h × 58,50 EUR = 936 EUR, auf 24 Monate verteilt: 936 / 24 = 39,00 EUR
Interner Aufwand C: 117,00 + 39,00 = **156,00 EUR**

## Schritt 7: C gesamt und Vergleich

5.122,50 + 156,00 + 15.717,52 = **20.996,02 EUR je Monat**

A − C = 18.962,96 − 20.996,02 = **−2.033,06 EUR**: Bei 10.000 Tickets ist selbst betreiben rund 2.000 EUR im Monat günstiger.

## Schritt 8: Ab welcher Menge ist A günstiger als C?

Das Personal ist gleich und fällt heraus. Übrig bleiben Fixkosten gegen Stückkosten:

| | fest je Monat | je Ticket |
|---|---|---|
| A | 2,67 + 2.944,50 = 2.947,17 EUR | 0,0298268 EUR |
| C | 450 + 156,00 = 606,00 EUR | 0,75 × 0,623 = 0,46725 EUR |

Gleichstand: 2.947,17 + 0,0298268 × N = 606,00 + 0,46725 × N
N = (2.947,17 − 606,00) / (0,46725 − 0,0298268) = 2.341,17 / 0,4374232 = **5.352 Tickets je Monat**

Darunter ist C günstiger, darüber A. Der Kipppunkt hängt fast vollständig am laufenden Aufwand für A. Mit 21 h statt 45 h im Monat läge er bei 2.142 Tickets, mit 100 h bei 12.708 ([evals/build_buy.md](../evals/build_buy.md)).
