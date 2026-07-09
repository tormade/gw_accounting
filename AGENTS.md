# Arbeitsregeln fuer Codex-Agenten

## Architektur

- Die Anwendung bleibt eine Windows-Desktop-App mit UI-unabhaengigem Kern.
- Schichten bleiben getrennt: Oberflaeche -> Vorgaenge/Services -> Kernlogik -> Datenrueckgrat.
- Fachlogik gehoert nie direkt in die Oberflaeche.
- Vorlagen, Briefkopf, Pfandwerte und Exportpfade sind Konfiguration oder Daten, nicht hart verdrahtete UI-Logik.
- SQLite bleibt offen lesbar. Excel, PDF und CSV-Ausgaben muessen weiterhin exportierbar bleiben.
- Die Zielarchitektur steht in `docs/technische-architektur.md` und ist bei groesseren Umbauten verbindlich.
- Neue groessere Funktionen sollen in Richtung `kern` -> `vorgaenge` -> `adapter` -> `ui` getrennt werden.
- Bestehende `services` werden schrittweise entkoppelt, nicht blind umbenannt.

## Architektur-Invarianten

1. Der Kern haengt von nichts ab: keine UI-, DB- oder Dateisystem-Imports im Kern.
2. Persistenz und Ausgabe laufen hinter Schnittstellen und bleiben austauschbar.
3. Preise werden live beim Erfassen aus dem Artikelstamm gezogen und beim Finalisieren als Snapshot gespeichert.
4. Vorlagen und Einstellungen sind Konfiguration, kein Code.
5. Daten bleiben offen exportierbar: SQLite, Excel, PDF und CSV.
6. Tests sind vor Commit gruen; Golden-Files sind der wichtigste Korrektheitsanker.

## Datenmodell und Rechenregeln

- Zeilensumme = Menge * (Lieferpreis + Pfand).
- Pfand-Rueckgabe wird negativ gerechnet.
- Lieferpauschale wird als eigene Zeile gefuehrt und aktuell bewusst vom Sachbearbeiter gewaehlt.
- Standard-Lieferpauschale: 3,90 EUR.
- Brutto = Lieferwert + Pfand-Rueckgabe + Lieferpauschale.
- Netto = Brutto / 1,19.
- MwSt = Brutto - Netto.
- Zahlart steuert Fuss-/Hinweistext: SEPA fuehrt zu Lastschrifttext, Ueberweisung zu Ueberweisungstext mit Faelligkeit.

## Onboarding- und Migrationsprinzip

- Die je-Kunde-Excel im Ordner ist die operative Wahrheit fuer Sortiment, letzte Mengen, letzte Rechnungsnummer, letztes Datum, Zahlart und gedruckte Liefer-/Zugangsnotizen.
- Die zentrale Lieferkunden-Liste ist die Wahrheit fuer Planung und Beziehung: Rhythmus, naechster Kontakt, Prioritaet, Kontakt-Mail, Rechnungs-Mail, Vormittag/Nachmittag, ABO und Bemerkungen.
- Der Kopfbereich der Ordnerdatei ist nicht positionssicher. Felder werden nach Inhalt erkannt: `@` bedeutet Mail, Telefonmuster bedeutet Telefon, Datum bedeutet Belegdatum, `Re. Nr.` plus Nachbarwert bedeutet Belegnummer.
- Ueberschneidungen bei Mail, Telefon und Adresse werden nicht automatisch aufgeloest. Sie landen in der Pruefliste.
- Unsichere Artikel-Treffer landen ebenfalls in der Pruefliste. Bestaetigte Schreibweisen werden spaeter als Alias am Artikel gespeichert.
- Ausreisser-Dateien werden gemeldet und uebersprungen, nicht erraten und nicht zum Absturz gebracht.
- Nach dem Onboarding ist das Programm die Arbeitsquelle. Die Excel-Dateien sind Startpunkt und Nachweis, nicht mehr die laufende Ablage.

## Entwicklungs-Schleife

Jeder Meilenstein laeuft in dieser Reihenfolge:

Plan -> Entwickeln -> Testen -> Review -> Debuggen -> Anwender-Smoke -> Commit -> Checkpoint

- Vor Verhaltenaenderungen zuerst Tests schreiben.
- Golden-File-Tests aus echten Beispieldateien sind das Korrektheitssignal fuer Rechnungen, Lieferscheine und Migration.
- Tests muessen gruen sein, bevor ein Commit erstellt wird.
- Nach jedem Meilenstein `FORTSCHRITT.md` aktualisieren.
- An Meilenstein-Grenzen fuer Thomas' Abnahme anhalten.

## Akzeptanz fuer Onboarding

- Metzgerei Karl muss aus echter Rechnung und Lieferkundenliste zusammengefuehrt werden.
- Erwartete Golden-Werte: Lieferwert 234,28 EUR, Pfand-Rueckgabe -47,90 EUR, Brutto 186,38 EUR, Netto 156,62 EUR, MwSt 29,76 EUR, Lieferpauschale 0.
- Zeilenprobe: Frucade Colamix, Menge 3, Pfand 3,10 EUR, Preis 10,48 EUR -> 40,74 EUR.
- Ueberweiser-Beispiel muss spaeter Fusstext Ueberweisung und Faelligkeit Datum + 7 erkennen.

## Agent skills

### Issue tracker

GitHub Issues im Repository sind die Arbeitswarteschlange; externe Pull Requests werden nicht triagiert. Siehe `docs/agents/issue-tracker.md`.

### Triage labels

Die Standardlabels `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human` und `wontfix` werden verwendet. Siehe `docs/agents/triage-labels.md`.

### Domain docs

Dieses Projekt hat eine gemeinsame Domain-Dokumentation in `CONTEXT.md` und Architekturentscheidungen unter `docs/adr/`. Siehe `docs/agents/domain.md`.
