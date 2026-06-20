# Design: Lokales Windows-Tool fuer Rechnungen, Lieferscheine und Listen

## Ziel

Fuer den Getraenkeladen soll ein kleines Windows-Programm entstehen, das die heutige Excel-basierte Arbeitsweise verbessert, ohne ein grosses ERP-System einzufuehren. Die Loesung soll lokal im eigenen Netzwerk einsetzbar sein, zunaechst aber auf einem einzelnen Windows-Rechner laufen.

Das Tool soll keine revisionssichere Vollhistorie fuehren. Es ist ein pragmatisches Arbeitswerkzeug. Verbindliche Ausgabedokumente sind die erzeugten PDF-Dateien fuer Rechnungen und Lieferscheine. Zusaetzlich sollen bearbeitbare Excel-Dateien erzeugt und in der bestehenden Ordnerstruktur abgelegt werden koennen.

## Rahmenbedingungen

- Einsatz zuerst auf genau einem Windows-PC
- Keine Cloud in Phase 1
- Daten bleiben lokal im Laden bzw. spaeter optional auf NAS/LAN
- Bestehende Ordnerstruktur pro Kunde soll erhalten bleiben
- Excel-Arbeitsweise soll weiterhin moeglich sein
- PDFs fuer Rechnungen und Lieferscheine gelten als unveraenderbare Ausgabe
- Rechnungsnummern bleiben in Phase 1 manuell, passend zum bestehenden Papierzettel
- Das Tool soll intern nicht als nachvollziehbares ERP oder Buchhaltungssystem auftreten
- Perspektivisch soll spaeter eine Erweiterung fuer E-Rechnungen, insbesondere ZUGFeRD, moeglich sein
- Die Bedienoberflaeche soll sich optisch an der bestehenden Winklmeier-Website orientieren

## Corporate Design

Die App soll die bestehende Winklmeier-Wirkung aufgreifen: familiaer, regional, klar und serviceorientiert. Als Referenz dient die Website https://www.getraenke-winklmeier.de mit sichtbaren Elementen wie dem Getraenke-Winklmeier-Logo, dem Claim "Wir bringen's einfach", dem Lieferservice-Fokus, Schwarz-Weiss-Logoeinsatz und regionalen/familiaeren Akzenten.

Fuer die Umsetzung gilt:

- echtes Logo nur aus einer bereitgestellten Originaldatei oder mit ausdruecklicher Freigabe verwenden
- Website nicht 1:1 kopieren, sondern als Corporate-Design-Referenz nutzen
- UI bleibt ein Arbeitswerkzeug, keine Marketingseite
- Farben, Schriftwirkung, Buttons und PDF-Briefkopf sollen zum bestehenden Auftritt passen
- Belege und PDFs sollen langfristig denselben Wiedererkennungswert wie Website und Briefpapier haben

## Empfohlener Ansatz

Empfohlen wird ein kleines Windows-Desktopprogramm mit lokaler Datenhaltung und dateibasierter Ablage.

Das Programm verwaltet Stammdaten und Arbeitsablaeufe in einer schlanken internen Struktur, erzeugt aber nach aussen weiterhin genau die Artefakte, mit denen der Betrieb heute arbeitet:

- Excel-Dateien pro Vorgang
- PDF-Rechnungen und PDF-Lieferscheine
- Ablage in Kundenordnern
- Listen fuer offene Posten, Lieferungen und Kontakte

Damit entsteht ein sinnvoller Mittelweg zwischen zu viel Technik und zu wenig Struktur.

## Phase-1-Umfang

### 1. Kundenpflege

Pflege von Kundendaten mit mindestens folgenden Feldern:

- Kundenname
- Adresse
- Ansprechpartner
- Kontaktdaten
- Zahlungsart, z. B. SEPA oder Ueberweisung
- Naechstes Kontaktdatum
- Lieferhinweise
- Oeffnungszeiten
- Interne Zusatzinformationen
- Zielordner fuer die Ablage

### 2. Produkt- und Preispflege

Zentrale Artikelliste mit:

- Artikelname
- Gebinde oder Einheit
- Standardpreis
- optional Artikelnummer
- optional Aktiv/Inaktiv-Status

Die Preisliste wird zentral gepflegt und bei neuen Belegen als Standard verwendet.

### 3. Beleg erstellen

Benutzer kann fuer einen Kunden einen neuen Vorgang erstellen und dabei:

- Rechnung oder Lieferschein auswaehlen
- Rechnungsnummer manuell eintragen
- Positionen aus der Produktliste waehlen
- Mengen erfassen
- Preise bei Bedarf im Einzelfall anpassen
- Zusatztexte oder Hinweise erfassen

### 4. Dokumente erzeugen

Aus einem Vorgang werden erzeugt:

- eine bearbeitbare Excel-Datei
- eine PDF-Datei mit Briefkopf fuer Rechnung oder Lieferschein

Die Dateien werden automatisch im zugehoerigen Kundenordner gespeichert.

### 5. Offene-Posten-Liste

Bei Rechnungserstellung wird automatisch ein Eintrag in einer offenen Postenliste angelegt, mindestens mit:

- Rechnungsnummer
- Kunde
- Rechnungsdatum
- Betrag
- Zahlungsart
- Status offen/bezahlt
- Kennung fuer SEPA oder Ueberweisung

Zahlungseingaenge koennen manuell abgehakt werden. Bei SEPA kann auch festgehalten werden, dass der Einzug vorgenommen wurde.

### 6. Tageslieferuebersicht

Das Tool soll eine Auswertung erzeugen, welche Lieferungen an einem Tag anstehen. Pro Eintrag sollen mindestens sichtbar sein:

- Kunde
- Adresse
- Vormittag/Nachmittag
- Lieferhinweise
- Bezug zum erzeugten Vorgang

Eine automatische Routenoptimierung ist bewusst nicht Teil von Phase 1.

### 7. Kontaktliste und Anschreiben

Das Tool soll Kunden mit faelligem Kontaktdatum auflisten und die Basis fuer ein Anschreiben liefern, um Bestellungen anzufragen. Der konkrete Versand kann in Phase 1 einfach gehalten werden, zum Beispiel durch Export oder Erzeugung eines Serienbrief-Dokuments.

## Was bewusst nicht in Phase 1 enthalten ist

- keine Cloud-Anbindung
- kein Mehrbenutzerbetrieb
- keine automatische Tourenplanung
- keine vollstaendige Buchhaltung
- keine revisionssichere Historie
- keine automatische Vergabe von Rechnungsnummern
- keine vollstaendig umgesetzte ZUGFeRD-Erzeugung

## Technischer Zuschnitt

### Anwendungstyp

Windows-Desktop-App.

Begruendung:

- passt zur Arbeitsumgebung der Nutzer
- einfache Bedienung fuer nicht-technische Anwender
- lokale Dateizugriffe auf Ordner und Excel/PDF-Ausgaben sind unkompliziert
- spaeter kann eine Netzlaufwerk- oder NAS-Ablage ergaenzt werden

### Datenhaltung

In Phase 1 keine Server-Datenbank. Stattdessen lokale, schlanke Datenhaltung fuer:

- Kundenstammdaten
- Produktstammdaten
- Einstellungen
- Vorlagenkonfiguration
- offene Posten

Wichtig ist nicht die konkrete Technologie, sondern dass die Datenhaltung:

- einfach zu sichern ist
- lokal auf einem Rechner laeuft
- spaeter auf gemeinsame Nutzung vorbereitet werden kann

### Dateisystem und Ablage

Die bestehende Ordnerlogik pro Kunde bleibt erhalten. Das Tool legt Dokumente in definierte Kundenordner ab und kann dort vorhandene Excel-Dateien referenzieren oder neue erzeugen.

### Dokumentgenerator

Das Tool benoetigt eine Komponente, die:

- Excel-Dateien nach Vorlage erzeugt
- PDF-Dateien mit Briefkopf erzeugt
- spaeter strukturierte Belegdaten fuer E-Rechnungen bereitstellen kann

## Datenfluss

1. Benutzer waehlt Kunde oder legt einen neuen Kunden an.
2. Benutzer startet neuen Vorgang.
3. Benutzer waehlt Belegtyp, traegt Rechnungsnummer ein und erfasst Positionen.
4. Das Tool uebernimmt Standardpreise aus der Produktliste.
5. Das Tool erzeugt Excel-Datei und PDF-Datei.
6. Das Tool speichert beide Dateien im Kundenordner.
7. Falls der Vorgang eine Rechnung ist, wird automatisch ein Eintrag in die offene Postenliste geschrieben.
8. Falls ein Lieferdatum gesetzt ist, erscheint der Vorgang in der Tageslieferuebersicht.
9. Falls ein Kontaktdatum erreicht ist, erscheint der Kunde in der Kontaktliste.

## Fehlerbehandlung

Das Tool soll alltagsrobust sein und einfache, konkrete Fehlermeldungen liefern. Wichtige Faelle:

- Kundenordner fehlt oder ist nicht erreichbar
- Vorlage fehlt oder ist beschaedigt
- Pflichtfelder fehlen
- Rechnungsnummer wurde nicht eingetragen
- PDF oder Excel konnte nicht geschrieben werden
- Offene-Posten-Liste konnte nicht aktualisiert werden

Fehler sollen den Nutzer nicht mit technischen Details ueberfordern, sondern mit klaren Hinweisen, was zu tun ist.

## Erweiterbarkeit

Die Architektur soll von Anfang an so geschnitten sein, dass spaeter folgende Ausbaustufen moeglich sind:

- gemeinsame Nutzung ueber NAS oder internes Netzwerk
- echte Mehrbenutzerfaehigkeit
- E-Rechnungen/ZUGFeRD
- E-Mail-Versand direkt aus dem Tool
- weitergehende Auswertungen

Deshalb sollten Belegdaten intern strukturiert gespeichert werden, auch wenn in Phase 1 hauptsaechlich Excel und PDF im Vordergrund stehen.

## Teststrategie

Vor der Einfuehrung sollten mindestens diese Faelle getestet werden:

- Kunde anlegen und bearbeiten
- Produktpreise pflegen
- Rechnung mit mehreren Positionen erzeugen
- Lieferschein erzeugen
- Excel-Ausgabe im richtigen Kundenordner
- PDF-Ausgabe mit Briefkopf
- Offene-Posten-Eintrag nach Rechnung
- Zahlungseingang abhaken
- Tageslieferuebersicht mit Vormittag/Nachmittag
- Kontaktliste fuer faellige Kunden
- Verhalten bei fehlendem Ordner oder fehlender Vorlage

## Empfohlene Umsetzungsreihenfolge

1. Stammdaten und Ordnerkonzept festziehen
2. Rechnung/Lieferschein-Erzeugung mit Excel und PDF umsetzen
3. Offene Posten automatisch anbinden
4. Tageslieferliste und Kontaktliste ergaenzen
5. spaetere ZUGFeRD-Erweiterung vorbereiten

## Offene bewusste Entscheidungen

Diese Punkte sind absichtlich fuer die Implementierungsplanung aufgehoben, ohne den Entwurf zu blockieren:

- konkrete Technologie fuer die Windows-Oberflaeche
- konkretes Format der lokalen Datenhaltung
- exakte Struktur der Excel-Vorlagen
- Art des Serienbrief-Exports

Diese Entscheidungen koennen im naechsten Schritt anhand von Aufwand, Wartbarkeit und Windows-Kompatibilitaet getroffen werden.
