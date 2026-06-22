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


def test_document_workflow_allows_editing_lines_and_deposit_returns():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")
    presets_source = Path("src/getraenkeladen_tool/ui/deposit_return_presets.py").read_text(encoding="utf-8")

    assert "DEPOSIT_RETURN_PRESETS" in source
    assert "Pfand 1,50 EUR" in presets_source
    assert "Pfand 5,10 EUR" in presets_source
    assert "self.deposit_return_select = QComboBox()" in source
    assert "self.deposit_return_select.currentIndexChanged.connect(self.apply_selected_deposit_return)" in source
    assert '"removeDocumentLineButton": "Position entfernen"' in source
    assert '"addDocumentDepositReturnButton": "Pfand zurueck hinzufuegen"' in source
    assert '"removeDocumentDepositReturnButton": "Pfand zurueck entfernen"' in source
    assert "self.remove_line_button.clicked.connect(self.remove_selected_line)" in source
    assert "self.add_return_button.clicked.connect(self.add_deposit_return)" in source
    assert "self.remove_return_button.clicked.connect(self.remove_selected_deposit_return)" in source
    assert "def add_deposit_return" in source
    assert "def apply_selected_deposit_return" in source
    assert "def remove_selected_line" in source


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
    assert "self.deposit_return_select = QComboBox()" in source
    assert "DEPOSIT_RETURN_PRESETS" in source
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
    assert "self.order_workspace_tabs.setCurrentIndex(0)" in source


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


def test_order_panel_forms_expand_to_available_width_instead_of_floating_centered():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")
    layout_source = Path("src/getraenkeladen_tool/ui/layouts.py").read_text(encoding="utf-8")

    assert "configure_form_layout(customer_form)" in source
    assert "configure_form_layout(position_form)" in source
    assert "configure_form_layout(deposit_return_form)" in source
    assert "setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)" in layout_source
    assert "setLabelAlignment(Qt.AlignmentFlag.AlignLeft)" in layout_source


def test_order_and_document_filters_are_compact_top_toolbars():
    order_source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")
    document_source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "self.order_customer_filter.result_list.setMaximumHeight(56)" in order_source
    assert "self.order_customer_filter.setMaximumWidth(340)" in order_source
    assert "filter_toolbar = FilterBar()" in order_source
    assert "orders_layout.addWidget(filter_toolbar)" in order_source
    assert "self.customer_filter.result_list.setMaximumHeight(56)" in document_source
    assert "self.customer_filter.setMaximumWidth(340)" in document_source
    assert "filter_toolbar = FilterBar()" in document_source
    assert "order_layout.addWidget(filter_toolbar)" in document_source


def test_order_context_menu_offers_copy_delivery_note_and_invoice_actions():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert '"create_delivery_note": "Lieferschein erstellen"' in source
    assert '"create_invoice": "Rechnung erstellen"' in source
    assert "self.request_delivery_note_for_selected_order()" in source
    assert "self.request_invoice_for_selected_order()" in source
