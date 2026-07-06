from dataclasses import dataclass
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
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, Signal

from ..schemas import DepositReturnCreate, OrderCreate, OrderLineCreate
from ..services.automation_service import validate_order_before_save
from ..services.customer_service import list_active_customers
from ..services.customer_assortment_service import list_customer_assortment
from ..services.deposit_service import validate_deposit_returns
from ..services.number_suggestion_service import suggest_order_number
from ..services.order_service import (
    archive_order,
    create_order,
    get_order,
    latest_order_for_customer,
    list_active_orders,
    update_order,
)
from ..services.product_service import list_active_products
from .date_input import DateInput, to_display_date
from .deposit_return_presets import DEPOSIT_RETURN_PRESETS
from .layouts import (
    ContentSurface,
    PageHeader,
    WorkspaceCard,
    configure_form_layout,
    set_equal_button_widths,
)
from .searchable_select import SearchableSelect


ORDER_PANEL_ACTIONS = {
    "orderHelpButton": "?",
    "newOrderButton": "Neue Bestellung",
    "copyOrderButton": "Als Vorlage kopieren",
    "refreshOrderDataButton": "Daten neu laden",
    "suggestOrderNumberButton": "Nummer vorschlagen",
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
    "Kunde und Lieferdatum",
    "Mengen erfassen",
    "Bestellungen",
)
ORDER_HELP_TEXT = (
    "Kunde und Lieferdatum: Kunde, Lieferdatum, Zeitfenster und Bestellnummer pruefen.\n\n"
    "Mengen erfassen: letzte Mengen sehen, neue Mengen eintragen und Artikel hinzufuegen.\n\n"
    "Bestellungen: Vorhandene Bestellungen oeffnen, archivieren oder als Vorlage kopieren."
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


@dataclass(frozen=True, slots=True)
class PreviousOrderSuggestionRow:
    product_id: int | None
    source_product_name: str
    product_name: str | None
    last_quantity: int
    excel_price_cents: int
    excel_deposit_cents: int
    current_price_cents: int
    current_deposit_cents: int
    price_decision: str = "letzte_bestellung"
    price_differs_from_central: bool = False
    needs_review: bool = False


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
        self.product_select.help_label.setText("Erst Empfehlungen dieses Kunden, darunter alle Artikel.")
        self.assortment_table = QTableWidget(0, len(ASSORTMENT_COLUMNS))
        self.assortment_table.setHorizontalHeaderLabels(ASSORTMENT_COLUMNS)
        self.assortment_table.setMinimumHeight(180)
        self.assortment_table.setVisible(False)
        self.assortment_table.setAccessibleName("Interne Vorschlagsliste bisher bestellter Artikel")
        self.assortment_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.assortment_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.assortment_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.assortment_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.assortment_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.assortment_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.assortment_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.order_number = QLineEdit()
        self.order_number.setPlaceholderText("z. B. 2606196 oder LS-3001")
        self.suggest_order_number_button = self._button("suggestOrderNumberButton")
        self.delivery_date = DateInput(date.today().isoformat())
        self.delivery_slot = QComboBox()
        self.delivery_slot.addItems(["", "vormittag", "nachmittag", "ganztags"])
        self.quantity = QSpinBox()
        self.quantity.setRange(0, 999)
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
        self.order_lines_table.setMinimumHeight(220)
        self.order_lines_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.order_lines_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.order_lines_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.order_lines_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.order_lines_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.order_lines_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.deposit_returns_table = QTableWidget(0, len(DEPOSIT_RETURN_COLUMNS))
        self.deposit_returns_table.setHorizontalHeaderLabels(DEPOSIT_RETURN_COLUMNS)
        self.deposit_returns_table.setMaximumHeight(120)
        self.deposit_returns_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_total_label = QLabel("Bestellsumme: 0,00 EUR")
        self.order_total_label.setObjectName("totalAmount")
        self.orders_table = QTableWidget(0, len(ORDER_COLUMNS))
        self.orders_table.setHorizontalHeaderLabels(ORDER_COLUMNS)
        self.orders_table.setMinimumHeight(360)
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.order_table_search = QLineEdit()
        self.order_table_search.setObjectName("tableSearchField")
        self.order_table_search.setPlaceholderText("In den Bestellungen suchen, z. B. Kunde, Nummer oder Datum")
        self.status_label = QLabel("Kunde suchen, letzte Mengen pruefen, Bestellung speichern.")
        self.status_label.setObjectName("muted")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        self.help_button = QPushButton(ORDER_PANEL_ACTIONS["orderHelpButton"])
        self.help_button.setObjectName("helpButton")
        layout.addWidget(
            PageHeader(
                "Bestellungen",
                "Kunde waehlen, Mengen erfassen und direkt den naechsten Beleg vorbereiten.",
                self.help_button,
            )
        )

        self.refresh_data_button = self._button("refreshOrderDataButton")
        self.add_line_button = self._button("addOrderLineButton")
        self.remove_line_button = self._button("removeOrderLineButton")
        self.add_deposit_return_button = self._button("addDepositReturnButton")
        self.remove_deposit_return_button = self._button("removeDepositReturnButton")
        self.save_order_button = self._button("saveOrderButton")
        self.cancel_order_dialog_button = QPushButton("Eingabe zuruecksetzen")
        self.refresh_orders_button = self._button("refreshOrdersButton")
        self.new_order_button = self._button("newOrderButton")
        self.copy_order_button = self._button("copyOrderButton")
        self.create_delivery_note_button = self._button("createDeliveryNoteFromOrderButton")
        self.create_invoice_button = self._button("createInvoiceFromOrderButton")
        self.use_assortment_button = QPushButton("Aus Sortiment uebernehmen")
        set_equal_button_widths(
            (
                self.refresh_data_button,
                self.save_order_button,
                self.cancel_order_dialog_button,
                self.add_line_button,
                self.remove_line_button,
                self.add_deposit_return_button,
                self.remove_deposit_return_button,
                self.new_order_button,
                self.refresh_orders_button,
                self.copy_order_button,
                self.create_delivery_note_button,
                self.create_invoice_button,
                self.use_assortment_button,
            ),
            220,
        )

        self.order_dialog: QDialog | None = None
        self.order_editor_scroll: QScrollArea | None = None
        self.order_editor_widget = QWidget()
        self.order_editor_widget.setObjectName("orderEditorWorkspace")
        new_order_layout = QVBoxLayout(self.order_editor_widget)
        new_order_layout.setContentsMargins(0, 0, 0, 0)
        new_order_layout.setSpacing(14)

        customer_box, customer_layout = self._section(
            ORDER_PANEL_SECTIONS[0],
            "Oben stehen die Angaben, die beim Telefonat und fuer den Beleg wichtig sind.",
            tone="route",
            kicker="TELEFON",
        )
        customer_layout.addWidget(self.order_mode_label)
        customer_form = QFormLayout()
        configure_form_layout(customer_form)
        customer_form.addRow("Kunde", self.customer_select)
        order_number_row = QHBoxLayout()
        order_number_row.addWidget(self.order_number)
        order_number_row.addWidget(self.suggest_order_number_button)
        customer_form.addRow("Bestellnummer", order_number_row)
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

        quantity_box, quantity_layout = self._section(
            "Mengenliste bearbeiten",
            "Alle bekannten Artikel stehen direkt in der Liste. In der Spalte Menge tragen Sie nur ein, was heute geliefert werden soll. 0 bleibt auf dem Beleg sichtbar.",
            tone="document",
            kicker="BESTELLUNG",
        )
        quantity_hint = QLabel("Die Liste wird nach Kundenauswahl automatisch mit den letzten Artikeln gefuellt.")
        quantity_hint.setObjectName("sectionSubtitle")
        quantity_hint.setWordWrap(True)
        quantity_layout.addWidget(quantity_hint)
        quantity_layout.addWidget(self.assortment_table)
        quantity_layout.addWidget(self.order_lines_table)
        line_actions = QHBoxLayout()
        line_actions.addWidget(self.remove_line_button)
        line_actions.addStretch()
        quantity_layout.addLayout(line_actions)

        self.add_product_toggle = QPushButton("Weiteren Artikel hinzufuegen")
        self.add_product_toggle.setObjectName("disclosureButton")
        self.add_product_toggle.setCheckable(True)
        self.add_product_toggle.setChecked(False)
        quantity_layout.addWidget(self.add_product_toggle)
        self.add_product_content = QWidget()
        self.add_product_content.setObjectName("disclosurePanel")
        self.add_product_content.setVisible(False)
        add_product_layout = QVBoxLayout(self.add_product_content)
        position_form = QFormLayout()
        configure_form_layout(position_form)
        position_form.addRow("Produkt", self.product_select)
        position_form.addRow("Menge", self.quantity)
        position_form.addRow("Preis EUR", self.unit_price_eur)
        position_form.addRow("Pfand je Einheit EUR", self.deposit_eur)
        add_product_layout.addLayout(position_form)
        position_actions = QHBoxLayout()
        position_actions.addWidget(self.add_line_button)
        position_actions.addStretch()
        add_product_layout.addLayout(position_actions)
        quantity_layout.addWidget(self.add_product_content)

        return_title = QLabel("Pfand zurueck")
        return_title.setObjectName("sectionTitle")
        quantity_layout.addWidget(return_title)
        deposit_return_form = QFormLayout()
        configure_form_layout(deposit_return_form)
        deposit_return_form.addRow("Pfandart", self.deposit_return_select)
        deposit_return_form.addRow("Menge", self.deposit_return_quantity)
        deposit_return_form.addRow("Pfandwert EUR", self.deposit_return_eur)
        quantity_layout.addLayout(deposit_return_form)
        deposit_return_actions = QHBoxLayout()
        deposit_return_actions.addWidget(self.add_deposit_return_button)
        deposit_return_actions.addWidget(self.remove_deposit_return_button)
        deposit_return_actions.addStretch()
        quantity_layout.addLayout(deposit_return_actions)
        self.deposit_returns_table.setMaximumHeight(110)
        quantity_layout.addWidget(self.deposit_returns_table)
        total_bar = QWidget()
        total_bar.setObjectName("totalBar")
        total_bar.setMinimumHeight(58)
        total_layout = QHBoxLayout(total_bar)
        total_layout.setContentsMargins(16, 10, 16, 10)
        total_layout.addStretch()
        total_layout.addWidget(self.order_total_label)
        quantity_layout.addWidget(total_bar)
        new_order_layout.addWidget(quantity_box)
        layout.addWidget(self.order_editor_widget, 2)

        orders_box, orders_layout = self._section(
            ORDER_PANEL_SECTIONS[2],
            "Vorhandene Bestellung auswaehlen. Die Details werden oben im Arbeitsbereich bearbeitet.",
            tone="route",
            kicker="BESTELLSTAPEL",
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
        self.suggest_order_number_button.clicked.connect(self.apply_suggested_order_number)
        self.new_order_button.clicked.connect(self.open_new_order_dialog)
        self.cancel_order_dialog_button.clicked.connect(self.reset_order_form)
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
        self.add_product_toggle.toggled.connect(self.add_product_content.setVisible)
        self.order_table_search.textChanged.connect(self.apply_order_table_search)
        self.product_select.selection_changed.connect(self.apply_selected_product)
        self.orders_table.itemDoubleClicked.connect(lambda _item: self.load_selected_order_id())
        self.order_lines_table.customContextMenuRequested.connect(self.show_order_line_context_menu)
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

    def _section(self, title: str, subtitle: str, tone: str = "default", kicker: str = "") -> tuple[QWidget, QVBoxLayout]:
        box = WorkspaceCard(title, subtitle, tone=tone, kicker=kicker)
        return box, box.layout

    def show_help(self) -> None:
        QMessageBox.information(self, "Hilfe: Bestellung erfassen", ORDER_HELP_TEXT)

    def open_new_order_dialog(self) -> None:
        self.reset_order_form()
        self.open_order_dialog("Neue Bestellung")

    def open_new_order_for_customer(self, customer_id: int) -> None:
        self.reset_order_form()
        self.customer_select.select_value(customer_id)
        self.apply_selected_customer()
        self.order_mode_label.setText("Neue Bestellung aus Kunden")
        self.open_order_dialog("Neue Bestellung aus Kunden")
        self.prefill_order_lines_from_customer_assortment()

    def open_order_dialog(self, title: str = "Bestellung bearbeiten") -> None:
        self.order_mode_label.setText(title)
        self.status_label.setText(f"{title}: Angaben oben pruefen, Mengen erfassen und speichern.")

    def _restore_order_editor_parent(self) -> None:
        if self.order_editor_scroll is not None:
            self.order_editor_scroll.takeWidget()
            self.order_editor_scroll = None
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
        message.addButton("Nur speichern", QMessageBox.ButtonRole.RejectRole)
        delivery_button = message.addButton("Lieferschein erstellen", QMessageBox.ButtonRole.ActionRole)
        invoice_button = message.addButton("Rechnung erstellen", QMessageBox.ButtonRole.ActionRole)
        new_order_button = message.addButton("Weitere Bestellung", QMessageBox.ButtonRole.ActionRole)
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
        self.refresh_product_picker_items()
        self.apply_selected_customer()
        self.status_label.setText(f"{len(customers)} Kunden und {len(products)} Produkte geladen.")

    def refresh_product_picker_items(self) -> None:
        recommended_rows = [
            row
            for row in self.assortment_rows_by_row.values()
            if row.product_id is not None and row.product_id in self.products_by_id
        ]
        recommended_ids = {row.product_id for row in recommended_rows}
        items = []
        for row in recommended_rows:
            product_name = row.product_name or row.source_product_name
            detail = f"Letzte Menge {row.last_quantity} | {self._format_euro_cents(row.current_price_cents)}"
            items.append((product_name, row.product_id, detail, "Empfohlen fuer diesen Kunden"))
        for product in sorted(self.products_by_id.values(), key=lambda product: product.name.casefold()):
            if product.id in recommended_ids:
                continue
            items.append(
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
                    "Alle Artikel" if recommended_rows else "",
                )
            )
        self.product_select.set_items(items)
        if recommended_rows:
            self.product_select.help_label.setText("Oben: Empfehlungen dieses Kunden. Darunter: alle weiteren Artikel.")

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
        if self.current_order_id is None and self.order_lines_table.rowCount() == 0:
            self.prefill_order_lines_from_customer_assortment()

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
        self.refresh_product_picker_items()

    def prefill_order_lines_from_customer_assortment(self) -> None:
        self.order_lines_table.setRowCount(0)
        added_count = 0
        skipped_count = 0
        skipped_price_count = 0
        for row in self.assortment_rows_by_row.values():
            if row.product_id is None:
                skipped_count += 1
                continue
            if row.price_differs_from_central and row.price_decision == "offen":
                skipped_price_count += 1
                continue
            self._append_order_line_to_table(
                row.product_name or row.source_product_name,
                row.last_quantity,
                row.current_price_cents,
                row.current_deposit_cents,
                row.product_id,
            )
            added_count += 1
        self.update_order_total()
        if added_count:
            message = f"{added_count} Positionen aus den letzten Mengen uebernommen."
            if skipped_count:
                message += " Ungeklaerte Artikel wurden ausgelassen."
            if skipped_price_count:
                message += " Preisabweichungen wurden ausgelassen."
            self.status_label.setText(message)
        else:
            self.prefill_order_lines_from_latest_order()

    def prefill_order_lines_from_latest_order(self) -> None:
        customer_id = self.customer_select.current_value()
        if customer_id is None or self.session_factory is None:
            self.status_label.setText("Keine letzten Mengen zum Uebernehmen gefunden. Bitte Positionen manuell erfassen.")
            return
        session = self.session_factory()
        try:
            latest_order = latest_order_for_customer(session, int(customer_id))
            if latest_order is None:
                self.status_label.setText("Keine letzten Mengen zum Uebernehmen gefunden. Bitte Positionen manuell erfassen.")
                return
            self.show_previous_order_suggestions(latest_order.lines)
            for line in latest_order.lines:
                self._append_order_line_to_table(
                    line.product_name,
                    line.quantity,
                    line.unit_price_cents,
                    line.deposit_cents,
                    line.product_id,
                )
        finally:
            session.close()
        if self.order_lines_table.rowCount():
            self.status_label.setText("Positionen aus letzter Bestellung uebernommen.")
        else:
            self.status_label.setText("Letzte Bestellung hatte keine Mengen. Bitte Positionen manuell erfassen.")

    def show_previous_order_suggestions(self, lines: list) -> None:
        rows = [
            PreviousOrderSuggestionRow(
                product_id=line.product_id,
                source_product_name=line.product_name,
                product_name=line.product_name,
                last_quantity=line.quantity,
                excel_price_cents=line.unit_price_cents,
                excel_deposit_cents=line.deposit_cents,
                current_price_cents=line.unit_price_cents,
                current_deposit_cents=line.deposit_cents,
            )
            for line in lines
        ]
        self.show_customer_assortment(rows)

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
        self.product_select.clear_selection("Naechsten Artikel aus der Liste anklicken.")
        self.quantity.setValue(0)
        self.unit_price_eur.clear()
        self.deposit_eur.clear()
        self.status_label.setText("Position hinzugefuegt. Weitere Positionen erfassen oder Bestellung speichern.")

    def apply_suggested_order_number(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            suggestion = suggest_order_number(session, fallback_date=self.delivery_date.iso_date() or None)
        finally:
            session.close()
        self.order_number.setText(suggestion)
        self.status_label.setText(f"Vorschlag uebernommen: {suggestion}. Die Nummer kann frei geaendert werden.")

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
            self.warn_invalid_order_save("Keine Datenbankverbindung vorhanden.")
            return
        customer_id = self.customer_select.current_value()
        if customer_id is None:
            self.warn_invalid_order_save("Bitte zuerst einen Kunden auswaehlen.")
            return
        if not self.order_number.text().strip():
            self.warn_invalid_order_save("Bitte eine Bestellnummer eintragen.")
            return
        order_lines = self._order_lines_from_table()
        if not order_lines:
            self.warn_invalid_order_save("Bitte mindestens eine Position hinzufuegen.")
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
            warnings = [
                *validate_order_before_save(session, payload, exclude_order_id=self.current_order_id),
                *validate_deposit_returns(payload),
            ]
            if warnings and not self.confirm_automation_warnings(warnings):
                self.status_label.setText("Speichern abgebrochen. Hinweise bitte pruefen.")
                return
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

    def confirm_automation_warnings(self, warnings) -> bool:
        grouped = {
            "Blocker": [warning for warning in warnings if getattr(warning, "severity", "") == "error"],
            "Warnungen": [warning for warning in warnings if getattr(warning, "severity", "warning") == "warning"],
            "Hinweise": [
                warning
                for warning in warnings
                if getattr(warning, "severity", "") not in {"error", "warning"}
            ],
        }
        message = "Pruefung vor dem Speichern:\n\n"
        for title, entries in grouped.items():
            if not entries:
                continue
            message += f"{title}:\n"
            message += "\n".join(f"- {warning.message}" for warning in entries)
            message += "\n\n"
        message += "\n\nTrotzdem speichern?"
        answer = QMessageBox.question(
            self,
            "Bestellung pruefen",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def warn_invalid_order_save(self, message: str) -> None:
        self.status_label.setText(message)
        QMessageBox.warning(self, "Bestellung noch nicht gespeichert", message)

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
        self._select_order_row(self.current_order_id)
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
        order_id = self._selected_or_loaded_order_id()
        if order_id is None:
            self.status_label.setText("Bitte zuerst eine Bestellung aus der Liste auswaehlen.")
            return
        self.delivery_note_requested.emit(order_id)

    def request_invoice_for_selected_order(self) -> None:
        order_id = self._selected_or_loaded_order_id()
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

    def show_order_line_context_menu(self, position) -> None:
        clicked_row = self.order_lines_table.indexAt(position).row()
        if clicked_row >= 0:
            self.order_lines_table.setCurrentCell(clicked_row, 0)
        if self.order_lines_table.currentRow() < 0:
            return
        menu = QMenu(self)
        copy_action = menu.addAction("Position in neue Bestellung uebernehmen")
        remove_action = menu.addAction("Position entfernen")
        selected = menu.exec(self.order_lines_table.viewport().mapToGlobal(position))
        if selected == copy_action:
            self.copy_selected_order_line()
        elif selected == remove_action:
            self.remove_selected_order_line()

    def copy_selected_order_line(self) -> None:
        row = self.order_lines_table.currentRow()
        if row < 0:
            self.status_label.setText("Bitte zuerst eine Position auswaehlen.")
            return
        product_item = self.order_lines_table.item(row, 0)
        quantity_item = self.order_lines_table.item(row, 1)
        price_item = self.order_lines_table.item(row, 2)
        deposit_item = self.order_lines_table.item(row, 3)
        if product_item is None:
            self.status_label.setText("Diese Position kann nicht uebernommen werden.")
            return
        product_name = product_item.text().strip()
        product_id = product_item.data(Qt.ItemDataRole.UserRole) or self._product_id_for_name(product_name)
        try:
            quantity = int(quantity_item.text()) if quantity_item is not None else 0
        except ValueError:
            quantity = 0
        self._append_order_line_to_table(
            product_name,
            quantity,
            self._parse_euro_cents_or_zero(price_item.text() if price_item is not None else "0"),
            self._parse_euro_cents_or_zero(deposit_item.text() if deposit_item is not None else "0"),
            product_id,
        )
        self.status_label.setText("Position in die neue Bestellung uebernommen. Menge kann angepasst werden.")

    def _selected_order_id(self) -> int | None:
        row = self.orders_table.currentRow()
        return self.order_ids_by_row.get(row)

    def _select_order_row(self, order_id: int | None) -> None:
        if order_id is None:
            return
        for row, candidate_order_id in self.order_ids_by_row.items():
            if candidate_order_id == order_id and not self.orders_table.isRowHidden(row):
                self.orders_table.setCurrentCell(row, 0)
                item = self.orders_table.item(row, 0)
                if item is not None:
                    self.orders_table.scrollToItem(item)
                return

    def _selected_or_loaded_order_id(self) -> int | None:
        return self._selected_order_id() or self.current_order_id

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
