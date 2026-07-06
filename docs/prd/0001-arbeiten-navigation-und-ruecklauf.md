# PRD: Erster Meilenstein für `Arbeiten`, dreiteilige Navigation und Rücklauf

## Problem Statement

Der Büro-/Thekennutzer muss aktuell zu viele Hauptbereiche verstehen, um die tägliche Arbeit zu erledigen. `Heute`, `Kunden`, `Bestellungen`, `Belege`, `Rechnungen` und `Stammdaten` wirken gleich wichtig, obwohl der Alltag aus einer klaren Kette besteht: Kunde finden, Bestellung aufnehmen, Lieferschein erzeugen, zurückgekommene Lieferscheine bearbeiten, Rechnung erzeugen und Zahlung prüfen.

Die App soll nach dem Import die operative Wahrheit sein. Excel und PDF bleiben Ausgabe und Nachweis, aber der Nutzer soll nicht mehr in alten Excel-Dateien denken müssen. Die aktuelle funktionsorientierte Navigation zieht ihn jedoch weiterhin in Modul- und Datei-Logik hinein.

Der erste Meilenstein soll deshalb die Hauptnavigation und den primären Arbeitsfluss neu ausrichten, ohne Kernlogik, Excel-/PDF-Export oder Belegberechnung komplett neu zu schreiben.

## Solution

Die Hauptnavigation wird auf drei sichtbare Bereiche reduziert:

- `Arbeiten`
- `Rechnungen`
- `Verwaltung`

`Arbeiten` wird der primäre Tagesarbeitsplatz. Der erste Bildschirm zeigt zwei gleichwertig erkennbare Aufgaben:

- Kundensuche / Bestellung aufnehmen
- offene Lieferschein-Rückläufe

Nach Kundenauswahl fokussiert `Arbeiten` auf den Kundenkontext: Kundendaten, Warnhinweise, empfohlene Artikel, letzte Mengen, letzte Bestellungen und die primäre Aktion `Neue Bestellung aufnehmen`.

Nach Auswahl eines offenen Rücklaufs fokussiert `Arbeiten` auf diesen Rücklauf: Kunde, Lieferscheinnummer, einfache Mengenliste, Pfand-Rückgabe und die Aktion `Rechnung erstellen`.

`Rechnungen` bleibt der Kassen-/Offene-Posten-Arbeitsplatz. `Verwaltung` bündelt Adminfunktionen wie Kundenstamm, Artikelstamm, Import, Prüfpunkte, Belegarchiv und Einstellungen.

## User Stories

1. Als Büro-/Thekennutzer möchte ich nur drei Hauptbereiche sehen, damit ich nicht überlegen muss, ob ich unter Kunden, Bestellungen oder Belege beginnen soll.
2. Als Büro-/Thekennutzer möchte ich im Bereich `Arbeiten` sofort Kunden suchen können, damit ich einen Telefonanruf direkt bearbeiten kann.
3. Als Büro-/Thekennutzer möchte ich im Bereich `Arbeiten` offene Lieferschein-Rückläufe sehen, damit ich den Papierstapel aus dem Fahrerfach abarbeiten kann.
4. Als Büro-/Thekennutzer möchte ich nach Auswahl eines Kunden einen fokussierten Kundenarbeitsplatz sehen, damit ich nicht parallel von anderen Listen abgelenkt werde.
5. Als Büro-/Thekennutzer möchte ich nach Kundenauswahl Kundendaten, Lieferhinweise und Zahlart sehen, damit ich während des Telefonats wichtige Informationen griffbereit habe.
6. Als Büro-/Thekennutzer möchte ich offene oder überfällige Rechnungen des Kunden als kompakten Warnhinweis sehen, damit ich beim Bestellen auf Zahlungsprobleme reagieren kann.
7. Als Büro-/Thekennutzer möchte ich empfohlene Artikel und letzte Mengen sehen, damit ich typische Bestellungen schnell übernehmen oder anpassen kann.
8. Als Büro-/Thekennutzer möchte ich eine neue Bestellung aus dem Kundenkontext starten, damit ich nicht in einen separaten Hauptbereich wechseln muss.
9. Als Büro-/Thekennutzer möchte ich die Bestellaufnahme inline in `Arbeiten` bedienen, damit die App wie ein durchgehender Arbeitsfluss wirkt.
10. Als Büro-/Thekennutzer möchte ich Mengen direkt in einer einfachen Liste erfassen, damit die Bedienung der bisherigen Excel-Gewohnheit ähnlich bleibt.
11. Als Büro-/Thekennutzer möchte ich Artikel mit Menge `0` oder leer sichtbar behalten können, damit bekannte Artikel auf Lieferschein und Rechnung erhalten bleiben.
12. Als Büro-/Thekennutzer möchte ich Pfand-Rückgaben separat erfassen, damit ich Rückgabe-Pfand nicht mit Artikelpfand verwechsle.
13. Als Büro-/Thekennutzer möchte ich nach dem Speichern einer Bestellung primär `Lieferschein erstellen` sehen, damit der Standardprozess klar ist.
14. Als Büro-/Thekennutzer möchte ich `Rechnung direkt erstellen` weiterhin nutzen können, damit sichere Direktabrechnungen möglich bleiben.
15. Als Büro-/Thekennutzer möchte ich bei `Rechnung direkt erstellen` bewusst bestätigen, dass Mengen und Pfand-Rückgabe final sind, damit ich nicht versehentlich zu früh fakturiere.
16. Als Büro-/Thekennutzer möchte ich nach Lieferschein-Erstellung automatisch einen offenen Rücklauf bekommen, damit nicht berechnete Lieferscheine zuverlässig in der Arbeitsliste landen.
17. Als Büro-/Thekennutzer möchte ich einen offenen Rücklauf aus der Arbeitsliste öffnen, damit ich zurückgekommene Papier-Lieferscheine schnell bearbeiten kann.
18. Als Büro-/Thekennutzer möchte ich im Rücklauf eine einfache Mengenliste sehen, damit ich Mengen wie bisher in Excel korrigieren kann.
19. Als Büro-/Thekennutzer möchte ich im Rücklauf Pfand-Rückgaben ergänzen, damit die spätere Rechnung stimmt.
20. Als Büro-/Thekennutzer möchte ich aus dem Rücklauf direkt die Rechnung erstellen, damit der Papierstapel zügig abgearbeitet wird.
21. Als Büro-/Thekennutzer möchte ich nach Rechnungserstellung automatisch zur Rücklaufliste zurückkehren, damit ich den nächsten Rücklauf bearbeiten kann.
22. Als Büro-/Thekennutzer möchte ich sichtbare Status in Alltagssprache sehen, damit ich keine technischen Begriffe wie `lieferauftrag_erstellt` verstehen muss.
23. Als Büro-/Thekennutzer möchte ich Status wie `Bestellung aufgenommen`, `Rücklauf offen` und `Rechnung erstellt` sehen, damit ich den Prozessstand sofort verstehe.
24. Als Büro-/Thekennutzer möchte ich `Rechnungen` als Kassenarbeitsplatz nutzen, damit offene, fällige, überfällige und bezahlte Rechnungen klar getrennt sind.
25. Als Büro-/Thekennutzer möchte ich in `Rechnungen` Zahlungen und Teilzahlungen erfassen, damit offene Posten aktuell bleiben.
26. Als Admin möchte ich Stammdaten und Import in `Verwaltung` finden, damit sie den täglichen Bestellfluss nicht stören.
27. Als Admin möchte ich Prüfpunkte in `Verwaltung` bearbeiten, damit Konflikte gezielt geklärt werden können.
28. Als Admin möchte ich das Belegarchiv in `Verwaltung` finden, damit Belege bei Bedarf gesucht werden können, ohne den Hauptfluss zu belasten.
29. Als wenig computeraffiner Nutzer möchte ich große, klare Hauptaktionen sehen, damit ich ohne Schulung verstehe, was als Nächstes zu tun ist.
30. Als wenig computeraffiner Nutzer möchte ich keine versteckten Pflicht-Rechtsklicks brauchen, damit die Bedienung verlässlich bleibt.
31. Als wenig computeraffiner Nutzer möchte ich echte Umlaute und verständliche deutsche Texte sehen, damit die Oberfläche nicht technisch oder unfertig wirkt.
32. Als Betreiber möchte ich Excel und PDF weiterhin im Kundenordner erhalten, damit der bisherige Nachweis- und Ablageprozess erhalten bleibt.
33. Als Betreiber möchte ich die bestehende Exportlogik weiterverwenden, damit der Umbau nicht unnötig riskant wird.
34. Als Entwickler möchte ich Statuslogik und UI-Sprache sauber trennen, damit interne Werte stabil bleiben und sichtbare Texte trotzdem alltagstauglich sind.
35. Als Entwickler möchte ich den ersten Meilenstein begrenzen, damit Navigation und Arbeitsfluss bewiesen werden können, bevor ein vollständiger Rücklaufeditor vertieft wird.

## Implementation Decisions

- Die sichtbare Hauptnavigation wird auf `Arbeiten`, `Rechnungen` und `Verwaltung` reduziert.
- Frühere Hauptbereiche wie `Heute`, `Kunden`, `Bestellungen` und `Belege` werden in diese drei Bereiche integriert oder zurückgestuft.
- `Arbeiten` wird als neuer primärer Arbeitsbereich eingeführt.
- Der erste Bildschirm von `Arbeiten` zeigt Kundensuche/Bestellaufnahme und offene Lieferschein-Rückläufe als zwei erkennbare Aufgaben.
- Nach Kundenauswahl fokussiert `Arbeiten` auf den Kundenkontext.
- Nach Auswahl eines Rücklaufs fokussiert `Arbeiten` auf die Rücklaufbearbeitung.
- Die bestehende Kundenkontext-Logik und die bestehende Bestelllogik sollen im ersten Meilenstein weiterverwendet und neu zusammengesetzt werden, statt komplett neu geschrieben zu werden.
- Der bestehende Bestelleditor darf im ersten Meilenstein eingebettet oder stark wiederverwendet werden, solange er aus Nutzersicht Teil von `Arbeiten` ist.
- Die bestehende Rechnungs-/Lieferschein-Erzeugung bleibt technische Grundlage.
- Nach Lieferschein-Erstellung wird der Vorgang für die Arbeitsliste als `Rücklauf offen` sichtbar.
- `Mengen final` ist kein separater Alltagsschritt, sondern wird beim Erstellen der Rechnung aus dem Rücklauf automatisch gesetzt.
- `Rechnung direkt erstellen` bleibt möglich, ist aber sekundär zur Standardaktion `Lieferschein erstellen`.
- `Rechnung direkt erstellen` muss eine bewusste Bestätigung enthalten, dass Mengen und Pfand-Rückgabe final sind.
- Eine Sofort-Rechnung überspringt `Rücklauf offen` vollständig.
- Sichtbare Status verwenden Alltagssprache.
- Interne Statuswerte können aus Stabilitätsgründen ASCII und technisch bleiben.
- Sichtbare deutsche Texte und Dokumentation verwenden echte Umlaute.
- Technische Bezeichner, Datenbankwerte und Dateinamen müssen in diesem Meilenstein nicht pauschal umbenannt werden.
- `Rechnungen` bleibt primär Kassen-/Offene-Posten-Arbeitsplatz.
- `Verwaltung` bündelt Kundenstamm, Artikelstamm, Import, Prüfpunkte, Belegarchiv und Einstellungen.
- Belegarchiv wird nicht als Hauptbereich gezeigt.
- Der erste Meilenstein soll keine neue Fahrer-App und keine große Tourenplanung einführen.
- Der erste Meilenstein soll keine komplette neue Exportpipeline einführen.

## Testing Decisions

- Tests sollen externes Verhalten prüfen: sichtbare Navigation, erreichbare Hauptaktionen, Statusübergänge und erzeugte Belege.
- Die höchste UI-Testnaht ist das Hauptfenster mit neuer Navigation und neuem Arbeitsbereich.
- Bestehende UI-Quelltests für Navigation, Kundenkontext, Bestellaufnahme, Rechnungen und Verwaltung werden angepasst oder ersetzt.
- Service-Tests prüfen, dass Lieferschein-Erstellung einen offenen Rücklauf erzeugt oder als solcher gelistet wird.
- Service-Tests prüfen, dass Sofort-Rechnung `Rücklauf offen` überspringt.
- Service-Tests prüfen, dass Rechnungserstellung aus Rücklauf Mengen finalisiert und Rechnung/offenen Posten erzeugt.
- Bestehende Golden-File-Tests für Excel/PDF bleiben der Korrektheitsanker für Belegausgabe.
- Bestehende Tests für Menge `0` und sichtbare Leerpositionen bleiben relevant und dürfen nicht gebrochen werden.
- Bestehende Tests für Pfand-Rückgabe mit festen Stufen bleiben relevant.
- UI-Tests sollen prüfen, dass `Bestellungen` und `Belege` nicht mehr als Hauptnavigation erscheinen.
- UI-Tests sollen prüfen, dass `Arbeiten`, `Rechnungen` und `Verwaltung` sichtbar sind.
- UI-Tests sollen prüfen, dass nach Kundenauswahl die Rücklaufliste zurücktritt und Kundenkontext sichtbar wird.
- UI-Tests sollen prüfen, dass nach Rücklaufauswahl der Rücklauf-Arbeitsplatz sichtbar wird.
- UAT soll den Hauptweg abdecken: Kunde suchen, Bestellung aufnehmen, Lieferschein erzeugen, Rücklauf öffnen, Mengen/Pfand prüfen, Rechnung erzeugen.
- UAT soll zusätzlich Sofort-Rechnung mit Bestätigung abdecken.
- Regression soll sicherstellen, dass bestehende Excel-/PDF-Ausgabe weiterhin funktioniert.

## Out of Scope

- Vollständige Fahrer-App.
- Mobile Fahreransicht.
- Große Tourenplanung.
- Neue E-Mail- oder DATEV-Automation.
- Neue ZUGFeRD-/E-Rechnung.
- Komplette technische Neuschreibung der Services.
- Vollständige Umbenennung aller internen Statuswerte.
- Vollständige Umstellung aller bestehenden ASCII-Dateinamen oder technischen Bezeichner auf Umlaute.
- Ein perfekter neuer Rücklaufeditor mit Abweichungsspalten.
- Ein neuer globaler Suchindex.
- Mehrplatz-/NAS-Architektur.

## Further Notes

- Dieses PRD folgt `CONTEXT.md` und ADR 0001.
- Der Meilenstein soll beweisen, dass die neue Produktstruktur funktioniert: `Arbeiten`, `Rechnungen`, `Verwaltung`.
- Die App bleibt die operative Wahrheit; Excel/PDF sind Ausgabe und Nachweis.
- Der erste Umsetzungsschnitt soll bewusst die vorhandene Logik nutzen, um Risiko zu begrenzen.
- Nach diesem Meilenstein kann ein zweiter PRD den Rücklaufeditor, Statusmodell-Vertiefung und weitere Admin-Vereinfachungen behandeln.
