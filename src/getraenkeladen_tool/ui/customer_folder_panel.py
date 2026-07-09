from pathlib import Path
import os
import platform
import subprocess

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
from ..services.customer_folder_service import CustomerFolderFile, get_customer_folder_snapshot
from ..services.customer_service import list_active_customers
from ..services.order_service import archive_order
from .date_input import to_display_date
from .layouts import ContentSurface, PageHeader, ResponsiveSplitter, WorkspaceCard
from .searchable_select import SearchableSelect


FOLDER_FILE_COLUMNS = ("Datei", "Art", "Aktion")
ORDER_COLUMNS = ("Bestellung", "Lieferdatum", "Status")
ASSORTMENT_COLUMNS = ("Artikel", "Letzte Menge", "Zuletzt", "Bisher", "Preis", "Verlauf")
MAX_VISIBLE_FOLDER_FILES = 20
MAX_VISIBLE_ORDERS = 30


class CustomerFolderPanel(QWidget):
    new_order_requested = Signal(int)
    open_order_requested = Signal(int)
    copy_order_requested = Signal(int)
    delivery_note_requested = Signal(int)
    invoice_requested = Signal(int)

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.customers_by_id = {}
        self.files_by_row: dict[int, CustomerFolderFile] = {}
        self.order_ids_by_row: dict[int, int] = {}
        self.current_customer_id: int | None = None
        self.current_folder_path: Path | None = None
        self.has_seed_quantities = False
        self.visible_file_limit_message: str | None = None
        self.visible_order_limit_message: str | None = None

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout
        layout.addWidget(
            PageHeader(
                "Kundenordner",
                "1 Kunde suchen -> 2 alte Bestellung pruefen -> 3 Lieferschein oder Rechnung erstellen.",
            )
        )

        self.customer_select = SearchableSelect("Kunde suchen, z. B. Cafe oder Metzgerei")
        self.refresh_button = QPushButton("Kundenliste aktualisieren")
        self.open_folder_button = QPushButton("Kundenordner oeffnen")
        self.open_file_button = QPushButton("Markierte Excel/PDF oeffnen")
        self.new_order_button = QPushButton("Neue Bestellung aus letzten Mengen starten")
        self.seed_file_hint = QLabel("Die Vorlage kommt aus den letzten importierten Mengen rechts.")
        self.seed_file_hint.setObjectName("sectionSubtitle")
        self.workflow_hint = QLabel("Bestellung markieren, dann Beleg erstellen oder als neue Bestellung kopieren.")
        self.workflow_hint.setObjectName("sectionSubtitle")
        self.open_order_button = QPushButton("Bestellung oeffnen")
        self.copy_order_button = QPushButton("Als neue Bestellung kopieren")
        self.delivery_note_button = QPushButton("Lieferschein erstellen")
        self.invoice_button = QPushButton("Rechnung erstellen")
        self.delete_order_button = QPushButton("Bestellung loeschen")
        self.delete_order_button.setObjectName("dangerAction")
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

        workflow_card = WorkspaceCard(
            "Aus alter Bestellung weiterarbeiten",
            "Alte Excel/PDF links ist zum Nachsehen. Die letzten Mengen rechts werden automatisch vorgeschlagen.",
        )
        self.orders_table = self._table(ORDER_COLUMNS, 180)
        self.assortment_table = self._table(ASSORTMENT_COLUMNS, 260)
        orders_title = QLabel("Bestellungen dieses Kunden")
        orders_title.setObjectName("sectionTitle")
        workflow_card.layout.addWidget(orders_title)
        workflow_card.layout.addWidget(self.workflow_hint)
        workflow_primary_actions = QHBoxLayout()
        workflow_primary_actions.addWidget(self.open_order_button)
        workflow_primary_actions.addWidget(self.copy_order_button)
        workflow_primary_actions.addStretch()
        workflow_card.layout.addLayout(workflow_primary_actions)
        workflow_document_actions = QHBoxLayout()
        workflow_document_actions.addWidget(self.delivery_note_button)
        workflow_document_actions.addWidget(self.invoice_button)
        workflow_document_actions.addStretch()
        workflow_card.layout.addLayout(workflow_document_actions)
        workflow_delete_actions = QHBoxLayout()
        workflow_delete_actions.addWidget(self.delete_order_button)
        workflow_delete_actions.addStretch()
        workflow_card.layout.addLayout(workflow_delete_actions)
        workflow_card.layout.addWidget(self.orders_table)
        assortment_title = QLabel("Letzte Mengen aus dem Kundenordner")
        assortment_title.setObjectName("sectionTitle")
        workflow_card.layout.addWidget(assortment_title)
        workflow_card.layout.addWidget(self.assortment_table)
        workflow_card.layout.addWidget(self.seed_file_hint)
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
        self.open_order_button.clicked.connect(self.request_open_selected_order)
        self.copy_order_button.clicked.connect(self.request_copy_for_selected_order)
        self.delivery_note_button.clicked.connect(self.request_delivery_note_for_selected_order)
        self.invoice_button.clicked.connect(self.request_invoice_for_selected_order)
        self.delete_order_button.clicked.connect(self.delete_selected_order)

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
            self.clear_customer_context("Bitte einen Kunden aus der Trefferliste anklicken.")
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

    def clear_customer_context(self, message: str) -> None:
        self.current_customer_id = None
        self.current_folder_path = None
        self.has_seed_quantities = False
        self.visible_file_limit_message = None
        self.visible_order_limit_message = None
        self.files_by_row.clear()
        self.order_ids_by_row.clear()
        self.files_table.setRowCount(0)
        self.orders_table.setRowCount(0)
        self.assortment_table.setRowCount(0)
        self.status_label.setText(message)
        self.update_action_state()

    def show_snapshot(self, snapshot, assortment_rows=None) -> None:
        self.current_customer_id = snapshot.customer.id
        self.current_folder_path = snapshot.folder_path
        assortment_rows = assortment_rows or []
        self.has_seed_quantities = bool(assortment_rows)
        self.visible_file_limit_message = None
        self.visible_order_limit_message = None

        visible_files = snapshot.files[:MAX_VISIBLE_FOLDER_FILES]
        self.files_by_row.clear()
        self.files_table.setRowCount(len(visible_files))
        for row, folder_file in enumerate(visible_files):
            self.files_by_row[row] = folder_file
            action = "Excel ansehen" if folder_file.can_seed_order else "oeffnen"
            self._set_row(self.files_table, row, (folder_file.label, folder_file.kind, action))

        visible_orders = snapshot.orders[:MAX_VISIBLE_ORDERS]
        self.order_ids_by_row.clear()
        self.orders_table.setRowCount(len(visible_orders))
        for row, order in enumerate(visible_orders):
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
                    to_display_date(getattr(item, "last_order_date", None)) if getattr(item, "last_order_date", None) else "-",
                    self._history_count_text(item),
                    self._money(item.current_price_cents),
                    self._assortment_hint(item),
                ),
            )

        folder_status = "vorhanden" if snapshot.folder_exists else "fehlt"
        self.status_label.setText(
            f"{snapshot.customer.name}: Kundenordner {folder_status}, "
            f"{len(snapshot.files)} Dateien, {len(snapshot.orders)} Bestellungen."
        )
        if len(snapshot.files) > MAX_VISIBLE_FOLDER_FILES:
            self.visible_file_limit_message = (
                f"Aus Stabilitaetsgruenden werden hier die neuesten {MAX_VISIBLE_FOLDER_FILES} "
                "Dateien angezeigt. Alle Dateien bleiben ueber 'Kundenordner oeffnen' erreichbar."
            )
        if len(snapshot.orders) > MAX_VISIBLE_ORDERS:
            self.visible_order_limit_message = (
                f"Aus Stabilitaetsgruenden werden hier die neuesten {MAX_VISIBLE_ORDERS} "
                "Bestellungen angezeigt."
            )
        self.update_action_state()

    def select_order(self, order_id: int) -> None:
        for row, row_order_id in self.order_ids_by_row.items():
            if row_order_id != order_id:
                continue
            self.orders_table.setCurrentCell(row, 0)
            item = self.orders_table.item(row, 0)
            if item is not None:
                self.orders_table.scrollToItem(item)
            self.update_action_state()
            return

    def open_customer_folder(self) -> None:
        if self.current_folder_path is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswaehlen.")
            return
        if not self.current_folder_path.is_dir():
            self._show_missing_file("Der Kundenordner wurde nicht gefunden.")
            return
        if self._open_url(self.current_folder_path):
            self.status_label.setText(f"Kundenordner geoeffnet: {self.current_folder_path}")
        else:
            self.status_label.setText("Kundenordner konnte nicht geoeffnet werden.")

    def open_selected_file(self) -> None:
        row = self.files_table.currentRow()
        folder_file = self.files_by_row.get(row)
        if folder_file is None:
            self.status_label.setText("Bitte zuerst eine Datei im Kundenordner auswaehlen.")
            return
        path = folder_file.path
        if not path.exists():
            self._show_missing_file("Die Datei wurde nicht gefunden.")
            return
        if self._open_url(path):
            self.status_label.setText(f"Datei geoeffnet: {path.name}")
        else:
            self.status_label.setText("Datei konnte nicht geoeffnet werden.")

    def request_new_order_for_customer(self) -> None:
        if self.current_customer_id is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswaehlen.")
            return
        self.new_order_requested.emit(self.current_customer_id)

    def request_open_selected_order(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            self.status_label.setText("Bitte zuerst eine Bestellung dieses Kunden auswaehlen.")
            return
        self.open_order_requested.emit(order_id)

    def request_copy_for_selected_order(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            self.status_label.setText("Bitte zuerst eine alte Bestellung dieses Kunden auswaehlen.")
            return
        self.copy_order_requested.emit(order_id)

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

    def delete_selected_order(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            self.status_label.setText("Bitte zuerst eine Bestellung dieses Kunden auswaehlen.")
            return
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        if not self.confirm_order_delete():
            return
        session = self.session_factory()
        try:
            order = archive_order(session, order_id)
            self.status_label.setText(f"Bestellung geloescht: {order.order_number}")
        except Exception as error:
            QMessageBox.warning(self, "Bestellung nicht geloescht", f"Die Bestellung konnte nicht geloescht werden.\n\nGrund: {error}")
        finally:
            session.close()
        self.load_selected_customer()

    def confirm_order_delete(self) -> bool:
        answer = QMessageBox.question(
            self,
            "Bestellung loeschen",
            "Willst du diese Bestellung wirklich loeschen?\n\n"
            "Sie verschwindet danach aus den normalen Listen, auch wenn bereits ein Lieferschein oder eine Rechnung erstellt wurde.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.status_label.setText("Loeschen abgebrochen.")
            return False
        return True

    def update_action_state(self) -> None:
        has_customer = self.current_customer_id is not None
        has_folder = self.current_folder_path is not None and self.current_folder_path.is_dir()
        selected_file = self.files_by_row.get(self.files_table.currentRow())
        has_file = selected_file is not None
        has_order = self._selected_order_id() is not None
        self.open_folder_button.setEnabled(has_folder)
        self.open_file_button.setEnabled(has_file)
        self.new_order_button.setEnabled(has_customer)
        if self.has_seed_quantities:
            self.new_order_button.setText("Neue Bestellung aus letzten Mengen starten")
        elif has_customer and not has_folder:
            self.new_order_button.setText("Ohne Kundenordner leere Bestellung starten")
        else:
            self.new_order_button.setText("Neue leere Bestellung starten")
        self.copy_order_button.setEnabled(has_order)
        self.open_order_button.setEnabled(has_order)
        self.delivery_note_button.setEnabled(has_order)
        self.invoice_button.setEnabled(has_order)
        self.delete_order_button.setEnabled(has_order)
        if self.visible_order_limit_message is not None and not has_order:
            self.workflow_hint.setText(self.visible_order_limit_message)
        elif self.visible_order_limit_message is not None:
            self.workflow_hint.setText(
                self.visible_order_limit_message + " Markierte Bestellung kann direkt weiterverarbeitet werden."
            )
        else:
            self.workflow_hint.setText("Bestellung markieren, dann Beleg erstellen oder als neue Bestellung kopieren.")
        if selected_file is None:
            if self.visible_file_limit_message is not None:
                self.seed_file_hint.setText(self.visible_file_limit_message)
            elif has_customer and not has_folder:
                self.seed_file_hint.setText(
                    "Kundenordner fehlt. Es kann nur eine leere Bestellung gestartet werden."
                )
            else:
                self.seed_file_hint.setText("Die Vorlage kommt aus den letzten importierten Mengen rechts.")
        elif selected_file.can_seed_order:
            self.seed_file_hint.setText(f"Excel-Datei zum Nachsehen: {selected_file.label}")
        else:
            self.seed_file_hint.setText("PDF ist nur zum Nachsehen. Neue Mengen stehen rechts.")

    def _set_row(self, table: QTableWidget, row: int, values: tuple[str, ...]) -> None:
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setToolTip(value)
            table.setItem(row, column, item)

    def _money(self, cents: int | None) -> str:
        return f"{(cents or 0) / 100:.2f} EUR".replace(".", ",")

    def _history_count_text(self, item) -> str:
        order_count = getattr(item, "order_count", 0)
        total_quantity = getattr(item, "total_quantity", 0)
        if order_count <= 0:
            return "-"
        return f"{order_count}x / {total_quantity} gesamt"

    def _assortment_hint(self, item) -> str:
        if getattr(item, "price_warning_text", None):
            return item.price_warning_text
        if getattr(item, "needs_review", False):
            return "Pruefen"
        return getattr(item, "sales_hint", "") or ""

    def _open_url(self, path: Path) -> bool:
        absolute_path = path.resolve()
        if QDesktopServices.openUrl(QUrl.fromLocalFile(str(absolute_path))):
            return True
        return self._open_path_with_system(absolute_path)

    def _open_path_with_system(self, path: Path) -> bool:
        try:
            system_name = platform.system()
            if system_name == "Darwin":
                return subprocess.run(["open", str(path)], check=False).returncode == 0
            if system_name == "Windows":
                os.startfile(str(path))  # type: ignore[attr-defined]
                return True
            return subprocess.run(["xdg-open", str(path)], check=False).returncode == 0
        except Exception:
            return False

    def _show_missing_file(self, message: str) -> None:
        QMessageBox.warning(self, "Kundenordner", message)
