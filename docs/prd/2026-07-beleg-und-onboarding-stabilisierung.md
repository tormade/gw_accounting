# PRD: Beleg- und Onboarding-Stabilisierung

## Problem Statement

Die bisherige Arbeitsweise verwendet je Kunde alte Excel-Belege als Vorlage. Dadurch sind Zahlart, Mengen und Lieferhinweise vorhanden, aber die Mitarbeitenden verlieren den Ueberblick ueber aktuelle Preise. Gleichzeitig soll die neue zentrale Artikeldatenbank der verbindliche Ausgangspunkt sein, ohne notwendige Einzelfallkorrekturen unmittelbar vor der Rechnungsstellung zu verhindern. Erzeugte Rechnungen muessen anschliessend reproduzierbar bleiben, auch wenn eine Excel-Datei spaeter bearbeitet oder geloescht wird.

Das Onboarding muss Informationen aus alten Kunden-Excels sicher uebernehmen, ohne Kunden oder Artikel bei unsicheren Treffern automatisch zusammenzufuehren.

## Solution

Das Programm erzeugt aus einer mengenorientierten Bestellung und dem zentralen Artikelstamm einen Belegentwurf. Preis und Pfand werden dort zentral vorbelegt und duerfen fuer eine einzelne Belegposition vor dem Finalisieren angepasst werden. Beim Finalisieren entsteht ein verbindlicher Beleg-Snapshot. Excel, PDF, offene Posten und spaetere Neuerzeugungen verwenden diesen Snapshot.

Die Zahlart wird beim Erstimport aus der juengsten Kunden-Excel uebernommen und danach zentral am Kunden gepflegt. Sie bestimmt den Rechnungstext; bei Ueberweisung wird die Faelligkeit aus Rechnungsdatum plus sieben Kalendertagen abgeleitet. Unsichere Kunden- und Artikelzuordnungen werden als Prueffaelle vorgelegt.

## User Stories

1. Als Sachbearbeitung moechte ich beim Rechnungsentwurf immer den zentral gepflegten Artikelpreis sehen, damit aktuelle Preise nicht in einzelnen Kunden-Excels verloren gehen.
2. Als Sachbearbeitung moechte ich einen Preis oder Pfandwert vor dem Finalisieren fuer diese eine Rechnung aendern, damit ein vereinbarter Einzelfall moeglich bleibt.
3. Als Sachbearbeitung moechte ich, dass ein einmaliger Belegpreis den Artikelstamm nicht veraendert, damit kuenftige Rechnungen weiter den zentralen Preis verwenden.
4. Als Sachbearbeitung moechte ich einen finalisierten Beleg jederzeit identisch erneut als Excel oder PDF erzeugen, damit verlorene Ausgaben wiederherstellbar sind.
5. Als Sachbearbeitung moechte ich, dass der Rechnungstext der Zahlart des Kunden folgt, damit SEPA- und Ueberweisungsrechnungen korrekt sind.
6. Als Sachbearbeitung moechte ich bei Ueberweisung eine automatisch berechnete Faelligkeit sehen, damit Rechnungen ein klares Zahlungsziel haben.
7. Als Sachbearbeitung moechte ich Kontakt- und Rechnungs-E-Mail getrennt verwalten, damit spaeter die richtige Empfaengeradresse verfuegbar ist.
8. Als Sachbearbeitung moechte ich Zahlarten aus alten Kunden-Excels einmalig in den Kundenstamm uebernehmen, damit die bestehende Ablage als Migrationsquelle dient.
9. Als Sachbearbeitung moechte ich unklare Artikel- und Kundenabgleiche bestaetigen, damit keine falschen Preise oder Kundenbeziehungen uebernommen werden.
10. Als Sachbearbeitung moechte ich nach dem Onboarding im Programm arbeiten, waehrend die alten Excel-Dateien nachvollziehbarer Nachweis bleiben.

## Implementation Decisions

- Ein UI-freier Belegvorgang bildet die zentrale Testnaht: Bestellung und Artikelstamm ergeben einen Belegentwurf; der finale Snapshot ist die verbindliche Ausgabequelle.
- Bestellungen bleiben mengenorientiert. Die zentrale Preis- und Pfandauflosung erfolgt im Belegentwurf, nicht durch einen verbindlichen Bestellpreis.
- Ein einmaliger Belegpreis ist nur im Entwurf moeglich und wirkt ausschliesslich auf den finalen Snapshot dieses Belegs.
- Der Snapshot umfasst Positionen, Ruecknahmen, Summen, Zahlungstext, Zahlart und Faelligkeit, soweit fachlich vorhanden.
- Zahlart ist ein zentraler Kundenwert. Beim Erstimport ist die juengste Kunden-Excel die Quelle; danach ist der Kundenstamm die Arbeitsquelle.
- SEPA- und Ueberweisungstexte sowie Lieferpauschale und Ausgabeziele werden als Konfiguration behandelt, nicht als UI-Konstanten.
- Excel und PDF werden aus derselben Snapshot-Eingabe erzeugt; PDF-Neuerzeugung liest nicht die bearbeitbare Excel-Datei.
- Unsichere Kundentreffer und Artikelzuordnungen erzeugen Prueffaelle. Nur explizit bestaetigte Schreibweisen werden als Artikelalias gespeichert.

## Testing Decisions

- Tests pruefen das fachliche Ergebnis, nicht interne Implementierungsdetails.
- Der vorhandene Kernberechnungs-Golden-Test fuer Metzgerei Karl bleibt der Summenanker.
- Ein Test prueft: Produktpreis nach Bestellung geaendert, Entwurf verwendet den aktuellen Stammwert.
- Ein Test prueft: einmaliger Entwurfs-Override beeinflusst nur diesen finalen Snapshot.
- Ein Test prueft: Excel fehlt oder wurde geaendert, erneute Ausgabe verwendet unveraendert den Snapshot.
- Golden-Tests pruefen SEPA und Ueberweisung einschliesslich Faelligkeit plus sieben Tage.
- Onboarding-Tests pruefen verschobene Kopfbereiche, getrennte E-Mail-Adressen, unsichere Kundenkandidaten und unbestaetigte Artikelaliasse.
- Jeder Meilenstein endet mit gesamter Test-Suite, Review, Anwender-Smoke, `FORTSCHRITT.md`-Update und Thomas' Abnahme.

## Out of Scope

- E-Mail-Versand, ZUGFeRD, NAS-/Mehrbenutzerbetrieb und Web-Variante.
- Dauerhafte kundenbezogene Preislisten oder Rabattmodelle.
- Automatisches Zusammenfuehren unsicherer Kunden oder Artikel.
- Vollstaendige Umbenennung aller bestehenden Services in einem grossen Umbau.

## Further Notes

Die bestehende zentrale Lieferkundenliste bleibt fuer Planung und Beziehung massgeblich. Alte Kunden-Excels bleiben Quelle fuer operative Migrationsdaten und Nachweis, nicht fuer laufende Preisfindung.
