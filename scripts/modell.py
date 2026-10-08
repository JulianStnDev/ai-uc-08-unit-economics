"""Kostenmodell UC8: Kosten pro Ticket und pro Monat, ohne Agent gegen mit Agent. Ohne API, nur data/annahmen.csv.

    python3 scripts/modell.py

Schreibt evals/modell_ergebnisse.csv, evals/modell.md, docs/kipppunkt.svg und docs/tornado.svg.
Rechenweg von Hand für ein Szenario: docs/RECHENWEG.md.

Tokens und Cloud-Run-Preise sind in USD und werden einmal mit usd_je_eur umgerechnet, Personal ist in EUR.
Szenarien variieren Anteile (Freigabe, Übergabe, Nacharbeit) und Minuten je Eingriff. Alle anderen Eingaben stehen
auf „mittel“. Minuten je Übergabe = min_ohne_agent × faktor_uebergabe, Nacharbeit kostet je Fall min_ohne_agent.
"""
import csv
import math
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
MENGEN = [1_000, 10_000, 100_000]
SZENARIEN = {"optimistisch": "niedrig", "mittel": "mittel", "pessimistisch": "hoch"}
SZENARIO_PARAMETER = ["anteil_freigabe", "anteil_uebergabe", "min_freigabe", "faktor_uebergabe", "anteil_nacharbeit"]
BETRAGSGRENZEN = [5, 10, 20, 59]  # EUR, Option „automatisch bis X €“
TORNADO_MENGE = 10_000


def annahmen() -> dict:
    with open(HIER / "data" / "annahmen.csv", encoding="utf-8") as f:
        return {r["id"]: {k: (float(r[k]) if r[k] else None) for k in ("niedrig", "mittel", "hoch")}
                for r in csv.DictReader(f)}


A = annahmen()


def wert(id_, stufe="mittel"):
    return A[id_][stufe]


def eingaben(szenario: str) -> dict:
    stufe = SZENARIEN[szenario]
    e = {id_: wert(id_) for id_ in A if A[id_]["mittel"] is not None}
    e.update({p: wert(p, stufe) for p in SZENARIO_PARAMETER})
    return e


def je_ticket(e: dict, menge: int) -> dict:
    """Kosten je Ticket in EUR, aufgeteilt in Posten."""
    kurs = e["usd_je_eur"]
    tokens_usd = e["tok_agent"] + e["anteil_freigabe"] * e["tok_antwort"] + e["judge_quote"] * e["tok_judge"]
    instanz_s = e["laufzeit"] / e["auslastung"]
    hosting_usd = instanz_s * (e["cr_preis_vcpu"] * 1 + e["cr_preis_gib"] * 1)  # 1 vCPU, 1 GiB
    autonom = 1 - e["anteil_freigabe"] - e["anteil_uebergabe"]
    p = {
        "tokens": tokens_usd / kurs,
        "hosting_variabel": hosting_usd / kurs,
        "freigabe": e["anteil_freigabe"] * e["min_freigabe"] * e["eur_je_minute"],
        "uebergabe": e["anteil_uebergabe"] * min_uebergabe(e) * e["eur_je_minute"],
        "nacharbeit": autonom * e["anteil_nacharbeit"] * e["min_ohne_agent"] * e["eur_je_minute"],
        "fix": (e["hosting_fix"] + e["neon_fix"]) / menge,
    }
    p["variabel"] = p["tokens"] + p["hosting_variabel"] + p["freigabe"] + p["uebergabe"] + p["nacharbeit"]
    p["mit_agent"] = p["variabel"] + p["fix"]
    p["ohne_agent"] = e["min_ohne_agent"] * e["eur_je_minute"]
    p["ersparnis"] = p["ohne_agent"] - p["mit_agent"]
    return p


def min_uebergabe(e: dict) -> float:
    return e["min_ohne_agent"] * e["faktor_uebergabe"]


def kipppunkt(e: dict, menge: int, min_ohne=None) -> float:
    """Übergabequote, ab der mit Agent nicht mehr günstiger ist (Ersparnis = 0). Freigabe-Anteil bleibt fest.
    Die Ersparnis ist linear in der Übergabequote; inf, wenn sie mit der Quote nicht sinkt."""
    if min_ohne is not None:
        e = {**e, "min_ohne_agent": min_ohne}
    s0, s1 = ersparnis_bei(e, 0.0, menge), ersparnis_bei(e, 1.0, menge)
    return s0 / (s0 - s1) if s0 > s1 else math.inf


def ersparnis_bei(e: dict, quote: float, menge: int) -> float:
    return je_ticket({**e, "anteil_uebergabe": quote}, menge)["ersparnis"]


def eur(x, stellen=2):
    return f"{x:,.{stellen}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, stellen=0):
    return f"{x * 100:.{stellen}f}".replace(".", ",") + " %"


# ---------- Diagramm ----------

FARBEN = {  # Kategorial Slots 1–3 (dataviz-Referenzpalette), hell / dunkel
    "optimistisch": ("#2a78d6", "#3987e5"),
    "mittel": ("#eb6834", "#d95926"),
    "pessimistisch": ("#1baf7a", "#199e70"),
}


def diagramm(menge: int) -> str:
    B, H = 760, 490
    L, R, O, U = 70, 170, 96, 78
    xmin, xmax, ymin, ymax = 0.0, 1.0, -1.0, 4.0
    def X(q): return L + (q - xmin) / (xmax - xmin) * (B - L - R)
    def Y(v): return O + (ymax - v) / (ymax - ymin) * (H - O - U)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {B} {H}" width="{B}" height="{H}" '
         f'font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif" role="img" '
         f'aria-label="Ersparnis je Ticket über der Übergabequote, drei Szenarien">']
    css = [":root{--bg:#fcfcfb;--t1:#0b0b0b;--t2:#52514e;--grid:#e6e5e1;--zero:#8a8984;"]
    css += [f"--{n}:{h};" for n, (h, _) in FARBEN.items()]
    css += ["}@media (prefers-color-scheme: dark){:root{--bg:#1a1a19;--t1:#ffffff;--t2:#c3c2b7;--grid:#34332f;--zero:#8a8984;"]
    css += [f"--{n}:{d};" for n, (_, d) in FARBEN.items()]
    css += ["}}"]
    s.append(f"<style>{''.join(css)} text{{fill:var(--t2);font-size:12px}} .t1{{fill:var(--t1)}}</style>")
    s.append(f'<rect width="{B}" height="{H}" fill="var(--bg)"/>')
    s.append(f'<text x="{L}" y="26" class="t1" font-size="16" font-weight="600">Ersparnis je Ticket gegenüber Mensch allein</text>')
    s.append(f'<text x="{L}" y="46">EUR je Ticket bei {eur(menge, 0)} Tickets im Monat. Unter 0 ist der Agent teurer. '
             f'Mensch allein: {eur(wert("min_ohne_agent"), 0)} min × {eur(wert("eur_je_minute"), 3)} EUR/min</text>')
    # Legende
    lx = L
    for n in FARBEN:
        s.append(f'<line x1="{lx}" y1="70" x2="{lx + 22}" y2="70" stroke="var(--{n})" stroke-width="2"/>')
        s.append(f'<text x="{lx + 28}" y="74">{n}</text>')
        lx += 130
    # Raster und Achsen
    for v in [x * 0.5 for x in range(-2, 9)]:
        s.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{B - R}" y2="{Y(v):.1f}" '
                 f'stroke="{"var(--zero)" if v == 0 else "var(--grid)"}" stroke-width="1"/>')
        if v == int(v):
            s.append(f'<text x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end">{eur(v, 0)}</text>')
    for q in [x / 10 for x in range(0, 11, 2)]:
        s.append(f'<text x="{X(q):.1f}" y="{H - U + 18}" text-anchor="middle">{int(q * 100)} %</text>')
    s.append(f'<text x="{(L + B - R) / 2:.0f}" y="{H - U + 38}" text-anchor="middle">Übergabequote (Anteil der Tickets, die an einen Menschen gehen)</text>')
    # gemessene Quote
    gemessen = 10 / 45
    s.append(f'<line x1="{X(gemessen):.1f}" y1="{O}" x2="{X(gemessen):.1f}" y2="{H - U}" stroke="var(--t2)" '
             f'stroke-width="1" stroke-dasharray="4 4"/>')
    s.append(f'<text x="{X(gemessen) + 6:.1f}" y="{O + 12}">Goldset UC6 gemessen: {pct(gemessen)}</text>')
    # Linien
    label_y = []
    for n in FARBEN:
        e = eingaben(n)
        qmax = 1 - e["anteil_freigabe"]
        pts = [(q / 100 * qmax, ersparnis_bei(e, q / 100 * qmax, menge)) for q in range(0, 101, 5)]
        s.append(f'<polyline fill="none" stroke="var(--{n})" stroke-width="2" stroke-linejoin="round" points="'
                 + " ".join(f"{X(q):.1f},{Y(v):.1f}" for q, v in pts) + '"/>')
        # Betriebspunkt des Szenarios
        q0 = e["anteil_uebergabe"]; v0 = ersparnis_bei(e, q0, menge)
        s.append(f'<circle cx="{X(q0):.1f}" cy="{Y(v0):.1f}" r="5" fill="var(--{n})" stroke="var(--bg)" stroke-width="2">'
                 f'<title>{n}: Übergabe {pct(q0)}, Ersparnis {eur(v0)} EUR je Ticket</title></circle>')
        k = kipppunkt(e, menge)
        if 0 <= k <= qmax:
            s.append(f'<circle cx="{X(k):.1f}" cy="{Y(0):.1f}" r="5" fill="var(--bg)" stroke="var(--{n})" stroke-width="2">'
                     f'<title>Kipppunkt {n}: {pct(k)}</title></circle>')
        label_y.append((Y(pts[-1][1]), X(qmax) + 8, n, "kein Kipppunkt" if k > qmax else f"Kipppunkt {pct(k)}"))
    # Direkte Labels am Linienende, von unten nach oben gesetzt, damit sie nach oben ausweichen
    oben = H - U - 24
    for y_end, x, n, rest in sorted(label_y, reverse=True):
        y_end = min(y_end, oben)
        oben = y_end - 32
        s.append(f'<text x="{x:.1f}" y="{y_end + 4:.1f}" class="t1">{n}</text>')
        s.append(f'<text x="{x:.1f}" y="{y_end + 18:.1f}" font-size="11">{rest}</text>')
    s.append(f'<text x="{L}" y="{H - 10}" font-size="11">Punkt = Übergabequote des Szenarios, Ring = Kipppunkt. '
             f'Linien enden bei 100 % minus Freigabe-Anteil.</text>')
    s.append("</svg>")
    return "\n".join(s)


TORNADO_PARAMETER = {  # id: Beschriftung
    "anteil_uebergabe": "Übergabequote", "faktor_uebergabe": "Faktor Minuten je Übergabe",
    "min_ohne_agent": "Minuten ohne Agent", "anteil_nacharbeit": "Anteil Nacharbeit",
    "anteil_freigabe": "Freigabe-Anteil", "min_freigabe": "Minuten je Freigabe",
    "eur_je_minute": "Personalkosten je Minute", "auslastung": "Auslastung Cloud Run",
}


def tornado_daten(menge: int) -> tuple[float, list]:
    basis_e = eingaben("mittel")
    basis = je_ticket(basis_e, menge)["ersparnis"]
    rows = []
    for id_, name in TORNADO_PARAMETER.items():
        lo, hi = wert(id_, "niedrig"), wert(id_, "hoch")
        s_lo = je_ticket({**basis_e, id_: lo}, menge)["ersparnis"]
        s_hi = je_ticket({**basis_e, id_: hi}, menge)["ersparnis"]
        rows.append((name, id_, lo, hi, s_lo, s_hi))
    rows.sort(key=lambda r: abs(r[5] - r[4]), reverse=True)
    return basis, rows


def zahl(x):
    return eur(x, 2 if x < 1 else (1 if x != int(x) else 0))


def tornado(menge: int) -> str:
    basis, rows = tornado_daten(menge)
    B, zeile_h = 760, 34
    L, R, O = 230, 40, 104
    H = O + zeile_h * len(rows) + 56
    werte = [v for r in rows for v in r[4:6]] + [basis]
    xmin, xmax = math.floor(min(werte) - 0.4), math.ceil(max(werte))
    def X(v): return L + (v - xmin) / (xmax - xmin) * (B - L - R)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {B} {H}" width="{B}" height="{H}" '
         f'font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif" role="img" '
         f'aria-label="Tornado: Ausschlag der Ersparnis je Ticket, wenn eine Annahme von niedrig auf hoch geht">']
    s.append("<style>:root{--bg:#fcfcfb;--t1:#0b0b0b;--t2:#52514e;--grid:#e6e5e1;--lo:#2a78d6;--hi:#eb6834;}"
             "@media (prefers-color-scheme: dark){:root{--bg:#1a1a19;--t1:#ffffff;--t2:#c3c2b7;--grid:#34332f;"
             "--lo:#3987e5;--hi:#d95926;}} text{fill:var(--t2);font-size:12px} .t1{fill:var(--t1)}</style>")
    s.append(f'<rect width="{B}" height="{H}" fill="var(--bg)"/>')
    s.append(f'<text x="24" y="26" class="t1" font-size="16" font-weight="600">Welche Annahme bewegt die Ersparnis am stärksten?</text>')
    s.append(f'<text x="24" y="46">Ersparnis je Ticket in EUR, Szenario mittel ({eur(basis)} EUR), {eur(menge, 0)} Tickets im Monat. '
             f'Je Zeile wandert genau eine Annahme.</text>')
    s.append(f'<rect x="24" y="62" width="14" height="10" rx="2" fill="var(--lo)"/><text x="44" y="71">Annahme auf niedrig</text>')
    s.append(f'<rect x="184" y="62" width="14" height="10" rx="2" fill="var(--hi)"/><text x="204" y="71">Annahme auf hoch</text>')
    for v in range(int(xmin), int(xmax) + 1):
        s.append(f'<line x1="{X(v):.1f}" y1="{O - 8}" x2="{X(v):.1f}" y2="{O + zeile_h * len(rows)}" stroke="var(--grid)"/>')
        s.append(f'<text x="{X(v):.1f}" y="{O + zeile_h * len(rows) + 18}" text-anchor="middle">{eur(v, 0)}</text>')
    for i, (name, id_, lo, hi, s_lo, s_hi) in enumerate(rows):
        y = O + i * zeile_h
        s.append(f'<text x="{L - 10}" y="{y + 15}" text-anchor="end" class="t1">{name}</text>')
        s.append(f'<text x="{L - 10}" y="{y + 28}" text-anchor="end" font-size="11">{zahl(lo)} … {zahl(hi)}</text>')
        for v, farbe, stufe, roh in [(s_lo, "lo", "niedrig", lo), (s_hi, "hi", "hoch", hi)]:
            if abs(v - basis) < 1e-9:
                continue
            x0, x1 = sorted([X(basis), X(v)])
            s.append(f'<rect x="{x0:.1f}" y="{y + 6}" width="{max(x1 - x0, 1):.1f}" height="20" rx="4" fill="var(--{farbe})">'
                     f'<title>{name} {stufe} ({zahl(roh)}): Ersparnis {eur(v)} EUR je Ticket</title></rect>')
            anker = "end" if v < basis else "start"
            dx = -6 if v < basis else 6
            s.append(f'<text x="{X(v) + dx:.1f}" y="{y + 20}" text-anchor="{anker}">{eur(v)}</text>')
    s.append(f'<line x1="{X(basis):.1f}" y1="{O - 8}" x2="{X(basis):.1f}" y2="{O + zeile_h * len(rows)}" stroke="var(--t1)" stroke-width="1.5"/>')
    s.append(f'<text x="{X(basis):.1f}" y="{O - 12}" text-anchor="middle" class="t1">mittel {eur(basis)}</text>')
    s.append(f'<text x="24" y="{H - 10}" font-size="11">Tokens, Kurs und Hosting-Preise sind gemessene Punktwerte und wandern nicht. '
             f'Quelle: data/annahmen.csv</text>')
    s.append("</svg>")
    return "\n".join(s)


# ---------- main ----------

def main():
    # Gegenprobe der abgeleiteten Minutenkosten (annahmen.csv führt sie gerundet)
    for stufe, brutto in [("niedrig", wert("brutto_monat", "niedrig")), ("mittel", wert("brutto_monat"))]:
        roh = brutto * 12 * wert("ag_faktor") / wert("stunden_jahr") / 60
        assert abs(roh - wert("eur_je_minute", stufe)) < 0.0005, (stufe, roh)
    assert abs(wert("arbeitskosten_stunde", "hoch") / 60 - wert("eur_je_minute", "hoch")) < 0.0005

    zeilen, roh, md = [], [], []
    md.append("# Kostenmodell: Ergebnisse\n\nErzeugt von `scripts/modell.py` aus `data/annahmen.csv`. Beträge in EUR, "
              f"Tokens umgerechnet mit {eur(wert('usd_je_eur'), 4)} USD/EUR. Rechenweg von Hand: [docs/RECHENWEG.md](../docs/RECHENWEG.md).\n")
    md.append("## Szenarien\n")
    md.append("| Szenario | Freigabe | Übergabe | autonom | Nacharbeit (der autonomen) | min/Freigabe | Faktor Übergabe | min/Übergabe |\n|---|---|---|---|---|---|---|---|")
    for n in SZENARIEN:
        e = eingaben(n)
        md.append(f"| {n} | {pct(e['anteil_freigabe'])} | {pct(e['anteil_uebergabe'])} | "
                  f"{pct(1 - e['anteil_freigabe'] - e['anteil_uebergabe'])} | {pct(e['anteil_nacharbeit'])} | "
                  f"{eur(e['min_freigabe'], 0)} | {eur(e['faktor_uebergabe'], 1)} | {eur(min_uebergabe(e), 1)} |")

    md.append("\n## Kosten je Ticket (EUR)\n")
    md.append("| Szenario | Tickets/Monat | Tokens | Hosting variabel | Freigabe | Übergabe | Nacharbeit | **variabel** | Fix je Ticket | **mit Agent** | **ohne Agent** | **Ersparnis** |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for n in SZENARIEN:
        e = eingaben(n)
        for m in MENGEN:
            p = je_ticket(e, m)
            roh.append((n, m, p))
            zeilen.append({"szenario": n, "tickets_monat": m, **{k: round(v, 6) for k, v in p.items()},
                           "mit_agent_monat": round(p["mit_agent"] * m, 2), "ohne_agent_monat": round(p["ohne_agent"] * m, 2),
                           "ersparnis_monat": round(p["ersparnis"] * m, 2), "kipppunkt_uebergabe": round(kipppunkt(e, m), 4)})
            md.append(f"| {n} | {eur(m, 0)} | {eur(p['tokens'], 4)} | {eur(p['hosting_variabel'], 4)} | {eur(p['freigabe'], 4)} | "
                      f"{eur(p['uebergabe'], 4)} | {eur(p['nacharbeit'], 4)} | **{eur(p['variabel'], 4)}** | {eur(p['fix'], 4)} | **{eur(p['mit_agent'], 4)}** | "
                      f"**{eur(p['ohne_agent'], 4)}** | **{eur(p['ersparnis'], 4)}** |")

    md.append("\n## Kosten je Monat (EUR)\n")
    md.append("| Szenario | Tickets/Monat | ohne Agent | mit Agent | davon variabel | davon fix | Ersparnis | Ersparnis in % |")
    md.append("|---|---|---|---|---|---|---|---|")
    for n, m, p in roh:
        md.append(f"| {n} | {eur(m, 0)} | {eur(p['ohne_agent'] * m)} | {eur(p['mit_agent'] * m)} | "
                  f"{eur(p['variabel'] * m)} | {eur(p['fix'] * m)} | {eur(p['ersparnis'] * m)} | {pct(p['ersparnis'] / p['ohne_agent'], 1)} |")

    md.append("\n## Kipppunkt: Übergabequote, ab der der Agent nicht mehr günstiger ist\n")
    md.append("Freigabe-Anteil, Nacharbeit-Anteil und Faktor bleiben je Szenario fest, nur die Übergabequote wandert "
              "(die autonomen Tickets schrumpfen entsprechend). Möglich sind höchstens 100 % minus Freigabe-Anteil. "
              "Minuten je Übergabe wandern mit den Minuten ohne Agent. 10.000 Tickets/Monat.\n")
    md.append("| Szenario | Mensch allein 5 min | **8 min (mittel)** | 14,4 min | Übergabequote des Szenarios |\n|---|---|---|---|---|")
    for n in SZENARIEN:
        e = eingaben(n); qmax = 1 - e["anteil_freigabe"]
        zellen = []
        for mo in [5, wert("min_ohne_agent"), 14.4]:
            k = kipppunkt(e, 10_000, mo)
            zellen.append(f"kein (> {pct(qmax)})" if k > qmax else pct(k))
        zellen[1] = f"**{zellen[1]}**"
        md.append(f"| {n} | {' | '.join(zellen)} | {pct(e['anteil_uebergabe'])} |")
    md.append("\nDie Personalkosten je Minute verschieben den Kipppunkt kaum: Tokens und Hosting zusammen kosten je Ticket so viel "
              "wie wenige Sekunden Arbeitszeit. Entscheidend sind Faktor je Übergabe und Nacharbeit. Für die Höhe der Ersparnis "
              "zählen die Personalkosten dagegen voll, siehe Tornado.")

    md.append("\n## Sensitivität (Tornado)\n")
    basis, rows = tornado_daten(TORNADO_MENGE)
    md.append(f"Szenario mittel, {eur(TORNADO_MENGE, 0)} Tickets/Monat, Ersparnis je Ticket {eur(basis, 4)} EUR. "
              "Je Zeile wandert genau eine Annahme von niedrig auf hoch, alle anderen bleiben auf mittel. "
              "Diagramm: [docs/tornado.svg](../docs/tornado.svg).\n")
    md.append("| Rang | Annahme | niedrig … hoch | Ersparnis bei niedrig | Ersparnis bei hoch | Ausschlag |\n|---|---|---|---|---|---|")
    for i, (name, id_, lo, hi, s_lo, s_hi) in enumerate(rows, 1):
        md.append(f"| {i} | {name} (`{id_}`) | {zahl(lo)} … {zahl(hi)} | {eur(s_lo, 4)} | {eur(s_hi, 4)} | {eur(abs(s_hi - s_lo), 4)} |")

    md.append("\n## Reparatur-Kandidat T04: Frist im Werkzeug berechnen\n")
    e = eingaben("mittel")
    m = 10_000
    autonom = 1 - e["anteil_freigabe"] - e["anteil_uebergabe"]
    verschoben = e["anteil_t04_an_autonom"] * autonom
    varianten = [("heute (T04-Fehler drin)", e),
                 ("nur Nacharbeit sinkt", {**e, "anteil_nacharbeit": e["nacharbeit_ohne_t04"]}),
                 ("Nacharbeit sinkt, T04 wird Freigabe", {**e, "anteil_nacharbeit": e["nacharbeit_ohne_t04"],
                                                          "anteil_freigabe": e["anteil_freigabe"] + verschoben})]
    vorher = je_ticket(e, m)
    md.append(f"Szenario mittel, {eur(m, 0)} Tickets/Monat. Ohne T04 hätte der deployte Agent 1 von 26 autonomen Läufen mit "
              f"falscher Kernaussage ({pct(e['nacharbeit_ohne_t04'], 1)} statt {pct(e['anteil_nacharbeit'], 0)}). "
              f"Repariert bekäme T04 eine Empfehlung, also eine Freigabe: {pct(e['anteil_t04_an_autonom'], 1)} der autonomen "
              f"Tickets ({pct(verschoben, 1)} aller Tickets) wandern von autonom zu Freigabe.\n")
    md.append("| Variante | Freigabe | Nacharbeit | Nacharbeit je Ticket | Freigabe je Ticket | mit Agent je Ticket | Monat mit Agent | **Ersparnis gegenüber heute / Monat** |")
    md.append("|---|---|---|---|---|---|---|---|")
    for name, e_ in varianten:
        p = je_ticket(e_, m)
        md.append(f"| {name} | {pct(e_['anteil_freigabe'], 1)} | {pct(e_['anteil_nacharbeit'], 1)} | {eur(p['nacharbeit'], 4)} | "
                  f"{eur(p['freigabe'], 4)} | {eur(p['mit_agent'], 4)} | {eur(p['mit_agent'] * m)} | "
                  f"**{eur((vorher['mit_agent'] - p['mit_agent']) * m)}** |")
    md.append("\nDie Erstattungen selbst sind nicht eingerechnet: Auf sie hat die Kundin Anspruch, ein Mensch ohne Agent "
              "würde sie ebenso auszahlen. Basis sind 29 autonome Goldset-Läufe, das ist eine Größenordnung, keine Prognose.")

    md.append("\n## Option „Doppelbuchung automatisch erstatten“: Erwartungswert je Fall\n")
    e = eingaben("mittel")
    gespart = e["min_freigabe"] * e["eur_je_minute"] + e["tok_antwort"] / e["usd_je_eur"]
    md.append(f"Gespart je Fall: {eur(e['min_freigabe'], 0)} min Freigabe × {eur(e['eur_je_minute'], 4)} EUR/min "
              f"+ Haiku-Antwort {eur(e['tok_antwort'] / e['usd_je_eur'], 4)} EUR = **{eur(gespart, 4)} EUR**. "
              "Erwarteter Verlust je Fall: Fehlerquote × Betrag. Netto = gespart − Verlust.\n")
    md.append("| Fehlerquote | Verlust bei 6,99 EUR | Netto bei 6,99 EUR | Verlust bei 59 EUR | Netto bei 59 EUR |\n|---|---|---|---|---|")
    for f in [wert("fehlerquote_auto", s) for s in ("niedrig", "mittel", "hoch")]:
        v1, v2 = f * wert("betrag_auto", "niedrig"), f * wert("betrag_auto", "hoch")
        md.append(f"| {pct(f, 1)} | {eur(v1, 4)} | {eur(gespart - v1, 4)} | {eur(v2, 4)} | {eur(gespart - v2, 4)} |")
    md.append("\nGewinnschwelle (Fehlerquote, bei der Netto = 0), je nach Minuten je Freigabe:\n")
    md.append("| min/Freigabe | gespart je Fall | Schwelle bei 6,99 EUR | Schwelle bei 59 EUR |\n|---|---|---|---|")
    for mf in [wert("min_freigabe", s) for s in ("niedrig", "mittel", "hoch")]:
        g = mf * e["eur_je_minute"] + e["tok_antwort"] / e["usd_je_eur"]
        md.append(f"| {eur(mf, 0)} | {eur(g, 4)} | {pct(g / wert('betrag_auto', 'niedrig'), 1)} | {pct(g / wert('betrag_auto', 'hoch'), 1)} |")

    md.append("\n### Wie viele fehlerfreie Fälle braucht „automatisch bis X EUR“? (Dreierregel)\n")
    md.append("Schwelle = gespart je Fall / X (der ungünstigste Betrag unter der Grenze). Nach der Dreierregel belegen n Fälle "
              "ohne Fehler eine Fehlerquote unter 3/n (95 %). Gebraucht werden also n = 3 / Schwelle fehlerfreie Fälle, "
              "aufgerundet. Bisher gemessen: 6 Doppelbuchungs-Läufe ohne falsche Erstattung (UC6 T01, T02), das belegt nur < 50 %.\n")
    kopf = " / ".join(eur(wert("min_freigabe", s), 0) for s in ("niedrig", "mittel", "hoch"))
    md.append(f"| Grenze X | Schwelle (2 min) | **n fehlerfrei (2 min)** | n bei {kopf} min je Freigabe |\n|---|---|---|---|")
    for x in BETRAGSGRENZEN:
        ns = []
        for mf in [wert("min_freigabe", s) for s in ("niedrig", "mittel", "hoch")]:
            g = mf * e["eur_je_minute"] + e["tok_antwort"] / e["usd_je_eur"]
            ns.append(str(math.ceil(3 / (g / x))))
        md.append(f"| bis {eur(x, 0)} EUR | {pct(gespart / x, 1)} | **{math.ceil(3 / (gespart / x))}** | {' / '.join(ns)} |")

    (HIER / "evals").mkdir(exist_ok=True)
    with open(HIER / "evals" / "modell_ergebnisse.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(zeilen[0].keys()))
        w.writeheader(); w.writerows(zeilen)
    (HIER / "evals" / "modell.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HIER / "docs" / "kipppunkt.svg").write_text(diagramm(10_000) + "\n", encoding="utf-8")
    (HIER / "docs" / "tornado.svg").write_text(tornado(TORNADO_MENGE) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
