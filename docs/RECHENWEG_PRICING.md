# Rechenweg Pricing von Hand: Kundentyp „mittel“, Abrechnung pro gelöstem Ticket

Jede Zeile lässt sich mit dem Taschenrechner nachprüfen. Eingaben: [data/annahmen.csv](../data/annahmen.csv), Skript: [scripts/pricing.py](../scripts/pricing.py). Die Kosten des Kunden je Ticket stammen aus [RECHENWEG.md](RECHENWEG.md) (Szenario mittel). Zwischenergebnisse mit 4 bis 7 Nachkommastellen.

## Eingaben

| Größe | Wert | Herkunft |
|---|---|---|
| Tickets je Monat | 10.000 | Vorgabe |
| Minuten ohne Agent | 8 min | Kundentyp mittel |
| Personal je Minute (Kunde) | 0,4420 EUR | RECHENWEG Schritt 1 |
| Szenario | Freigabe 15 % × 2 min, Übergabe 30 % × 8,8 min, Nacharbeit 14 % der autonomen Tickets | Szenario mittel |
| Tokens + Hosting variabel je Ticket | 0,0287076 + 0,0011192 EUR | RECHENWEG Schritte 3 und 4 |
| Hosting fest | 2,67 EUR je Monat | Abrechnung |
| Einrichtung | 40 h, auf 12 Monate verteilt | Annahme |
| Kundensupport | 4 h je Monat | Annahme |
| Stundensatz Anbieter | 58,50 EUR | Destatis 2025, Information und Kommunikation |
| Aufschlag | 20 % auf die Vollkosten | Vorgabe |
| Anteil, der beim Kunden bleibt | mindestens 50 % der Ersparnis | Vorgabe |

## Schritt 1: Was der Kunde mit Agent noch an Personal zahlt (je Ticket)

Freigabe: 0,15 × 2 × 0,4420 = 0,1326000 EUR
Übergabe: 0,30 × 8,8 × 0,4420 = 1,1668800 EUR
Nacharbeit: 0,55 × 0,14 × 8 × 0,4420 = 0,2722720 EUR
Summe Personal mit Agent: 0,1326 + 1,16688 + 0,272272 = **1,5717520 EUR**

## Schritt 2: Brutto-Ersparnis des Kunden (vor unserem Preis)

Ohne Agent: 8 × 0,4420 = 3,5360 EUR
Brutto-Ersparnis je Ticket: 3,5360 − 1,5717520 = **1,9642480 EUR**
Je Monat: 1,9642480 × 10.000 = **19.642,48 EUR**

Tokens und Hosting stehen hier nicht drin, die tragen jetzt wir. Der Kunde zahlt stattdessen unseren Preis.

## Schritt 3: Unsere Vollkosten je Monat

Tokens + Hosting variabel: (0,0287076 + 0,0011192) × 10.000 = 0,0298268 × 10.000 = 298,27 EUR
Hosting fest: 2,67 EUR
Einrichtung: 40 h × 58,50 EUR / 12 = 2.340 / 12 = 195,00 EUR
Kundensupport: 4 h × 58,50 EUR = 234,00 EUR
Vollkosten: 298,27 + 2,67 + 195,00 + 234,00 = **729,94 EUR je Monat**

## Schritt 4: Wie viele Tickets sind „gelöst“?

Gelöst = ohne Übergabe und ohne Nacharbeit.
Autonome Tickets: 100 % − 15 % − 30 % = 55 %, davon ohne Nacharbeit: 55 % × (1 − 0,14) = 47,3 %
Dazu die Freigaben (keine Übergabe, keine Nacharbeit): 15 %
Gelöst-Anteil: 15 % + 47,3 % = **62,3 %**, also 0,623 × 10.000 = **6.230 gelöste Tickets je Monat**

## Schritt 5: Untergrenze je gelöstem Ticket

Monatsbetrag: 729,94 × 1,2 = 875,93 EUR
Je gelöstem Ticket: 875,93 / 6.230 = **0,1406 EUR**

## Schritt 6: Obergrenze je gelöstem Ticket

Der Kunde behält mindestens 50 % von 19.642,48 EUR, wir bekommen höchstens die andere Hälfte:
Monatsbetrag: 0,5 × 19.642,48 = 9.821,24 EUR
Je gelöstem Ticket: 9.821,24 / 6.230 = **1,5764 EUR**

**Korridor: 0,14 bis 1,58 EUR je gelöstem Ticket**, also 876 bis 9.821 EUR im Monat.

## Schritt 7: Einordnung gegen Intercom Fin

Fin: 0,99 USD je Outcome / 1,1177 = 0,8857 EUR (geprüft auf intercom.com, 08.10.2026)
Lage im Korridor: (0,8857 − 0,1406) / (1,5764 − 0,1406) = 0,7451 / 1,4358 = **52 %**

Fin liegt also etwa in der Mitte unseres Korridors. Zwei Unterschiede machen Fin für den Kunden teurer, als die 0,89 EUR aussehen:
- Fin berechnet auch „Procedure Handoffs“ (Übergaben) mit 0,99 USD. Laufen alle Übergaben (30 %) darüber, zahlt der Kunde 0,8857 × (6.230 + 3.000) = 8.175 EUR statt 0,8857 × 6.230 = 5.518 EUR im Monat.
- Fin zählt eine Lösung schon als gelöst, wenn der Kunde ohne weitere Frage geht („assumed resolution“). Unsere Definition zieht die Nacharbeit ab.

## Schritt 8: Was das für den Kunden heißt

Bei einem Preis in der Korridormitte, (0,1406 + 1,5764) / 2 = 0,8585 EUR je gelöstem Ticket:
Kunde zahlt 0,8585 × 6.230 = 5.348,46 EUR im Monat
Kunde behält 19.642,48 − 5.348,46 = 14.294,02 EUR, das sind 14.294,02 / 19.642,48 = **72,8 %** seiner Ersparnis
Wir verdienen 5.348,46 − 729,94 = 4.618,52 EUR im Monat über den Vollkosten
