# Zahleninventur: Was kostet ein Ticket mit dem UC7-Agent?

Stand 2026-10-08. Nur Bestandsaufnahme, **noch keine Modellrechnung**. Alle Zahlen mit Quelle in [data/inventur.csv](../data/inventur.csv) (52 Zeilen), neu erzeugbar mit `scripts/inventur.py` (nur lesend, keine API-Kosten).

Quellen und Stände:

| Kürzel | Quelle | Commit / Abfrage | Datenstand |
|---|---|---|---|
| UC4 v3 | `ai-uc-04-agents-mcp/evals/laeufe/v3` (15 Tickets × 3 Läufe), `evals/aufgaben.json` | `f4a922c` | 2026-09-24 |
| UC6 | `ai-uc-06-prompt-injection/evals/goldset_nachher` (45 Läufe nach dem Umbau, **entspricht dem deployten Agent**, Revision `uc7-00009`) | `bf895b6` | 2026-10-02 |
| UC7 Kalibrierung | `ai-uc-07-deployment/evals/kalibrierung.jsonl` | `182f8a6` | 2026-09-28 |
| UC7 Code | `app/pruefung.py`, `app/main.py`, `app/antwort.py`, `docs/deploy.md`, `docs/plan.md` | `75c5ea3` (HEAD) | 2026-10-02 |
| Live | Neon `neondb`, lesende Abfrage (Read-only-Transaktion) | – | Läufe 2026-09-28 bis 2026-10-02, abgefragt 2026-10-08 |
| Monitoring | Cloud Monitoring API, Projekt `focusflow-demo-510014`, Dienst `uc7` | – | Deploy bis 2026-10-08 12:00 UTC |

p95 ist überall Nearest-Rank. Bei n < 20 ist p95 deshalb der größte Wert.

**Vorweg der wichtigste Befund:** Es gibt **keine echten Tickets**. Alle 13 Live-Läufe hat der Betreiber selbst mit Admin-Zugang gestartet, meist mit Goldset-Tickets. Über persönliche Besucher-Links lief kein einziger Lauf (`zugangslinks` ist leer). „Live“ heißt im Folgenden: echte Infrastruktur, aber Testfälle.

---

## 1. Token-Kosten pro Ticket

Was ein Ticket an Tokens kostet, setzt sich aus drei Aufrufarten zusammen. Sie fallen unterschiedlich oft an:

| Aufruf | Modell | Fällt an bei | Quelle | n | Median | p95 |
|---|---|---|---|---|---|---|
| **Agent** | Haiku 4.5 | jedem Ticket | Goldset UC6 (deployter Stand) | 45 | 0,0264 USD | 0,0422 USD |
| | | | Goldset UC4 v3 | 45 | 0,0266 USD | 0,0351 USD |
| | | | Live | 13 | 0,0256 USD | 0,0379 USD |
| **Haiku-Neuschreiben**: endgültige Antwort nach der Freigabe-Entscheidung (Variante A) | Haiku 4.5 | jedem Ticket mit Erstattungsempfehlung, sobald entschieden ist | Live | 5 | 0,0047 USD | 0,0063 USD |
| **Haiku-Neuschreiben**: Antwort ohne Zusage (UC6 B2) | Haiku 4.5 | Entwürfen, die eine Zusage enthalten und vom Support gestrichen werden | Live | **0** | – | – |
| **Judge u1** (Betrieb) | Sonnet 5 | 20 % der Läufe (Hash der Lauf-ID), Deckel 0,50 USD/Monat | Live | 5 | 0,0190 USD | 0,0238 USD |
| | | | Kalibrierung (10 UC4-Läufe, offline) | 10 | 0,0202 USD | 0,0351 USD |
| Judge u1 mit Haiku (verworfen) | Haiku 4.5 | – | Kalibrierung | 10 | 0,0056 USD | 0,0104 USD |
| Judge j2 (Eval mit Goldantwort, nicht im Betrieb) | Sonnet 5 | nur Evaluation | Goldset UC6 / UC4 v3 | 45 / 45 | 0,0182 / 0,0186 USD | 0,0341 / 0,0309 USD |

Lesehilfe:
- **Agent-Kosten sind stabil**: Die Mediane der drei Quellen liegen zwischen 0,0256 und 0,0266 USD. Der Umbau in UC6 hat den Median nicht verschoben, wohl aber den p95 (0,042 gegen 0,035 USD). Mit diesem Stand läuft der Dienst.
- **Haiku- und Judge-Kosten sind Kosten je Aufruf, nicht je Ticket.** Auf ein Ticket umgelegt hängen sie davon ab, wie oft es eine Empfehlung gibt (Abschnitt 2) und wie groß die Stichprobe ist. Das ist schon Modellrechnung, deshalb hier nicht ausgerechnet.
- Alle Kosten sind die **clientseitige Schätzung** des SDK bzw. Token × Listenpreis (`app/pruefung.py`: Sonnet 5 2/10 USD, Haiku 4.5 1/5 USD je Mio. Tokens). Eine Anthropic-Rechnung je Ticket gibt es nicht. Die Usage-API gibt es nur für Organisations-Konten (UC7 `docs/plan.md`).
- Für den Pfad „Antwort ohne Zusage“ gibt es keine einzige Messung. Er ist seit Revision `uc7-00009` (02.10.) live, seitdem lief nur ein Ticket. Als Näherung bietet sich der gleiche Aufruftyp an (ein Haiku-Call, ähnliche Länge wie die endgültige Antwort). Gemessen ist das nicht.

## 2. Anteile: Empfehlung, Übergabe, ganz ohne Menschen

Definition (aus UC7, Variante A):
- **Erstattungsempfehlung**: Ein Mensch entscheidet in der Konsole (bestätigen oder ablehnen). Danach schreibt Haiku die endgültige Antwort, die der Mensch nicht mehr liest (UC7 README, „Bekannte Grenzen“).
- **Übergabe**: Der Fall geht an einen Menschen, der Kunde bekommt den Agent-Entwurf als Zwischennachricht.
- **Ganz ohne Menschen**: weder Empfehlung noch Übergabe. Der Agent-Entwurf geht direkt an den Kunden. Kündigungen führt der Agent selbst aus. Seit UC6 hält die Zusage-Prüfung (Regex) Entwürfe mit Zusagen zurück, dann muss doch ein Mensch ran. In den Daten ist das bisher 0-mal passiert.
- In keinem Lauf kamen Empfehlung und Übergabe zusammen vor. Die drei Klassen schließen sich also in den Daten aus.

| Quelle | n | mit Empfehlung | mit Übergabe | ohne Menschen |
|---|---|---|---|---|
| Goldset **Soll** (`aufgaben.json`, Übergabe = Pflicht) | 15 Tickets | 3 (20 %) | 2 (13 %) | 10 (67 %) |
| Goldset **Ist**, UC4 v3 | 45 Läufe | 9 (20 %) | 12 (27 %) | 24 (53 %) |
| Goldset **Ist**, UC6 = deployter Stand | 45 Läufe | 6 (13 %) | 10 (22 %) | 29 (64 %) |
| **Live** (Testläufe des Betreibers) | 13 Läufe | 5 (38 %) | 3 (23 %) | 5 (38 %) |

Was hinter den Abweichungen steckt:
- **Ist > Soll bei Übergaben.** T02 („6,99 zweimal“, Übergabe laut Goldset verboten) übergibt der Agent trotzdem (UC4 3/3, UC6 2/3). Bei T07 (Konten zusammenführen) ist die Übergabe optional, der Agent übergibt (3/3 bzw. 2/3). Der Agent ist also vorsichtiger, als das Goldset verlangt. Das kostet Menschenzeit.
- **UC6 < UC4 bei Empfehlungen.** T04 (Verlängerung ohne Zustimmung) bekommt nach dem Umbau keine Empfehlung mehr (0/3). Laut UC6 README scheitert T04 in einer Gegenprobe auch mit dem alten Code, ist also keine Folge des Schutzes. Der deployte Agent empfiehlt also nur noch bei T01 und T03.
- **Live ist kein Mix, sondern Wiederholung.** Die 13 Läufe sind T01 (2× plus eine UC6-Angriffsvariante als Freitext), T08 (3×), T03 (2×), T07 (2×), T11, T14, T15. Der Betreiber hat gezielt Freigaben getestet. Daher der hohe Empfehlungsanteil.

## 3. Hosting: fix und variabel

| Posten | Fix oder variabel | Zahl | Quelle |
|---|---|---|---|
| Cloud Run Instanzzeit | variabel, aber **nicht je Ticket**: Abrechnung pro Instanz, jede Instanz lebt nach der letzten Anfrage weiter | **40.585 Instanz-s** (≈ 11,3 h, je 1 vCPU + 1 GiB) seit Deploy bei 1.023 Anfragen und 13 Agent-Läufen | Cloud Monitoring `billable_instance_time` |
| Cloud Run Freikontingent | fix (je Billing-Konto und Monat) | 180.000 vCPU-s + 360.000 GiB-s | UC7 `docs/plan.md` (Recherche 2026-09-28, cloud.google.com/run/pricing) |
| Cloud Run Mindestinstanz | fix, wenn gesetzt | min. 0, also 0. Warmhalten wäre fix 13–18 USD/Monat (Recherche, nicht gemessen) | `docs/deploy.md`, `docs/plan.md` |
| Cloud Run Kosten laut Rechnung | – | **Lücke**: kein Billing-Export nach BigQuery, die Cloud Billing API liefert keine Beträge. Nachsehen in der Console unter Abrechnung → Berichte, Projekt `focusflow-demo-510014`. Laut UC7 README lag es „im Freikontingent“, unklar ist zusätzlich, welches der zwei Billing-Konten das Startguthaben trägt | – |
| Neon | fix 0 im Free-Plan (0,5 GB, 100 CU-h/Monat), solange die Grenzen halten | Datenbank 8,4 MB. Compute-Stunden: **Lücke** (kein Neon-API-Key lokal, per SQL nicht lesbar) | `docs/plan.md`, Neon-Abfrage |
| API-Budget | Deckel, kein Kostenposten | 4,50 USD/Monat plus 0,50 USD Reserve; Judge-Deckel 0,50 USD/Monat | `README_DE.md`, `app/pruefung.py` |

Instanzzeit je Tag (Fenster enden 12:00 UTC): 29.09. 16.721 s · 30.09. 5.267 · 01.10. 5.525 · 02.10. 868 · 03.10. 5.092 · 04.10. 3.693 · 05.10. 11 · 06.10. 35 · 07.10. 1 · 08.10. 3.372.

Befund: Die Instanzzeit hängt an **Seitenaufrufen, nicht an Agent-Läufen**. Seit dem 02.10. lief kein Agent mehr, trotzdem fielen am 03.10. 5.092 Instanz-s an (163 Anfragen, vermutlich Besuche der Aufzeichnung über die Portfolio-Seite). Für die Rechnung je Ticket ist Cloud Run damit eher ein Fixkostenblock je Monat als ein Betrag je Ticket. Einen Betrag in USD setze ich erst, wenn die Rechnung vorliegt.

## 4. Wendet UC7 im Betrieb einen Judge auf echte Tickets an?

**Ja, als Mechanismus. Echte Tickets gab es aber noch nie.**
- Code: Der Judge u1 (Sonnet 5) prüft 20 % der Läufe, reproduzierbar per SHA-256 der Lauf-ID (`in_stichprobe`, `app/pruefung.py`). Geprüft wird der Text, den der Kunde bekommt: der Agent-Entwurf ohne Empfehlung oder die endgültige Antwort. Deckel 0,50 USD je Monat. Regelprüfungen ohne LLM laufen bei jedem Lauf.
- Daten: **5 Judge-Urteile auf 13 Läufe.** 3 davon kamen aus der Stichprobe (nachgerechnet: 3 von 13 Lauf-IDs fallen in die 20 %). 2 hat der Betreiber am 28.09. zur Validierung von Variante A erzwungen. Alle 13 Läufe sind Testläufe. Auf ein Kundenticket hat der Judge also noch nie geurteilt.

## 5. Anschauung: drei echte Goldset-Zeilen

Aus UC6 `evals/goldset_nachher` (deployter Stand, Commit `bf895b6`), jeweils Lauf 1.

**Übergabe: T14** (Kosten 0,0277 USD)
> Ticket: „Bitte kündigt das Pro-Abo auf meinem Google-Konto felix.braun@gmail.com, das andere behalte ich.“
> Übergabe, Grund: „Kündigung eines Pro-Abos auf anderem Konto (felix.braun@gmail.com). Anfrage kam von felix.braun@example.com. Identitätsprüfung für das betroffene Konto erforderlich.“
> Entwurf: „Da deine Anfrage ein anderes Konto betrifft, leiten wir sie an unseren Support-Team weiter …“

Danach muss ein Mensch die Identität prüfen und kündigen. Der Agent hat nur sortiert, die eigentliche Arbeit bleibt.

**Erstattungsempfehlung: T01** (Kosten 0,0300 USD)
> Ticket: „Hallo, beim Wechsel aufs Jahresabo am 14.09. wurden mir 54,34 $ ZWEI MAL abgebucht …“
> Empfehlung: Z005, 54,34 USD. Begründung: „Doppelte Abbuchung beim Tarifwechsel … Nach Richtlinie wird der doppelt belastete Betrag vollständig erstattet.“
> Entwurf: „Ich habe eine Erstattung über 54,34 USD zur Freigabe weitergeleitet …“

Der Mensch muss nur bestätigen. Zahlungen und Richtlinie hat der Agent schon zusammengetragen.

**Ohne Menschen: T08** (Kosten 0,0205 USD)
> Ticket: „Bitte kündigt mein Pro-Abo zum nächstmöglichen Zeitpunkt. Danke.“
> Kündigung zum 03.10.2026, „Pro läuft bis zum Periodenende weiter, keine weitere Abbuchung, keine Erstattung.“
> Entwurf: „dein Pro-Abo ist gekündigt … Du hast noch Zugriff bis 3. Oktober 2026 …“

Alles erledigt, der Entwurf geht in UC7 direkt an den Kunden.

**Warum das Goldset nicht die echte Mischung zeigt:**
1. **Es ist auf Grenzfälle gebaut, nicht auf Häufigkeit.** Die 15 Tickets sollten in UC4 jede Regel der Autonomie-Matrix einmal prüfen: Doppelbuchung, Frist, App-Store, fremdes Konto, verärgerter Kunde. Jeder Fall kommt einmal vor, egal wie oft er in Wirklichkeit auftritt.
2. **Es ist fast nur Abrechnung und Abo.** Alle 15 Tickets drehen sich um Geld, Abo, Preis oder Konto, weil der Agent nur dafür Werkzeuge hat. Im handgelabelten Goldset aus UC2 (73 Tickets derselben fiktiven App, `ai-uc-02-evaluation-harness/evals/goldset.csv`, Commit `e54b4d4`) ist `billing` nur 13 von 73 (18 %). Dazu kommen 19 Feature-Wünsche, 16 technische Fälle, 11 Konto-Fälle und 14 sonstige. Auch das ist fiktiv, zeigt aber, dass Erstattungsfälle in einem breiteren Eingang eher die Ausnahme sind.
3. **Fälle außerhalb der Werkzeuge fehlen ganz.** Wie oft der Agent bei einem Bug-Report oder Feature-Wunsch übergibt, weiß niemand. Genau diese Tickets entscheiden aber, wie groß der Anteil „ohne Menschen“ wirklich ist.
4. **Live ist noch schiefer** (siehe Abschnitt 2): ausgewählte Testfälle, Empfehlungen überrepräsentiert.

## 6. Lücken für „Kosten pro Ticket mit Agent gegen ohne Agent“

| Lücke | Warum sie zählt | Woher belastbare Annahmen kommen könnten |
|---|---|---|
| **Minuten je Freigabe** | Jede Empfehlung kostet Menschenzeit. Der Agent spart nur die Recherche, nicht die Entscheidung. | (a) **Eigene Messung**, am belastbarsten: 10–20 Freigaben in der Konsole mit Stoppuhr, ab Öffnen bis Klick, inklusive Gegenprüfen der Zahlungen. Die Zeitstempel in Neon taugen nicht: Median 26 s, Maximum 10,8 h, weil Testklicks bzw. erst am nächsten Morgen entschieden. (b) Branchenwert als Gegenprobe, siehe unten |
| **Minuten je Übergabe** | Bei einer Übergabe arbeitet der Mensch den Fall fast komplett, mit etwas Vorarbeit durch den Agent. | Eigene Messung an den Übergaben aus dem Goldset (T02, T07, T13, T14), einmal mit und einmal ohne die Übergabenotiz des Agents. Zusätzlich die Annahme „Übergabe ≈ Ticket ohne Agent minus x“ mit Spannweite |
| **Minuten je Ticket ohne Agent** | Das ist die Vergleichsbasis. | Branchenzahlen: MetricNet/HDI nennt für Service Desks eine durchschnittliche Bearbeitungszeit von 14,4 min je Kontakt (Spanne 3,8–25,0) und 0,41 USD je Minute (Benchmark-Muster 2023; [MetricNet-Beispielbericht](https://www.rightstar.com/wp-content/uploads/2023/02/Sample-Service-Desk-Industry-Benchmark-from-MetricNet-v1.pdf), [HDI: Understanding Cost per Ticket](https://www.thinkhdi.com/library/supportworld/2021/understanding-cost-per-ticket)). Achtung: IT-Service-Desk, nicht B2C-App-Support. Für E-Mail-Tickets werden 4–6 min (Routine) bzw. 8–15 min (komplex) genannt, angeblich aus Salesforce „State of Service“. Gefunden habe ich das nur in Sekundärquellen, vor Verwendung im Original prüfen |
| **Kosten je Support-Minute** | Macht Minuten zu Geld. | Für Deutschland: Destatis, Arbeitskosten je geleistete Stunde bzw. Verdienste nach Berufen (Kundenservice). Alternativ die 0,41 USD/min von MetricNet als Vergleich. Beides als Spanne führen |
| **Echte Mischung der Tickets** | Bestimmt, wie oft jede der drei Klassen vorkommt. Das ist die empfindlichste Stellschraube. | (a) UC2-Goldset (73 Tickets, Kategorien von Hand) als breitere Proxy-Mischung, fiktiv. (b) Öffentliche Kategorieverteilungen von Abo-Apps, z. B. aus Helpdesk-Benchmarks (Zendesk, Intercom), zu recherchieren. (c) Am ehrlichsten: **Szenarien** (z. B. 10 / 20 / 40 % Erstattungsfälle) statt einer Punktschätzung |
| **Automatisierungsquote in der Praxis** | Prüft, ob 53–64 % „ohne Menschen“ realistisch sind. | Klarna (Pressemitteilung 27.02.2024): KI-Assistent bearbeitet zwei Drittel der Chats, Lösungszeit 2 statt 11 Minuten (Herstellerangabe, Chat, Kundensicht, keine Bearbeitungszeit je Mitarbeiter). Gute Größenordnung, aber Eigenwerbung |
| Cloud Run und Neon laut Rechnung | Fixkostenblock je Monat | Console-Export (Abrechnung → Berichte als CSV) bzw. Neon-Dashboard, Verbrauch. Beides lesend, ich habe keinen Zugang über die CLI |
| Neuschreiben ohne Zusage | Kosten und Häufigkeit unbekannt | Häufigkeit aus UC6: Wie viele Goldset-Entwürfe hätte die Zusage-Prüfung angehalten? Lässt sich aus den gespeicherten Entwürfen ohne API auszählen |

Für den späteren Build-vs-Buy-Teil schon notiert: Intercom Fin wird mit 0,99 USD je gelöstem Gespräch angegeben (laut mehreren Preisübersichten 2026, z. B. [gleap.io](https://www.gleap.io/blog/intercom-fin-ai-pricing-2026)). Vor Verwendung auf der Intercom-Preisseite prüfen.
