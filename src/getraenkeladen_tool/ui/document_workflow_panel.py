from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..schemas import DepositReturnCreate, DocumentLineItem
from ..services.customer_service import list_active_customers
from ..services.numbering_service import suggest_next_numbers
from ..services.order_service import create_order_delivery_order, create_order_invoice, get_order, list_active_orders
from .date_input import to_display_date
from .deposit_return_presets import DEPOSIT_RETURN_PRESETS
from .layouts import ContentSurface, FilterBar, PageHeader, ResponsiveSplitter, WorkspaceCard, configure_form_layout
from .searchable_select import SearchableSelect


DOCUMENT_WORKFLOW_ACTIONS = {
    "removeDocumentLineButton": "Position entfernen",
    "addDocumentDepositReturnButton": "Pfand zurueck hinzufuegen",
    "removeDocumentDepositReturnButton": "Pfand zurueck entfernen",
}
DOCUMENT_LINE_COLUMNS = ("Artikel", "Menge", "Preis EUR", "Pfand EUR", "Summe EUR")
DOCUMENT_RETURN_COLUMNS = ("Pfandart", "Menge", "Pfand EUR", "Gutschrift EUR")
DOCUMENT_ORDER_COLUMNS = ("Auftrag", "Kunde", "Lieferdatum", "Zeitfenster", "Status")


class DocumentWorkflowPanel(QWidget):
    document_type = ""
    number_label = ""
    create_button_text = ""

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.order_ids_by_row = {}
        self.current_order_id = None
        self.last_excel_path: Path | None = None
        self.last_pdf_path: Path | None = None

        self.customer_filter = SearchableSelect("Alle Kunden anzeigen")
        self.customer_filter.result_list.setMaximumHeight(56)
        self.customer_filter.setMinimumWidth(280)
        self.customer_filter.setMaximumWidth(340)
        self.orders_table = QTableWidget(0, len(DOCUMENT_ORDER_COLUMNS))
        self.orders_table.setHorizontalHeaderLabels(DOCUMENT_ORDER_COLUMNS)
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.setMinimumHeight(220)

        self.order_summary = QLabel("Noch kein Auftrag ausgewaehlt.")
        self.order_summary.setObjectName("sectionSubtitle")
        self.order_summary.setWordWrap(True)
        self.document_number = QLineEdit()
        self.document_number.setPlaceholderText(self.number_label)
        self.lines_table = QTableWidget(0, len(DOCUMENT_LINE_COLUMNS))
        self.lines_table.setHorizontalHeaderLabels(DOCUMENT_LINE_COLUMNS)
        self.lines_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lines_table.setMinimumHeight(260)
        self.returns_table = QTableWidget(0, len(DOCUMENT_RETURN_COLUMNS))
        self.returns_table.setHorizontalHeaderLabels(DOCUMENT_RETURN_COLUMNS)
        self.returns_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.returns_table.setMaximumHeight(150)
        self.deposit_return_select = QComboBox()
        for label, cents in DEPOSIT_RETURN_PRESETS:
            self.deposit_return_select.addItem(label, cents)
        self.deposit_return_quantity = QLineEdit()
        self.deposit_return_quantity.setPlaceholderText("z. B. 1")
        self.deposit_return_eur = QLineEdit()
        self.deposit_return_eur.setPlaceholderText("z. B. 4,80")
        self.total_label = QLabel("Belegsumme: 0,00 EUR")
        self.total_label.setObjectName("stepTitle")
        self.status_label = QLabel("Auftrag auswaehlen, Positionen pruefen, dann Datei erstellen.")
        self.status_label.setObjectName("muted")
        self.result_label = QLabel("Noch keine Datei erstellt.")
        self.result_label.setObjectName("sectionSubtitle")
        self.result_label.setWordWrap(True)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        layout.addWidget(
            PageHeader(
                self.document_type,
                "Auftrag waehlen, Positionen bei Bedarf fuer diesen Beleg anpassen und Excel/PDF erzeugen.",
            )
        )

        body = ResponsiveSplitter()
        layout.addWidget(body, 1)

        order_box, order_layout = self._section("1. Auftrag auswaehlen", "Liste filtern und Auftrag doppelt anklicken.")
        filter_toolbar = FilterBar()
        filter_label = QLabel("Auftraege filtern nach Kunde")
        filter_label.setObjectName("sectionSubtitle")
        filter_toolbar.layout.addWidget(filter_label)
        filter_toolbar.layout.addWidget(self.customer_filter)
        filter_toolbar.layout.addStretch()
        order_layout.addWidget(filter_toolbar)
        order_layout.addWidget(self.orders_table)
        refresh_row = QHBoxLayout()
        self.refresh_button = QPushButton("Auftraege laden")
        self.load_button = QPushButton("Auftrag uebernehmen")
        refresh_row.addWidget(self.refresh_button)
        refresh_row.addWidget(self.load_button)
        refresh_row.addStretch()
        order_layout.addLayout(refresh_row)
        body.addWidget(order_box)

        document_box, document_layout = self._section(
            "2. Beleg pruefen",
            "Die Positionen gelten nur fuer diesen Beleg. Der urspruengliche Auftrag bleibt als Vorlage erhalten.",
        )
        document_layout.addWidget(self.order_summary)
        number_row = QHBoxLayout()
        number_form = QFormLayout()
        configure_form_layout(number_form)
        number_form.addRow(self.number_label, self.document_number)
        number_row.addLayout(number_form)
        self.suggest_number_button = QPushButton("Nummer vorschlagen")
        number_row.addWidget(self.suggest_number_button)
        document_layout.addLayout(number_row)
        document_layout.addWidget(self.lines_table)
        line_action_row = QHBoxLayout()
        self.remove_line_button = QPushButton(DOCUMENT_WORKFLOW_ACTIONS["removeDocumentLineButton"])
        line_action_row.addWidget(self.remove_line_button)
        line_action_row.addStretch()
        document_layout.addLayout(line_action_row)
        return_form = QFormLayout()
        configure_form_layout(return_form)
        return_form.addRow("Pfandart", self.deposit_return_select)
        return_form.addRow("Menge", self.deposit_return_quantity)
        return_form.addRow("Pfand EUR", self.deposit_return_eur)
        document_layout.addLayout(return_form)
        return_action_row = QHBoxLayout()
        self.add_return_button = QPushButton(DOCUMENT_WORKFLOW_ACTIONS["addDocumentDepositReturnButton"])
        self.remove_return_button = QPushButton(DOCUMENT_WORKFLOW_ACTIONS["removeDocumentDepositReturnButton"])
        return_action_row.addWidget(self.add_return_button)
        return_action_row.addWidget(self.remove_return_button)
        return_action_row.addStretch()
        document_layout.addLayout(return_action_row)
        document_layout.addWidget(self.returns_table)
        total_bar = QWidget()
        total_bar.setObjectName("totalBar")
        total_layout = QHBoxLayout(total_bar)
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)
        document_layout.addWidget(total_bar)
        action_row = QHBoxLayout()
        self.create_button = QPushButton(self.create_button_text)
        self.open_excel_button = QPushButton("Excel oeffnen")
        self.open_pdf_button = QPushButton("PDF oeffnen")
        self.open_excel_button.setEnabled(False)
        self.open_pdf_button.setEnabled(False)
        action_row.addWidget(self.create_button)
        action_row.addWidget(self.open_excel_button)
        action_row.addWidget(self.open_pdf_button)
        action_row.addStretch()
        document_layout.addLayout(action_row)
        document_layout.addWidget(self.result_label)
        body.addWidget(document_box)
        body.setStretchFactor(0, 1)
        body.setStretchFactor(1, 2)
        layout.addWidget(self.status_label)

        self.refresh_button.clicked.connect(self.refresh_orders)
        self.load_button.clicked.connect(self.load_selected_order)
        self.suggest_number_button.clicked.connect(self.suggest_document_number)
        self.remove_line_button.clicked.connect(self.remove_selected_line)
        self.add_return_button.clicked.connect(self.add_deposit_return)
        self.remove_return_button.clicked.connect(self.remove_selected_deposit_return)
        self.deposit_return_select.currentIndexChanged.connect(self.apply_selected_deposit_return)
        self.create_button.clicked.connect(self.create_document)
        self.open_excel_button.clicked.connect(lambda: self._open_local_file(self.last_excel_path))
        self.open_pdf_button.clicked.connect(lambda: self._open_local_file(self.last_pdf_path))
        self.orders_table.itemDoubleClicked.connect(lambda _item: self.load_selected_order())
        self.customer_filter.selection_changed.connect(self.refresh_orders)
        self.lines_table.itemChanged.connect(self.update_total)
        self.returns_table.itemChanged.connect(self.update_total)
        self.refresh_master_data()
        self.refresh_orders()
        self.suggest_document_number()
        self.apply_selected_deposit_return()

    def _button(self, object_name: str) -> QPushButton:
        return QPushButton(DOCUMENT_WORKFLOW_ACTIONS[object_name])

    def _section(self, title: str, subtitle: str) -> tuple[QWidget, QVBoxLayout]:
        box = WorkspaceCard(title, subtitle)
        return box, box.layout

    def refresh_master_data(self) -> None:
        if self.session_factory is None:
            return
        session = self.session_factory()
        try:
            customers = list_active_customers(session)
        finally:
            session.close()
        self.customer_filter.set_items(
            [("Alle Kunden", None, "Keine Einschraenkung")]
            + [(customer.name, customer.id, customer.address or "") for customer in customers]
        )

    def refresh_orders(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        customer_id = self.customer_filter.current_value()
        session = self.session_factory()
        try:
            orders = list_active_orders(session, customer_id=customer_id)
        finally:
            session.close()
        self.order_ids_by_row = {}
        self.orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self.order_ids_by_row[row] = order.id
            values = (
                order.order_number,
                order.customer.name,
                to_display_date(order.delivery_date),
                order.delivery_slot or "",
                order.status,
            )
            for column, value in enumerate(values):
                self.orders_table.setItem(row, column, QTableWidgetItem(value))
        self.status_label.setText(f"{len(orders)} Auftraege geladen.")

    def load_selected_order(self) -> None:
        row = self.orders_table.currentRow()
        order_id = self.order_ids_by_row.get(row)
        if order_id is None or self.session_factory is None:
            self.status_label.setText("Bitte zuerst einen Auftrag auswaehlen.")
            return
        self.select_order(order_id)

    def select_order(self, order_id: int) -> None:
        if self.session_factory is None:
            return
        session = self.session_factory()
        try:
            order = get_order(session, order_id)
            self.current_order_id = order.id
            self.order_summary.setText(
                f"{order.order_number} | {order.customer.name} | Lieferdatum {to_display_date(order.delivery_date)}"
            )
            self.lines_table.setRowCount(0)
            self.returns_table.setRowCount(0)
            for line in order.lines:
                self._append_line(line.product_name, line.quantity, line.unit_price_cents, line.deposit_cents)
            for deposit_return in order.deposit_returns:
                self._append_return(deposit_return.name, deposit_return.quantity, deposit_return.deposit_cents)
            self.status_label.setText("Auftrag uebernommen. Positionen pruefen und Beleg erstellen.")
        finally:
            session.close()

    def suggest_document_number(self) -> None:
        if self.session_factory is None:
            return
        session = self.session_factory()
        try:
            suggestions = suggest_next_numbers(session)
        finally:
            session.close()
        self.document_number.setText(self._number_from_suggestions(suggestions))

    def create_document(self) -> None:
        if self.current_order_id is None:
            self.load_selected_order()
        if self.current_order_id is None or self.session_factory is None:
            return
        session = self.session_factory()
        try:
            document = self._create_document_for_order(session)
            self.refresh_orders()
            self.last_excel_path = Path(document.excel_path)
            self.last_pdf_path = Path(document.pdf_path)
            self.open_excel_button.setEnabled(True)
            self.open_pdf_button.setEnabled(True)
            self.result_label.setText(f"Erstellt.\nExcel: {self.last_excel_path}\nPDF: {self.last_pdf_path}")
            self.status_label.setText(f"{self.document_type} erstellt.")
        finally:
            session.close()

    def _create_document_for_order(self, session):
        raise NotImplementedError

    def _number_from_suggestions(self, suggestions) -> str:
        raise NotImplementedError

    def _line_items_from_table(self) -> list[DocumentLineItem]:
        items = []
        for row in range(self.lines_table.rowCount()):
            name_item = self.lines_table.item(row, 0)
            quantity_item = self.lines_table.item(row, 1)
            price_item = self.lines_table.item(row, 2)
            deposit_item = self.lines_table.item(row, 3)
            if name_item is None or not name_item.text().strip():
                continue
            items.append(
                DocumentLineItem(
                    name=name_item.text().strip(),
                    quantity=int(quantity_item.text()) if quantity_item is not None else 1,
                    unit_price_cents=self._parse_euro_cents(price_item.text() if price_item is not None else "0"),
                    deposit_cents=self._parse_euro_cents(deposit_item.text() if deposit_item is not None else "0"),
                )
            )
        return items

    def _deposit_returns_from_table(self) -> list[DepositReturnCreate]:
        returns = []
        for row in range(self.returns_table.rowCount()):
            name_item = self.returns_table.item(row, 0)
            quantity_item = self.returns_table.item(row, 1)
            deposit_item = self.returns_table.item(row, 2)
            if name_item is None or not name_item.text().strip():
                continue
            returns.append(
                DepositReturnCreate(
                    name=name_item.text().strip(),
                    quantity=int(quantity_item.text()) if quantity_item is not None else 1,
                    deposit_cents=self._parse_euro_cents(deposit_item.text() if deposit_item is not None else "0"),
                )
            )
        return returns

    def add_deposit_return(self) -> None:
        name = self.deposit_return_select.currentText().strip()
        if not name:
            self.status_label.setText("Bitte eine Pfandart eintragen.")
            return
        quantity = self._parse_quantity(self.deposit_return_quantity.text())
        deposit_cents = self._parse_euro_cents_or_zero(self.deposit_return_eur.text())
        if quantity <= 0 or deposit_cents <= 0:
            self.status_label.setText("Bitte Menge und Pfandwert groesser 0 eintragen.")
            return
        self._append_return(name, quantity, deposit_cents)
        self.status_label.setText("Pfandrueckgabe fuer diesen Beleg hinzugefuegt.")

    def apply_selected_deposit_return(self) -> None:
        cents = self.deposit_return_select.currentData()
        if cents is None:
            return
        self.deposit_return_eur.setText(f"{int(cents) / 100:.2f}".replace(".", ","))

    def remove_selected_line(self) -> None:
        row = self.lines_table.currentRow()
        if row >= 0:
            self.lines_table.removeRow(row)
            self.update_total()

    def remove_selected_deposit_return(self) -> None:
        row = self.returns_table.currentRow()
        if row >= 0:
            self.returns_table.removeRow(row)
            self.update_total()

    def _append_line(self, product_name: str, quantity: int, unit_price_cents: int, deposit_cents: int) -> None:
        row = self.lines_table.rowCount()
        self.lines_table.blockSignals(True)
        self.lines_table.insertRow(row)
        values = (
            product_name,
            str(quantity),
            f"{unit_price_cents / 100:.2f}".replace(".", ","),
            f"{deposit_cents / 100:.2f}".replace(".", ","),
            self._format_euro_cents((unit_price_cents + deposit_cents) * quantity),
        )
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column == 4:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.lines_table.setItem(row, column, item)
        self.lines_table.blockSignals(False)
        self.update_total()

    def _append_return(self, name: str, quantity: int, deposit_cents: int) -> None:
        row = self.returns_table.rowCount()
        self.returns_table.blockSignals(True)
        self.returns_table.insertRow(row)
        values = (
            name,
            str(quantity),
            f"{deposit_cents / 100:.2f}".replace(".", ","),
            self._format_euro_cents(-deposit_cents * quantity),
        )
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column == 3:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.returns_table.setItem(row, column, item)
        self.returns_table.blockSignals(False)
        self.update_total()

    def update_total(self, _item=None) -> None:
        total_cents = 0
        self.lines_table.blockSignals(True)
        self.returns_table.blockSignals(True)
        try:
            for row in range(self.lines_table.rowCount()):
                line_total = self._line_total_cents(row)
                total_cents += line_total
                self._set_total_item(self.lines_table, row, 4, line_total)
            for row in range(self.returns_table.rowCount()):
                return_total = self._return_total_cents(row)
                total_cents -= return_total
                self._set_total_item(self.returns_table, row, 3, -return_total)
        finally:
            self.lines_table.blockSignals(False)
            self.returns_table.blockSignals(False)
        self.total_label.setText(f"Belegsumme: {self._format_euro_cents(total_cents)}")

    def _set_total_item(self, table: QTableWidget, row: int, column: int, cents: int) -> None:
        item = table.item(row, column)
        if item is None:
            item = QTableWidgetItem()
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, column, item)
        item.setText(self._format_euro_cents(cents))

    def _line_total_cents(self, row: int) -> int:
        quantity = self._parse_int(self.lines_table.item(row, 1))
        price = self._parse_euro_cents_or_zero(self._item_text(self.lines_table.item(row, 2)))
        deposit = self._parse_euro_cents_or_zero(self._item_text(self.lines_table.item(row, 3)))
        return (price + deposit) * quantity

    def _return_total_cents(self, row: int) -> int:
        quantity = self._parse_int(self.returns_table.item(row, 1))
        deposit = self._parse_euro_cents_or_zero(self._item_text(self.returns_table.item(row, 2)))
        return deposit * quantity

    def _open_local_file(self, path: Path | None) -> None:
        if path is not None and path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _parse_int(self, item: QTableWidgetItem | None) -> int:
        try:
            return int(item.text()) if item is not None else 0
        except ValueError:
            return 0

    def _parse_quantity(self, value: str) -> int:
        try:
            return int(value.strip())
        except ValueError:
            return 0

    def _item_text(self, item: QTableWidgetItem | None) -> str:
        return item.text() if item is not None else ""

    def _parse_euro_cents(self, value: str) -> int:
        normalized = value.strip().replace(".", "").replace(",", ".").replace(" EUR", "")
        return int(round(float(normalized) * 100))

    def _parse_euro_cents_or_zero(self, value: str) -> int:
        try:
            return self._parse_euro_cents(value)
        except ValueError:
            return 0

    def _format_euro_cents(self, cents: int) -> str:
        return f"{cents / 100:.2f} EUR".replace(".", ",")


class DeliveryNotePanel(DocumentWorkflowPanel):
    document_type = "Lieferscheine"
    number_label = "LS-Nummer"
    create_button_text = "Lieferschein Excel/PDF erstellen"

    def _number_from_suggestions(self, suggestions) -> str:
        return suggestions.delivery_note_number

    def _create_document_for_order(self, session):
        return create_order_delivery_order(
            session,
            self.current_order_id,
            self.document_number.text().strip(),
            line_items=self._line_items_from_table(),
            deposit_returns=self._deposit_returns_from_table(),
        )


class InvoicePanel(DocumentWorkflowPanel):
    document_type = "Rechnungen"
    number_label = "Rechnungsnummer"
    create_button_text = "Rechnung Excel/PDF erstellen"

    def _number_from_suggestions(self, suggestions) -> str:
        return suggestions.invoice_number

    def _create_document_for_order(self, session):
        return create_order_invoice(
            session,
            self.current_order_id,
            self.document_number.text().strip(),
            line_items=self._line_items_from_table(),
            deposit_returns=self._deposit_returns_from_table(),
            datev_upload_dir=Path.cwd() / "outputs" / "datev_upload",
        )
