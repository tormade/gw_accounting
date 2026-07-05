# UAT- und Regressionstest 2026-06-24

## Umfang

Geprueft wurde der aktuelle Stand der lokalen Getraenkeladen-Desktop-App gegen das Zielbild:

- Kundenordner-Hauptweg
- Bestellung aus letzten Mengen
- Lieferschein und Rechnung als Excel/PDF
- Belegberechnung, Snapshot und offene Posten
- Stammdatenimport, Onboarding, Kundensortiment und Pruefliste
- Tageslisten, Kontakte und CSV-Exporte
- UI-Navigation und Bedienrisiken

Die GUI wurde mit einer isolierten UAT-Datenbank unter `/private/tmp/getraenkeladen-uat` gestartet. Das native Qt-Fenster war fuer Computer Use auf diesem Mac nicht als bedienbares App-Fenster erreichbar; der Prozess lief, aber `get_app_state` fuer `Python` lief in Timeouts. Der manuelle Klick-UAT wurde deshalb nicht vollstaendig per Computer Use abgeschlossen.

## Ausgefuehrte Checks

```text
/Users/thomasrumel/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest -q
212 passed
```

```text
/Users/thomasrumel/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_daily_workflow.py tests/test_report_service.py tests/test_customer_folder_service.py tests/test_checklist_service.py tests/test_onboarding_service.py tests/test_master_data_import_service.py -q
26 passed
```

```text
/Users/thomasrumel/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m compileall -q src tests
OK
```

Zusaetzlicher Service-UAT gegen temporare Datenbank:

- 4 Demo-Kunden erzeugt
- 4 Demo-Artikel erzeugt
- 40 Demo-Bestellungen erzeugt
- 4 Belege erzeugt
- 9 Beleg-Snapshot-Zeilen erzeugt
- 2 offene Posten erzeugt
- Dashboard fuer `2026-06-24`: 2 Lieferungen, 2 offene Posten, 3 faellige Kontakte
- CSV-Exporte fuer offene Posten, Lieferungen und Kontakte erzeugt
- Alle erzeugten Excel-/PDF-Pfade existieren
- Alle erzeugten PDFs beginnen mit `%PDF-`

## Ergebnis

### Bestanden

- Kernberechnung fuer Belege inklusive Metzgerei-Karl-Goldenwerte.
- Excel-/PDF-Erzeugung fuer Lieferschein und Rechnung.
- Beleg-Snapshot-Zeilen fuer Positionen, Pfand-Rueckgaben, Lieferpauschale und Brutto.
- Offene Posten werden bei Rechnungserzeugung angelegt und nutzen den Snapshot-Brutto.
- Bestellung -> Lieferschein -> Rechnung aktualisiert Bestellstatus.
- DATEV-PDF-Kopie fuer Rechnungen.
- Kundenordner-Snapshot findet erzeugte Excel/PDF-Dateien.
- Stammdatenimport und Onboarding-Goldenpfad laufen automatisiert.
- Prueflisten-Entscheidungen fuer Preise, Alias und Kundendaten sind service-seitig getestet.
- Dashboard-/Reportdaten und CSV-Exporte funktionieren service-seitig.
- UI-Vertraege fuer Navigation, Kundenordner, Suchfelder, Bestelldialog und Belegdialog sind automatisiert abgedeckt.

### Nicht vollstaendig bestanden / nicht vollstaendig testbar

- Native Bedienung per Computer Use konnte nicht abgeschlossen werden, weil das Qt-Fenster auf diesem Mac nicht als bedienbares App-Fenster erkannt wurde.
- Windows-spezifisches Verhalten wurde nicht getestet: Explorer-Oeffnen, PyInstaller-Paket, echte Windows-Kundenordnerpfade, Druck-/Office-Integration.
- Datei-Oeffnen ueber `QDesktopServices` wurde nicht real per GUI bestaetigt.
- Visuelle Regression auf kleinen Windows-Bildschirmen wurde nicht per Screenshot verifiziert.

## Fachliche Befunde

### P1: Zahlart steuert Rechnungstext noch nicht automatisch

Soll laut AGENTS-Regel:

- SEPA fuehrt zu Lastschrifttext.
- Ueberweisung fuehrt zu Ueberweisungstext mit Faelligkeit Datum + 7.

Ist-Stand:

- Der Rechnungspanel-Default ist SEPA-nahe und nicht erkennbar automatisch an den Kunden gekoppelt.
- Der Ueberweiser-Goldenfall ist im Onboarding vorhanden, aber nicht als aktueller Belegfluss-Automatismus abgesichert.

UAT-Erwartung: Ueberweisungskunde erzeugt automatisch den passenden Fuss-/Hinweistext inklusive Faelligkeitsdatum.

### P1: Teil-Export kann Belegwahrheit auseinanderziehen

Ist-Stand:

- `assets={"excel"}` und spaeter `assets={"pdf"}` schreiben Snapshot und offenen Posten jeweils neu.
- Wenn zwischen beiden Schritten Positionen geaendert werden, koennen Excel, PDF, Snapshot und offener Posten fachlich auseinanderlaufen.

UAT-Erwartung: Die App verhindert Divergenz oder verlangt bewusstes Neu-Erzeugen beider Ausgaben.

### P1: Offene Posten sind gegen Zielbild noch unvollstaendig

Zielbild verlangt Kunde, Rechnungsnummer, Datum, Betrag, Zahlart, Faelligkeit und Status sowie getrennte Sicht auf SEPA/Ueberweisung.

Ist-Stand:

- `OpenItem` speichert Kunde, Rechnungsnummer, Betrag, Zahlart und Status.
- Datum, Faelligkeit, Ueberfaellig-Markierung und Zahlart-Filter fehlen.
- CSV exportiert nur Kunde, Rechnungsnummer, Betrag und Status.

### P2: Offene Preisentscheidungen koennen beim Vorbefuellen automatisch Zentralpreise nutzen

Ist-Stand:

- Kundensortiment liefert bei offener Preisabweichung den zentralen Preis als aktuellen Preis.
- Automatisches Vorbefuellen aus letzten Mengen uebernimmt diesen Wert.
- Die manuelle Einzeluebernahme fragt dagegen bei offenen Preisabweichungen nach.

UAT-Erwartung: Offene Preisabweichung muss beim Start aus letzten Mengen sichtbar bewusst entschieden oder ausgelassen werden.

### P2: Re-Onboarding ist vermutlich nicht idempotent

Ist-Stand:

- Onboarding legt Prueffaelle ohne erkennbare Dublettenpruefung erneut an.
- Preisabweichungen koennen bestaetigte Entscheidungen wieder auf `offen` setzen.

UAT-Erwartung: Wiederholter Import derselben Quellen erzeugt keine doppelten Prueffaelle und setzt erledigte Entscheidungen nicht zurueck.

### P2: Kundendaten-Konflikt-Label ist uneinheitlich

Ist-Stand:

- UI/Label spricht von Kundendatenkonflikt.
- Aufloesung arbeitet intern mit `merge_conflict`.
- Risiko: Rohwert oder uneinheitlicher Text erscheint in der Pruefliste.

### P2: Onboarding erkennt Kopf flexibel, Positionsbereiche aber noch teilweise fest

Ist-Stand:

- Kopfbereich wird nach Inhalt erkannt.
- Artikelzeilen, Pfand-Rueckgaben und Lieferpauschale haengen noch an festen Bereichen/Zellen.

UAT-Erwartung: Echte Ausreisser mit verschobenen Positionsbereichen werden sauber gemeldet und uebersprungen, nicht falsch importiert.

## Empfohlene naechste Schritte

1. Echten Windows-UAT mit komplettem Kundenordner durchfuehren: Import, Kundenordner-Start, Bestellung, Lieferschein, Rechnung, Excel/PDF, offene Posten, Explorer-Oeffnen.
2. Visuellen UAT auf kleinem Windows-Bildschirm nachholen, inklusive Belegdialog und Bestelldialog.
3. Onboarding-Ausreisser mit verschobenen Positionsbereichen aus echten Dateien sammeln und als weitere Golden-Files aufnehmen.

## Fix-Nachtrag

Nach diesem UAT wurden die fachlichen Befunde aus diesem Bericht im Code adressiert:

- Zahlart-gesteuerte Rechnungstexte inklusive Ueberweisung-Faelligkeit +7.
- Teil-Export-Schutz gegen auseinanderlaufende Excel/PDF/Snapshot-Daten.
- Offene Posten mit Rechnungsdatum, Faelligkeit, Zahlart und erweitertem CSV-Export.
- Automatisches Vorbefuellen aus Kundensortiment laesst offene Preisabweichungen aus.
- Re-Onboarding erzeugt keine doppelten Pruefpunkte und erhaelt bestaetigte Preisentscheidungen.
- `merge_conflict` wird in der Pruefliste als Kundendaten-Konflikt beschriftet.

Verifikation nach Fix:

```text
/Users/thomasrumel/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest -q
219 passed
```

```text
/Users/thomasrumel/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m compileall -q src tests
OK
```
