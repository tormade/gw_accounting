from pathlib import Path

from openpyxl import load_workbook

from getraenkeladen_tool.services.excel_service import (
    TEMPLATE_PATH,
    build_delivery_note_workbook,
    build_invoice_workbook,
)


def test_winklmeier_template_is_available():
    assert TEMPLATE_PATH.exists()


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
    assert sheet["A8"].value == "Rechnung"
    assert sheet["F8"].value == "RG-1001"
    assert sheet["A13"].value == 10
    assert sheet["B13"].value == "Wasser"
    assert sheet["D13"].value == 12.99
    assert sheet["E13"].value == "=(C13+D13)*A13"
    assert sheet.print_area == "'Tabelle1'!$A$1:$F$48"


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
    assert sheet["A8"].value == "Lieferschein"
    assert sheet["F8"].value == "LS-2001"
    assert sheet["A13"].value == 4
    assert sheet["B13"].value == "Apfelschorle"
