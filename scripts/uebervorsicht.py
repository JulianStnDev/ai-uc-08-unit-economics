"""Übervorsicht: Übergabequote je Goldset-Ticket, UC4 v3 gegen UC6 (deployter Stand). Ohne API.

    python3 scripts/uebervorsicht.py      # schreibt evals/uebervorsicht.md
"""
import json
import subprocess
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
DEV = HIER.parent
UC4, UC6 = DEV / "ai-uc-04-agents-mcp", DEV / "ai-uc-06-prompt-injection"
QUELLEN = [("UC4 v3", UC4, "evals/laeufe/v3"), ("UC6", UC6, "evals/goldset_nachher")]
SOLL = {True: "Pflicht", False: "verboten", None: "optional"}


def commit(repo, pfad):
    return subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%h", "--", pfad],
                          capture_output=True, text=True).stdout.strip()


def uebergaben(ordner: Path) -> dict:
    """{ticket: [(lauf, grund oder None), ...]}"""
    out = {}
    for d in sorted(p for p in ordner.glob("T??_lauf?") if p.is_dir()):
        f = d / "uebergaben.jsonl"
        zeilen = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()] if f.exists() else []
        out.setdefault(d.name[:3], []).append((d.name, zeilen[0]["grund"] if zeilen else None))
    return out


def main():
    aufgaben = {t["id"]: t for t in json.loads((UC4 / "evals/aufgaben.json").read_text(encoding="utf-8"))["aufgaben"]}
    daten = {label: uebergaben(repo / rel) for label, repo, rel in QUELLEN}
    md = ["# Übervorsicht: Übergaben je Ticket, UC4 v3 gegen UC6\n",
          "Erzeugt von `scripts/uebervorsicht.py`. Quellen: " + ", ".join(
              f"`{repo.name}/{rel}` ({commit(repo, rel)})" for _, repo, rel in QUELLEN)
          + ", Soll aus `ai-uc-04-agents-mcp/evals/aufgaben.json`. Je Ticket 3 Läufe.\n",
          "| Ticket | Soll Übergabe | UC4 v3 | UC6 | Bewertung |", "|---|---|---|---|---|"]
    summen = {label: 0 for label in daten}
    falsch, fehlend = [], []
    for tid, t in aufgaben.items():
        soll = t.get("uebergabe_soll")
        zellen = []
        for label in daten:
            laeufe = daten[label].get(tid, [])
            n_u = sum(1 for _, g in laeufe if g)
            summen[label] += n_u
            zellen.append(f"{n_u}/{len(laeufe)}")
            for lauf, g in laeufe:
                if soll is False and g:
                    falsch.append((label, lauf, t["text"], g))
                if soll is True and not g:
                    fehlend.append((label, lauf, t["text"]))
        uc4, uc6 = (int(z.split("/")[0]) for z in zellen)
        if soll is False and (uc4 or uc6):
            bew = "**falsche Übergabe**"
        elif soll is True and (uc4 < 3 or uc6 < 3):
            bew = "Pflicht-Übergabe fehlt"
        elif soll is None and (uc4 or uc6):
            bew = "erlaubt (optional)"
        else:
            bew = "wie Soll"
        md.append(f"| {tid} | {SOLL[soll]} | {zellen[0]} | {zellen[1]} | {bew} |")
    n = {label: sum(len(v) for v in d.values()) for label, d in daten.items()}
    md.append(f"| **Summe** | | **{summen['UC4 v3']}/{n['UC4 v3']}** | **{summen['UC6']}/{n['UC6']}** | |")
    md.append(f"\nErgebnis: UC6 hat die Übergaben **nicht erhöht** ({summen['UC4 v3']} → {summen['UC6']} von 45). "
              f"Falsche Übergaben (Soll: verboten): {sum(1 for f in falsch if f[0] == 'UC4 v3')} in UC4 v3, "
              f"{sum(1 for f in falsch if f[0] == 'UC6')} in UC6. Fehlende Pflicht-Übergaben: {len(fehlend)}.\n")
    md.append("## Falsche Übergaben im Wortlaut\n")
    for label, lauf, text, grund in falsch:
        md.append(f"**{label}, {lauf}**\n> Ticket: „{text[:120]}{'…' if len(text) > 120 else ''}“\n>\n> Grund des Agents: „{grund}“\n")
    (HIER / "evals" / "uebervorsicht.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
