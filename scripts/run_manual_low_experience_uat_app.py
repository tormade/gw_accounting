from pathlib import Path
from shutil import rmtree

from PySide6.QtCore import QTimer

from getraenkeladen_tool.app import create_app, create_runtime
from getraenkeladen_tool.models import CustomerAssortmentItem
from getraenkeladen_tool.schemas import CustomerCreate, ProductCreate
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.product_service import create_product
from getraenkeladen_tool.ui.main_window import MAIN_TABS, MainWindow

from run_low_experience_order_uat import PRODUCTS, prepare_source_workbook


BASE_DIR = Path("/private/tmp/getraenkeladen_manual_low_experience_uat_runtime")
CUSTOMER_ROOT = Path("/private/tmp/getraenkeladen_manual_low_experience_uat_customer")


def seed(runtime) -> None:
    if CUSTOMER_ROOT.exists():
        rmtree(CUSTOMER_ROOT)
    customer_dir = CUSTOMER_ROOT / "Cafe Seniorenfreundlich"
    source_workbook = customer_dir / "2026-06-01_RE_ALT_Cafe_Seniorenfreundlich.xlsx"
    prepare_source_workbook(source_workbook)
    session = runtime.session_factory()
    try:
        customer = create_customer(
            session,
            CustomerCreate(
                name="Cafe Seniorenfreundlich",
                folder_path=str(customer_dir),
                payment_method="Ueberweisung",
                delivery_notes="Seiteneingang, vormittags. Bitte einfache Bedienung.",
            ),
        )
        for sort_order, (name, price_cents, deposit_cents, last_quantity) in enumerate(PRODUCTS):
            product = create_product(
                session,
                ProductCreate(
                    name=name,
                    unit="Kiste",
                    standard_price_cents=price_cents,
                    default_deposit_cents=deposit_cents,
                ),
            )
            session.add(
                CustomerAssortmentItem(
                    customer_id=customer.id,
                    product_id=product.id,
                    source_product_name=name,
                    last_quantity=last_quantity,
                    last_unit_price_cents=price_cents,
                    last_deposit_cents=deposit_cents,
                    price_decision="zentraler_preis",
                    sort_order=sort_order,
                    source_file=str(source_workbook),
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
    seed(runtime)
    window = MainWindow(session_factory=runtime.session_factory)
    window.navigation.setCurrentRow(MAIN_TABS.index("Kunden"))
    window.show()
    window.raise_()
    window.activateWindow()
    QTimer.singleShot(0, window.raise_)
    QTimer.singleShot(0, window.activateWindow)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
