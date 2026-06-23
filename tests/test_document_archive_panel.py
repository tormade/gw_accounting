from pathlib import Path


def test_document_archive_panel_exposes_two_clear_document_tables_and_actions():
    source = Path("src/getraenkeladen_tool/ui/document_archive_panel.py").read_text(encoding="utf-8")

    assert "class DocumentArchivePanel" in source
    assert "Bereits erstellte Rechnungen" in source
    assert "Bereits erstellte Lieferscheine" in source
    assert "Kunde, Nummer oder Datum suchen" in source
    assert "Excel oeffnen" in source
    assert "PDF oeffnen" in source
    assert "Ordner oeffnen" in source
    assert "Die Excel-Datei wurde nicht gefunden." in source
    assert "Die PDF-Datei wurde nicht gefunden." in source
    assert "Der Kundenordner wurde nicht gefunden." in source
    assert "setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)" in source
    assert "setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)" in source
    assert "update_action_buttons" in source
    assert "button.setEnabled(False)" in source
    assert "clearSelection()" in source
    assert "Belege gefunden" in source
    assert "konnte nicht geoeffnet werden" in source


def test_main_window_adds_document_archive_tab_and_refresh_hook():
    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert '"Belegarchiv"' in source
    assert "DocumentArchivePanel" in source
    assert "self.document_archive_panel = DocumentArchivePanel" in source
    assert '"Belegarchiv": (self.document_archive_panel.refresh_archive,)' in source
