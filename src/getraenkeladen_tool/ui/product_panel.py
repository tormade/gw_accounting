from PySide6.QtWidgets import (
    QCheckBox,
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

from ..models import Product
from ..schemas import ProductCreate
from ..services.product_service import (
    create_product,
    deactivate_product,
    list_products,
    restore_product,
    update_product,
)


PRODUCT_PANEL_ACTIONS = {
    "saveProductButton": "Produkt speichern",
    "refreshProductsButton": "Produktliste laden",
    "loadProductButton": "Auswahl bearbeiten",
    "deactivateProductButton": "Produkt deaktivieren",
    "restoreProductButton": "Produkt wiederherstellen",
}

PRODUCT_COLUMNS = ("Produkt", "Einheit", "Artikelnummer", "Preis", "Status")
PRODUCT_PANEL_SECTIONS = ("1. Produkt erfassen", "2. Preisliste pruefen")
PRODUCT_GUIDANCE_STEPS = (
    "Artikel mit Einheit und Standardpreis pflegen.",
    "Vorhandene Artikel unten auswaehlen und zur Bearbeitung laden.",
    "Nicht mehr benoetigte Artikel deaktivieren statt endgueltig loeschen.",
)


class ProductPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.current_product_id = None
        self.product_ids_by_row = {}

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
        self.products_table = QTableWidget(0, len(PRODUCT_COLUMNS))
        self.products_table.setHorizontalHeaderLabels(PRODUCT_COLUMNS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        headline = QLabel("Produkte")
        headline.setObjectName("headline")
        layout.addWidget(headline)

        muted = QLabel("Zentrale Artikelliste und Standardpreise")
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
            PRODUCT_PANEL_SECTIONS[0],
            "Produktname, Einheit und Preis sind die Basis fuer spaetere Auftraege.",
        )
        form = QFormLayout()
        form.addRow("Produkt", self.product_name)
        form.addRow("Einheit", self.unit)
        form.addRow("Artikelnummer", self.article_number)
        form.addRow("Preis EUR", self.price_eur)
        form.addRow("Status", self.is_active)
        edit_layout.addLayout(form)

        action_row = QHBoxLayout()
        self.save_button = self._button("saveProductButton")
        self.load_button = self._button("loadProductButton")
        action_row.addWidget(self.save_button)
        action_row.addWidget(self.load_button)
        action_row.addStretch()
        edit_layout.addLayout(action_row)
        left_column.addWidget(edit_box)

        list_box, list_layout = self._section(
            PRODUCT_PANEL_SECTIONS[1],
            "Artikel unten anklicken. Deaktivieren verhindert neue Nutzung, Wiederherstellen macht ihn wieder aktiv.",
        )
        list_actions = QHBoxLayout()
        self.refresh_button = self._button("refreshProductsButton")
        self.deactivate_button = self._button("deactivateProductButton")
        self.restore_button = self._button("restoreProductButton")
        for button in (
            self.refresh_button,
            self.deactivate_button,
            self.restore_button,
        ):
            list_actions.addWidget(button)
        list_actions.addStretch()
        list_layout.addLayout(list_actions)
        list_layout.addWidget(self.products_table)
        right_column.addWidget(list_box)

        layout.addWidget(self.status_label)

        self.save_button.clicked.connect(self.save_product)
        self.refresh_button.clicked.connect(self.refresh_products)
        self.load_button.clicked.connect(self.load_selected_product)
        self.deactivate_button.clicked.connect(self.deactivate_current_product)
        self.restore_button.clicked.connect(self.restore_selected_product)
        self.products_table.itemDoubleClicked.connect(lambda _item: self.load_selected_product())

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(PRODUCT_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def _guidance_box(self) -> QWidget:
        box = QWidget()
        box.setObjectName("guidanceBox")
        layout = QVBoxLayout(box)
        layout.setSpacing(8)
        title = QLabel("So pflegen Sie Produkte")
        title.setObjectName("stepTitle")
        layout.addWidget(title)
        for index, step in enumerate(PRODUCT_GUIDANCE_STEPS, start=1):
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

    def save_product(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        payload = ProductCreate(
            name=self.product_name.text().strip(),
            unit=self.unit.text().strip(),
            standard_price_cents=self._parse_euro_cents(self.price_eur.text()),
            article_number=self.article_number.text().strip() or None,
            is_active=self.is_active.isChecked(),
        )
        session = self.session_factory()
        try:
            if self.current_product_id is None:
                product = create_product(session, payload)
            else:
                product = update_product(session, self.current_product_id, payload)
            self.current_product_id = product.id
            self.status_label.setText(f"Produkt gespeichert: {product.name}")
            self.show_products(list_products(session))
        finally:
            session.close()

    def refresh_products(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return

        session = self.session_factory()
        try:
            self.show_products(list_products(session))
        finally:
            session.close()

    def show_products(self, products: list) -> None:
        self.product_ids_by_row = {}
        self.products_table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.product_ids_by_row[row] = product.id
            values = (
                product.name,
                product.unit,
                product.article_number or "",
                f"{product.standard_price_cents / 100:.2f} EUR".replace(".", ","),
                "aktiv" if product.is_active else "archiviert",
            )
            for column, value in enumerate(values):
                self.products_table.setItem(row, column, QTableWidgetItem(value))
        self.status_label.setText(f"{len(products)} Produkte geladen.")

    def load_selected_product(self) -> None:
        product_id = self._selected_product_id()
        if product_id is None or self.session_factory is None:
            self.status_label.setText("Bitte zuerst ein Produkt auswaehlen.")
            return

        session = self.session_factory()
        try:
            product = session.get(Product, product_id)
            if product is None:
                self.status_label.setText("Produkt wurde nicht gefunden.")
                return
            self.current_product_id = product.id
            self.product_name.setText(product.name)
            self.unit.setText(product.unit)
            self.article_number.setText(product.article_number or "")
            self.price_eur.setText(f"{product.standard_price_cents / 100:.2f}".replace(".", ","))
            self.is_active.setChecked(product.is_active)
            self.status_label.setText(f"Produkt geladen: {product.name}")
        finally:
            session.close()

    def deactivate_current_product(self) -> None:
        product_id = self.current_product_id or self._selected_product_id()
        if self.session_factory is None or product_id is None:
            self.status_label.setText("Kein Produkt zum Deaktivieren ausgewaehlt.")
            return

        session = self.session_factory()
        try:
            product = deactivate_product(session, product_id)
            self.current_product_id = product.id
            self.is_active.setChecked(False)
            self.show_products(list_products(session))
            self.status_label.setText(f"Produkt deaktiviert: {product.name}")
        finally:
            session.close()

    def restore_selected_product(self) -> None:
        product_id = self.current_product_id or self._selected_product_id()
        if self.session_factory is None or product_id is None:
            self.status_label.setText("Kein Produkt zum Wiederherstellen ausgewaehlt.")
            return

        session = self.session_factory()
        try:
            product = restore_product(session, product_id)
            self.current_product_id = product.id
            self.is_active.setChecked(True)
            self.show_products(list_products(session))
            self.status_label.setText(f"Produkt wiederhergestellt: {product.name}")
        finally:
            session.close()

    def _selected_product_id(self) -> int | None:
        row = self.products_table.currentRow()
        return self.product_ids_by_row.get(row)

    def _parse_euro_cents(self, value: str) -> int:
        normalized = value.strip().replace(".", "").replace(",", ".")
        return int(round(float(normalized) * 100))
