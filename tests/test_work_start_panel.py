from pathlib import Path


def test_work_start_panel_shows_customer_search_and_open_returns_tasks():
    source = Path("src/getraenkeladen_tool/ui/work_start_panel.py").read_text(encoding="utf-8")

    assert "class WorkStartPanel" in source
    assert "customer_search_requested = Signal()" in source
    assert "customer_selected = Signal(int)" in source
    assert "return_selected = Signal(int)" in source
    assert "Bestellung aufnehmen" in source
    assert 'SearchableSelect("Kundenname eingeben' in source
    assert "Offene Lieferschein-Rückläufe" in source
    assert "Keine offenen Rückläufe." in source
    assert "Bitte erst Kunden importieren oder unter Verwaltung anlegen." in source
    assert "list_active_customers" in source
    assert "list_open_delivery_returns" in source


def test_work_start_panel_uses_compact_task_panels_without_card_stretch():
    source = Path("src/getraenkeladen_tool/ui/work_start_panel.py").read_text(encoding="utf-8")

    assert "WorkspaceCard" not in source
    assert 'work_column.setObjectName("workStartColumn")' in source
    assert "work_column.setMaximumWidth(980)" in source
    assert 'panel.setObjectName("workTaskPanel")' in source
    assert "panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)" in source
    assert "work_flow = QVBoxLayout()" in source
    assert "QGridLayout" not in source
    assert "self.customer_select.setMinimumWidth" not in source
    assert "self.returns_table.setMinimumWidth(320)" in source
    assert "self.open_return_button.setVisible(bool(items))" in source
    assert 'self.customer_search_button.setObjectName("secondaryActionButton")' in source
    assert 'QPushButton("Alle Kunden öffnen")' in source


def test_main_window_opens_work_start_as_first_arbeiten_screen():
    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "from .work_start_panel import WorkStartPanel" in source
    assert "self.work_start_panel = WorkStartPanel(session_factory=session_factory)" in source
    assert "self.work_workspace = QStackedWidget()" in source
    assert 'tabs.addTab(self.work_start_panel, "Start")' not in source
    assert "self.work_start_panel.customer_search_requested.connect(self.open_customer_folder_tab)" in source
    assert "self.work_start_panel.customer_selected.connect(self.open_customer_focus)" in source
    assert "self.work_start_panel.return_selected.connect(self.open_return_for_order)" in source
    assert "self.return_invoice_panel = ReturnInvoicePanel(session_factory=session_factory)" in source
    assert 'tabs.addTab(self.return_invoice_panel, "Rücklauf")' not in source
    assert "def open_return_for_order" in source
    assert "self.return_invoice_panel.select_order(order_id)" in source


def test_return_invoice_panel_uses_return_language():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "class ReturnInvoicePanel(InvoicePanel)" in source
    assert "back_requested = Signal()" in source
    assert "show_work_overview_button = True" in source
    assert "Zurück zur Übersicht" in source
    assert 'page_title = "Rücklauf bearbeiten und Rechnung erstellen"' in source
    assert 'create_both_button_text = "Rechnung aus Rücklauf als Excel + PDF erstellen"' in source
