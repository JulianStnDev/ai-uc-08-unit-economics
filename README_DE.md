🇬🇧 [English version](README.md)

# UC8: Unit Economics, Pricing & Build-vs-Buy

> Stand 2026-10-08: Zahleninventur fertig ([docs/INVENTUR.md](docs/INVENTUR.md)), Modellrechnung noch offen.

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

Die größten Lücken: Minuten je Freigabe und je Übergabe, Minuten je Ticket ohne Agent und die echte Mischung der Tickets.

## Kosten & Latenz
- Kosten pro 1000 Requests: offen (folgt aus der Modellrechnung)
- p95-Latenz: entfällt für eine Entscheidungsvorlage. Agent-Latenz siehe UC7 (p95 39,7 s)
- Qualitätsmetrik: offen
- Kosten UC8 bisher: 0 USD (keine API-Aufrufe)

## Learnings
Folgt.

## Was ich anders machen würde
Folgt.
