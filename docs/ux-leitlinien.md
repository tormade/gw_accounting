# UX-Leitlinien fuer das Winklmeier Buero-Werkzeug

Diese Leitlinien uebertragen das Konzept in konkrete Produktregeln fuer die aktuelle PySide6-App. Zielgruppe sind Mitarbeitende, die bisher vor allem mit Excel gearbeitet haben und im Arbeitsalltag schnell, sicher und ohne IT-Frust arbeiten muessen.

## Grundprinzip

Die App fuehrt durch wenige klare Arbeitsschritte. Sie soll nicht wie ein technisches Verwaltungsprogramm wirken, sondern wie ein ruhiger Buero-Assistent: Starten, Kunde waehlen, Lieferung erfassen, Belege erzeugen, offene Aufgaben pruefen.

## Bedienregeln

1. **Startseite mit einem Hauptweg:** Der wichtigste Einstieg ist immer `Neue Lieferung erfassen`. Tageskarten fuer offene Posten, Lieferungen und Kontakte bleiben sichtbar, aber sie konkurrieren nicht mit dem Hauptweg.
2. **Kundenorientierter Ablauf:** Neue Vorgange starten beim Kunden. Perspektivisch soll `Letzte Bestellung uebernehmen` ein zentraler Komfortschritt werden, weil viele Getraenkeauftraege wiederkehrend sind.
3. **Sinnvolle Vorschlaege:** Auftrags-, Lieferschein- und Rechnungsnummern werden vorgeschlagen, bleiben aber manuell ueberschreibbar. Das Programm zaehlt nach manuellen Nummern weiter.
4. **Tolerante Entwuerfe:** Eingaben duerfen korrigierbar bleiben. Stammdaten werden nicht hart geloescht, sondern archiviert, deaktiviert oder wiederhergestellt.
5. **Papiernahe Belege:** Rechnung und Lieferschein sollen optisch moeglichst nah an die bekannte Vorlage und das bestehende Briefpapier herankommen.
6. **Deutsche Buero-Sprache:** Beschriftungen sollen konkrete Arbeitsbegriffe nutzen, zum Beispiel `Auftrag speichern`, `Lieferschein erzeugen`, `Kunde archivieren`.
7. **Grosse, eindeutige Aktionen:** Wichtige Buttons stehen dort, wo der Arbeitsschritt passiert. Nebenschritte bleiben kleiner oder in Kontextmenues.
8. **Weniger Listen auf einmal:** Listen helfen beim Pruefen, duerfen den Anwender aber nicht erschlagen. Wo moeglich werden Suche, Filter und Kontextaktionen statt vieler paralleler Tabellen genutzt.
9. **Datumseingabe freundlich:** Datumsfelder erlauben Tastatureingabe im Format `DD.MM.JJJJ` und Kalenderauswahl.
10. **Einstellungen klar benennen:** Einstellungsbereiche sagen, welche Liste bearbeitet wird, zum Beispiel `Produkteinheiten bearbeiten` statt allgemein `Dropdown-Listen`.

## Bewusste Entscheidungen

- Die App bleibt zuerst lokal und einfach installierbar. NAS- oder Mehrbenutzerbetrieb ist spaeter moeglich, aber nicht Voraussetzung fuer die erste nutzbare Version.
- `PDF + E-Mail` bleibt vorerst ausgeklammert. PDF-Erzeugung ist wichtiger; E-Mail-Versand braucht spaeter ein sauberes Sicherheits- und Kontokonzept.
- Die aktuelle technische Richtung bleibt PySide6, weil sie lokal auf Mac und Windows laufen kann und gut zu Excel/PDF-Erzeugung passt.
- HTML/CSS kann spaeter fuer Beleglayout oder Vorschau interessant sein, ersetzt aber aktuell nicht die Desktop-App.

## Offene UX-Ausbaustufen

- `Letzte Bestellung uebernehmen` fuer wiederkehrende Kundenauftraege.
- Noch klarere Beleg-Vorschau, die wie eine Papier-Rechnung wirkt.
- Einfachere Listenansicht mit Filtern statt dauerhaft vielen Tabellen.
- Kurzanleitung direkt im Programm fuer die haeufigsten Arbeitsschritte.
