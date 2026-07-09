from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from ..models import Customer
from ..schemas import CustomerCreate
from ..services.customer_service import (
    archive_customer,
    create_customer,
    list_customer_changes,
    list_customers,
    revert_customer_change,
    restore_customer,
    update_customer,
)
from .date_input import DateInput, to_display_date
from .layouts import ContentSurface, PageHeader, WorkspaceCard, configure_form_layout, set_equal_button_widths


CUSTOMER_PANEL_ACTIONS = {
    "newCustomerButton": "Neu",
    "saveCustomerButton": "Kunde speichern",
    "discardCustomerChangesButton": "Verwerfen",
    "undoCustomerChangeButton": "Rückgängig",
    "refreshCustomersButton": "Kundenliste laden",
    "loadCustomerButton": "Auswahl bearbeiten",
    "archiveCustomerButton": "Kunde archivieren",
    "restoreCustomerButton": "Kunde wiederherstellen",
    "chooseCustomerFolderButton": "Ordner wählen",
}
CUSTOMER_COLUMNS = ("Name", "Adresse", "Nächster Kontakt", "Status")
CUSTOMER_PANEL_SECTIONS = ("1. Kunden erfassen", "2. Bestehende Kunden prüfen")
CUSTOMER_GUIDANCE_STEPS = (
    "Neuen Kunden links eintragen oder unten einen Kunden auswählen.",
    "Mit Auswahl bearbeiten Stammdaten in das Formular laden.",
    "Änderungen können vor dem Speichern verworfen werden.",
)
CUSTOMER_CONTEXT_ACTIONS = {
    "edit": "Kunde bearbeiten",
    "archive": "Kunde archivieren",
    "restore": "Kunde wiederherstellen",
}
DATE_FIELD_WIDGETS = ("next_contact_date",)


class CustomerPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.current_customer_id = None
        self.customer_ids_by_row = {}
        self.loaded_form_snapshot = None
        self.has_loaded = False

        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("z. B. Cafe Nord")
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText("Kundenordner")
        self.folder_path.setMinimumWidth(0)
        self.address = QLineEdit()
        self.next_contact_date = DateInput()
        self.delivery_notes = QLineEdit()
        self.status_label = QLabel("Noch kein Kunde gespeichert.")
        self.status_label.setObjectName("muted")
        self.customers_table = QTableWidget(0, len(CUSTOMER_COLUMNS))
        self.customers_table.setHorizontalHeaderLabels(CUSTOMER_COLUMNS)
        self.customers_table.setMinimumHeight(360)
        self.customers_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.customers_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.customers_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.customers_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        layout.addWidget(PageHeader("Kunden", "Stammdaten, Lieferhinweise und Kontakttermine."))
        layout.addWidget(self._guidance_box())

        edit_box, edit_layout = self._section(
            CUSTOMER_PANEL_SECTIONS[0],
            "Pflicht ist der Kundenname. Ordner, Lieferhinweise und Kontakttermin helfen später beim Tagesablauf.",
            tone="route",
            kicker="KUNDENKARTE",
        )
        edit_box.setMaximumHeight(520)
        form = QFormLayout()
        configure_form_layout(form)
        form.addRow("Kunde", self.customer_name)
        form.addRow("Kundenordner", self._folder_row())
        form.addRow("Adresse", self.address)
        form.addRow("Nächster Kontakt", self.next_contact_date)
        form.addRow("Lieferhinweise", self.delivery_notes)
        edit_layout.addLayout(form)

        action_row = QHBoxLayout()
        self.new_button = self._button("newCustomerButton")
        self.save_button = self._button("saveCustomerButton")
        self.discard_button = self._button("discardCustomerChangesButton")
        self.undo_change_button = self._button("undoCustomerChangeButton")
        self.load_button = self._button("loadCustomerButton")
        set_equal_button_widths((self.new_button, self.save_button, self.load_button), 170)
        set_equal_button_widths((self.discard_button, self.undo_change_button), 170)
        action_row.addWidget(self.new_button)
        action_row.addWidget(self.save_button)
        action_row.addWidget(self.load_button)
        action_row.addStretch()
        edit_layout.addLayout(action_row)
        correction_row = QHBoxLayout()
        correction_row.addWidget(self.discard_button)
        correction_row.addWidget(self.undo_change_button)
        correction_row.addStretch()
        edit_layout.addLayout(correction_row)
        list_box, list_layout = self._section(
            CUSTOMER_PANEL_SECTIONS[1],
            "Kunden unten anklicken. Archivieren blendet sie aus dem Alltag aus, Wiederherstellen holt sie zurück.",
            tone="document",
            kicker="KUNDENSTAMM",
        )
        list_actions = QHBoxLayout()
        self.refresh_button = self._button("refreshCustomersButton")
        self.archive_button = self._button("archiveCustomerButton")
        self.restore_button = self._button("restoreCustomerButton")
        set_equal_button_widths((self.refresh_button, self.archive_button, self.restore_button), 170)
        for button in (
            self.refresh_button,
            self.archive_button,
            self.restore_button,
        ):
            list_actions.addWidget(button)
        list_actions.addStretch()
        list_layout.addLayout(list_actions)
        list_layout.addWidget(self.customers_table)
        layout.addWidget(edit_box)
        layout.addWidget(list_box, 1)

        layout.addWidget(self.status_label)

        self.new_button.clicked.connect(self.new_customer)
        self.save_button.clicked.connect(self.save_customer)
        self.discard_button.clicked.connect(self.discard_changes)
        self.undo_change_button.clicked.connect(self.undo_last_change)
        self.refresh_button.clicked.connect(self.refresh_customers)
        self.load_button.clicked.connect(self.load_selected_customer)
        self.archive_button.clicked.connect(self.archive_selected_customer)
        self.restore_button.clicked.connect(self.restore_selected_customer)
        self.customers_table.itemDoubleClicked.connect(lambda _item: self.load_selected_customer())
        self.customers_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customers_table.customContextMenuRequested.connect(self.show_customer_context_menu)

    def ensure_loaded(self) -> None:
        if not self.has_loaded:
            self.refresh_customers()

    def _folder_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.folder_path)
        self.choose_folder_button = self._button("chooseCustomerFolderButton")
        self.choose_folder_button.setFixedWidth(150)
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

    def _section(self, title: str, subtitle: str, tone: str = "default", kicker: str = "") -> tuple[QWidget, QVBoxLayout]:
        box = WorkspaceCard(title, subtitle, tone=tone, kicker=kicker)
        return box, box.layout

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Kundenordner wählen")
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
            self.loaded_form_snapshot = self._snapshot_from_customer(customer)
            self.status_label.setText(f"Erfolgreich gespeichert: Kunde gespeichert: {customer.name}.")
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
            self.has_loaded = True
        finally:
            session.close()

    def show_customers(self, customers: list) -> None:
        self.customer_ids_by_row = {}
        self.customers_table.setUpdatesEnabled(False)
        try:
            self.customers_table.setRowCount(len(customers))
            for row, customer in enumerate(customers):
                self.customer_ids_by_row[row] = customer.id
                values = (
                    customer.name,
                    customer.address or "",
                    to_display_date(customer.next_contact_date),
                    "aktiv" if customer.is_active else "archiviert",
                )
                for column, value in enumerate(values):
                    self.customers_table.setItem(row, column, QTableWidgetItem(value))
        finally:
            self.customers_table.setUpdatesEnabled(True)
        self.status_label.setText(f"{len(customers)} Kunden geladen.")

    def load_selected_customer(self) -> None:
        customer_id = self._selected_customer_id()
        if customer_id is None or self.session_factory is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswählen.")
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
            self.next_contact_date.set_iso_date(customer.next_contact_date)
            self.delivery_notes.setText(customer.delivery_notes or "")
            self.loaded_form_snapshot = self._snapshot_from_customer(customer)
            self.status_label.setText(f"Kunde geladen: {customer.name}")
        finally:
            session.close()

    def archive_selected_customer(self) -> None:
        self._set_selected_customer_active(False)

    def restore_selected_customer(self) -> None:
        self._set_selected_customer_active(True)

    def undo_last_change(self) -> None:
        customer_id = self.current_customer_id or self._selected_customer_id()
        if customer_id is None or self.session_factory is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswählen.")
            return

        session = self.session_factory()
        try:
            changes = [change for change in list_customer_changes(session, customer_id) if change.action != "revert"]
            if not changes:
                self.status_label.setText("Keine Änderung zum Rückgängigmachen gefunden.")
                return
            customer = revert_customer_change(session, changes[0].id)
            self.current_customer_id = customer.id
            self.show_customers(list_customers(session))
            self.loaded_form_snapshot = self._snapshot_from_customer(customer)
            self.status_label.setText(f"Letzte Änderung rückgängig gemacht: {customer.name}")
        finally:
            session.close()

    def _set_selected_customer_active(self, active: bool) -> None:
        customer_id = self._selected_customer_id()
        if customer_id is None or self.session_factory is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswählen.")
            return

        session = self.session_factory()
        try:
            customer = restore_customer(session, customer_id) if active else archive_customer(session, customer_id)
            self.show_customers(list_customers(session))
            self.loaded_form_snapshot = self._snapshot_from_customer(customer)
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
            next_contact_date=self.next_contact_date.iso_date() or None,
            delivery_notes=self.delivery_notes.text().strip() or None,
        )

    def new_customer(self) -> None:
        self.current_customer_id = None
        self.customer_name.clear()
        self.folder_path.clear()
        self.address.clear()
        self.next_contact_date.set_iso_date(None)
        self.delivery_notes.clear()
        self.loaded_form_snapshot = self._form_snapshot()
        self.status_label.setText("Neuer Kunde. Erst Speichern übernimmt die Angaben.")

    def discard_changes(self) -> None:
        if self.loaded_form_snapshot is None:
            self.new_customer()
            return
        self._apply_snapshot(self.loaded_form_snapshot)
        self.status_label.setText("Änderungen verworfen. Der zuletzt geladene Stand ist wiederhergestellt.")

    def show_customer_context_menu(self, position) -> None:
        if self.customers_table.currentRow() < 0:
            return
        menu = QMenu(self)
        edit_action = menu.addAction(CUSTOMER_CONTEXT_ACTIONS["edit"])
        archive_action = menu.addAction(CUSTOMER_CONTEXT_ACTIONS["archive"])
        restore_action = menu.addAction(CUSTOMER_CONTEXT_ACTIONS["restore"])
        selected = menu.exec(self.customers_table.viewport().mapToGlobal(position))
        if selected == edit_action:
            self.load_selected_customer()
        elif selected == archive_action:
            self.archive_selected_customer()
        elif selected == restore_action:
            self.restore_selected_customer()

    def _form_snapshot(self) -> dict:
        return {
            "id": self.current_customer_id,
            "name": self.customer_name.text(),
            "folder_path": self.folder_path.text(),
            "address": self.address.text(),
            "next_contact_date": self.next_contact_date.iso_date(),
            "delivery_notes": self.delivery_notes.text(),
        }

    def _snapshot_from_customer(self, customer: Customer) -> dict:
        return {
            "id": customer.id,
            "name": customer.name,
            "folder_path": customer.folder_path,
            "address": customer.address or "",
            "next_contact_date": customer.next_contact_date or "",
            "delivery_notes": customer.delivery_notes or "",
        }

    def _apply_snapshot(self, snapshot: dict) -> None:
        self.current_customer_id = snapshot["id"]
        self.customer_name.setText(snapshot["name"])
        self.folder_path.setText(snapshot["folder_path"])
        self.address.setText(snapshot["address"])
        self.next_contact_date.set_iso_date(snapshot["next_contact_date"])
        self.delivery_notes.setText(snapshot["delivery_notes"])
