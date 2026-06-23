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
    assert 'PageHeader("Kundenordner"' in source
    assert 'SearchableSelect("Kunde suchen' in source
    assert "Kundenakte" in source
    assert "Kundenordner oeffnen" in source
    assert "Dateien im Kundenordner" in source
    assert "Letzte bekannte Bestellung" in source
    assert "Neue Bestellung fuer Kunden" in source
    assert "Lieferschein erstellen" in source
    assert "Rechnung erstellen" in source
    assert "get_customer_folder_snapshot" in source


def test_customer_folder_panel_disables_actions_until_customer_context_exists():
    _app()
    from getraenkeladen_tool.ui.customer_folder_panel import CustomerFolderPanel

    panel = CustomerFolderPanel(session_factory=None)

    assert panel.open_folder_button.isEnabled() is False
    assert panel.open_file_button.isEnabled() is False
    assert panel.new_order_button.isEnabled() is False
    assert panel.delivery_note_button.isEnabled() is False
    assert panel.invoice_button.isEnabled() is False


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
    assert panel.delivery_note_button.isEnabled() is False
    assert panel.invoice_button.isEnabled() is False

    panel.files_table.setCurrentCell(0, 0)
    panel.update_action_state()
    assert panel.open_file_button.isEnabled() is True

    panel.orders_table.setCurrentCell(0, 0)
    panel.update_action_state()
    assert panel.delivery_note_button.isEnabled() is True
    assert panel.invoice_button.isEnabled() is True
