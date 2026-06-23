from pathlib import Path


def test_order_panel_loads_master_data_and_orders_on_open():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.refresh_master_data()" in source
    assert "self.refresh_orders()" in source
    assert "suggest_order_number" not in source


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
    assert "Excel-Lieferschein erstellen" in source
    assert "PDF-Lieferschein erstellen" in source
    assert "Excel-Rechnung erstellen" in source
    assert "PDF-Rechnung erstellen" in source
    assert "self.create_excel_button.clicked.connect(self.create_excel_document)" in source
    assert "self.create_pdf_button.clicked.connect(self.create_pdf_document)" in source
    assert "self._created_asset_label(assets)" in source
    assert "QMessageBox.information" in source
    assert "QMessageBox.critical" in source
    assert "QMessageBox.warning" in source
    assert "Erstellung fehlgeschlagen" in source
    assert "Auftrag suchen" in source
    assert 'self.order_select = SearchableSelect("Kunde, Auftragsnummer oder Lieferdatum suchen")' in source
    assert "self.order_select.set_items(" in source
    assert "self.order_select.current_value()" in source
    assert "self.orders_table = QTableWidget" not in source
    assert "Auftraege laden" not in source
    assert "Excel:" in source
    assert "PDF:" in source
    assert "Nummer vorschlagen" not in source
    assert "suggest_document_number" not in source
    assert "Lieferpauschale" in source
    assert "self.delivery_fee_choice = QComboBox()" in source
    assert "self.document_note = QLineEdit()" in source


def test_document_workflow_uses_compact_order_search_instead_of_large_order_list():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "SearchableSelect" in source
    assert "Auftrag uebernehmen" in source
    assert "Suche zuruecksetzen" in source
    assert "Ausgewaehlter Auftrag" in source
    assert "Kunde, Auftragsnummer oder Lieferdatum suchen" in source


def test_document_workflow_uses_rounded_tabs_for_document_steps():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "self.document_tabs = QTabWidget()" in source
    assert 'addTab(positions_tab, "1 Positionen")' in source
    assert 'addTab(deposit_tab, "2 Pfand")' in source
    assert 'addTab(details_tab, "3 Belegdaten")' in source
    assert 'addTab(output_tab, "4 Ausgabe")' in source
    assert "document_layout.addWidget(total_bar)" in source
    assert "PDF-Rechnung erstellen" in source
    assert "PDF-Lieferschein erstellen" in source


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
    assert 'self.remove_line_button.setObjectName("dangerAction")' in source
    assert 'self.remove_return_button.setObjectName("dangerAction")' in source
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


def test_order_panel_uses_list_page_and_order_dialog_for_editing():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "QDialog" in source
    assert "self.order_dialog" in source
    assert "def open_order_dialog" in source
    assert "def close_order_dialog_after_success" in source
    assert "Neuen Auftrag anlegen" in source
    assert "Auftrag speichern" in source
    assert "WA_DeleteOnClose" in source
    assert "self.order_workspace_tabs = QTabWidget()" not in source
    assert "self.order_editor_widget" in source


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

    assert '"newOrderButton": "Bestellung erfassen"' in source
    assert '"copyOrderButton": "Aus letzter Bestellung uebernehmen"' in source
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

    assert '"copyOrderButton": "Aus letzter Bestellung uebernehmen"' in source
    assert "self.order_table_search = QLineEdit()" in source
    assert "self.order_table_search.textChanged.connect(self.apply_order_table_search)" in source
    assert "def apply_order_table_search" in source
    assert "def copy_selected_order_as_new" in source
    assert "self.current_order_id = None" in source
    assert "Kopie aus Auftrag" in source
    assert "list_active_orders(session)" in source
    assert "open_order_dialog" in source


def test_order_panel_focuses_on_order_management_not_document_creation():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert '"saveOrderButton": "Bestellung speichern"' in source
    assert '"createDeliveryOrderButton"' not in source
    assert '"createInvoiceButton"' not in source
    assert "Excel/PDF aus Auftrag erstellen" not in source


def test_order_panel_splits_list_and_dialog_into_resize_friendly_workspaces():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "QDialog" in source
    assert "ResponsiveSplitter" in source
    assert "PageHeader" in source
    assert "self.order_editor_widget" in source
    assert "layout.addWidget(orders_box, 1)" in source
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


def test_order_and_document_use_table_search_instead_of_customer_filter_dropdowns():
    order_source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")
    document_source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "FilterBar" not in order_source
    assert "self.order_customer_filter" not in order_source
    assert "customerFilterLabel" not in order_source
    assert "setObjectName(\"tableSearchField\")" in order_source
    assert "FilterBar" not in document_source
    assert "self.customer_filter" not in document_source
    assert "setObjectName(\"tableSearchField\")" in document_source
    assert "def _row_matches_query" in order_source
    assert "self.order_select = SearchableSelect" in document_source
    assert "def _row_matches_query" not in document_source


def test_order_context_menu_offers_copy_delivery_note_and_invoice_actions():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert '"create_delivery_note": "Lieferschein erstellen"' in source
    assert '"create_invoice": "Rechnung erstellen"' in source
    assert "self.request_delivery_note_for_selected_order()" in source
    assert "self.request_invoice_for_selected_order()" in source


def test_order_context_archive_does_not_open_edit_dialog():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "elif selected == archive_action:" in source
    assert "self.current_order_id = self._selected_order_id()" in source
    assert "self.load_selected_order_id()\n            self.archive_selected_order()" not in source
