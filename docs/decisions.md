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
