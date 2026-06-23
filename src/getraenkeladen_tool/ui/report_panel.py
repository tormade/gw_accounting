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
from .layouts import ContentSurface, PageHeader, WorkspaceCard, configure_form_layout
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
    "refreshOpenItemsButton": "Offene Posten aktualisieren",
    "markPaidButton": "Zahlung markieren",
    "refreshDeliveriesButton": "Lieferliste laden",
    "refreshContactsButton": "Kontaktliste laden",
    "exportOpenItemsButton": "Offene Posten exportieren",
    "exportDeliveriesButton": "Lieferliste exportieren",
    "exportContactsButton": "Kontaktliste exportieren",
}

OPEN_ITEMS_COLUMNS = ("Kunde", "Rechnungsnr.", "Betrag", "Status")
DELIVERY_COLUMNS = ("Datum", "Zeitfenster", "Belegnr.", "Kunde", "Adresse", "Hinweise")
CONTACT_COLUMNS = ("Kontakttermin", "Kunde", "E-Mail", "Hinweise")
DATE_FIELD_WIDGETS = ("target_date",)


class ReportPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.open_item_ids_by_row = {}

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout
        layout.addWidget(PageHeader("Listen", "Offene Posten, Tageslieferungen und Kontaktliste."))

        self.target_date = DateInput(date.today().isoformat())
        form = QFormLayout()
        configure_form_layout(form)
        form.addRow("Stichtag", self.target_date)
        filter_box = WorkspaceCard("Auswertung", "Stichtag waehlen und die Listen darunter aktualisieren.")
        filter_box.layout.addLayout(form)
        layout.addWidget(filter_box)

        self.open_items_table = QTableWidget(0, len(OPEN_ITEMS_COLUMNS))
        self.open_items_table.setHorizontalHeaderLabels(OPEN_ITEMS_COLUMNS)
        self.open_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        open_items_box = WorkspaceCard("Offene Posten")
        open_items_box.layout.addWidget(self.open_items_table)
        layout.addWidget(open_items_box)

        self.deliveries_table = QTableWidget(0, len(DELIVERY_COLUMNS))
        self.deliveries_table.setHorizontalHeaderLabels(DELIVERY_COLUMNS)
        self.deliveries_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        deliveries_box = WorkspaceCard("Tageslieferungen")
        deliveries_box.layout.addWidget(self.deliveries_table)
        layout.addWidget(deliveries_box)

        self.contacts_table = QTableWidget(0, len(CONTACT_COLUMNS))
        self.contacts_table.setHorizontalHeaderLabels(CONTACT_COLUMNS)
        self.contacts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        contacts_box = WorkspaceCard("Kontaktliste")
        contacts_box.layout.addWidget(self.contacts_table)
        layout.addWidget(contacts_box)

        action_row = QHBoxLayout()
        self.seed_button = self._button("seedDemoDataButton")
        self.refresh_button = self._button("refreshOpenItemsButton")
        self.mark_paid_button = self._button("markPaidButton")
        self.refresh_deliveries_button = self._button("refreshDeliveriesButton")
        self.refresh_contacts_button = self._button("refreshContactsButton")
        for button in (
            self.seed_button,
            self.refresh_button,
            self.mark_paid_button,
            self.refresh_deliveries_button,
            self.refresh_contacts_button,
        ):
            action_row.addWidget(button)
        action_row.addStretch()
        layout.addLayout(action_row)

        export_row = QHBoxLayout()
        self.export_open_items_button = self._button("exportOpenItemsButton")
        self.export_deliveries_button = self._button("exportDeliveriesButton")
        self.export_contacts_button = self._button("exportContactsButton")
        export_row.addWidget(self.export_open_items_button)
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
        self.open_items_table.setRowCount(len(open_items))
        for row, item in enumerate(open_items):
            self.open_item_ids_by_row[row] = item.id
            amount = f"{item.amount_cents / 100:.2f} EUR".replace(".", ",")
            values = (
                item.customer_name,
                item.document_number,
                amount,
                item.status,
            )
            self._set_row(self.open_items_table, row, values)
        self.status_label.setText(f"{len(open_items)} offene Posten geladen.")

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
            self.status_label.setText("Bitte zuerst einen offenen Posten auswaehlen.")
            return

        session = self.session_factory()
        try:
            mark_open_item_paid(session, open_item_id)
            self.show_open_items(list_open_items(session))
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
            self.status_label.setText(f"Offene Posten exportiert: {output_path}")
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
