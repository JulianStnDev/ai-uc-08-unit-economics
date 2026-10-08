# Build vs. Buy aus Käufer-Sicht (FocusFlow)

Erzeugt von `scripts/build_buy.py` aus `data/annahmen.csv`. Alle Annahmen auf „mittel“, Kundentyp mittel (8 min ohne Agent, 0,4420 EUR/min). Nur entscheidungsrelevante Kosten: Menschliche Grundlast, die in jeder Option gleich ist, fehlt; die Minuten an Tickets unterscheiden sich je Option und sind drin. Rechenweg: [docs/RECHENWEG_BUILD_BUY.md](../docs/RECHENWEG_BUILD_BUY.md).

## TCO für A: laufender Aufwand in Stunden je Monat (Annahmen)

| Aufgabe | aus | niedrig | mittel | hoch |
|---|---|---|---|---|
| Goldset und Evals pflegen (UC2, UC4): neue Fälle aufnehmen, Läufe nach jeder Änderung | UC2, UC4 | 4 | 8 | 16 |
| Judge betreiben und nachkalibrieren (UC7): Stichprobe auswerten, Kalibrierung bei Prompt- oder Modellwechsel | UC7 | 2 | 4 | 8 |
| Sicherheit (UC6): Bedrohungsmodell, Zusage-Prüfung und Angriffsfälle pflegen | UC6 | 2 | 6 | 12 |
| Betrieb inklusive Bereitschaft (UC7): Deploy, Monitoring, Budget, Rollback, Rufbereitschaft | UC7 | 8 | 16 | 40 |
| Modell- und SDK-Updates: neue Versionen testen, Goldset neu laufen lassen | UC4, UC6 | 2 | 4 | 10 |
| Datenschutz: Auftragsverarbeitung (Anthropic, Google, Neon), Löschfristen, Auskünfte | UC7 | 1 | 3 | 6 |
| Regeln und Werkzeuge an Richtlinien anpassen (z. B. Fristberechnung T04) | UC4, UC6 | 2 | 4 | 8 |
| **Summe** | | **21** | **45** | **100** |

Zum Stundensatz von 58,50 EUR: 2.632 EUR je Monat (mittel), Spanne 1.228 bis 5.850 EUR.

## Eigene Bauzeit (grobe Näherung aus der Git-Historie)

| Repo | Zeitraum | Commits ohne Merges | aktive Tage (mit Commit) |
|---|---|---|---|
| UC4 Agents/MCP | 24.09.–30.09.2026 | 8 | 2 |
| UC6 Prompt Injection | 02.10.–08.10.2026 | 15 | 2 |
| UC7 Deployment | 28.09.–02.10.2026 | 28 | 4 |
| **Summe** | 24.09.–08.10.2026 | **51** | **8** |

8 Tage × 8 h × Faktor 2 (Demo → Produktion) = **128 h**, auf 24 Monate verteilt 312 EUR je Monat. Ausdrücklich grob: Commits sind gebündelt (UC4: 7 von 8 Commits an einem Tag), Arbeit ohne Commit fehlt, und gebaut hat eine Person mit Claude Code an erfundenen Kundendaten. UC5 (Text-to-SQL) ist kein Agent und nicht gezählt.

## Kosten je Monat bei 10.000 Tickets (EUR)

| Option | Technik und Gebühren | interner Aufwand | Personal an Tickets | **gesamt** |
|---|---|---|---|---|
| A selbst betreiben | 300,94 | 2.944,50 | 15.717,52 | **18.962,96** |
| B Intercom Fin | 7.528,85 | 331,50 | 15.717,52 | **23.577,87** |
| C unser Produkt | 5.122,50 | 156,00 | 15.717,52 | **20.996,02** |
| D nur Klassifikation | 12,26 | 117,00 | 33.150,00 | **33.279,26** |

B: 8.500 Outcomes (alle nicht übergebenen Tickets, weil Fin auch „assumed resolutions“ abrechnet, plus 50 % der Übergaben als Procedure Handoff), Übergabequote 30 % als Annahme. C: 6.230 gelöste Tickets.

## Kipppunkt nach Volumen

| Tickets je Monat | A selbst betreiben | B Intercom Fin | C unser Produkt | D nur Klassifikation | günstigste |
|---|---|---|---|---|---|
| 1.000 | 4.549 | 2.656 | 2.645 | 3.433 | C |
| 2.000 | 6.150 | 4.981 | 4.684 | 6.749 | C |
| 3.000 | 7.752 | 7.305 | 6.723 | 10.066 | C |
| 5.000 | 10.955 | 11.955 | 10.801 | 16.698 | C |
| 7.500 | 14.959 | 17.766 | 15.899 | 24.989 | A |
| 10.000 | 18.963 | 23.578 | 20.996 | 33.279 | A |
| 15.000 | 26.971 | 35.201 | 31.191 | 49.860 | A |
| 20.000 | 34.979 | 46.824 | 41.386 | 66.442 | A |
| 30.000 | 50.995 | 70.071 | 61.776 | 99.604 | A |
| 50.000 | 83.026 | 116.563 | 102.556 | 165.928 | A |
| 75.000 | 123.066 | 174.679 | 153.531 | 248.834 | A |
| 100.000 | 163.105 | 232.795 | 204.506 | 331.740 | A |

**A wird günstiger als B ab 3.618 Tickets je Monat, günstiger als C ab 5.352 Tickets je Monat.** Die Personal-Minuten sind bei A und C gleich (derselbe Agent), bei B nur unter der Annahme gleicher Übergabequote. Der Kipppunkt entsteht deshalb aus Fixkosten (Betrieb von A) gegen Stückpreis (B, C).

Wie stark der Kipppunkt am TCO von A hängt:

| TCO-Stunden für A | Stunden je Monat | A günstiger als B ab | A günstiger als C ab |
|---|---|---|---|
| niedrig | 21 | 1.676 | 2.142 |
| mittel | 45 | 3.618 | 5.352 |
| hoch | 100 | 8.067 | 12.708 |

Fins Übergabequote (Annahme) verschiebt A gegen B stark, weil jede Übergabe Menschenzeit kostet: Bei 20 % statt 30 % ist A erst ab 6.113 Tickets günstiger, bei 40 % schon ab 2.569.

## Qualitative Kriterien

| Kriterium | A selbst betreiben | B Intercom Fin | C unser Produkt | D nur Klassifikation |
|---|---|---|---|---|
| Kontrolle | Voll: Prompt, Regeln im Code, Judge, Schwellen und Freigaben selbst festgelegt | Gering bis mittel: Verhalten über Inhalte, Prozeduren und Einstellungen steuerbar, das Modell nicht | Mittel: Regeln und Freigabe-Schwellen vertraglich, Umsetzung bei uns | Voll, es gibt aber wenig zu steuern |
| Daten verlassen das Haus | Ja, an Anthropic (Modell) und den gewählten Hoster (UC7: Google Frankfurt, Neon Frankfurt) | Ja, an Intercom und dessen Modellanbieter; Speicherort laut Intercom-Vertrag | Ja, an uns, Anthropic und unsere Hoster | Ja, nur der Tickettext an Anthropic für die Klassifikation |
| Anpassbarkeit | Beliebig, jede Änderung braucht aber Goldset, Judge und Sicherheitstests (UC2, UC6, UC7) | Innerhalb dessen, was Fin anbietet | Über uns, Wünsche konkurrieren mit anderen Kunden | Kategorien frei, sonst nichts |
| Abhängigkeit vom Anbieter | Vom Modellanbieter (Modell- und SDK-Wechsel, siehe UC6 T04) und vom eigenen Team | Von Intercom (Preis, Outcome-Definition, Plattform) | Von uns als kleinem Anbieter (Fortbestand, Preis nach Pilot) | Gering |
| Zeit bis zum Start | Lang: Bau, Evals, Sicherheit, Betrieb (bei uns 8 aktive Tage für die Demo, Produktion mehr) | Kurz, wenn die Inhalte da sind; Prozeduren für Erstattungen brauchen Einrichtung | Kurz bis mittel: Einrichtung durch uns, Pilot im Schattenmodus | Sehr kurz (UC1 an einem Tag) |
