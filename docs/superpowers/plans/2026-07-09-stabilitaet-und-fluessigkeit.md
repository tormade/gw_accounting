# Stabilitaet und Fluessigkeit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die Anwendung loest Pfade robust auf, sichert Belegdateien gegen Teilfehler ab und fuehrt lange UI-Aktionen im Hintergrund aus.

**Architecture:** Eine kleine Infrastruktur kapselt Ressourcen, Startfehler und Qt-Hintergrundarbeit. Services behalten ihre Fachlogik; Panels rufen sie nur noch ueber den Worker auf.

**Tech Stack:** Python 3.11, PySide6, SQLAlchemy, openpyxl, reportlab, pytest.

## Global Constraints

- Kein Windows-EXE-Build und keine PyInstaller-Ausfuehrung in diesem Vorhaben.
- Bestehende Dokumente duerfen bei einem fehlgeschlagenen Export nie geloescht werden.
- Neue Verhaltensaenderungen entstehen testgetrieben und der volle Testlauf muss grün bleiben.
- Die vorhandenen uncommitteten Aenderungen gehoeren zur gemeinsamen Grundlage und werden nicht pauschal gestagt.

---

### Task 1: Pfad- und Dateinameninfrastruktur

**Files:**
- Create: `src/getraenkeladen_tool/resources.py`
- Modify: `src/getraenkeladen_tool/services/excel_service.py`, `src/getraenkeladen_tool/services/pdf_service.py`, `src/getraenkeladen_tool/ui/main_window.py`, `src/getraenkeladen_tool/ui/settings_panel.py`, `src/getraenkeladen_tool/services/file_naming_service.py`
- Test: `tests/test_resources.py`, `tests/test_file_naming_service.py`

- [ ] Schreibe Tests fuer projektaufgeloeste Ressourcen und Windows-Dateinamen mit `: * ? < > |`, reservierten Namen und abschliessenden Leerzeichen/Punkten.
- [ ] Fuehre die Tests aus und bestaetige den roten Zustand.
- [ ] Implementiere `resource_path()` und eine vollstaendige Windows-Dateinamenbereinigung; ersetze die lokalen Pfadberechnungen.
- [ ] Fuehre die fokussierten Tests aus und bestaetige den grünen Zustand.

### Task 2: Startfehler und atomare Belegerzeugung

**Files:**
- Create: `src/getraenkeladen_tool/errors.py`
- Modify: `src/getraenkeladen_tool/app.py`, `src/getraenkeladen_tool/db.py`, `src/getraenkeladen_tool/services/document_service.py`
- Test: `tests/test_db_bootstrap.py`, `tests/test_document_service.py`

- [ ] Schreibe Tests, die einen Datenbank-Startfehler in `ApplicationStartupError` uebersetzen und einen PDF-Fehler ohne neue Enddateien pruefen.
- [ ] Fuehre die Tests aus und bestaetige den roten Zustand.
- [ ] Fuehre eine schmale Startfehlergrenze und temporaere Belegausgabe mit bereinigendem Fehlerpfad ein.
- [ ] Fuehre die fokussierten Tests aus und bestaetige den grünen Zustand.

### Task 3: Wiederverwendbare Qt-Hintergrundarbeit

**Files:**
- Create: `src/getraenkeladen_tool/ui/background_task.py`
- Modify: `src/getraenkeladen_tool/ui/settings_panel.py`, `src/getraenkeladen_tool/ui/document_workflow_panel.py`
- Test: `tests/test_background_task.py`, `tests/test_main_window.py`

- [ ] Schreibe Headless-Qt-Tests fuer Ergebnis- und Fehler-Signal eines Workers.
- [ ] Fuehre die Tests aus und bestaetige den roten Zustand.
- [ ] Implementiere einen `QThread`-Worker und nutze ihn fuer beide Importe sowie die Belegerzeugung; Aktionen bleiben waehrend der Arbeit deaktiviert.
- [ ] Fuehre die fokussierten Tests aus und bestaetige den grünen Zustand.

### Task 4: Gesamtnachweis und gezielter Commit

**Files:**
- Modify: alle Dateien aus Tasks 1-3
- Test: gesamtes `tests/`

- [ ] Fuehre `python -m compileall -q src` und `.venv/bin/python -m pytest -q` aus.
- [ ] Pruefe `git diff --check` und den gestagten Diff gegen die Aufgabenliste.
- [ ] Stage ausschliesslich die neu hinzugefuegten Stabilitaets-Hunks, committe sie und pushe den aktuellen Branch.
