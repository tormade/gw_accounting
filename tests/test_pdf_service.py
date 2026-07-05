from pathlib import Path

from getraenkeladen_tool.services.pdf_service import build_document_pdf


def test_build_document_pdf_uses_letterhead_config(tmp_path: Path):
    output_path = tmp_path / "RG-1001.pdf"

    build_document_pdf(
        output_path=output_path,
        document_title="Rechnung",
        customer_name="Cafe Nord",
        document_number="RG-1001",
        line_items=[{"name": "Wasser", "quantity": 1, "unit_price_cents": 1299}],
    )

    pdf_bytes = output_path.read_bytes()
    assert pdf_bytes.startswith(b"%PDF-")
    assert b"Getraenke Winklmeier" in pdf_bytes
    assert b"Wir bringen" in pdf_bytes
    assert b"/Image" in pdf_bytes
    assert b"RECHNUNG" in pdf_bytes


def test_build_document_pdf_includes_line_and_document_totals(tmp_path: Path):
    output_path = tmp_path / "RG-1002.pdf"

    build_document_pdf(
        output_path=output_path,
        document_title="Rechnung",
        customer_name="Cafe Nord",
        document_number="RG-1002",
        line_items=[
            {"name": "Wasser", "quantity": 2, "unit_price_cents": 1299, "deposit_cents": 330},
            {"name": "Spezi", "quantity": 1, "unit_price_cents": 1599, "deposit_cents": 330},
        ],
    )

    pdf_text = output_path.read_bytes().decode("latin-1")
    assert "32,58 EUR" in pdf_text
    assert "19,29 EUR" in pdf_text
    assert "51,87 EUR" in pdf_text
    assert "Gesamtbetrag" in pdf_text


def test_build_document_pdf_keeps_zero_quantity_lines_without_zero_amount(tmp_path: Path):
    output_path = tmp_path / "RG-NULL.pdf"

    build_document_pdf(
        output_path=output_path,
        document_title="Rechnung",
        customer_name="Cafe Nord",
        document_number="RG-NULL",
        line_items=[
            {"name": "Wasser", "quantity": 0, "unit_price_cents": 1299, "deposit_cents": 330},
            {"name": "Spezi", "quantity": 2, "unit_price_cents": 1599, "deposit_cents": 310},
        ],
    )

    pdf_text = output_path.read_bytes().decode("latin-1")
    assert "Wasser" in pdf_text
    assert "Spezi" in pdf_text
    assert "0,00 EUR" not in pdf_text
    assert "38,18 EUR" in pdf_text


def test_build_document_pdf_reduces_total_by_deposit_returns(tmp_path: Path):
    output_path = tmp_path / "RG-1003.pdf"

    build_document_pdf(
        output_path=output_path,
        document_title="Rechnung",
        customer_name="Cafe Nord",
        document_number="RG-1003",
        line_items=[{"name": "Wasser", "quantity": 1, "unit_price_cents": 1030, "deposit_cents": 480}],
        deposit_returns=[{"name": "Leergut Kiste 4,80", "quantity": 1, "deposit_cents": 480}],
    )

    pdf_text = output_path.read_bytes().decode("latin-1")
    assert "Pfandrueckgabe:" in pdf_text
    assert "-4,80 EUR" in pdf_text
    assert "10,30 EUR" in pdf_text


def test_build_document_pdf_includes_delivery_fee_note_and_footer_text(tmp_path: Path):
    output_path = tmp_path / "RG-1005.pdf"

    build_document_pdf(
        output_path=output_path,
        document_title="Rechnung",
        customer_name="Metzgerei Karl",
        document_number="RG-1005",
        line_items=[{"name": "Frucade Colamix 20x0,5", "quantity": 3, "unit_price_cents": 1048, "deposit_cents": 310}],
        delivery_fee_enabled=True,
        note_text="bis13Uhr und ab 15 Uhr",
        footer_text="Rechnungsbetrag wird per Sepa Basis Lastschrift Mandat eingezogen.",
    )

    pdf_text = output_path.read_bytes().decode("latin-1")
    assert "Lieferpauschale" in pdf_text
    assert "entf. ab 6 Traeger" not in pdf_text
    assert "3,90 EUR" in pdf_text
    assert "44,64 EUR" in pdf_text
    assert "bis13Uhr und ab 15 Uhr" in pdf_text
    assert "Rechnungsbetrag wird per Sepa Basis Lastschrift Mandat eingezogen." in pdf_text


def test_build_document_pdf_includes_customer_document_date_and_table_headers(tmp_path: Path):
    output_path = tmp_path / "RG-1004.pdf"

    build_document_pdf(
        output_path=output_path,
        document_title="Rechnung",
        customer_name="Cafe Nord",
        document_number="RG-1004",
        line_items=[{"name": "Wasser", "quantity": 1, "unit_price_cents": 1299, "deposit_cents": 330}],
        document_date="2026-06-21",
        customer_address="Hauptstrasse 1",
    )

    pdf_text = output_path.read_bytes().decode("latin-1")
    assert "Cafe Nord" in pdf_text
    assert "Hauptstrasse 1" in pdf_text
    assert "21.06.2026" in pdf_text
    assert "Menge" in pdf_text
    assert "Artikel" in pdf_text
    assert "Pfand" in pdf_text
