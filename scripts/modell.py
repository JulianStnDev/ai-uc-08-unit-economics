"""Kostenmodell UC8: Kosten pro Ticket und pro Monat, ohne Agent gegen mit Agent. Ohne API, nur data/annahmen.csv.

    python3 scripts/modell.py

Schreibt evals/modell_ergebnisse.csv, evals/modell.md und docs/kipppunkt.svg.
Rechenweg von Hand für ein Szenario: docs/RECHENWEG.md.

Tokens und Cloud-Run-Preise sind in USD und werden einmal mit usd_je_eur umgerechnet, Personal ist in EUR.
Szenarien variieren nur Anteile (Freigabe, Übergabe) und Minuten je Eingriff. Alle anderen Eingaben stehen auf „mittel“.
"""
import csv
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
MENGEN = [1_000, 10_000, 100_000]
SZENARIEN = {"optimistisch": "niedrig", "mittel": "mittel", "pessimistisch": "hoch"}
SZENARIO_PARAMETER = ["anteil_freigabe", "anteil_uebergabe", "min_freigabe", "min_uebergabe"]


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
    p = {
        "tokens": tokens_usd / kurs,
        "hosting_variabel": hosting_usd / kurs,
        "freigabe": e["anteil_freigabe"] * e["min_freigabe"] * e["eur_je_minute"],
        "uebergabe": e["anteil_uebergabe"] * e["min_uebergabe"] * e["eur_je_minute"],
        "fix": (e["hosting_fix"] + e["neon_fix"]) / menge,
    }
    p["variabel"] = p["tokens"] + p["hosting_variabel"] + p["freigabe"] + p["uebergabe"]
    p["mit_agent"] = p["variabel"] + p["fix"]
    p["ohne_agent"] = e["min_ohne_agent"] * e["eur_je_minute"]
    p["ersparnis"] = p["ohne_agent"] - p["mit_agent"]
    return p


def kipppunkt(e: dict, menge: int, min_ohne=None) -> float:
    """Übergabequote, ab der mit Agent nicht mehr günstiger ist (Ersparnis = 0). Freigabe-Anteil bleibt fest."""
    p = je_ticket({**e, "anteil_uebergabe": 0.0}, menge)
    ohne = (min_ohne if min_ohne is not None else e["min_ohne_agent"]) * e["eur_je_minute"]
    return (ohne - p["mit_agent"]) / (e["min_uebergabe"] * e["eur_je_minute"])


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
        # Direktes Label am Linienende
        y_end = Y(pts[-1][1])
        while any(abs(y_end - y) < 15 for y in label_y):
            y_end += 15
        label_y.append(y_end)
        rest = "kein Kipppunkt" if k > qmax else f"Kipppunkt {pct(k)}"
        s.append(f'<text x="{X(qmax) + 8:.1f}" y="{y_end + 4:.1f}" class="t1">{n}</text>')
        s.append(f'<text x="{X(qmax) + 8:.1f}" y="{y_end + 18:.1f}" font-size="11">{rest}</text>')
    s.append(f'<text x="{L}" y="{H - 10}" font-size="11">Punkt = Übergabequote des Szenarios, Ring = Kipppunkt. '
             f'Linien enden bei 100 % minus Freigabe-Anteil.</text>')
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
    md.append("| Szenario | Freigabe | Übergabe | min/Freigabe | min/Übergabe |\n|---|---|---|---|---|")
    for n in SZENARIEN:
        e = eingaben(n)
        md.append(f"| {n} | {pct(e['anteil_freigabe'])} | {pct(e['anteil_uebergabe'])} | {eur(e['min_freigabe'], 0)} | {eur(e['min_uebergabe'], 0)} |")

    md.append("\n## Kosten je Ticket (EUR)\n")
    md.append("| Szenario | Tickets/Monat | Tokens | Hosting variabel | Freigabe | Übergabe | **variabel** | Fix je Ticket | **mit Agent** | **ohne Agent** | **Ersparnis** |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for n in SZENARIEN:
        e = eingaben(n)
        for m in MENGEN:
            p = je_ticket(e, m)
            roh.append((n, m, p))
            zeilen.append({"szenario": n, "tickets_monat": m, **{k: round(v, 6) for k, v in p.items()},
                           "mit_agent_monat": round(p["mit_agent"] * m, 2), "ohne_agent_monat": round(p["ohne_agent"] * m, 2),
                           "ersparnis_monat": round(p["ersparnis"] * m, 2), "kipppunkt_uebergabe": round(kipppunkt(e, m), 4)})
            md.append(f"| {n} | {eur(m, 0)} | {eur(p['tokens'], 4)} | {eur(p['hosting_variabel'], 4)} | {eur(p['freigabe'], 4)} | "
                      f"{eur(p['uebergabe'], 4)} | **{eur(p['variabel'], 4)}** | {eur(p['fix'], 4)} | **{eur(p['mit_agent'], 4)}** | "
                      f"**{eur(p['ohne_agent'], 4)}** | **{eur(p['ersparnis'], 4)}** |")

    md.append("\n## Kosten je Monat (EUR)\n")
    md.append("| Szenario | Tickets/Monat | ohne Agent | mit Agent | davon variabel | davon fix | Ersparnis | Ersparnis in % |")
    md.append("|---|---|---|---|---|---|---|---|")
    for n, m, p in roh:
        md.append(f"| {n} | {eur(m, 0)} | {eur(p['ohne_agent'] * m)} | {eur(p['mit_agent'] * m)} | "
                  f"{eur(p['variabel'] * m)} | {eur(p['fix'] * m)} | {eur(p['ersparnis'] * m)} | {pct(p['ersparnis'] / p['ohne_agent'], 1)} |")

    md.append("\n## Kipppunkt: Übergabequote, ab der der Agent nicht mehr günstiger ist\n")
    md.append("Freigabe-Anteil und Minuten bleiben je Szenario fest, nur die Übergabequote wandert. Möglich sind höchstens "
              "100 % minus Freigabe-Anteil. 10.000 Tickets/Monat.\n")
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
              "wie wenige Sekunden Arbeitszeit. Entscheidend ist das Verhältnis Minuten je Übergabe zu Minuten ohne Agent.")

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

    (HIER / "evals").mkdir(exist_ok=True)
    with open(HIER / "evals" / "modell_ergebnisse.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(zeilen[0].keys()))
        w.writeheader(); w.writerows(zeilen)
    (HIER / "evals" / "modell.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (HIER / "docs" / "kipppunkt.svg").write_text(diagramm(10_000) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
