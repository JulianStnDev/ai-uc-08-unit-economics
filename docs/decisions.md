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

## 2026-10-08: Übergabe-Minuten gekoppelt, Nacharbeit als Folgekosten

Kontext: Im ersten Modell waren die Minuten je Übergabe ein eigener Wert (6 / 8 / 10). Damit konnte eine Übergabe billiger sein als das Ticket ohne Agent, und die Sensitivität auf die Minuten ohne Agent war verzerrt. Autonome Tickets kosteten 0 Minuten.

Entscheidung:
- Minuten je Übergabe = Minuten ohne Agent × Faktor (1,0 / 1,1 / 1,3). Eine Übergabe kostet nie weniger als das Ticket ohne Agent.
- Neuer Parameter `anteil_nacharbeit` (5 / 10 / 20 % der autonomen Tickets), je Fall die vollen Minuten ohne Agent.

Begründung: Goldset-Anker für die Nacharbeit ist der Anteil autonomer Läufe mit falscher Kernaussage. Beim deployten Stand (UC6) sind das 4 von 29 (14 %, 95-%-Intervall 5–31 %), bei UC4 v3 1 von 24 (4 %). „Mittel“ (10 %) liegt damit unter dem gemessenen Wert des deployten Agents, weil 3 der 4 Fehler auf T04 fallen. Details und zwei Beispiele: [docs/NACHARBEIT.md](NACHARBEIT.md).

Folge: Ersparnis im Szenario mittel sinkt von 65,4 % auf 56,9 %. Der Kipppunkt im mittleren Szenario liegt jetzt bei 86,9 %, knapp über der möglichen Grenze von 85 %. Pessimistisch fällt er von 71 % auf 66 %.

## 2026-10-08: Option „Doppelbuchung automatisch bis X EUR, darüber Freigabe“

Kontext: Eine automatische Erstattung spart je Fall die Freigabe (2 min × 0,4420 EUR + Haiku-Antwort = 0,89 EUR). Dagegen steht der erwartete Verlust: Fehlerquote × Betrag. Die Gewinnschwelle ist gespart / Betrag. Nach der Dreierregel braucht man 3 / Schwelle fehlerfreie Fälle, um zu zeigen, dass die Fehlerquote darunter liegt.

| Grenze X | Schwelle | fehlerfreie Fälle nötig (1 / 2 / 4 min je Freigabe) |
|---|---|---|
| bis 5 EUR | 17,8 % | 34 / **17** / 9 |
| bis 10 EUR | 8,9 % | 68 / **34** / 17 |
| bis 20 EUR | 4,4 % | 135 / **68** / 34 |
| bis 59 EUR | 1,5 % | 397 / **200** / 100 |

Bisher belegt: 6 Doppelbuchungs-Läufe ohne falsche Erstattung (UC6 T01, T02). Das zeigt nur eine Fehlerquote < 50 %.

Option (vorgeschlagen, nicht entschieden): **automatisch bis 10 EUR, darüber Freigabe.**
- 10 EUR deckt das Monatsabo (6,99) ab, also den häufigsten kleinen Fall. Jahresabos (59) bleiben bei der Freigabe.
- 34 fehlerfreie Fälle sind im Schattenbetrieb erreichbar: Der Agent entscheidet mit, der Mensch gibt weiter frei, verglichen wird hinterher. Das Muster gibt es schon aus UC4 (Schattenmodus für Erstattungen).
- Bei 59 EUR bräuchte es 200 fehlerfreie Fälle, und der Gewinn je Fall wäre trotzdem klein (bei 1 % Fehlerquote 0,30 EUR).
- Voraussetzungen: Die Erstattungsregel bleibt im Werkzeug (UC6, nicht im Prompt). Je Kunde gibt es eine Obergrenze, damit sich die Option nicht wiederholt ausnutzen lässt. Der Schutz gegen Social Engineering aus UC6 („telefonisch abgesprochen“) muss in den 34 Fällen mitgetestet sein.
- Grenzen der Rechnung: Die Dreierregel setzt unabhängige, repräsentative Fälle voraus. Folgeschäden einer falschen Erstattung (Missbrauch, Nachahmer) sind nicht eingerechnet.

## 2026-10-08: Nacharbeit „mittel“ = gemessene 14 %

Kontext: „Mittel“ stand bei 10 % und damit unter dem gemessenen Wert des deployten Agents (4 von 29 autonomen Läufen mit falscher Kernaussage, 95-%-Intervall 5–31 %).

Entscheidung (Julian): „Mittel“ = 14 %, Spanne 5 / 14 / 20 %.

Begründung: 3 der 4 Fehler sind T04. Der Agent rechnet dort die 14-Tage-Frist falsch, in allen drei Läufen und auch mit altem Code. Das ist ein systematischer Fehler und kein Ausreißer, er darf nicht herausgerechnet werden. Folge im Szenario mittel (10.000 Tickets): Ersparnis 19.342 EUR statt 20.119 EUR im Monat (54,7 % statt 56,9 %). Der Kipppunkt bleibt knapp außerhalb des möglichen Bereichs (87,0 % gegen höchstens 85 %).

## 2026-10-08: Offene Option „Frist im Werkzeug berechnen und dem Agent fertig liefern (Regel im Code)“

Kontext: T04 („59 $ abgebucht, vergessen zu kündigen“) scheitert systematisch: Der Agent rechnet die 14-Tage-Frist ab Beginn des neuen Jahreszeitraums selbst aus und kommt falsch auf „abgelaufen“. Die Erstattungsregeln liegen seit UC6 schon im Werkzeug, die Frist aber nicht. Der Agent bekommt Rohdaten (Datum der Verlängerung) und muss selbst rechnen.

Option: Das Werkzeug liefert zu jeder Zahlung das fertige Ergebnis, zum Beispiel `frist_14_tage_offen: true, endet_am: 2026-09-29`. Der Agent rechnet nicht mehr selbst. Das ist dasselbe Muster wie in UC4 und UC6: Was immer gelten muss, gehört in den Code.

Abschätzung (nur gerechnet, UC7 nicht geändert; [evals/modell.md](../evals/modell.md), Abschnitt „Reparatur-Kandidat T04“), Szenario mittel, 10.000 Tickets im Monat:

| Variante | Nacharbeit | Freigabe | Monat mit Agent | gespart gegenüber heute |
|---|---|---|---|---|
| heute | 14 % | 15 % | 16.018 EUR | – |
| nur Nacharbeit sinkt | 3,9 % (1 von 26) | 15 % | 14.044 EUR | 1.974 EUR/Monat |
| Nacharbeit sinkt, T04 wird Freigabe | 3,9 % | 20,7 % | 14.472 EUR | **1.546 EUR/Monat** |

Die realistische Zahl ist die dritte Zeile. Repariert bekommt die Kundin eine Empfehlung, und die kostet eine Freigabe (2 min). Die berechtigten Erstattungen selbst sind nicht eingerechnet, ein Mensch ohne Agent würde sie ebenso auszahlen.

Grenzen: Die Basis sind 29 autonome Läufe, davon 3 T04. Wie häufig T04-artige Fälle im echten Mix sind (Verlängerung vergessen, noch in der Frist), ist offen. 1.546 EUR sind eine Größenordnung, keine Prognose. Nachweis nach der Reparatur: T04 dreimal im Goldset, dazu ein deterministischer Test für die Fristberechnung (Grenzfälle Tag 14 und 15).

Status: offen, nicht umgesetzt.
