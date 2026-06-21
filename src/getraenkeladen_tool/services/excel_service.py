from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from .file_service import ensure_parent_folder


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
    _build_document_workbook(output_path, "Lieferschein", customer_name, document_number, line_items)


def _build_document_workbook(
    output_path: Path,
    document_title: str,
    customer_name: str,
    document_number: str,
    line_items: list[dict],
) -> None:
    ensure_parent_folder(output_path)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = document_title

    sheet["A1"] = document_title
    sheet["A1"].font = Font(size=18, bold=True)
    sheet["A2"] = "Kunde"
    sheet["B2"] = customer_name
    sheet["A3"] = "Belegnummer"
    sheet["B3"] = document_number

    headers = ("Artikel", "Menge", "Einzelpreis", "Einzelpreis EUR", "Gesamt EUR")
    for column, label in enumerate(headers, start=1):
        cell = sheet.cell(row=5, column=column, value=label)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="111111")

    for row, item in enumerate(line_items, start=6):
        quantity = item["quantity"]
        unit_price_cents = item["unit_price_cents"]
        unit_price = unit_price_cents / 100
        sheet.cell(row=row, column=1, value=item["name"])
        sheet.cell(row=row, column=2, value=quantity)
        sheet.cell(row=row, column=3, value=unit_price_cents)
        sheet.cell(row=row, column=4, value=unit_price)
        sheet.cell(row=row, column=5, value=quantity * unit_price)

    sheet.column_dimensions["A"].width = 32
    sheet.column_dimensions["B"].width = 12
    sheet.column_dimensions["C"].width = 14
    sheet.column_dimensions["D"].width = 16
    sheet.column_dimensions["E"].width = 14

    workbook.save(output_path)
