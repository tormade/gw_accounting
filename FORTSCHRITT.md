# Fortschritt

## Aktueller Meilenstein

Onboarding-/Migrations-Tool als belastbare Datenbasis.

## Zielbild

Das Produktziel steht in `docs/zielbild.md`: ein schlankes lokales Windows-Buerowerkzeug fuer Kundenkontakt, Bestellung, Lieferschein, Rechnung, offene Posten, Tagesliste und Auswertung. Der wichtigste Hauptweg ist Kunde oeffnen -> letzte Mengen sehen -> neue Mengen erfassen -> Beleg erzeugen.

## Erledigt

- UI-Prototyp mit Kundenordner-Arbeitsplatz, Bestellverwaltung, Rechnungs-/Lieferschein-Erzeugung und Stammdatenpflege.
- Import der zentralen Artikel- und Lieferkundenlisten als Stammdaten.
- Archivieren statt Loeschen fuer Stammdaten und Auftraege.
- Excel-/PDF-Ausgabe fuer Rechnung und Lieferschein mit Lieferpauschale, Pfand und Summenformeln.
- Onboarding-Kern fuer echte Kundenordnerdateien.
- Golden-File-Tests fuer Metzgerei Karl Rechnung und Lieferschein.
- Golden-File-Test fuer Privat-Ueberweiser mit Faelligkeitsdatum.
- Robuster Ordnerlauf, der Ausreisser-Dateien meldet und ueberspringt.
- Artikel-Matching gegen die zentrale Artikelliste mit bestaetigten Alias-Schreibweisen.
- Kundensortiment-Datenmodell mit letzter Menge, alter Quelle und aktuellem zentralem Preis.
- Preisabweichungen zwischen Kunden-Excel und zentralem Artikelstamm werden als offene Prueffaelle erkannt.
- Prueflisten-UI fuer offene Kunden-/Artikel-/Preiskonflikte mit Erledigt/Wieder-oeffnen-Aktion.
- Pruefliste mit konkreten Aktionen: zentraler Preis, Excel-Preis oder Artikelalias bestaetigen.
- Pruefliste mit konkreten Aktionen fuer Kundendaten-Konflikte: zentrale Liste oder Kunden-Excel uebernehmen.
- Kundensortiment im Auftragsdialog: letzte Artikel sehen und direkt als Position uebernehmen.
- Persona-UX-Test fuer wenig IT-affine Anwender ausgewertet und Sofortverbesserungen umgesetzt.
- End-to-End-Test fuer realen Ablauf: Kunden-Excel importieren, zentrale Preise anwenden, Bestellung erstellen, Excel/PDF erzeugen.
- Belegfluss mit Hauptbutton fuer komplette Erstellung von Excel + PDF.
- PDF-Nacherzeugung aus vorhandener Excel liest Pfand-Rueckgaben aus denselben Zeilen wie der Excel-Export.
- Gespeicherte Preisentscheidungen aus der Pruefliste werden im Kundensortiment direkt angewendet.
- Rechnung-/Lieferschein-Erstellung sprachlich und visuell als gefuehrter Ablauf fuer Erstnutzer vereinfacht.
- Hauptnavigation auf Kundenordner-Arbeitsweise umgestellt: Kunde suchen, Ordnerdateien sehen, Bestellung und Belege von dort starten.
- UI-Altlasten entfernt: alter Direktbeleg-Sonderweg geloescht, verstecktes Belegarchiv aus dem Hauptfenster entkoppelt und sichtbare Texte auf Kundenordner/Bestellung vereinheitlicht.
- Persona-Review fuer einen wenig IT-affinen Erstnutzer umgesetzt: Vorlage aus Kundenordner klarer markiert, Beispielkontakte gekennzeichnet und Beleg-Korrekturen verstaendlicher benannt.
- Startseite ueberarbeitet: Hauptbuttons fuehren jetzt in unterschiedliche Arbeitsbereiche statt alle in denselben Kundenordner.
- Neues Bestellfenster kleiner und scrollbar gemacht, damit es auf kleineren Bildschirmen nutzbar bleibt.
- Kundenordner zeigt neueste Excel/PDF-Dateien zuerst und vermeidet das falsche Versprechen einer markierten Excel-Direktvorlage.
- Suchfelder erklaeren jetzt, dass ein Treffer angeklickt werden muss, und zeigen klar an, wenn nichts gefunden wurde.

## In Arbeit

- Kundenordner-Arbeitsplatz weiter abrunden: echte Windows-Kundenordner importieren und mit dem Bueroablauf gegenpruefen.

## Offen

- Importlauf mit einem echten kompletten Windows-Kundenordner testen.
- Offene Posten, Tagesliste und spaetere Windows-Verpackung.
- Startbildschirm mit Kennzahlen: heutige Lieferungen, offene Posten, faellige Kontakte.
- Tagesliste fuer Fahrer mit Adresse, Zeitfenster und Kundenhinweisen.
- Kontakt-/Wiedervorlage ohne Kunden, die sich selbst melden.
- Auswertung fuer Stopps, Mengen und Umsatz mit Excel-Export.

## Naechste Aufgabe

Bedienprobe mit einem echten kompletten Kundenordner durchspielen und daraus die naechsten UI-Korrekturen fuer den Hauptweg ableiten.
