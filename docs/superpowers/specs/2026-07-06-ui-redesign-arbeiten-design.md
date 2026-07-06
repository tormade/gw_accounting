# UI-Redesign: Arbeiten als geführtes Arbeitsbrett

## Ziel

Die Oberfläche soll nicht mehr wie eine Sammlung aus Modulen, Tabs und Karten wirken. Der Hauptnutzer ist der Büro-/Thekennutzer, der schnell einen Kunden findet, eine Bestellung aufnimmt, einen Lieferschein erzeugt, Rückläufe bearbeitet und daraus Rechnungen erstellt.

## Leitregeln

- Eine Ansicht zeigt eine Hauptaufgabe und eine primäre Aktion.
- `Arbeiten` ist kein Wizard und keine sichtbare Tab-Sammlung, sondern ein Arbeitsbrett mit geführtem Fokus.
- Listen dienen der Auswahl. Bearbeitung findet in ruhigen Mengenkarten statt, nicht in gequetschten Tabellen.
- Sichtbare Workflow-Tabs wie `Start`, `Heute`, `Kunden`, `Bestellung`, `Rücklauf` verschwinden aus dem Hauptfluss.
- `Verwaltung` ist Adminbereich und nicht Tagesarbeit.
- `Rechnungen` ist Kasse/offene Posten, nicht Belegerstellung.
- Kein generisches KI-Dashboard: keine KPI-Card-Suppe, keine verschachtelten Karten, keine lauten Farben.

## Arbeiten-Zustände

`Arbeiten` besteht aus Zuständen innerhalb einer Oberfläche:

1. **Übersicht**
   - Prominente Kundensuche.
   - Kompakte Liste offener Lieferschein-Rückläufe.
   - Keine Kennzahlenwand und kein `Heute`-Dashboard.

2. **Kundenfokus**
   - Kunde, Lieferhinweise, Zahlart und Rechnungswarnungen sichtbar.
   - Primäre Aktion: Bestellung aufnehmen.
   - Letzte Mengen und letzte Bestellungen sind Kontext, nicht konkurrierende Hauptbereiche.

3. **Bestellfokus**
   - Bestellkarte mit Mengenzeilen.
   - Nullmengen bleiben sichtbar.
   - Pfand-Rückgabe ist ein eigener kurzer Abschnitt.
   - Abschlussleiste führt zu Speichern und danach Lieferschein.

4. **Rücklauffokus**
   - Gleiche ruhige Mengenkarte wie Bestellung.
   - Kopf zeigt Kunde, Lieferschein und Datum.
   - Primäre Aktion: Rechnung erstellen.
   - Nach Rechnungserstellung zurück zur Übersicht.

## Erste Umsetzungsscheibe

Die erste Scheibe entfernt die sichtbaren Workflow-Tabs in `Arbeiten` und ersetzt sie durch einen internen `QStackedWidget`-Zustandswechsel. Die Startfläche bekommt eine echte Kundensuche statt nur eines Buttons. Der vorhandene Kunden-, Bestell- und Rücklauf-Code wird weiterverwendet, aber nicht mehr als sichtbares Tab-Modell gezeigt.

## Teststrategie

- UI-Tests prüfen, dass `Arbeiten` keine sichtbaren Workflow-Tabs mehr nutzt.
- UI-Tests prüfen, dass die Startfläche eine echte Kundensuche und Rücklaufliste hat.
- Bestehende Service- und Exporttests bleiben der Korrektheitsanker für Belege, Pfand, Nullmengen und Excel/PDF.
- Volle Regression und `compileall src tests` laufen vor Commit.
