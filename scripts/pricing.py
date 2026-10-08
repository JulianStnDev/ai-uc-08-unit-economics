"""Pricing aus Anbieter-Sicht: Preiskorridor je Kundentyp und Abrechnungsart. Ohne API, nur data/annahmen.csv.

    python3 scripts/pricing.py

Schreibt evals/pricing.md, evals/pricing_ergebnisse.csv und docs/korridor.svg. Rechenweg: docs/RECHENWEG_PRICING.md.

Untergrenze = unsere Vollkosten × (1 + Marge). Obergrenze = (1 − Mindestanteil Kunde) × Brutto-Ersparnis des Kunden.
Brutto-Ersparnis = Kosten ohne Agent − Personalkosten mit Agent (Freigabe, Übergabe, Nacharbeit). Tokens und Hosting
trägt jetzt der Anbieter, der Kunde zahlt stattdessen den Preis.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from modell import eingaben, eur, je_ticket, pct, wert  # noqa: E402

HIER = Path(__file__).resolve().parent.parent
MENGE = 10_000
KUNDENTYPEN = {  # Hebel aus dem Tornado: Minuten ohne Agent, alles andere auf „mittel“
    "günstig": wert("min_ohne_agent", "niedrig"),
    "mittel": wert("min_ohne_agent", "mittel"),
    "teuer": wert("min_ohne_agent", "hoch"),
}
ABRECHNUNG = ["pro Sitz", "pro Ticket", "pro gelöstem Ticket"]


def kunde(min_ohne: float) -> dict:
    return {**eingaben("mittel"), "min_ohne_agent": min_ohne}


def rechnung(e: dict, menge: int = MENGE) -> dict:
    p = je_ticket(e, menge)
    r = {"min_ohne_agent": e["min_ohne_agent"], "tickets": menge}
    r["ohne_agent_ticket"] = p["ohne_agent"]
    r["personal_mit_ticket"] = p["freigabe"] + p["uebergabe"] + p["nacharbeit"]
    r["brutto_ersparnis_ticket"] = r["ohne_agent_ticket"] - r["personal_mit_ticket"]
    # Anbieter: Vollkosten je Monat
    r["variabel_monat"] = menge * (p["tokens"] + p["hosting_variabel"])
    r["hosting_fix_monat"] = e["hosting_fix"] + e["neon_fix"]
    r["einrichtung_monat"] = e["einrichtung_h"] * e["stundensatz_anbieter"] / e["verteilung_monate"]
    r["kundensupport_monat"] = e["kundensupport_h"] * e["stundensatz_anbieter"]
    r["vollkosten_monat"] = r["variabel_monat"] + r["hosting_fix_monat"] + r["einrichtung_monat"] + r["kundensupport_monat"]
    r["untergrenze_monat"] = r["vollkosten_monat"] * (1 + e["marge"])
    r["obergrenze_monat"] = (1 - e["anteil_kunde_min"]) * r["brutto_ersparnis_ticket"] * menge
    # Mengen je Abrechnungsart
    fte_min = e["stunden_jahr"] / 12 * 60
    autonom = 1 - e["anteil_freigabe"] - e["anteil_uebergabe"]
    r["geloest_anteil"] = e["anteil_freigabe"] + autonom * (1 - e["anteil_nacharbeit"])
    r["einheiten"] = {"pro Sitz": menge * e["min_ohne_agent"] / fte_min,
                      "pro Ticket": menge,
                      "pro gelöstem Ticket": menge * r["geloest_anteil"]}
    r["stellen_mit_agent"] = menge * r["personal_mit_ticket"] / e["eur_je_minute"] / fte_min
    # Wettbewerb: Fin, einmal nur Lösungen, einmal zusätzlich jede Übergabe als Procedure Handoff
    r["fin_eur"] = e["fin_preis"] / e["usd_je_eur"]
    r["fin_nur_loesung_monat"] = r["fin_eur"] * menge * r["geloest_anteil"]
    r["fin_mit_uebergabe_monat"] = r["fin_eur"] * menge * (r["geloest_anteil"] + e["anteil_uebergabe"])
    return r


def erosion(e: dict, r: dict) -> list:
    """Pro Sitz: Jahr 1 gegen Jahr 2 mit abbau_jahr2 weniger Stellen. Einrichtung ist nach 12 Monaten bezahlt."""
    sitze1 = r["einheiten"]["pro Sitz"]
    sitze2 = sitze1 * (1 - e["abbau_jahr2"])
    kosten1 = r["vollkosten_monat"]
    kosten2 = kosten1 - r["einrichtung_monat"]
    zeilen = []
    for name, umsatz1 in [("Preis an der Untergrenze", r["untergrenze_monat"]),
                          ("Preis in der Mitte", (r["untergrenze_monat"] + r["obergrenze_monat"]) / 2),
                          ("Preis an der Obergrenze", r["obergrenze_monat"])]:
        preis = umsatz1 / sitze1
        umsatz2 = preis * sitze2
        zeilen.append({"preispunkt": name, "preis_sitz": preis, "sitze1": sitze1, "sitze2": sitze2,
                       "umsatz1": umsatz1, "umsatz2": umsatz2, "kosten1": kosten1, "kosten2": kosten2,
                       "marge1": umsatz1 / kosten1 - 1, "marge2": umsatz2 / kosten2 - 1,
                       "preis_sitz2_fuer_untergrenze": kosten2 * (1 + e["marge"]) / sitze2})
    return zeilen


# ---------- Diagramm ----------

def korridor_svg(daten: dict) -> str:
    B, zeile_h = 760, 74
    L, R, O = 160, 40, 112
    H = O + zeile_h * len(daten) + 74
    xmax = max(max(r["obergrenze_monat"], r["fin_mit_uebergabe_monat"]) for r in daten.values())
    xmax = (int(xmax / 5000) + 1) * 5000
    def X(v): return L + v / xmax * (B - L - R)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {B} {H}" width="{B}" height="{H}" '
         f'font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif" role="img" '
         f'aria-label="Preiskorridor je Kundentyp in EUR je Monat, mit Intercom Fin als Vergleich">']
    s.append("<style>:root{--bg:#fcfcfb;--t1:#0b0b0b;--t2:#52514e;--grid:#e6e5e1;--band:#2a78d6;--fin:#eb6834;}"
             "@media (prefers-color-scheme: dark){:root{--bg:#1a1a19;--t1:#ffffff;--t2:#c3c2b7;--grid:#34332f;"
             "--band:#3987e5;--fin:#d95926;}} text{fill:var(--t2);font-size:12px} .t1{fill:var(--t1)}</style>")
    s.append(f'<rect width="{B}" height="{H}" fill="var(--bg)"/>')
    s.append(f'<text x="24" y="26" class="t1" font-size="16" font-weight="600">Preiskorridor je Kundentyp</text>')
    s.append(f'<text x="24" y="46">EUR je Monat bei {eur(MENGE, 0)} Tickets. Links: Vollkosten + 20 % Marge. '
             f'Rechts: Kunde behält 50 % seiner Ersparnis.</text>')
    s.append(f'<text x="24" y="64">Bei fester Menge ist der Korridor für Sitz, Ticket und gelöstes Ticket derselbe Monatsbetrag.</text>')
    s.append(f'<rect x="24" y="78" width="22" height="10" rx="3" fill="var(--band)"/><text x="52" y="87">Korridor</text>')
    s.append(f'<circle cx="140" cy="83" r="5" fill="var(--fin)" stroke="var(--bg)" stroke-width="2"/>'
             f'<text x="150" y="87">Fin, nur Lösungen</text>')
    s.append(f'<circle cx="290" cy="83" r="5" fill="var(--bg)" stroke="var(--fin)" stroke-width="2"/>'
             f'<text x="300" y="87">Fin, zusätzlich jede Übergabe als Procedure Handoff</text>')
    for v in range(0, int(xmax) + 1, 5000):
        s.append(f'<line x1="{X(v):.1f}" y1="{O - 6}" x2="{X(v):.1f}" y2="{O + zeile_h * len(daten)}" stroke="var(--grid)"/>')
        s.append(f'<text x="{X(v):.1f}" y="{O + zeile_h * len(daten) + 18}" text-anchor="middle">{eur(v, 0)}</text>')
    s.append(f'<text x="{(L + B - R) / 2:.0f}" y="{O + zeile_h * len(daten) + 38}" text-anchor="middle">EUR je Monat</text>')
    for i, (typ, r) in enumerate(daten.items()):
        y = O + i * zeile_h
        s.append(f'<text x="{L - 12}" y="{y + 22}" text-anchor="end" class="t1">{typ}</text>')
        s.append(f'<text x="{L - 12}" y="{y + 37}" text-anchor="end" font-size="11">{eur(r["min_ohne_agent"], 1 if r["min_ohne_agent"] % 1 else 0)} min ohne Agent</text>')
        x0, x1 = X(r["untergrenze_monat"]), X(r["obergrenze_monat"])
        s.append(f'<rect x="{x0:.1f}" y="{y + 10}" width="{x1 - x0:.1f}" height="24" rx="4" fill="var(--band)">'
                 f'<title>{typ}: {eur(r["untergrenze_monat"], 0)} bis {eur(r["obergrenze_monat"], 0)} EUR je Monat</title></rect>')
        s.append(f'<text x="{x0:.1f}" y="{y + 50}" text-anchor="start">{eur(r["untergrenze_monat"], 0)}</text>')
        s.append(f'<text x="{x1:.1f}" y="{y + 50}" text-anchor="end">{eur(r["obergrenze_monat"], 0)}</text>')
        for v, gefuellt in [(r["fin_nur_loesung_monat"], True), (r["fin_mit_uebergabe_monat"], False)]:
            fill = "var(--fin)" if gefuellt else "var(--bg)"
            s.append(f'<circle cx="{X(v):.1f}" cy="{y + 22}" r="6" fill="{fill}" stroke="{"var(--bg)" if gefuellt else "var(--fin)"}" '
                     f'stroke-width="2"><title>Fin {"nur Lösungen" if gefuellt else "mit Übergaben"}: {eur(v, 0)} EUR je Monat</title></circle>')
    s.append(f'<text x="24" y="{H - 8}" font-size="11">Fin: 0,99 USD je Outcome (intercom.com, 08.10.2026), umgerechnet mit 1,1177 USD/EUR. '
             f'Quelle: scripts/pricing.py</text>')
    s.append("</svg>")
    return "\n".join(s)


# ---------- main ----------

def main():
    daten = {typ: rechnung(kunde(mo)) for typ, mo in KUNDENTYPEN.items()}
    e0 = kunde(wert("min_ohne_agent"))
    md = ["# Pricing: Preiskorridor je Kundentyp und Abrechnungsart\n",
          f"Erzeugt von `scripts/pricing.py` aus `data/annahmen.csv`. {eur(MENGE, 0)} Tickets je Kunde und Monat, alle Annahmen "
          "auf „mittel“ außer den Minuten ohne Agent (Hebel aus dem Tornado). Rechenweg: [docs/RECHENWEG_PRICING.md](../docs/RECHENWEG_PRICING.md).\n",
          "## Unsere Vollkosten je Kunde und Monat (EUR)\n",
          "| Posten | Rechnung | EUR je Monat |", "|---|---|---|"]
    r0 = daten["mittel"]
    md += [f"| Tokens + Hosting variabel | {eur(MENGE, 0)} × {eur(r0['variabel_monat'] / MENGE, 4)} | {eur(r0['variabel_monat'])} |",
           f"| Hosting fest | Abrechnung | {eur(r0['hosting_fix_monat'])} |",
           f"| Einrichtung | {eur(e0['einrichtung_h'], 0)} h × {eur(e0['stundensatz_anbieter'])} EUR / {eur(e0['verteilung_monate'], 0)} Monate | {eur(r0['einrichtung_monat'])} |",
           f"| Kundensupport | {eur(e0['kundensupport_h'], 0)} h × {eur(e0['stundensatz_anbieter'])} EUR | {eur(r0['kundensupport_monat'])} |",
           f"| **Vollkosten** | | **{eur(r0['vollkosten_monat'])}** |",
           f"| **Untergrenze** (× 1,2) | | **{eur(r0['untergrenze_monat'])}** |",
           f"\nDie Vollkosten sind für alle drei Kundentypen gleich (gleiche Ticketmenge). "
           f"{pct((r0['einrichtung_monat'] + r0['kundensupport_monat']) / r0['vollkosten_monat'])} davon sind Personal beim "
           f"Anbieter (Einrichtung und Kundensupport), {pct(r0['variabel_monat'] / r0['vollkosten_monat'])} Tokens und Hosting.\n"]

    md.append("## Kundentypen\n")
    md.append("| Kundentyp | min ohne Agent | Ersparnis je Ticket (Modell, nach Tokens) | Brutto-Ersparnis je Ticket (vor Preis) | Stellen ohne Agent | Stellen mit Agent nötig | gelöst-Anteil |")
    md.append("|---|---|---|---|---|---|---|")
    for typ, r in daten.items():
        p = je_ticket(kunde(r["min_ohne_agent"]), MENGE)
        md.append(f"| {typ} | {eur(r['min_ohne_agent'], 1)} | {eur(p['ersparnis'], 2)} | {eur(r['brutto_ersparnis_ticket'], 4)} | "
                  f"{eur(r['einheiten']['pro Sitz'], 2)} | {eur(r['stellen_mit_agent'], 2)} | {pct(r['geloest_anteil'], 1)} |")
    md.append("\nGelöst = ohne Übergabe und ohne Nacharbeit: Freigaben plus autonome Tickets ohne Nacharbeit "
              "(15 % + 55 % × 86 %). Stellen = Ticketminuten / 8.000 Minuten je Vollzeitstelle und Monat (1.600 h / 12).\n")

    md.append("## Preiskorridor (EUR)\n")
    md.append("| Kundentyp | Abrechnung | Einheiten je Monat | **Untergrenze je Einheit** | **Obergrenze je Einheit** | Untergrenze je Monat | Obergrenze je Monat |")
    md.append("|---|---|---|---|---|---|---|")
    csv_zeilen = []
    for typ, r in daten.items():
        for art in ABRECHNUNG:
            n = r["einheiten"][art]
            u, o = r["untergrenze_monat"] / n, r["obergrenze_monat"] / n
            st = 0 if art == "pro Sitz" else 2
            md.append(f"| {typ} | {art} | {eur(n, 2 if art == 'pro Sitz' else 0)} | **{eur(u, st)}** | **{eur(o, st)}** | {eur(r['untergrenze_monat'], 0)} | {eur(r['obergrenze_monat'], 0)} |")
            csv_zeilen.append({"kundentyp": typ, "abrechnung": art, "einheiten_monat": round(n, 2),
                               "untergrenze_einheit": round(u, 4), "obergrenze_einheit": round(o, 4),
                               "untergrenze_monat": round(r["untergrenze_monat"], 2), "obergrenze_monat": round(r["obergrenze_monat"], 2)})
    md.append("\nBei fester Menge ergeben alle drei Abrechnungsarten denselben Monatsbetrag. Sie unterscheiden sich darin, "
              "wer das Risiko trägt, wenn sich etwas ändert: Stellenabbau beim Kunden (pro Sitz), Ticketmenge (pro Ticket) "
              "oder Lösungsquote (pro gelöstem Ticket).\n")

    md.append("## Wettbewerb: Intercom Fin\n")
    md.append(f"Geprüft in der Primärquelle (intercom.com/pricing und Hilfeartikel „Fin AI Agent outcomes“, 08.10.2026): "
              f"**0,99 USD je Outcome** = {eur(r0['fin_eur'], 4)} EUR. Outcomes sind Lösungen **und** „Procedure Handoffs“ "
              "(Übergabe an einen Menschen über eine konfigurierte Prozedur), höchstens eines je Gespräch. Eine Lösung zählt "
              "auch „assumed“, wenn der Kunde ohne weitere Frage geht. Fins „gelöst“ ist also weiter gefasst als unseres "
              "(Nacharbeit-Fälle würden bei Fin oft als gelöst abgerechnet).\n")
    md.append("| Kundentyp | unser Korridor je gelöstem Ticket | Fin je Outcome | Fin je Monat, nur Lösungen | Fin je Monat, mit Übergaben | Lage von Fin im Korridor |")
    md.append("|---|---|---|---|---|---|")
    for typ, r in daten.items():
        n = r["einheiten"]["pro gelöstem Ticket"]
        u, o = r["untergrenze_monat"] / n, r["obergrenze_monat"] / n
        lage = "über der Obergrenze" if r["fin_eur"] > o else ("unter der Untergrenze" if r["fin_eur"] < u else
                                                              f"bei {pct((r['fin_eur'] - u) / (o - u))} des Korridors")
        md.append(f"| {typ} | {eur(u)} … {eur(o)} | {eur(r['fin_eur'])} | {eur(r['fin_nur_loesung_monat'], 0)} | "
                  f"{eur(r['fin_mit_uebergabe_monat'], 0)} | {lage} |")

    md.append("\n## Sitz-Erosion: Kunde baut im zweiten Jahr 30 % der Support-Stellen ab\n")
    md.append("Preis je Sitz im ersten Jahr so gesetzt, dass er den Monatsbetrag an Unter-, Mitte- oder Obergrenze trifft. "
              "Im zweiten Jahr ist die Einrichtung bezahlt, unsere Kosten sinken um diesen Anteil. Ticketmenge und damit "
              "Tokens bleiben gleich.\n")
    for typ, r in daten.items():
        e = kunde(r["min_ohne_agent"])
        md.append(f"**{typ}** ({eur(r['einheiten']['pro Sitz'], 2)} → {eur(r['einheiten']['pro Sitz'] * 0.7, 2)} Sitze; "
                  f"nötig mit Agent wären {eur(r['stellen_mit_agent'], 2)})\n")
        md.append("| Preispunkt | Preis je Sitz | Umsatz Jahr 1 / Monat | Umsatz Jahr 2 / Monat | Kosten Jahr 1 / Jahr 2 | Aufschlag auf Kosten Jahr 1 | Aufschlag Jahr 2 | Preis je Sitz, damit Jahr 2 die Untergrenze hält |")
        md.append("|---|---|---|---|---|---|---|---|")
        for z in erosion(e, r):
            md.append(f"| {z['preispunkt']} | {eur(z['preis_sitz'], 0)} | {eur(z['umsatz1'], 0)} | {eur(z['umsatz2'], 0)} | "
                      f"{eur(z['kosten1'], 0)} / {eur(z['kosten2'], 0)} | {pct(z['marge1'])} | {pct(z['marge2'])} | "
                      f"{eur(z['preis_sitz2_fuer_untergrenze'], 0)} |")
        md.append("")
    rm = daten["mittel"]
    md.append(f"30 % Abbau ist dabei vorsichtig: Mit Agent bräuchte der mittlere Kunde nur noch {eur(rm['stellen_mit_agent'], 2)} "
              f"von {eur(rm['einheiten']['pro Sitz'], 0)} Stellen, könnte also bis zu "
              f"{pct(1 - rm['stellen_mit_agent'] / rm['einheiten']['pro Sitz'])} abbauen. Dann fiele unser Sitz-Umsatz um denselben Anteil.\n")
    md.append("Pro Ticket und pro gelöstem Ticket bleibt der Umsatz im zweiten Jahr gleich, weil sich an Ticketmenge und "
              "Lösungsquote nichts ändert. Bei pro Sitz verliert der Anbieter genau dann Umsatz, wenn der Agent wirkt: "
              "Der Kunde braucht weniger Menschen.")

    (HIER / "evals" / "pricing.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    with open(HIER / "evals" / "pricing_ergebnisse.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(csv_zeilen[0].keys()))
        w.writeheader(); w.writerows(csv_zeilen)
    (HIER / "docs" / "korridor.svg").write_text(korridor_svg(daten) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
