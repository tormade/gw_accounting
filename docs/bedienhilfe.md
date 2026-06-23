# Bedienhilfe Getraenkeladen Tool

Diese App ist fuer den lokalen Bueroalltag gedacht. Sie soll nicht wie ein grosses ERP wirken, sondern Schritt fuer Schritt durch die wichtigsten Aufgaben fuehren.

## Startseite

Die Startseite ist der erste Blick in den Arbeitstag. Dort sehen Sie:

- Lieferungen heute
- Offene Posten
- Kontaktanfragen heute

Wenn hier etwas angezeigt wird, ist das der naechste Arbeitsvorrat.

Die drei Startbuttons fuehren auf unterschiedliche Arbeitsbereiche:

- Kundenordner oeffnen: normaler Weg fuer Kunde, alte Excel/PDF und neue Bestellung.
- Offene Posten pruefen: Zahlungen, SEPA und offene Rechnungen kontrollieren.
- Preis-/Importpruefung: unklare Artikel, Preise oder Kundenhinweise abarbeiten.

## Kundenordner und Bestellung

Der normale Ablauf ist:

1. Auf der Startseite "Kundenordner oeffnen" waehlen.
2. Kunden suchen und in der Trefferliste anklicken.
3. Alte Excel- oder PDF-Dateien im Kundenordner bei Bedarf oeffnen.
4. Rechts die letzten importierten Mengen pruefen.
5. "Neue Bestellung aus letzten Mengen starten" waehlen.
6. Bestellnummer, Lieferdatum, Mengen, Preise und Pfand pruefen.
7. Bestellung speichern.
8. Danach Lieferschein oder Rechnung aus der markierten Bestellung erstellen.

Bestell-, Lieferschein- und Rechnungsnummern werden frei eingetragen. Die App uebernimmt genau die Nummer, die im Feld steht.

Datumsfelder koennen entweder ueber den Kalender ausgewaehlt oder direkt im Format TT.MM.JJJJ eingetragen werden, zum Beispiel 21.06.2026.

Der normale Ablauf fuer Positionen ist:

1. Produkt waehlen.
2. Menge pruefen.
3. Position hinzufuegen.
4. Bei Bedarf weitere Positionen hinzufuegen.

Wenn etwas fehlt, zeigt die Statuszeile unten an, was als Naechstes zu tun ist.

## Kunden und Produkte pflegen

Neue Kunden und Produkte werden links eingetragen. Vorhandene Stammdaten werden in der Liste ausgewaehlt und mit "Auswahl bearbeiten" wieder in das Formular geladen.

Bei Produkten koennen versehentliche Eingaben mit "Aenderungen verwerfen" zurueckgenommen werden, solange noch nicht gespeichert wurde. Die Einheit wird ueber ein Dropdown gewaehlt.

In den Listen fuer Kunden, Produkte und Bestellungen koennen Eintraege per Rechtsklick bearbeitet, archiviert oder wiederhergestellt werden. Doppelklick laedt einen Eintrag ebenfalls zur Bearbeitung.

Wichtig: Archivieren statt loeschen. Dadurch verschwinden Kunden oder Produkte aus dem normalen Alltag, koennen aber bei einem Fehler wiederhergestellt werden.

## Einstellungen

Im Bereich Einstellungen werden zentrale Auswahlwerte und Hilfsfunktionen gepflegt.

Zusaetzlich koennen Stammdaten manuell aus dem Input-Ordner importiert werden. Erwartet werden die Dateien "Artikel Liste Preise.xlsx" und "Lieferkunden Liste.xlsx". Die App liest diese Excel-Dateien nur aus und schreibt keine Aenderungen in die Originaldateien zurueck.

Beim Import werden neue Kunden und Produkte in die Datenbank uebernommen. Bereits vorhandene Kunden oder Produkte werden anhand des Namens aktualisiert. Archivierte Kunden und deaktivierte Produkte bleiben archiviert beziehungsweise deaktiviert.

Preis-, Pfand- und Adressaenderungen werden als Aenderungshistorie gespeichert. Dadurch kann eine falsche Stammdatenkorrektur spaeter wieder nachvollzogen und gezielt zurueckgenommen werden.

## Listen bearbeiten

Im Bereich Listen werden offene Posten, Tageslieferungen und faellige Kundenkontakte gesammelt. Hier koennen offene Zahlungen markiert und Listen exportiert werden.

## Windows

Die App ist so vorbereitet, dass sie spaeter auf einem Windows-Rechner mit PyInstaller als ausfuehrbare Anwendung gebaut werden kann. Der erste echte Test sollte auf einem einzelnen Windows-PC mit lokalen Daten erfolgen. Erst danach sollte ein NAS-Pfad oder ein gemeinsam genutzter Ordner ausprobiert werden.
