from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..models import Customer
from ..schemas import CustomerCreate
from ..services.customer_service import (
    archive_customer,
    create_customer,
    list_customers,
    restore_customer,
    update_customer,
)
from .date_input import DateInput, to_display_date


CUSTOMER_PANEL_ACTIONS = {
    "saveCustomerButton": "Kunde speichern",
    "refreshCustomersButton": "Kundenliste laden",
    "loadCustomerButton": "Auswahl bearbeiten",
    "archiveCustomerButton": "Kunde archivieren",
    "restoreCustomerButton": "Kunde wiederherstellen",
    "chooseCustomerFolderButton": "Ordner waehlen",
}

CUSTOMER_COLUMNS = ("Name", "Adresse", "Zahlungsart", "Naechster Kontakt", "Status")
CUSTOMER_PANEL_SECTIONS = ("1. Kunden erfassen", "2. Bestehende Kunden pruefen")
CUSTOMER_GUIDANCE_STEPS = (
    "Neuen Kunden links eintragen oder unten einen Kunden auswaehlen.",
    "Mit Auswahl bearbeiten Stammdaten in das Formular laden.",
    "Archivieren statt loeschen, damit versehentliche Aenderungen rueckgaengig bleiben.",
)
DATE_FIELD_WIDGETS = ("next_contact_date",)


class CustomerPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.current_customer_id = None
        self.customer_ids_by_row = {}

        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("z. B. Cafe Nord")
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText("Kundenordner")
        self.address = QLineEdit()
        self.payment_method = QLineEdit()
        self.payment_method.setPlaceholderText("SEPA oder Ueberweisung")
        self.next_contact_date = DateInput()
        self.delivery_notes = QLineEdit()
        self.status_label = QLabel("Noch kein Kunde gespeichert.")
        self.status_label.setObjectName("muted")
        self.customers_table = QTableWidget(0, len(CUSTOMER_COLUMNS))
        self.customers_table.setHorizontalHeaderLabels(CUSTOMER_COLUMNS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        headline = QLabel("Kunden")
        headline.setObjectName("headline")
        layout.addWidget(headline)

        muted = QLabel("Stammdaten, Lieferhinweise und Kontakttermine")
        muted.setObjectName("muted")
        layout.addWidget(muted)

        layout.addWidget(self._guidance_box())

        workspace = QHBoxLayout()
        workspace.setSpacing(18)
        left_column = QVBoxLayout()
        right_column = QVBoxLayout()
        workspace.addLayout(left_column, 1)
        workspace.addLayout(right_column, 1)
        layout.addLayout(workspace)

        edit_box, edit_layout = self._section(
            CUSTOMER_PANEL_SECTIONS[0],
            "Pflicht ist der Kundenname. Ordner, Zahlungsart und Kontakttermin helfen spaeter beim Tagesablauf.",
        )
        form = QFormLayout()
        form.addRow("Kunde", self.customer_name)
        form.addRow("Kundenordner", self._folder_row())
        form.addRow("Adresse", self.address)
        form.addRow("Zahlungsart", self.payment_method)
        form.addRow("Naechster Kontakt", self.next_contact_date)
        form.addRow("Lieferhinweise", self.delivery_notes)
        edit_layout.addLayout(form)

        action_row = QHBoxLayout()
        self.save_button = self._button("saveCustomerButton")
        self.load_button = self._button("loadCustomerButton")
        action_row.addWidget(self.save_button)
        action_row.addWidget(self.load_button)
        action_row.addStretch()
        edit_layout.addLayout(action_row)
        left_column.addWidget(edit_box)

        list_box, list_layout = self._section(
            CUSTOMER_PANEL_SECTIONS[1],
            "Kunden unten anklicken. Archivieren blendet sie aus dem Alltag aus, Wiederherstellen holt sie zurueck.",
        )
        list_actions = QHBoxLayout()
        self.refresh_button = self._button("refreshCustomersButton")
        self.archive_button = self._button("archiveCustomerButton")
        self.restore_button = self._button("restoreCustomerButton")
        for button in (
            self.refresh_button,
            self.archive_button,
            self.restore_button,
        ):
            list_actions.addWidget(button)
        list_actions.addStretch()
        list_layout.addLayout(list_actions)
        list_layout.addWidget(self.customers_table)
        right_column.addWidget(list_box)

        layout.addWidget(self.status_label)

        self.save_button.clicked.connect(self.save_customer)
        self.refresh_button.clicked.connect(self.refresh_customers)
        self.load_button.clicked.connect(self.load_selected_customer)
        self.archive_button.clicked.connect(self.archive_selected_customer)
        self.restore_button.clicked.connect(self.restore_selected_customer)
        self.customers_table.itemDoubleClicked.connect(lambda _item: self.load_selected_customer())
        self.refresh_customers()

    def _folder_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.folder_path)
        self.choose_folder_button = self._button("chooseCustomerFolderButton")
        self.choose_folder_button.clicked.connect(self.choose_folder)
        layout.addWidget(self.choose_folder_button)
        return row

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(CUSTOMER_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def _guidance_box(self) -> QWidget:
        box = QWidget()
        box.setObjectName("guidanceBox")
        layout = QVBoxLayout(box)
        layout.setSpacing(8)
        title = QLabel("So pflegen Sie Kunden")
        title.setObjectName("stepTitle")
        layout.addWidget(title)
        for index, step in enumerate(CUSTOMER_GUIDANCE_STEPS, start=1):
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

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Kundenordner waehlen")
        if folder:
            self.folder_path.setText(folder)

    def save_customer(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        payload = self._payload_from_form()
        session = self.session_factory()
        try:
            if self.current_customer_id is None:
                customer = create_customer(session, payload)
            else:
                customer = update_customer(session, self.current_customer_id, payload)
            self.current_customer_id = customer.id
            self.status_label.setText(f"Kunde gespeichert: {customer.name}")
            self.show_customers(list_customers(session))
        finally:
            session.close()

    def refresh_customers(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        session = self.session_factory()
        try:
            self.show_customers(list_customers(session))
        finally:
            session.close()

    def show_customers(self, customers: list) -> None:
        self.customer_ids_by_row = {}
        self.customers_table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            self.customer_ids_by_row[row] = customer.id
            values = (
                customer.name,
                customer.address or "",
                customer.payment_method or "",
                to_display_date(customer.next_contact_date),
                "aktiv" if customer.is_active else "archiviert",
            )
            for column, value in enumerate(values):
                self.customers_table.setItem(row, column, QTableWidgetItem(value))
        self.status_label.setText(f"{len(customers)} Kunden geladen.")

    def load_selected_customer(self) -> None:
        customer_id = self._selected_customer_id()
        if customer_id is None or self.session_factory is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswaehlen.")
            return

        session = self.session_factory()
        try:
            customer = session.get(Customer, customer_id)
            if customer is None:
                self.status_label.setText("Kunde wurde nicht gefunden.")
                return
            self.current_customer_id = customer.id
            self.customer_name.setText(customer.name)
            self.folder_path.setText(customer.folder_path)
            self.address.setText(customer.address or "")
            self.payment_method.setText(customer.payment_method or "")
            self.next_contact_date.set_iso_date(customer.next_contact_date)
            self.delivery_notes.setText(customer.delivery_notes or "")
            self.status_label.setText(f"Kunde geladen: {customer.name}")
        finally:
            session.close()

    def archive_selected_customer(self) -> None:
        self._set_selected_customer_active(False)

    def restore_selected_customer(self) -> None:
        self._set_selected_customer_active(True)

    def _set_selected_customer_active(self, active: bool) -> None:
        customer_id = self._selected_customer_id()
        if customer_id is None or self.session_factory is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswaehlen.")
            return

        session = self.session_factory()
        try:
            customer = restore_customer(session, customer_id) if active else archive_customer(session, customer_id)
            self.show_customers(list_customers(session))
            action = "wiederhergestellt" if active else "archiviert"
            self.status_label.setText(f"Kunde {action}: {customer.name}")
        finally:
            session.close()

    def _selected_customer_id(self) -> int | None:
        row = self.customers_table.currentRow()
        return self.customer_ids_by_row.get(row)

    def _payload_from_form(self) -> CustomerCreate:
        return CustomerCreate(
            name=self.customer_name.text().strip(),
            folder_path=self.folder_path.text().strip(),
            address=self.address.text().strip() or None,
            payment_method=self.payment_method.text().strip() or None,
            next_contact_date=self.next_contact_date.iso_date() or None,
            delivery_notes=self.delivery_notes.text().strip() or None,
        )
