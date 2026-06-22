from pathlib import Path

from openpyxl import load_workbook

from .file_service import ensure_parent_folder


TEMPLATE_PATH = Path(__file__).resolve().parents[3] / "templates" / "vorlage_liefern_bar.xlsx"
FIRST_ITEM_ROW = 13
MAX_ITEM_ROW = 30


def build_invoice_workbook(
    output_path: Path,
    customer_name: str,
    document_number: str,
    line_items: list[dict],
) -> None:
    _build_document_workbook(output_path, "Rechnung", customer_name, document_number, line_items)


def build_delivery_note_workbook(
    output_path: Path,
    customer_name: str,
    document_number: str,
    line_items: list[dict],
) -> None:
    _build_document_workbook(output_path, "Lieferauftrag", customer_name, document_number, line_items)


def _build_document_workbook(
    output_path: Path,
    document_title: str,
    customer_name: str,
    document_number: str,
    line_items: list[dict],
) -> None:
    ensure_parent_folder(output_path)

    workbook = load_workbook(TEMPLATE_PATH)
    workbook.calculation.calcMode = "auto"
    workbook.calculation.forceFullCalc = True
    workbook.calculation.fullCalcOnLoad = True
    workbook.calculation.calcOnSave = True
    sheet = workbook.active

    sheet["A8"] = document_title
    sheet["F8"] = document_number
    sheet["B10"] = customer_name

    if len(line_items) > MAX_ITEM_ROW - FIRST_ITEM_ROW + 1:
        raise ValueError("Die Winklmeier-Vorlage erlaubt maximal 18 Positionszeilen.")

    for row in range(FIRST_ITEM_ROW, MAX_ITEM_ROW + 1):
        sheet.cell(row=row, column=1, value=None)
        sheet.cell(row=row, column=2, value=None)
        sheet.cell(row=row, column=3, value=None)
        sheet.cell(row=row, column=4, value=None)
        sheet.cell(row=row, column=5, value=f"=(C{row}+D{row})*A{row}")

    for row, item in enumerate(line_items, start=6):
        target_row = FIRST_ITEM_ROW + row - 6
        quantity = item["quantity"]
        unit_price = item["unit_price_cents"] / 100
        deposit = item.get("deposit_cents", 0) / 100
        sheet.cell(row=target_row, column=1, value=quantity)
        sheet.cell(row=target_row, column=2, value=item["name"])
        sheet.cell(row=target_row, column=3, value=deposit)
        sheet.cell(row=target_row, column=4, value=unit_price)
        sheet.cell(row=target_row, column=5, value=f"=(C{target_row}+D{target_row})*A{target_row}")

    sheet["A32"] = f"=SUM(A{FIRST_ITEM_ROW}:A{MAX_ITEM_ROW})"
    sheet["F32"] = f"=SUM(E{FIRST_ITEM_ROW}:E{MAX_ITEM_ROW})"

    workbook.save(output_path)
