from pathlib import Path
from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QHeaderView,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from ..schemas import DepositReturnCreate, OrderCreate, OrderLineCreate
from ..services.customer_service import list_active_customers
from ..services.numbering_service import suggest_next_numbers
from ..services.order_service import (
    archive_order,
    create_order,
    create_order_delivery_order,
    create_order_invoice,
    get_order,
    list_active_orders,
    update_order,
)
from ..services.product_service import list_active_products
from .date_input import DateInput, to_display_date
from .searchable_select import SearchableSelect


ORDER_PANEL_ACTIONS = {
    "orderHelpButton": "?",
    "newOrderButton": "Neuer Auftrag",
    "refreshOrderDataButton": "Stammdaten laden",
    "suggestOrderNumberButton": "Auftragsnummer vorschlagen",
    "suggestDeliveryNoteNumberButton": "Lieferscheinnummer vorschlagen",
    "suggestInvoiceNumberButton": "Rechnungsnummer vorschlagen",
    "addOrderLineButton": "Position hinzufuegen",
    "removeOrderLineButton": "Position entfernen",
    "addDepositReturnButton": "Pfand zurueck hinzufuegen",
    "removeDepositReturnButton": "Pfand zurueck entfernen",
    "saveOrderButton": "Auftrag speichern",
    "createDeliveryOrderButton": "LS Excel/PDF erstellen",
    "createInvoiceButton": "Rechnung Excel/PDF erstellen",
    "openLastExcelButton": "Excel oeffnen",
    "openLastPdfButton": "PDF oeffnen",
    "refreshOrdersButton": "Auftragsliste laden",
}

ORDER_LINE_COLUMNS = ("Produkt", "Menge", "Preis EUR", "Pfand EUR", "Summe EUR")
DEPOSIT_RETURN_COLUMNS = ("Pfandart", "Menge", "Pfand EUR", "Gutschrift EUR")
ORDER_COLUMNS = ("Auftrag", "Kunde", "Lieferdatum", "Zeitfenster", "Status")
ORDER_PANEL_SECTIONS = (
    "Kopfdaten",
    "Positionen",
    "Excel/PDF aus Auftrag erstellen",
    "Bestehende Auftraege",
)
ORDER_HELP_TEXT = (
    "Kopfdaten: Kunde, Lieferdatum, Zeitfenster und Auftragsnummer pruefen.\n\n"
    "Positionen: Produkt waehlen, Menge eintragen und Position hinzufuegen.\n\n"
    "Belegabschluss: Erst speichern, danach entweder Lieferauftrag (LS) oder Rechnung gezielt erzeugen."
)
ORDER_GUIDANCE_STEPS = (
    "Kunden suchen und Lieferdatum pruefen.",
    "Produkte hinzufuegen und Positionen kontrollieren.",
    "Auftrag speichern, danach Lieferauftrag oder Rechnung gezielt erstellen.",
)
ORDER_CONTEXT_ACTIONS = {
    "open": "Auftrag oeffnen",
    "create_delivery_order": "LS Excel/PDF erstellen",
    "create_invoice": "Rechnung Excel/PDF erstellen",
    "archive": "Auftrag archivieren",
}
DATE_FIELD_WIDGETS = ("delivery_date",)


class OrderPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.customers_by_id = {}
        self.products_by_id = {}
        self.customer_rows = []
        self.order_ids_by_row = {}
        self.current_order_id = None
        self.current_order_status = "geplant"
        self.last_excel_path: Path | None = None
        self.last_pdf_path: Path | None = None

        self.order_mode_label = QLabel("Neuer Auftrag")
        self.order_mode_label.setObjectName("stepTitle")
        self.customer_select = SearchableSelect("Kunde suchen, z. B. Cafe oder Hotel")
        self.customer_summary = QLabel("Noch kein Kunde ausgewaehlt.")
        self.customer_summary.setObjectName("sectionSubtitle")
        self.customer_summary.setWordWrap(True)
        self.product_select = SearchableSelect("Produkt suchen, z. B. Spezi oder Wasser")
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
        self.deposit_return_name = QLineEdit()
        self.deposit_return_name.setPlaceholderText("z. B. Leergut Kiste 4,80")
        self.deposit_return_quantity = QSpinBox()
        self.deposit_return_quantity.setRange(1, 999)
        self.deposit_return_eur = QLineEdit()
        self.deposit_return_eur.setPlaceholderText("z. B. 4,80")
        self.order_lines_table = QTableWidget(0, len(ORDER_LINE_COLUMNS))
        self.order_lines_table.setHorizontalHeaderLabels(ORDER_LINE_COLUMNS)
        self.order_lines_table.setMinimumHeight(320)
        self.order_lines_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.deposit_returns_table = QTableWidget(0, len(DEPOSIT_RETURN_COLUMNS))
        self.deposit_returns_table.setHorizontalHeaderLabels(DEPOSIT_RETURN_COLUMNS)
        self.deposit_returns_table.setMaximumHeight(150)
        self.deposit_returns_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_total_label = QLabel("Auftragssumme: 0,00 EUR")
        self.order_total_label.setObjectName("stepTitle")
        self.orders_table = QTableWidget(0, len(ORDER_COLUMNS))
        self.orders_table.setHorizontalHeaderLabels(ORDER_COLUMNS)
        self.orders_table.setMaximumHeight(180)
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.status_label = QLabel("Schritt 1: Stammdaten laden, dann Kunde und Produkte auswaehlen.")
        self.status_label.setObjectName("muted")
        self.document_result_label = QLabel(
            "Noch keine Datei erstellt. Erst Auftrag speichern, dann LS oder Rechnung als Excel/PDF erzeugen."
        )
        self.document_result_label.setObjectName("sectionSubtitle")
        self.document_result_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        header_row = QHBoxLayout()
        title_column = QVBoxLayout()
        headline = QLabel("Auftraege")
        headline.setObjectName("headline")
        title_column.addWidget(headline)
        muted = QLabel("Kopfdaten erfassen, Positionen pruefen, Belege erzeugen")
        muted.setObjectName("muted")
        title_column.addWidget(muted)
        header_row.addLayout(title_column)
        header_row.addStretch()
        self.help_button = QPushButton(ORDER_PANEL_ACTIONS["orderHelpButton"])
        self.help_button.setObjectName("helpButton")
        header_row.addWidget(self.help_button)
        layout.addLayout(header_row)

        self.refresh_data_button = self._button("refreshOrderDataButton")
        self.suggest_order_number_button = self._button("suggestOrderNumberButton")
        self.suggest_delivery_note_number_button = self._button("suggestDeliveryNoteNumberButton")
        self.suggest_invoice_number_button = self._button("suggestInvoiceNumberButton")
        self.add_line_button = self._button("addOrderLineButton")
        self.remove_line_button = self._button("removeOrderLineButton")
        self.add_deposit_return_button = self._button("addDepositReturnButton")
        self.remove_deposit_return_button = self._button("removeDepositReturnButton")
        self.save_order_button = self._button("saveOrderButton")
        self.create_delivery_order_button = self._button("createDeliveryOrderButton")
        self.create_invoice_button = self._button("createInvoiceButton")
        self.open_last_excel_button = self._button("openLastExcelButton")
        self.open_last_pdf_button = self._button("openLastPdfButton")
        self.open_last_excel_button.setEnabled(False)
        self.open_last_pdf_button.setEnabled(False)
        self.refresh_orders_button = self._button("refreshOrdersButton")
        self.new_order_button = self._button("newOrderButton")

        customer_box, customer_layout = self._section(
            ORDER_PANEL_SECTIONS[0],
            "Wie beim Rechnungsformular: oben stehen Kunde, Lieferdatum, Zeitfenster und Auftragsnummer.",
        )
        customer_layout.addWidget(self.order_mode_label)
        customer_form = QFormLayout()
        customer_form.addRow("Kunde", self.customer_select)
        customer_form.addRow("Auftragsnummer", self._number_row(self.order_number, self.suggest_order_number_button))
        customer_form.addRow("Lieferdatum", self.delivery_date)
        customer_form.addRow("Zeitfenster", self.delivery_slot)
        customer_layout.addLayout(customer_form)
        customer_layout.addWidget(self.customer_summary)
        customer_actions = QHBoxLayout()
        customer_actions.addWidget(self.new_order_button)
        customer_actions.addWidget(self.refresh_data_button)
        customer_actions.addStretch()
        customer_layout.addLayout(customer_actions)
        layout.addWidget(customer_box)

        middle_row = QHBoxLayout()
        middle_row.setSpacing(18)
        layout.addLayout(middle_row)

        position_box, position_layout = self._section(
            ORDER_PANEL_SECTIONS[1],
            "Links Produkt erfassen, rechts die Positionen wie in einer Belegliste kontrollieren.",
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

        return_title = QLabel("Pfand zurueck")
        return_title.setObjectName("sectionTitle")
        position_layout.addWidget(return_title)
        deposit_return_form = QFormLayout()
        deposit_return_form.addRow("Pfandart", self.deposit_return_name)
        deposit_return_form.addRow("Menge", self.deposit_return_quantity)
        deposit_return_form.addRow("Pfand EUR", self.deposit_return_eur)
        position_layout.addLayout(deposit_return_form)
        deposit_return_actions = QHBoxLayout()
        deposit_return_actions.addWidget(self.add_deposit_return_button)
        deposit_return_actions.addWidget(self.remove_deposit_return_button)
        deposit_return_actions.addStretch()
        position_layout.addLayout(deposit_return_actions)
        middle_row.addWidget(position_box, 1)

        line_box, line_layout = self._section("Belegpositionen", "Alle hinzugefuegten Artikel dieses Auftrags.")
        line_layout.addWidget(self.order_lines_table)
        line_layout.addWidget(self.deposit_returns_table)
        line_layout.addWidget(self.order_total_label)
        middle_row.addWidget(line_box, 3)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(18)
        layout.addLayout(bottom_row)

        document_box, document_layout = self._section(
            ORDER_PANEL_SECTIONS[2],
            "Erst Auftrag speichern. Danach wird die Excel-Vorlage automatisch befuellt und als Excel/PDF abgelegt.",
        )
        document_form = QFormLayout()
        document_form.addRow(
            "LS-Nummer",
            self._number_row(self.delivery_note_number, self.suggest_delivery_note_number_button),
        )
        document_form.addRow(
            "Rechnungsnummer",
            self._number_row(self.invoice_number, self.suggest_invoice_number_button),
        )
        document_layout.addLayout(document_form)
        document_actions = QHBoxLayout()
        document_actions.addWidget(self.save_order_button)
        document_actions.addWidget(self.create_delivery_order_button)
        document_actions.addWidget(self.create_invoice_button)
        document_actions.addWidget(self.open_last_excel_button)
        document_actions.addWidget(self.open_last_pdf_button)
        document_actions.addStretch()
        document_layout.addLayout(document_actions)
        document_layout.addWidget(self.document_result_label)
        bottom_row.addWidget(document_box, 1)

        orders_box, orders_layout = self._section(
            ORDER_PANEL_SECTIONS[3],
            "Vorhandenen Auftrag doppelt anklicken oder per Rechtsklick weiterbearbeiten.",
        )
        orders_actions = QHBoxLayout()
        orders_actions.addWidget(self.refresh_orders_button)
        orders_actions.addStretch()
        orders_layout.addLayout(orders_actions)
        orders_layout.addWidget(self.orders_table)
        bottom_row.addWidget(orders_box, 2)

        layout.addWidget(self.status_label)

        self.help_button.clicked.connect(self.show_help)
        self.refresh_data_button.clicked.connect(self.refresh_master_data)
        self.suggest_order_number_button.clicked.connect(self.suggest_order_number)
        self.suggest_delivery_note_number_button.clicked.connect(self.suggest_delivery_note_number)
        self.suggest_invoice_number_button.clicked.connect(self.suggest_invoice_number)
        self.new_order_button.clicked.connect(self.reset_order_form)
        self.add_line_button.clicked.connect(self.add_order_line)
        self.remove_line_button.clicked.connect(self.remove_selected_order_line)
        self.add_deposit_return_button.clicked.connect(self.add_deposit_return)
        self.remove_deposit_return_button.clicked.connect(self.remove_selected_deposit_return)
        self.save_order_button.clicked.connect(self.save_order)
        self.create_delivery_order_button.clicked.connect(self.create_delivery_order_from_order)
        self.create_invoice_button.clicked.connect(self.create_invoice_from_order)
        self.open_last_excel_button.clicked.connect(self.open_last_excel_file)
        self.open_last_pdf_button.clicked.connect(self.open_last_pdf_file)
        self.refresh_orders_button.clicked.connect(self.refresh_orders)
        self.order_lines_table.itemChanged.connect(self.update_order_total)
        self.deposit_returns_table.itemChanged.connect(self.update_order_total)
        self.customer_select.selection_changed.connect(self.apply_selected_customer)
        self.product_select.selection_changed.connect(self.apply_selected_product)
        self.orders_table.itemDoubleClicked.connect(lambda _item: self.load_selected_order_id())
        self.orders_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.orders_table.customContextMenuRequested.connect(self.show_order_context_menu)
        self.refresh_master_data()
        self.refresh_orders()
        self.suggest_order_number()

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(ORDER_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def _number_row(self, field: QLineEdit, button: QPushButton) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(field)
        layout.addWidget(button)
        return row

    def _number_suggestions(self):
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return None

        session = self.session_factory()
        try:
            return suggest_next_numbers(session)
        finally:
            session.close()

    def suggest_order_number(self) -> None:
        suggestions = self._number_suggestions()
        if suggestions is None:
            return
        self.order_number.setText(suggestions.order_number)
        self.status_label.setText("Auftragsnummer vorgeschlagen. Sie kann manuell ueberschrieben werden.")

    def suggest_delivery_note_number(self) -> None:
        suggestions = self._number_suggestions()
        if suggestions is None:
            return
        self.delivery_note_number.setText(suggestions.delivery_note_number)
        self.status_label.setText("Lieferscheinnummer vorgeschlagen. Sie kann manuell ueberschrieben werden.")

    def suggest_invoice_number(self) -> None:
        suggestions = self._number_suggestions()
        if suggestions is None:
            return
        self.invoice_number.setText(suggestions.invoice_number)
        self.status_label.setText("Rechnungsnummer vorgeschlagen. Sie kann manuell ueberschrieben werden.")

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

    def _section(self, title: str, subtitle: str) -> tuple[QWidget, QVBoxLayout]:
        box = QWidget()
        box.setObjectName("sectionBox")
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("sectionSubtitle")
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)
        return box, layout

    def show_help(self) -> None:
        QMessageBox.information(self, "Hilfe: Auftrag erfassen", ORDER_HELP_TEXT)

    def reset_order_form(self) -> None:
        self.current_order_id = None
        self.current_order_status = "geplant"
        self.last_excel_path = None
        self.last_pdf_path = None
        self.order_mode_label.setText("Neuer Auftrag")
        self.order_number.clear()
        self.delivery_date.set_iso_date(date.today().isoformat())
        self.delivery_slot.setCurrentText("")
        self.order_lines_table.setRowCount(0)
        self.deposit_returns_table.setRowCount(0)
        self.deposit_return_name.clear()
        self.deposit_return_quantity.setValue(1)
        self.deposit_return_eur.clear()
        self.document_result_label.setText(
            "Noch keine Datei erstellt. Erst Auftrag speichern, dann LS oder Rechnung als Excel/PDF erzeugen."
        )
        self.open_last_excel_button.setEnabled(False)
        self.open_last_pdf_button.setEnabled(False)
        self.update_order_total()
        self.suggest_order_number()
        self.status_label.setText("Neuer Auftrag gestartet.")

    def confirm_documented_order_change(self) -> bool:
        if self.current_order_status == "geplant":
            return True
        answer = QMessageBox.question(
            self,
            "Auftrag wurde bereits belegt",
            "Dieser Auftrag hat bereits einen Lieferauftrag oder eine Rechnung. "
            "Wenn Sie ihn aendern, bitte die Belege neu erstellen. Fortfahren?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.status_label.setText("Aenderung abgebrochen. Belege bleiben unveraendert.")
            return False
        self.status_label.setText("Auftrag geaendert. Belege neu erstellen.")
        return True

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

        self.customers_by_id = {customer.id: customer for customer in customers}
        self.customer_rows = customers
        self.products_by_id = {product.id: product for product in products}
        self.customer_select.set_items(
            [
                (
                    customer.name,
                    customer.id,
                    " | ".join(
                        value
                        for value in (
                            customer.address or "",
                            customer.delivery_notes or "",
                            customer.payment_method or "",
                        )
                        if value
                    ),
                )
                for customer in customers
            ]
        )
        self.product_select.set_items(
            [
                (
                    product.name,
                    product.id,
                    " | ".join(
                        value
                        for value in (
                            product.article_number or "",
                            product.unit,
                            f"{product.standard_price_cents / 100:.2f} EUR",
                        )
                        if value
                    ),
                )
                for product in products
            ]
        )
        self.apply_selected_customer()
        self.status_label.setText(f"{len(customers)} Kunden und {len(products)} Produkte geladen.")

    def apply_selected_customer(self) -> None:
        customer_id = self.customer_select.current_value()
        customer = self.customers_by_id.get(customer_id)
        if customer is None:
            self.customer_summary.setText("Noch kein Kunde ausgewaehlt.")
            return
        details = [
            f"Adresse: {customer.address or 'nicht gepflegt'}",
            f"Zahlungsart: {customer.payment_method or 'nicht gepflegt'}",
            f"Hinweis: {customer.delivery_notes or 'kein Lieferhinweis'}",
        ]
        self.customer_summary.setText(" | ".join(details))

    def apply_selected_product(self) -> None:
        product_id = self.product_select.current_value()
        if product_id is None:
            return
        product = self.products_by_id.get(product_id)
        if product is None:
            return
        self.unit_price_eur.setText(f"{product.standard_price_cents / 100:.2f}".replace(".", ","))
        self.deposit_eur.setText(f"{product.default_deposit_cents / 100:.2f}".replace(".", ","))

    def add_order_line(self) -> None:
        product_id = self.product_select.current_value()
        product = self.products_by_id.get(product_id)
        if product is None:
            self.status_label.setText("Bitte zuerst ein Produkt auswaehlen.")
            return
        self._append_order_line_to_table(
            product.name,
            self.quantity.value(),
            self._parse_euro_cents(self.unit_price_eur.text().strip()),
            self._parse_euro_cents(self.deposit_eur.text().strip() or "0"),
            product.id,
        )
        self.status_label.setText("Position hinzugefuegt. Weitere Positionen erfassen oder Auftrag speichern.")

    def add_deposit_return(self) -> None:
        name = self.deposit_return_name.text().strip()
        if not name:
            self.status_label.setText("Bitte eine Pfandart fuer die Rueckgabe eintragen.")
            return
        deposit_cents = self._parse_euro_cents_or_zero(self.deposit_return_eur.text())
        if deposit_cents <= 0:
            self.status_label.setText("Bitte einen Pfandwert groesser 0 eintragen.")
            return
        self._append_deposit_return_to_table(
            name,
            self.deposit_return_quantity.value(),
            deposit_cents,
        )
        self.status_label.setText("Pfandrueckgabe hinzugefuegt.")

    def remove_selected_order_line(self) -> None:
        row = self.order_lines_table.currentRow()
        if row >= 0:
            self.order_lines_table.removeRow(row)
            self.update_order_total()

    def remove_selected_deposit_return(self) -> None:
        row = self.deposit_returns_table.currentRow()
        if row >= 0:
            self.deposit_returns_table.removeRow(row)
            self.update_order_total()

    def save_order(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        customer_id = self.customer_select.current_value()
        if customer_id is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswaehlen.")
            return
        order_lines = self._order_lines_from_table()
        if not order_lines:
            self.status_label.setText("Bitte mindestens eine Position hinzufuegen.")
            return
        if self.current_order_id is not None and not self.confirm_documented_order_change():
            return

        session = self.session_factory()
        try:
            payload = OrderCreate(
                order_number=self.order_number.text().strip(),
                customer_id=customer_id,
                order_date=self.delivery_date.iso_date() or "ohne-datum",
                delivery_date=self.delivery_date.iso_date() or "ohne-datum",
                delivery_slot=self.delivery_slot.currentText() or None,
                lines=order_lines,
                deposit_returns=self._deposit_returns_from_table(),
            )
            if self.current_order_id is None:
                order = create_order(session, payload)
                self.status_label.setText("Auftrag gespeichert. Jetzt Lieferauftrag oder Rechnung erstellen.")
            else:
                order = update_order(session, self.current_order_id, payload)
                self.status_label.setText("Auftrag aktualisiert. Excel/PDF bei Bedarf neu erstellen.")
            self.current_order_id = order.id
            self.current_order_status = order.status
            self.order_mode_label.setText(f"Auftrag bearbeiten: {order.order_number}")
            self.show_orders(list_active_orders(session))
        finally:
            session.close()

    def create_delivery_order_from_order(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        if self.current_order_id is None:
            self.load_selected_order_id()
        if self.current_order_id is None:
            self.status_label.setText("Bitte zuerst Auftrag speichern.")
            return
        session = self.session_factory()
        try:
            document = create_order_delivery_order(
                session,
                self.current_order_id,
                self.delivery_note_number.text().strip(),
            )
            self.show_orders(list_active_orders(session))
            self.current_order_status = "lieferauftrag_erstellt"
            self._show_document_result("Lieferauftrag", document.excel_path, document.pdf_path)
        finally:
            session.close()

    def create_invoice_from_order(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        if self.current_order_id is None:
            self.load_selected_order_id()
        if self.current_order_id is None:
            self.status_label.setText("Bitte zuerst Auftrag speichern.")
            return
        session = self.session_factory()
        try:
            document = create_order_invoice(
                session,
                self.current_order_id,
                self.invoice_number.text().strip(),
                datev_upload_dir=Path.cwd() / "outputs" / "datev_upload",
            )
            self.show_orders(list_active_orders(session))
            self.current_order_status = "fakturiert"
            self._show_document_result("Rechnung", document.excel_path, document.pdf_path)
        finally:
            session.close()

    def _show_document_result(self, document_label: str, excel_path: str, pdf_path: str) -> None:
        excel = Path(excel_path)
        pdf = Path(pdf_path)
        self.last_excel_path = excel
        self.last_pdf_path = pdf
        self.open_last_excel_button.setEnabled(True)
        self.open_last_pdf_button.setEnabled(True)
        self.status_label.setText(f"{document_label} erstellt. Excel und PDF liegen im Kundenordner.")
        self.document_result_label.setText(
            f"{document_label} erstellt.\nExcel: {excel}\nPDF: {pdf}"
        )

    def open_last_excel_file(self) -> None:
        self._open_local_file(self.last_excel_path)

    def open_last_pdf_file(self) -> None:
        self._open_local_file(self.last_pdf_path)

    def _open_local_file(self, path: Path | None) -> None:
        if path is None or not path.exists():
            self.status_label.setText("Noch keine Datei zum Oeffnen vorhanden.")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

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
        if self.current_order_id is None or self.session_factory is None:
            return
        session = self.session_factory()
        try:
            order = get_order(session, self.current_order_id)
            self.populate_order_form(order)
            self.status_label.setText("Auftrag geladen. Positionen anpassen und Auftrag speichern.")
        finally:
            session.close()

    def populate_order_form(self, order) -> None:
        self.order_mode_label.setText(f"Auftrag bearbeiten: {order.order_number}")
        self.current_order_status = order.status
        self.order_number.setText(order.order_number)
        self.customer_select.select_value(order.customer_id)
        self.delivery_date.set_iso_date(order.delivery_date)
        self.delivery_slot.setCurrentText(order.delivery_slot or "")
        self.order_lines_table.setRowCount(0)
        self.deposit_returns_table.setRowCount(0)
        for line in order.lines:
            self._append_order_line_to_table(
                line.product_name,
                line.quantity,
                line.unit_price_cents,
                line.deposit_cents,
                line.product_id,
            )
        for deposit_return in order.deposit_returns:
            self._append_deposit_return_to_table(
                deposit_return.name,
                deposit_return.quantity,
                deposit_return.deposit_cents,
            )

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
        delivery_order_action = menu.addAction(ORDER_CONTEXT_ACTIONS["create_delivery_order"])
        invoice_action = menu.addAction(ORDER_CONTEXT_ACTIONS["create_invoice"])
        archive_action = menu.addAction(ORDER_CONTEXT_ACTIONS["archive"])
        selected = menu.exec(self.orders_table.viewport().mapToGlobal(position))
        if selected == open_action:
            self.load_selected_order_id()
        elif selected == delivery_order_action:
            self.load_selected_order_id()
            self.create_delivery_order_from_order()
        elif selected == invoice_action:
            self.load_selected_order_id()
            self.create_invoice_from_order()
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
            product_id = product_item.data(Qt.ItemDataRole.UserRole) or self._product_id_for_name(product_item.text())
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

    def _deposit_returns_from_table(self) -> list[DepositReturnCreate]:
        deposit_returns = []
        for row in range(self.deposit_returns_table.rowCount()):
            name_item = self.deposit_returns_table.item(row, 0)
            quantity_item = self.deposit_returns_table.item(row, 1)
            deposit_item = self.deposit_returns_table.item(row, 2)
            if name_item is None or not name_item.text().strip():
                continue
            deposit_returns.append(
                DepositReturnCreate(
                    name=name_item.text().strip(),
                    quantity=int(quantity_item.text()) if quantity_item is not None else 1,
                    deposit_cents=self._parse_euro_cents(deposit_item.text() if deposit_item is not None else "0"),
                )
            )
        return deposit_returns

    def _append_order_line_to_table(
        self,
        product_name: str,
        quantity: int,
        unit_price_cents: int,
        deposit_cents: int,
        product_id: int | None = None,
    ) -> None:
        line_total_cents = (unit_price_cents + deposit_cents) * quantity
        row = self.order_lines_table.rowCount()
        self.order_lines_table.blockSignals(True)
        self.order_lines_table.insertRow(row)
        values = (
            product_name,
            str(quantity),
            f"{unit_price_cents / 100:.2f}".replace(".", ","),
            f"{deposit_cents / 100:.2f}".replace(".", ","),
            self._format_euro_cents(line_total_cents),
        )
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column == 0:
                item.setData(Qt.ItemDataRole.UserRole, product_id)
            if column == 4:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.order_lines_table.setItem(row, column, item)
        self.order_lines_table.blockSignals(False)
        self.update_order_total()

    def _append_deposit_return_to_table(
        self,
        name: str,
        quantity: int,
        deposit_cents: int,
    ) -> None:
        credit_cents = deposit_cents * quantity
        row = self.deposit_returns_table.rowCount()
        self.deposit_returns_table.blockSignals(True)
        self.deposit_returns_table.insertRow(row)
        values = (
            name,
            str(quantity),
            f"{deposit_cents / 100:.2f}".replace(".", ","),
            self._format_euro_cents(-credit_cents),
        )
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column == 3:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.deposit_returns_table.setItem(row, column, item)
        self.deposit_returns_table.blockSignals(False)
        self.update_order_total()

    def update_order_total(self, _item=None) -> None:
        total_cents = 0
        self.order_lines_table.blockSignals(True)
        self.deposit_returns_table.blockSignals(True)
        try:
            for row in range(self.order_lines_table.rowCount()):
                line_total_cents = self._line_total_cents_for_row(row)
                total_cents += line_total_cents
                total_item = self.order_lines_table.item(row, 4)
                if total_item is None:
                    total_item = QTableWidgetItem()
                    total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.order_lines_table.setItem(row, 4, total_item)
                total_item.setText(self._format_euro_cents(line_total_cents))
            for row in range(self.deposit_returns_table.rowCount()):
                return_total_cents = self._deposit_return_total_cents_for_row(row)
                total_cents -= return_total_cents
                total_item = self.deposit_returns_table.item(row, 3)
                if total_item is None:
                    total_item = QTableWidgetItem()
                    total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.deposit_returns_table.setItem(row, 3, total_item)
                total_item.setText(self._format_euro_cents(-return_total_cents))
        finally:
            self.order_lines_table.blockSignals(False)
            self.deposit_returns_table.blockSignals(False)
        self.order_total_label.setText(f"Auftragssumme: {self._format_euro_cents(total_cents)}")

    def _line_total_cents_for_row(self, row: int) -> int:
        quantity_item = self.order_lines_table.item(row, 1)
        price_item = self.order_lines_table.item(row, 2)
        deposit_item = self.order_lines_table.item(row, 3)
        try:
            quantity = int(quantity_item.text()) if quantity_item is not None else 0
        except ValueError:
            quantity = 0
        return (
            self._parse_euro_cents_or_zero(price_item.text() if price_item is not None else "")
            + self._parse_euro_cents_or_zero(deposit_item.text() if deposit_item is not None else "")
        ) * quantity

    def _deposit_return_total_cents_for_row(self, row: int) -> int:
        quantity_item = self.deposit_returns_table.item(row, 1)
        deposit_item = self.deposit_returns_table.item(row, 2)
        try:
            quantity = int(quantity_item.text()) if quantity_item is not None else 0
        except ValueError:
            quantity = 0
        return self._parse_euro_cents_or_zero(deposit_item.text() if deposit_item is not None else "") * quantity

    def _product_id_for_name(self, product_name: str) -> int | None:
        for product_id, product in self.products_by_id.items():
            if product.name == product_name:
                return product_id
        return None

    def _parse_euro_cents(self, value: str) -> int:
        normalized = value.strip().replace(".", "").replace(",", ".")
        return int(round(float(normalized) * 100))

    def _parse_euro_cents_or_zero(self, value: str) -> int:
        try:
            return self._parse_euro_cents(value)
        except ValueError:
            return 0

    def _format_euro_cents(self, cents: int) -> str:
        return f"{cents / 100:.2f} EUR".replace(".", ",")
