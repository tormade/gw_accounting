from PySide6.QtWidgets import QCheckBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from ..schemas import ProductCreate
from ..services.product_service import create_product, deactivate_product


PRODUCT_PANEL_ACTIONS = {
    "saveProductButton": "Produkt speichern",
    "deactivateProductButton": "Produkt deaktivieren",
}


class ProductPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("z. B. Wasser 0,7")
        self.unit = QLineEdit()
        self.unit.setPlaceholderText("z. B. Kiste")
        self.article_number = QLineEdit()
        self.price_eur = QLineEdit()
        self.price_eur.setPlaceholderText("z. B. 12,99")
        self.is_active = QCheckBox("Aktiv")
        self.is_active.setChecked(True)
        self.current_product_id = None
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
        self.save_button.clicked.connect(self.save_product)
        self.deactivate_button.clicked.connect(self.deactivate_current_product)

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(PRODUCT_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def save_product(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        session = self.session_factory()
        try:
            product = create_product(
                session,
                ProductCreate(
                    name=self.product_name.text().strip(),
                    unit=self.unit.text().strip(),
                    standard_price_cents=self._parse_euro_cents(self.price_eur.text()),
                    article_number=self.article_number.text().strip() or None,
                    is_active=self.is_active.isChecked(),
                ),
            )
            self.current_product_id = product.id
            self.status_label.setText(f"Produkt gespeichert: {product.name}")
        finally:
            session.close()

    def deactivate_current_product(self) -> None:
        if self.session_factory is None or self.current_product_id is None:
            self.status_label.setText("Kein gespeichertes Produkt zum Deaktivieren ausgewaehlt.")
            return

        session = self.session_factory()
        try:
            product = deactivate_product(session, self.current_product_id)
            self.is_active.setChecked(False)
            self.status_label.setText(f"Produkt deaktiviert: {product.name}")
        finally:
            session.close()

    def _parse_euro_cents(self, value: str) -> int:
        normalized = value.strip().replace(".", "").replace(",", ".")
        return int(round(float(normalized) * 100))
