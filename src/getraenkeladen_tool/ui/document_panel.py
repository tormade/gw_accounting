from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..services.excel_service import build_delivery_note_workbook, build_invoice_workbook


DOCUMENT_FORM_ACTIONS = {
    "sampleDocumentButton": "Beispiel laden",
    "chooseCustomerFolderButton": "Ordner waehlen",
    "createDocumentButton": "Excel erstellen",
}


class DocumentPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory

        self.document_type = QComboBox()
        self.document_type.addItems(["Rechnung", "Lieferschein"])
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("z. B. Cafe Nord")
        self.customer_folder = QLineEdit()
        self.customer_folder.setPlaceholderText("Kundenordner auswaehlen oder eintragen")
        self.document_number = QLineEdit()
        self.document_number.setPlaceholderText("z. B. RG-1001")
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("z. B. Wasser 0,7")
        self.quantity = QSpinBox()
        self.quantity.setRange(1, 999)
        self.unit_price_eur = QLineEdit()
        self.unit_price_eur.setPlaceholderText("z. B. 12,99")
        self.deposit_eur = QLineEdit()
        self.deposit_eur.setPlaceholderText("z. B. 3,30")
        self.status_label = QLabel("Noch kein Beleg erzeugt.")
        self.status_label.setObjectName("muted")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        headline = QLabel("Belege")
        headline.setObjectName("headline")
        layout.addWidget(headline)

        muted = QLabel("Erste Arbeitsmaske fuer Rechnung oder Lieferschein aus der Winklmeier-Excel-Vorlage")
        muted.setObjectName("muted")
        layout.addWidget(muted)

        form = QFormLayout()
        form.addRow("Belegtyp", self.document_type)
        form.addRow("Kunde", self.customer_name)
        form.addRow("Kundenordner", self._folder_row())
        form.addRow("Belegnummer", self.document_number)
        form.addRow("Produkt", self.product_name)
        form.addRow("Menge", self.quantity)
        form.addRow("Preis EUR", self.unit_price_eur)
        form.addRow("Pfand EUR", self.deposit_eur)
        layout.addLayout(form)

        action_row = QHBoxLayout()
        self.sample_button = self._button("sampleDocumentButton")
        self.create_button = self._button("createDocumentButton")
        action_row.addWidget(self.sample_button)
        action_row.addWidget(self.create_button)
        action_row.addStretch()
        layout.addLayout(action_row)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.sample_button.clicked.connect(self.load_sample)
        self.create_button.clicked.connect(self.create_excel)

    def _folder_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.customer_folder)
        self.choose_folder_button = self._button("chooseCustomerFolderButton")
        layout.addWidget(self.choose_folder_button)
        self.choose_folder_button.clicked.connect(self.choose_folder)
        return row

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(DOCUMENT_FORM_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def choose_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Kundenordner waehlen")
        if folder:
            self.customer_folder.setText(folder)

    def load_sample(self) -> None:
        sample_folder = Path.cwd() / "outputs" / "Cafe Nord"
        self.document_type.setCurrentText("Rechnung")
        self.customer_name.setText("Cafe Nord")
        self.customer_folder.setText(str(sample_folder))
        self.document_number.setText("RG-1001")
        self.product_name.setText("Wasser 0,7")
        self.quantity.setValue(10)
        self.unit_price_eur.setText("12,99")
        self.deposit_eur.setText("3,30")
        self.status_label.setText("Beispiel geladen. Jetzt kann die Excel-Datei erzeugt werden.")

    def create_excel(self) -> None:
        output_path = self._output_path()
        line_items = [
            {
                "name": self.product_name.text().strip(),
                "quantity": self.quantity.value(),
                "unit_price_cents": self._parse_euro_cents(self.unit_price_eur.text()),
                "deposit_cents": self._parse_euro_cents(self.deposit_eur.text()),
            }
        ]

        if self.document_type.currentText() == "Rechnung":
            build_invoice_workbook(output_path, self.customer_name.text().strip(), self.document_number.text().strip(), line_items)
        else:
            build_delivery_note_workbook(output_path, self.customer_name.text().strip(), self.document_number.text().strip(), line_items)

        self.status_label.setText(f"Excel-Datei erstellt: {output_path}")

    def _output_path(self) -> Path:
        document_type = self.document_type.currentText()
        document_number = self.document_number.text().strip()
        safe_document_number = document_number.replace("/", "-").replace("\\", "-").replace(" ", "_")
        safe_document_type = document_type.replace(" ", "_")
        return Path(self.customer_folder.text().strip()) / f"{safe_document_number}_{safe_document_type}.xlsx"

    def _parse_euro_cents(self, value: str) -> int:
        normalized = value.strip().replace(".", "").replace(",", ".")
        return int(round(float(normalized) * 100))
