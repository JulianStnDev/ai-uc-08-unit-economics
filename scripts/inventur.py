"""Zahleninventur für UC8: liest UC4, UC6 und UC7 (Nachbar-Repos), das UC7-Protokoll in Neon und Cloud Monitoring.

Nur lesend, keine API-Kosten. Schreibt data/inventur.csv und gibt die Belegzeilen für docs/INVENTUR.md aus.

    ../ai-uc-07-deployment/.venv/bin/python scripts/inventur.py            # alles (Neon + Monitoring)
    python3 scripts/inventur.py --offline                                  # nur Repos, Live-Zeilen als Lücke

Perzentile: p95 als Nearest-Rank (kleinster Wert, unter dem mindestens 95 % liegen). Bei n < 20 ist das der
größte Wert. So steht es auch in UC7 („p95 entspricht hier dem längsten Lauf“).
"""
import csv
import hashlib
import json
import math
import statistics
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
DEV = HIER.parent
UC4 = DEV / "ai-uc-04-agents-mcp"
UC6 = DEV / "ai-uc-06-prompt-injection"
UC7 = DEV / "ai-uc-07-deployment"
GCP_PROJEKT = "focusflow-demo-510014"
HEUTE = date.today().isoformat()
OFFLINE = "--offline" in sys.argv

FELDER = ["id", "gruppe", "kennzahl", "wert", "einheit", "modell", "gezaehlt", "n",
          "quelle", "commit", "datum_daten", "erhoben", "art"]
zeilen: list[dict] = []


def commit(repo: Path, pfad: str) -> str:
    out = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%h", "--", pfad],
                         capture_output=True, text=True).stdout.strip()
    return out or "?"


def p95(xs):
    xs = sorted(xs)
    return xs[math.ceil(0.95 * len(xs)) - 1]


def zeile(id, gruppe, kennzahl, wert, einheit, modell, gezaehlt, n, quelle, commit_, datum, art="gemessen"):
    if isinstance(wert, float):
        wert = round(wert, 5)
    zeilen.append(dict(id=id, gruppe=gruppe, kennzahl=kennzahl, wert=wert, einheit=einheit, modell=modell,
                       gezaehlt=gezaehlt, n=n, quelle=quelle, commit=commit_, datum_daten=datum, erhoben=HEUTE, art=art))


def median_p95(prefix, gruppe, was, xs, einheit, modell, gezaehlt, quelle, commit_, datum):
    zeile(f"{prefix}_median", gruppe, f"{was} Median", statistics.median(xs), einheit, modell, gezaehlt, len(xs),
          quelle, commit_, datum)
    zeile(f"{prefix}_p95", gruppe, f"{was} p95", p95(xs), einheit, modell, gezaehlt, len(xs), quelle, commit_, datum)


def laeufe(ordner: Path):
    """Läufe im UC4-Format: je Lauf ein Ordner T01_lauf1 mit lauf.json und optional jsonl-Dateien je Aktion."""
    for d in sorted(p for p in ordner.glob("T??_lauf?") if p.is_dir()):
        def hat(name):
            f = d / f"{name}.jsonl"
            return f.exists() and f.read_text(encoding="utf-8").strip() != ""
        yield d, json.loads((d / "lauf.json").read_text(encoding="utf-8")), hat


# ---------- 1. Token-Kosten pro Ticket ----------

def goldset_kosten(repo, ordner_rel, prefix, label, datum):
    ordner = repo / ordner_rel
    kosten, judge = [], []
    for d, lauf, _ in laeufe(ordner):
        kosten.append(lauf["kosten_usd"])
        j = d / "judge_j2.json"
        if j.exists():
            judge.append(json.loads(j.read_text(encoding="utf-8"))["judge_kosten_usd"])
    c = commit(repo, ordner_rel)
    median_p95(f"{prefix}_agent", "Token-Kosten", f"Agent je Ticket ({label})", kosten, "USD", "claude-haiku-4-5",
               "kosten_usd aus lauf.json je Goldset-Lauf (15 Tickets × 3 Läufe), SDK-Schätzung inkl. Cache",
               f"{repo.name}/{ordner_rel}/*/lauf.json", c, datum)
    if judge:
        median_p95(f"{prefix}_judge", "Token-Kosten", f"Judge j2 je Urteil ({label}, Eval)", judge, "USD",
                   "claude-sonnet-5", "judge_kosten_usd je Goldset-Lauf; Eval-Judge mit Goldantwort, nicht der Betriebs-Judge u1",
                   f"{repo.name}/{ordner_rel}/*/judge_j2.json", c, datum)
    return kosten


def kalibrierung():
    pfad = "evals/kalibrierung.jsonl"
    rs = [json.loads(l) for l in (UC7 / pfad).read_text(encoding="utf-8").splitlines() if l.strip()]
    c = commit(UC7, pfad)
    for modell, kurz in [("claude-sonnet-5", "sonnet"), ("claude-haiku-4-5", "haiku")]:
        median_p95(f"kalib_judge_{kurz}", "Token-Kosten", f"Judge u1 je Urteil (Kalibrierung, {kurz})",
                   [r[modell]["kosten_usd"] for r in rs], "USD", modell,
                   "Betriebs-Judge u1 auf 10 UC4-Läufen (v3), offline nachgemessen", f"{UC7.name}/{pfad}", c, "2026-09-28")


# ---------- Live (Neon) ----------

def neon():
    from dotenv import dotenv_values
    import psycopg
    url = dotenv_values(UC7 / ".env")["DATABASE_URL"]
    with psycopg.connect(url) as conn:
        conn.read_only = True
        cur = conn.cursor()
        cur.execute("SELECT run_id, erstellt, kunden_id, titel, kosten_usd, ergebnis, zugang FROM laeufe "
                    "WHERE status = 'fertig' ORDER BY erstellt")
        laeufe_ = [dict(zip(["run_id", "erstellt", "kunden_id", "titel", "kosten", "ergebnis", "zugang"], r))
                   for r in cur.fetchall()]
        cur.execute("SELECT run_id, quelle, modell, kosten_usd, entscheidungen FROM antworten ORDER BY erstellt")
        antworten = cur.fetchall()
        cur.execute("SELECT run_id, art, modell, kosten_usd FROM pruefungen WHERE judge IS NOT NULL ORDER BY erstellt")
        judge = cur.fetchall()
        cur.execute("SELECT e.run_id, e.erstellt, f.entscheidung, f.entschieden FROM empfehlungen e "
                    "LEFT JOIN freigaben f USING (empfehlungs_id) ORDER BY e.erstellt")
        freigaben = cur.fetchall()
        cur.execute("SELECT pg_database_size(current_database())")
        groesse = cur.fetchone()[0]
    return laeufe_, antworten, judge, freigaben, groesse


def live(daten):
    laeufe_, antworten, judge, freigaben, groesse = daten
    q = "Neon neondb (UC7-Protokoll), lesende Abfrage"
    zeitraum = f"{laeufe_[0]['erstellt'][:10]}..{laeufe_[-1]['erstellt'][:10]}"
    median_p95("live_agent", "Token-Kosten", "Agent je Ticket (live)", [l["kosten"] for l in laeufe_], "USD",
               "claude-haiku-4-5", "laeufe.kosten_usd aller fertigen Läufe auf Cloud Run (alle mit Admin-Zugang gestartet)",
               q + ", Tabelle laeufe", "—", zeitraum)
    llm = [a for a in antworten if a[1] == "llm"]
    zusage = [a for a in antworten if a[4] and any(e.get("art") == "zusage" for e in json.loads(a[4]))]
    median_p95("live_haiku_antwort", "Token-Kosten", "Haiku endgültige Antwort je Ticket mit Empfehlung (live)",
               [a[3] for a in llm], "USD", "claude-haiku-4-5",
               "antworten.kosten_usd, ein Haiku-Aufruf nach der Entscheidung über die Empfehlung (Variante A)",
               q + ", Tabelle antworten", "—", zeitraum)
    zeile("live_haiku_zusage_n", "Token-Kosten", "Haiku Neuschreiben ohne Zusage (UC6 B2), Anzahl live", len(zusage),
          "Aufrufe", "claude-haiku-4-5", "antworten mit entscheidungen.art = zusage; seit uc7-00009 möglich", len(laeufe_),
          q + ", Tabelle antworten", "—", zeitraum, art="Lücke" if not zusage else "gemessen")
    median_p95("live_judge", "Token-Kosten", "Judge u1 je Urteil (live)", [j[3] for j in judge], "USD", "claude-sonnet-5",
               "pruefungen.kosten_usd mit Urteil (Stichprobe und von Hand erzwungen)", q + ", Tabelle pruefungen", "—", zeitraum)

    # ---------- 2. Anteile live ----------
    n = len(laeufe_)
    e = u = k = 0
    for l in laeufe_:
        erg = json.loads(l["ergebnis"] or "{}")
        hat_e, hat_u = bool(erg.get("empfehlungen")), bool(erg.get("uebergaben"))
        e += hat_e; u += hat_u; k += (not hat_e and not hat_u)
    for id_, was, wert in [("live_anteil_empfehlung", "mit Erstattungsempfehlung", e),
                           ("live_anteil_uebergabe", "mit Übergabe an Mensch", u),
                           ("live_anteil_ohne_mensch", "ohne Menschen (weder Empfehlung noch Übergabe)", k)]:
        zeile(id_, "Anteile", f"Tickets {was} (live)", f"{wert}/{n}", "Tickets", "claude-haiku-4-5",
              "Ergebnis-JSON je fertigem Lauf; Testläufe des Betreibers mit Goldset-Tickets, keine echten Kunden",
              n, q + ", laeufe.ergebnis", "—", zeitraum)
    besucher = sum(1 for l in laeufe_ if l["zugang"])
    zeile("live_laeufe_besucher", "Anteile", "Läufe über persönliche Besucher-Links", besucher, "Läufe", "—",
          "laeufe.zugang IS NOT NULL (sonst Admin)", n, q + ", laeufe.zugang", "—", zeitraum)

    # ---------- 4. Judge im Betrieb ----------
    stichprobe = sum(1 for j in judge if int(hashlib.sha256(j[0].encode()).hexdigest(), 16) % 100 < 20)
    zeile("live_judge_urteile", "Judge im Betrieb", "Judge-Urteile im Betrieb", len(judge), "Urteile", "claude-sonnet-5",
          "pruefungen mit Urteil; davon per Hash-Stichprobe (20 %), Rest von Hand erzwungen", n, q + ", Tabelle pruefungen",
          "—", zeitraum)
    zeile("live_judge_stichprobe", "Judge im Betrieb", "davon aus der 20-%-Stichprobe", stichprobe, "Urteile",
          "claude-sonnet-5", "in_stichprobe(run_id) aus app/pruefung.py nachgerechnet", n, q, "—", zeitraum)

    # Freigabe-Dauer (Klick des Betreibers, keine Bearbeitungszeit)
    from datetime import datetime
    dauern = [(datetime.fromisoformat(f[3]) - datetime.fromisoformat(f[1])).total_seconds()
              for f in freigaben if f[3]]
    if dauern:
        median_p95("live_freigabe_dauer", "Lücken", "Zeit Empfehlung bis Entscheidung (Testklicks)", dauern, "s", "—",
                   "freigaben.entschieden minus empfehlungen.erstellt; Betreiber testet, keine echte Bearbeitungszeit",
                   q + ", Tabellen empfehlungen/freigaben", "—", zeitraum)
    zeile("neon_groesse", "Hosting", "Neon Datenbankgröße", round(groesse / 1024 / 1024, 1), "MB", "—",
          "pg_database_size(neondb)", "—", q, "—", HEUTE)
    return laeufe_


# ---------- Cloud Monitoring ----------

def monitoring(metrik, wertfeld):
    token = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True).stdout.strip()
    params = urllib.parse.urlencode({
        "filter": f'metric.type="run.googleapis.com/{metrik}"',
        "interval.startTime": "2026-09-01T00:00:00Z", "interval.endTime": f"{HEUTE}T12:00:00Z",
        "aggregation.alignmentPeriod": "86400s", "aggregation.perSeriesAligner": "ALIGN_SUM",
        "aggregation.crossSeriesReducer": "REDUCE_SUM"})
    req = urllib.request.Request(f"https://monitoring.googleapis.com/v3/projects/{GCP_PROJEKT}/timeSeries?{params}",
                                 headers={"Authorization": f"Bearer {token}"})
    d = json.load(urllib.request.urlopen(req))
    punkte = [(p["interval"]["endTime"][:10], float(p["value"].get(wertfeld, 0)))
              for s in d.get("timeSeries", []) for p in s["points"]]
    return sorted(punkte)


# ---------- main ----------

def main():
    datum_uc4 = "2026-09-24"
    goldset_kosten(UC4, "evals/laeufe/v3", "uc4v3", "Goldset UC4 v3", datum_uc4)
    goldset_kosten(UC6, "evals/goldset_nachher", "uc6", "Goldset UC6 nachher = deployter Stand", "2026-10-02")
    kalibrierung()

    # ---------- 2. Anteile Goldset (Soll und Ist) ----------
    aufg_pfad = "evals/aufgaben.json"
    aufgaben = json.loads((UC4 / aufg_pfad).read_text(encoding="utf-8"))["aufgaben"]
    n = len(aufgaben)
    soll_e = sum(1 for t in aufgaben if t.get("erstattung_soll"))
    soll_u = sum(1 for t in aufgaben if t.get("uebergabe_soll") is True)
    soll_k = sum(1 for t in aufgaben if not t.get("erstattung_soll") and t.get("uebergabe_soll") is not True)
    c = commit(UC4, aufg_pfad)
    for id_, was, wert in [("gold_soll_empfehlung", "mit Erstattungsempfehlung", soll_e),
                           ("gold_soll_uebergabe", "mit Pflicht-Übergabe", soll_u),
                           ("gold_soll_ohne_mensch", "ohne Menschen", soll_k)]:
        zeile(id_, "Anteile", f"Goldset-Tickets {was} (Soll)", f"{wert}/{n}", "Tickets", "—",
              "erstattung_soll / uebergabe_soll (true = Pflicht, null = optional zählt nicht)", n,
              f"{UC4.name}/{aufg_pfad}", c, datum_uc4, art="dokumentiert")
    for repo, rel, prefix, label in [(UC4, "evals/laeufe/v3", "gold_ist_uc4v3", "UC4 v3"),
                                     (UC6, "evals/goldset_nachher", "gold_ist_uc6", "UC6 nachher")]:
        e = u = k = m = 0
        for _, _, hat in laeufe(repo / rel):
            m += 1
            e += hat("erstattungsempfehlungen"); u += hat("uebergaben")
            k += (not hat("erstattungsempfehlungen") and not hat("uebergaben"))
        for suf, was, wert in [("empfehlung", "mit Erstattungsempfehlung", e), ("uebergabe", "mit Übergabe", u),
                               ("ohne_mensch", "ohne Menschen", k)]:
            zeile(f"{prefix}_{suf}", "Anteile", f"Goldset-Läufe {was} (Ist, {label})", f"{wert}/{m}", "Läufe",
                  "claude-haiku-4-5", "Lauf hat nicht leere erstattungsempfehlungen.jsonl bzw. uebergaben.jsonl",
                  m, f"{repo.name}/{rel}/*", commit(repo, rel), datum_uc4 if repo == UC4 else "2026-10-02")

    # ---------- 3./4. dokumentierte Konfiguration ----------
    for id_, gruppe, was, wert, einheit, gezaehlt, quelle_rel in [
        ("cfg_judge_stichprobe", "Judge im Betrieb", "Judge-Stichprobe", 20, "% der Läufe",
         "STICHPROBE_PROZENT, reproduzierbar per SHA-256 der Lauf-ID", "app/pruefung.py"),
        ("cfg_judge_deckel", "Judge im Betrieb", "Judge-Deckel je Monat", 0.50, "USD",
         "JUDGE_DECKEL_MONAT_USD; darüber kein Judge mehr", "app/pruefung.py"),
        ("cfg_monatsdeckel", "Hosting", "API-Monatsdeckel in der App", 4.50, "USD",
         "Deckel plus 0,50 USD Reserve je laufendem Ticket = 5 USD harte Grenze", "README_DE.md"),
        ("cfg_cloudrun", "Hosting", "Cloud Run Instanzgröße", "1 vCPU / 1 GiB", "—",
         "min. 0, max. 2 Instanzen, Abrechnung pro Instanz (--no-cpu-throttling), europe-west3", "docs/deploy.md"),
        ("cfg_freikontingent", "Hosting", "Cloud Run Freikontingent laut Recherche", "180000 vCPU-s + 360000 GiB-s", "je Monat",
         "Free Tier je Billing-Konto, Stand der Recherche 2026-09-28 (cloud.google.com/run/pricing)", "docs/plan.md"),
        ("cfg_neon_plan", "Hosting", "Neon Tarif laut Entscheidung", "Free (0,5 GB, 100 CU-h/Monat)", "—",
         "Free-Plan, Frankfurt; tatsächlicher Tarif im Konto nicht lesend geprüft", "docs/plan.md"),
    ]:
        zeile(id_, gruppe, was, wert, einheit, "—", gezaehlt, "—", f"{UC7.name}/{quelle_rel}",
              commit(UC7, quelle_rel), HEUTE if quelle_rel != "docs/plan.md" else "2026-09-28", art="dokumentiert")

    if OFFLINE:
        print("--offline: Live- und Monitoring-Zeilen fehlen")
    else:
        live(neon())
        inst = monitoring("container/billable_instance_time", "doubleValue")
        reqs = monitoring("request_count", "int64Value")
        zeitraum = f"{inst[0][0]}..{inst[-1][0]}"
        q = f"Cloud Monitoring API, Projekt {GCP_PROJEKT}, Dienst uc7, Tagessummen (Fenster enden 12:00 UTC)"
        zeile("cr_instanzzeit", "Hosting", "Cloud Run abgerechnete Instanzzeit seit Deploy", round(sum(v for _, v in inst)),
              "Instanz-s", "—", "run.googleapis.com/container/billable_instance_time, 1 vCPU und 1 GiB je Instanz-s",
              len(inst), q, "—", zeitraum)
        zeile("cr_requests", "Hosting", "Cloud Run Anfragen seit Deploy", int(sum(v for _, v in reqs)), "Anfragen", "—",
              "run.googleapis.com/request_count (Seiten, SSE, Health, Konsole)", len(reqs), q, "—", zeitraum)
        print("Instanzzeit je Tag:", inst)
        print("Anfragen je Tag:", reqs)

    for id_, gruppe, was, warum in [
        ("luecke_rechnung_gcp", "Hosting", "Cloud Run Kosten laut Rechnung",
         "kein Billing-Export nach BigQuery; Cloud Billing API liefert keine Beträge. Console: Abrechnung → Berichte"),
        ("luecke_neon_verbrauch", "Hosting", "Neon Compute-Stunden und Tarif im Konto",
         "kein Neon-API-Key/neonctl lokal; per SQL nur die Datenbankgröße lesbar"),
        ("luecke_minuten_freigabe", "Lücken", "Minuten je Freigabe (Mensch)", "nirgends gemessen; Klickzeiten sind Tests"),
        ("luecke_minuten_uebergabe", "Lücken", "Minuten je Übergabe (Mensch)", "nirgends gemessen; Übergaben werden nicht bearbeitet"),
        ("luecke_mischung", "Lücken", "Echte Mischung der Tickets", "keine echten Kunden; Goldset und Live sind ausgewählte Fälle"),
        ("luecke_minuten_ohne_agent", "Lücken", "Minuten je Ticket ohne Agent (Mensch komplett)", "nirgends gemessen"),
        ("luecke_stundensatz", "Lücken", "Kosten je Support-Minute (Lohn inkl. Nebenkosten)", "nirgends erhoben"),
    ]:
        zeile(id_, gruppe, was, "", "", "—", warum, "—", "—", "—", "—", art="Lücke")

    with open(HIER / "data" / "inventur.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FELDER)
        w.writeheader()
        w.writerows(zeilen)
    print(f"{len(zeilen)} Zeilen → data/inventur.csv")
    for z in zeilen:
        print(f"{z['id']:28} {z['wert']!s:>30} {z['einheit']:10} n={z['n']}")


if __name__ == "__main__":
    main()
