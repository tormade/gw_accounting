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
