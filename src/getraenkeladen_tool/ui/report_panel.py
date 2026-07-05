from pathlib import Path
from datetime import date

from PySide6.QtWidgets import (
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
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
    list_open_items,
    mark_open_item_paid,
)
from ..services.sample_data_service import seed_demo_workflow


REPORT_PANEL_ACTIONS = {
    "seedDemoDataButton": "Beispieldaten anlegen",
    "refreshOpenItemsButton": "Rechnungen aktualisieren",
    "markPaidButton": "Als bezahlt markieren",
    "refreshDeliveriesButton": "Lieferliste laden",
    "refreshContactsButton": "Kontaktliste laden",
    "exportOpenItemsButton": "Rechnungen exportieren",
    "exportDeliveriesButton": "Lieferliste exportieren",
    "exportContactsButton": "Kontaktliste exportieren",
}

OPEN_ITEMS_COLUMNS = ("Kunde", "Rechnungsnr.", "Datum", "Faelligkeit", "Zahlart", "Betrag", "Status")
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
        layout.addWidget(PageHeader("Rechnungen", "Offene Rechnungen, Faelligkeiten und Zahlungseingaenge pruefen."))

        self.target_date = DateInput(date.today().isoformat())
        form = QFormLayout()
        configure_form_layout(form)
        form.addRow("Stichtag", self.target_date)
        filter_box = WorkspaceCard(
            "Filter",
            "Stichtag fuer Lieferungen und Wiedervorlagen waehlen.",
            tone="route",
            kicker="STICHTAG",
        )
        filter_box.layout.addLayout(form)
        layout.addWidget(filter_box)

        invoice_splitter = ResponsiveSplitter()
        layout.addWidget(invoice_splitter, 2)

        self.open_items_table = QTableWidget(0, len(OPEN_ITEMS_COLUMNS))
        self.open_items_table.setHorizontalHeaderLabels(OPEN_ITEMS_COLUMNS)
        self.open_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        open_items_box = WorkspaceCard(
            "Rechnungsliste",
            "Offene und faellige Rechnungen nach Status pruefen.",
            tone="cash",
            kicker="KASSE",
        )
        open_items_box.layout.addWidget(self.open_items_table)
        invoice_splitter.addWidget(open_items_box)

        self.invoice_customer_label = QLabel("Kunde: -")
        self.invoice_number_label = QLabel("Rechnung: -")
        self.invoice_due_label = QLabel("Faelligkeit: -")
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

        self.invoice_inspector = InspectorPanel("Rechnung auswaehlen", "Details und naechster Zahlungsschritt erscheinen hier.")
        self.invoice_inspector.add_section_label("Rechnung")
        self.invoice_inspector.body.addWidget(self.invoice_customer_label)
        self.invoice_inspector.body.addWidget(self.invoice_number_label)
        self.invoice_inspector.body.addWidget(self.invoice_due_label)
        self.invoice_inspector.body.addWidget(self.invoice_payment_label)
        self.invoice_inspector.body.addWidget(self.invoice_amount_label)
        self.invoice_inspector.body.addWidget(self.invoice_status_label)
        self.invoice_inspector.add_section_label("Aktionen")
        self.mark_paid_button = self._button("markPaidButton")
        self.export_open_items_button = self._button("exportOpenItemsButton")
        set_equal_button_widths((self.mark_paid_button, self.export_open_items_button), 260)
        self.invoice_inspector.body.addWidget(self.mark_paid_button)
        self.invoice_inspector.body.addWidget(self.export_open_items_button)
        invoice_splitter.addWidget(self.invoice_inspector)
        invoice_splitter.setStretchFactor(0, 3)
        invoice_splitter.setStretchFactor(1, 1)

        self.deliveries_table = QTableWidget(0, len(DELIVERY_COLUMNS))
        self.deliveries_table.setHorizontalHeaderLabels(DELIVERY_COLUMNS)
        self.deliveries_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        deliveries_box = WorkspaceCard("Tageslieferungen", tone="route", kicker="TOUR")
        deliveries_box.layout.addWidget(self.deliveries_table)
        layout.addWidget(deliveries_box)

        self.contacts_table = QTableWidget(0, len(CONTACT_COLUMNS))
        self.contacts_table.setHorizontalHeaderLabels(CONTACT_COLUMNS)
        self.contacts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        contacts_box = WorkspaceCard("Kontaktliste", tone="audit", kicker="WIEDERVORLAGE")
        contacts_box.layout.addWidget(self.contacts_table)
        layout.addWidget(contacts_box)

        action_row = QHBoxLayout()
        self.seed_button = self._button("seedDemoDataButton")
        self.refresh_button = self._button("refreshOpenItemsButton")
        self.refresh_deliveries_button = self._button("refreshDeliveriesButton")
        self.refresh_contacts_button = self._button("refreshContactsButton")
        set_equal_button_widths((self.refresh_button, self.refresh_deliveries_button, self.refresh_contacts_button), 190)
        for button in (self.refresh_button, self.refresh_deliveries_button, self.refresh_contacts_button):
            action_row.addWidget(button)
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
        export_row.addWidget(self.export_deliveries_button)
        export_row.addWidget(self.export_contacts_button)
        export_row.addStretch()
        layout.addLayout(export_row)

        self.status_label = QLabel("Noch keine Listen geladen.")
        self.status_label.setObjectName("muted")
        layout.addWidget(self.status_label)

        self.seed_button.clicked.connect(self.seed_demo_data)
        self.refresh_button.clicked.connect(self.refresh_open_items)
        self.mark_paid_button.clicked.connect(self.mark_selected_paid)
        self.refresh_deliveries_button.clicked.connect(self.refresh_deliveries)
        self.refresh_contacts_button.clicked.connect(self.refresh_contacts)
        self.export_open_items_button.clicked.connect(self.export_open_items)
        self.export_deliveries_button.clicked.connect(self.export_deliveries)
        self.export_contacts_button.clicked.connect(self.export_contacts)
        self.open_items_table.itemSelectionChanged.connect(self.update_invoice_context)
        self.mark_paid_button.setEnabled(False)
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
            self.show_open_items(list_open_items(session))
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
            self.show_open_items(list_open_items(session))
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
            self.status_label.setText("Bitte zuerst eine Rechnung auswaehlen.")
            return

        session = self.session_factory()
        try:
            mark_open_item_paid(session, open_item_id)
            self.show_open_items(list_open_items(session))
            self.status_label.setText("Rechnung als bezahlt markiert.")
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

    def update_invoice_context(self) -> None:
        item = self.open_items_by_row.get(self.open_items_table.currentRow())
        if item is None:
            self.invoice_inspector.set_heading(
                "Rechnung auswaehlen",
                "Details und naechster Zahlungsschritt erscheinen hier.",
            )
            self.invoice_customer_label.setText("Kunde: -")
            self.invoice_number_label.setText("Rechnung: -")
            self.invoice_due_label.setText("Faelligkeit: -")
            self.invoice_payment_label.setText("Zahlart: -")
            self.invoice_amount_label.setText("Betrag: -")
            self.invoice_status_label.setText("Status: -")
            self.mark_paid_button.setEnabled(False)
            return

        amount = f"{item.amount_cents / 100:.2f} EUR".replace(".", ",")
        self.invoice_inspector.set_heading(item.document_number, item.customer_name)
        self.invoice_customer_label.setText(f"Kunde: {item.customer_name}")
        self.invoice_number_label.setText(f"Rechnung: {item.document_number}")
        self.invoice_due_label.setText(f"Faelligkeit: {to_display_date(item.due_date) or '-'}")
        self.invoice_payment_label.setText(f"Zahlart: {item.payment_method}")
        self.invoice_amount_label.setText(f"Betrag: {amount}")
        self.invoice_status_label.setText(f"Status: {item.status}")
        self.mark_paid_button.setEnabled(item.status != "bezahlt")
