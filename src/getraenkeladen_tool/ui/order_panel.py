from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
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
from PySide6.QtCore import Qt, Signal

from ..schemas import DepositReturnCreate, OrderCreate, OrderLineCreate
from ..services.customer_service import list_active_customers
from ..services.customer_assortment_service import list_customer_assortment
from ..services.order_service import (
    archive_order,
    create_order,
    get_order,
    list_active_orders,
    update_order,
)
from ..services.product_service import list_active_products
from .date_input import DateInput, to_display_date
from .deposit_return_presets import DEPOSIT_RETURN_PRESETS
from .layouts import ContentSurface, PageHeader, ResponsiveSplitter, WorkspaceCard, configure_form_layout
from .searchable_select import SearchableSelect


ORDER_PANEL_ACTIONS = {
    "orderHelpButton": "?",
    "newOrderButton": "Bestellung erfassen",
    "copyOrderButton": "Markierte Bestellung kopieren",
    "refreshOrderDataButton": "Kunden/Artikel neu laden",
    "addOrderLineButton": "Position hinzufuegen",
    "removeOrderLineButton": "Position entfernen",
    "addDepositReturnButton": "Pfand-Rueckgabe eintragen",
    "removeDepositReturnButton": "Pfand-Rueckgabe entfernen",
    "saveOrderButton": "Bestellung speichern",
    "refreshOrdersButton": "Bestellungen laden",
    "createDeliveryNoteFromOrderButton": "Lieferschein erstellen",
    "createInvoiceFromOrderButton": "Rechnung erstellen",
}

ORDER_LINE_COLUMNS = ("Produkt", "Menge", "Preis je Einheit EUR", "Pfand je Einheit EUR", "Summe EUR")
ASSORTMENT_COLUMNS = ("Artikel", "Letzte Menge", "Preis aktuell", "Preis Excel", "Hinweis")
DEPOSIT_RETURN_COLUMNS = ("Pfandart", "Menge", "Pfand EUR", "Gutschrift EUR")
ORDER_COLUMNS = ("Bestellung", "Kunde", "Lieferdatum", "Zeitfenster", "Status")
ORDER_PANEL_SECTIONS = (
    "Kundenkopf",
    "Kundensortiment",
    "Bestellungen verwalten",
)
ORDER_HELP_TEXT = (
    "Kundenkopf: Kunde, Lieferdatum, Zeitfenster und Bestellnummer pruefen.\n\n"
    "Kundensortiment: letzte Mengen sehen, neue Mengen eintragen und Artikel hinzufuegen.\n\n"
    "Bestellungen: Vorhandene Bestellungen oeffnen, archivieren oder als Vorlage fuer eine neue Bestellung kopieren."
)
ORDER_GUIDANCE_STEPS = (
    "Kunde suchen und letzte Mengen als Vorlage sehen.",
    "Neue Mengen, neue Artikel und Pfand-Rueckgabe erfassen.",
    "Bestellung speichern und daraus Lieferschein oder Rechnung erzeugen.",
)
ORDER_CONTEXT_ACTIONS = {
    "open": "Bestellung oeffnen",
    "copy": "Als neue Bestellung kopieren",
    "create_delivery_note": "Lieferschein erstellen",
    "create_invoice": "Rechnung erstellen",
    "archive": "Bestellung archivieren",
}
DATE_FIELD_WIDGETS = ("delivery_date",)


class OrderPanel(QWidget):
    delivery_note_requested = Signal(int)
    invoice_requested = Signal(int)

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.customers_by_id = {}
        self.products_by_id = {}
        self.customer_rows = []
        self.order_ids_by_row = {}
        self.assortment_rows_by_row = {}
        self.current_order_id = None
        self.current_order_status = "geplant"

        self.order_mode_label = QLabel("Neue Bestellung")
        self.order_mode_label.setObjectName("stepTitle")
        self.customer_select = SearchableSelect("Kunde suchen, z. B. Cafe oder Hotel")
        self.customer_select.setMinimumWidth(420)
        self.customer_summary = QLabel("Noch kein Kunde ausgewaehlt.")
        self.customer_summary.setObjectName("sectionSubtitle")
        self.customer_summary.setWordWrap(True)
        self.product_select = SearchableSelect("Produkt suchen, z. B. Spezi oder Wasser")
        self.product_select.setMinimumWidth(420)
        self.assortment_table = QTableWidget(0, len(ASSORTMENT_COLUMNS))
        self.assortment_table.setHorizontalHeaderLabels(ASSORTMENT_COLUMNS)
        self.assortment_table.setMinimumHeight(220)
        self.assortment_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.assortment_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.assortment_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_number = QLineEdit()
        self.order_number.setPlaceholderText("z. B. 2606196 oder LS-3001")
        self.delivery_date = DateInput(date.today().isoformat())
        self.delivery_slot = QComboBox()
        self.delivery_slot.addItems(["", "vormittag", "nachmittag", "ganztags"])
        self.quantity = QSpinBox()
        self.quantity.setRange(1, 999)
        self.unit_price_eur = QLineEdit()
        self.deposit_eur = QLineEdit()
        self.deposit_eur.setPlaceholderText("z. B. 3,30")
        self.deposit_return_select = QComboBox()
        for label, cents in DEPOSIT_RETURN_PRESETS:
            self.deposit_return_select.addItem(label, cents)
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
        self.order_total_label = QLabel("Bestellsumme: 0,00 EUR")
        self.order_total_label.setObjectName("stepTitle")
        self.orders_table = QTableWidget(0, len(ORDER_COLUMNS))
        self.orders_table.setHorizontalHeaderLabels(ORDER_COLUMNS)
        self.orders_table.setMinimumHeight(360)
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_table_search = QLineEdit()
        self.order_table_search.setObjectName("tableSearchField")
        self.order_table_search.setPlaceholderText("In den Bestellungen suchen, z. B. Kunde, Nummer oder Datum")
        self.status_label = QLabel("Schritt 1: Kunde suchen, letzte Mengen pruefen, neue Bestellung erfassen.")
        self.status_label.setObjectName("muted")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        self.help_button = QPushButton(ORDER_PANEL_ACTIONS["orderHelpButton"])
        self.help_button.setObjectName("helpButton")
        layout.addWidget(PageHeader("Bestellung erfassen", "Kundenordner-Vorlage oeffnen, Mengen pruefen und Bestellung speichern.", self.help_button))

        self.refresh_data_button = self._button("refreshOrderDataButton")
        self.add_line_button = self._button("addOrderLineButton")
        self.remove_line_button = self._button("removeOrderLineButton")
        self.add_deposit_return_button = self._button("addDepositReturnButton")
        self.remove_deposit_return_button = self._button("removeDepositReturnButton")
        self.save_order_button = self._button("saveOrderButton")
        self.cancel_order_dialog_button = QPushButton("Abbrechen")
        self.refresh_orders_button = self._button("refreshOrdersButton")
        self.new_order_button = self._button("newOrderButton")
        self.copy_order_button = self._button("copyOrderButton")
        self.create_delivery_note_button = self._button("createDeliveryNoteFromOrderButton")
        self.create_invoice_button = self._button("createInvoiceFromOrderButton")
        self.use_assortment_button = QPushButton("Aus Sortiment uebernehmen")

        self.order_dialog: QDialog | None = None
        self.order_editor_widget = QWidget()
        self.order_editor_widget.setObjectName("orderEditorDialogBody")
        new_order_layout = QVBoxLayout(self.order_editor_widget)
        new_order_layout.setContentsMargins(0, 0, 0, 0)
        new_order_layout.setSpacing(14)

        customer_box, customer_layout = self._section(
            ORDER_PANEL_SECTIONS[0],
            "Oben stehen die Angaben, die beim Telefonat und fuer den Beleg wichtig sind.",
        )
        customer_layout.addWidget(self.order_mode_label)
        customer_form = QFormLayout()
        configure_form_layout(customer_form)
        customer_form.addRow("Kunde", self.customer_select)
        customer_form.addRow("Bestellnummer", self.order_number)
        customer_form.addRow("Lieferdatum", self.delivery_date)
        customer_form.addRow("Zeitfenster", self.delivery_slot)
        customer_layout.addLayout(customer_form)
        customer_layout.addWidget(self.customer_summary)
        customer_actions = QHBoxLayout()
        customer_actions.addWidget(self.refresh_data_button)
        customer_actions.addWidget(self.save_order_button)
        customer_actions.addWidget(self.cancel_order_dialog_button)
        customer_actions.addStretch()
        customer_layout.addLayout(customer_actions)
        new_order_layout.addWidget(customer_box)

        order_entry_splitter = ResponsiveSplitter()
        new_order_layout.addWidget(order_entry_splitter, 1)

        position_box, position_layout = self._section(
            ORDER_PANEL_SECTIONS[1],
            "Links Produkt erfassen, rechts die Positionen wie in einer Belegliste kontrollieren.",
        )
        position_layout.addWidget(self.assortment_table)
        assortment_actions = QHBoxLayout()
        assortment_actions.addWidget(self.use_assortment_button)
        assortment_actions.addStretch()
        position_layout.addLayout(assortment_actions)
        position_form = QFormLayout()
        configure_form_layout(position_form)
        position_form.addRow("Produkt", self.product_select)
        position_form.addRow("Menge", self.quantity)
        position_form.addRow("Preis EUR", self.unit_price_eur)
        position_form.addRow("Pfand je Einheit EUR", self.deposit_eur)
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
        configure_form_layout(deposit_return_form)
        deposit_return_form.addRow("Pfandart", self.deposit_return_select)
        deposit_return_form.addRow("Menge", self.deposit_return_quantity)
        deposit_return_form.addRow("Pfandwert EUR", self.deposit_return_eur)
        position_layout.addLayout(deposit_return_form)
        deposit_return_actions = QHBoxLayout()
        deposit_return_actions.addWidget(self.add_deposit_return_button)
        deposit_return_actions.addWidget(self.remove_deposit_return_button)
        deposit_return_actions.addStretch()
        position_layout.addLayout(deposit_return_actions)
        order_entry_splitter.addWidget(position_box)

        line_box, line_layout = self._section("Bestellpositionen", "Alle hinzugefuegten Artikel dieser Bestellung.")
        line_layout.addWidget(self.order_lines_table)
        line_layout.addWidget(self.deposit_returns_table)
        total_bar = QWidget()
        total_bar.setObjectName("totalBar")
        total_layout = QHBoxLayout(total_bar)
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_layout.addStretch()
        total_layout.addWidget(self.order_total_label)
        line_layout.addWidget(total_bar)
        order_entry_splitter.addWidget(line_box)
        order_entry_splitter.setStretchFactor(0, 1)
        order_entry_splitter.setStretchFactor(1, 3)

        orders_box, orders_layout = self._section(
            ORDER_PANEL_SECTIONS[2],
            "Vorhandene Bestellung doppelt anklicken oder per Rechtsklick weiterbearbeiten.",
        )
        orders_actions = QHBoxLayout()
        orders_actions.addWidget(self.new_order_button)
        orders_actions.addWidget(self.refresh_orders_button)
        orders_actions.addWidget(self.copy_order_button)
        orders_actions.addWidget(self.create_delivery_note_button)
        orders_actions.addWidget(self.create_invoice_button)
        orders_actions.addStretch()
        orders_layout.addLayout(orders_actions)
        orders_layout.addWidget(self.order_table_search)
        orders_layout.addWidget(self.orders_table)
        layout.addWidget(orders_box, 1)

        layout.addWidget(self.status_label)

        self.help_button.clicked.connect(self.show_help)
        self.refresh_data_button.clicked.connect(self.refresh_master_data)
        self.new_order_button.clicked.connect(self.open_new_order_dialog)
        self.cancel_order_dialog_button.clicked.connect(self.close_order_dialog)
        self.copy_order_button.clicked.connect(self.copy_selected_order_as_new)
        self.create_delivery_note_button.clicked.connect(self.request_delivery_note_for_selected_order)
        self.create_invoice_button.clicked.connect(self.request_invoice_for_selected_order)
        self.use_assortment_button.clicked.connect(self.add_selected_assortment_item)
        self.add_line_button.clicked.connect(self.add_order_line)
        self.remove_line_button.clicked.connect(self.remove_selected_order_line)
        self.add_deposit_return_button.clicked.connect(self.add_deposit_return)
        self.remove_deposit_return_button.clicked.connect(self.remove_selected_deposit_return)
        self.save_order_button.clicked.connect(self.save_order)
        self.refresh_orders_button.clicked.connect(self.refresh_orders)
        self.order_lines_table.itemChanged.connect(self.update_order_total)
        self.deposit_returns_table.itemChanged.connect(self.update_order_total)
        self.deposit_return_select.currentIndexChanged.connect(self.apply_selected_deposit_return)
        self.customer_select.selection_changed.connect(self.apply_selected_customer)
        self.order_table_search.textChanged.connect(self.apply_order_table_search)
        self.product_select.selection_changed.connect(self.apply_selected_product)
        self.orders_table.itemDoubleClicked.connect(lambda _item: self.load_selected_order_id())
        self.orders_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.orders_table.customContextMenuRequested.connect(self.show_order_context_menu)
        self.refresh_master_data()
        self.refresh_orders()
        self.apply_selected_deposit_return()

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(ORDER_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def _guidance_box(self) -> QWidget:
        box = QWidget()
        box.setObjectName("guidanceBox")
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        title = QLabel("So erfassen Sie eine Bestellung")
        title.setObjectName("stepTitle")
        layout.addWidget(title)

        for index, step in enumerate(ORDER_GUIDANCE_STEPS, start=1):
            label = QLabel(f"{index}. {step}")
            label.setObjectName("stepText")
            layout.addWidget(label)

        return box

    def _section(self, title: str, subtitle: str) -> tuple[QWidget, QVBoxLayout]:
        box = WorkspaceCard(title, subtitle)
        return box, box.layout

    def show_help(self) -> None:
        QMessageBox.information(self, "Hilfe: Bestellung erfassen", ORDER_HELP_TEXT)

    def open_new_order_dialog(self) -> None:
        self.reset_order_form()
        self.open_order_dialog("Neue Bestellung anlegen")

    def open_new_order_for_customer(self, customer_id: int) -> None:
        self.reset_order_form()
        self.customer_select.select_value(customer_id)
        self.apply_selected_customer()
        self.order_mode_label.setText("Neue Bestellung aus Kundenordner")
        self.open_order_dialog("Neue Bestellung aus Kundenordner")

    def open_order_dialog(self, title: str = "Bestellung bearbeiten") -> None:
        if self.order_dialog is not None:
            self.order_dialog.close()
        self.order_dialog = QDialog(self)
        self.order_dialog.setWindowTitle(title)
        self.order_dialog.setModal(True)
        self.order_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.order_dialog.resize(1100, 760)
        dialog_layout = QVBoxLayout(self.order_dialog)
        dialog_layout.setContentsMargins(18, 18, 18, 18)
        dialog_layout.addWidget(self.order_editor_widget)
        self.order_dialog.finished.connect(lambda _result: self._restore_order_editor_parent())
        self.order_dialog.show()

    def _restore_order_editor_parent(self) -> None:
        self.order_editor_widget.setParent(self)
        self.order_dialog = None

    def close_order_dialog(self) -> None:
        if self.order_dialog is not None:
            self.order_dialog.close()

    def close_order_dialog_after_success(self, order_number: str) -> None:
        self.close_order_dialog()
        self.refresh_orders()
        self.status_label.setText(f"Bestellung {order_number} gespeichert. Liste wurde aktualisiert.")

    def show_saved_order_next_steps(self, order_id: int, order_number: str) -> None:
        message = QMessageBox(self)
        message.setIcon(QMessageBox.Icon.Information)
        message.setWindowTitle("Bestellung gespeichert")
        message.setText(f"Bestellung {order_number} wurde gespeichert.")
        message.setInformativeText("Was moechten Sie als Naechstes tun?")
        delivery_button = message.addButton("Lieferschein erstellen", QMessageBox.ButtonRole.ActionRole)
        invoice_button = message.addButton("Rechnung erstellen", QMessageBox.ButtonRole.ActionRole)
        new_order_button = message.addButton("Weitere Bestellung", QMessageBox.ButtonRole.ActionRole)
        message.addButton("Zur Liste", QMessageBox.ButtonRole.RejectRole)
        message.exec()
        selected_button = message.clickedButton()
        if selected_button == delivery_button:
            self.delivery_note_requested.emit(order_id)
        elif selected_button == invoice_button:
            self.invoice_requested.emit(order_id)
        elif selected_button == new_order_button:
            self.open_new_order_dialog()

    def reset_order_form(self) -> None:
        self.current_order_id = None
        self.current_order_status = "geplant"
        self.order_mode_label.setText("Neue Bestellung")
        self.order_number.clear()
        self.delivery_date.set_iso_date(date.today().isoformat())
        self.delivery_slot.setCurrentText("")
        self.order_lines_table.setRowCount(0)
        self.deposit_returns_table.setRowCount(0)
        self.deposit_return_quantity.setValue(1)
        self.deposit_return_eur.clear()
        self.apply_selected_deposit_return()
        self.update_order_total()
        self.status_label.setText("Neue Bestellung gestartet. Bitte Bestellnummer eintragen.")

    def confirm_documented_order_change(self) -> bool:
        if self.current_order_status == "geplant":
            return True
        answer = QMessageBox.question(
            self,
            "Bestellung wurde bereits verwendet",
            "Aus dieser Bestellung wurde bereits ein Lieferschein oder eine Rechnung erstellt. "
            "Wenn Sie die Bestellung aendern, bitte die Dateien danach neu erstellen. Fortfahren?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.status_label.setText("Aenderung abgebrochen. Belege bleiben unveraendert.")
            return False
        self.status_label.setText("Bestellung geaendert. Dateien bitte neu erstellen.")
        return True

    def confirm_price_mismatch(
        self,
        product_name: str,
        excel_price_cents: int,
        central_price_cents: int,
        excel_deposit_cents: int = 0,
        central_deposit_cents: int = 0,
    ) -> bool:
        message = (
            f"Beim Artikel {product_name} weicht der Preis aus der Excel-Datei vom zentral gepflegten Preis ab.\n\n"
            f"Preis aus Excel: {self._format_euro_cents(excel_price_cents)}"
            f" | Pfand: {self._format_euro_cents(excel_deposit_cents)}\n"
            f"Zentral gepflegter Preis: {self._format_euro_cents(central_price_cents)}"
            f" | Pfand: {self._format_euro_cents(central_deposit_cents)}\n\n"
            "Ja = zentral gepflegten Preis uebernehmen.\n"
            "Nein = Preis aus Excel fuer diesen Vorgang behalten."
        )
        answer = QMessageBox.question(
            self,
            "Preisabweichung gefunden",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        return answer == QMessageBox.StandardButton.Yes

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
            customer_items := [
                (
                    customer.name,
                    customer.id,
                    " | ".join(
                        value
                        for value in (
                            customer.address or "",
                            customer.delivery_notes or "",
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
            self.show_customer_assortment([])
            return
        details = [
            f"Adresse: {customer.address or 'nicht gepflegt'}",
            f"Hinweis: {customer.delivery_notes or 'kein Lieferhinweis'}",
        ]
        self.customer_summary.setText(" | ".join(details))
        self.refresh_customer_assortment(customer.id)

    def refresh_customer_assortment(self, customer_id: int) -> None:
        if self.session_factory is None:
            self.show_customer_assortment([])
            return
        session = self.session_factory()
        try:
            rows = list_customer_assortment(session, customer_id)
        finally:
            session.close()
        self.show_customer_assortment(rows)

    def show_customer_assortment(self, rows: list) -> None:
        self.assortment_rows_by_row = {}
        self.assortment_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self.assortment_rows_by_row[row_index] = row
            hint = ""
            if row.product_id is None:
                hint = "Artikel pruefen"
            elif row.price_differs_from_central:
                hint = "Preis pruefen"
            values = (
                row.product_name or row.source_product_name,
                str(row.last_quantity),
                self._format_euro_cents(row.current_price_cents),
                self._format_euro_cents(row.excel_price_cents),
                hint,
            )
            for column, value in enumerate(values):
                self.assortment_table.setItem(row_index, column, QTableWidgetItem(value))

    def add_selected_assortment_item(self) -> None:
        row = self.assortment_rows_by_row.get(self.assortment_table.currentRow())
        if row is None:
            self.status_label.setText("Bitte zuerst einen Artikel aus dem Kundensortiment auswaehlen.")
            return
        if row.product_id is None:
            self.status_label.setText("Artikel ist noch nicht sicher zugeordnet. Bitte zuerst in der Pruefliste klaeren.")
            return
        unit_price_cents = row.current_price_cents
        deposit_cents = row.current_deposit_cents
        if row.price_differs_from_central and row.price_decision == "offen":
            use_central_price = self.confirm_price_mismatch(
                row.product_name or row.source_product_name,
                row.excel_price_cents,
                row.current_price_cents,
                row.excel_deposit_cents,
                row.current_deposit_cents,
            )
            if not use_central_price:
                unit_price_cents = row.excel_price_cents
                deposit_cents = row.excel_deposit_cents
        self._append_order_line_to_table(
            row.product_name or row.source_product_name,
            row.last_quantity if row.last_quantity > 0 else self.quantity.value(),
            unit_price_cents,
            deposit_cents,
            row.product_id,
        )
        self.status_label.setText("Position aus Kundensortiment uebernommen.")

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
        unit_price_cents = self._parse_euro_cents(self.unit_price_eur.text().strip())
        deposit_cents = self._parse_euro_cents(self.deposit_eur.text().strip() or "0")
        if unit_price_cents != product.standard_price_cents or deposit_cents != product.default_deposit_cents:
            use_central_price = self.confirm_price_mismatch(
                product.name,
                unit_price_cents,
                product.standard_price_cents,
                deposit_cents,
                product.default_deposit_cents,
            )
            if use_central_price:
                unit_price_cents = product.standard_price_cents
                deposit_cents = product.default_deposit_cents
                self.unit_price_eur.setText(f"{unit_price_cents / 100:.2f}".replace(".", ","))
                self.deposit_eur.setText(f"{deposit_cents / 100:.2f}".replace(".", ","))
        self._append_order_line_to_table(
            product.name,
            self.quantity.value(),
            unit_price_cents,
            deposit_cents,
            product.id,
        )
        self.status_label.setText("Position hinzugefuegt. Weitere Positionen erfassen oder Bestellung speichern.")

    def add_deposit_return(self) -> None:
        name = self.deposit_return_select.currentText().strip()
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

    def apply_selected_deposit_return(self) -> None:
        cents = self.deposit_return_select.currentData()
        if cents is None:
            return
        self.deposit_return_eur.setText(f"{int(cents) / 100:.2f}".replace(".", ","))

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
                self.status_label.setText(f"Erfolgreich gespeichert: Bestellung {order.order_number}.")
            else:
                order = update_order(session, self.current_order_id, payload)
                self.status_label.setText(f"Erfolgreich aktualisiert: Bestellung {order.order_number}.")
            self.current_order_id = order.id
            self.current_order_status = order.status
            self.order_mode_label.setText(f"Bestellung bearbeiten: {order.order_number}")
            self.show_orders(list_active_orders(session))
            self.close_order_dialog_after_success(order.order_number)
            self.show_saved_order_next_steps(order.id, order.order_number)
        except Exception as error:
            self.status_label.setText(f"Bestellung konnte nicht gespeichert werden: {error}")
            QMessageBox.warning(
                self,
                "Bestellung nicht gespeichert",
                f"Die Bestellung konnte nicht gespeichert werden.\n\nGrund: {error}",
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
        self.apply_order_table_search()
        self.status_label.setText(f"{len(orders)} Bestellungen geladen.")

    def apply_order_table_search(self) -> None:
        query = self.order_table_search.text().strip().lower()
        for row in range(self.orders_table.rowCount()):
            self.orders_table.setRowHidden(row, not self._row_matches_query(self.orders_table, row, query))

    def _row_matches_query(self, table: QTableWidget, row: int, query: str) -> bool:
        if not query:
            return True
        for column in range(table.columnCount()):
            item = table.item(row, column)
            if item is not None and query in item.text().lower():
                return True
        return False

    def load_selected_order_id(self) -> None:
        row = self.orders_table.currentRow()
        self.current_order_id = self.order_ids_by_row.get(row)
        if self.current_order_id is None or self.session_factory is None:
            return
        self.load_order_by_id(self.current_order_id)

    def load_order_by_id(self, order_id: int) -> None:
        if self.session_factory is None:
            return
        session = self.session_factory()
        try:
            order = get_order(session, order_id)
            self.current_order_id = order.id
            self.populate_order_form(order)
            self.open_order_dialog(f"Bestellung bearbeiten: {order.order_number}")
            self.status_label.setText("Bestellung geladen. Positionen anpassen und Bestellung speichern.")
        finally:
            session.close()

    def populate_order_form(self, order) -> None:
        self.order_mode_label.setText(f"Bestellung bearbeiten: {order.order_number}")
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

    def copy_selected_order_as_new(self) -> None:
        selected_order_id = self._selected_order_id()
        if selected_order_id is not None and selected_order_id != self.current_order_id:
            self.load_order_by_id(selected_order_id)
        if self.current_order_id is None:
            self.status_label.setText("Bitte zuerst eine Bestellung aus der Liste auswaehlen.")
            return
        original_number = self.order_number.text().strip()
        self.current_order_id = None
        self.current_order_status = "geplant"
        self.order_mode_label.setText(f"Kopie aus Bestellung {original_number}")
        self.order_number.clear()
        self.delivery_date.set_iso_date(date.today().isoformat())
        self.open_order_dialog(f"Bestellung aus {original_number} kopieren")
        self.status_label.setText("Bestellung kopiert. Bitte neue Bestellnummer und Datum pruefen.")

    def request_delivery_note_for_selected_order(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            self.status_label.setText("Bitte zuerst eine Bestellung aus der Liste auswaehlen.")
            return
        self.delivery_note_requested.emit(order_id)

    def request_invoice_for_selected_order(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            self.status_label.setText("Bitte zuerst eine Bestellung aus der Liste auswaehlen.")
            return
        self.invoice_requested.emit(order_id)

    def archive_selected_order(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        if self.current_order_id is None:
            self.current_order_id = self._selected_order_id()
        if self.current_order_id is None:
            self.status_label.setText("Bitte zuerst eine Bestellung auswaehlen.")
            return

        session = self.session_factory()
        try:
            order = archive_order(session, self.current_order_id)
            self.current_order_id = None
            self.show_orders(list_active_orders(session))
            self.status_label.setText(f"Bestellung archiviert: {order.order_number}")
        finally:
            session.close()

    def show_order_context_menu(self, position) -> None:
        if self.orders_table.currentRow() < 0:
            return
        menu = QMenu(self)
        open_action = menu.addAction(ORDER_CONTEXT_ACTIONS["open"])
        copy_action = menu.addAction(ORDER_CONTEXT_ACTIONS["copy"])
        delivery_note_action = menu.addAction(ORDER_CONTEXT_ACTIONS["create_delivery_note"])
        invoice_action = menu.addAction(ORDER_CONTEXT_ACTIONS["create_invoice"])
        archive_action = menu.addAction(ORDER_CONTEXT_ACTIONS["archive"])
        selected = menu.exec(self.orders_table.viewport().mapToGlobal(position))
        if selected == open_action:
            self.load_selected_order_id()
        elif selected == copy_action:
            self.load_selected_order_id()
            self.copy_selected_order_as_new()
        elif selected == delivery_note_action:
            self.request_delivery_note_for_selected_order()
        elif selected == invoice_action:
            self.request_invoice_for_selected_order()
        elif selected == archive_action:
            self.current_order_id = self._selected_order_id()
            self.archive_selected_order()

    def _selected_order_id(self) -> int | None:
        row = self.orders_table.currentRow()
        return self.order_ids_by_row.get(row)

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
        self.order_total_label.setText(f"Bestellsumme: {self._format_euro_cents(total_cents)}")

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
