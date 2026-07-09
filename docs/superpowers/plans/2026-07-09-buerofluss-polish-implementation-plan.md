# Bürofluss-Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or execute each task with a red-green-refactor cycle.

**Goal:** Den sichtbaren Bürofluss zuverlässig abschließen: sichere Import-Vorschau, klare Verwaltungswege, ruhigere Hilfe- und Leerzustände sowie ein verifizierter Ablauf Kunde → Bestellung → Lieferschein → Rücklauf → Rechnung.

**Architecture:** Die Fachprüfung für fehlende Importquellen bleibt im Import-Service. Die Oberfläche zeigt nur den vom Service gelieferten Status an und führt Nutzer mit kurzen, nicht-blockierenden Hinweisen. Der Hauptfluss bleibt in `Arbeiten`; Verwaltung bleibt nachrangig.

**Tech Stack:** Python 3.11, PySide6, SQLAlchemy, pytest, pytest-qt.

## Global Constraints

- Sichtbare Texte verwenden echte deutsche Umlaute.
- Fachlogik bleibt außerhalb der UI.
- Keine Pflicht-Rechtsklicks und keine versteckten Hauptaktionen.
- Der normale Bürofluss bleibt Kunde → Bestellung → Lieferschein → Rücklauf → Rechnung.
- Bestehende Excel-, PDF-, CSV- und SQLite-Ausgaben bleiben unverändert nutzbar.

---

### Task 1: Import sicher und eindeutig machen

**Files:**
- Modify: `src/getraenkeladen_tool/services/master_data_import_service.py`
- Modify: `src/getraenkeladen_tool/ui/settings_panel.py`
- Modify: `tests/test_master_data_import_service.py`
- Modify: `tests/test_main_window.py`

- [ ] Schreiben, dass eine Vorschau fehlende Pflichtdateien meldet und ein Import nicht bestätigt werden kann.
- [ ] Test rot ausführen.
- [ ] Fehlende Quelldateien im Service sichtbar machen und den Start in der UI blockieren.
- [ ] Seite, Dialogtitel und Hilfetext einheitlich auf `Excel-Import` benennen.
- [ ] Zieltests grün ausführen.

### Task 2: Verwaltung ohne Sackgassen abschließen

**Files:**
- Modify: `src/getraenkeladen_tool/ui/document_archive_panel.py`
- Modify: `src/getraenkeladen_tool/ui/checklist_panel.py`
- Modify: `tests/test_document_archive_panel.py`
- Modify: `tests/test_main_window.py`

- [ ] Schreiben, dass leere Filterergebnisse im Archiv eine klare Erklärung anzeigen.
- [ ] Test rot ausführen.
- [ ] Sichtbaren Leerzustand für Archiv und Prüfpunkte ergänzen; vorhandene Aktionen bleiben nur bei gewähltem Beleg aktiv.
- [ ] Zieltests grün ausführen.

### Task 3: Hilfen in den Arbeitskontext holen

**Files:**
- Modify: `src/getraenkeladen_tool/ui/customer_panel.py`
- Modify: `src/getraenkeladen_tool/ui/product_panel.py`
- Modify: `tests/test_main_window.py`

- [ ] Schreiben, dass Kunden- und Produktpflege kurze, sichtbare Schritt-Hinweise enthalten.
- [ ] Test rot ausführen.
- [ ] Vorhandene Guidance-Boxen in die Oberfläche einhängen und Systemdialog-Hilfen entfernen oder auf eine ruhige Kurzinfo reduzieren.
- [ ] Zieltests grün ausführen.

### Task 4: End-to-End-Abnahme und Checkpoint

**Files:**
- Modify: `FORTSCHRITT.md`
- Test: `tests/test_daily_workflow.py`
- Test: `tests/test_return_workflow.py`
- Test: `tests/test_main_window.py`

- [ ] Gesamte Regression, Kompilierung und den Bürofluss im echten Fenster ausführen.
- [ ] Auf abgeschnittene Texte, Rückwege und Bedienzustände prüfen.
- [ ] Source-Control-Blockade getrennt diagnostizieren; keine destruktive Git-Aktion.
- [ ] `FORTSCHRITT.md` mit Ergebnissen aktualisieren.
