# Kundenordner-Zielbild Design

## Ziel

Das Programm wird vom bisherigen ERP-aehnlichen Aufbau zur gewohnten Kundenordner-Arbeitsweise umgebaut. Der Hauptweg lautet kuenftig: Kunde suchen, Kundenordner sehen, alte Excel/PDF-Dateien und letzte Mengen pruefen, neue Bestellung erfassen, Lieferschein oder Rechnung als Excel/PDF im Kundenordner erzeugen.

## Problem Im Aktuellen Stand

Die App hat technisch viele richtige Bausteine, aber die sichtbare Struktur fuehrt in die falsche Richtung. Eigene Bereiche fuer Belege, Lieferschein, Rechnung und globale Auftragsverwaltung erzeugen den Eindruck eines kleinen ERP-Systems. Das widerspricht dem Zielbild: Die Mitarbeitenden denken nicht in Modulen, sondern in Kundenordnern und vorhandenen Excel-Dateien.

## Leitentscheidung

Der Kunde wird zum Mittelpunkt. Ein Vorgang startet nicht bei einem Auftrag und nicht bei einem Beleg, sondern in einer Kundenakte, die den echten Windows-Kundenordner abbildet. Auftraege, Lieferscheine und Rechnungen bleiben technisch erhalten, werden aber aus der Kundenakte heraus bedient.

## Neue Hauptnavigation

- `Heute`: Tagesstart mit faelligen Kontakten, Lieferungen, offenen Posten und Einstieg in Kundenordner.
- `Kundenordner`: Operativer Hauptarbeitsplatz.
- `Offene Posten`: Rechnungen mit Zahlungsstatus.
- `Stammdaten`: Kunden- und Artikelpflege.
- `Pruefliste`: Migration, Preisabweichungen und Zuordnungen klaeren.
- `Einstellungen`: technische und organisatorische Einstellungen.

`Belege` wird aus der Hauptnavigation entfernt. Belege werden im jeweiligen Kundenordner angezeigt.

## Kundenordner-Arbeitsplatz

Die neue Ansicht besteht aus drei klaren Bereichen.

### 1. Kunde Finden

Links steht eine grosse Kundensuche. Die Suche zeigt Name, Adresse und wichtige Hinweise. Nach Auswahl eines Kunden wird die Kundenakte geladen.

### 2. Kundenakte

Oben werden die Kopfdaten angezeigt:

- Name und Adresse.
- Telefonnummer und Ansprechpartner, wenn vorhanden.
- Lieferhinweise, Oeffnungszeiten und interne Hinweise.
- Naechster Kontakt.
- Kundenordner-Pfad mit Aktion `Ordner oeffnen`.

Diese Ansicht ist zuerst lesend. Stammdatenbearbeitung bleibt im Bereich `Stammdaten`, damit der Hauptweg nicht mit Pflegefunktionen ueberladen wird.

### 3. Ordnerinhalt Und Letzte Bestellung

Die Kundenakte zeigt die Dateien aus dem Kundenordner:

- Excel-Rechnungen.
- PDF-Rechnungen.
- Excel-Lieferscheine.
- PDF-Lieferscheine.
- erkannte Altdateien, die noch nicht importiert wurden.

Die Liste ist nach Datum sortiert. Ein Doppelklick oeffnet die Datei. Rechtsklick bietet `Excel oeffnen`, `PDF oeffnen`, `Ordner oeffnen`, `Als neue Bestellung verwenden`, sofern die Datei auswertbar ist.

Darunter steht das Kundensortiment aus der letzten bekannten Bestellung. Die Tabelle zeigt Artikel, letzte Menge, neue Menge, zentralen Lieferpreis, Pfand und Hinweise wie `Preis pruefen`.

## Neuer Hauptablauf

1. Mitarbeiterin oeffnet `Kundenordner`.
2. Sie sucht den Kunden.
3. Sie sieht den echten Kundenordner und die letzte bekannte Bestellung.
4. Sie klickt `Neue Bestellung aus letzter Datei`.
5. Das Programm uebernimmt Mengen und Artikel aus dem Kundensortiment.
6. Die Mitarbeiterin aendert nur neue Mengen, fuegt Artikel hinzu oder entfernt Artikel.
7. Pfand-Rueckgabe und Lieferpauschale werden im selben Dialog gesetzt.
8. Sie traegt frei die Lieferschein- oder Rechnungsnummer ein.
9. Sie erzeugt Excel und/oder PDF.
10. Die Dateien landen im echten Kundenordner.

## Umgang Mit Auftraegen

Auftraege bleiben technisch bestehen, aber sie werden nicht mehr als eigener Hauptarbeitsplatz vermarktet. Im Kundenordner gibt es eine kleine Historie `Bestellungen dieses Kunden`. Dort kann eine Bestellung geoeffnet, kopiert oder archiviert werden.

Eine globale Auftragsliste ist vorerst nicht Teil der Hauptnavigation. Falls sie spaeter gebraucht wird, wird sie als Such-/Adminfunktion hinter `Einstellungen` oder `Stammdaten` versteckt, nicht als Tagesarbeitsplatz.

## Umgang Mit Belegen

Der bisherige Belegbereich wird in die Kundenakte integriert:

- Erstellte Rechnungen und Lieferscheine erscheinen beim Kunden.
- Fehlende PDF- oder Excel-Dateien koennen dort neu erzeugt werden.
- Globale Belegsuche ist nicht mehr der primaere Weg.

## Was Entfernt Oder Zurueckgestuft Wird

- Hauptnavigation `Belege`.
- separate sichtbare Seiten `Lieferbeleg` und `Rechnung`.
- globale Auftragsverwaltung als dominanter Startpunkt.
- doppelte Suchfelder fuer Beleg- und Auftragslisten.
- technische Begriffe wie `Belegbereich`, wo `Kundenordner` oder `Datei` gemeint ist.

## Was Bleibt

- Excel- und PDF-Erzeugung.
- freie Nummerneingabe.
- zentrale Artikelpreise und Preisabweichungswarnung.
- Kundensortiment aus alten Excel-Dateien.
- Archivieren statt hart loeschen.
- Pruefliste fuer unsichere Migrationsergebnisse.
- offene Posten bei Rechnungsstellung.

## Datenfluss

Die App liest Kundendaten, Kundensortiment, gespeicherte Bestellungen und Dokumente aus SQLite. Der echte Kundenordner bleibt fuer die Nutzer sichtbar und relevant. Neue Excel/PDF-Dateien werden weiterhin in `Customer.folder_path` abgelegt. Alte Excel-Dateien dienen als Migrations- und Referenzquelle; zentrale Preise bleiben fuehrend.

## Fehler Und Sicherheitsverhalten

- Wenn der Kundenordner fehlt, zeigt die Kundenakte eine klare Warnung und bietet an, den Pfad in `Stammdaten` zu korrigieren.
- Wenn eine alte Excel-Datei nicht gelesen werden kann, bleibt sie als Datei sichtbar, aber `Als neue Bestellung verwenden` ist deaktiviert.
- Wenn ein Preis aus einer alten Datei vom zentralen Preis abweicht, fragt die App wie bisher, ob der zentrale Preis uebernommen werden soll.
- Wenn Excel oder PDF nicht erzeugt werden kann, erscheint eine Meldung mit Grund und Zielordner.

## Teststrategie

- UI-Tests sichern die neue Navigation ohne `Belege` als Haupttab.
- Service-Tests sichern eine kundenbezogene Dokumentliste.
- UI-Tests sichern, dass der Kundenordner-Arbeitsplatz Kundensuche, Ordnerpfad, Dateiliste, Kundensortiment und Aktionen enthaelt.
- Bestehende Excel-/PDF-Tests bleiben unveraendert und sichern die Ausgabe.
- Ein End-to-End-Test spielt den Hauptweg durch: Kunde waehlen, Sortiment uebernehmen, Bestellung speichern, Lieferschein oder Rechnung erzeugen, Datei im Kundenordner finden.

## Nicht In Diesem Umbau

- Mehrplatzbetrieb.
- E-Mail-Versand.
- ZUGFeRD/E-Rechnung.
- vollautomatische Routenplanung.
- neue Buchhaltungslogik ausser bestehender offener Posten.

## Erfolgskriterium

Eine Person, die bisher mit Kundenordnern und Excel gearbeitet hat, soll nach dem Start der App ohne Erklaerung verstehen: Ich suche zuerst den Kunden, sehe seinen Ordner und mache daraus die neue Lieferung oder Rechnung.
