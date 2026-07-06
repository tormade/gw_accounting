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
    assert '"Kunden"' in source
    assert 'SearchableSelect("Kunde suchen' in source
    assert "Kunden finden" in source
    assert "InspectorPanel" in source
    assert "Kundenlage" in source
    assert "Rechnungswarnung" in source
    assert "Nächster Schritt" in source
    assert "Bestellung starten" in source
    assert "Liste aktualisieren" in source
    assert "Letzte Dateien" in source
    assert "Letzte Mengen" in source
    assert "Excel ansehen" in source
    assert "Lieferschein erstellen" in source
    assert "Rechnung erstellen" in source
    assert "get_customer_folder_snapshot" in source
    assert "get_customer_invoice_warning" in source


def test_customer_folder_panel_disables_actions_until_customer_context_exists():
    _app()
    from getraenkeladen_tool.ui.customer_folder_panel import CustomerFolderPanel

    panel = CustomerFolderPanel(session_factory=None)

    assert panel.open_folder_button.isEnabled() is False
    assert panel.open_file_button.isEnabled() is False
    assert panel.new_order_button.isEnabled() is False
    assert panel.seed_file_hint.text() == "Kunde suchen, dann erscheinen letzte Mengen und passende Aktionen."
    assert panel.delivery_note_button.isEnabled() is False
    assert panel.invoice_button.isEnabled() is False
    assert panel.customer_next_step_label.text() == "Nächster Schritt: Kunde suchen."


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
    assert panel.open_folder_button.isEnabled() is True
    assert panel.new_order_button.isEnabled() is True
    assert panel.new_order_button.text() == "Neue Bestellung starten"
    assert panel.seed_file_hint.text() == "Letzte Mengen sind vorbereitet. Neue Bestellung starten und Mengen anpassen."
    assert panel.inspector.title_label.text() == "Cafe Nord"
    assert panel.customer_next_step_label.text() == "Nächster Schritt: Neue Bestellung starten; die letzten Mengen sind vorbereitet."
    assert panel.customer_invoice_warning_label.text() == "Offene Rechnungen: -"
    assert panel.delivery_note_button.isEnabled() is False
    assert panel.invoice_button.isEnabled() is False

    panel.files_table.setCurrentCell(0, 0)
    panel.update_action_state()
    assert panel.open_file_button.isEnabled() is True
    assert panel.seed_file_hint.text() == f"Excel-Datei zum Nachsehen: {excel_path.name}"

    panel.files_table.setCurrentCell(1, 0)
    panel.update_action_state()
    assert panel.seed_file_hint.text() == "PDF ist nur zum Nachsehen. Neue Mengen stehen rechts."

    panel.orders_table.setCurrentCell(0, 0)
    panel.update_action_state()
    assert panel.delivery_note_button.isEnabled() is True
    assert panel.invoice_button.isEnabled() is True


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
    assert panel.new_order_button.text() == "Leere Bestellung starten"
    assert "Kundenordner fehlt" in panel.seed_file_hint.text()


def test_customer_folder_panel_uses_clear_customer_folder_language():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "Belege anstossen" not in source
    assert "Bestellung starten" in source
    assert "Excel ansehen" in source
    assert "Bestellungen dieses Kunden" in source
    assert "Lieferschein erstellen" in source
    assert "Rechnung erstellen" in source


def test_customer_folder_panel_routes_selected_order_to_documents():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "def request_delivery_note_for_selected_order" in source
    assert "self.delivery_note_requested.emit(order_id)" in source
    assert "def request_invoice_for_selected_order" in source
    assert "self.invoice_requested.emit(order_id)" in source
    assert "Bitte zuerst eine Bestellung dieses Kunden auswählen" in source


def test_customer_folder_panel_shows_automation_quickstart_suggestions():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "from ..services.automation_service import get_customer_quickstart, list_customer_folder_excel_previews" in source
    assert "quickstart = get_customer_quickstart(session, customer.id)" in source
    assert "quickstart.suggestions" in source
    assert "excel_previews = list_customer_folder_excel_previews(session, customer.id)" in source
    assert "Neue Excel-Datei" in source


def test_customer_folder_panel_emits_new_order_for_selected_customer(tmp_path: Path):
    _app()
    from getraenkeladen_tool.ui.customer_folder_panel import CustomerFolderPanel

    folder = tmp_path / "Cafe Nord"
    customer = SimpleNamespace(id=7, name="Cafe Nord")
    snapshot = SimpleNamespace(
        customer=customer,
        folder_path=folder,
        folder_exists=False,
        files=[],
        orders=[],
    )
    panel = CustomerFolderPanel(session_factory=None)
    requested_ids: list[int] = []
    panel.new_order_requested.connect(requested_ids.append)

    panel.show_snapshot(snapshot, [])
    panel.request_new_order()

    assert requested_ids == [7]


def test_customer_folder_panel_loads_last_quantities_from_latest_order_when_assortment_is_empty():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "list_customer_assortment_with_order_fallback" in source
    assert "Letzte Mengen aus letzter Bestellung" in source
    assert "Neue Bestellung starten" in source
    assert "self.customer_context_tabs.setCurrentIndex(0)" in source


def test_customer_folder_panel_keeps_next_step_short_enough_for_inspector():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "quickstart.suggestions[0]" in source
    assert '" | ".join(quickstart.suggestions[:3])' not in source
    assert 'self.customer_next_step_label.setObjectName("nextStepValue")' in source
    assert "self.customer_next_step_label.setMinimumHeight(72)" in source
