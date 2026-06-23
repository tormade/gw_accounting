from pathlib import Path

from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..services.customer_assortment_service import list_customer_assortment
from ..services.customer_folder_service import get_customer_folder_snapshot
from ..services.customer_service import list_active_customers
from .date_input import to_display_date
from .layouts import ContentSurface, PageHeader, ResponsiveSplitter, WorkspaceCard
from .searchable_select import SearchableSelect


FOLDER_FILE_COLUMNS = ("Datei", "Art", "Aktion")
ORDER_COLUMNS = ("Bestellung", "Lieferdatum", "Status")
ASSORTMENT_COLUMNS = ("Artikel", "Letzte Menge", "Neuer Preis", "Pfand", "Hinweis")


class CustomerFolderPanel(QWidget):
    new_order_requested = Signal(int)
    delivery_note_requested = Signal(int)
    invoice_requested = Signal(int)

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.customers_by_id = {}
        self.files_by_row: dict[int, Path] = {}
        self.order_ids_by_row: dict[int, int] = {}
        self.current_customer_id: int | None = None
        self.current_folder_path: Path | None = None

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout
        layout.addWidget(PageHeader("Kundenordner", "Kundenakte oeffnen, vorhandene Dateien sehen und Belege anstossen."))

        self.customer_select = SearchableSelect("Kunde suchen, z. B. Cafe oder Metzgerei")
        self.refresh_button = QPushButton("Kunden laden")
        self.open_folder_button = QPushButton("Kundenordner oeffnen")
        self.open_file_button = QPushButton("Datei oeffnen")
        self.new_order_button = QPushButton("Neue Bestellung fuer Kunden")
        self.delivery_note_button = QPushButton("Lieferschein erstellen")
        self.invoice_button = QPushButton("Rechnung erstellen")
        self.status_label = QLabel("Noch kein Kunde ausgewaehlt.")
        self.status_label.setObjectName("muted")

        search_card = WorkspaceCard("Kundenakte", "Kunden aus der Datenbank suchen und die echte Ordneransicht laden.")
        search_card.layout.addWidget(self.customer_select)
        search_actions = QHBoxLayout()
        search_actions.addWidget(self.refresh_button)
        search_actions.addWidget(self.open_folder_button)
        search_actions.addWidget(self.new_order_button)
        search_actions.addStretch()
        search_card.layout.addLayout(search_actions)
        layout.addWidget(search_card)

        splitter = ResponsiveSplitter()
        layout.addWidget(splitter, 1)

        files_card = WorkspaceCard("Dateien im Kundenordner", "Excel- und PDF-Dateien aus dem hinterlegten Kundenordner.")
        self.files_table = self._table(FOLDER_FILE_COLUMNS, 220)
        files_card.layout.addWidget(self.files_table)
        file_actions = QHBoxLayout()
        file_actions.addWidget(self.open_file_button)
        file_actions.addStretch()
        files_card.layout.addLayout(file_actions)
        splitter.addWidget(files_card)

        workflow_card = WorkspaceCard("Letzte bekannte Bestellung", "Offene Bestellungen und Sortiment als Arbeitsgrundlage.")
        self.orders_table = self._table(ORDER_COLUMNS, 180)
        self.assortment_table = self._table(ASSORTMENT_COLUMNS, 260)
        workflow_card.layout.addWidget(self.orders_table)
        workflow_card.layout.addWidget(self.assortment_table)
        workflow_actions = QHBoxLayout()
        workflow_actions.addWidget(self.delivery_note_button)
        workflow_actions.addWidget(self.invoice_button)
        workflow_actions.addStretch()
        workflow_card.layout.addLayout(workflow_actions)
        splitter.addWidget(workflow_card)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(self.status_label)

        self.customer_select.selection_changed.connect(self.load_selected_customer)
        self.files_table.itemSelectionChanged.connect(self.update_action_state)
        self.orders_table.itemSelectionChanged.connect(self.update_action_state)
        self.refresh_button.clicked.connect(self.refresh_customers)
        self.open_folder_button.clicked.connect(self.open_customer_folder)
        self.open_file_button.clicked.connect(self.open_selected_file)
        self.new_order_button.clicked.connect(self.request_new_order_for_customer)
        self.delivery_note_button.clicked.connect(self.request_delivery_note_for_selected_order)
        self.invoice_button.clicked.connect(self.request_invoice_for_selected_order)

        self.refresh_customers()
        self.update_action_state()

    def _table(self, columns: tuple[str, ...], minimum_height: int) -> QTableWidget:
        table = QTableWidget(0, len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setMinimumHeight(minimum_height)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table

    def refresh_customers(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            customers = list_active_customers(session)
            self.customers_by_id = {customer.id: customer for customer in customers}
            self.customer_select.set_items(
                (customer.name, customer.id, customer.folder_path or "") for customer in customers
            )
        finally:
            session.close()
        self.status_label.setText(f"{len(self.customers_by_id)} Kunden geladen.")

    def load_selected_customer(self) -> None:
        customer_id = self.customer_select.current_value()
        if customer_id is None:
            return
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            snapshot = get_customer_folder_snapshot(session, int(customer_id))
            assortment = list_customer_assortment(session, int(customer_id))
            self.show_snapshot(snapshot, assortment)
        except ValueError as exc:
            QMessageBox.warning(self, "Kundenordner", str(exc))
        finally:
            session.close()

    def show_snapshot(self, snapshot, assortment_rows=None) -> None:
        self.current_customer_id = snapshot.customer.id
        self.current_folder_path = snapshot.folder_path
        assortment_rows = assortment_rows or []

        self.files_by_row.clear()
        self.files_table.setRowCount(len(snapshot.files))
        for row, folder_file in enumerate(snapshot.files):
            self.files_by_row[row] = folder_file.path
            self._set_row(self.files_table, row, (folder_file.label, folder_file.kind, "oeffnen"))

        self.order_ids_by_row.clear()
        self.orders_table.setRowCount(len(snapshot.orders))
        for row, order in enumerate(snapshot.orders):
            self.order_ids_by_row[row] = order.id
            self._set_row(
                self.orders_table,
                row,
                (order.order_number, to_display_date(order.delivery_date), order.status),
            )

        self.assortment_table.setRowCount(len(assortment_rows))
        for row, item in enumerate(assortment_rows):
            self._set_row(
                self.assortment_table,
                row,
                (
                    item.product_name or item.source_product_name,
                    str(item.last_quantity),
                    self._money(item.current_price_cents),
                    self._money(item.current_deposit_cents),
                    item.price_warning_text or ("Pruefen" if item.needs_review else ""),
                ),
            )

        folder_status = "vorhanden" if snapshot.folder_exists else "fehlt"
        self.status_label.setText(
            f"{snapshot.customer.name}: Kundenordner {folder_status}, "
            f"{len(snapshot.files)} Dateien, {len(snapshot.orders)} Bestellungen."
        )
        self.update_action_state()

    def open_customer_folder(self) -> None:
        if self.current_folder_path is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswaehlen.")
            return
        if not self.current_folder_path.is_dir():
            self._show_missing_file("Der Kundenordner wurde nicht gefunden.")
            return
        self._open_url(self.current_folder_path)

    def open_selected_file(self) -> None:
        row = self.files_table.currentRow()
        path = self.files_by_row.get(row)
        if path is None:
            self.status_label.setText("Bitte zuerst eine Datei im Kundenordner auswaehlen.")
            return
        if not path.exists():
            self._show_missing_file("Die Datei wurde nicht gefunden.")
            return
        self._open_url(path)

    def request_new_order_for_customer(self) -> None:
        if self.current_customer_id is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswaehlen.")
            return
        self.new_order_requested.emit(self.current_customer_id)

    def _selected_order_id(self) -> int | None:
        return self.order_ids_by_row.get(self.orders_table.currentRow())

    def request_delivery_note_for_selected_order(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            self.status_label.setText("Bitte zuerst eine Bestellung dieses Kunden auswaehlen.")
            return
        self.delivery_note_requested.emit(order_id)

    def request_invoice_for_selected_order(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            self.status_label.setText("Bitte zuerst eine Bestellung dieses Kunden auswaehlen.")
            return
        self.invoice_requested.emit(order_id)

    def update_action_state(self) -> None:
        has_customer = self.current_customer_id is not None
        has_folder = self.current_folder_path is not None and self.current_folder_path.is_dir()
        has_file = self.files_by_row.get(self.files_table.currentRow()) is not None
        has_order = self._selected_order_id() is not None
        self.open_folder_button.setEnabled(has_folder)
        self.open_file_button.setEnabled(has_file)
        self.new_order_button.setEnabled(has_customer)
        self.delivery_note_button.setEnabled(has_order)
        self.invoice_button.setEnabled(has_order)

    def _set_row(self, table: QTableWidget, row: int, values: tuple[str, ...]) -> None:
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setToolTip(value)
            table.setItem(row, column, item)

    def _money(self, cents: int | None) -> str:
        return f"{(cents or 0) / 100:.2f} EUR".replace(".", ",")

    def _open_url(self, path: Path) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _show_missing_file(self, message: str) -> None:
        QMessageBox.warning(self, "Kundenordner", message)
