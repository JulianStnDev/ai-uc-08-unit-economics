# Entscheidungen

<!-- Format:
## YYYY-MM-DD: Kurztitel
Kontext, Optionen, Entscheidung, Begründung
-->

## 2026-09-18: Status-Vokabular für meta.json

Kontext: meta.json legt "status": "planned" fest, ohne definierte erlaubte Werte —
das driftet über mehrere Repos auseinander (planned/in-progress/wip/...).

Optionen: (a) einfach: planned → active → done, (b) zusätzlich mit
parked/abandoned für verworfene Use Cases, (c) feiner: research →
building → evaluating → shipped.

Entscheidung: (a) — planned, active, done. Zusätzlich in CLAUDE.md verankert.

Begründung: Bei einem Solo-Portfolio mit meist einem aktiven Repo lohnt sich
keine feinere Staffelung. CLAUDE.md-Verankerung, damit der Agent das Vokabular
bei jedem neuen Repo automatisch mitliest statt dass ich mich erinnern muss.

## 2026-10-08: UC8 als Entscheidungsvorlage, erst Inventur, dann Modell

Kontext: Leitfrage ist, was ein Support-Ticket mit dem UC7-Agent im Vergleich zu einem rein menschlich bearbeiteten Ticket kostet. Dafür gibt es Zahlen aus drei Repos und dem Betrieb, aber verstreut und mit unterschiedlichen Ständen.

Optionen: (a) direkt eine Modellrechnung mit Annahmen, (b) erst jede Zahl mit Quelle inventarisieren und die Lücken benennen, dann rechnen.

Entscheidung: (b). Kein Produktcode, keine API-Aufrufe. Die Inventur erzeugt ein Skript (`scripts/inventur.py`), damit jede Zahl neu berechnet werden kann.

Begründung: Eine Modellrechnung ist nur so gut wie ihre schwächste Annahme. Erst die Inventur zeigt, welche Zahlen gemessen und welche geschätzt sind.

## 2026-10-08: Messregeln der Inventur

- **Zwei Goldset-Quellen:** UC4 v3 und UC6 „nachher“. Der deployte Agent (Revision `uc7-00009`) enthält den Schutz aus UC6. Maßgeblich ist daher UC6, UC4 v3 bleibt als Vergleich.
- **Goldset und Live getrennt:** Live heißt echte Infrastruktur, aber Testläufe des Betreibers. Die Zahlen werden nie gemischt.
- **p95 als Nearest-Rank:** Bei n < 20 ist p95 der größte Wert, wie in UC7.
- **„Ohne Menschen“** = weder Erstattungsempfehlung noch Übergabe. Kündigungen zählen dazu, weil der Agent sie selbst ausführt.
- **Haiku- und Judge-Kosten je Aufruf, nicht je Ticket:** Das Umlegen auf ein Ticket braucht Anteile und Stichprobengröße und gehört in die Modellrechnung.
- **Nur lesend:** Neon per Read-only-Transaktion, Cloud Run über die Monitoring-API. Rechnungsbeträge sind über die CLI nicht erreichbar und bleiben als Lücke markiert.

## 2026-10-08: Regeln des Kostenmodells

Kontext: Kostenmodell ohne Pricing und ohne Build-vs-Buy, Eingaben in `data/annahmen.csv`, Rechnung in `scripts/modell.py`.

- **Mittelwerte statt Mediane für Tokens:** Für Summen über viele Tickets zählt der Erwartungswert. Mediane und p95 bleiben in der Inventur.
- **Deckel aus dem Demo-Betrieb aufgehoben:** Judge-Deckel (0,50 USD/Monat) und API-Monatsdeckel (4,50 USD) würden bei 10.000 Tickets den Judge bzw. den Dienst abschalten. Das Modell rechnet mit dem Judge auf 20 % aller Tickets.
- **Hosting ist nicht nur fix:** Der feste Block (2,67 EUR/Monat laut Abrechnung) deckt den Demo-Betrieb. Bei 1.000 und mehr Tickets kommt Rechenzeit je Lauf dazu (1 Lauf je Instanz, 1 vCPU / 1 GiB, Tier-2-Preis). Sie steht als eigene variable Zeile „Hosting variabel“ neben den Tokens. Das Freikontingent ist dabei nicht abgezogen, das rechnet also vorsichtig.
- **Szenarien variieren nur Anteile und Minuten je Eingriff.** Minuten ohne Agent (8) und Personalkosten (0,4420 EUR/min) stehen auf „mittel“. Wie stark der Kipppunkt von den Minuten ohne Agent abhängt, zeigt eine eigene Tabelle (5 / 8 / 14,4 min).
- **Tickets ohne Menschen kosten 0 Minuten.** Folgekosten falscher Antworten (Nachfragen, Wiedereröffnung, Kulanz, Kündigung) sind nicht modelliert. Das ist die größte optimistische Verzerrung des Modells und der nächste Kandidat für eine Annahme mit Quelle.
- **Neon-Speicher bei Volumen nicht modelliert:** Etwa 5,7 KB je Lauf ergeben bei 100.000 Tickets rund 0,57 GB im Monat. Das sprengt den Free-Plan nach dem ersten Monat. Der Preis eines bezahlten Neon-Tarifs ist nicht recherchiert, die Speichermenge ist aber klein.
- **Doppelbuchung automatisch erstatten:** Beträge in EUR laut Vorgabe (6,99 / 59 EUR), obwohl das Goldset in USD rechnet.
