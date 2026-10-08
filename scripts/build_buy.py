"""Build vs. Buy aus Käufer-Sicht (FocusFlow): A selbst betreiben, B Intercom Fin, C unser Produkt, D nur Klassifikation.

    python3 scripts/build_buy.py

Schreibt evals/build_buy.md, evals/build_buy_ergebnisse.csv, docs/build_buy_kosten.svg und docs/build_buy_differenz.svg.
Rechenweg A gegen C bei 10.000 Tickets: docs/RECHENWEG_BUILD_BUY.md.

Nur entscheidungsrelevante Kosten: Menschliche Grundlast, die in jeder Option gleich ist (Teamleitung, Helpdesk-Lizenzen
für Menschen, Schulung), fehlt. Gezählt werden die Minuten, die Menschen je Option an Tickets arbeiten, weil sie sich
zwischen den Optionen unterscheiden (Übergaben, Freigaben, Nacharbeit, bei D alle Tickets).
"""
import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from modell import eingaben, eur, je_ticket, pct, wert  # noqa: E402

HIER = Path(__file__).resolve().parent.parent
MENGEN = [1_000, 2_000, 3_000, 5_000, 7_500, 10_000, 15_000, 20_000, 30_000, 50_000, 75_000, 100_000]
OPTIONEN = {"A": "A selbst betreiben", "B": "B Intercom Fin", "C": "C unser Produkt", "D": "D nur Klassifikation"}
TCO = ["tco_goldset_h", "tco_judge_h", "tco_sicherheit_h", "tco_betrieb_h", "tco_modellupdate_h", "tco_datenschutz_h",
       "tco_regeln_h"]
FARBEN = {"A": ("#2a78d6", "#3987e5"), "B": ("#eb6834", "#d95926"), "C": ("#1baf7a", "#199e70"), "D": ("#eda100", "#c98500")}


def basis(stufe_tco: str = "mittel") -> dict:
    e = eingaben("mittel")
    for t in TCO:
        e[t] = wert(t, stufe_tco)
    return e


def personal(e: dict, menge: int, uebergabe=None) -> float:
    """Minuten, die Menschen mit Agent an Tickets arbeiten, in EUR (Freigabe, Übergabe, Nacharbeit)."""
    p = je_ticket({**e, "anteil_uebergabe": e["anteil_uebergabe"] if uebergabe is None else uebergabe}, menge)
    return (p["freigabe"] + p["uebergabe"] + p["nacharbeit"]) * menge


def kosten(e: dict, menge: int) -> dict:
    """Kosten je Monat in EUR je Option, aufgeteilt in Technik/Gebühren, interner Aufwand und Personal an Tickets."""
    kurs, satz = e["usd_je_eur"], e["stundensatz_intern"]
    p = je_ticket(e, menge)
    out = {}
    # A: selbst betreiben
    tco_h = sum(e[t] for t in TCO)
    bau_h = e["bau_tage"] * e["bau_h_je_tag"] * e["faktor_produktion"]
    out["A"] = {"technik": menge * (p["tokens"] + p["hosting_variabel"]) + e["hosting_fix"] + e["neon_fix"],
                "intern": tco_h * satz + bau_h * satz / e["abschreibung_monate"],
                "personal": personal(e, menge), "tco_h": tco_h, "bau_h": bau_h}
    # B: Fin neben dem eigenen Helpdesk
    q_u = e["fin_uebergabe"]
    outcomes = menge * ((1 - q_u) + q_u * e["fin_anteil_handoff_berechnet"])
    out["B"] = {"technik": max(outcomes, e["fin_mindest_outcomes"]) * e["fin_preis"] / kurs,
                "intern": e["b_laufend_h"] * satz + e["b_einrichtung_h"] * satz / e["abschreibung_monate"],
                "personal": personal(e, menge, q_u), "outcomes": outcomes}
    # C: unser Produkt
    autonom = 1 - e["anteil_freigabe"] - e["anteil_uebergabe"]
    geloest = menge * (e["anteil_freigabe"] + autonom * (1 - e["anteil_nacharbeit"]))
    out["C"] = {"technik": e["grundgebuehr"] + e["preis_geloest"] * geloest,
                "intern": e["c_laufend_h"] * satz + e["c_einrichtung_h"] * satz / e["abschreibung_monate"],
                "personal": personal(e, menge), "geloest": geloest}
    # D: nur Klassifikation, Menschen bearbeiten jedes Ticket
    out["D"] = {"technik": menge * e["d_klassifikation"] / kurs,
                "intern": e["d_betrieb_h"] * satz,
                "personal": menge * (e["min_ohne_agent"] - e["d_triage_min"]) * e["eur_je_minute"]}
    for o in out.values():
        o["gesamt"] = o["technik"] + o["intern"] + o["personal"]
    return out


def kipppunkt(e: dict, a: str, b: str) -> float:
    """Menge, ab der Option a günstiger ist als b (Kosten linear in der Menge, außer Fin-Mindestabnahme)."""
    lo, hi = 50, 1_000_000
    d = lambda m: kosten(e, m)[a]["gesamt"] - kosten(e, m)[b]["gesamt"]
    if d(lo) <= 0:
        return lo
    if d(hi) > 0:
        return math.inf
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if d(mid) > 0 else (lo, mid)
    return hi


# ---------- Diagramme ----------

def _svg_kopf(B, H, aria, farben):
    css = [":root{--bg:#fcfcfb;--t1:#0b0b0b;--t2:#52514e;--grid:#e6e5e1;--zero:#8a8984;"]
    css += [f"--{k}:{h};" for k, (h, _) in farben.items()]
    css += ["}@media (prefers-color-scheme: dark){:root{--bg:#1a1a19;--t1:#ffffff;--t2:#c3c2b7;--grid:#34332f;"]
    css += [f"--{k}:{d};" for k, (_, d) in farben.items()]
    css += ["}}"]
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {B} {H}" width="{B}" height="{H}" '
            f'font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif" role="img" aria-label="{aria}">',
            f"<style>{''.join(css)} text{{fill:var(--t2);font-size:12px}} .t1{{fill:var(--t1)}}</style>",
            f'<rect width="{B}" height="{H}" fill="var(--bg)"/>']


def linien_svg(titel, untertitel, reihen, ymin, ymax, ytick, yfmt, aria, legende, marker=(), nulllinie=False):
    """reihen: {key: (label, [(menge, wert)])}; x logarithmisch 1.000–100.000."""
    B, H = 760, 500
    L, R, O, U = 84, 150, 104, 64
    lx0, lx1 = math.log10(1_000), math.log10(100_000)
    def X(m): return L + (math.log10(m) - lx0) / (lx1 - lx0) * (B - L - R)
    def Y(v): return O + (ymax - v) / (ymax - ymin) * (H - O - U)
    s = _svg_kopf(B, H, aria, {k: FARBEN[k[-1]] for k in reihen})
    s.append(f'<text x="24" y="26" class="t1" font-size="16" font-weight="600">{titel}</text>')
    s.append(f'<text x="24" y="46">{untertitel}</text>')
    lx = 24
    for k, (label, _) in reihen.items():
        s.append(f'<line x1="{lx}" y1="70" x2="{lx + 22}" y2="70" stroke="var(--{k})" stroke-width="2"/>'
                 f'<text x="{lx + 28}" y="74">{label}</text>')
        lx += legende
    v = ymin
    while v <= ymax + 1e-9:
        stroke = "var(--zero)" if (nulllinie and abs(v) < 1e-9) else "var(--grid)"
        s.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{B - R}" y2="{Y(v):.1f}" stroke="{stroke}"/>')
        s.append(f'<text x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end">{yfmt(v)}</text>')
        v += ytick
    for m in [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000]:
        s.append(f'<line x1="{X(m):.1f}" y1="{O}" x2="{X(m):.1f}" y2="{H - U}" stroke="var(--grid)"/>')
        s.append(f'<text x="{X(m):.1f}" y="{H - U + 18}" text-anchor="middle">{eur(m, 0)}</text>')
    s.append(f'<text x="{(L + B - R) / 2:.0f}" y="{H - U + 40}" text-anchor="middle">Tickets je Monat (logarithmisch)</text>')
    ends = []
    for k, (label, pts) in reihen.items():
        s.append(f'<polyline fill="none" stroke="var(--{k})" stroke-width="2" stroke-linejoin="round" points="'
                 + " ".join(f"{X(m):.1f},{Y(min(max(v, ymin), ymax)):.1f}" for m, v in pts) + '"/>')
        for m, v in pts:
            if ymin <= v <= ymax:
                s.append(f'<circle cx="{X(m):.1f}" cy="{Y(v):.1f}" r="7" fill="transparent">'
                         f'<title>{label}, {eur(m, 0)} Tickets: {eur(v, 0)} EUR</title></circle>')
        ends.append((Y(min(max(pts[-1][1], ymin), ymax)), label, k))
    unten = H - U - 4
    for y, label, k in sorted(ends, reverse=True):
        y = min(y, unten); unten = y - 16
        s.append(f'<text x="{B - R + 8}" y="{y + 4:.1f}" class="t1">{label}</text>')
    for m, v, text in marker:
        s.append(f'<circle cx="{X(m):.1f}" cy="{Y(v):.1f}" r="5" fill="var(--bg)" stroke="var(--t1)" stroke-width="2">'
                 f'<title>{text}</title></circle>')
        s.append(f'<text x="{X(m):.1f}" y="{Y(v) - 10:.1f}" text-anchor="middle" class="t1">{text}</text>')
    s.append("</svg>")
    return "\n".join(s)


# ---------- main ----------

def main():
    e = basis()
    md = ["# Build vs. Buy aus Käufer-Sicht (FocusFlow)\n",
          "Erzeugt von `scripts/build_buy.py` aus `data/annahmen.csv`. Alle Annahmen auf „mittel“, Kundentyp mittel "
          "(8 min ohne Agent, 0,4420 EUR/min). Nur entscheidungsrelevante Kosten: Menschliche Grundlast, die in jeder Option "
          "gleich ist, fehlt; die Minuten an Tickets unterscheiden sich je Option und sind drin. "
          "Rechenweg: [docs/RECHENWEG_BUILD_BUY.md](../docs/RECHENWEG_BUILD_BUY.md).\n"]

    md.append("## TCO für A: laufender Aufwand in Stunden je Monat (Annahmen)\n")
    md.append("| Aufgabe | aus | niedrig | mittel | hoch |\n|---|---|---|---|---|")
    herkunft = {"tco_goldset_h": "UC2, UC4", "tco_judge_h": "UC7", "tco_sicherheit_h": "UC6", "tco_betrieb_h": "UC7",
                "tco_modellupdate_h": "UC4, UC6", "tco_datenschutz_h": "UC7", "tco_regeln_h": "UC4, UC6"}
    beschr = {r["id"]: r["beschreibung"] for r in csv.DictReader(open(HIER / "data" / "annahmen.csv", encoding="utf-8"))}
    summe = {s: 0 for s in ("niedrig", "mittel", "hoch")}
    for t in TCO:
        md.append(f"| {beschr[t]} | {herkunft[t]} | " + " | ".join(eur(wert(t, s), 0) for s in summe) + " |")
        for s in summe:
            summe[s] += wert(t, s)
    md.append("| **Summe** | | " + " | ".join(f"**{eur(v, 0)}**" for v in summe.values()) + " |")
    md.append(f"\nZum Stundensatz von {eur(e['stundensatz_intern'])} EUR: {eur(summe['mittel'] * e['stundensatz_intern'], 0)} EUR je Monat (mittel), "
              f"Spanne {eur(summe['niedrig'] * e['stundensatz_intern'], 0)} bis {eur(summe['hoch'] * e['stundensatz_intern'], 0)} EUR.\n")

    k10 = kosten(e, 10_000)
    md.append("## Eigene Bauzeit (grobe Näherung aus der Git-Historie)\n")
    md.append("| Repo | Zeitraum | Commits ohne Merges | aktive Tage (mit Commit) |\n|---|---|---|---|")
    md += ["| UC4 Agents/MCP | 24.09.–30.09.2026 | 8 | 2 |", "| UC6 Prompt Injection | 02.10.–08.10.2026 | 15 | 2 |",
           "| UC7 Deployment | 28.09.–02.10.2026 | 28 | 4 |", "| **Summe** | 24.09.–08.10.2026 | **51** | **8** |"]
    md.append(f"\n{eur(e['bau_tage'], 0)} Tage × {eur(e['bau_h_je_tag'], 0)} h × Faktor {eur(e['faktor_produktion'], 0)} (Demo → Produktion) "
              f"= **{eur(k10['A']['bau_h'], 0)} h**, auf {eur(e['abschreibung_monate'], 0)} Monate verteilt "
              f"{eur(k10['A']['bau_h'] * e['stundensatz_intern'] / e['abschreibung_monate'], 0)} EUR je Monat. "
              "Ausdrücklich grob: Commits sind gebündelt (UC4: 7 von 8 Commits an einem Tag), Arbeit ohne Commit fehlt, "
              "und gebaut hat eine Person mit Claude Code an erfundenen Kundendaten. UC5 (Text-to-SQL) ist kein Agent und "
              "nicht gezählt.\n")

    md.append("## Kosten je Monat bei 10.000 Tickets (EUR)\n")
    md.append("| Option | Technik und Gebühren | interner Aufwand | Personal an Tickets | **gesamt** |\n|---|---|---|---|---|")
    for o, name in OPTIONEN.items():
        z = k10[o]
        md.append(f"| {name} | {eur(z['technik'])} | {eur(z['intern'])} | {eur(z['personal'])} | **{eur(z['gesamt'])}** |")
    md.append(f"\nB: {eur(k10['B']['outcomes'], 0)} Outcomes (alle nicht übergebenen Tickets, weil Fin auch „assumed resolutions“ "
              f"abrechnet, plus {pct(e['fin_anteil_handoff_berechnet'])} der Übergaben als Procedure Handoff), "
              f"Übergabequote {pct(e['fin_uebergabe'])} als Annahme. C: {eur(k10['C']['geloest'], 0)} gelöste Tickets.\n")

    md.append("## Kipppunkt nach Volumen\n")
    zeilen_csv = []
    for m in MENGEN:
        k = kosten(e, m)
        zeilen_csv.append({"tickets": m, **{f"{o}_gesamt": round(k[o]["gesamt"], 2) for o in OPTIONEN},
                           **{f"{o}_ohne_personal": round(k[o]["technik"] + k[o]["intern"], 2) for o in OPTIONEN}})
    md.append("| Tickets je Monat | " + " | ".join(OPTIONEN.values()) + " | günstigste |\n|---|---|---|---|---|---|")
    for z in zeilen_csv:
        best = min(OPTIONEN, key=lambda o: z[f"{o}_gesamt"])
        md.append(f"| {eur(z['tickets'], 0)} | " + " | ".join(eur(z[f'{o}_gesamt'], 0) for o in OPTIONEN) + f" | {best} |")
    kab, kac = kipppunkt(e, "A", "B"), kipppunkt(e, "A", "C")
    md.append(f"\n**A wird günstiger als B ab {eur(kab, 0)} Tickets je Monat, günstiger als C ab {eur(kac, 0)} Tickets je Monat.** "
              "Die Personal-Minuten sind bei A und C gleich (derselbe Agent), bei B nur unter der Annahme gleicher Übergabequote. "
              "Der Kipppunkt entsteht deshalb aus Fixkosten (Betrieb von A) gegen Stückpreis (B, C).\n")
    md.append("Wie stark der Kipppunkt am TCO von A hängt:\n")
    md.append("| TCO-Stunden für A | Stunden je Monat | A günstiger als B ab | A günstiger als C ab |\n|---|---|---|---|")
    for s in ("niedrig", "mittel", "hoch"):
        es = basis(s)
        md.append(f"| {s} | {eur(summe[s], 0)} | {eur(kipppunkt(es, 'A', 'B'), 0)} | {eur(kipppunkt(es, 'A', 'C'), 0)} |")
    eb = {**e, "fin_uebergabe": wert("fin_uebergabe", "niedrig")}
    eb2 = {**e, "fin_uebergabe": wert("fin_uebergabe", "hoch")}
    md.append(f"\nFins Übergabequote (Annahme) verschiebt A gegen B stark, weil jede Übergabe Menschenzeit kostet: "
              f"Bei {pct(wert('fin_uebergabe', 'niedrig'))} statt 30 % ist A erst ab {eur(kipppunkt(eb, 'A', 'B'), 0)} Tickets günstiger, "
              f"bei {pct(wert('fin_uebergabe', 'hoch'))} schon ab {eur(kipppunkt(eb2, 'A', 'B'), 0)}.\n")

    md.append("## Qualitative Kriterien\n")
    md += ["| Kriterium | A selbst betreiben | B Intercom Fin | C unser Produkt | D nur Klassifikation |",
           "|---|---|---|---|---|",
           "| Kontrolle | Voll: Prompt, Regeln im Code, Judge, Schwellen und Freigaben selbst festgelegt | Gering bis mittel: Verhalten über Inhalte, Prozeduren und Einstellungen steuerbar, das Modell nicht | Mittel: Regeln und Freigabe-Schwellen vertraglich, Umsetzung bei uns | Voll, es gibt aber wenig zu steuern |",
           "| Daten verlassen das Haus | Ja, an Anthropic (Modell) und den gewählten Hoster (UC7: Google Frankfurt, Neon Frankfurt) | Ja, an Intercom und dessen Modellanbieter; Speicherort laut Intercom-Vertrag | Ja, an uns, Anthropic und unsere Hoster | Ja, nur der Tickettext an Anthropic für die Klassifikation |",
           "| Anpassbarkeit | Beliebig, jede Änderung braucht aber Goldset, Judge und Sicherheitstests (UC2, UC6, UC7) | Innerhalb dessen, was Fin anbietet | Über uns, Wünsche konkurrieren mit anderen Kunden | Kategorien frei, sonst nichts |",
           "| Abhängigkeit vom Anbieter | Vom Modellanbieter (Modell- und SDK-Wechsel, siehe UC6 T04) und vom eigenen Team | Von Intercom (Preis, Outcome-Definition, Plattform) | Von uns als kleinem Anbieter (Fortbestand, Preis nach Pilot) | Gering |",
           "| Zeit bis zum Start | Lang: Bau, Evals, Sicherheit, Betrieb (bei uns 8 aktive Tage für die Demo, Produktion mehr) | Kurz, wenn die Inhalte da sind; Prozeduren für Erstattungen brauchen Einrichtung | Kurz bis mittel: Einrichtung durch uns, Pilot im Schattenmodus | Sehr kurz (UC1 an einem Tag) |"]

    (HIER / "evals" / "build_buy.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    with open(HIER / "evals" / "build_buy_ergebnisse.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(zeilen_csv[0].keys()))
        w.writeheader(); w.writerows(zeilen_csv)

    mengen = sorted(set(MENGEN + [round(10 ** (3 + i / 20)) for i in range(41)]))
    reihen = {o: (OPTIONEN[o], [(m, kosten(e, m)[o]["gesamt"] / 1000) for m in mengen]) for o in OPTIONEN}
    (HIER / "docs" / "build_buy_kosten.svg").write_text(linien_svg(
        "Gesamtkosten je Monat nach Volumen",
        "Tausend EUR je Monat, entscheidungsrelevante Kosten inklusive Personal an Tickets. Alle Annahmen auf „mittel“.",
        reihen, 0, 360, 40, lambda v: eur(v, 0), "Gesamtkosten je Monat für die Optionen A bis D über der Ticketmenge",
        150) + "\n", encoding="utf-8")
    diff = {"AB": ("A minus B", [(m, kosten(e, m)["A"]["gesamt"] - kosten(e, m)["B"]["gesamt"]) for m in mengen]),
            "AC": ("A minus C", [(m, kosten(e, m)["A"]["gesamt"] - kosten(e, m)["C"]["gesamt"]) for m in mengen])}
    FARBEN["AB"], FARBEN["AC"] = FARBEN["B"], FARBEN["C"]
    lo = min(v for _, pts in diff.values() for _, v in pts)
    hi = max(v for _, pts in diff.values() for _, v in pts)
    ymin, ymax = math.floor(lo / 10_000) * 10_000, math.ceil(hi / 10_000) * 10_000
    (HIER / "docs" / "build_buy_differenz.svg").write_text(linien_svg(
        "Selbst betreiben (A) gegen Kaufen (B, C)",
        "EUR je Monat. Über 0: A ist teurer. Unter 0: A ist günstiger. Ring = Kipppunkt.",
        diff, ymin, ymax, 10_000, lambda v: eur(v, 0), "Kostendifferenz A minus B und A minus C über der Ticketmenge",
        130, marker=[(kab, 0, f"{eur(kab, 0)}"), (kac, 0, f"{eur(kac, 0)}")], nulllinie=True) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
