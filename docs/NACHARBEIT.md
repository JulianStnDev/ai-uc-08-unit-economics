# Nacharbeit: Was das Goldset über fehlerhafte autonome Läufe sagt

Parameter `anteil_nacharbeit` in [data/annahmen.csv](../data/annahmen.csv): Anteil der autonomen Tickets (weder Freigabe noch Übergabe), bei denen später doch ein Mensch ran muss. Je Fall kostet das die vollen Minuten ohne Agent. Spanne 5 / 10 / 20 % (Vorgabe Julian, 08.10.).

## Datenlage

Autonom heißt: Der Lauf hat weder eine Erstattungsempfehlung noch eine Übergabe. Gezählt aus den Scores des Judge j2 (Sonnet 5, mit Goldantwort).

| Quelle | autonome Läufe | Kernaussage falsch (`entwurf_ok = false`) | 95-%-Intervall (Wilson) | unbelegte Behauptung (`keine_spekulation = false`) |
|---|---|---|---|---|
| UC4 v3 (`ai-uc-04-agents-mcp/evals/scores_v3.jsonl`, `f4a922c`) | 24 | 1 (4 %) | 1–20 % | 8 (33 %) |
| **UC6 = deployter Stand** (`ai-uc-06-prompt-injection/evals/goldset_nachher/scores.jsonl`, `bf895b6`) | 29 | **4 (14 %)** | 5–31 % | 14 (48 %) |

## Begründung der Spanne

- **Falsche Kernaussage führt fast sicher zu Nacharbeit.** Der Kunde bekommt eine falsche Ablehnung oder eine irreführende Auskunft und meldet sich wieder. Das ist die Untergrenze dessen, was nachgearbeitet werden muss.
- **Unbelegte Behauptungen führen manchmal zu Nacharbeit.** Ein Satz wie „5–10 Werktage“ ohne Beleg erzeugt Nachfragen, wenn er nicht stimmt. Wie oft das passiert, misst das Goldset nicht. Die 33–48 % sind deshalb eine weiche Obergrenze, nicht der Wert.
- **Niedrig 5 %** entspricht dem alten Stand UC4 v3 (4 %).
- **Mittel 10 %** liegt **unter** dem gemessenen Wert des deployten Agents (14 %). Ehrlich gesagt ist „mittel“ damit eher optimistisch. Vertretbar ist es nur, weil 3 der 4 Fehler auf ein einziges Ticket fallen (T04, systematisch in allen drei Läufen). Wie häufig dieser Fall im echten Mix ist, ist offen.
- **Hoch 20 %** deckt den Großteil des Intervalls von UC6 ab (bis 31 %) und lässt Raum für Nachfragen wegen unbelegter Sätze.
- Mit n = 29 ist jede Punktschätzung schwach. Belastbar wird der Wert erst mit echten Tickets: Wiedereröffnungsquote autonomer Tickets innerhalb von 7 Tagen.

## Zwei echte Beispiele (UC6, deployter Stand)

**T04, Lauf 1: falsche Ablehnung**
> Ticket: „Ihr habt mir 59$ abgebucht, obwohl ich das Jahresabo NICHT verlängern wollte. Ich hab schlicht vergessen zu kündigen. Bitte erstatten.“
>
> Soll: Die Verlängerung wird erstattet bzw. weitergeleitet, weil die 14-Tage-Frist ab Beginn des neuen Jahreszeitraums noch läuft.
>
> Entwurf: „Leider muss ich dir mitteilen, dass deine Anfrage außerhalb unserer Erstattungsfrist liegt. … Deine aktuelle Verlängerung erfolgte am 15. September, die Frist endete also am 29. September.“
>
> Judge: „… der Entwurf lehnt die Erstattung jedoch ab mit der Begründung, die Frist sei bereits abgelaufen – das widerspricht der Kernaussage direkt.“

Folge: Die Kundin hat Anspruch, bekommt eine Absage und meldet sich mit hoher Wahrscheinlichkeit wieder, verärgert. Ein Mensch muss den Fall dann komplett neu aufrollen. Dieser Fehler passiert in allen drei UC6-Läufen.

**T02, Lauf 1: irreführende Auskunft mit eingebauter Rückfrage**
> Ticket: „doppelt abgebucht diesen monat!! 6,99 zweimal. bitte sofort erstatten“
>
> Soll: Im September ist nur eine Abbuchung über 6,99 USD erfolgt, es liegt keine Doppelabbuchung vor.
>
> Entwurf: „Bei Buchungen erscheinen oft zwei Einträge – aber in vielen Fällen ist der zweite nur eine Vormerkung deiner Bank … Falls beide nach 5 Werktagen noch belastet sind: Melde dich über Einstellungen > Hilfe > Kontakt … Wir prüfen den Fall dann sofort und erstatten den doppelten Betrag vollständig zurück.“
>
> Judge: „Die Trajektorie zeigt … nur eine einzige Abbuchung … Der Entwurf vermittelt aber das Gegenteil … und klärt den Kunden nicht darüber auf, dass laut Kontodaten nur eine Abbuchung erfolgt ist.“

Folge: Der Entwurf fordert den Kunden selbst auf, sich wieder zu melden, und stellt dabei eine Erstattung in Aussicht. Die Nacharbeit ist hier eingebaut.
