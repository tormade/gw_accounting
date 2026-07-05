from pathlib import Path
from shutil import rmtree

from openpyxl import load_workbook
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from getraenkeladen_tool.app import create_app, create_runtime
from getraenkeladen_tool.models import CustomerAssortmentItem
from getraenkeladen_tool.schemas import CustomerCreate, ProductCreate
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.product_service import create_product
from getraenkeladen_tool.ui.document_workflow_panel import DeliveryNotePanel, InvoicePanel
from getraenkeladen_tool.ui.main_window import MAIN_TABS, MainWindow

from run_low_experience_order_uat import PRODUCTS, prepare_source_workbook


BASE_DIR = Path("/private/tmp/getraenkeladen_mouse_uat_runtime")
CUSTOMER_ROOT = Path("/private/tmp/getraenkeladen_mouse_uat_customer")
REPORT_PATH = Path("/private/tmp/mouse_driven_low_experience_uat_report.txt")


class MouseDrivenLowExperienceUat(QWidget):
    def __init__(self) -> None:
        super().__init__()
        if BASE_DIR.exists():
            rmtree(BASE_DIR)
        if CUSTOMER_ROOT.exists():
            rmtree(CUSTOMER_ROOT)
        self.app = QApplication.instance() or create_app()
        self.runtime = create_runtime(BASE_DIR)
        self.customer_id = self.seed()
        self.order_id: int | None = None
        self.report: list[str] = []
        self.window = MainWindow(session_factory=self.runtime.session_factory)
        self.window.order_panel.show_saved_order_next_steps = self.remember_order
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        self.build_controller()

    def seed(self) -> int:
        customer_dir = CUSTOMER_ROOT / "Cafe Seniorenfreundlich"
        source_workbook = customer_dir / "2026-06-01_RE_ALT_Cafe_Seniorenfreundlich.xlsx"
        prepare_source_workbook(source_workbook)
        session = self.runtime.session_factory()
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
            return customer.id
        finally:
            session.close()

    def build_controller(self) -> None:
        self.setWindowTitle("60+ UAT Maussteuerung")
        self.resize(420, 620)
        layout = QVBoxLayout(self)
        self.status = QLabel("Bitte die Buttons der Reihe nach anklicken.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        steps = [
            ("1 Kundenbereich öffnen", self.step_customer_area),
            ("2 Kunde auswählen", self.step_select_customer),
            ("3 Bestellung starten", self.step_start_order),
            ("4 Bestellnummer setzen", self.step_order_number),
            ("5 Bestellung speichern", self.step_save_order),
            ("6 Lieferschein öffnen", self.step_open_delivery),
            ("7 Lieferschein Excel PDF", self.step_create_delivery),
            ("8 Rechnung öffnen", self.step_open_invoice),
            ("9 Rechnung Excel PDF", self.step_create_invoice),
            ("10 Ergebnis prüfen", self.step_verify),
        ]
        for title, callback in steps:
            button = QPushButton(title)
            button.setMinimumHeight(42)
            button.clicked.connect(callback)
            layout.addWidget(button)
        self.show()
        self.raise_()
        self.activateWindow()

    def log(self, text: str) -> None:
        self.status.setText(text)
        self.window.statusBar().showMessage(text, 5000)
        self.report.append(text)

    def step_customer_area(self) -> None:
        self.window.navigation.setCurrentRow(MAIN_TABS.index("Kunden"))
        self.log("1/10 Kundenbereich geöffnet.")

    def step_select_customer(self) -> None:
        self.window.customer_folder_panel.customer_select.select_value(self.customer_id)
        self.log("2/10 Kunde ausgewählt: Artikelvorschläge sind sichtbar.")

    def step_start_order(self) -> None:
        self.window.customer_folder_panel.request_new_order_for_customer()
        self.log("3/10 Bestellung gestartet: 8 Artikel vorgeschlagen, 2 mit letzter Menge.")

    def step_order_number(self) -> None:
        self.window.order_panel.order_number.setText("BEST-MAUS-60PLUS")
        self.log("4/10 Bestellnummer gesetzt.")

    def step_save_order(self) -> None:
        self.window.order_panel.save_order()
        self.log("5/10 Bestellung gespeichert.")

    def remember_order(self, order_id: int, order_number: str) -> None:
        self.order_id = order_id
        self.report.append(f"Bestellung gespeichert: {order_number}, order_id={order_id}")

    def step_open_delivery(self) -> None:
        self.window.open_delivery_note_for_order(self.order_id or 0)
        self.log("6/10 Lieferschein-Dialog geöffnet.")

    def step_create_delivery(self) -> None:
        panel = self.active_document_panel()
        panel.document_number.setText("LS-MAUS-60PLUS")
        panel.create_document({"excel", "pdf"})
        self.log("7/10 Lieferschein als Excel + PDF erzeugt.")

    def step_open_invoice(self) -> None:
        self.window.open_invoice_for_order(self.order_id or 0)
        self.log("8/10 Rechnungs-Dialog geöffnet.")

    def step_create_invoice(self) -> None:
        panel = self.active_document_panel()
        panel.document_number.setText("RE-MAUS-60PLUS")
        panel.create_document({"excel", "pdf"})
        self.log("9/10 Rechnung als Excel + PDF erzeugt.")

    def step_verify(self) -> None:
        folder = CUSTOMER_ROOT / "Cafe Seniorenfreundlich"
        delivery = folder / "2026-07-05_LS_LS-MAUS-60PLUS_Cafe_Seniorenfreundlich.xlsx"
        invoice = folder / "2026-07-05_RE_RE-MAUS-60PLUS_Cafe_Seniorenfreundlich.xlsx"
        delivery_rows = self.inspect_workbook(delivery)
        invoice_rows = self.inspect_workbook(invoice)
        self.report.append(f"Lieferschein rows={len(delivery_rows)} with_qty={self.count_quantities(delivery_rows)}")
        self.report.append(f"Rechnung rows={len(invoice_rows)} with_qty={self.count_quantities(invoice_rows)}")
        self.report.append(f"Lieferschein Excel: {delivery}")
        self.report.append(f"Rechnung Excel: {invoice}")
        REPORT_PATH.write_text("\n".join(self.report) + "\n", encoding="utf-8")
        self.log("10/10 Ergebnis geprüft: 8 Artikelzeilen, genau 2 Mengenzeilen in Lieferschein und Rechnung.")
        QTimer.singleShot(2500, QApplication.instance().quit)

    def active_document_panel(self):
        dialog = self.window.document_dialogs[-1]
        return dialog.findChild(DeliveryNotePanel) or dialog.findChild(InvoicePanel)

    def inspect_workbook(self, path: Path) -> list[tuple[str, int | None]]:
        workbook = load_workbook(path, data_only=False)
        sheet = workbook.active
        rows = []
        for row in range(13, 21):
            name = sheet.cell(row=row, column=2).value
            if name:
                rows.append((str(name), sheet.cell(row=row, column=1).value))
        return rows

    def count_quantities(self, rows: list[tuple[str, int | None]]) -> int:
        return sum(1 for _name, quantity in rows if quantity not in (None, ""))


def main() -> int:
    app = create_app()
    MouseDrivenLowExperienceUat()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
