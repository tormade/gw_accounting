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
    assert sheet["F32"].value == "=SUM(E13:E30)"
    assert workbook.calculation.calcMode == "auto"
    assert workbook.calculation.forceFullCalc is True
    assert sheet.print_area == "'Tabelle1'!$A$1:$F$48"


def test_build_delivery_order_workbook_writes_customer_excel_file(tmp_path: Path):
    output_path = tmp_path / "Kunden" / "Cafe Nord" / "LS-2001.xlsx"

    build_delivery_note_workbook(
        output_path=output_path,
        customer_name="Cafe Nord",
        document_number="LS-2001",
        line_items=[{"name": "Apfelschorle", "quantity": 4, "unit_price_cents": 1499}],
    )

    workbook = load_workbook(output_path)
    sheet = workbook.active
    assert sheet["A8"].value == "Lieferauftrag"
    assert sheet["F8"].value == "LS-2001"
    assert sheet["A13"].value == 4
    assert sheet["B13"].value == "Apfelschorle"


def test_build_invoice_workbook_refreshes_sum_formulas_for_all_item_rows(tmp_path: Path):
    output_path = tmp_path / "Kunden" / "Cafe Nord" / "RG-1002.xlsx"

    build_invoice_workbook(
        output_path=output_path,
        customer_name="Cafe Nord",
        document_number="RG-1002",
        line_items=[
            {"name": "Wasser", "quantity": 2, "unit_price_cents": 1299, "deposit_cents": 330},
            {"name": "Spezi", "quantity": 3, "unit_price_cents": 1599, "deposit_cents": 330},
        ],
    )

    workbook = load_workbook(output_path, data_only=False)
    sheet = workbook.active

    assert sheet["E13"].value == "=(C13+D13)*A13"
    assert sheet["E14"].value == "=(C14+D14)*A14"
    assert sheet["E30"].value == "=(C30+D30)*A30"
    assert sheet["F32"].value == "=SUM(E13:E30)"
    assert sheet["A32"].value == "=SUM(A13:A30)"
