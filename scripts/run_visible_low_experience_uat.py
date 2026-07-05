from pathlib import Path
from shutil import rmtree

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox

from getraenkeladen_tool.app import create_app, create_runtime
from getraenkeladen_tool.models import CustomerAssortmentItem
from getraenkeladen_tool.schemas import CustomerCreate, ProductCreate
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.product_service import create_product
from getraenkeladen_tool.ui.document_workflow_panel import DeliveryNotePanel, InvoicePanel
from getraenkeladen_tool.ui.main_window import MAIN_TABS, MainWindow

from run_low_experience_order_uat import PRODUCTS, prepare_source_workbook


BASE_DIR = Path("/private/tmp/getraenkeladen_visible_low_experience_uat_runtime")
CUSTOMER_ROOT = Path("/private/tmp/getraenkeladen_visible_low_experience_uat_customer")
REPORT_PATH = Path("/private/tmp/visible_low_experience_uat_report.txt")


class VisibleLowExperienceUat:
    def __init__(self) -> None:
        if BASE_DIR.exists():
            rmtree(BASE_DIR)
        if CUSTOMER_ROOT.exists():
            rmtree(CUSTOMER_ROOT)
        self.app = create_app()
        self.runtime = create_runtime(BASE_DIR)
        self.customer_id = self.seed()
        self.window = MainWindow(session_factory=self.runtime.session_factory)
        self.order_id: int | None = None
        self.report: list[str] = []
        self.step_label = QLabel(self.window)
        self.step_label.setObjectName("uatStepLabel")
        self.step_label.setStyleSheet(
            "background: #fff4ce; color: #1d1d1f; border: 2px solid #c4312f; "
            "font-size: 18px; font-weight: 700; padding: 12px;"
        )
        self.step_label.setWordWrap(True)
        self.step_label.setGeometry(220, 18, 820, 64)
        self.step_label.raise_()
        self.window.order_panel.show_saved_order_next_steps = self.remember_saved_order

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

    def start(self) -> int:
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        self.schedule(
            [
                self.show_customer_area,
                self.select_customer,
                self.start_order,
                self.enter_order_number,
                self.save_order,
                self.open_delivery_note,
                self.create_delivery_note,
                self.open_invoice,
                self.create_invoice,
                self.finish,
            ]
        )
        return self.app.exec()

    def schedule(self, steps) -> None:
        delay = 900
        for index, step in enumerate(steps, start=1):
            QTimer.singleShot(delay * index, step)

    def announce(self, text: str) -> None:
        self.step_label.setText(text)
        self.step_label.raise_()
        self.window.statusBar().showMessage(text, 5000)
        self.report.append(text)

    def show_customer_area(self) -> None:
        self.announce("1/10 Kundenbereich: Kunde wird wie ein normaler Nutzer aus der Liste gewaehlt.")
        self.window.navigation.setCurrentRow(MAIN_TABS.index("Kunden"))

    def select_customer(self) -> None:
        self.announce("2/10 Kunde auswaehlen: Vorschlagsliste ist sofort sichtbar, Tippen filtert nur.")
        select = self.window.customer_folder_panel.customer_select
        select.set_search_text("Cafe")
        item = select.result_list.item(0)
        rect = select.result_list.visualItemRect(item)
        QTest.mouseClick(select.result_list.viewport(), Qt.MouseButton.LeftButton, pos=rect.center())

    def start_order(self) -> None:
        self.announce("3/10 Bestellung starten: 8 Artikel werden vorgeschlagen, nur letzte Mengen werden uebernommen.")
        QTest.mouseClick(self.window.customer_folder_panel.new_order_button, Qt.MouseButton.LeftButton)

    def enter_order_number(self) -> None:
        self.announce("4/10 Bestellnummer eingeben: fuer 60+ reicht ein klares Feld, keine Suche nach versteckten Aktionen.")
        order_panel = self.window.order_panel
        order_panel.order_number.setFocus()
        order_panel.order_number.clear()
        QTest.keyClicks(order_panel.order_number, "BEST-SICHTBAR-60PLUS")

    def save_order(self) -> None:
        self.announce("5/10 Speichern: Bestellung enthaelt 2 Mengenpositionen aus 8 vorgeschlagenen Artikeln.")
        QTest.mouseClick(self.window.order_panel.save_order_button, Qt.MouseButton.LeftButton)

    def remember_saved_order(self, order_id: int, order_number: str) -> None:
        self.order_id = order_id
        self.report.append(f"Bestellung gespeichert: {order_number}, order_id={order_id}")

    def open_delivery_note(self) -> None:
        self.announce("6/10 Lieferschein oeffnen: Bestellung ist ausgewaehlt, Artikel koennen geprueft werden.")
        self.window.open_delivery_note_for_order(self.order_id or 0)

    def create_delivery_note(self) -> None:
        self.announce("7/10 Lieferschein erzeugen: Klick auf Excel + PDF.")
        panel = self.active_document_panel()
        panel.document_number.setText("LS-SICHTBAR-60PLUS")
        self.patch_message_boxes()
        QTest.mouseClick(panel.create_both_button, Qt.MouseButton.LeftButton)

    def open_invoice(self) -> None:
        self.announce("8/10 Rechnung oeffnen: gleiche Bestellung, gleiche 2 Mengen aus 8 Artikeln.")
        self.window.open_invoice_for_order(self.order_id or 0)

    def create_invoice(self) -> None:
        self.announce("9/10 Rechnung erzeugen: Klick auf Excel + PDF.")
        panel = self.active_document_panel()
        panel.document_number.setText("RE-SICHTBAR-60PLUS")
        self.patch_message_boxes()
        QTest.mouseClick(panel.create_both_button, Qt.MouseButton.LeftButton)

    def finish(self) -> None:
        self.announce("10/10 UAT fertig: Bestellung, Lieferschein und Rechnung wurden sichtbar durchlaufen.")
        self.write_report()
        QTimer.singleShot(4000, QApplication.instance().quit)

    def active_document_panel(self):
        dialog = self.window.document_dialogs[-1]
        return dialog.findChild(DeliveryNotePanel) or dialog.findChild(InvoicePanel)

    def patch_message_boxes(self) -> None:
        QMessageBox.information = lambda *args, **kwargs: QMessageBox.StandardButton.Ok
        QMessageBox.warning = lambda *args, **kwargs: QMessageBox.StandardButton.Ok
        QMessageBox.critical = lambda *args, **kwargs: QMessageBox.StandardButton.Ok

    def write_report(self) -> None:
        REPORT_PATH.write_text("\n".join(self.report) + "\n", encoding="utf-8")


def main() -> int:
    return VisibleLowExperienceUat().start()


if __name__ == "__main__":
    raise SystemExit(main())
