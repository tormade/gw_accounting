from pathlib import Path

from getraenkeladen_tool.services.file_naming_service import _safe_filename_part, build_document_paths


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

    assert paths.excel_path.name == "2026-06-21_LS_42_Gasthof_Sued.xlsx"


def test_build_document_paths_does_not_duplicate_document_type_prefixes():
    invoice_paths = build_document_paths(
        customer_folder=Path("Kunden/Cafe Nord"),
        document_type="Rechnung",
        document_number="RE-FLOW-240624-1",
        customer_name="Cafe Nord",
        document_date="2026-06-24",
    )
    delivery_paths = build_document_paths(
        customer_folder=Path("Kunden/Cafe Nord"),
        document_type="Lieferschein",
        document_number="LS-FLOW-240624-1",
        customer_name="Cafe Nord",
        document_date="2026-06-24",
    )

    assert invoice_paths.excel_path.name == "2026-06-24_RE-FLOW-240624-1_Cafe_Nord.xlsx"
    assert delivery_paths.pdf_path.name == "2026-06-24_LS-FLOW-240624-1_Cafe_Nord.pdf"


def test_safe_filename_part_removes_windows_reserved_characters_and_names():
    assert _safe_filename_part('CON: Angebot* "Neu"? ') == "CON_Angebot_Neu"
    assert _safe_filename_part("Kunde. ") == "Kunde"
    assert _safe_filename_part("CON") == "CON_"
