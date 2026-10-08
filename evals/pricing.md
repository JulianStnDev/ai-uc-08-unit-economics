# Pricing: Preiskorridor je Kundentyp und Abrechnungsart

Erzeugt von `scripts/pricing.py` aus `data/annahmen.csv`. 10.000 Tickets je Kunde und Monat, alle Annahmen auf „mittel“ außer den Minuten ohne Agent (Hebel aus dem Tornado). Rechenweg: [docs/RECHENWEG_PRICING.md](../docs/RECHENWEG_PRICING.md).

## Unsere Vollkosten je Kunde und Monat (EUR)

| Posten | Rechnung | EUR je Monat |
|---|---|---|
| Tokens + Hosting variabel | 10.000 × 0,0298 | 298,27 |
| Hosting fest | Abrechnung | 2,67 |
| Einrichtung | 40 h × 58,50 EUR / 12 Monate | 195,00 |
| Kundensupport | 4 h × 58,50 EUR | 234,00 |
| **Vollkosten** | | **729,94** |
| **Untergrenze** (× 1,2) | | **875,93** |

Die Vollkosten sind für alle drei Kundentypen gleich (gleiche Ticketmenge). 59 % davon sind Personal beim Anbieter (Einrichtung und Kundensupport), 41 % Tokens und Hosting.

## Kundentypen

| Kundentyp | min ohne Agent | Ersparnis je Ticket (Modell, nach Tokens) | Brutto-Ersparnis je Ticket (vor Preis) | Stellen ohne Agent | Stellen mit Agent nötig | gelöst-Anteil |
|---|---|---|---|---|---|---|
| günstig | 5,0 | 1,15 | 1,1779 | 6,25 | 2,92 | 62,3 % |
| mittel | 8,0 | 1,93 | 1,9642 | 10,00 | 4,45 | 62,3 % |
| teuer | 14,4 | 3,61 | 3,6417 | 18,00 | 7,70 | 62,3 % |

Gelöst = ohne Übergabe und ohne Nacharbeit: Freigaben plus autonome Tickets ohne Nacharbeit (15 % + 55 % × 86 %). Stellen = Ticketminuten / 8.000 Minuten je Vollzeitstelle und Monat (1.600 h / 12).

## Preiskorridor (EUR)

| Kundentyp | Abrechnung | Einheiten je Monat | **Untergrenze je Einheit** | **Obergrenze je Einheit** | Untergrenze je Monat | Obergrenze je Monat |
|---|---|---|---|---|---|---|
| günstig | pro Sitz | 6,25 | **140** | **942** | 876 | 5.890 |
| günstig | pro Ticket | 10.000 | **0,09** | **0,59** | 876 | 5.890 |
| günstig | pro gelöstem Ticket | 6.230 | **0,14** | **0,95** | 876 | 5.890 |
| mittel | pro Sitz | 10,00 | **88** | **982** | 876 | 9.821 |
| mittel | pro Ticket | 10.000 | **0,09** | **0,98** | 876 | 9.821 |
| mittel | pro gelöstem Ticket | 6.230 | **0,14** | **1,58** | 876 | 9.821 |
| teuer | pro Sitz | 18,00 | **49** | **1.012** | 876 | 18.209 |
| teuer | pro Ticket | 10.000 | **0,09** | **1,82** | 876 | 18.209 |
| teuer | pro gelöstem Ticket | 6.230 | **0,14** | **2,92** | 876 | 18.209 |

Bei fester Menge ergeben alle drei Abrechnungsarten denselben Monatsbetrag. Sie unterscheiden sich darin, wer das Risiko trägt, wenn sich etwas ändert: Stellenabbau beim Kunden (pro Sitz), Ticketmenge (pro Ticket) oder Lösungsquote (pro gelöstem Ticket).

## Wettbewerb: Intercom Fin

Geprüft in der Primärquelle (intercom.com/pricing und Hilfeartikel „Fin AI Agent outcomes“, 08.10.2026): **0,99 USD je Outcome** = 0,8857 EUR. Outcomes sind Lösungen **und** „Procedure Handoffs“ (Übergabe an einen Menschen über eine konfigurierte Prozedur), höchstens eines je Gespräch. Eine Lösung zählt auch „assumed“, wenn der Kunde ohne weitere Frage geht. Fins „gelöst“ ist also weiter gefasst als unseres (Nacharbeit-Fälle würden bei Fin oft als gelöst abgerechnet).

| Kundentyp | unser Korridor je gelöstem Ticket | Fin je Outcome | Fin je Monat, nur Lösungen | Fin je Monat, mit Übergaben | Lage von Fin im Korridor |
|---|---|---|---|---|---|
| günstig | 0,14 … 0,95 | 0,89 | 5.518 | 8.175 | bei 93 % des Korridors |
| mittel | 0,14 … 1,58 | 0,89 | 5.518 | 8.175 | bei 52 % des Korridors |
| teuer | 0,14 … 2,92 | 0,89 | 5.518 | 8.175 | bei 27 % des Korridors |

## Sitz-Erosion: Kunde baut im zweiten Jahr 30 % der Support-Stellen ab

Preis je Sitz im ersten Jahr so gesetzt, dass er den Monatsbetrag an Unter-, Mitte- oder Obergrenze trifft. Im zweiten Jahr ist die Einrichtung bezahlt, unsere Kosten sinken um diesen Anteil. Ticketmenge und damit Tokens bleiben gleich.

**günstig** (6,25 → 4,37 Sitze; nötig mit Agent wären 2,92)

| Preispunkt | Preis je Sitz | Umsatz Jahr 1 / Monat | Umsatz Jahr 2 / Monat | Kosten Jahr 1 / Jahr 2 | Aufschlag auf Kosten Jahr 1 | Aufschlag Jahr 2 | Preis je Sitz, damit Jahr 2 die Untergrenze hält |
|---|---|---|---|---|---|---|---|
| Preis an der Untergrenze | 140 | 876 | 613 | 730 / 535 | 20 % | 15 % | 147 |
| Preis in der Mitte | 541 | 3.383 | 2.368 | 730 / 535 | 363 % | 343 % | 147 |
| Preis an der Obergrenze | 942 | 5.890 | 4.123 | 730 / 535 | 707 % | 671 % | 147 |

**mittel** (10,00 → 7,00 Sitze; nötig mit Agent wären 4,45)

| Preispunkt | Preis je Sitz | Umsatz Jahr 1 / Monat | Umsatz Jahr 2 / Monat | Kosten Jahr 1 / Jahr 2 | Aufschlag auf Kosten Jahr 1 | Aufschlag Jahr 2 | Preis je Sitz, damit Jahr 2 die Untergrenze hält |
|---|---|---|---|---|---|---|---|
| Preis an der Untergrenze | 88 | 876 | 613 | 730 / 535 | 20 % | 15 % | 92 |
| Preis in der Mitte | 535 | 5.349 | 3.744 | 730 / 535 | 633 % | 600 % | 92 |
| Preis an der Obergrenze | 982 | 9.821 | 6.875 | 730 / 535 | 1245 % | 1185 % | 92 |

**teuer** (18,00 → 12,60 Sitze; nötig mit Agent wären 7,70)

| Preispunkt | Preis je Sitz | Umsatz Jahr 1 / Monat | Umsatz Jahr 2 / Monat | Kosten Jahr 1 / Jahr 2 | Aufschlag auf Kosten Jahr 1 | Aufschlag Jahr 2 | Preis je Sitz, damit Jahr 2 die Untergrenze hält |
|---|---|---|---|---|---|---|---|
| Preis an der Untergrenze | 49 | 876 | 613 | 730 / 535 | 20 % | 15 % | 51 |
| Preis in der Mitte | 530 | 9.542 | 6.680 | 730 / 535 | 1207 % | 1149 % | 51 |
| Preis an der Obergrenze | 1.012 | 18.209 | 12.746 | 730 / 535 | 2395 % | 2283 % | 51 |

30 % Abbau ist dabei vorsichtig: Mit Agent bräuchte der mittlere Kunde nur noch 4,45 von 10 Stellen, könnte also bis zu 56 % abbauen. Dann fiele unser Sitz-Umsatz um denselben Anteil.

Pro Ticket und pro gelöstem Ticket bleibt der Umsatz im zweiten Jahr gleich, weil sich an Ticketmenge und Lösungsquote nichts ändert. Bei pro Sitz verliert der Anbieter genau dann Umsatz, wenn der Agent wirkt: Der Kunde braucht weniger Menschen.
