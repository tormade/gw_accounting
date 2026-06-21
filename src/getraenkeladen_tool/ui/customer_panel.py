from PySide6.QtWidgets import QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from ..schemas import CustomerCreate
from ..services.customer_service import create_customer


CUSTOMER_PANEL_ACTIONS = {
    "saveCustomerButton": "Kunde speichern",
    "chooseCustomerFolderButton": "Ordner waehlen",
}


class CustomerPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory

        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("z. B. Cafe Nord")
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText("Kundenordner")
        self.address = QLineEdit()
        self.payment_method = QLineEdit()
        self.payment_method.setPlaceholderText("SEPA oder Ueberweisung")
        self.next_contact_date = QLineEdit()
        self.next_contact_date.setPlaceholderText("YYYY-MM-DD")
        self.delivery_notes = QLineEdit()
        self.status_label = QLabel("Noch kein Kunde gespeichert.")
        self.status_label.setObjectName("muted")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        headline = QLabel("Kunden")
        headline.setObjectName("headline")
        layout.addWidget(headline)

        muted = QLabel("Stammdaten, Lieferhinweise und Kontakttermine")
        muted.setObjectName("muted")
        layout.addWidget(muted)

        form = QFormLayout()
        form.addRow("Kunde", self.customer_name)
        form.addRow("Kundenordner", self._folder_row())
        form.addRow("Adresse", self.address)
        form.addRow("Zahlungsart", self.payment_method)
        form.addRow("Naechster Kontakt", self.next_contact_date)
        form.addRow("Lieferhinweise", self.delivery_notes)
        layout.addLayout(form)

        action_row = QHBoxLayout()
        self.save_button = self._button("saveCustomerButton")
        action_row.addWidget(self.save_button)
        action_row.addStretch()
        layout.addLayout(action_row)
        layout.addWidget(self.status_label)
        layout.addStretch()
        self.save_button.clicked.connect(self.save_customer)

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

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Kundenordner waehlen")
        if folder:
            self.folder_path.setText(folder)

    def save_customer(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        session = self.session_factory()
        try:
            customer = create_customer(
                session,
                CustomerCreate(
                    name=self.customer_name.text().strip(),
                    folder_path=self.folder_path.text().strip(),
                    address=self.address.text().strip() or None,
                    payment_method=self.payment_method.text().strip() or None,
                    next_contact_date=self.next_contact_date.text().strip() or None,
                    delivery_notes=self.delivery_notes.text().strip() or None,
                ),
            )
            self.status_label.setText(f"Kunde gespeichert: {customer.name}")
        finally:
            session.close()
