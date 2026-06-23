# Technische Architektur: Getraenke-Tool

Diese Architektur ist die Zielreferenz fuer die weitere Entwicklung. Sie beschreibt, wohin die
Codebasis schrittweise wachsen soll, ohne den aktuell funktionierenden Stand durch grosse
Umbenennungen zu gefaehrden.

## Prinzip

Das Programm folgt einer geschichteten Architektur mit einem UI- und DB-freien Kern. Abhaengigkeiten
zeigen immer nach innen:

```text
Oberflaeche -> Vorgaenge -> Kern <- Adapter
```

Der Kern kennt weder SQLite noch PySide6 noch Dateisystem. Dadurch bleiben Rechenregeln,
Beleglogik und fachliche Entscheidungen isoliert testbar.

## Schichten

### Kern

Der Kern enthaelt einfache Modelle, reine Rechenregeln und Schnittstellen. Hier gehoeren die
Golden-Tests hin, zum Beispiel fuer Lieferschein- und Rechnungssummen.

### Vorgaenge

Vorgaenge orchestrieren je einen Geschaeftsablauf, zum Beispiel Bestellung starten, Beleg erzeugen
oder Zahlung buchen. Sie nutzen Kernregeln und Adapter ueber Schnittstellen. Sie enthalten keine
UI- und keine SQL-Details.

### Adapter

Adapter setzen die Schnittstellen konkret um: SQLite-Repositories, Excel-Erzeugung, PDF-Erzeugung,
Dateiablage in Kundenordnern und spaeter ZUGFeRD oder Mail. Adapter duerfen ausgetauscht werden,
ohne Kern und Vorgaenge umzubauen.

### Oberflaeche

Die Oberflaeche sammelt Eingaben, ruft genau den passenden Vorgang auf und zeigt Ergebnis oder
Fehler. Fachlogik gehoert nicht in die UI.

### Onboarding

Onboarding ist ein eigener Einstieg fuer Migration und Erstimport. Es liest Kundenordner, alte Excel
Dateien und zentrale Listen, schreibt ueber dieselben Repositories ins Datenrueckgrat und erzeugt
Prueffaelle fuer unsichere Treffer.

## Technologie-Entscheidungen

| Baustein | Ziel |
| --- | --- |
| Sprache | Python 3.11+ aktuell, spaeter kompatibel zu Python 3.12+ halten |
| Oberflaeche | PySide6 fuer lokale Desktop-App |
| Datenhaltung | SQLite als offene lokale Datei |
| Excel | openpyxl fuer bearbeitbare Arbeitsdateien |
| PDF | aktuell reportlab, spaeter HTML/CSS-PDF pruefen |
| E-Rechnung | spaeter ZUGFeRD/Factur-X als Adapter |
| Tests | pytest mit Kern- und Golden-File-Tests |
| Paketierung | PyInstaller fuer Windows |

## Zielstruktur

Die heutige Codebasis ist historisch gewachsen. Neue groessere Aenderungen sollen sich an dieser
Zielstruktur orientieren:

```text
src/getraenkeladen_tool/
├─ kern/                 # Modelle, reine Regeln, Ports
├─ vorgaenge/            # Use Cases / Anwendungsschicht
├─ adapter/              # SQLite, Excel, PDF, Dateiablage, spaeter Mail/ZUGFeRD
├─ onboarding/           # Migration und Erstimport
├─ ui/                   # PySide6-Oberflaeche
├─ templates/            # Belegvorlagen und Texte als Konfiguration
└─ config.py             # Pfade und Defaults
```

Bestehende `services` werden nicht blind umbenannt. Bei groesseren Arbeiten werden sie
schrittweise in Kern, Vorgaenge und Adapter getrennt.

## Datenrueckgrat

Wichtige Tabellen beziehungsweise Konzepte:

- `artikel`: zentrale Artikel mit Lieferpreis, Pfand und Aktiv-Status.
- `artikel_alias`: Schreibvarianten aus alten Excel-Dateien fuer Suche und Matching.
- `kunde`: zentrale Kundeninformationen inklusive Kontakt, Lieferhinweisen und Ordnerpfad.
- `sortiment_position`: kundenbezogene letzte Menge je Artikel.
- `bestellung` und `bestellposition`: geplante oder gespeicherte Bestellung ohne Preis-Snapshot.
- `pfand_rueckgabe`: Rueckgaben mit Pfandsatz und Menge.
- `beleg`: Rechnung oder Lieferschein mit Summen, Status und Dateiwegen.
- `beleg_position`: denormalisierter Snapshot fuer Bezeichnung, Pfand, Preis, Menge und Summe.

Kernregel: Bestellpositionen speichern keinen Preis. Der aktuelle Preis kommt beim Erfassen aus dem
zentralen Artikelstamm. Beim Finalisieren eines Belegs werden Bezeichnung, Preis und Pfand als
Snapshot eingefroren, damit alte Belege reproduzierbar bleiben.

Offene Posten sind keine eigene fachliche Welt, sondern eine Sicht auf offene Rechnungsbelege.

## Rechenregeln

Die Belegberechnung ist ein Golden-Test-Anker und soll als reine Funktion formulierbar bleiben:

```python
def berechne_beleg(positionen, ruecknahmen, parameter):
    ...
```

Verbindliche Regeln:

- Zeilensumme = `(Lieferpreis + Pfand) * Menge`.
- Lieferpauschale ist eine eigene Position und wird aktuell vom Sachbearbeiter bewusst gesetzt.
- Langfristig kann sie automatisch entfallen, wenn die Traeger-Menge groesser oder gleich 6 ist.
- Pfand-Rueckgabe wird negativ gerechnet.
- Brutto = Lieferwert + Lieferpauschale + Pfand-Rueckgabe.
- Netto = Brutto / 1,19.
- MwSt = Brutto - Netto.

## Wichtige Vorgaenge

- `bestellung_starten(kunde)`
- `aktueller_preis(artikel)`
- `beleg_erzeugen(bestellung, typ)`
- `zahlung_buchen(beleg)`
- `sepa_einzug_markieren(beleg)`
- `faellige_kontakte(stichtag)`
- `tagesliste(datum)`
- `auswertung(zeitraum)`

Eine Rechnungserzeugung folgt diesem Ablauf:

1. Bestellung und Kunde laden.
2. Aktuelle Preise und Pfand aus dem Artikelstamm ziehen.
3. Belegpositionen als Snapshot vorbereiten.
4. Summen mit Kernregel berechnen.
5. Beleg und Belegpositionen speichern.
6. Excel und PDF erzeugen und im Kundenordner ablegen.
7. Rechnung als offenen Posten sichtbar machen.
8. Kundensortiment mit letzten Mengen aktualisieren.

## Ausgabe

Briefkopf, Belegtexte, Zahlungstexte und Layoutwerte sind Konfiguration, kein UI-Code. Excel bleibt
bearbeitbar, PDF ist der verbindliche Ausdruck. ZUGFeRD wird spaeter als eigener Adapter auf Basis
derselben Belegdaten ergaenzt.

## Onboarding

Onboarding erkennt Kopffelder in alten Excel-Dateien am Inhalt, nicht an festen Zellpositionen.
Unsichere Kunden-, Artikel- und Preisentscheidungen werden nicht geraten, sondern in die Pruefliste
geschrieben. Bestaetigte Schreibweisen werden spaeter als Alias am Artikel nutzbar.

## Qualitaet

- Tests vor Verhaltenaenderungen.
- Golden-Files aus echten Belegen sind der Korrektheitsanker.
- Der Kern muss headless auf dem Mac testbar bleiben.
- Ein Smoke-Test soll den Hauptweg pruefen: Kunde oeffnen, letzte Mengen uebernehmen, Bestellung
  erstellen, Excel und PDF erzeugen.

## Ausbau

- NAS / Mehrbenutzer: Persistenz hinter Repository-Schnittstellen halten.
- Web-Variante: dieselben Vorgaenge und Kernregeln weiterverwenden.
- E-Rechnung: ZUGFeRD-Adapter ergaenzen, ohne Kern oder Vorgaenge umzubauen.

## Architektur-Invarianten

1. Der Kern haengt von nichts ab: keine UI-, DB- oder Dateisystem-Imports im Kern.
2. Persistenz und Ausgabe laufen hinter Schnittstellen.
3. Preise werden live beim Erfassen gezogen und beim Finalisieren als Snapshot gespeichert.
4. Vorlagen und Einstellungen sind Konfiguration, kein Code.
5. Daten bleiben offen exportierbar: SQLite, Excel, PDF und CSV.
6. Tests sind vor Commit gruen; Golden-Files sind der wichtigste Korrektheitsanker.
