# Roadmap

Diese Roadmap uebersetzt den Umsetzungsplan in den aktuellen Projektstand. Sie ist bewusst praktisch gehalten: Was ist da, was ist in Arbeit, was kommt spaeter?

| Meilenstein | Ziel | Status |
| --- | --- | --- |
| Meilenstein 0 | Projektbasis, Datenbank, lokale App-Struktur, Beispieldaten | weitgehend umgesetzt |
| Meilenstein 1 | Kunden- und Produktstammdaten mit Bearbeiten, Archivieren und Wiederherstellen | umgesetzt, UX weiter verbessern |
| Meilenstein 2 | Gefuehrter Ablauf: Lieferung erfassen, Excel und PDF erzeugen | in Arbeit |
| Meilenstein 3 | Offene Posten automatisch anzeigen und als bezahlt markieren | teilweise umgesetzt |
| Meilenstein 4 | Lieferliste pro Tag mit Tour-/Zeitinformationen | teilweise umgesetzt |
| Meilenstein 5 | Auswertungen, Serienbriefe, E-Mail-Komfort | spaeter; E-Mail vorerst ausgeklammert |
| Meilenstein 6 | Aufraeumen, Einstellungen, Bedienfuehrung fuer nicht-technische Nutzer | laufend |
| Meilenstein 7 | E-Rechnung / ZUGFeRD | spaeter, nach stabiler PDF-/Rechnungslogik |
| Meilenstein 8 | NAS-/Mehrbenutzerbetrieb im lokalen Netzwerk | spaeter, nach lokaler Einzelplatzversion |

## Technische Architektur

Die Zielarchitektur ist in `docs/technische-architektur.md` festgehalten. Der aktuelle Code wird
nicht per grossem Schnitt umgebaut; stattdessen werden neue oder groessere Aenderungen schrittweise
in Kernregeln, Vorgaenge, Adapter und UI-Schale getrennt. Wichtigster naechster Architekturpunkt:
Belegberechnung und Belegerzeugung weiter aus der UI und aus breit gewachsenen Services loesen,
damit Excel, PDF und spaeter ZUGFeRD dieselben geprueften Belegdaten verwenden.

## Naechste fachliche Schritte

1. `Letzte Bestellung uebernehmen` fuer Kundenauftraege konzipieren und danach umsetzen.
2. Belegerzeugung an die echte Excel-Vorlage und das Winklmeier-Briefpapier anpassen.
3. Listenbereich vereinfachen: weniger Tabellen gleichzeitig, mehr gefuehrte Auswahl.
4. PDF-Vorschau oder Belegkontrolle vor dem Speichern pruefen.
5. Windows-Test durchfuehren, sobald ein Zielrechner verfuegbar ist.
