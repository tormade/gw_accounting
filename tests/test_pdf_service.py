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
    assert "Summe 32.58 EUR" in pdf_text
    assert "Summe 19.29 EUR" in pdf_text
    assert "Gesamt: 51.87 EUR" in pdf_text


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
    assert "Gutschrift 4.80 EUR" in pdf_text
    assert "Gesamt: 10.30 EUR" in pdf_text
