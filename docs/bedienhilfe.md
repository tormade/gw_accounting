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
2. Nummern vorschlagen lassen oder manuell eintragen.
3. Lieferdatum und Zeitfenster eintragen.
4. Produkt waehlen, Menge pruefen und Position hinzufuegen.
5. Auftrag speichern.
6. Lieferschein und Rechnung erzeugen.

Die vorgeschlagenen Auftrags-, Lieferschein- und Rechnungsnummern koennen immer ueberschrieben werden. Wenn eine hoehere Nummer manuell eingetragen und gespeichert wird, zaehlt die App beim naechsten Vorschlag von dieser Nummer aus weiter.

Datumsfelder koennen entweder ueber den Kalender ausgewaehlt oder direkt im Format TT.MM.JJJJ eingetragen werden, zum Beispiel 21.06.2026.

Der normale Ablauf fuer Positionen ist:

1. Produkt waehlen.
2. Menge pruefen.
3. Position hinzufuegen.
4. Bei Bedarf weitere Positionen hinzufuegen.

Wenn etwas fehlt, zeigt die Statuszeile unten an, was als Naechstes zu tun ist.

## Kunden und Produkte pflegen

Neue Kunden und Produkte werden links eingetragen. Vorhandene Stammdaten werden in der Liste ausgewaehlt und mit "Auswahl bearbeiten" wieder in das Formular geladen.

Wichtig: Archivieren statt loeschen. Dadurch verschwinden Kunden oder Produkte aus dem normalen Alltag, koennen aber bei einem Fehler wiederhergestellt werden.

## Listen bearbeiten

Im Bereich Listen werden offene Posten, Tageslieferungen und faellige Kundenkontakte gesammelt. Hier koennen offene Zahlungen markiert und Listen exportiert werden.

## Windows

Die App ist so vorbereitet, dass sie spaeter auf einem Windows-Rechner mit PyInstaller als ausfuehrbare Anwendung gebaut werden kann. Der erste echte Test sollte auf einem einzelnen Windows-PC mit lokalen Daten erfolgen. Erst danach sollte ein NAS-Pfad oder ein gemeinsam genutzter Ordner ausprobiert werden.
