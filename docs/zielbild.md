# Zielbild: Getraenke Winklmeier Buerowerkzeug

## In Einem Satz

Ein schlankes lokales Windows-Programm, das den kompletten Buerotag des Getraenkehandels traegt: Kunden kontaktieren, Bestellung erfassen, Lieferschein und Rechnung erzeugen, offene Posten im Blick behalten und Dateien weiterhin im gewohnten Kundenordner-System ablegen.

Das Werkzeug soll bewusst klein bleiben. Es ist kein ERP, keine Cloud-Loesung und kein zweites Buchhaltungssystem. DATEV bleibt das verbindliche Archiv, waehrend SQLite, Excel, PDF und CSV dafuer sorgen, dass der Betrieb nicht eingesperrt ist.

## Hauptweg Des Fertigen Programms

Der wichtigste Ablauf ist:

1. Kunde suchen oder aus Wiedervorlage oeffnen.
2. Kundenkopf sehen: Adresse, Lieferfenster, Hinweise, Telefon, Zahlart, offene Posten, naechster Kontakt.
3. Kundensortiment sehen: Artikel, Pfand, aktueller zentraler Preis, letzte Menge, neue Menge.
4. Mengen am Telefon anpassen, Artikel entfernen oder neue Artikel aus dem Gesamtkatalog hinzufuegen.
5. Pfand-Rueckgabe erfassen.
6. Live-Summen sehen: Lieferwert, Lieferpauschale, Pfand-Rueckgabe, Netto, MwSt, Brutto.
7. Belegnummer eintragen.
8. Lieferschein, Rechnung oder spaeter Rechnung plus E-Mail erzeugen.
9. Excel und PDF landen im richtigen Kundenordner; Rechnung erzeugt automatisch einen offenen Posten.

Dieser Hauptweg hat Vorrang vor Nebenfunktionen. Jede UI-Entscheidung muss ihn einfacher, sicherer oder schneller machen.

## Startbildschirm

Der Startbildschirm soll morgens ohne Suchen zeigen, was ansteht:

- Heute zu liefern.
- Offene Posten.
- Faellige Kontakte.
- Einstieg fuer neue Lieferung oder Bestellung.
- Heutige Anruf-/Kontaktliste, ohne Kunden, die sich selbst melden.

## Kunden Und Bestellung

Der Kundenbildschirm ist der operative Mittelpunkt. Er zeigt nicht nur Stammdaten, sondern die letzte bekannte Bestellung als Arbeitsvorlage. Das Sortiment lernt mit: Wenn ein Kunde einen neuen Artikel bekommt, bleibt dieser kuenftig in seinem Sortiment sichtbar.

Bekannte Werte sind vorbelegt. Die Sachbearbeitung korrigiert nur die Abweichungen.

## Stammdaten

Artikel und Kunden bleiben getrennte, durchsuchbare Listen:

- Artikel: zentraler Lieferpreis, Pfand, Aktiv/Inaktiv, spaeter Alias-Schreibweisen.
- Kunden: Kontakt, zwei getrennte E-Mail-Adressen, Rhythmus, Zahlart, Lieferfenster, Hinweise, Wiedervorlage.

Preis und Pfand werden nur zentral gepflegt. Alte Einzeldateien dienen nur der Migration und Ablage, nicht mehr als Preisquelle.

## Belege

Excel bleibt bearbeitbar, PDF ist verbindlich. Beide werden im Kundenordner erzeugt.

Die Rechnung am Bildschirm und in der Ausgabe soll sich vertraut anfuehlen:

- Zeilensumme = Menge * (Lieferpreis + Pfand).
- Lieferpauschale entfaellt ab sechs Traegern, langfristig automatisch; aktuell kann sie bewusst gesetzt werden.
- Pfand-Rueckgabe wird negativ gerechnet.
- Netto = Brutto / 1,19.
- MwSt = Brutto - Netto.
- Fuss- und Zahlungstexte folgen der Zahlart.

## Offene Posten

Offene Posten entstehen automatisch bei Rechnungsstellung. Die Liste zeigt Kunde, Rechnungsnummer, Datum, Betrag, Zahlart, Faelligkeit und Status.

Ueberfaellige Posten werden sichtbar hervorgehoben. Ueberweisung und SEPA sollen getrennt filterbar sein, damit Banklauf und Nachfassen einfach bleiben.

## Tagesliste

Die Tagesliste zeigt pro Tag alle Stopps mit Adresse, Zeitfenster und wichtigen Hinweisen. Sie soll druckbar sein und spaeter auch als Fahreransicht nutzbar werden.

## Kontakte Und Serienbrief

Die Wiedervorlage erzeugt eine Anrufliste oder spaeter Serienbrief/-mail fuer Bestellanfragen. Kunden, die sich selbst melden, werden dabei nicht automatisch vorgeschlagen.

## Auswertung

Auswertungen bleiben schlank:

- Stopps pro Tag/Woche/Monat.
- Gelieferte Mengen.
- Umsatz.
- Export nach Excel.

## Daten-Endzustand

Alle Artikel und Kunden sind importiert. Pro Kunde ist das Sortiment aus Ordnerdatei und Lieferkundenliste zusammengefuehrt. Jede Position soll langfristig mit einem zentralen Artikel verbunden sein, damit Preise und Pfand immer aus einer Quelle kommen.

Konflikte aus der Migration werden nicht geraten, sondern in einer Pruefliste vorgelegt.

## Bewusst Spaeter

- E-Rechnung/ZUGFeRD.
- Mehrplatzbetrieb im lokalen Netzwerk/NAS.
- E-Mail-Versand aus der App.
- Fahreransicht am Handy.

Diese Tueren bleiben offen, duerfen aber den ersten stabilen lokalen Hauptweg nicht verkomplizieren.
