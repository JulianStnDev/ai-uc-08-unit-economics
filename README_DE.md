🇬🇧 [English version](README.md)

# UC8: Unit Economics, Pricing & Build-vs-Buy

> Stand 2026-10-08: Zahleninventur ([docs/INVENTUR.md](docs/INVENTUR.md)) und Kostenmodell ([evals/modell.md](evals/modell.md), Rechenweg: [docs/RECHENWEG.md](docs/RECHENWEG.md)). Pricing und Build-vs-Buy folgen.

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

| Szenario | Freigabe / Übergabe (Faktor Minuten, Nacharbeit 5 / 10 / 20 %) | mit Agent je Ticket | Ersparnis im Monat | Kipppunkt Übergabequote |
|---|---|---|---|---|
| optimistisch | 10 % / 15 % | 0,74 EUR | 27.989 EUR (79,2 %) | keiner |
| mittel | 15 % / 30 % | 1,52 EUR | 20.119 EUR (56,9 %) | keiner (87 % > 85 % möglich) |
| pessimistisch | 20 % / 50 % | 2,89 EUR | 6.415 EUR (18,1 %) | 66 % |

![Ersparnis je Ticket über der Übergabequote](docs/kipppunkt.svg)

Minuten je Übergabe = Minuten ohne Agent × 1,0 / 1,1 / 1,3. Nacharbeit: Anteil autonomer Tickets, die doch ein Mensch nacharbeitet, begründet in [docs/NACHARBEIT.md](docs/NACHARBEIT.md) (deployter Agent im Goldset: 4 von 29 autonomen Läufen mit falscher Kernaussage).

Tokens kosten je Ticket 0,03 EUR, so viel wie 4 Sekunden Arbeitszeit. Am stärksten bewegen die Ersparnis die Minuten ohne Agent, die Personalkosten und die Übergabequote:

![Tornado: Sensitivität der Ersparnis je Ticket](docs/tornado.svg)

## Kosten & Latenz
- Kosten pro 1000 Requests: 1.524,05 EUR je 1.000 Tickets mit Agent (Szenario mittel, inklusive Personal), davon Tokens 32,09 USD
- p95-Latenz: entfällt für eine Entscheidungsvorlage. Agent-Latenz siehe UC7 (p95 39,7 s)
- Qualitätsmetrik: Kipppunkt der Übergabequote 66 % im pessimistischen Szenario, gemessen im Goldset 22 %
- Kosten UC8 bisher: 0 USD (keine API-Aufrufe)

## Learnings
Folgt.

## Was ich anders machen würde
Folgt.
