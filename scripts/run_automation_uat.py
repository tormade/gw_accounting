from pathlib import Path
from shutil import rmtree

from openpyxl import Workbook

from PySide6.QtCore import QTimer

from getraenkeladen_tool.app import create_app, create_runtime
from getraenkeladen_tool.models import CustomerAssortmentItem, OnboardingIssue
from getraenkeladen_tool.schemas import CustomerCreate, DocumentCreate, DocumentLineItem, OrderCreate, OrderLineCreate, ProductCreate
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.document_service import create_document
from getraenkeladen_tool.services.order_service import create_order
from getraenkeladen_tool.services.product_service import create_product
from getraenkeladen_tool.ui.main_window import MainWindow, MAIN_TABS


BASE_DIR = Path("/private/tmp/getraenkeladen_automation_uat_runtime")
CUSTOMER_ROOT = Path("/private/tmp/getraenkeladen_automation_uat_customer")


def seed_uat_data(session_factory) -> None:
    if CUSTOMER_ROOT.exists():
        rmtree(CUSTOMER_ROOT)
    folder = CUSTOMER_ROOT / "Cafe Nord"
    folder.mkdir(parents=True)
    missing_folder = CUSTOMER_ROOT / "Fehlt"

    session = session_factory()
    try:
        customer = create_customer(
            session,
            CustomerCreate(
                name="Cafe Nord",
                folder_path=str(folder),
                payment_method="Ueberweisung",
                delivery_notes="Seiteneingang benutzen",
            ),
        )
        review_customer = create_customer(
            session,
            CustomerCreate(name="Review Kunde", folder_path=str(missing_folder)),
        )
        water = create_product(
            session,
            ProductCreate(name="Wasser Classic 12x0,7", unit="Kiste", standard_price_cents=1000, default_deposit_cents=330),
        )
        spezi = create_product(
            session,
            ProductCreate(name="Spezi 20x0,5", unit="Kiste", standard_price_cents=900, default_deposit_cents=310),
        )
        for index, water_quantity in enumerate((2, 4, 6), start=1):
            order = create_order(
                session,
                OrderCreate(
                    order_number=f"BEST-AUTO-{index}",
                    customer_id=customer.id,
                    order_date=f"2026-07-0{index}",
                    delivery_date=f"2026-07-0{index}",
                    lines=[
                        OrderLineCreate(product_id=water.id, quantity=water_quantity, deposit_cents=330),
                        OrderLineCreate(product_id=spezi.id, quantity=1, deposit_cents=310),
                    ],
                ),
            )
        create_document(
            session,
            DocumentCreate(
                customer_id=customer.id,
                order_id=order.id,
                document_type="Rechnung",
                document_number="RE-AUTO-1",
                delivery_date="2026-07-01",
                line_items=[DocumentLineItem(name="Wasser Classic 12x0,7", quantity=1, unit_price_cents=1000, deposit_cents=330)],
            ),
        )
        workbook = Workbook()
        workbook.active["A1"] = "Neue Kunden-Excel fuer UAT"
        workbook.save(folder / "neue_kunden_excel.xlsx")
        session.add(
            CustomerAssortmentItem(
                customer_id=review_customer.id,
                product_id=None,
                source_product_name="Unklarer Artikel",
                last_quantity=1,
            )
        )
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
    finally:
        session.close()


def main() -> int:
    if BASE_DIR.exists():
        rmtree(BASE_DIR)
    app = create_app()
    runtime = create_runtime(BASE_DIR)
    seed_uat_data(runtime.session_factory)
    window = MainWindow(session_factory=runtime.session_factory)
    window.navigation.setCurrentRow(MAIN_TABS.index("Kunden"))
    window.show()
    QTimer.singleShot(0, window.raise_)
    QTimer.singleShot(0, window.activateWindow)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
