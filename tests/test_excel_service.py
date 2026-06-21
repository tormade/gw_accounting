from pathlib import Path

from openpyxl import load_workbook

from getraenkeladen_tool.services.excel_service import (
    build_delivery_note_workbook,
    build_invoice_workbook,
)


def test_build_invoice_workbook_writes_customer_excel_file(tmp_path: Path):
    output_path = tmp_path / "Kunden" / "Cafe Nord" / "RG-1001.xlsx"

    build_invoice_workbook(
        output_path=output_path,
        customer_name="Cafe Nord",
        document_number="RG-1001",
        line_items=[{"name": "Wasser", "quantity": 10, "unit_price_cents": 1299}],
    )

    workbook = load_workbook(output_path)
    sheet = workbook.active
    assert sheet["A1"].value == "Rechnung"
    assert sheet["B3"].value == "RG-1001"
    assert sheet["A6"].value == "Wasser"
    assert sheet["D6"].value == 12.99


def test_build_delivery_note_workbook_writes_customer_excel_file(tmp_path: Path):
    output_path = tmp_path / "Kunden" / "Cafe Nord" / "LS-2001.xlsx"

    build_delivery_note_workbook(
        output_path=output_path,
        customer_name="Cafe Nord",
        document_number="LS-2001",
        line_items=[{"name": "Apfelschorle", "quantity": 4, "unit_price_cents": 1499}],
    )

    workbook = load_workbook(output_path)
    sheet = workbook.active
    assert sheet["A1"].value == "Lieferschein"
    assert sheet["B3"].value == "LS-2001"
    assert sheet["A6"].value == "Apfelschorle"
