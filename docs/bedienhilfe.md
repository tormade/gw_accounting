# Bedienhilfe Getraenkeladen Tool

Diese App ist fuer den lokalen Bueroalltag gedacht. Sie soll nicht wie ein grosses ERP wirken, sondern Schritt fuer Schritt durch die wichtigsten Aufgaben fuehren.

## Startseite

Die Startseite ist der erste Blick in den Arbeitstag. Dort sehen Sie:

- Lieferungen heute
- Offene Posten
- Kontaktanfragen heute

Wenn hier etwas angezeigt wird, ist das der naechste Arbeitsvorrat. Danach wechseln Sie in den passenden Bereich: Auftraege, Listen, Kunden oder Produkte.

## Auftrag erfassen

Der normale Ablauf ist:

1. Stammdaten laden und Kunden waehlen.
2. Auftragsnummer vorschlagen lassen oder manuell eintragen.
3. Lieferdatum und Zeitfenster eintragen.
4. Produkt waehlen, Menge pruefen und Position hinzufuegen.
5. Auftrag speichern.
6. Bei Bedarf Lieferscheinnummer oder Rechnungsnummer vorschlagen lassen.
7. Lieferschein und Rechnung erzeugen.

Auftrags-, Lieferschein- und Rechnungsnummern werden einzeln vorgeschlagen. Jede Nummer kann immer ueberschrieben werden. Wenn eine hoehere Nummer manuell eingetragen und gespeichert wird, zaehlt die App beim naechsten Vorschlag von dieser Nummer aus weiter.

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

In den Listen fuer Kunden, Produkte und Auftraege koennen Eintraege per Rechtsklick bearbeitet, archiviert oder wiederhergestellt werden. Doppelklick laedt einen Eintrag ebenfalls zur Bearbeitung.

Wichtig: Archivieren statt loeschen. Dadurch verschwinden Kunden oder Produkte aus dem normalen Alltag, koennen aber bei einem Fehler wiederhergestellt werden.

## Einstellungen

Im Bereich Einstellungen werden zentrale Auswahlwerte gepflegt. Aktuell koennen dort Produkteinheiten wie Kiste, Flasche, Fass oder Karton erweitert werden. Diese Werte erscheinen im Feld "Einheit" bei Produkten.

Zusaetzlich koennen Stammdaten manuell aus dem Input-Ordner importiert werden. Erwartet werden die Dateien "Artikel Liste Preise.xlsx" und "Lieferkunden Liste.xlsx". Die App liest diese Excel-Dateien nur aus und schreibt keine Aenderungen in die Originaldateien zurueck.

Beim Import werden neue Kunden und Produkte in die Datenbank uebernommen. Bereits vorhandene Kunden oder Produkte werden anhand des Namens aktualisiert. Archivierte Kunden und deaktivierte Produkte bleiben archiviert beziehungsweise deaktiviert.

Preis-, Pfand- und Adressaenderungen werden als Aenderungshistorie gespeichert. Dadurch kann eine falsche Stammdatenkorrektur spaeter wieder nachvollzogen und gezielt zurueckgenommen werden.

## Listen bearbeiten

Im Bereich Listen werden offene Posten, Tageslieferungen und faellige Kundenkontakte gesammelt. Hier koennen offene Zahlungen markiert und Listen exportiert werden.

## Windows

Die App ist so vorbereitet, dass sie spaeter auf einem Windows-Rechner mit PyInstaller als ausfuehrbare Anwendung gebaut werden kann. Der erste echte Test sollte auf einem einzelnen Windows-PC mit lokalen Daten erfolgen. Erst danach sollte ein NAS-Pfad oder ein gemeinsam genutzter Ordner ausprobiert werden.
