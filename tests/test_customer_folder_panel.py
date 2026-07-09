from pathlib import Path
from types import SimpleNamespace


def _app():
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def test_customer_folder_panel_exposes_real_folder_workflow():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "class CustomerFolderPanel" in source
    assert "PageHeader(" in source
    assert '"Kundenordner"' in source
    assert 'SearchableSelect("Kunde suchen' in source
    assert "Kundenakte" in source
    assert "Kundenordner oeffnen" in source
    assert "Kundenliste aktualisieren" in source
    assert "Dateien im Kundenordner" in source
    assert "Aus alter Bestellung weiterarbeiten" in source
    assert "Neue Bestellung aus letzten Mengen starten" in source
    assert "Excel ansehen" in source
    assert "Bestellung markieren, dann Beleg erstellen oder als neue Bestellung kopieren." in source
    assert "Lieferschein erstellen" in source
    assert "Rechnung erstellen" in source
    assert "Bestellung oeffnen" in source
    assert "Bestellung loeschen" in source
    assert "Willst du diese Bestellung wirklich loeschen?" in source
    assert "workflow_primary_actions" in source
    assert "workflow_document_actions" in source
    assert "workflow_delete_actions" in source
    assert "workflow_actions.addWidget(self.delete_order_button)" not in source
    assert "get_customer_folder_snapshot" in source


def test_customer_folder_panel_disables_actions_until_customer_context_exists():
    _app()
    from getraenkeladen_tool.ui.customer_folder_panel import CustomerFolderPanel

    panel = CustomerFolderPanel(session_factory=None)

    assert panel.open_folder_button.isEnabled() is False
    assert panel.open_file_button.isEnabled() is False
    assert panel.new_order_button.isEnabled() is False
    assert panel.seed_file_hint.text() == "Die Vorlage kommt aus den letzten importierten Mengen rechts."
    assert panel.delivery_note_button.isEnabled() is False
    assert panel.invoice_button.isEnabled() is False
    assert panel.open_order_button.isEnabled() is False
    assert panel.delete_order_button.isEnabled() is False


def test_customer_folder_panel_enables_actions_from_snapshot_state(tmp_path: Path):
    _app()
    from getraenkeladen_tool.services.customer_folder_service import CustomerFolderFile
    from getraenkeladen_tool.ui.customer_folder_panel import CustomerFolderPanel

    folder = tmp_path / "Cafe Nord"
    folder.mkdir()
    excel_path = folder / "2026-05-01_RE_Cafe_Nord.xlsx"
    excel_path.write_text("placeholder", encoding="utf-8")
    pdf_path = folder / "2026-05-01_RE_Cafe_Nord.pdf"
    pdf_path.write_text("placeholder", encoding="utf-8")
    customer = SimpleNamespace(id=7, name="Cafe Nord")
    order = SimpleNamespace(id=11, order_number="BEST-11", delivery_date="2026-06-24", status="geplant")
    assortment_row = SimpleNamespace(
        product_name="Frucade",
        source_product_name="Frucade alt",
        last_quantity=3,
        current_price_cents=1190,
        current_deposit_cents=330,
        price_warning_text=None,
        needs_review=False,
        last_order_date="2026-06-20",
        order_count=3,
        total_quantity=12,
        sales_hint="regelmaessig bestellt",
    )
    snapshot = SimpleNamespace(
        customer=customer,
        folder_path=folder,
        folder_exists=True,
        files=[
            CustomerFolderFile(excel_path, "Excel-Rechnung", excel_path.name, True),
            CustomerFolderFile(pdf_path, "PDF", pdf_path.name, False),
        ],
        orders=[order],
    )
    panel = CustomerFolderPanel(session_factory=None)

    panel.show_snapshot(snapshot, [assortment_row])

    assert panel.current_customer_id == 7
    assert panel.files_table.item(0, 0).text() == excel_path.name
    assert panel.orders_table.item(0, 0).text() == "BEST-11"
    assert panel.assortment_table.item(0, 0).text() == "Frucade"
    assert panel.assortment_table.item(0, 2).text() == "20.06.2026"
    assert panel.assortment_table.item(0, 3).text() == "3x / 12 gesamt"
    assert panel.assortment_table.item(0, 5).text() == "regelmaessig bestellt"
    assert panel.open_folder_button.isEnabled() is True
    assert panel.new_order_button.isEnabled() is True
    assert panel.new_order_button.text() == "Neue Bestellung aus letzten Mengen starten"
    assert panel.seed_file_hint.text() == "Die Vorlage kommt aus den letzten importierten Mengen rechts."
    assert panel.delivery_note_button.isEnabled() is False
    assert panel.invoice_button.isEnabled() is False
    assert panel.open_order_button.isEnabled() is False
    assert panel.delete_order_button.isEnabled() is False

    panel.files_table.setCurrentCell(0, 0)
    panel.update_action_state()
    assert panel.open_file_button.isEnabled() is True
    assert panel.seed_file_hint.text() == f"Excel-Datei zum Nachsehen: {excel_path.name}"

    panel.files_table.setCurrentCell(1, 0)
    panel.update_action_state()
    assert panel.seed_file_hint.text() == "PDF ist nur zum Nachsehen. Neue Mengen stehen rechts."

    panel.orders_table.setCurrentCell(0, 0)
    panel.update_action_state()
    assert panel.open_order_button.isEnabled() is True
    assert panel.delivery_note_button.isEnabled() is True
    assert panel.invoice_button.isEnabled() is True
    assert panel.delete_order_button.isEnabled() is True


def test_customer_folder_panel_falls_back_when_qdesktopservices_does_not_open_folder(tmp_path: Path, monkeypatch):
    _app()
    from getraenkeladen_tool.services.customer_folder_service import CustomerFolderFile
    from getraenkeladen_tool.ui import customer_folder_panel
    from getraenkeladen_tool.ui.customer_folder_panel import CustomerFolderPanel

    folder = tmp_path / "BEGO Bremer Goldschlaegerei"
    folder.mkdir()
    excel_path = folder / "2026-06-24_LS-3050_BEGO.xlsx"
    excel_path.write_text("placeholder", encoding="utf-8")
    customer = SimpleNamespace(id=8, name="BEGO Bremer Goldschlaegerei")
    snapshot = SimpleNamespace(
        customer=customer,
        folder_path=folder,
        folder_exists=True,
        files=[CustomerFolderFile(excel_path, "Excel-Lieferschein", excel_path.name, True)],
        orders=[],
    )
    panel = CustomerFolderPanel(session_factory=None)
    fallback_paths = []

    monkeypatch.setattr(customer_folder_panel.QDesktopServices, "openUrl", lambda _url: False)
    monkeypatch.setattr(panel, "_open_path_with_system", lambda path: fallback_paths.append(path) or True)
    panel.show_snapshot(snapshot, [])

    panel.open_customer_folder()

    assert fallback_paths == [folder.resolve()]
    assert "Kundenordner geoeffnet" in panel.status_label.text()


def test_customer_folder_panel_limits_rendered_files_for_large_customer_folders(tmp_path: Path):
    _app()
    from getraenkeladen_tool.services.customer_folder_service import CustomerFolderFile
    from getraenkeladen_tool.ui.customer_folder_panel import CustomerFolderPanel, MAX_VISIBLE_FOLDER_FILES

    folder = tmp_path / "Cafe Nord"
    folder.mkdir()
    files = []
    for index in range(MAX_VISIBLE_FOLDER_FILES + 5):
        file_path = folder / f"2026-06-{index + 1:02d}_LS_Test_{index}.xlsx"
        file_path.write_text("placeholder", encoding="utf-8")
        files.append(CustomerFolderFile(file_path, "Excel-Lieferschein", file_path.name, True))
    customer = SimpleNamespace(id=7, name="Cafe Nord")
    snapshot = SimpleNamespace(
        customer=customer,
        folder_path=folder,
        folder_exists=True,
        files=files,
        orders=[],
    )
    panel = CustomerFolderPanel(session_factory=None)

    panel.show_snapshot(snapshot, [])

    assert panel.files_table.rowCount() == MAX_VISIBLE_FOLDER_FILES
    assert len(panel.files_by_row) == MAX_VISIBLE_FOLDER_FILES
    assert f"{len(files)} Dateien" in panel.status_label.text()
    assert f"neuesten {MAX_VISIBLE_FOLDER_FILES}" in panel.seed_file_hint.text()


def test_customer_folder_panel_limits_rendered_orders_for_large_order_history(tmp_path: Path):
    _app()
    from getraenkeladen_tool.ui.customer_folder_panel import CustomerFolderPanel, MAX_VISIBLE_ORDERS

    folder = tmp_path / "Cafe Nord"
    folder.mkdir()
    customer = SimpleNamespace(id=7, name="Cafe Nord")
    orders = [
        SimpleNamespace(id=index + 1, order_number=f"AUF-{index + 1:04d}", delivery_date="2026-06-24", status="geplant")
        for index in range(MAX_VISIBLE_ORDERS + 7)
    ]
    snapshot = SimpleNamespace(
        customer=customer,
        folder_path=folder,
        folder_exists=True,
        files=[],
        orders=orders,
    )
    panel = CustomerFolderPanel(session_factory=None)

    panel.show_snapshot(snapshot, [])

    assert panel.orders_table.rowCount() == MAX_VISIBLE_ORDERS
    assert len(panel.order_ids_by_row) == MAX_VISIBLE_ORDERS
    assert f"{len(orders)} Bestellungen" in panel.status_label.text()
    assert f"neuesten {MAX_VISIBLE_ORDERS}" in panel.workflow_hint.text()


def test_customer_folder_panel_clears_previous_customer_when_search_is_ambiguous(tmp_path: Path):
    _app()
    from getraenkeladen_tool.services.customer_folder_service import CustomerFolderFile
    from getraenkeladen_tool.ui.customer_folder_panel import CustomerFolderPanel

    folder = tmp_path / "Cafe Nord"
    folder.mkdir()
    excel_path = folder / "2026-05-01_RE_Cafe_Nord.xlsx"
    excel_path.write_text("placeholder", encoding="utf-8")
    customer = SimpleNamespace(id=7, name="Cafe Nord")
    snapshot = SimpleNamespace(
        customer=customer,
        folder_path=folder,
        folder_exists=True,
        files=[CustomerFolderFile(excel_path, "Excel-Rechnung", excel_path.name, True)],
        orders=[],
    )
    panel = CustomerFolderPanel(session_factory=None)
    panel.show_snapshot(snapshot, [])

    panel.clear_customer_context("Bitte einen Kunden aus der Trefferliste anklicken.")

    assert panel.current_customer_id is None
    assert panel.current_folder_path is None
    assert panel.files_table.rowCount() == 0
    assert panel.orders_table.rowCount() == 0
    assert panel.assortment_table.rowCount() == 0
    assert panel.new_order_button.isEnabled() is False
    assert panel.open_file_button.isEnabled() is False
    assert panel.status_label.text() == "Bitte einen Kunden aus der Trefferliste anklicken."


def test_customer_folder_panel_names_empty_order_action_when_no_seed_quantities(tmp_path: Path):
    _app()
    from getraenkeladen_tool.ui.customer_folder_panel import CustomerFolderPanel

    folder = tmp_path / "ADC Distribution GmbH"
    customer = SimpleNamespace(id=12, name="ADC Distribution GmbH")
    snapshot = SimpleNamespace(
        customer=customer,
        folder_path=folder,
        folder_exists=False,
        files=[],
        orders=[],
    )
    panel = CustomerFolderPanel(session_factory=None)

    panel.show_snapshot(snapshot, [])

    assert panel.new_order_button.isEnabled() is True
    assert panel.new_order_button.text() == "Ohne Kundenordner leere Bestellung starten"
    assert "Kundenordner fehlt" in panel.seed_file_hint.text()


def test_customer_folder_panel_uses_clear_customer_folder_language():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "Belege anstossen" not in source
    assert "Neue Bestellung aus letzten Mengen starten" in source
    assert "Excel ansehen" in source
    assert "Bestellungen dieses Kunden" in source
    assert "Bestellung markieren, dann Beleg erstellen oder als neue Bestellung kopieren." in source
    assert "Lieferschein erstellen" in source
    assert "Rechnung erstellen" in source


def test_customer_folder_panel_routes_selected_order_to_documents():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "def request_delivery_note_for_selected_order" in source
    assert "self.delivery_note_requested.emit(order_id)" in source
    assert "def request_invoice_for_selected_order" in source
    assert "self.invoice_requested.emit(order_id)" in source
    assert "Bitte zuerst eine Bestellung dieses Kunden auswaehlen" in source


def test_customer_folder_panel_routes_selected_order_to_new_order_copy():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "copy_order_requested = Signal(int)" in source
    assert "open_order_requested = Signal(int)" in source
    assert 'QPushButton("Bestellung oeffnen")' in source
    assert 'QPushButton("Als neue Bestellung kopieren")' in source
    assert "self.open_order_button.clicked.connect(self.request_open_selected_order)" in source
    assert "self.copy_order_button.clicked.connect(self.request_copy_for_selected_order)" in source
    assert "def request_open_selected_order" in source
    assert "self.open_order_requested.emit(order_id)" in source
    assert "def request_copy_for_selected_order" in source
    assert "self.copy_order_requested.emit(order_id)" in source


def test_customer_folder_panel_can_select_order_after_external_save():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "def select_order(self, order_id: int)" in source
    assert "self.orders_table.setCurrentCell(row, 0)" in source
    assert "self.orders_table.scrollToItem" in source
