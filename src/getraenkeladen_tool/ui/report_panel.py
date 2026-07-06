from pathlib import Path
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .date_input import DateInput, to_display_date
from .layouts import (
    ContentSurface,
    InspectorPanel,
    PageHeader,
    ResponsiveSplitter,
    WorkspaceCard,
    configure_form_layout,
    set_equal_button_widths,
)
from ..services.report_service import (
    export_daily_deliveries_csv,
    export_due_contacts_csv,
    export_open_items_csv,
    list_daily_deliveries,
    list_due_contacts,
    list_invoice_worklist,
    mark_open_item_partially_paid,
    mark_open_item_paid,
)
from ..services.sample_data_service import seed_demo_workflow


REPORT_PANEL_ACTIONS = {
    "seedDemoDataButton": "Beispieldaten anlegen",
    "refreshOpenItemsButton": "Aktualisieren",
    "markPaidButton": "Bezahlt",
    "markPartialButton": "Teilzahlung",
    "refreshDeliveriesButton": "Lieferliste laden",
    "refreshContactsButton": "Kontaktliste laden",
    "exportOpenItemsButton": "Exportieren",
    "exportDeliveriesButton": "Lieferliste exportieren",
    "exportContactsButton": "Kontaktliste exportieren",
}

OPEN_ITEMS_COLUMNS = ("Kunde", "Rechnungsnr.", "Datum", "Fälligkeit", "Zahlart", "Betrag", "Status")
DELIVERY_COLUMNS = ("Datum", "Zeitfenster", "Belegnr.", "Kunde", "Adresse", "Hinweise")
CONTACT_COLUMNS = ("Kontakttermin", "Kunde", "E-Mail", "Hinweise")
DATE_FIELD_WIDGETS = ("target_date",)


class ReportPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.open_item_ids_by_row = {}
        self.open_items_by_row = {}

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout
        layout.addWidget(PageHeader("Rechnungen", "Offene Rechnungen, Fälligkeiten und Zahlungseingänge prüfen."))

        self.target_date = DateInput(date.today().isoformat())
        form = QFormLayout()
        configure_form_layout(form)
        form.addRow("Stichtag", self.target_date)
        self.invoice_status_filter = QComboBox()
        self.invoice_status_filter.addItem("Alle offenen", "alle")
        self.invoice_status_filter.addItem("Fällig", "faellig")
        self.invoice_status_filter.addItem("Überfällig", "überfällig")
        self.invoice_status_filter.addItem("Teilbezahlt", "teilbezahlt")
        self.invoice_status_filter.addItem("Normal offen", "offen")
        form.addRow("Rechnungen", self.invoice_status_filter)
        filter_box = WorkspaceCard(
            "Filter",
            "Stichtag für Lieferungen und Wiedervorlagen wählen.",
            tone="route",
            kicker="STICHTAG",
        )
        filter_box.layout.addLayout(form)
        layout.addWidget(filter_box)

        invoice_splitter = ResponsiveSplitter(Qt.Orientation.Vertical)
        layout.addWidget(invoice_splitter, 2)

        self.open_items_table = QTableWidget(0, len(OPEN_ITEMS_COLUMNS))
        self.open_items_table.setHorizontalHeaderLabels(OPEN_ITEMS_COLUMNS)
        self.open_items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.open_items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.open_items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.open_items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.open_items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.open_items_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.open_items_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        open_items_box = WorkspaceCard(
            "Rechnungsliste",
            "Offene und fällige Rechnungen nach Status prüfen.",
            tone="cash",
            kicker="KASSE",
        )
        open_items_box.layout.addWidget(self.open_items_table)
        invoice_splitter.addWidget(open_items_box)

        self.invoice_customer_label = QLabel("Kunde: -")
        self.invoice_number_label = QLabel("Rechnung: -")
        self.invoice_due_label = QLabel("Fälligkeit: -")
        self.invoice_payment_label = QLabel("Zahlart: -")
        self.invoice_amount_label = QLabel("Betrag: -")
        self.invoice_status_label = QLabel("Status: -")
        for label in (
            self.invoice_customer_label,
            self.invoice_number_label,
            self.invoice_due_label,
            self.invoice_payment_label,
            self.invoice_amount_label,
            self.invoice_status_label,
        ):
            label.setObjectName("inspectorValue")
            label.setWordWrap(True)

        self.invoice_inspector = InspectorPanel("Rechnung auswählen", "Details und nächster Zahlungsschritt erscheinen hier.")
        self.invoice_inspector.setMaximumWidth(16777215)
        self.invoice_inspector.add_section_label("Rechnung")
        self.invoice_inspector.body.addWidget(self.invoice_customer_label)
        self.invoice_inspector.body.addWidget(self.invoice_number_label)
        self.invoice_inspector.body.addWidget(self.invoice_due_label)
        self.invoice_inspector.body.addWidget(self.invoice_payment_label)
        self.invoice_inspector.body.addWidget(self.invoice_amount_label)
        self.invoice_inspector.body.addWidget(self.invoice_status_label)
        self.invoice_inspector.add_section_label("Aktionen")
        self.mark_paid_button = self._button("markPaidButton")
        self.mark_partial_button = self._button("markPartialButton")
        self.export_open_items_button = self._button("exportOpenItemsButton")
        invoice_action_row = QHBoxLayout()
        invoice_action_row.addWidget(self.mark_paid_button)
        invoice_action_row.addWidget(self.mark_partial_button)
        invoice_action_row.addWidget(self.export_open_items_button)
        invoice_action_row.addStretch()
        self.invoice_inspector.body.addLayout(invoice_action_row)
        invoice_splitter.addWidget(self.invoice_inspector)
        invoice_splitter.setStretchFactor(0, 4)
        invoice_splitter.setStretchFactor(1, 1)

        self.secondary_lists_tabs = QTabWidget()
        self.secondary_lists_tabs.setUsesScrollButtons(False)

        self.deliveries_table = QTableWidget(0, len(DELIVERY_COLUMNS))
        self.deliveries_table.setHorizontalHeaderLabels(DELIVERY_COLUMNS)
        self.deliveries_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.deliveries_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.deliveries_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.deliveries_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.deliveries_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.deliveries_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        deliveries_box = WorkspaceCard("Tageslieferungen", "Nebenliste für Tour und Export.", tone="route", kicker="TOUR")
        deliveries_box.layout.addWidget(self.deliveries_table)

        self.contacts_table = QTableWidget(0, len(CONTACT_COLUMNS))
        self.contacts_table.setHorizontalHeaderLabels(CONTACT_COLUMNS)
        self.contacts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        contacts_box = WorkspaceCard("Kontaktliste", "Nebenliste für Wiedervorlagen und Export.", tone="audit", kicker="WIEDERVORLAGE")
        contacts_box.layout.addWidget(self.contacts_table)

        action_row = QHBoxLayout()
        self.seed_button = self._button("seedDemoDataButton")
        self.refresh_button = self._button("refreshOpenItemsButton")
        self.refresh_deliveries_button = self._button("refreshDeliveriesButton")
        self.refresh_contacts_button = self._button("refreshContactsButton")
        self.seed_button.setVisible(False)
        self.refresh_button.setMinimumWidth(220)
        set_equal_button_widths((self.refresh_deliveries_button, self.refresh_contacts_button), 190)
        action_row.addWidget(self.refresh_button)
        action_row.addStretch()
        layout.addLayout(action_row)

        demo_row = QHBoxLayout()
        demo_row.addWidget(self.seed_button)
        demo_row.addStretch()
        layout.addLayout(demo_row)

        export_row = QHBoxLayout()
        self.export_deliveries_button = self._button("exportDeliveriesButton")
        self.export_contacts_button = self._button("exportContactsButton")
        set_equal_button_widths((self.export_deliveries_button, self.export_contacts_button), 190)
        deliveries_box.layout.addWidget(self.refresh_deliveries_button)
        deliveries_box.layout.addWidget(self.export_deliveries_button)
        contacts_box.layout.addWidget(self.refresh_contacts_button)
        contacts_box.layout.addWidget(self.export_contacts_button)
        export_row.addStretch()
        self.secondary_lists_tabs.addTab(deliveries_box, "Tageslieferungen")
        self.secondary_lists_tabs.addTab(contacts_box, "Kontaktliste")
        secondary_box = WorkspaceCard(
            "Nebenlisten",
            "Tour und Kontakte sind abrufbar, dominieren aber nicht mehr die Rechnungsarbeit.",
            tone="route",
            kicker="OPTIONAL",
        )
        secondary_box.layout.addWidget(self.secondary_lists_tabs)
        layout.addWidget(secondary_box)

        self.status_label = QLabel("Noch keine Listen geladen.")
        self.status_label.setObjectName("muted")
        layout.addWidget(self.status_label)

        self.seed_button.clicked.connect(self.seed_demo_data)
        self.refresh_button.clicked.connect(self.refresh_open_items)
        self.mark_paid_button.clicked.connect(self.mark_selected_paid)
        self.mark_partial_button.clicked.connect(self.mark_selected_partially_paid)
        self.refresh_deliveries_button.clicked.connect(self.refresh_deliveries)
        self.refresh_contacts_button.clicked.connect(self.refresh_contacts)
        self.export_open_items_button.clicked.connect(self.export_open_items)
        self.export_deliveries_button.clicked.connect(self.export_deliveries)
        self.export_contacts_button.clicked.connect(self.export_contacts)
        self.open_items_table.itemSelectionChanged.connect(self.update_invoice_context)
        self.invoice_status_filter.currentIndexChanged.connect(self.refresh_open_items)
        self.mark_paid_button.setEnabled(False)
        self.mark_partial_button.setEnabled(False)
        self.refresh_all_lists()

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(REPORT_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def seed_demo_data(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        session = self.session_factory()
        try:
            result = seed_demo_workflow(session, self._outputs_dir(), self._target_date())
            self.show_open_items(list_invoice_worklist(session, self._invoice_status_filter(), self._target_date()))
            self.show_deliveries(list_daily_deliveries(session, self._target_date()))
            self.show_contacts(list_due_contacts(session, self._target_date()))
            self.status_label.setText(
                "Beispieldaten angelegt: "
                f"{result.created_customers} Kunden, {result.created_products} Produkte, "
                f"{result.created_orders} Bestellungen, "
                f"{result.created_documents} Belege."
            )
        finally:
            session.close()

    def show_open_items(self, open_items: list) -> None:
        self.open_item_ids_by_row = {}
        self.open_items_by_row = {}
        self.open_items_table.setRowCount(len(open_items))
        for row, item in enumerate(open_items):
            self.open_item_ids_by_row[row] = item.id
            self.open_items_by_row[row] = item
            amount = f"{item.amount_cents / 100:.2f} EUR".replace(".", ",")
            values = (
                item.customer_name,
                item.document_number,
                to_display_date(item.document_date),
                to_display_date(item.due_date),
                item.payment_method,
                amount,
                item.status,
            )
            self._set_row(self.open_items_table, row, values)
        self.update_invoice_context()
        self.status_label.setText(f"{len(open_items)} Rechnungen offen.")

    def show_deliveries(self, deliveries: list) -> None:
        self.deliveries_table.setRowCount(len(deliveries))
        for row, document in enumerate(deliveries):
            values = (
                to_display_date(document.delivery_date),
                document.delivery_slot or "",
                document.document_number,
                document.customer.name,
                document.customer.address or "",
                document.customer.delivery_notes or "",
            )
            self._set_row(self.deliveries_table, row, values)
        self.status_label.setText(f"{len(deliveries)} Tageslieferungen geladen.")

    def show_contacts(self, contacts: list) -> None:
        self.contacts_table.setRowCount(len(contacts))
        for row, customer in enumerate(contacts):
            values = (
                to_display_date(customer.next_contact_date),
                customer.name,
                customer.contact_email or "",
                customer.delivery_notes or "",
            )
            self._set_row(self.contacts_table, row, values)
        self.status_label.setText(f"{len(contacts)} Kontakte geladen.")

    def refresh_open_items(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        session = self.session_factory()
        try:
            self.show_open_items(list_invoice_worklist(session, self._invoice_status_filter(), self._target_date()))
        finally:
            session.close()

    def refresh_deliveries(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        session = self.session_factory()
        try:
            self.show_deliveries(list_daily_deliveries(session, self._target_date()))
        finally:
            session.close()

    def refresh_contacts(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        session = self.session_factory()
        try:
            self.show_contacts(list_due_contacts(session, self._target_date()))
        finally:
            session.close()

    def mark_selected_paid(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        row = self.open_items_table.currentRow()
        open_item_id = self.open_item_ids_by_row.get(row)
        if open_item_id is None:
            self.status_label.setText("Bitte zuerst eine Rechnung auswählen.")
            return
        item = self.open_items_by_row.get(row)
        invoice_text = getattr(item, "document_number", "diese Rechnung")
        answer = QMessageBox.question(
            self,
            "Zahlung markieren",
            "Diese Rechnung wirklich als bezahlt markieren?\n\n"
            f"Rechnung: {invoice_text}\n"
            "Die offene-Posten-Liste wird danach aktualisiert.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.status_label.setText("Zahlung nicht geändert.")
            return

        session = self.session_factory()
        try:
            mark_open_item_paid(session, open_item_id)
            self.show_open_items(list_invoice_worklist(session, self._invoice_status_filter(), self._target_date()))
            self._select_open_item_by_id(open_item_id)
            self.status_label.setText("Rechnung als bezahlt markiert.")
        finally:
            session.close()

    def mark_selected_partially_paid(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        row = self.open_items_table.currentRow()
        open_item_id = self.open_item_ids_by_row.get(row)
        if open_item_id is None:
            self.status_label.setText("Bitte zuerst eine Rechnung auswählen.")
            return
        session = self.session_factory()
        try:
            mark_open_item_partially_paid(session, open_item_id)
            self.show_open_items(list_invoice_worklist(session, self._invoice_status_filter(), self._target_date()))
            self._select_open_item_by_id(open_item_id)
            self.status_label.setText("Rechnung als teilbezahlt markiert.")
        finally:
            session.close()

    def export_open_items(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        output_path = self._list_path("offene_posten.csv")
        session = self.session_factory()
        try:
            export_open_items_csv(session, output_path)
            self.status_label.setText(f"Rechnungen exportiert: {output_path}")
        finally:
            session.close()

    def export_deliveries(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        output_path = self._list_path(f"lieferliste_{self._target_date()}.csv")
        session = self.session_factory()
        try:
            export_daily_deliveries_csv(session, self._target_date(), output_path)
            self.status_label.setText(f"Lieferliste exportiert: {output_path}")
        finally:
            session.close()

    def export_contacts(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        output_path = self._list_path(f"kontaktliste_{self._target_date()}.csv")
        session = self.session_factory()
        try:
            export_due_contacts_csv(session, self._target_date(), output_path)
            self.status_label.setText(f"Kontaktliste exportiert: {output_path}")
        finally:
            session.close()

    def _set_row(self, table: QTableWidget, row: int, values: tuple[str, ...]) -> None:
        for column, value in enumerate(values):
            table.setItem(row, column, QTableWidgetItem(value))

    def _outputs_dir(self) -> Path:
        return Path.cwd() / "outputs"

    def _list_path(self, filename: str) -> Path:
        return self._outputs_dir() / "listen" / filename

    def refresh_all_lists(self) -> None:
        self.refresh_open_items()
        self.refresh_deliveries()
        self.refresh_contacts()

    def _target_date(self) -> str:
        return self.target_date.iso_date() or date.today().isoformat()

    def _invoice_status_filter(self) -> str:
        return self.invoice_status_filter.currentData() or "alle"

    def update_invoice_context(self) -> None:
        item = self.open_items_by_row.get(self.open_items_table.currentRow())
        if item is None:
            self.invoice_inspector.set_heading(
                "Rechnung auswählen",
                "Details und nächster Zahlungsschritt erscheinen hier.",
            )
            self.invoice_customer_label.setText("Kunde: -")
            self.invoice_number_label.setText("Rechnung: -")
            self.invoice_due_label.setText("Fälligkeit: -")
            self.invoice_payment_label.setText("Zahlart: -")
            self.invoice_amount_label.setText("Betrag: -")
            self.invoice_status_label.setText("Status: -")
            self.mark_paid_button.setEnabled(False)
            self.mark_partial_button.setEnabled(False)
            return

        amount = f"{item.amount_cents / 100:.2f} EUR".replace(".", ",")
        self.invoice_inspector.set_heading(item.document_number, item.customer_name)
        self.invoice_customer_label.setText(f"Kunde: {item.customer_name}")
        self.invoice_number_label.setText(f"Rechnung: {item.document_number}")
        self.invoice_due_label.setText(f"Fälligkeit: {to_display_date(item.due_date) or '-'}")
        self.invoice_payment_label.setText(f"Zahlart: {item.payment_method}")
        self.invoice_amount_label.setText(f"Betrag: {amount}")
        self.invoice_status_label.setText(f"Status: {item.status}")
        self.mark_paid_button.setEnabled(item.status != "bezahlt")
        self.mark_partial_button.setEnabled(item.status == "offen")

    def _select_open_item_by_id(self, open_item_id: int) -> None:
        for row, candidate_id in self.open_item_ids_by_row.items():
            if candidate_id == open_item_id:
                self.open_items_table.setCurrentCell(row, 0)
                return
        self.open_items_table.clearSelection()
        self.update_invoice_context()
