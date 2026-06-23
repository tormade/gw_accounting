# Fortschritt

## Aktueller Meilenstein

Onboarding-/Migrations-Tool als belastbare Datenbasis.

## Zielbild

Das Produktziel steht in `docs/zielbild.md`: ein schlankes lokales Windows-Buerowerkzeug fuer Kundenkontakt, Bestellung, Lieferschein, Rechnung, offene Posten, Tagesliste und Auswertung. Der wichtigste Hauptweg ist Kunde oeffnen -> letzte Mengen sehen -> neue Mengen erfassen -> Beleg erzeugen.

## Erledigt

- UI-Prototyp mit Auftragsverwaltung, Rechnungs-/Lieferschein-Erzeugung, Belegarchiv und Stammdatenpflege.
- Import der zentralen Artikel- und Lieferkundenlisten als Stammdaten.
- Archivieren statt Loeschen fuer Stammdaten und Auftraege.
- Excel-/PDF-Ausgabe fuer Rechnung und Lieferschein mit Lieferpauschale, Pfand und Summenformeln.
- Onboarding-Kern fuer echte Kundenordnerdateien.
- Golden-File-Tests fuer Metzgerei Karl Rechnung und Lieferschein.
- Golden-File-Test fuer Privat-Ueberweiser mit Faelligkeitsdatum.
- Robuster Ordnerlauf, der Ausreisser-Dateien meldet und ueberspringt.

## In Arbeit

- Pruefliste fuer Konflikte aus Lieferkundenliste und Kundenordnerdatei.
- Artikel-Matching mit Alias-Speicherung fuer abgekuerzte Produktnamen.

## Offen

- UI fuer Pruefliste und manuelle Konfliktfreigabe.
- Importlauf mit einem echten kompletten Windows-Kundenordner testen.
- Hauptweg nach Migration: Kunde oeffnen -> letzte Mengen sehen -> Mengen anpassen -> Beleg erzeugen.
- Offene Posten, Tagesliste und spaetere Windows-Verpackung.
- Startbildschirm mit Kennzahlen: heutige Lieferungen, offene Posten, faellige Kontakte.
- Tagesliste fuer Fahrer mit Adresse, Zeitfenster und Kundenhinweisen.
- Kontakt-/Wiedervorlage ohne Kunden, die sich selbst melden.
- Auswertung fuer Stopps, Mengen und Umsatz mit Excel-Export.

## Naechste Aufgabe

Artikel-Matching gegen die Artikelliste ergaenzen, sichere Treffer automatisch verbinden und unsichere Treffer als Prueflistenpunkte speichern.
