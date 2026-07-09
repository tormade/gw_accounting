# Datenintegrität und Arbeitsfluss – Implementierungsplan

> **Ziel:** Die Kundenpflege verliert keine importierten Stammdaten mehr; Such-,
> Beleg- und Importabläufe bleiben bewusst steuerbar und blockieren die Oberfläche
> nicht.

## Ausgangspunkt

Die freigegebene Spezifikation ist
`docs/superpowers/specs/2026-07-09-datenintegritaet-und-arbeitsfluss-design.md`.
Diese Umsetzung umfasst ausschließlich die dort beschriebenen fünf Punkte.

## Arbeitspakete

1. **Kundenstammdaten vollständig führen**
   - `ui/customer_panel.py`: Die sechs bisher nicht geführten Werte
     (`phone`, `contact_name`, `contact_email`, `payment_method`,
     `opening_hours`, `internal_notes`) im einklappbaren Bereich
     „Weitere Kundendaten“ ergänzen.
   - Beim Laden, Speichern und Verwerfen dieselben Werte in die Form- und
     Kunden-Snapshots aufnehmen.
   - `tests/test_customer_panel.py`: Ein importierter Kunde wird geladen,
     eine sichtbare Angabe wird verändert und alle weiteren Angaben bleiben
     nach dem Speichern erhalten.

2. **Kundensuche nur nach expliziter Auswahl ausführen**
   - `ui/searchable_select.py`: Filtern darf nie einen Treffer als aktuelle
     Auswahl setzen. Nur Klick, Doppelklick, Enter oder `select_value()`
     dürfen `selection_changed` mit einem Wert auslösen.
   - `tests/test_searchable_select.py`: Ein eindeutiger Tipptreffer löst
     keine Auswahl aus; Enter und Klick tun es weiterhin.

3. **Semantische Button-Rollen zentralisieren**
   - `ui/layouts.py`: Eine kleine Hilfsfunktion setzt die Qt-Eigenschaft
     `role` auf `primary`, `secondary`, `danger` oder `quiet`.
   - `ui/theme.py`: Selektoren stylen diese Rollen; die bisherigen
     fachlichen Objekt-Namen bleiben nur für Identifikation und werden nicht
     mehr für die Farbbedeutung benötigt.
   - Betroffene Buttons in den aktuellen Arbeitsflächen erhalten eine Rolle,
     einschließlich der neuen Wechselaktion im Belegworkflow.
   - `tests/test_theme.py` (oder vorhandener passender UI-Test): prüft die
     Rollen-Selektoren und dass der alte `#primaryAction`-Selektor nicht mehr
     die Designbedeutung trägt.

4. **Eine gemeinsame Hintergrundausführung einführen**
   - `ui/background_task.py`: Ein Qt-Worker führt eine abgegrenzte Funktion
     in einem `QThread` aus und meldet Ergebnis oder Fehler zurück. Der
     Worker erstellt und schließt seine Datenbank-Session im Hintergrund;
     UI-Objekte und ORM-Instanzen bleiben im GUI-Thread.
   - `ui/settings_panel.py`: Excel-Import über den Worker ausführen; Import-
     Aktion währenddessen sperren und Abschluss/Fehler im Status anzeigen.
   - `ui/customer_folder_panel.py`: Snapshot, Schnellstart und
     Excel-Vorschauen zusammen im Worker laden; nur ein noch aktueller
     Kunde darf das Ergebnis in die Oberfläche schreiben.
   - `ui/document_workflow_panel.py`: Belegerstellung und Prüfung über den
     Worker ausführen; Buttons währenddessen sperren und primitive Ergebnis-
     daten zurückgeben.
   - Tests prüfen mindestens den Worker-Lebenszyklus und den gesperrten
     Auslösezustand, ohne echte Excel-/PDF-Operationen in einem UI-Test zu
     benötigen.

5. **Bestellung im Belegworkflow sichtbar wechseln**
   - `ui/document_workflow_panel.py`: Nach dem Laden einer Bestellung bleibt
     „Andere Bestellung wählen“ sichtbar. Die Aktion setzt Auswahl,
     Zusammenfassung und Eingabekontext sauber zurück.
   - UI-Test prüft Sichtbarkeit nach Auswahl und den vollständigen Reset.

## Prüfsequenz

1. Betroffene, neu ergänzte Tests gezielt ausführen.
2. Die zusammenhängenden UI-, Service- und Smoke-Tests ausführen.
3. Syntax- und Importprüfung der geänderten UI-Module durchführen.
4. Einen manuellen Sichtcheck mit dem bestehenden Start-/Kunden-/Belegfluss
   vornehmen, falls der lokale Qt-Start verfügbar ist.

## Nicht Teil dieser Änderung

- Windows-Export oder EXE-Paketierung.
- Zahlungs-/Teilzahlungsfachlogik.
- Produkt-Einheiten oder eine größere Navigation-Umstrukturierung.
- Abbruch bereits laufender Excel- oder PDF-Schreibvorgänge.

## Abschlussnachweis vom 9. Juli 2026

- Alle fünf Arbeitspakete sind umgesetzt und durch fokussierte Regressionstests abgedeckt.
- Die vollständige Testsuite beendet sich sauber mit `326 passed`.
- `python -m compileall -q -f src tests` ist erfolgreich.
- Ein isolierter Offscreen-Anwender-Smoke bestätigt den bewussten Suchstart per Enter,
  das asynchrone Laden des Kundenarbeitsplatzes, den verlustfreien Kundendaten-Edit,
  den vollständigen Bestellwechsel sowie die appweiten semantischen Buttonrollen.
- Standards- und Spezifikationsreview melden keine verbleibenden P0-P2-Befunde.
