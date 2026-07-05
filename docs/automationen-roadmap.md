# Automationen-Roadmap

Stand: 2026-07-05

Ziel: Automationen sollen die Arbeitskette beschleunigen, aber keine fachlichen Entscheidungen unsichtbar treffen. Kritische Aktionen brauchen Vorschau, klare Aenderungsliste und Bestaetigung.

## Umgesetzt am 2026-07-05

- Kunden-Schnellstart: letzte Bestellung, offene Rechnungen, Lieferhinweise und Kundenordnerstatus werden als naechste Schritte vorgeschlagen.
- Dublettenwarnung fuer aehnliche Kunden, Artikel und bereits verwendete Belegnummern.
- Plausibilitaetspruefung vor dem Speichern von Bestellungen: doppelte Nummern, hohe Mengen, Nullpreise, doppelte Artikel und Pfandabweichungen.
- Belegpruefung nach Export: angeforderte Excel-/PDF-Dateien und Snapshot-Summe werden kontrolliert.
- Kundenordner-Scan fuer neue Excel-Dateien, die noch keinem erzeugten Beleg zugeordnet sind.
- Zahlungshinweis-Vorschau fuer Ueberweisung und SEPA.
- Monatsabschluss-Check fuer ueberfaellige offene Posten, fehlende PDF/Excel-Dateien und fehlenden DATEV-Export.
- Typische Mengen aus den letzten Bestellungen als Vorschlag.
- Arbeits-Cockpit als Service: offene Pruefpunkte, fehlende Kundenordner, fehlende Kontakt-Mail und nicht zugeordnete Kundenartikel.
- Unvollstaendige Bestellungen werden vor dem Speichern erkannt: fehlende Kundenadresse, fehlende Zahlart und Bestellungen ohne positive Menge.
- Belegfolge wird geprueft: Lieferschein ohne Rechnung, doppelte Lieferscheine/Rechnungen und fehlende Excel-/PDF-Dateien werden als Arbeits-Cockpit-Punkte sichtbar.
- Kundenordner-Sync zeigt neue Excel-Dateien mit erkannter Belegnummer, Datum und gefuellten Mengenzeilen als Vorschau im Kundenkontext.
- Mengen-Vorschlaege zeigen zusaetzlich letzte Menge, typische Spanne und Bestellhaeufigkeit.
- Kundenpreis-Abweichungen gegen den Artikelstamm werden als Pruefpunkte im Arbeits-Cockpit vorbereitet.
- Import-Sicherheitspruefung trennt neu, geaendert, unsicher und uebersprungen fuer die Bestaetigung.

## Prioritaet 1: Sofort sinnvoll

### 1. Naechste Rechnungs- und Lieferscheinnummer vorschlagen

- Kontext: Beim Erzeugen eines Belegs wird heute eine Nummer eingetragen.
- Automation: Das Programm schlaegt die naechste freie Nummer auf Basis der letzten Belege vor.
- Kontrolle: Sachbearbeiter kann die Nummer vor dem Export aendern.
- Nutzen: Weniger Tippfehler und weniger doppelte Nummern.

### 2. Bestellung aus letzter Kunden-Excel vorbereiten

- Kontext: Die operative Wahrheit ist die letzte Kunden-Excel.
- Automation: Beim Kundenstart werden bekannte Artikel mit leerer Menge und letzte Mengen als Orientierung vorbereitet.
- Kontrolle: Nicht bestellte Artikel bleiben sichtbar, Mengen koennen leer bleiben oder neu gesetzt werden.
- Nutzen: Entspricht dem heutigen Arbeitsablauf und reduziert manuelle Suche.

### 3. Pfandstufen automatisch erkennen

- Kontext: Pfand-Rueckgaben laufen ueber feste Stufen wie 1,50 EUR, 3,10 EUR und 4,50 EUR.
- Automation: Das Programm zeigt nur bekannte Pfandstufen aus Kunden-Excel und Artikelstamm prominent an.
- Kontrolle: Abweichende Werte landen in der Pruefliste.
- Nutzen: Weniger Rechen- und Eingabefehler.

### 4. Offene-Rechnung-Wiedervorlage

- Kontext: Offene Rechnungen und Faelligkeit sind bereits vorhanden.
- Automation: Faellige oder ueberfaellige Rechnungen erscheinen automatisch auf "Heute".
- Kontrolle: Zahlung wird weiterhin bewusst markiert.
- Nutzen: Mahn- und Nachfassarbeit wird sichtbar.

## Prioritaet 2: Nach Import-Vorschau

### 5. Import mit Vorschau und Aenderungsliste

- Kontext: Stammdatenimport ist sensibel.
- Automation: Vor dem Import zeigt das Programm: neu, geaendert, unsicher, uebersprungen. Eine erste Sicherheitszusammenfassung ist umgesetzt.
- Kontrolle: Import startet erst nach Bestaetigung.
- Nutzen: Sicherer Import ohne Angst, bestehende Daten kaputt zu machen.

### 6. Pruefliste automatisch priorisieren

- Kontext: Pruefpunkte entstehen bei unsicheren Artikeln, Preisen und Kundendaten.
- Automation: Kritische Punkte fuer aktuelle Bestellungen, heutige Lieferungen und Rechnungen stehen oben.
- Kontrolle: Loesung bleibt manuell.
- Nutzen: Der Nutzer sieht zuerst, was den Tagesablauf blockiert.

### 7. Tagesliste automatisch vorbereiten

- Kontext: Lieferdatum, Zeitfenster, Adresse und Hinweise sind vorhanden.
- Automation: "Heute" zeigt automatisch Lieferungen, faellige Kontakte und offene Belegaufgaben.
- Kontrolle: Keine automatische Routenoptimierung in dieser Stufe.
- Nutzen: Tagesstart ohne manuelles Zusammensuchen.

## Prioritaet 3: Spaeter

### 8. Belege gesammelt erzeugen

- Kontext: Mehrere fertige Bestellungen koennen am selben Tag Belege brauchen.
- Automation: Markierte Bestellungen bekommen in einem Lauf Lieferscheine oder Rechnungen.
- Kontrolle: Vorher Vorschau aller Kunden, Nummern, Summen und Exportpfade.
- Nutzen: Spart Klicks bei vielen Standardkunden.

### 9. Exportpakete fuer Buchhaltung

- Kontext: DATEV-/PDF-Exportpfade sind vorhanden.
- Automation: Monats- oder Wochenpaket fuer Buchhaltung erzeugen.
- Kontrolle: Zeitraum und Inhalte werden vor dem Export bestaetigt.
- Nutzen: Weniger Sucharbeit bei Monatsabschluss.

### 10. Kundenkontakt-Vorschlaege

- Kontext: Kontakttermine und Bemerkungen sind vorhanden.
- Automation: Das Programm schlaegt Kunden fuer Nachfassen vor, wenn Rhythmus oder Kontakttermin faellig ist.
- Kontrolle: Anruf oder Mail passiert nicht automatisch.
- Nutzen: Bessere Kundenpflege ohne zu viel Systemzwang.

## Nicht automatisieren

- Preise nicht ohne sichtbare Bestaetigung ueberschreiben.
- Kundenkonflikte bei Mail, Telefon oder Adresse nicht automatisch aufloesen.
- Unsichere Artikel nicht automatisch einem Stammdatenartikel zuordnen.
- Belege nicht ohne Vorschau und bewussten Klick erzeugen.
- Zahlungen nicht automatisch als bezahlt markieren.
