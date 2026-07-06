from pathlib import Path


def test_document_archive_panel_exposes_one_combined_document_list_and_actions():
    source = Path("src/getraenkeladen_tool/ui/document_archive_panel.py").read_text(encoding="utf-8")

    assert "class DocumentArchivePanel" in source
    assert "Alle Belege" in source
    assert "self.document_table" in source
    assert "self.document_filter = QComboBox()" in source
    assert "Rechnungen und Lieferscheine gemeinsam" in source
    assert "Kunde, Nummer oder Datum suchen" in source
    assert "Excel oeffnen" in source
    assert "PDF oeffnen" in source
    assert "Ordner oeffnen" in source
    assert "Im Belegbereich oeffnen" in source
    assert "Zugehoerige Bestellung" in source
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
    assert "customContextMenuRequested.connect" in source
    assert "show_document_context_menu" in source
    assert "PDF neu erzeugen" in source
    assert "Excel neu erzeugen" in source
    assert "Alle Aktionen stehen auch als Buttons bereit" in source
    assert "table.indexAt(position).row()" in source
    assert "table.setCurrentCell(clicked_row, 0)" in source
    assert "Zugehoerige Bestellung oeffnen" in source
    assert "document_open_requested = Signal(str, int)" in source
    assert "order_open_requested = Signal(int)" in source
    assert "table.setColumnWidth(1, 180)" in source
    assert "table.setColumnWidth(6, 190)" in source


def test_main_window_wires_document_archive_workspace_for_users():
    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert 'tabs.addTab(self.document_archive_panel, "Belegarchiv")' in source
    assert '"Belege"' not in source
    assert "from .document_archive_panel import DocumentArchivePanel" in source
    assert "self.document_archive_panel = DocumentArchivePanel" in source
    assert "self.pages.addWidget(self._scrollable_tab(self.document_archive_panel))" not in source
    assert "self.document_archive_panel.document_open_requested.connect(self.open_document_from_archive)" in source
    assert "self.document_archive_panel.order_open_requested.connect(self.open_order_for_id)" in source
