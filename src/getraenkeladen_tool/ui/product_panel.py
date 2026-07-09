from PySide6.QtWidgets import (
    QCheckBox,
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

from ..models import Product
from ..schemas import ProductCreate
from ..services.product_service import (
    create_product,
    deactivate_product,
    list_product_changes,
    list_products,
    revert_product_change,
    restore_product,
    update_product,
)
from .layouts import ContentSurface, PageHeader, WorkspaceCard, configure_form_layout, set_button_role, set_equal_button_widths


PRODUCT_PANEL_ACTIONS = {
    "newProductButton": "Neu",
    "saveProductButton": "Produkt speichern",
    "discardProductChangesButton": "Verwerfen",
    "undoProductChangeButton": "Rückgängig",
    "refreshProductsButton": "Produktliste laden",
    "loadProductButton": "Auswahl bearbeiten",
    "deactivateProductButton": "Produkt deaktivieren",
    "restoreProductButton": "Produkt wiederherstellen",
}
PRODUCT_BUTTON_ROLES = {
    "newProductButton": "quiet",
    "saveProductButton": "primary",
    "discardProductChangesButton": "quiet",
    "undoProductChangeButton": "quiet",
    "refreshProductsButton": "quiet",
    "loadProductButton": "secondary",
    "deactivateProductButton": "danger",
    "restoreProductButton": "secondary",
}
PRODUCT_COLUMNS = ("Produkt", "Artikelnummer", "Preis", "Pfand", "Status")
PRODUCT_PANEL_SECTIONS = ("1. Produkt erfassen", "2. Preisliste prüfen")
PRODUCT_GUIDANCE_STEPS = (
    "Artikel mit Standardpreis pflegen.",
    "Vorhandene Artikel unten auswählen und zur Bearbeitung laden.",
    "Änderungen können vor dem Speichern verworfen werden.",
)
PRODUCT_CONTEXT_ACTIONS = {
    "edit": "Produkt bearbeiten",
    "deactivate": "Produkt deaktivieren",
    "restore": "Produkt wiederherstellen",
}


class ProductPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.current_product_id = None
        self.product_ids_by_row = {}
        self.loaded_form_snapshot = None
        self.has_loaded = False

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("z. B. Wasser 0,7")
        self.article_number = QLineEdit()
        self.price_eur = QLineEdit()
        self.price_eur.setPlaceholderText("z. B. 12,99")
        self.deposit_eur = QLineEdit()
        self.deposit_eur.setPlaceholderText("z. B. 3,30")
        self.is_active = QCheckBox("Aktiv")
        self.is_active.setChecked(True)
        self.status_label = QLabel("Noch kein Produkt gespeichert.")
        self.status_label.setObjectName("muted")
        self.products_table = QTableWidget(0, len(PRODUCT_COLUMNS))
        self.products_table.setHorizontalHeaderLabels(PRODUCT_COLUMNS)
        self.products_table.setMinimumHeight(360)
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.products_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        layout.addWidget(PageHeader("Produkte", "Zentrale Artikelliste und Standardpreise."))
        layout.addWidget(self._guidance_box())

        edit_box, edit_layout = self._section(
            PRODUCT_PANEL_SECTIONS[0],
            "Produktname, Artikelnummer, Preis und Pfand sind die Basis für spätere Bestellungen.",
            tone="cash",
            kicker="PREISKARTE",
        )
        edit_box.setMaximumHeight(500)
        form = QFormLayout()
        configure_form_layout(form)
        form.addRow("Produkt", self.product_name)
        form.addRow("Artikelnummer", self.article_number)
        form.addRow("Preis EUR", self.price_eur)
        form.addRow("Pfand EUR", self.deposit_eur)
        form.addRow("Status", self.is_active)
        edit_layout.addLayout(form)

        action_row = QHBoxLayout()
        self.new_button = self._button("newProductButton")
        self.save_button = self._button("saveProductButton")
        self.discard_button = self._button("discardProductChangesButton")
        self.undo_change_button = self._button("undoProductChangeButton")
        self.load_button = self._button("loadProductButton")
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
            PRODUCT_PANEL_SECTIONS[1],
            "Artikel unten anklicken. Deaktivieren verhindert neue Nutzung, Wiederherstellen macht ihn wieder aktiv.",
            tone="document",
            kicker="ARTIKELSTAMM",
        )
        list_actions = QHBoxLayout()
        self.refresh_button = self._button("refreshProductsButton")
        self.deactivate_button = self._button("deactivateProductButton")
        self.restore_button = self._button("restoreProductButton")
        set_equal_button_widths((self.refresh_button, self.deactivate_button, self.restore_button), 170)
        for button in (
            self.refresh_button,
            self.deactivate_button,
            self.restore_button,
        ):
            list_actions.addWidget(button)
        list_actions.addStretch()
        list_layout.addLayout(list_actions)
        list_layout.addWidget(self.products_table)
        layout.addWidget(edit_box)
        layout.addWidget(list_box, 1)

        layout.addWidget(self.status_label)

        self.new_button.clicked.connect(self.new_product)
        self.save_button.clicked.connect(self.save_product)
        self.discard_button.clicked.connect(self.discard_changes)
        self.undo_change_button.clicked.connect(self.undo_last_change)
        self.refresh_button.clicked.connect(self.refresh_products)
        self.load_button.clicked.connect(self.load_selected_product)
        self.deactivate_button.clicked.connect(self.deactivate_current_product)
        self.restore_button.clicked.connect(self.restore_selected_product)
        self.products_table.itemDoubleClicked.connect(lambda _item: self.load_selected_product())
        self.products_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.products_table.customContextMenuRequested.connect(self.show_product_context_menu)

    def ensure_loaded(self) -> None:
        if not self.has_loaded:
            self.refresh_products()

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(PRODUCT_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return set_button_role(button, PRODUCT_BUTTON_ROLES[object_name])

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

    def _section(self, title: str, subtitle: str, tone: str = "default", kicker: str = "") -> tuple[QWidget, QVBoxLayout]:
        box = WorkspaceCard(title, subtitle, tone=tone, kicker=kicker)
        return box, box.layout

    def save_product(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        if not self._validate_product_form():
            return

        payload = ProductCreate(
            name=self.product_name.text().strip(),
            unit="Menge",
            standard_price_cents=self._parse_euro_cents(self.price_eur.text()),
            default_deposit_cents=self._parse_euro_cents(self.deposit_eur.text()),
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
            self.loaded_form_snapshot = self._snapshot_from_product(product)
            self.status_label.setText(f"Erfolgreich gespeichert: Produkt gespeichert: {product.name}.")
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
            self.has_loaded = True
        finally:
            session.close()

    def show_products(self, products: list) -> None:
        self.product_ids_by_row = {}
        self.products_table.setUpdatesEnabled(False)
        try:
            self.products_table.setRowCount(len(products))
            for row, product in enumerate(products):
                self.product_ids_by_row[row] = product.id
                values = (
                    product.name,
                    product.article_number or "",
                    f"{product.standard_price_cents / 100:.2f} EUR".replace(".", ","),
                    f"{product.default_deposit_cents / 100:.2f} EUR".replace(".", ","),
                    "aktiv" if product.is_active else "archiviert",
                )
                for column, value in enumerate(values):
                    self.products_table.setItem(row, column, QTableWidgetItem(value))
        finally:
            self.products_table.setUpdatesEnabled(True)
        self.status_label.setText(f"{len(products)} Produkte geladen.")

    def load_selected_product(self) -> None:
        product_id = self._selected_product_id()
        if product_id is None or self.session_factory is None:
            self.status_label.setText("Bitte zuerst ein Produkt auswählen.")
            return

        session = self.session_factory()
        try:
            product = session.get(Product, product_id)
            if product is None:
                self.status_label.setText("Produkt wurde nicht gefunden.")
                return
            self.current_product_id = product.id
            self.product_name.setText(product.name)
            self.article_number.setText(product.article_number or "")
            self.price_eur.setText(f"{product.standard_price_cents / 100:.2f}".replace(".", ","))
            self.deposit_eur.setText(f"{product.default_deposit_cents / 100:.2f}".replace(".", ","))
            self.is_active.setChecked(product.is_active)
            self.loaded_form_snapshot = self._snapshot_from_product(product)
            self.status_label.setText(f"Produkt geladen: {product.name}")
        finally:
            session.close()

    def deactivate_current_product(self) -> None:
        product_id = self.current_product_id or self._selected_product_id()
        if self.session_factory is None or product_id is None:
            self.status_label.setText("Kein Produkt zum Deaktivieren ausgewählt.")
            return

        session = self.session_factory()
        try:
            product = deactivate_product(session, product_id)
            self.current_product_id = product.id
            self.is_active.setChecked(False)
            self.loaded_form_snapshot = self._form_snapshot()
            self.show_products(list_products(session))
            self.status_label.setText(f"Produkt deaktiviert: {product.name}")
        finally:
            session.close()

    def restore_selected_product(self) -> None:
        product_id = self.current_product_id or self._selected_product_id()
        if self.session_factory is None or product_id is None:
            self.status_label.setText("Kein Produkt zum Wiederherstellen ausgewählt.")
            return

        session = self.session_factory()
        try:
            product = restore_product(session, product_id)
            self.current_product_id = product.id
            self.is_active.setChecked(True)
            self.loaded_form_snapshot = self._form_snapshot()
            self.show_products(list_products(session))
            self.status_label.setText(f"Produkt wiederhergestellt: {product.name}")
        finally:
            session.close()

    def undo_last_change(self) -> None:
        product_id = self.current_product_id or self._selected_product_id()
        if self.session_factory is None or product_id is None:
            self.status_label.setText("Bitte zuerst ein Produkt auswählen.")
            return

        session = self.session_factory()
        try:
            changes = [change for change in list_product_changes(session, product_id) if change.action != "revert"]
            if not changes:
                self.status_label.setText("Keine Änderung zum Rückgängigmachen gefunden.")
                return
            product = revert_product_change(session, changes[0].id)
            self.current_product_id = product.id
            self.show_products(list_products(session))
            self.loaded_form_snapshot = self._snapshot_from_product(product)
            self.status_label.setText(f"Letzte Änderung rückgängig gemacht: {product.name}")
        finally:
            session.close()

    def _selected_product_id(self) -> int | None:
        row = self.products_table.currentRow()
        return self.product_ids_by_row.get(row)

    def new_product(self) -> None:
        self.current_product_id = None
        self._set_field_error(self.product_name, False)
        self.product_name.clear()
        self.article_number.clear()
        self.price_eur.clear()
        self.deposit_eur.clear()
        self.is_active.setChecked(True)
        self.loaded_form_snapshot = self._form_snapshot()
        self.status_label.setText("Neues Produkt. Erst Speichern übernimmt die Angaben.")

    def discard_changes(self) -> None:
        if self.loaded_form_snapshot is None:
            self.new_product()
            return
        self._apply_snapshot(self.loaded_form_snapshot)
        self.status_label.setText("Änderungen verworfen. Der zuletzt geladene Stand ist wiederhergestellt.")

    def show_product_context_menu(self, position) -> None:
        if self.products_table.currentRow() < 0:
            return
        menu = QMenu(self)
        edit_action = menu.addAction(PRODUCT_CONTEXT_ACTIONS["edit"])
        deactivate_action = menu.addAction(PRODUCT_CONTEXT_ACTIONS["deactivate"])
        restore_action = menu.addAction(PRODUCT_CONTEXT_ACTIONS["restore"])
        selected = menu.exec(self.products_table.viewport().mapToGlobal(position))
        if selected == edit_action:
            self.load_selected_product()
        elif selected == deactivate_action:
            self.deactivate_current_product()
        elif selected == restore_action:
            self.restore_selected_product()

    def _form_snapshot(self) -> dict:
        return {
            "id": self.current_product_id,
            "name": self.product_name.text(),
            "article_number": self.article_number.text(),
            "price_eur": self.price_eur.text(),
            "deposit_eur": self.deposit_eur.text(),
            "is_active": self.is_active.isChecked(),
        }

    def _snapshot_from_product(self, product: Product) -> dict:
        return {
            "id": product.id,
            "name": product.name,
            "article_number": product.article_number or "",
            "price_eur": f"{product.standard_price_cents / 100:.2f}".replace(".", ","),
            "deposit_eur": f"{product.default_deposit_cents / 100:.2f}".replace(".", ","),
            "is_active": product.is_active,
        }

    def _apply_snapshot(self, snapshot: dict) -> None:
        self.current_product_id = snapshot["id"]
        self._set_field_error(self.product_name, False)
        self.product_name.setText(snapshot["name"])
        self.article_number.setText(snapshot["article_number"])
        self.price_eur.setText(snapshot["price_eur"])
        self.deposit_eur.setText(snapshot["deposit_eur"])
        self.is_active.setChecked(snapshot["is_active"])

    def _parse_euro_cents(self, value: str) -> int:
        if not value.strip():
            return 0
        normalized = value.strip().replace(".", "").replace(",", ".")
        return int(round(float(normalized) * 100))

    def _validate_product_form(self) -> bool:
        if not self.product_name.text().strip():
            self._set_field_error(self.product_name, True)
            self.status_label.setText("Bitte Produktnamen eintragen.")
            self.product_name.setFocus()
            return False
        self._set_field_error(self.product_name, False)
        return True

    def _set_field_error(self, field: QLineEdit, has_error: bool) -> None:
        if has_error:
            field.setProperty("state", "error")
        else:
            field.setProperty("state", "")
        field.style().unpolish(field)
        field.style().polish(field)
