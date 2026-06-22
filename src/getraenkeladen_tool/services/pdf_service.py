import json
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .file_service import ensure_parent_folder


LETTERHEAD_PATH = Path(__file__).resolve().parents[3] / "templates" / "briefkopf.json"
LOGO_PATH = Path(__file__).resolve().parents[3] / "assets" / "brand" / "logo_winklmeier.png"
BRAND_GREEN = colors.HexColor("#116149")
BRAND_RED = colors.HexColor("#c4312f")
SOFT_GREEN = colors.HexColor("#e8f3ee")
SOFT_BEIGE = colors.HexColor("#f4f1ea")
TEXT_DARK = colors.HexColor("#1f2a24")


def build_document_pdf(
    output_path: Path,
    document_title: str,
    customer_name: str,
    document_number: str,
    line_items: list[dict],
    deposit_returns: list[dict] | None = None,
    document_date: str | None = None,
    customer_address: str | None = None,
) -> None:
    ensure_parent_folder(output_path)
    letterhead = _load_letterhead()
    story = _build_story(
        letterhead=letterhead,
        document_title=document_title,
        customer_name=customer_name,
        customer_address=customer_address,
        document_number=document_number,
        line_items=line_items,
        deposit_returns=deposit_returns or [],
        document_date=document_date,
    )
    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=15 * mm,
        pageCompression=0,
        title=f"{document_title} {document_number}",
        author=letterhead["sender"],
    )
    document.build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)


def _build_story(
    letterhead: dict[str, str],
    document_title: str,
    customer_name: str,
    customer_address: str | None,
    document_number: str,
    line_items: list[dict],
    deposit_returns: list[dict],
    document_date: str | None,
) -> list:
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        "WinklmeierNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=TEXT_DARK,
    )
    muted = ParagraphStyle("WinklmeierMuted", parent=normal, textColor=colors.HexColor("#66736b"))
    title = ParagraphStyle(
        "WinklmeierTitle",
        parent=normal,
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=BRAND_GREEN,
    )

    story = []
    logo = Image(str(LOGO_PATH), width=58 * mm, height=25 * mm) if LOGO_PATH.exists() else Paragraph("Getraenke Winklmeier", title)
    header = Table(
        [
            [
                logo,
                Paragraph(
                    f"<b>{letterhead['sender']}</b><br/>{letterhead['claim']}<br/>{letterhead['phone']}",
                    normal,
                ),
            ]
        ],
        colWidths=[92 * mm, 67 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )
    story.extend([header, Spacer(1, 8 * mm)])

    recipient_lines = [customer_name]
    if customer_address:
        recipient_lines.extend(customer_address.splitlines())
    meta_table = Table(
        [
            [
                Paragraph("<b>Empfaenger</b><br/>" + "<br/>".join(recipient_lines), normal),
                Paragraph(
                    f"<b>{_display_title(document_title)}</b><br/>"
                    f"Belegnummer: {document_number}<br/>"
                    f"Datum: {_display_date(document_date)}",
                    normal,
                ),
            ]
        ],
        colWidths=[92 * mm, 67 * mm],
    )
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SOFT_BEIGE),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#e1ddd3")),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e1ddd3")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.extend([meta_table, Spacer(1, 8 * mm), Paragraph(_display_title(document_title).upper(), title), Spacer(1, 5 * mm)])

    rows, gross_total_cents = _line_rows(line_items, deposit_returns)
    table = Table(rows, colWidths=[18 * mm, 72 * mm, 24 * mm, 24 * mm, 25 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_GREEN),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d8d6cf")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfaf6")]),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([table, Spacer(1, 7 * mm)])

    net_cents = round(gross_total_cents / 1.19)
    tax_cents = gross_total_cents - net_cents
    totals = Table(
        [
            ["Netto", _format_euro(net_cents)],
            ["MwSt. 19%", _format_euro(tax_cents)],
            ["Gesamtbetrag", _format_euro(gross_total_cents)],
        ],
        colWidths=[38 * mm, 32 * mm],
        hAlign="RIGHT",
    )
    totals.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SOFT_GREEN),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#cfe3d9")),
                ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 2), (-1, 2), BRAND_GREEN),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend([totals, Spacer(1, 7 * mm)])
    story.append(Paragraph("Vielen Dank fuer Ihren Auftrag.", muted))
    return story


def _line_rows(line_items: list[dict], deposit_returns: list[dict]) -> tuple[list[list[str]], int]:
    rows = [["Menge", "Artikel", "Preis", "Pfand", "Summe"]]
    total_cents = 0
    for item in line_items:
        deposit_cents = item.get("deposit_cents", 0)
        line_total = (item["unit_price_cents"] + deposit_cents) * item["quantity"]
        total_cents += line_total
        rows.append(
            [
                str(item["quantity"]),
                item["name"],
                _format_euro(item["unit_price_cents"]),
                _format_euro(deposit_cents),
                _format_euro(line_total),
            ]
        )
    if deposit_returns:
        rows.append(["", "Pfandrueckgabe:", "", "", ""])
        for deposit_return in deposit_returns:
            line_total = -deposit_return["deposit_cents"] * deposit_return["quantity"]
            total_cents += line_total
            rows.append(
                [
                    str(deposit_return["quantity"]),
                    deposit_return["name"],
                    "",
                    _format_euro(-deposit_return["deposit_cents"]),
                    _format_euro(line_total),
                ]
            )
    return rows, total_cents


def _draw_footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(BRAND_RED)
    canvas.setLineWidth(1.2)
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFillColor(colors.HexColor("#66736b"))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(18 * mm, 9 * mm, "Getraenke Winklmeier - automatisch erzeugter Beleg")
    canvas.drawRightString(192 * mm, 9 * mm, f"Seite {document.page}")
    canvas.restoreState()


def _load_letterhead() -> dict[str, str]:
    return json.loads(LETTERHEAD_PATH.read_text(encoding="utf-8"))


def _display_title(document_title: str) -> str:
    return "Lieferschein" if document_title == "Lieferauftrag" else document_title


def _display_date(document_date: str | None) -> str:
    if document_date:
        try:
            return datetime.strptime(document_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        except ValueError:
            return document_date
    return datetime.today().strftime("%d.%m.%Y")


def _format_euro(cents: int) -> str:
    return f"{cents / 100:.2f} EUR".replace(".", ",")
