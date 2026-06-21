from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..schemas import DocumentCreate, DocumentLineItem, OrderCreate, OrderLineCreate
from ..services.customer_service import list_customers
from ..services.document_service import create_document
from ..services.excel_service import build_delivery_note_workbook, build_invoice_workbook
from ..services.file_naming_service import build_document_paths
from ..services.order_service import create_order, create_order_documents
from ..services.pdf_service import build_document_pdf
from ..services.product_service import list_active_products


DOCUMENT_FORM_ACTIONS = {
    "sampleDocumentButton": "Beispiel laden",
    "chooseCustomerFolderButton": "Ordner waehlen",
    "refreshMasterDataButton": "Stammdaten laden",
    "addLineItemButton": "Position hinzufuegen",
    "removeLineItemButton": "Position entfernen",
    "saveOrderButton": "Auftrag speichern",
    "createOrderDocumentsButton": "Lieferschein und Rechnung aus Auftrag",
    "createDocumentButton": "Excel und PDF erstellen",
}

LINE_ITEM_COLUMNS = ("Produkt", "Menge", "Preis EUR", "Pfand EUR")


class DocumentPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.customers_by_id = {}
        self.products_by_id = {}

        self.document_type = QComboBox()
        self.document_type.addItems(["Rechnung", "Lieferschein"])
        self.customer_select = QComboBox()
        self.customer_select.addItem("Manuelle Eingabe", None)
        self.product_select = QComboBox()
        self.product_select.addItem("Manuelle Eingabe", None)
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("z. B. Cafe Nord")
        self.customer_folder = QLineEdit()
        self.customer_folder.setPlaceholderText("Kundenordner auswaehlen oder eintragen")
        self.document_number = QLineEdit()
        self.document_number.setPlaceholderText("z. B. RG-1001")
        self.order_number = QLineEdit()
        self.order_number.setPlaceholderText("z. B. AUF-1001")
        self.delivery_note_number = QLineEdit()
        self.delivery_note_number.setPlaceholderText("z. B. LS-1001")
        self.invoice_number = QLineEdit()
        self.invoice_number.setPlaceholderText("z. B. RG-1001")
        self.delivery_date = QLineEdit()
        self.delivery_date.setPlaceholderText("YYYY-MM-DD")
        self.delivery_slot = QComboBox()
        self.delivery_slot.addItems(["", "vormittag", "nachmittag", "ganztags"])
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("z. B. Wasser 0,7")
        self.quantity = QSpinBox()
        self.quantity.setRange(1, 999)
        self.unit_price_eur = QLineEdit()
        self.unit_price_eur.setPlaceholderText("z. B. 12,99")
        self.deposit_eur = QLineEdit()
        self.deposit_eur.setPlaceholderText("z. B. 3,30")
        self.line_items_table = QTableWidget(0, len(LINE_ITEM_COLUMNS))
        self.line_items_table.setHorizontalHeaderLabels(LINE_ITEM_COLUMNS)
        self.status_label = QLabel("Noch kein Beleg erzeugt.")
        self.status_label.setObjectName("muted")
        self.current_order_id = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        headline = QLabel("Direktbelege")
        headline.setObjectName("headline")
        layout.addWidget(headline)

        muted = QLabel("Sonderweg fuer einzelne Rechnung oder einzelnen Lieferschein ohne gespeicherten Auftrag")
        muted.setObjectName("muted")
        layout.addWidget(muted)

        form = QFormLayout()
        form.addRow("Belegtyp", self.document_type)
        form.addRow("Kunde aus Stammdaten", self.customer_select)
        form.addRow("Kunde", self.customer_name)
        form.addRow("Kundenordner", self._folder_row())
        form.addRow("Belegnummer", self.document_number)
        form.addRow("Auftragsnummer", self.order_number)
        form.addRow("Lieferscheinnummer", self.delivery_note_number)
        form.addRow("Rechnungsnummer", self.invoice_number)
        form.addRow("Lieferdatum", self.delivery_date)
        form.addRow("Zeitfenster", self.delivery_slot)
        form.addRow("Produkt aus Preisliste", self.product_select)
        form.addRow("Produkt", self.product_name)
        form.addRow("Menge", self.quantity)
        form.addRow("Preis EUR", self.unit_price_eur)
        form.addRow("Pfand EUR", self.deposit_eur)
        layout.addLayout(form)
        layout.addWidget(self.line_items_table)

        action_row = QHBoxLayout()
        self.sample_button = self._button("sampleDocumentButton")
        self.refresh_master_data_button = self._button("refreshMasterDataButton")
        self.add_line_item_button = self._button("addLineItemButton")
        self.remove_line_item_button = self._button("removeLineItemButton")
        self.save_order_button = self._button("saveOrderButton")
        self.create_order_documents_button = self._button("createOrderDocumentsButton")
        self.create_button = self._button("createDocumentButton")
        action_row.addWidget(self.sample_button)
        action_row.addWidget(self.refresh_master_data_button)
        action_row.addWidget(self.add_line_item_button)
        action_row.addWidget(self.remove_line_item_button)
        action_row.addWidget(self.save_order_button)
        action_row.addWidget(self.create_order_documents_button)
        action_row.addWidget(self.create_button)
        action_row.addStretch()
        layout.addLayout(action_row)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.sample_button.clicked.connect(self.load_sample)
        self.refresh_master_data_button.clicked.connect(self.refresh_master_data)
        self.add_line_item_button.clicked.connect(self.add_line_item)
        self.remove_line_item_button.clicked.connect(self.remove_selected_line_item)
        self.save_order_button.clicked.connect(self.save_order)
        self.create_order_documents_button.clicked.connect(self.create_documents_from_order)
        self.create_button.clicked.connect(self.create_excel)
        self.customer_select.currentIndexChanged.connect(self.apply_selected_customer)
        self.product_select.currentIndexChanged.connect(self.apply_selected_product)

    def _folder_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.customer_folder)
        self.choose_folder_button = self._button("chooseCustomerFolderButton")
        layout.addWidget(self.choose_folder_button)
        self.choose_folder_button.clicked.connect(self.choose_folder)
        return row

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(DOCUMENT_FORM_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Kundenordner waehlen")
        if folder:
            self.customer_folder.setText(folder)

    def load_sample(self) -> None:
        sample_folder = Path.cwd() / "outputs" / "Cafe Nord"
        self.document_type.setCurrentText("Rechnung")
        self.customer_name.setText("Cafe Nord")
        self.customer_folder.setText(str(sample_folder))
        self.document_number.setText("RG-1001")
        self.order_number.setText("AUF-1001")
        self.delivery_note_number.setText("LS-1001")
        self.invoice_number.setText("RG-1001")
        self.delivery_date.setText("2026-06-21")
        self.delivery_slot.setCurrentText("vormittag")
        self.product_name.setText("Wasser 0,7")
        self.quantity.setValue(10)
        self.unit_price_eur.setText("12,99")
        self.deposit_eur.setText("3,30")
        self.add_line_item()
        self.status_label.setText("Beispiel geladen. Jetzt kann die Excel-Datei erzeugt werden.")

    def refresh_master_data(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung fuer Stammdaten vorhanden.")
            return

        session = self.session_factory()
        try:
            customers = list_customers(session)
            products = list_active_products(session)
        finally:
            session.close()

        self.customer_select.blockSignals(True)
        self.product_select.blockSignals(True)
        self.customer_select.clear()
        self.product_select.clear()
        self.customer_select.addItem("Manuelle Eingabe", None)
        self.product_select.addItem("Manuelle Eingabe", None)
        self.customers_by_id = {customer.id: customer for customer in customers}
        self.products_by_id = {product.id: product for product in products}
        for customer in customers:
            self.customer_select.addItem(customer.name, customer.id)
        for product in products:
            self.product_select.addItem(product.name, product.id)
        self.customer_select.blockSignals(False)
        self.product_select.blockSignals(False)
        self.status_label.setText(f"{len(customers)} Kunden und {len(products)} Produkte geladen.")

    def apply_selected_customer(self) -> None:
        customer_id = self.customer_select.currentData()
        if customer_id is None:
            return
        customer = self.customers_by_id.get(customer_id)
        if customer is None:
            return
        self.customer_name.setText(customer.name)
        self.customer_folder.setText(customer.folder_path)

    def apply_selected_product(self) -> None:
        product_id = self.product_select.currentData()
        if product_id is None:
            return
        product = self.products_by_id.get(product_id)
        if product is None:
            return
        self.product_name.setText(product.name)
        self.unit_price_eur.setText(f"{product.standard_price_cents / 100:.2f}".replace(".", ","))

    def add_line_item(self) -> None:
        row = self.line_items_table.rowCount()
        self.line_items_table.insertRow(row)
        values = (
            self.product_name.text().strip(),
            str(self.quantity.value()),
            self.unit_price_eur.text().strip(),
            self.deposit_eur.text().strip() or "0,00",
        )
        for column, value in enumerate(values):
            self.line_items_table.setItem(row, column, QTableWidgetItem(value))

    def remove_selected_line_item(self) -> None:
        row = self.line_items_table.currentRow()
        if row >= 0:
            self.line_items_table.removeRow(row)

    def create_excel(self) -> None:
        line_items = self._line_items_from_table()
        if not line_items:
            self.add_line_item()
            line_items = self._line_items_from_table()

        customer_id = self.customer_select.currentData()
        if self.session_factory is not None and customer_id is not None:
            session = self.session_factory()
            try:
                document = create_document(
                    session,
                    DocumentCreate(
                        customer_id=customer_id,
                        document_type=self.document_type.currentText(),
                        document_number=self.document_number.text().strip(),
                        delivery_date=self.delivery_date.text().strip() or None,
                        delivery_slot=self.delivery_slot.currentText() or None,
                        line_items=[
                            DocumentLineItem(
                                name=item["name"],
                                quantity=item["quantity"],
                                unit_price_cents=item["unit_price_cents"],
                                deposit_cents=item["deposit_cents"],
                            )
                            for item in line_items
                        ],
                    ),
                    datev_upload_dir=Path.cwd() / "outputs" / "datev_upload",
                )
                self.status_label.setText(f"Excel und PDF erstellt: {document.excel_path}")
            finally:
                session.close()
            return

        output_path = self._output_path()
        if self.document_type.currentText() == "Rechnung":
            build_invoice_workbook(output_path, self.customer_name.text().strip(), self.document_number.text().strip(), line_items)
        else:
            build_delivery_note_workbook(output_path, self.customer_name.text().strip(), self.document_number.text().strip(), line_items)
        pdf_path = output_path.with_suffix(".pdf")
        build_document_pdf(
            pdf_path,
            self.document_type.currentText(),
            self.customer_name.text().strip(),
            self.document_number.text().strip(),
            line_items,
        )

        self.status_label.setText(f"Excel und PDF erstellt: {output_path}")

    def save_order(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        customer_id = self.customer_select.currentData()
        if customer_id is None:
            self.status_label.setText("Bitte einen Kunden aus den Stammdaten auswaehlen.")
            return

        line_items = self._line_items_from_table()
        if not line_items:
            self.add_line_item()
            line_items = self._line_items_from_table()
        order_lines = self._order_lines_from_items(line_items)
        if not order_lines:
            self.status_label.setText("Bitte Produkte aus der Preisliste verwenden, um einen Auftrag zu speichern.")
            return

        session = self.session_factory()
        try:
            order = create_order(
                session,
                OrderCreate(
                    order_number=self.order_number.text().strip(),
                    customer_id=customer_id,
                    order_date=self.delivery_date.text().strip() or "ohne-datum",
                    delivery_date=self.delivery_date.text().strip() or "ohne-datum",
                    delivery_slot=self.delivery_slot.currentText() or None,
                    lines=order_lines,
                ),
            )
            self.current_order_id = order.id
            self.status_label.setText(f"Auftrag gespeichert: {order.order_number}")
        finally:
            session.close()

    def create_documents_from_order(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        if self.current_order_id is None:
            self.save_order()
        if self.current_order_id is None:
            return

        session = self.session_factory()
        try:
            documents = create_order_documents(
                session,
                order_id=self.current_order_id,
                delivery_note_number=self.delivery_note_number.text().strip(),
                invoice_number=self.invoice_number.text().strip(),
                datev_upload_dir=Path.cwd() / "outputs" / "datev_upload",
            )
            self.status_label.setText(
                f"Lieferschein und Rechnung erstellt: {documents[0].excel_path} / {documents[1].excel_path}"
            )
        finally:
            session.close()

    def _line_items_from_table(self) -> list[dict]:
        line_items = []
        for row in range(self.line_items_table.rowCount()):
            name_item = self.line_items_table.item(row, 0)
            quantity_item = self.line_items_table.item(row, 1)
            price_item = self.line_items_table.item(row, 2)
            deposit_item = self.line_items_table.item(row, 3)
            if name_item is None or not name_item.text().strip():
                continue
            line_items.append(
                {
                    "name": name_item.text().strip(),
                    "quantity": int(quantity_item.text()) if quantity_item is not None else 1,
                    "unit_price_cents": self._parse_euro_cents(price_item.text() if price_item is not None else "0"),
                    "deposit_cents": self._parse_euro_cents(deposit_item.text() if deposit_item is not None else "0"),
                    "product_id": self._product_id_for_name(name_item.text().strip()),
                }
            )
        return line_items

    def _order_lines_from_items(self, line_items: list[dict]) -> list[OrderLineCreate]:
        order_lines = []
        for item in line_items:
            product_id = item.get("product_id")
            if product_id is None:
                continue
            order_lines.append(
                OrderLineCreate(
                    product_id=product_id,
                    quantity=item["quantity"],
                    unit_price_cents=item["unit_price_cents"],
                    deposit_cents=item["deposit_cents"],
                )
            )
        return order_lines

    def _product_id_for_name(self, product_name: str) -> int | None:
        for product_id, product in self.products_by_id.items():
            if product.name == product_name:
                return product_id
        return None

    def _output_path(self) -> Path:
        paths = build_document_paths(
            customer_folder=Path(self.customer_folder.text().strip()),
            document_type=self.document_type.currentText(),
            document_number=self.document_number.text().strip(),
            customer_name=self.customer_name.text().strip(),
            document_date=self.delivery_date.text().strip() or "ohne-datum",
        )
        return paths.excel_path

    def _parse_euro_cents(self, value: str) -> int:
        normalized = value.strip().replace(".", "").replace(",", ".")
        return int(round(float(normalized) * 100))
