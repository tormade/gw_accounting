from dataclasses import dataclass
from datetime import date
from functools import partial
from pathlib import Path

from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..services.customer_assortment_service import CustomerAssortmentRow, list_customer_assortment_with_order_fallback
from ..services.automation_service import (
    CustomerFolderExcelPreview,
    CustomerQuickstart,
    get_customer_quickstart,
    list_customer_folder_excel_previews,
)
from ..services.customer_folder_service import CustomerFolderFile, get_customer_folder_snapshot
from ..services.customer_service import list_active_customers
from ..services.report_service import CustomerInvoiceWarning, get_customer_invoice_warning
from .background_task import BackgroundTask
from .date_input import to_display_date
from .layouts import ContentSurface, InspectorPanel, PageHeader, ResponsiveSplitter, WorkspaceCard, set_button_role
from .searchable_select import SearchableSelect


FOLDER_FILE_COLUMNS = ("Datei", "Art", "Aktion")
ORDER_COLUMNS = ("Bestellung", "Lieferdatum", "Status")
ASSORTMENT_COLUMNS = ("Artikel", "Letzte Menge", "Neuer Preis", "Pfand", "Hinweis")


@dataclass(frozen=True, slots=True)
class CustomerFolderCustomerData:
    id: int
    name: str
    address: str | None
    phone: str | None
    contact_name: str | None
    contact_email: str | None
    payment_method: str | None
    delivery_notes: str | None


@dataclass(frozen=True, slots=True)
class CustomerFolderOrderData:
    id: int
    order_number: str
    delivery_date: str
    status: str


@dataclass(frozen=True, slots=True)
class CustomerFolderSnapshotData:
    customer: CustomerFolderCustomerData
    folder_path: Path
    folder_exists: bool
    files: tuple[CustomerFolderFile, ...]
    documents_count: int
    orders: tuple[CustomerFolderOrderData, ...]


@dataclass(frozen=True, slots=True)
class CustomerFolderLoadData:
    snapshot: CustomerFolderSnapshotData
    assortment_rows: tuple[CustomerAssortmentRow, ...]
    quickstart: CustomerQuickstart
    excel_previews: tuple[CustomerFolderExcelPreview, ...]
    invoice_warning: CustomerInvoiceWarning


def _load_customer_context_in_background(session_factory, customer_id: int) -> CustomerFolderLoadData:
    session = session_factory()
    try:
        snapshot = get_customer_folder_snapshot(session, customer_id)
        customer = snapshot.customer
        display_snapshot = CustomerFolderSnapshotData(
            customer=CustomerFolderCustomerData(
                id=customer.id,
                name=customer.name,
                address=customer.address,
                phone=customer.phone,
                contact_name=customer.contact_name,
                contact_email=customer.contact_email,
                payment_method=customer.payment_method,
                delivery_notes=customer.delivery_notes,
            ),
            folder_path=snapshot.folder_path,
            folder_exists=snapshot.folder_exists,
            files=tuple(snapshot.files),
            documents_count=len(snapshot.documents),
            orders=tuple(
                CustomerFolderOrderData(
                    id=order.id,
                    order_number=order.order_number,
                    delivery_date=order.delivery_date,
                    status=order.status,
                )
                for order in snapshot.orders
            ),
        )
        return CustomerFolderLoadData(
            snapshot=display_snapshot,
            assortment_rows=tuple(list_customer_assortment_with_order_fallback(session, customer_id)),
            quickstart=get_customer_quickstart(session, customer_id),
            excel_previews=tuple(list_customer_folder_excel_previews(session, customer_id)),
            invoice_warning=get_customer_invoice_warning(
                session,
                customer.name,
                target_date=date.today().isoformat(),
            ),
        )
    finally:
        session.close()


class CustomerFolderPanel(QWidget):
    new_order_requested = Signal(int)
    order_open_requested = Signal(int)
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
        self.current_folder_exists = False
        self.has_seed_quantities = False
        self._customer_load_task = BackgroundTask(self)
        self._is_customer_loading = False
        self._loading_customer_id: int | None = None
        self._pending_customer_id: int | None = None

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout
        layout.addWidget(
            PageHeader(
                "Kunden",
                "Kunde finden, Kontext prüfen und direkt die nächste Bestellung starten.",
            )
        )

        self.customer_select = SearchableSelect("Kunde suchen, z. B. Cafe oder Metzgerei")
        self.open_folder_button = QPushButton("Kundenordner")
        self.open_file_button = QPushButton("Datei öffnen")
        self.new_order_button = QPushButton("Bestellung neu")
        self.new_order_button.setObjectName("primaryAction")
        self.seed_file_hint = QLabel("Letzte Mengen erscheinen nach der Kundenauswahl.")
        self.seed_file_hint.setObjectName("sectionSubtitle")
        self.customer_guide_label = QLabel("1. Kunde suchen  2. Letzte Mengen prüfen  3. Neue Bestellung starten")
        self.customer_guide_label.setObjectName("stepText")
        self.customer_guide_label.setWordWrap(True)
        self.delivery_note_button = QPushButton("Lieferschein erstellen")
        self.invoice_button = QPushButton("Rechnung erstellen")
        self.open_order_button = QPushButton("Öffnen")
        self.open_order_button.setToolTip("Ausgewählte frühere Bestellung öffnen")
        set_button_role(self.new_order_button, "primary")
        set_button_role(self.open_order_button, "secondary")
        set_button_role(self.delivery_note_button, "secondary")
        set_button_role(self.invoice_button, "secondary")
        set_button_role(self.open_folder_button, "quiet")
        set_button_role(self.open_file_button, "quiet")
        self.status_label = QLabel("Noch kein Kunde ausgewählt.")
        self.status_label.setObjectName("muted")

        self.customer_address_label = QLabel("Adresse: -")
        self.customer_contact_label = QLabel("Kontakt: -")
        self.customer_payment_label = QLabel("Zahlart: -")
        self.customer_delivery_notes_label = QLabel("Lieferhinweise: -")
        self.customer_folder_label = QLabel("Ablage: -")
        self.customer_documents_label = QLabel("Belege: -")
        self.customer_invoice_warning_label = QLabel("Offene Rechnungen: -")
        self.customer_next_step_label = QLabel("Nächster Schritt: Kunde suchen.")
        self.customer_next_step_label.setObjectName("nextStepValue")
        self.customer_next_step_label.setMinimumHeight(72)
        for label in (
            self.customer_address_label,
            self.customer_contact_label,
            self.customer_payment_label,
            self.customer_delivery_notes_label,
            self.customer_folder_label,
            self.customer_documents_label,
            self.customer_invoice_warning_label,
        ):
            label.setObjectName("inspectorValue")
            label.setWordWrap(True)
        self.customer_next_step_label.setWordWrap(True)

        splitter = ResponsiveSplitter()
        layout.addWidget(splitter, 1)

        workspace_card = WorkspaceCard(
            "Kunden finden",
            "Suche einen Kunden. Danach zeigt die rechte Seite Adresse, Zahlart, Hinweise und den besten nächsten Schritt.",
            tone="route",
            kicker="ARBEITSPLATZ",
        )
        workspace_card.layout.addWidget(self.customer_select)
        workspace_card.layout.addWidget(self.customer_guide_label)
        self.orders_table = self._table(ORDER_COLUMNS, 180)
        self.assortment_table = self._table(ASSORTMENT_COLUMNS, 260)
        self.files_table = self._table(FOLDER_FILE_COLUMNS, 180)
        self.customer_context_tabs = QTabWidget()
        self.customer_context_tabs.setUsesScrollButtons(False)

        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        orders_title = QLabel("Frühere Bestellungen")
        orders_title.setObjectName("sectionTitle")
        assortment_title = QLabel("Letzte Mengen")
        assortment_title.setObjectName("sectionTitle")
        overview_layout.addWidget(assortment_title)
        overview_layout.addWidget(self.assortment_table)
        overview_layout.addWidget(self.seed_file_hint)
        self.customer_context_tabs.addTab(overview_tab, "Übersicht")

        orders_tab = QWidget()
        orders_layout = QVBoxLayout(orders_tab)
        orders_layout.addWidget(orders_title)
        orders_layout.addWidget(self.orders_table)
        self.customer_context_tabs.addTab(orders_tab, "Frühere Bestellungen")

        files_tab = QWidget()
        files_layout = QVBoxLayout(files_tab)
        files_title = QLabel("Letzte Dateien")
        files_title.setObjectName("sectionTitle")
        files_layout.addWidget(files_title)
        files_layout.addWidget(self.files_table)
        self.customer_context_tabs.addTab(files_tab, "Dateien")
        workspace_card.layout.addWidget(self.customer_context_tabs, 1)
        splitter.addWidget(workspace_card)

        self.inspector = InspectorPanel("Kunde auswählen", "Nach der Auswahl stehen hier Kontext und nächste Aktion.")
        self.inspector.add_section_label("Kundenlage")
        self.inspector.body.addWidget(self.customer_address_label)
        self.inspector.body.addWidget(self.customer_contact_label)
        self.inspector.body.addWidget(self.customer_payment_label)
        self.inspector.body.addWidget(self.customer_delivery_notes_label)
        self.inspector.add_section_label("Ablage und Belege")
        self.inspector.body.addWidget(self.customer_folder_label)
        self.inspector.body.addWidget(self.customer_documents_label)
        self.inspector.add_section_label("Rechnungswarnung")
        self.inspector.body.addWidget(self.customer_invoice_warning_label)
        self.inspector.add_section_label("Nächster Schritt")
        self.inspector.body.addWidget(self.customer_next_step_label)
        self.inspector.body.addWidget(self.new_order_button)
        self.inspector.body.addWidget(self.open_order_button)
        self.inspector.body.addWidget(self.open_folder_button)
        self.inspector.body.addWidget(self.open_file_button)
        self.inspector.body.addWidget(self.delivery_note_button)
        self.inspector.body.addWidget(self.invoice_button)
        splitter.addWidget(self.inspector)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(self.status_label)

        self.customer_select.selection_changed.connect(self.load_selected_customer)
        self.files_table.itemSelectionChanged.connect(self.update_action_state)
        self.orders_table.itemSelectionChanged.connect(self.update_action_state)
        self.open_folder_button.clicked.connect(self.open_customer_folder)
        self.open_file_button.clicked.connect(self.open_selected_file)
        self.new_order_button.clicked.connect(self.request_new_order_for_customer)
        self.open_order_button.clicked.connect(self.request_open_selected_order)
        self.orders_table.itemDoubleClicked.connect(lambda _item: self.request_open_selected_order())
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
            self._pending_customer_id = None
            self.clear_customer_context("Bitte einen Kunden aus der Trefferliste anklicken.")
            return
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        customer_id = int(customer_id)
        if self._customer_load_task.is_running:
            if customer_id != self._loading_customer_id:
                self._pending_customer_id = customer_id
                self.status_label.setText("Auswahl wird nach dem aktuellen Laden übernommen.")
            return
        self._start_customer_loading(customer_id)

    def _start_customer_loading(self, customer_id: int) -> None:
        if self.current_customer_id is not None and self.current_customer_id != customer_id:
            self.clear_customer_context("Kundenwechsel wird vorbereitet.")
        self._loading_customer_id = customer_id
        self._set_customer_loading(True)
        if not self._customer_load_task.start(
            partial(_load_customer_context_in_background, self.session_factory, customer_id),
            on_success=self._show_loaded_customer_context,
            on_error=self._show_customer_load_error,
            on_finished=self._customer_load_finished,
        ):
            self._pending_customer_id = customer_id

    def _show_loaded_customer_context(self, result: object) -> None:
        if not isinstance(result, CustomerFolderLoadData):
            self._show_customer_load_error("Kundenordner konnte nicht gelesen werden.")
            return
        if self.customer_select.current_value() != result.snapshot.customer.id:
            return
        self.show_snapshot(
            result.snapshot,
            result.assortment_rows,
            quickstart=result.quickstart,
            excel_previews=result.excel_previews,
            invoice_warning=result.invoice_warning,
        )

    def _show_customer_load_error(self, error: Exception | str) -> None:
        message = str(error).strip() or type(error).__name__
        self.status_label.setText(f"Kundenordner konnte nicht geladen werden: {message}")
        QMessageBox.warning(self, "Kundenordner", message)

    def _customer_load_finished(self) -> None:
        self._set_customer_loading(False)
        self._loading_customer_id = None
        pending_customer_id = self._pending_customer_id
        self._pending_customer_id = None
        if pending_customer_id is not None and self.customer_select.current_value() == pending_customer_id:
            self._start_customer_loading(pending_customer_id)

    def _set_customer_loading(self, is_loading: bool) -> None:
        self._is_customer_loading = is_loading
        self.customer_select.setEnabled(not is_loading)
        if is_loading:
            self.status_label.setText("Kundenordner wird geladen...")
        self.update_action_state()

    def clear_customer_context(self, message: str) -> None:
        self.current_customer_id = None
        self.current_folder_path = None
        self.current_folder_exists = False
        self.has_seed_quantities = False
        self.files_by_row.clear()
        self.order_ids_by_row.clear()
        self.files_table.setRowCount(0)
        self.orders_table.setRowCount(0)
        self.assortment_table.setRowCount(0)
        self.inspector.set_heading("Kunde auswählen", "Nach der Auswahl stehen hier Kontext und nächste Aktion.")
        self.customer_address_label.setText("Adresse: -")
        self.customer_contact_label.setText("Kontakt: -")
        self.customer_payment_label.setText("Zahlart: -")
        self.customer_delivery_notes_label.setText("Lieferhinweise: -")
        self.customer_folder_label.setText("Ablage: -")
        self.customer_documents_label.setText("Belege: -")
        self.customer_invoice_warning_label.setText("Offene Rechnungen: -")
        self.customer_next_step_label.setText("Nächster Schritt: Kunde suchen.")
        self.seed_file_hint.setText("Letzte Mengen erscheinen nach der Kundenauswahl.")
        self.status_label.setText(message)
        self.update_action_state()

    def show_snapshot(
        self,
        snapshot,
        assortment_rows=None,
        *,
        quickstart: CustomerQuickstart | None = None,
        excel_previews: tuple[CustomerFolderExcelPreview, ...] = (),
        invoice_warning: CustomerInvoiceWarning | None = None,
    ) -> None:
        self.current_customer_id = snapshot.customer.id
        self.current_folder_path = snapshot.folder_path
        self.current_folder_exists = snapshot.folder_exists
        assortment_rows = assortment_rows or []
        self.has_seed_quantities = bool(assortment_rows)

        self.files_by_row.clear()
        self.files_table.setRowCount(len(snapshot.files))
        for row, folder_file in enumerate(snapshot.files):
            self.files_by_row[row] = folder_file
            action = "Excel ansehen" if folder_file.can_seed_order else "öffnen"
            self._set_row(self.files_table, row, (folder_file.label, folder_file.kind, action))

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
        self.customer_context_tabs.setCurrentIndex(0)
        for row, item in enumerate(assortment_rows):
            self._set_row(
                self.assortment_table,
                row,
                (
                    item.product_name or item.source_product_name,
                    str(item.last_quantity),
                    self._money(item.current_price_cents),
                    self._money(item.current_deposit_cents),
                    item.price_warning_text or ("Prüfen" if item.needs_review else ""),
                ),
            )

        folder_status = "vorhanden" if snapshot.folder_exists else "fehlt"
        customer = snapshot.customer
        contact_parts = [
            self._text(getattr(customer, "contact_name", "")),
            self._text(getattr(customer, "phone", "")),
            self._text(getattr(customer, "contact_email", "")),
        ]
        contact_text = " · ".join(part for part in contact_parts if part) or "-"
        self.inspector.set_heading(customer.name, "Kundenkontext für Bestellung, Beleg und Zahlung.")
        self.customer_address_label.setText(f"Adresse: {self._text(getattr(customer, 'address', '')) or '-'}")
        self.customer_contact_label.setText(f"Kontakt: {contact_text}")
        self.customer_payment_label.setText(f"Zahlart: {self._text(getattr(customer, 'payment_method', '')) or '-'}")
        self.customer_delivery_notes_label.setText(
            f"Lieferhinweise: {self._text(getattr(customer, 'delivery_notes', '')) or '-'}"
        )
        self.customer_folder_label.setText(f"Ablage: Kundenordner {folder_status}")
        document_count = getattr(snapshot, "documents_count", len(getattr(snapshot, "documents", [])))
        self.customer_documents_label.setText(
            f"Belege: {document_count} Dokumente, {len(snapshot.orders)} Bestellungen"
        )
        if invoice_warning is not None:
            self.customer_invoice_warning_label.setText(self._invoice_warning_text(invoice_warning))
        if quickstart is not None and quickstart.suggestions:
            next_step = quickstart.suggestions[0]
        elif assortment_rows:
            next_step = "Neue Bestellung starten; die letzten Mengen sind vorbereitet."
        elif snapshot.folder_exists:
            next_step = "Leere Bestellung starten oder alte Datei zum Nachsehen öffnen."
        else:
            next_step = "Leere Bestellung starten; Kundenordner später in Stammdaten prüfen."
        if excel_previews:
            preview = excel_previews[0]
            document_bits = [
                preview.document_number or "ohne Nummer",
                to_display_date(preview.document_date) if preview.document_date else "",
                f"{preview.filled_quantity_rows} Mengenzeile(n)",
            ]
            preview_text = " · ".join(bit for bit in document_bits if bit)
            next_step = f"Neue Excel-Datei prüfen: {preview.path.name} ({preview_text}). " + next_step
        self.customer_next_step_label.setText(f"Nächster Schritt: {next_step}")
        self.status_label.setText(
            f"{snapshot.customer.name}: Kundenordner {folder_status}, "
            f"{len(snapshot.files)} Dateien, {len(snapshot.orders)} Bestellungen."
        )
        if assortment_rows and all(getattr(row, "price_warning_text", None) == "aus letzter Bestellung" for row in assortment_rows):
            self.seed_file_hint.setText("Letzte Mengen aus letzter Bestellung. Mengen können in der neuen Bestellung geändert werden.")
        self.update_action_state()

    def open_customer_folder(self) -> None:
        if self.current_folder_path is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswählen.")
            return
        if not self.current_folder_exists:
            self._show_missing_file("Der Kundenordner wurde nicht gefunden.")
            return
        self._open_url(self.current_folder_path)

    def open_selected_file(self) -> None:
        row = self.files_table.currentRow()
        folder_file = self.files_by_row.get(row)
        if folder_file is None:
            self.status_label.setText("Bitte zuerst eine Datei im Kundenordner auswählen.")
            return
        path = folder_file.path
        if not path.exists():
            self._show_missing_file("Die Datei wurde nicht gefunden.")
            return
        self._open_url(path)

    def request_new_order_for_customer(self) -> None:
        if self.current_customer_id is None:
            self.status_label.setText("Bitte zuerst einen Kunden auswählen.")
            return
        self.new_order_requested.emit(self.current_customer_id)

    def request_new_order(self) -> None:
        self.request_new_order_for_customer()

    def _selected_order_id(self) -> int | None:
        return self.order_ids_by_row.get(self.orders_table.currentRow())

    def request_open_selected_order(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            self.status_label.setText("Bitte zuerst eine frühere Bestellung dieses Kunden auswählen.")
            return
        self.order_open_requested.emit(order_id)

    def request_delivery_note_for_selected_order(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            self.status_label.setText("Bitte zuerst eine Bestellung dieses Kunden auswählen.")
            return
        self.delivery_note_requested.emit(order_id)

    def request_invoice_for_selected_order(self) -> None:
        order_id = self._selected_order_id()
        if order_id is None:
            self.status_label.setText("Bitte zuerst eine Bestellung dieses Kunden auswählen.")
            return
        self.invoice_requested.emit(order_id)

    def update_action_state(self) -> None:
        has_customer = self.current_customer_id is not None
        has_folder = self.current_folder_path is not None and self.current_folder_exists
        selected_file = self.files_by_row.get(self.files_table.currentRow())
        has_file = selected_file is not None
        has_order = self._selected_order_id() is not None
        can_act = not self._is_customer_loading
        self.open_folder_button.setEnabled(can_act and has_folder)
        self.open_file_button.setEnabled(can_act and has_file)
        self.new_order_button.setEnabled(can_act and has_customer)
        self.open_order_button.setEnabled(can_act and has_order)
        if self.has_seed_quantities:
            self.new_order_button.setText("Bestellung neu")
        elif has_customer and not has_folder:
            self.new_order_button.setText("Leere Bestellung starten")
        else:
            self.new_order_button.setText("Bestellung neu")
        self.delivery_note_button.setEnabled(can_act and has_order)
        self.invoice_button.setEnabled(can_act and has_order)
        if self._is_customer_loading:
            self.seed_file_hint.setText("Kundenordner wird geladen...")
            return
        if selected_file is None:
            if not has_customer:
                self.seed_file_hint.setText("Kunde suchen, dann erscheinen letzte Mengen und passende Aktionen.")
            elif has_customer and not has_folder:
                self.seed_file_hint.setText(
                    "Kundenordner fehlt. Es kann nur eine leere Bestellung gestartet werden."
                )
            else:
                if self.has_seed_quantities:
                    self.seed_file_hint.setText("Letzte Mengen sind vorbereitet. Neue Bestellung starten und Mengen anpassen.")
                else:
                    self.seed_file_hint.setText("Noch keine letzten Mengen gefunden. Neue leere Bestellung starten.")
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

    def _invoice_warning_text(self, warning: CustomerInvoiceWarning) -> str:
        if warning.open_count == 0:
            return "Offene Rechnungen: keine"
        parts = [f"{warning.open_count} offen"]
        if warning.overdue_count:
            parts.append(f"{warning.overdue_count} überfällig")
        if warning.due_count:
            parts.append(f"{warning.due_count} heute fällig")
        return f"Offene Rechnungen: {', '.join(parts)} · {self._money(warning.amount_cents)}"

    def _text(self, value: object) -> str:
        return str(value or "").strip()

    def _open_url(self, path: Path) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _show_missing_file(self, message: str) -> None:
        QMessageBox.warning(self, "Kundenordner", message)
