from pathlib import Path


def test_order_panel_loads_master_data_and_orders_on_open():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.refresh_master_data()" in source
    assert "self.refresh_orders()" in source
    assert "self.suggest_order_number()" in source


def test_order_panel_uses_searchable_customer_and_product_selects():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.customer_select = SearchableSelect(\"Kunde suchen" in source
    assert "self.product_select = SearchableSelect(\"Produkt suchen" in source
    assert "self.customer_select.set_items(" in source
    assert "self.product_select.set_items(" in source
    assert "self.customer_select.current_value()" in source
    assert "self.product_select.current_value()" in source


def test_document_workflow_panels_make_excel_pdf_generation_flow_visible():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "class DeliveryNotePanel" in source
    assert "class InvoicePanel" in source
    assert "Lieferschein Excel/PDF erstellen" in source
    assert "Rechnung Excel/PDF erstellen" in source
    assert "Auftrag waehlen" in source
    assert "Excel:" in source
    assert "PDF:" in source


def test_order_panel_supports_editing_existing_orders():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.order_mode_label" in source
    assert "Auftrag bearbeiten" in source
    assert "update_order(" in source
    assert "def populate_order_form" in source
    assert "self.order_lines_table.setRowCount(0)" in source
    assert "Auftrag aktualisiert" in source


def test_order_panel_keeps_product_ids_when_existing_orders_are_loaded():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "Qt.ItemDataRole.UserRole" in source
    assert "line.product_id" in source


def test_order_panel_shows_running_order_total():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert '"Summe EUR"' in source
    assert "self.order_total_label" in source
    assert "itemChanged.connect(self.update_order_total)" in source
    assert "def update_order_total" in source
    assert "Auftragssumme" in source


def test_order_panel_exposes_deposit_returns_new_order_and_copy_actions():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert '"newOrderButton": "Neuer Auftrag"' in source
    assert '"copyOrderButton": "Aus Auftrag kopieren"' in source
    assert '"addDepositReturnButton": "Pfand zurueck hinzufuegen"' in source
    assert "self.deposit_returns_table" in source
    assert "def reset_order_form" in source
    assert "def copy_selected_order_as_new" in source


def test_order_panel_warns_before_changing_documented_orders():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.current_order_status" in source
    assert "def confirm_documented_order_change" in source
    assert "Belege neu erstellen" in source


def test_order_panel_filters_orders_by_customer_and_can_copy_existing_order():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert '"copyOrderButton": "Aus Auftrag kopieren"' in source
    assert '"customerFilterLabel": "Auftraege filtern nach Kunde"' in source
    assert "self.order_customer_filter = SearchableSelect" in source
    assert "self.order_customer_filter.selection_changed.connect(self.refresh_orders)" in source
    assert "def copy_selected_order_as_new" in source
    assert "self.current_order_id = None" in source
    assert "Kopie aus Auftrag" in source
    assert "list_active_orders(session, customer_id=customer_id)" in source


def test_order_panel_focuses_on_order_management_not_document_creation():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert '"saveOrderButton": "Auftrag speichern"' in source
    assert '"createDeliveryOrderButton"' not in source
    assert '"createInvoiceButton"' not in source
    assert "Excel/PDF aus Auftrag erstellen" not in source


def test_order_panel_splits_creation_and_management_into_resize_friendly_workspaces():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "QTabWidget" in source
    assert "ResponsiveSplitter" in source
    assert "PageHeader" in source
    assert 'addTab(new_order_tab, "Neuer Auftrag")' in source
    assert 'addTab(manage_orders_tab, "Auftraege verwalten")' in source
    assert "setStretchFactor(0, 1)" in source
    assert "setStretchFactor(1, 3)" in source
    assert "setMaximumHeight(180)" not in source
