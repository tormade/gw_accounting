# Datenintegritaet und Arbeitsfluss – Design

## Ziel

Die aktuelle Winklmeier-Office-Oberflaeche behaelt ihre ruhige, aufgabenorientierte
Gestaltung und behebt fuenf konkrete Risiken: Datenverlust bei Kunden, blockierende
Dateioperationen, nicht wechselbare Belegauswahl, uneinheitliche Buttonrollen und
automatische Navigation aus der Suche.

## Kundendaten

Das Kundenformular erhaelt einen einklappbaren Abschnitt **Weitere Kundendaten**.
Er enthaelt Telefon, Ansprechpartner, Kontakt-E-Mail, Zahlart, Oeffnungszeiten und
interne Hinweise. Beim Speichern werden alle Felder explizit aus dem Formular
uebergeben. Dadurch bleiben importierte Werte erhalten und sind zugleich bearbeitbar.

## Hintergrundarbeit

Eine wiederverwendbare Qt-Hintergrundaufgabe fuehrt fachliche Funktionen ausserhalb
des GUI-Threads aus. Sie liefert Ergebnis oder Ausnahme ueber Qt-Signale zurueck.
Import, Kundenordner-Laden und Belegerzeugung deaktivieren ihre ausloesende Aktion,
zeigen einen laufenden Status und reaktivieren sie nach Erfolg oder Fehler. Eine
Abbruchfunktion wird nicht eingefuehrt, weil die verwendeten Excel-/PDF-Operationen
keine sichere Unterbrechung bieten.

## Belegauswahl

Nach dem Laden einer Bestellung bleibt eine sichtbare Aktion **Andere Bestellung
waehlen** erhalten. Sie setzt Auswahl, Zusammenfassung und Tabellen auf den
Ausgangszustand zurueck, ohne den Dialog schliessen zu muessen.

## Buttonrollen

Eine gemeinsame Helferfunktion weist Buttons eine der Rollen `primary`, `secondary`,
`danger` oder `quiet` zu. Das Stylesheet richtet Farben, Fokus und Hover-Zustand nur
nach dieser Rolle. Jede Arbeitsflaeche hat hoechstens eine primaere Aktion.

## Suche

Ein eindeutiger Treffer bleibt ein Vorschlag. Er setzt keinen aktuellen Wert und
emittiert keine Navigation. Auswaehlen erfolgt nur per Klick, Enter oder einer
programmatischen Auswahl.

## Tests

- Ein Kunden-Update erhaelt alle importierten Zusatzfelder und kann sie bearbeiten.
- Hintergrundaufgaben melden Erfolg und Fehler, ohne die ausloesende UI-Aktion aktiv
  zu lassen.
- Der Belegworkflow kann eine gewaehlte Bestellung sichtbar wechseln.
- Buttonrollen erhalten die erwarteten Eigenschaften.
- Ein eindeutiger Suchtreffer navigiert nicht ohne explizite Auswahl.

## Nicht im Umfang

- Kein Umbau der Hauptnavigation oder Wechsel des visuellen Designkonzepts.
- Keine echte Unterbrechung laufender Excel-/PDF-Verarbeitung.
- Keine Aenderung am Rechnungs-/Teilzahlungsmodell; das ist ein separates P0-Thema.
