🇬🇧 [English version](README.md)

# UC8: Unit Economics, Pricing & Build-vs-Buy

> Entscheidungsvorlage, kein Produktcode. Alle Zahlen kommen aus gemessenen Läufen (UC4, UC6, UC7) und einer Annahmen-Tabelle mit Quellen ([data/annahmen.csv](data/annahmen.csv)). Kosten: 0 USD, keine API-Aufrufe.

## Problem
FocusFlow hat einen funktionierenden Support-Agent als Prototyp (UC7). Offen sind drei Fragen: Was kostet ein Ticket mit Agent im Vergleich zu einem Ticket, das ein Mensch allein bearbeitet? Wie viel könnte man dafür verlangen, wenn man den Agent verkauft? Und sollte FocusFlow ihn selbst betreiben oder einkaufen?

## Drei Schritte

**1. Kosten: Tokens machen 2 % der Kosten je Ticket aus – Übergaben tragen den Business Case.**
Mit Agent kostet ein Ticket 1,60 EUR statt 3,54 EUR (Mensch allein, 8 min). Davon sind Tokens 0,03 EUR. 73 % sind Übergaben an Menschen. Ob sich der Agent lohnt, entscheidet die Übergabequote, nicht der Modellpreis. Im Goldset liegt sie bei 22 %. Teurer als ein Mensch allein wird der Agent erst im pessimistischen Szenario, und auch dort erst ab 66 % Übergaben.

![Ersparnis je Ticket über der Übergabequote](docs/kipppunkt.svg)

**2. Preis: 450 EUR im Monat + 0,75 EUR je gelöstem Ticket.**
„Gelöst“ heißt: ohne Übergabe und nicht innerhalb von 7 Tagen wieder geöffnet. Bei 10.000 Tickets im Monat ergibt das 85,8 % Marge. Der mittlere Kunde behält 73,9 % seiner Ersparnis. Der Preis liegt unter Fin (0,89 EUR je Outcome). Abrechnung pro Sitz ist verworfen: Baut der Kunde 30 % der Stellen ab, verliert der Anbieter 30 % Umsatz.

![Preiskorridor je Kundentyp](docs/korridor.svg)

**3. Build vs. Buy: Selbst betreiben lohnt sich ab ~5.000 Tickets im Monat – getragen von einer Annahme ohne Quelle.**
Selbst betreiben ist günstiger als unser Produkt ab 5.085 Tickets im Monat und günstiger als Fin ab 3.456. Bisherige Baukosten sind versunken und nicht eingerechnet. Der Kipppunkt hängt am laufenden Pflegeaufwand, einer Annahme ohne Quelle: Bei 21 h im Monat liegt er bei 1.875 Tickets, bei 100 h bei 12.440.

![Selbst betreiben gegen Kaufen](docs/build_buy_differenz.svg)

## Entscheidung
**FocusFlow betreibt den Agent selbst (A).** Gezählt werden nur künftige Kosten. Bei 10.000 Tickets kostet A im Monat 18.846 EUR, unser Produkt 20.996 EUR, Fin 23.578 EUR. Die Daten bleiben unter eigener Kontrolle: Sie gehen an den Modellanbieter und den eigenen Hoster (Frankfurt), nicht zusätzlich an einen SaaS-Anbieter.

**Neu entscheiden, wenn** die Vollkosten von A drei Monate in Folge über dem Angebot von C liegen oder der Pflegeaufwand dauerhaft über 45 h im Monat liegt. Dafür wird jeden Monat gemessen: Manntage je Pflegeaufgabe, Tagessatz, Betriebskosten und Tokens ([docs/decisions.md](docs/decisions.md)).

## Annahmen, die das Ergebnis tragen

| Annahme | Spanne | Wirkung | Quelle |
|---|---|---|---|
| Minuten je Ticket ohne Agent | 5 / 8 / 14,4 min | Ersparnis 1,15 bis 3,61 EUR je Ticket | Branchenwerte, teils aus Sekundärquellen |
| Personalkosten je Minute | 0,37 / 0,44 / 0,75 EUR | Ersparnis 1,61 bis 3,30 EUR je Ticket | Entgeltatlas, Destatis (im Original zu prüfen) |
| Übergabequote | 15 / 30 / 50 % | Ersparnis 2,44 bis 1,26 EUR je Ticket | Goldset 22 %, aber nur Abo- und Geld-Tickets |
| Pflegeaufwand für A | 21 / 45 / 100 h je Monat | Kipppunkt Build vs. Buy 1.875 bis 12.440 Tickets | keine, eigene Annahme |

![Tornado: Sensitivität der Ersparnis je Ticket](docs/tornado.svg)

## Kosten & Latenz
- Kosten pro 1000 Requests: 1.601,85 EUR je 1.000 Tickets mit Agent (Szenario mittel, inklusive Personal), davon Tokens 32,09 USD
- p95-Latenz: 39,7 s je Agent-Lauf (UC7, Cloud Run)
- Qualitätsmetrik: 4 von 29 autonomen Goldset-Läufen mit falscher Kernaussage (14 %), als Nacharbeit eingerechnet

## Was ich anders machen würde
- **Die großen Hebel zuerst messen.** Die drei stärksten Annahmen (Minuten ohne Agent, Personalkosten, Pflegeaufwand) sind nicht gemessen. 20 Freigaben und Übergaben mit der Stoppuhr und eine Zeiterfassung in UC4 bis UC7 hätten mehr gebracht als jede weitere Nachkommastelle bei den Tokens.
- **Echte Ticketmischung früher besorgen.** Das Goldset besteht nur aus Abo- und Geld-Tickets, die Übergabequote im echten Eingang ist unbekannt.
- **Versunkene Kosten von Anfang an weglassen.** Die erste Fassung rechnete die bisherige Bauzeit ein (312 EUR/Monat).
- **Begriffe vorher festlegen.** Aufschlag (Gewinn / Kosten) und Marge (Gewinn / Umsatz) waren zunächst vermischt.

Details: [Inventur](docs/INVENTUR.md) · [Kostenmodell](evals/modell.md) · [Pricing](evals/pricing.md) · [Build vs. Buy](evals/build_buy.md) · Rechenwege [Kosten](docs/RECHENWEG.md), [Preis](docs/RECHENWEG_PRICING.md), [Build vs. Buy](docs/RECHENWEG_BUILD_BUY.md) · [Nacharbeit](docs/NACHARBEIT.md) · [Entscheidungen](docs/decisions.md)
