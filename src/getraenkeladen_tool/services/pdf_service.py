import json
from pathlib import Path

from .file_service import ensure_parent_folder


LETTERHEAD_PATH = Path(__file__).resolve().parents[3] / "templates" / "briefkopf.json"


def build_document_pdf(
    output_path: Path,
    document_title: str,
    customer_name: str,
    document_number: str,
    line_items: list[dict],
) -> None:
    ensure_parent_folder(output_path)
    letterhead = _load_letterhead()
    lines = [
        letterhead["sender"],
        letterhead["claim"],
        letterhead["phone"],
        "",
        document_title,
        f"Belegnummer: {document_number}",
        f"Kunde: {customer_name}",
        "",
        "Positionen:",
    ]
    document_total_cents = 0
    for item in line_items:
        unit_price = item["unit_price_cents"] / 100
        deposit = item.get("deposit_cents", 0) / 100
        line_total_cents = (item["unit_price_cents"] + item.get("deposit_cents", 0)) * item["quantity"]
        document_total_cents += line_total_cents
        lines.append(
            f"{item['quantity']} x {item['name']} | Preis {unit_price:.2f} EUR | "
            f"Pfand {deposit:.2f} EUR | Summe {line_total_cents / 100:.2f} EUR"
        )
    lines.extend(["", f"Gesamt: {document_total_cents / 100:.2f} EUR"])

    _write_simple_pdf(output_path, lines)


def _load_letterhead() -> dict[str, str]:
    return json.loads(LETTERHEAD_PATH.read_text(encoding="utf-8"))


def _write_simple_pdf(output_path: Path, lines: list[str]) -> None:
    content_lines = ["BT", "/F1 12 Tf", "72 760 Td"]
    for index, line in enumerate(lines):
        if index:
            content_lines.append("0 -18 Td")
        content_lines.append(f"({_escape_pdf_text(line)}) Tj")
    content_lines.append("ET")
    content = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_number, payload in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode("ascii"))
        pdf.extend(payload)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode(
            "ascii"
        )
    )
    output_path.write_bytes(pdf)


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
