# Projekt-Kontext

## Problem
Entscheidungsvorlage, kein Produktcode: Was kostet ein Support-Ticket mit dem UC7-Agent im Vergleich zu einem Ticket, das komplett ein Mensch bearbeitet? Darauf aufbauend Pricing und Build-vs-Buy.

Datenquellen (Nachbar-Repos unter `~/dev`, nur lesen, nie ändern):
- `ai-uc-04-agents-mcp`: Goldset `evals/aufgaben.json` (15 Tickets), Läufe `evals/laeufe/v3` (45)
- `ai-uc-06-prompt-injection`: Läufe `evals/goldset_nachher` (45) = Stand des deployten Agents
- `ai-uc-07-deployment`: Code der Web-App, Kalibrierung, Protokoll in Neon (`DATABASE_URL` aus dessen `.env`, nur Read-only-Transaktionen)
- Cloud Run: Projekt `focusflow-demo-510014`, Dienst `uc7`, nur lesend (Monitoring-API, `gcloud ... describe`)

Regeln:
- Jede Zahl mit Wert, Einheit, Modell, was gezählt wird, Quelle (Datei + Commit) und Datum in `data/inventur.csv`. Erzeugt wird sie von `scripts/inventur.py` (mit dem Python aus `ai-uc-07-deployment/.venv`, wegen psycopg).
- Goldset und Live immer getrennt ausweisen. Live sind bisher nur Testläufe des Betreibers.
- Annahmen (Minuten, Stundensätze, Ticketmischung) nur mit Quelle oder als ausgewiesene Szenarien.
- Bezahlte Schritte (API-Läufe) vorher schätzen und freigeben lassen.

## Erwartete Artefakte
- README.md nach Schema (Problem, PM-Entscheidung, Architektur, Eval, Kosten/Latenz, Learnings)
- README.md auf Englisch, README_DE.md auf Deutsch, inhaltlich identisch (gleiche Zahlen, Tabellen, Fachbegriffe). Oben jeweils Sprachlink (🇩🇪 Deutsche Version / 🇬🇧 English version). Änderungen immer in beiden Dateien nachziehen.
- meta.json gepflegt (status ausschließlich: planned | active | done)
- meta.json auf Englisch (speist die Portfolio-Seite): title, summary = ein Satz „what it shows“, metrics = 1–2 Kennzahlen wörtlich aus dem README; optional demo {url, note} und screenshot (Pfad im Repo)
- evals/ mit Datensatz + Ergebnissen
- docs/decisions.md mit datierten Entscheidungen

## Erlaubte Libraries
- Direkt gegen das SDK, kein LangChain/LlamaIndex
- [ggf. weitere Einschränkungen pro Use Case]

## Stil
- Python, einfache Skripte statt Frameworks
- Drei Zahlen im README Pflicht: Kosten/1000 Requests, p95-Latenz, Qualitätsmetrik
