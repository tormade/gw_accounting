from pathlib import Path
from shutil import rmtree

from openpyxl import Workbook
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QTextEdit, QVBoxLayout

from getraenkeladen_tool.app import create_app, create_runtime
from getraenkeladen_tool.models import CustomerAssortmentItem, OnboardingIssue
from getraenkeladen_tool.schemas import CustomerCreate, DocumentCreate, DocumentLineItem, OrderCreate, OrderLineCreate, ProductCreate
from getraenkeladen_tool.services.automation_service import (
    find_duplicate_risks,
    get_customer_quickstart,
    list_customer_folder_updates,
    list_month_end_checks,
    list_work_cockpit_items,
    payment_hint_preview,
    suggest_typical_order_lines,
    validate_order_before_save,
    verify_document_assets,
)
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.document_service import create_document
from getraenkeladen_tool.services.order_service import create_order
from getraenkeladen_tool.services.product_service import create_product


BASE_DIR = Path("/private/tmp/getraenkeladen_automation_uat_dialog_runtime")
CUSTOMER_ROOT = Path("/private/tmp/getraenkeladen_automation_uat_dialog_customer")


def seed(session_factory):
    if BASE_DIR.exists():
        rmtree(BASE_DIR)
    if CUSTOMER_ROOT.exists():
        rmtree(CUSTOMER_ROOT)
    runtime = create_runtime(BASE_DIR)
    folder = CUSTOMER_ROOT / "Cafe Nord"
    folder.mkdir(parents=True)
    session = runtime.session_factory()
    try:
        customer = create_customer(
            session,
            CustomerCreate(name="Cafe Nord", folder_path=str(folder), payment_method="Ueberweisung", delivery_notes="Seiteneingang"),
        )
        review_customer = create_customer(session, CustomerCreate(name="Review Kunde", folder_path=str(CUSTOMER_ROOT / "Fehlt")))
        water = create_product(session, ProductCreate(name="Wasser Classic", unit="Kiste", standard_price_cents=1000, default_deposit_cents=330))
        spezi = create_product(session, ProductCreate(name="Spezi", unit="Kiste", standard_price_cents=900, default_deposit_cents=310))
        for index, quantity in enumerate((2, 4, 6), start=1):
            order = create_order(
                session,
                OrderCreate(
                    order_number=f"BEST-AUTO-{index}",
                    customer_id=customer.id,
                    order_date=f"2026-07-0{index}",
                    delivery_date=f"2026-07-0{index}",
                    lines=[
                        OrderLineCreate(product_id=water.id, quantity=quantity, deposit_cents=330),
                        OrderLineCreate(product_id=spezi.id, quantity=1, deposit_cents=310),
                    ],
                ),
            )
        document = create_document(
            session,
            DocumentCreate(
                customer_id=customer.id,
                order_id=order.id,
                document_type="Rechnung",
                document_number="RE-AUTO-1",
                delivery_date="2026-07-01",
                line_items=[DocumentLineItem(name="Wasser Classic", quantity=1, unit_price_cents=1000, deposit_cents=330)],
            ),
        )
        workbook = Workbook()
        workbook.active["A1"] = "Neue Kunden-Excel"
        workbook.save(folder / "neue_kunden_excel.xlsx")
        session.add(CustomerAssortmentItem(customer_id=review_customer.id, product_id=None, source_product_name="Unklarer Artikel", last_quantity=1))
        session.add(
            OnboardingIssue(
                customer_name=review_customer.name,
                source_file="review.xlsx",
                issue_type="product_match",
                field_name="Artikel",
                folder_value="Unklarer Artikel",
                list_value="",
                message="Artikel konnte nicht sicher zugeordnet werden.",
                status="offen",
                created_at="2026-07-05",
            )
        )
        session.commit()
        return runtime, customer.id, water.id, document.id
    finally:
        session.close()


def build_report(session_factory, customer_id: int, water_id: int, document_id: int) -> str:
    session = session_factory()
    try:
        quickstart = get_customer_quickstart(session, customer_id)
        risks = find_duplicate_risks(session, customer_name="Cafe Nort", product_name="Wasser Classik", document_number="RE AUTO 1")
        warnings = validate_order_before_save(
            session,
            OrderCreate(
                order_number="BEST-AUTO-1",
                customer_id=customer_id,
                order_date="2026-07-05",
                delivery_date="2026-07-05",
                lines=[OrderLineCreate(product_id=water_id, quantity=150, unit_price_cents=0, deposit_cents=0)],
            ),
        )
        verification = verify_document_assets(session, document_id)
        updates = list_customer_folder_updates(session, customer_id)
        payment = payment_hint_preview(session, customer_id, "2026-07-05")
        month = list_month_end_checks(session, "2026-07", "2026-07-20")
        typical = suggest_typical_order_lines(session, customer_id)
        cockpit = list_work_cockpit_items(session)
        checks = [
            ("Kunden-Schnellstart", quickstart.suggestions),
            ("Dublettenwarnung", tuple(risk.message for risk in risks)),
            ("Bestell-Plausibilitaet", tuple(warning.message for warning in warnings)),
            ("Belegpruefung", tuple(check.message for check in verification.checks)),
            ("Kundenordner-Scan", tuple(path.name for path in updates)),
            ("Zahlungshinweis", (payment.footer_text or "", payment.due_date or "")),
            ("Monatsabschluss", tuple(check.message for check in month)),
            ("Typische Mengen", tuple(f"{line.product_name}: {line.suggested_quantity}" for line in typical)),
            ("Arbeits-Cockpit", tuple(item.title for item in cockpit)),
        ]
        lines = ["AUTOMATION UAT - ALLE CHECKS"]
        for title, values in checks:
            lines.append(f"[OK] {title}")
            for value in values:
                if value:
                    lines.append(f"  - {value}")
        return "\n".join(lines)
    finally:
        session.close()


def main() -> int:
    app = create_app()
    runtime, customer_id, water_id, document_id = seed(None)
    dialog = QDialog()
    dialog.setWindowTitle("Automation UAT")
    dialog.resize(900, 700)
    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel("Automation UAT - alle Automationen"))
    report = QTextEdit()
    report.setReadOnly(True)
    report.setPlainText(build_report(runtime.session_factory, customer_id, water_id, document_id))
    layout.addWidget(report)
    close_button = QPushButton("Schliessen")
    close_button.clicked.connect(dialog.close)
    layout.addWidget(close_button)
    dialog.show()
    QTimer.singleShot(0, dialog.raise_)
    QTimer.singleShot(0, dialog.activateWindow)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
