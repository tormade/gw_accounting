from PySide6.QtWidgets import QCheckBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget


PRODUCT_PANEL_ACTIONS = {
    "saveProductButton": "Produkt speichern",
    "deactivateProductButton": "Produkt deaktivieren",
}


class ProductPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("z. B. Wasser 0,7")
        self.unit = QLineEdit()
        self.unit.setPlaceholderText("z. B. Kiste")
        self.article_number = QLineEdit()
        self.price_eur = QLineEdit()
        self.price_eur.setPlaceholderText("z. B. 12,99")
        self.is_active = QCheckBox("Aktiv")
        self.is_active.setChecked(True)
        self.status_label = QLabel("Noch kein Produkt gespeichert.")
        self.status_label.setObjectName("muted")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        headline = QLabel("Produkte")
        headline.setObjectName("headline")
        layout.addWidget(headline)

        muted = QLabel("Zentrale Artikelliste und Standardpreise")
        muted.setObjectName("muted")
        layout.addWidget(muted)

        form = QFormLayout()
        form.addRow("Produkt", self.product_name)
        form.addRow("Einheit", self.unit)
        form.addRow("Artikelnummer", self.article_number)
        form.addRow("Preis EUR", self.price_eur)
        form.addRow("Status", self.is_active)
        layout.addLayout(form)

        action_row = QHBoxLayout()
        self.save_button = self._button("saveProductButton")
        self.deactivate_button = self._button("deactivateProductButton")
        action_row.addWidget(self.save_button)
        action_row.addWidget(self.deactivate_button)
        action_row.addStretch()
        layout.addLayout(action_row)
        layout.addWidget(self.status_label)
        layout.addStretch()

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(PRODUCT_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button
