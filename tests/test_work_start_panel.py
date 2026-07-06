from pathlib import Path


def test_work_start_panel_shows_customer_search_and_open_returns_tasks():
    source = Path("src/getraenkeladen_tool/ui/work_start_panel.py").read_text(encoding="utf-8")

    assert "class WorkStartPanel" in source
    assert "customer_search_requested = Signal()" in source
    assert "return_selected = Signal(int)" in source
    assert "Bestellung aufnehmen" in source
    assert "Kunde suchen und Bestellung starten" in source
    assert "Offene Lieferschein-Rückläufe" in source
    assert "Keine offenen Rückläufe." in source
    assert "Bitte erst Kunden importieren oder unter Verwaltung anlegen." in source
    assert "list_open_delivery_returns" in source


def test_main_window_opens_work_start_as_first_arbeiten_screen():
    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "from .work_start_panel import WorkStartPanel" in source
    assert "self.work_start_panel = WorkStartPanel(session_factory=session_factory)" in source
    assert 'tabs.addTab(self.work_start_panel, "Start")' in source
    assert "self.work_start_panel.customer_search_requested.connect(self.open_customer_folder_tab)" in source
    assert "self.work_start_panel.return_selected.connect(self.open_invoice_for_order)" in source
