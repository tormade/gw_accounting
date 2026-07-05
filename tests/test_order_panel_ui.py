from pathlib import Path
from PySide6.QtCore import Qt


def _app():
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def test_order_panel_loads_master_data_and_orders_on_open():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.refresh_master_data()" in source
    assert "self.refresh_orders()" in source
    assert "suggest_order_number(session, fallback_date=self.delivery_date.iso_date() or None)" in source
    assert "self.apply_suggested_order_number()" not in source


def test_order_panel_can_start_new_order_for_preselected_customer():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "def open_new_order_for_customer" in source
    assert "self.customer_select.select_value(customer_id)" in source
    assert "Neue Bestellung aus Kunden" in source


def test_order_panel_prefills_lines_from_customer_assortment_when_started_from_customer_folder(session):
    _app()
    from getraenkeladen_tool.models import Customer, CustomerAssortmentItem, Product
    from getraenkeladen_tool.ui.order_panel import OrderPanel

    customer = Customer(name="Cafe Nord", folder_path="/tmp/Cafe Nord", address="Markt 1", is_active=True)
    water = Product(
        name="Adelholzener Wasser 12x0,7",
        unit="Kiste",
        standard_price_cents=890,
        default_deposit_cents=330,
        is_active=True,
    )
    spezi = Product(
        name="Paulaner Spezi 20x0,5",
        unit="Kiste",
        standard_price_cents=1490,
        default_deposit_cents=310,
        is_active=True,
    )
    session.add_all([customer, water, spezi])
    session.flush()
    session.add_all(
        [
            CustomerAssortmentItem(
                customer_id=customer.id,
                product_id=water.id,
                source_product_name=water.name,
                last_quantity=4,
                last_unit_price_cents=890,
                last_deposit_cents=330,
                sort_order=1,
                price_decision="zentraler_preis",
            ),
            CustomerAssortmentItem(
                customer_id=customer.id,
                product_id=spezi.id,
                source_product_name=spezi.name,
                last_quantity=2,
                last_unit_price_cents=1490,
                last_deposit_cents=310,
                sort_order=2,
                price_decision="zentraler_preis",
            ),
        ]
    )
    session.commit()
    session_factory = lambda: session

    panel = OrderPanel(session_factory=session_factory)
    panel.open_new_order_for_customer(customer.id)

    assert panel.customer_select.current_value() == customer.id
    assert panel.assortment_table.rowCount() == 2
    assert panel.assortment_table.item(0, 0).text() == water.name
    assert panel.assortment_table.item(0, 1).text() == "4"
    assert panel.order_lines_table.rowCount() == 2
    assert panel.order_lines_table.item(0, 0).text() == water.name
    assert panel.order_lines_table.item(0, 1).text() == "4"
    assert panel.order_lines_table.item(1, 0).text() == spezi.name
    assert panel.order_lines_table.item(1, 1).text() == "2"
    assert "letzten Mengen" in panel.status_label.text()
    panel.close_order_dialog()


def test_order_panel_prefills_customer_assortment_when_customer_is_selected_in_empty_order(session):
    _app()
    from getraenkeladen_tool.models import Customer, CustomerAssortmentItem, Product
    from getraenkeladen_tool.ui.order_panel import OrderPanel

    customer = Customer(name="Cafe Nord", folder_path="/tmp/Cafe Nord", address="Markt 1", is_active=True)
    water = Product(
        name="Adelholzener Wasser 12x0,7",
        unit="Kiste",
        standard_price_cents=890,
        default_deposit_cents=330,
        is_active=True,
    )
    spezi = Product(
        name="Paulaner Spezi 20x0,5",
        unit="Kiste",
        standard_price_cents=1490,
        default_deposit_cents=310,
        is_active=True,
    )
    session.add_all([customer, water, spezi])
    session.flush()
    session.add_all(
        [
            CustomerAssortmentItem(
                customer_id=customer.id,
                product_id=water.id,
                source_product_name=water.name,
                last_quantity=4,
                last_unit_price_cents=890,
                last_deposit_cents=330,
                sort_order=1,
                price_decision="zentraler_preis",
            ),
            CustomerAssortmentItem(
                customer_id=customer.id,
                product_id=spezi.id,
                source_product_name=spezi.name,
                last_quantity=0,
                last_unit_price_cents=1490,
                last_deposit_cents=310,
                sort_order=2,
                price_decision="zentraler_preis",
            ),
        ]
    )
    session.commit()

    panel = OrderPanel(session_factory=lambda: session)
    panel.reset_order_form()
    panel.customer_select.select_value(customer.id)

    assert panel.order_lines_table.rowCount() == 2
    assert panel.order_lines_table.item(0, 0).text() == water.name
    assert panel.order_lines_table.item(0, 1).text() == "4"
    assert panel.order_lines_table.item(1, 0).text() == spezi.name
    assert panel.order_lines_table.item(1, 1).text() == "0"


def test_order_panel_uses_single_editable_quantity_list_for_new_order():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "order_entry_splitter = ResponsiveSplitter()" not in source
    assert "Links Produkt erfassen, rechts die Positionen wie in einer Belegliste kontrollieren." not in source
    assert "Mengenliste bearbeiten" in source
    assert "self.assortment_table.setVisible(False)" in source
    assert "self.add_product_toggle.setCheckable(True)" in source
    assert "self.add_product_content.setVisible(False)" in source
    assert "self.add_product_box = QGroupBox" not in source
    assert "new_order_layout.addWidget(quantity_box)" in source
    assert "new_order_layout.addWidget(position_box)" not in source
    assert "new_order_layout.addWidget(line_box)" not in source


def test_order_panel_prefills_zero_quantity_assortment_lines_as_empty_order_placeholders(session):
    _app()
    from getraenkeladen_tool.models import Customer, CustomerAssortmentItem, Product
    from getraenkeladen_tool.ui.order_panel import OrderPanel

    customer = Customer(name="Cafe Nord", folder_path="/tmp/Cafe Nord", address="Markt 1", is_active=True)
    water = Product(
        name="Adelholzener Wasser 12x0,7",
        unit="Kiste",
        standard_price_cents=890,
        default_deposit_cents=330,
        is_active=True,
    )
    spezi = Product(
        name="Paulaner Spezi 20x0,5",
        unit="Kiste",
        standard_price_cents=1490,
        default_deposit_cents=310,
        is_active=True,
    )
    session.add_all([customer, water, spezi])
    session.flush()
    session.add_all(
        [
            CustomerAssortmentItem(
                customer_id=customer.id,
                product_id=water.id,
                source_product_name=water.name,
                last_quantity=0,
                last_unit_price_cents=890,
                last_deposit_cents=330,
                sort_order=1,
                price_decision="zentraler_preis",
            ),
            CustomerAssortmentItem(
                customer_id=customer.id,
                product_id=spezi.id,
                source_product_name=spezi.name,
                last_quantity=2,
                last_unit_price_cents=1490,
                last_deposit_cents=310,
                sort_order=2,
                price_decision="zentraler_preis",
            ),
        ]
    )
    session.commit()

    panel = OrderPanel(session_factory=lambda: session)
    panel.open_new_order_for_customer(customer.id)

    assert panel.order_lines_table.rowCount() == 2
    assert panel.order_lines_table.item(0, 0).text() == water.name
    assert panel.order_lines_table.item(0, 1).text() == "0"
    assert panel.order_lines_table.item(1, 0).text() == spezi.name
    assert panel.order_lines_table.item(1, 1).text() == "2"
    assert "Positionen aus den letzten Mengen" in panel.status_label.text()
    panel.close_order_dialog()


def test_order_panel_product_picker_shows_customer_recommendations_before_all_products(session):
    _app()
    from getraenkeladen_tool.models import Customer, CustomerAssortmentItem, Product
    from getraenkeladen_tool.ui.order_panel import OrderPanel

    customer = Customer(name="Cafe Nord", folder_path="/tmp/Cafe Nord", address="Markt 1", is_active=True)
    water = Product(
        name="Wasser 12x0,7",
        unit="Kiste",
        standard_price_cents=1299,
        default_deposit_cents=330,
        is_active=True,
    )
    spezi = Product(
        name="Spezi 20x0,5",
        unit="Kiste",
        standard_price_cents=1490,
        default_deposit_cents=310,
        is_active=True,
    )
    session.add_all([customer, water, spezi])
    session.flush()
    session.add(
        CustomerAssortmentItem(
            customer_id=customer.id,
            product_id=water.id,
            source_product_name=water.name,
            last_quantity=4,
            last_unit_price_cents=1299,
            last_deposit_cents=330,
            sort_order=1,
            price_decision="zentraler_preis",
        )
    )
    session.commit()

    panel = OrderPanel(session_factory=lambda: session)
    panel.customer_select.select_value(customer.id)

    assert panel.product_select.visible_labels() == [
        "Empfohlen fuer diesen Kunden",
        "Wasser 12x0,7",
        "Alle Artikel",
        "Spezi 20x0,5",
    ]


def test_order_panel_prefills_from_latest_order_when_customer_has_no_assortment(session):
    _app()
    from getraenkeladen_tool.models import Customer, Order, OrderLine, Product
    from getraenkeladen_tool.ui.order_panel import OrderPanel

    customer = Customer(name="Cafe Nord", folder_path="/tmp/Cafe Nord", address="Markt 1", is_active=True)
    water = Product(
        name="Adelholzener Wasser 12x0,7",
        unit="Kiste",
        standard_price_cents=890,
        default_deposit_cents=330,
        is_active=True,
    )
    spezi = Product(
        name="Paulaner Spezi 20x0,5",
        unit="Kiste",
        standard_price_cents=1490,
        default_deposit_cents=310,
        is_active=True,
    )
    session.add_all([customer, water, spezi])
    session.flush()
    session.add(
        Order(
            order_number="ALT-1",
            customer_id=customer.id,
            order_date="2026-07-01",
            delivery_date="2026-07-01",
            status="geplant",
            lines=[
                OrderLine(
                    product_id=water.id,
                    product_name=water.name,
                    quantity=4,
                    unit_price_cents=890,
                    deposit_cents=330,
                ),
                OrderLine(
                    product_id=spezi.id,
                    product_name=spezi.name,
                    quantity=2,
                    unit_price_cents=1490,
                    deposit_cents=310,
                ),
            ],
        )
    )
    session.commit()

    panel = OrderPanel(session_factory=lambda: session)
    panel.open_new_order_for_customer(customer.id)

    assert panel.customer_select.current_value() == customer.id
    assert panel.assortment_table.rowCount() == 2
    assert panel.assortment_table.item(0, 0).text() == water.name
    assert panel.assortment_table.item(0, 1).text() == "4"
    assert panel.order_lines_table.rowCount() == 2
    assert panel.order_lines_table.item(0, 0).text() == water.name
    assert panel.order_lines_table.item(0, 1).text() == "4"
    assert panel.order_lines_table.item(1, 0).text() == spezi.name
    assert panel.order_lines_table.item(1, 1).text() == "2"
    assert "letzter Bestellung" in panel.status_label.text()
    panel.close_order_dialog()


def test_order_panel_skips_unresolved_assortment_items_when_prefilling_from_customer_folder(session):
    _app()
    from getraenkeladen_tool.models import Customer, CustomerAssortmentItem, Product
    from getraenkeladen_tool.ui.order_panel import OrderPanel

    customer = Customer(name="Cafe Nord", folder_path="/tmp/Cafe Nord", is_active=True)
    water = Product(
        name="Adelholzener Wasser 12x0,7",
        unit="Kiste",
        standard_price_cents=890,
        default_deposit_cents=330,
        is_active=True,
    )
    session.add_all([customer, water])
    session.flush()
    session.add_all(
        [
            CustomerAssortmentItem(
                customer_id=customer.id,
                product_id=water.id,
                source_product_name=water.name,
                last_quantity=4,
                last_unit_price_cents=890,
                last_deposit_cents=330,
                sort_order=1,
            ),
            CustomerAssortmentItem(
                customer_id=customer.id,
                product_id=None,
                source_product_name="Unbekannte Limo 20x0,5",
                last_quantity=3,
                last_unit_price_cents=1090,
                last_deposit_cents=310,
                sort_order=2,
            ),
        ]
    )
    session.commit()
    session_factory = lambda: session

    panel = OrderPanel(session_factory=session_factory)
    panel.open_new_order_for_customer(customer.id)

    assert panel.order_lines_table.rowCount() == 1
    assert panel.order_lines_table.item(0, 0).text() == water.name
    assert "Ungeklaerte Artikel wurden ausgelassen." in panel.status_label.text()
    panel.close_order_dialog()


def test_order_panel_skips_open_price_mismatches_when_prefilling_from_customer_folder(session):
    _app()
    from getraenkeladen_tool.models import Customer, CustomerAssortmentItem, Product
    from getraenkeladen_tool.ui.order_panel import OrderPanel

    customer = Customer(name="Cafe Nord", folder_path="/tmp/Cafe Nord", is_active=True)
    water = Product(
        name="Adelholzener Wasser 12x0,7",
        unit="Kiste",
        standard_price_cents=890,
        default_deposit_cents=330,
        is_active=True,
    )
    frucade = Product(
        name="Frucade Colamix 20x0,5",
        unit="Kiste",
        standard_price_cents=1190,
        default_deposit_cents=310,
        is_active=True,
    )
    session.add_all([customer, water, frucade])
    session.flush()
    session.add_all(
        [
            CustomerAssortmentItem(
                customer_id=customer.id,
                product_id=water.id,
                source_product_name=water.name,
                last_quantity=4,
                last_unit_price_cents=890,
                last_deposit_cents=330,
                sort_order=1,
                price_decision="zentraler_preis",
            ),
            CustomerAssortmentItem(
                customer_id=customer.id,
                product_id=frucade.id,
                source_product_name=frucade.name,
                last_quantity=3,
                last_unit_price_cents=1048,
                last_deposit_cents=310,
                sort_order=2,
                price_decision="offen",
            ),
        ]
    )
    session.commit()

    panel = OrderPanel(session_factory=lambda: session)
    panel.open_new_order_for_customer(customer.id)

    assert panel.order_lines_table.rowCount() == 1
    assert panel.order_lines_table.item(0, 0).text() == water.name
    assert "Preisabweichungen wurden ausgelassen." in panel.status_label.text()
    panel.close_order_dialog()


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
    assert "Nur Excel-Lieferschein" in source
    assert "Nur PDF-Lieferschein" in source
    assert "Lieferschein als Excel + PDF erstellen" in source
    assert "Nur Excel-Rechnung" in source
    assert "Nur PDF-Rechnung" in source
    assert "Rechnung als Excel + PDF erstellen" in source
    assert "self.create_both_button.clicked.connect(self.create_complete_document)" in source
    assert "self.create_excel_button.clicked.connect(self.create_excel_document)" in source
    assert "self.create_pdf_button.clicked.connect(self.create_pdf_document)" in source
    assert "self._created_asset_label(assets)" in source
    assert 'return "Excel + PDF"' in source
    assert "QMessageBox.information" in source
    assert "QMessageBox.critical" in source
    assert "QMessageBox.warning" in source
    assert "Erstellung fehlgeschlagen" in source
    assert "Kundenbestellung suchen" in source
    assert 'self.order_select = SearchableSelect("Kunde, Bestellnummer oder Lieferdatum suchen")' in source
    assert "self.order_select.set_items(" in source
    assert "self.order_select.current_value()" in source
    assert "self.orders_table = QTableWidget" not in source
    assert "Auftraege laden" not in source
    assert "Excel:" in source
    assert "PDF:" in source
    assert "Nummer vorschlagen" in source
    assert "suggest_document_number" in source
    assert "Lieferpauschale hinzufuegen?" in source
    assert "self.delivery_fee_choice = QComboBox()" in source
    assert "self.document_note = QLineEdit()" in source
    assert "rote Hauptbutton" not in source


def test_order_panel_document_actions_use_loaded_order_when_table_selection_is_empty():
    _app()
    from getraenkeladen_tool.ui.order_panel import OrderPanel

    panel = OrderPanel(session_factory=None)
    emitted_delivery_order_ids = []
    emitted_invoice_order_ids = []
    panel.current_order_id = 42
    panel.orders_table.clearSelection()
    panel.delivery_note_requested.connect(emitted_delivery_order_ids.append)
    panel.invoice_requested.connect(emitted_invoice_order_ids.append)

    panel.request_delivery_note_for_selected_order()
    panel.request_invoice_for_selected_order()

    assert emitted_delivery_order_ids == [42]
    assert emitted_invoice_order_ids == [42]


def test_document_workflow_uses_compact_order_search_instead_of_large_order_list():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "SearchableSelect" in source
    assert "Diese Bestellung verwenden" in source
    assert "Suche zuruecksetzen" in source
    assert "Ausgewaehlte Bestellung" in source
    assert "Kunde, Bestellnummer oder Lieferdatum suchen" in source


def test_document_workflow_keeps_main_excel_pdf_action_always_visible():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "self.document_tabs = QTabWidget()" in source
    assert "self.document_tabs.setUsesScrollButtons(False)" in source
    assert 'addTab(positions_tab, "Artikel pruefen")' in source
    assert 'addTab(deposit_tab, "Pfand")' in source
    assert 'addTab(output_tab, "Ausgabe")' in source
    assert "finish_bar.setObjectName(\"documentFinishBar\")" in source
    assert "finish_layout.addWidget(self.create_both_button)" in source
    assert "self.more_output_box.setCheckable(True)" in source
    assert "Nur PDF-Rechnung" in source
    assert "Nur PDF-Lieferschein" in source


def test_document_workflow_hides_order_search_after_preselected_order_is_loaded():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "self.order_box = order_box" in source
    assert "self.order_box.setVisible(False)" in source
    assert "self.order_box.setVisible(True)" in source
    assert 'self.status_label.setText("Bestellung verwendet. Artikel pruefen und danach Excel oder PDF erstellen.")' in source


def test_document_workflow_allows_editing_lines_and_deposit_returns():
    from getraenkeladen_tool.ui.deposit_return_presets import DEPOSIT_RETURN_PRESETS

    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "DEPOSIT_RETURN_PRESETS" in source
    assert DEPOSIT_RETURN_PRESETS == (
        ("Pfand 1,50 EUR", 150),
        ("Pfand 3,10 EUR", 310),
        ("Pfand 4,50 EUR", 450),
    )
    assert "self.deposit_return_select = QComboBox()" in source
    assert "self.deposit_return_select.currentIndexChanged.connect(self.apply_selected_deposit_return)" in source
    assert '"removeDocumentLineButton": "Position entfernen"' in source
    assert '"addDocumentDepositReturnButton": "Pfand-Rueckgabe eintragen"' in source
    assert '"removeDocumentDepositReturnButton": "Pfand-Rueckgabe entfernen"' in source
    assert "self.remove_line_button.clicked.connect(self.remove_selected_line)" in source
    assert "self.add_return_button.clicked.connect(self.add_deposit_return)" in source
    assert "self.remove_return_button.clicked.connect(self.remove_selected_deposit_return)" in source
    assert 'self.remove_line_button.setObjectName("dangerAction")' in source
    assert 'self.remove_return_button.setObjectName("dangerAction")' in source
    assert "def add_deposit_return" in source
    assert "def apply_selected_deposit_return" in source
    assert "def remove_selected_line" in source


def test_document_workflow_preview_uses_shared_core_calculation():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "berechne_beleg" in source
    assert "BelegParameter(lieferpauschale_aktiv=self._delivery_fee_enabled())" in source


def test_document_workflow_uses_clearer_deposit_and_delivery_fee_labels():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert 'DOCUMENT_LINE_COLUMNS = ("Artikel", "Menge", "Preis je Einheit EUR", "Pfand je Einheit EUR", "Summe EUR")' in source
    assert '"addDocumentDepositReturnButton": "Pfand-Rueckgabe eintragen"' in source
    assert "Lieferpauschale hinzufuegen?" in source
    assert "Keine Pauschale" in source
    assert "3,90 EUR hinzufuegen" in source
    assert "Nur Beleg-Korrektur" in source
    assert "Lieferschein-Nummer" in source
    assert "Hinweis auf dem Lieferschein" in source
    assert "Zahlungshinweis auf Rechnung" in source


def test_document_workflow_prioritizes_complete_excel_pdf_generation():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "def create_complete_document" in source
    assert 'self.create_document({"excel", "pdf"})' in source
    assert "self.create_both_button" in source
    assert "finish_layout.addWidget(self.create_both_button)" in source
    assert "secondary_action_row.addWidget(self.create_excel_button)" in source
    assert "secondary_action_row.addWidget(self.create_pdf_button)" in source
    assert "Excel + PDF erstellt" in source
    assert "Normalerweise reicht der Hauptbutton: Excel und PDF zusammen erstellen." in source


def test_order_panel_supports_editing_existing_orders():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.order_mode_label" in source
    assert "Bestellung bearbeiten" in source
    assert "update_order(" in source
    assert "def populate_order_form" in source
    assert "self.order_lines_table.setRowCount(0)" in source
    assert "Bestellung" in source


def test_order_panel_uses_main_window_editor_for_editing():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.order_dialog" in source
    assert "def open_order_dialog" in source
    assert "def close_order_dialog_after_success" in source
    assert "Neue Bestellung" in source
    assert "Bestellung speichern" in source
    assert "orderEditorWorkspace" in source
    assert "layout.addWidget(self.order_editor_widget, 2)" in source
    assert "WA_DeleteOnClose" not in source
    assert "self.order_dialog.setMinimumSize(760, 480)" not in source
    assert "self.order_dialog.resize(1020, 620)" not in source
    assert "self.order_workspace_tabs = QTabWidget()" not in source
    assert "self.order_editor_widget" in source


def test_order_editor_is_embedded_in_main_window_instead_of_modal_dialog():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.order_editor_widget = QWidget()" in source
    assert 'self.order_editor_widget.setObjectName("orderEditorWorkspace")' in source
    assert "layout.addWidget(self.order_editor_widget, 2)" in source
    assert "self.assortment_table.setVisible(False)" in source
    assert "self.order_lines_table.setMinimumHeight(220)" in source
    assert "self.deposit_returns_table.setMaximumHeight(110)" in source


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
    assert "Bestellsumme" in source


def test_order_panel_exposes_deposit_returns_new_order_and_copy_actions():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert '"newOrderButton": "Neue Bestellung"' in source
    assert '"copyOrderButton": "Als Vorlage kopieren"' in source
    assert '"addDepositReturnButton": "Pfand-Rueckgabe eintragen"' in source
    assert "self.deposit_returns_table" in source
    assert "self.deposit_return_select = QComboBox()" in source
    assert "DEPOSIT_RETURN_PRESETS" in source
    assert "def reset_order_form" in source
    assert "def copy_selected_order_as_new" in source


def test_order_panel_warns_before_changing_documented_orders():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.current_order_status" in source
    assert "def confirm_documented_order_change" in source
    assert "Dateien bitte neu erstellen" in source


def test_order_panel_has_price_mismatch_confirmation_dialog():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "def confirm_price_mismatch" in source
    assert "QMessageBox.question" in source
    assert "Preisabweichung gefunden" in source
    assert "Zentral gepflegter Preis" in source
    assert "Preis aus Excel" in source
    assert "use_central_price = self.confirm_price_mismatch" in source
    assert "unit_price_cents = product.standard_price_cents" in source


def test_order_panel_guides_next_step_after_successful_save():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "def show_saved_order_next_steps" in source
    assert "Bestellung gespeichert" in source
    assert "Was moechten Sie als Naechstes tun?" in source
    assert "Nur speichern" in source
    assert "Lieferschein erstellen" in source
    assert "Rechnung erstellen" in source
    assert "Weitere Bestellung" in source
    assert "self.delivery_note_requested.emit(order_id)" in source
    assert "self.invoice_requested.emit(order_id)" in source


def test_order_panel_warns_clearly_before_invalid_save():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "def warn_invalid_order_save" in source
    assert "Bitte eine Bestellnummer eintragen." in source
    assert "Bitte mindestens eine Position hinzufuegen." in source
    assert "QMessageBox.warning" in source


def test_order_panel_uses_clearer_labels_for_less_technical_users():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert '"copyOrderButton": "Als Vorlage kopieren"' in source
    assert '"addDepositReturnButton": "Pfand-Rueckgabe eintragen"' in source
    assert '"removeDepositReturnButton": "Pfand-Rueckgabe entfernen"' in source
    assert 'ORDER_LINE_COLUMNS = ("Produkt", "Menge", "Preis je Einheit EUR", "Pfand je Einheit EUR", "Summe EUR")' in source
    assert 'customer_form.addRow("Bestellnummer", order_number_row)' in source
    assert "Auftragssumme" not in source


def test_order_panel_loads_customer_assortment_into_order_dialog():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "list_customer_assortment" in source
    assert "ASSORTMENT_COLUMNS" in source
    assert "self.assortment_table = QTableWidget" in source
    assert "self.assortment_table.setVisible(False)" in source
    assert "def refresh_customer_assortment" in source
    assert "self.customer_select.selection_changed.connect(self.apply_selected_customer)" in source
    assert "self.refresh_customer_assortment(customer.id)" in source
    assert "self.use_assortment_button.clicked.connect(self.add_selected_assortment_item)" in source
    assert "def add_selected_assortment_item" in source
    assert "row.price_differs_from_central" in source
    assert 'row.price_decision == "offen"' in source


def test_order_panel_filters_orders_by_customer_and_can_copy_existing_order():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert '"copyOrderButton": "Als Vorlage kopieren"' in source
    assert "self.order_table_search = QLineEdit()" in source
    assert "self.order_table_search.textChanged.connect(self.apply_order_table_search)" in source
    assert "def apply_order_table_search" in source
    assert "def copy_selected_order_as_new" in source
    assert "self.current_order_id = None" in source
    assert "Kopie aus Bestellung" in source
    assert "list_active_orders(session)" in source
    assert "open_order_dialog" in source


def test_order_panel_focuses_on_order_management_not_document_creation():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert '"saveOrderButton": "Bestellung speichern"' in source
    assert '"createDeliveryOrderButton"' not in source
    assert '"createInvoiceButton"' not in source
    assert "Excel/PDF aus Auftrag erstellen" not in source


def test_order_panel_uses_resize_friendly_single_flow_workspaces():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "QDialog" in source
    assert "PageHeader" in source
    assert "self.order_editor_widget" in source
    assert "layout.addWidget(orders_box, 1)" in source
    assert "new_order_layout.addWidget(quantity_box)" in source
    assert "self.add_product_toggle.setChecked(False)" in source
    assert "ResponsiveSplitter" not in source
    assert "setMaximumHeight(180)" not in source


def test_order_panel_uses_readable_total_bar_and_disclosure_for_extra_products():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")
    theme = Path("src/getraenkeladen_tool/ui/theme.py").read_text(encoding="utf-8")

    assert "total_bar.setMinimumHeight(58)" in source
    assert "total_layout.setContentsMargins(16, 10, 16, 10)" in source
    assert "self.order_total_label.setObjectName(\"totalAmount\")" in source
    assert 'QPushButton#disclosureButton' in theme
    assert 'QWidget#disclosurePanel' in theme


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


def test_order_line_context_menu_can_copy_selected_position_into_order():
    _app()
    from getraenkeladen_tool.ui.order_panel import OrderPanel

    panel = OrderPanel(session_factory=None)
    panel._append_order_line_to_table("Wasser 12x0,7", 4, 1299, 330, product_id=12)
    panel.order_lines_table.setCurrentCell(0, 0)

    panel.copy_selected_order_line()

    assert panel.order_lines_table.rowCount() == 2
    assert panel.order_lines_table.item(1, 0).text() == "Wasser 12x0,7"
    assert panel.order_lines_table.item(1, 1).text() == "4"
    assert panel.order_lines_table.item(1, 2).text() == "12,99"
    assert panel.order_lines_table.item(1, 3).text() == "3,30"
    assert panel.order_lines_table.item(1, 0).data(Qt.ItemDataRole.UserRole) == 12
    assert "Position in die neue Bestellung uebernommen" in panel.status_label.text()


def test_order_line_table_has_context_menu_for_copying_positions():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.order_lines_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)" in source
    assert "self.order_lines_table.customContextMenuRequested.connect(self.show_order_line_context_menu)" in source
    assert "def show_order_line_context_menu" in source
    assert "Position in neue Bestellung uebernehmen" in source
    assert "def copy_selected_order_line" in source


def test_order_panel_runs_automation_warnings_before_save():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "from ..services.automation_service import validate_order_before_save" in source
    assert "from ..services.deposit_service import validate_deposit_returns" in source
    assert "*validate_order_before_save(session, payload, exclude_order_id=self.current_order_id)" in source
    assert "*validate_deposit_returns(payload)" in source
    assert "def confirm_automation_warnings" in source
    assert "Pruefung vor dem Speichern" in source
    assert "Blocker" in source
    assert "Warnungen" in source
    assert "Hinweise" in source


def test_order_panel_offers_free_order_number_suggestion_without_autofill():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "suggest_order_number" in source
    assert '"suggestOrderNumberButton": "Nummer vorschlagen"' in source
    assert "self.suggest_order_number_button.clicked.connect(self.apply_suggested_order_number)" in source
    assert "self.order_number.setText(suggestion)" in source


def test_document_workflow_runs_asset_verification_after_export():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "from ..services.automation_service import verify_document_assets" in source
    assert "verification = verify_document_assets(session, document.id, expected_assets=assets)" in source
    assert "Belegpruefung: OK." in source


def test_order_context_archive_does_not_open_edit_dialog():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "elif selected == archive_action:" in source
    assert "self.current_order_id = self._selected_order_id()" in source
    assert "self.load_selected_order_id()\n            self.archive_selected_order()" not in source
