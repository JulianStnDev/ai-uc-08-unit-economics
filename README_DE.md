🇬🇧 [English version](README.md)

# UC8: Unit Economics, Pricing & Build-vs-Buy

> Stand 2026-10-08: Zahleninventur ([docs/INVENTUR.md](docs/INVENTUR.md)) und Kostenmodell ([evals/modell.md](evals/modell.md), Rechenweg: [docs/RECHENWEG.md](docs/RECHENWEG.md)). Pricing: [evals/pricing.md](evals/pricing.md), Rechenweg [docs/RECHENWEG_PRICING.md](docs/RECHENWEG_PRICING.md). Build-vs-Buy folgt.

## Problem
Der Support-Agent aus UC4/UC7 läuft als Web-Demo auf Cloud Run. Offen ist die Produktfrage dahinter: **Was kostet ein Support-Ticket mit dem Agent im Vergleich zu einem Ticket, das komplett ein Mensch bearbeitet?** Und daraus folgend: Wie ließe sich das bepreisen, und lohnt sich der Eigenbau gegenüber einem eingekauften Produkt?

Dieses Repo ist eine Entscheidungsvorlage, kein Produktcode. Grundlage sind die gemessenen Daten aus UC4, UC6 und UC7.

## PM-Entscheidung
Offen. Erster Schritt war eine Zahleninventur: Welche Zahlen gibt es schon, mit welcher Quelle, und welche fehlen für die Rechnung?

## Architekturskizze
```
UC4 Goldset (45 Läufe) ─┐
UC6 Goldset (45 Läufe) ─┼─▶ scripts/inventur.py ──▶ data/inventur.csv ──▶ docs/INVENTUR.md
UC7 Neon-Protokoll ─────┤      (nur lesend,          (Wert, Einheit, Modell,
Cloud Monitoring ───────┘       keine API-Kosten)     Quelle, Commit, Datum)
```

## Evaluationsergebnisse
Zahleninventur, Details in [docs/INVENTUR.md](docs/INVENTUR.md):

| Kennzahl | Wert | Quelle |
|---|---|---|
| Agent-Kosten je Ticket, Median / p95 | 0,0264 / 0,0422 USD | 45 Goldset-Läufe, deployter Stand (UC6) |
| Endgültige Antwort (Haiku) je Ticket mit Empfehlung, Median | 0,0047 USD | 5 Live-Läufe |
| Judge (Sonnet 5) je Urteil, Median | 0,0190 USD | 5 Live-Urteile, Stichprobe 20 % |
| Goldset-Läufe ohne Menschen | 29 von 45 (64 %) | UC6 Goldset |
| Echte Kundentickets im Betrieb | 0 | Neon: alle 13 Läufe sind Testläufe |

Kostenmodell (10.000 Tickets im Monat, Mensch allein 8 min × 0,4420 EUR/min = 3,54 EUR je Ticket):

| Szenario | Freigabe / Übergabe (Faktor Minuten 1,0 / 1,1 / 1,3, Nacharbeit 5 / 14 / 20 %) | mit Agent je Ticket | Ersparnis im Monat | Kipppunkt Übergabequote |
|---|---|---|---|---|
| optimistisch | 10 % / 15 % | 0,74 EUR | 27.989 EUR (79,2 %) | keiner |
| mittel | 15 % / 30 % | 1,60 EUR | 19.342 EUR (54,7 %) | keiner (87 % > 85 % möglich) |
| pessimistisch | 20 % / 50 % | 2,89 EUR | 6.415 EUR (18,1 %) | 66 % |

![Ersparnis je Ticket über der Übergabequote](docs/kipppunkt.svg)

Minuten je Übergabe = Minuten ohne Agent × 1,0 / 1,1 / 1,3. Nacharbeit: Anteil autonomer Tickets, die doch ein Mensch nacharbeitet, begründet in [docs/NACHARBEIT.md](docs/NACHARBEIT.md) (deployter Agent im Goldset: 4 von 29 autonomen Läufen mit falscher Kernaussage = 14 %, davon 3 systematisch bei T04). Würde die Frist im Werkzeug berechnet, sparte das etwa 1.546 EUR im Monat bei 10.000 Tickets (offene Option, [docs/decisions.md](docs/decisions.md)).

Tokens kosten je Ticket 0,03 EUR, so viel wie 4 Sekunden Arbeitszeit. Am stärksten bewegen die Ersparnis die Minuten ohne Agent, die Personalkosten und die Übergabequote:

![Tornado: Sensitivität der Ersparnis je Ticket](docs/tornado.svg)

Pricing aus Anbieter-Sicht (10.000 Tickets je Kunde und Monat). Untergrenze = unsere Vollkosten + 20 %, Obergrenze = Kunde behält 50 % seiner Ersparnis:

| Kundentyp | pro Sitz (Monat) | pro Ticket | pro gelöstem Ticket | Korridor je Monat |
|---|---|---|---|---|
| günstig (5 min) | 140 … 942 EUR | 0,09 … 0,59 EUR | 0,14 … 0,95 EUR | 876 … 5.890 EUR |
| mittel (8 min) | 88 … 982 EUR | 0,09 … 0,98 EUR | 0,14 … 1,58 EUR | 876 … 9.821 EUR |
| teuer (14,4 min) | 49 … 1.012 EUR | 0,09 … 1,82 EUR | 0,14 … 2,92 EUR | 876 … 18.209 EUR |

![Preiskorridor je Kundentyp](docs/korridor.svg)

Intercom Fin (0,99 USD je Outcome, geprüft auf intercom.com) liegt beim mittleren Kunden bei 52 % unseres Korridors je gelöstem Ticket. Entschieden: **450 EUR je Monat + 0,75 EUR je gelöstem Ticket** (ohne Übergabe, nicht innerhalb von 7 Tagen wieder geöffnet). Das ergibt beim mittleren Kunden 85,8 % Marge, der Kunde behält 73,9 % seiner Ersparnis. Verlust erst unter 3,7 % Lösungsquote ([docs/decisions.md](docs/decisions.md)). Bei Abrechnung pro Sitz kostet ein Stellenabbau von 30 % im zweiten Jahr den Anbieter 30 % des Umsatzes, obwohl die Ticketmenge gleich bleibt.

## Kosten & Latenz
- Kosten pro 1000 Requests: 1.601,85 EUR je 1.000 Tickets mit Agent (Szenario mittel, inklusive Personal), davon Tokens 32,09 USD
- p95-Latenz: entfällt für eine Entscheidungsvorlage. Agent-Latenz siehe UC7 (p95 39,7 s)
- Qualitätsmetrik: Kipppunkt der Übergabequote 66 % im pessimistischen Szenario, gemessen im Goldset 22 %
- Kosten UC8 bisher: 0 USD (keine API-Aufrufe)

## Learnings
Folgt.

## Was ich anders machen würde
Folgt.
