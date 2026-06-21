from pathlib import Path
from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from ..schemas import OrderCreate, OrderLineCreate
from ..services.customer_service import list_active_customers
from ..services.numbering_service import suggest_next_numbers
from ..services.order_service import archive_order, create_order, create_order_documents, list_active_orders
from ..services.product_service import list_active_products
from .date_input import DateInput, to_display_date


ORDER_PANEL_ACTIONS = {
    "refreshOrderDataButton": "Stammdaten laden",
    "suggestNumbersButton": "Nummern vorschlagen",
    "addOrderLineButton": "Position hinzufuegen",
    "removeOrderLineButton": "Position entfernen",
    "saveOrderButton": "Auftrag speichern",
    "createOrderDocumentsButton": "Lieferschein und Rechnung erzeugen",
    "refreshOrdersButton": "Auftragsliste laden",
}

ORDER_LINE_COLUMNS = ("Produkt", "Menge", "Preis EUR", "Pfand EUR")
ORDER_COLUMNS = ("Auftrag", "Kunde", "Lieferdatum", "Zeitfenster", "Status")
ORDER_PANEL_SECTIONS = (
    "1. Kunde und Lieferung",
    "2. Positionen",
    "3. Belege erzeugen",
    "Vorhandene Auftraege",
)
ORDER_GUIDANCE_STEPS = (
    "Stammdaten laden und Kunden waehlen.",
    "Produkte mit Menge als Positionen hinzufuegen.",
    "Auftrag speichern und daraus Lieferschein plus Rechnung erzeugen.",
)
ORDER_CONTEXT_ACTIONS = {
    "open": "Auftrag oeffnen",
    "create_documents": "Belege erzeugen",
    "archive": "Auftrag archivieren",
}
DATE_FIELD_WIDGETS = ("delivery_date",)


class OrderPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.customers_by_id = {}
        self.products_by_id = {}
        self.order_ids_by_row = {}
        self.current_order_id = None

        self.customer_select = QComboBox()
        self.customer_select.addItem("Bitte Kunden waehlen", None)
        self.product_select = QComboBox()
        self.product_select.addItem("Bitte Produkt waehlen", None)
        self.order_number = QLineEdit()
        self.order_number.setPlaceholderText("z. B. AUF-1001")
        self.delivery_date = DateInput(date.today().isoformat())
        self.delivery_slot = QComboBox()
        self.delivery_slot.addItems(["", "vormittag", "nachmittag", "ganztags"])
        self.delivery_note_number = QLineEdit()
        self.delivery_note_number.setPlaceholderText("z. B. LS-1001")
        self.invoice_number = QLineEdit()
        self.invoice_number.setPlaceholderText("z. B. RG-1001")
        self.quantity = QSpinBox()
        self.quantity.setRange(1, 999)
        self.unit_price_eur = QLineEdit()
        self.deposit_eur = QLineEdit()
        self.deposit_eur.setPlaceholderText("z. B. 3,30")
        self.order_lines_table = QTableWidget(0, len(ORDER_LINE_COLUMNS))
        self.order_lines_table.setHorizontalHeaderLabels(ORDER_LINE_COLUMNS)
        self.orders_table = QTableWidget(0, len(ORDER_COLUMNS))
        self.orders_table.setHorizontalHeaderLabels(ORDER_COLUMNS)
        self.status_label = QLabel("Schritt 1: Stammdaten laden, dann Kunde und Produkte auswaehlen.")
        self.status_label.setObjectName("muted")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        headline = QLabel("Auftraege")
        headline.setObjectName("headline")
        layout.addWidget(headline)

        muted = QLabel("Normaler Ablauf: Auftrag erfassen und daraus Lieferschein plus Rechnung erzeugen")
        muted.setObjectName("muted")
        layout.addWidget(muted)

        layout.addWidget(self._guidance_box())

        self.refresh_data_button = self._button("refreshOrderDataButton")
        self.suggest_numbers_button = self._button("suggestNumbersButton")
        self.add_line_button = self._button("addOrderLineButton")
        self.remove_line_button = self._button("removeOrderLineButton")
        self.save_order_button = self._button("saveOrderButton")
        self.create_documents_button = self._button("createOrderDocumentsButton")
        self.refresh_orders_button = self._button("refreshOrdersButton")

        workspace = QHBoxLayout()
        workspace.setSpacing(18)
        left_column = QVBoxLayout()
        left_column.setSpacing(14)
        right_column = QVBoxLayout()
        right_column.setSpacing(14)
        workspace.addLayout(left_column, 1)
        workspace.addLayout(right_column, 1)
        layout.addLayout(workspace)

        customer_box, customer_layout = self._section(
            ORDER_PANEL_SECTIONS[0],
            "Zuerst Stammdaten laden, dann Kunde, Lieferdatum und Nummern erfassen.",
        )
        customer_form = QFormLayout()
        customer_form.addRow("Kunde", self.customer_select)
        customer_form.addRow("Auftragsnummer", self.order_number)
        customer_form.addRow("Lieferdatum", self.delivery_date)
        customer_form.addRow("Zeitfenster", self.delivery_slot)
        customer_form.addRow("Lieferscheinnummer", self.delivery_note_number)
        customer_form.addRow("Rechnungsnummer", self.invoice_number)
        customer_layout.addLayout(customer_form)
        customer_actions = QHBoxLayout()
        customer_actions.addWidget(self.refresh_data_button)
        customer_actions.addWidget(self.suggest_numbers_button)
        customer_actions.addStretch()
        customer_layout.addLayout(customer_actions)
        left_column.addWidget(customer_box)

        position_box, position_layout = self._section(
            ORDER_PANEL_SECTIONS[1],
            "Produkt waehlen, Menge pruefen und als Position in den Auftrag uebernehmen.",
        )
        position_form = QFormLayout()
        position_form.addRow("Produkt", self.product_select)
        position_form.addRow("Menge", self.quantity)
        position_form.addRow("Preis EUR", self.unit_price_eur)
        position_form.addRow("Pfand EUR", self.deposit_eur)
        position_layout.addLayout(position_form)
        position_actions = QHBoxLayout()
        position_actions.addWidget(self.add_line_button)
        position_actions.addWidget(self.remove_line_button)
        position_actions.addStretch()
        position_layout.addLayout(position_actions)
        position_layout.addWidget(QLabel("Positionen im Auftrag"))
        position_layout.addWidget(self.order_lines_table)
        left_column.addWidget(position_box)

        document_box, document_layout = self._section(
            ORDER_PANEL_SECTIONS[2],
            "Wenn alle Positionen stimmen: Auftrag speichern und daraus die Belege erzeugen.",
        )
        document_actions = QHBoxLayout()
        document_actions.addWidget(self.save_order_button)
        document_actions.addWidget(self.create_documents_button)
        document_actions.addStretch()
        document_layout.addLayout(document_actions)
        right_column.addWidget(document_box)

        orders_box, orders_layout = self._section(
            ORDER_PANEL_SECTIONS[3],
            "Vorhandenen Auftrag doppelt anklicken, um danach die Belege zu erzeugen.",
        )
        orders_actions = QHBoxLayout()
        orders_actions.addWidget(self.refresh_orders_button)
        orders_actions.addStretch()
        orders_layout.addLayout(orders_actions)
        orders_layout.addWidget(self.orders_table)
        right_column.addWidget(orders_box)

        layout.addWidget(self.status_label)

        self.refresh_data_button.clicked.connect(self.refresh_master_data)
        self.suggest_numbers_button.clicked.connect(self.suggest_numbers)
        self.add_line_button.clicked.connect(self.add_order_line)
        self.remove_line_button.clicked.connect(self.remove_selected_order_line)
        self.save_order_button.clicked.connect(self.save_order)
        self.create_documents_button.clicked.connect(self.create_documents_from_order)
        self.refresh_orders_button.clicked.connect(self.refresh_orders)
        self.product_select.currentIndexChanged.connect(self.apply_selected_product)
        self.orders_table.itemDoubleClicked.connect(lambda _item: self.load_selected_order_id())
        self.orders_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.orders_table.customContextMenuRequested.connect(self.show_order_context_menu)
        self.refresh_master_data()
        self.refresh_orders()
        self.suggest_numbers()

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(ORDER_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def suggest_numbers(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        session = self.session_factory()
        try:
            suggestions = suggest_next_numbers(session)
        finally:
            session.close()

        self.order_number.setText(suggestions.order_number)
        self.delivery_note_number.setText(suggestions.delivery_note_number)
        self.invoice_number.setText(suggestions.invoice_number)
        self.status_label.setText(
            "Nummern vorgeschlagen. Sie koennen jede Nummer vor dem Speichern manuell ueberschreiben."
        )

    def _guidance_box(self) -> QWidget:
        box = QWidget()
        box.setObjectName("guidanceBox")
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        title = QLabel("So erstellen Sie einen Auftrag")
        title.setObjectName("stepTitle")
        layout.addWidget(title)

        for index, step in enumerate(ORDER_GUIDANCE_STEPS, start=1):
            label = QLabel(f"{index}. {step}")
            label.setObjectName("stepText")
            layout.addWidget(label)

        return box

    def _section(self, title: str, subtitle: str) -> tuple[QGroupBox, QVBoxLayout]:
        box = QGroupBox(title)
        box.setObjectName("sectionBox")
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("sectionSubtitle")
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)
        return box, layout

    def refresh_master_data(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            customers = list_active_customers(session)
            products = list_active_products(session)
        finally:
            session.close()

        self.customer_select.blockSignals(True)
        self.product_select.blockSignals(True)
        self.customer_select.clear()
        self.product_select.clear()
        self.customer_select.addItem("Bitte Kunden waehlen", None)
        self.product_select.addItem("Bitte Produkt waehlen", None)
        self.customers_by_id = {customer.id: customer for customer in customers}
        self.products_by_id = {product.id: product for product in products}
        for customer in customers:
            self.customer_select.addItem(customer.name, customer.id)
        for product in products:
            self.product_select.addItem(product.name, product.id)
        self.customer_select.blockSignals(False)
        self.product_select.blockSignals(False)
        self.status_label.setText(f"{len(customers)} Kunden und {len(products)} Produkte geladen.")

    def apply_selected_product(self) -> None:
        product_id = self.product_select.currentData()
        if product_id is None:
            return
        product = self.products_by_id.get(product_id)
        if product is None:
            return
        self.unit_price_eur.setText(f"{product.standard_price_cents / 100:.2f}".replace(".", ","))

    def add_order_line(self) -> None:
        product_id = self.product_select.currentData()
        product = self.products_by_id.get(product_id)
        if product is None:
            self.status_label.setText("Bitte zuerst ein Produkt auswaehlen.")
            return
        row = self.order_lines_table.rowCount()
        self.order_lines_table.insertRow(row)
        values = (
            product.name,
            str(self.quantity.value()),
            self.unit_price_eur.text().strip(),
            self.deposit_eur.text().strip() or "0,00",
        )
        for column, value in enumerate(values):
            self.order_lines_table.setItem(row, column, QTableWidgetItem(value))
        self.status_label.setText("Position hinzugefuegt. Weitere Positionen erfassen oder Auftrag speichern.")

    def remove_selected_order_line(self) -> None:
        row = self.order_lines_table.currentRow()
        if row >= 0:
            self.order_lines_table.removeRow(row)

    def save_order(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        customer_id = self.customer_select.currentData()
        if customer_id is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswaehlen.")
            return
        order_lines = self._order_lines_from_table()
        if not order_lines:
            self.status_label.setText("Bitte mindestens eine Position hinzufuegen.")
            return

        session = self.session_factory()
        try:
            order = create_order(
                session,
                OrderCreate(
                    order_number=self.order_number.text().strip(),
                    customer_id=customer_id,
                    order_date=self.delivery_date.iso_date() or "ohne-datum",
                    delivery_date=self.delivery_date.iso_date() or "ohne-datum",
                    delivery_slot=self.delivery_slot.currentText() or None,
                    lines=order_lines,
                ),
            )
            self.current_order_id = order.id
            self.show_orders(list_active_orders(session))
            self.status_label.setText("Auftrag gespeichert. Jetzt Lieferschein und Rechnung erzeugen.")
        finally:
            session.close()

    def create_documents_from_order(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        if self.current_order_id is None:
            self.load_selected_order_id()
        if self.current_order_id is None:
            self.status_label.setText("Bitte zuerst Auftrag speichern oder aus der Liste waehlen.")
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
            self.show_orders(list_active_orders(session))
            self.status_label.setText(
                f"Erstellt: {Path(documents[0].pdf_path).name} und {Path(documents[1].pdf_path).name}"
            )
        finally:
            session.close()

    def refresh_orders(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            self.show_orders(list_active_orders(session))
        finally:
            session.close()

    def show_orders(self, orders: list) -> None:
        self.order_ids_by_row = {}
        self.orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self.order_ids_by_row[row] = order.id
            values = (
                order.order_number,
                order.customer.name,
                to_display_date(order.delivery_date),
                order.delivery_slot or "",
                order.status,
            )
            for column, value in enumerate(values):
                self.orders_table.setItem(row, column, QTableWidgetItem(value))
        self.status_label.setText(f"{len(orders)} Auftraege geladen.")

    def load_selected_order_id(self) -> None:
        row = self.orders_table.currentRow()
        self.current_order_id = self.order_ids_by_row.get(row)
        if self.current_order_id is not None:
            self.status_label.setText("Auftrag ausgewaehlt. Jetzt Belege erzeugen.")

    def archive_selected_order(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        if self.current_order_id is None:
            self.load_selected_order_id()
        if self.current_order_id is None:
            self.status_label.setText("Bitte zuerst einen Auftrag auswaehlen.")
            return

        session = self.session_factory()
        try:
            order = archive_order(session, self.current_order_id)
            self.current_order_id = None
            self.show_orders(list_active_orders(session))
            self.status_label.setText(f"Auftrag archiviert: {order.order_number}")
        finally:
            session.close()

    def show_order_context_menu(self, position) -> None:
        if self.orders_table.currentRow() < 0:
            return
        menu = QMenu(self)
        open_action = menu.addAction(ORDER_CONTEXT_ACTIONS["open"])
        documents_action = menu.addAction(ORDER_CONTEXT_ACTIONS["create_documents"])
        archive_action = menu.addAction(ORDER_CONTEXT_ACTIONS["archive"])
        selected = menu.exec(self.orders_table.viewport().mapToGlobal(position))
        if selected == open_action:
            self.load_selected_order_id()
        elif selected == documents_action:
            self.load_selected_order_id()
            self.create_documents_from_order()
        elif selected == archive_action:
            self.load_selected_order_id()
            self.archive_selected_order()

    def _order_lines_from_table(self) -> list[OrderLineCreate]:
        order_lines = []
        for row in range(self.order_lines_table.rowCount()):
            product_item = self.order_lines_table.item(row, 0)
            quantity_item = self.order_lines_table.item(row, 1)
            price_item = self.order_lines_table.item(row, 2)
            deposit_item = self.order_lines_table.item(row, 3)
            if product_item is None:
                continue
            product_id = self._product_id_for_name(product_item.text())
            if product_id is None:
                continue
            order_lines.append(
                OrderLineCreate(
                    product_id=product_id,
                    quantity=int(quantity_item.text()) if quantity_item is not None else 1,
                    unit_price_cents=self._parse_euro_cents(price_item.text() if price_item is not None else "0"),
                    deposit_cents=self._parse_euro_cents(deposit_item.text() if deposit_item is not None else "0"),
                )
            )
        return order_lines

    def _product_id_for_name(self, product_name: str) -> int | None:
        for product_id, product in self.products_by_id.items():
            if product.name == product_name:
                return product_id
        return None

    def _parse_euro_cents(self, value: str) -> int:
        normalized = value.strip().replace(".", "").replace(",", ".")
        return int(round(float(normalized) * 100))
