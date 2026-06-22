from pathlib import Path

from getraenkeladen_tool.services.file_naming_service import build_document_paths


def test_build_document_paths_uses_concept_file_schema():
    paths = build_document_paths(
        customer_folder=Path("Kunden/Cafe Nord"),
        document_type="Rechnung",
        document_number="RG/1001",
        customer_name="Cafe Nord GmbH",
        document_date="2026-06-21",
    )

    assert paths.excel_path == Path("Kunden/Cafe Nord/2026-06-21_RE_RG-1001_Cafe_Nord_GmbH.xlsx")
    assert paths.pdf_path == Path("Kunden/Cafe Nord/2026-06-21_RE_RG-1001_Cafe_Nord_GmbH.pdf")


def test_build_document_paths_uses_delivery_order_ls_prefix():
    paths = build_document_paths(
        customer_folder=Path("Kunden/Gasthof Sued"),
        document_type="Lieferauftrag",
        document_number="LS 42",
        customer_name="Gasthof Sued",
        document_date="2026-06-21",
    )

    assert paths.excel_path.name == "2026-06-21_LS_LS_42_Gasthof_Sued.xlsx"
