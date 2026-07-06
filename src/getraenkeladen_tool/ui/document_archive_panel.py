from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..services.document_archive_service import list_documents_by_type, regenerate_document_asset
from .date_input import to_display_date
from .layouts import ContentSurface, PageHeader, WorkspaceCard


DOCUMENT_ARCHIVE_COLUMNS = ("Art", "Lieferdatum", "Belegnummer", "Kunde", "Excel-Datei", "PDF-Datei", "Kundenordner", "Status")
DOCUMENT_ARCHIVE_ACTIONS = {
    "openExcelButton": "Excel öffnen",
    "openPdfButton": "PDF öffnen",
    "openFolderButton": "Ordner öffnen",
}


class DocumentArchivePanel(QWidget):
    document_open_requested = Signal(str, int)
    order_open_requested = Signal(int)

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.document_ids_by_row = {}
        self.documents_by_id = {}
        self.document_action_buttons = []

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout
        layout.addWidget(
            PageHeader(
                "Belegarchiv",
                "Bisher erstellte Rechnungen und Lieferscheine finden, Excel/PDF öffnen oder direkt in den Kundenordner springen.",
            )
        )

        self.search_field = QLineEdit()
        self.search_field.setObjectName("tableSearchField")
        self.search_field.setPlaceholderText("Kunde, Nummer oder Datum suchen")
        self.document_filter = QComboBox()
        self.document_filter.addItem("Alle Belege", "all")
        self.document_filter.addItem("Nur Rechnungen", "Rechnung")
        self.document_filter.addItem("Nur Lieferscheine", "Lieferschein")
        self.document_filter.addItem("Fehlende Dateien", "missing")
        search_box = WorkspaceCard(
            "Suchen",
            "Rechnungen und Lieferscheine gemeinsam durchsuchen. Tippen reicht: Kunde, Nummer oder Datum.",
        )
        search_box.layout.addWidget(self.search_field)
        search_box.layout.addWidget(self.document_filter)
        self.context_hint = QLabel("Alle Aktionen stehen auch als Buttons bereit. Rechtsklick bietet zusaetzlich Neu-Erzeugen.")
        self.context_hint.setObjectName("sectionSubtitle")
        search_box.layout.addWidget(self.context_hint)
        layout.addWidget(search_box)

        self.document_table = self._document_table()
        self.document_table.customContextMenuRequested.connect(
            lambda position: self.show_document_context_menu(self.document_table, self.document_ids_by_row, position)
        )
        archive_box = WorkspaceCard(
            "Alle Belege",
            "Eine gemeinsame Liste für Rechnungen und Lieferscheine. Beleg markieren und Aktion wählen.",
        )
        archive_box.layout.addWidget(self.document_table)
        archive_box.layout.addLayout(self._action_row(self.document_table, self.document_ids_by_row, self.document_action_buttons))
        layout.addWidget(archive_box, 1)

        self.status_label = QLabel("Noch keine Belege geladen.")
        self.status_label.setObjectName("muted")
        layout.addWidget(self.status_label)

        self.search_field.textChanged.connect(self.apply_search)
        self.document_filter.currentIndexChanged.connect(self.apply_search)
        self.document_table.itemSelectionChanged.connect(self.update_action_buttons)
        self.refresh_archive()

    def _document_table(self) -> QTableWidget:
        table = QTableWidget(0, len(DOCUMENT_ARCHIVE_COLUMNS))
        table.setHorizontalHeaderLabels(DOCUMENT_ARCHIVE_COLUMNS)
        header = table.horizontalHeader()
        header.setMinimumSectionSize(96)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Interactive)
        table.setColumnWidth(1, 180)
        table.setColumnWidth(6, 190)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.setMinimumHeight(220)
        return table

    def _action_row(self, table: QTableWidget, row_map: dict[int, int], buttons: list[QPushButton]) -> QHBoxLayout:
        row = QHBoxLayout()
        excel_button = self._button("openExcelButton")
        pdf_button = self._button("openPdfButton")
        folder_button = self._button("openFolderButton")
        buttons.extend((excel_button, pdf_button, folder_button))
        excel_button.clicked.connect(lambda: self.open_selected_excel(table, row_map))
        pdf_button.clicked.connect(lambda: self.open_selected_pdf(table, row_map))
        folder_button.clicked.connect(lambda: self.open_selected_folder(table, row_map))
        row.addWidget(excel_button)
        row.addWidget(pdf_button)
        row.addWidget(folder_button)
        row.addStretch()
        return row

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(DOCUMENT_ARCHIVE_ACTIONS[object_name])
        button.setObjectName(object_name)
        button.setEnabled(False)
        return button

    def refresh_archive(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            invoices = list_documents_by_type(session, "Rechnung")
            delivery_notes = list_documents_by_type(session, "Lieferschein")
            self.documents_by_id = {
                document.id: {
                    "excel_path": Path(document.excel_path),
                    "pdf_path": Path(document.pdf_path),
                    "customer_name": document.customer.name,
                    "document_number": document.document_number,
                    "document_type": document.document_type,
                    "order_id": document.order_id,
                }
                for document in [*invoices, *delivery_notes]
            }
            documents = sorted(
                [*invoices, *delivery_notes],
                key=lambda document: (document.delivery_date, document.document_type, document.document_number),
                reverse=True,
            )
            self._show_documents(self.document_table, self.document_ids_by_row, documents)
        finally:
            session.close()
        self.apply_search()
        self.status_label.setText(f"{len(invoices)} Rechnungen und {len(delivery_notes)} Lieferscheine geladen.")

    def _show_documents(self, table: QTableWidget, row_map: dict[int, int], documents: list) -> None:
        row_map.clear()
        table.setRowCount(len(documents))
        for row, document in enumerate(documents):
            row_map[row] = document.id
            excel_path = Path(document.excel_path)
            pdf_path = Path(document.pdf_path)
            folder_path = excel_path.parent
            values = (
                document.document_type,
                to_display_date(document.delivery_date),
                document.document_number,
                document.customer.name,
                "vorhanden" if excel_path.exists() else "fehlt",
                "vorhanden" if pdf_path.exists() else "fehlt",
                "vorhanden" if folder_path.exists() else "fehlt",
                self._status_text(excel_path, pdf_path, folder_path),
            )
            self._set_row(table, row, values)

    def _set_row(self, table: QTableWidget, row: int, values: tuple[str, ...]) -> None:
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setToolTip(value)
            table.setItem(row, column, item)

    def _status_text(self, excel_path: Path, pdf_path: Path, folder_path: Path) -> str:
        if excel_path.exists() and pdf_path.exists():
            return "Excel und PDF vorhanden"
        if not folder_path.exists():
            return "Ordner fehlt"
        missing = []
        if not excel_path.exists():
            missing.append("Excel fehlt")
        if not pdf_path.exists():
            missing.append("PDF fehlt")
        return ", ".join(missing)

    def apply_search(self) -> None:
        query = self.search_field.text().strip().lower()
        filter_value = self.document_filter.currentData()
        table = self.document_table
        table.clearSelection()
        visible_count = 0
        for row in range(table.rowCount()):
            row_matches = self._row_matches_query(table, row, query) and self._row_matches_filter(table, row, filter_value)
            table.setRowHidden(row, not row_matches)
            if row_matches:
                visible_count += 1
        self.update_action_buttons()
        if query:
            self.status_label.setText(f"{visible_count} Belege gefunden.")

    def _row_matches_filter(self, table: QTableWidget, row: int, filter_value: str) -> bool:
        if filter_value == "all":
            return True
        if filter_value == "missing":
            return "fehlt" in self._item_text(table, row, 7).lower()
        return self._item_text(table, row, 0) == filter_value

    def _row_matches_query(self, table: QTableWidget, row: int, query: str) -> bool:
        if not query:
            return True
        for column in range(table.columnCount()):
            item = table.item(row, column)
            if item is not None and query in item.text().lower():
                return True
        return False

    def _item_text(self, table: QTableWidget, row: int, column: int) -> str:
        item = table.item(row, column)
        return item.text() if item is not None else ""

    def open_selected_excel(self, table: QTableWidget, row_map: dict[int, int]) -> None:
        self._open_selected_path(table, row_map, "excel_path", "Die Excel-Datei wurde nicht gefunden.")

    def open_selected_pdf(self, table: QTableWidget, row_map: dict[int, int]) -> None:
        self._open_selected_path(table, row_map, "pdf_path", "Die PDF-Datei wurde nicht gefunden.")

    def open_selected_folder(self, table: QTableWidget, row_map: dict[int, int]) -> None:
        document = self._selected_document(table, row_map)
        if document is None:
            return
        folder_path = document["excel_path"].parent
        if not folder_path.exists():
            self._show_missing_file("Der Kundenordner wurde nicht gefunden.")
            return
        self._open_url(folder_path, "Ordner")

    def show_document_context_menu(self, table: QTableWidget, row_map: dict[int, int], position) -> None:
        clicked_row = table.indexAt(position).row()
        if clicked_row >= 0:
            table.setCurrentCell(clicked_row, 0)
        document = self._selected_document(table, row_map, warn=False)
        if document is None:
            return
        menu = QMenu(self)
        pdf_action = menu.addAction("PDF öffnen")
        excel_action = menu.addAction("Excel öffnen")
        folder_action = menu.addAction("Kundenordner öffnen")
        menu.addSeparator()
        regenerate_pdf_action = menu.addAction("PDF neu erzeugen")
        regenerate_excel_action = menu.addAction("Excel neu erzeugen")
        regenerate_pdf_action.setEnabled(not document["pdf_path"].exists())
        regenerate_excel_action.setEnabled(not document["excel_path"].exists())
        regenerate_pdf_action.setToolTip("Nur aktiv, wenn die PDF-Datei fehlt.")
        regenerate_excel_action.setToolTip("Nur aktiv, wenn die Excel-Datei fehlt.")
        menu.addSeparator()
        document_label = "Im Belegbereich öffnen"
        open_document_action = menu.addAction(document_label)
        open_order_action = menu.addAction("Zugehörige Bestellung öffnen")
        open_order_action.setEnabled(document["order_id"] is not None)
        selected = menu.exec(table.viewport().mapToGlobal(position))
        if selected == pdf_action:
            self.open_selected_pdf(table, row_map)
        elif selected == excel_action:
            self.open_selected_excel(table, row_map)
        elif selected == folder_action:
            self.open_selected_folder(table, row_map)
        elif selected == regenerate_pdf_action:
            self.regenerate_selected_asset(table, row_map, "pdf")
        elif selected == regenerate_excel_action:
            self.regenerate_selected_asset(table, row_map, "excel")
        elif selected == open_document_action:
            self.open_selected_document_workflow(document)
        elif selected == open_order_action and document["order_id"] is not None:
            self.order_open_requested.emit(document["order_id"])

    def regenerate_selected_asset(self, table: QTableWidget, row_map: dict[int, int], asset: str) -> None:
        document_id = self._selected_document_id(table, row_map)
        if document_id is None:
            return
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            document = regenerate_document_asset(session, document_id, asset)
            document_number = document.document_number
        except Exception as error:
            QMessageBox.critical(
                self,
                "Datei konnte nicht neu erstellt werden",
                f"Die Datei konnte nicht neu erstellt werden.\n\nGrund: {error}\n\n"
                "Die vorhandenen Belegdaten wurden nicht verändert.",
            )
            self.status_label.setText(f"Neu-Erzeugung fehlgeschlagen: {error}")
            return
        finally:
            session.close()
        asset_label = "PDF" if asset == "pdf" else "Excel"
        self.refresh_archive()
        self.status_label.setText(f"{asset_label} neu erstellt und im Kundenordner abgelegt.")
        QMessageBox.information(
            self,
            f"{asset_label} neu erstellt",
            f"{asset_label} für {document_number} wurde neu erstellt und im Kundenordner abgelegt.",
        )

    def open_selected_document_workflow(self, document: dict) -> None:
        order_id = document.get("order_id")
        if order_id is None:
            QMessageBox.warning(
                self,
                "Bestellung nicht gefunden",
                "Die ursprüngliche Bestellung wurde nicht gefunden. Bitte Datei manuell prüfen.",
            )
            return
        self.document_open_requested.emit(document["document_type"], order_id)

    def _open_selected_path(self, table: QTableWidget, row_map: dict[int, int], path_key: str, error_message: str) -> None:
        document = self._selected_document(table, row_map)
        if document is None:
            return
        path = document[path_key]
        if not path.exists():
            self._show_missing_file(error_message)
            return
        self._open_url(path, path.name)

    def _selected_document_id(self, table: QTableWidget, row_map: dict[int, int], warn: bool = True) -> int | None:
        row = table.currentRow()
        document_id = row_map.get(row)
        if document_id is None or not table.selectedItems() or table.isRowHidden(row):
            if warn:
                QMessageBox.warning(self, "Beleg auswählen", "Bitte zuerst einen Beleg in der Tabelle auswählen.")
            return None
        return document_id

    def _selected_document(self, table: QTableWidget, row_map: dict[int, int], warn: bool = True) -> dict | None:
        document_id = self._selected_document_id(table, row_map, warn=warn)
        if document_id is None:
            return None
        document = self.documents_by_id.get(document_id)
        if document is None:
            QMessageBox.warning(self, "Beleg nicht gefunden", "Der Beleg wurde nicht gefunden. Bitte die Liste aktualisieren.")
            return None
        return document

    def update_action_buttons(self) -> None:
        self._set_action_buttons_enabled(
            self.document_action_buttons,
            self._has_visible_selection(self.document_table, self.document_ids_by_row),
        )

    def _has_visible_selection(self, table: QTableWidget, row_map: dict[int, int]) -> bool:
        row = table.currentRow()
        return bool(table.selectedItems()) and row in row_map and not table.isRowHidden(row)

    def _set_action_buttons_enabled(self, buttons: list[QPushButton], enabled: bool) -> None:
        for button in buttons:
            button.setEnabled(enabled)

    def _open_url(self, path: Path, label: str) -> None:
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):
            self._show_missing_file(f"{label} konnte nicht geöffnet werden.")
            return
        self.status_label.setText(f"Geoeffnet: {label}")

    def _show_missing_file(self, message: str) -> None:
        self.status_label.setText(message)
        QMessageBox.warning(
            self,
            "Datei nicht gefunden",
            f"{message}\n\nBitte prüfen, ob der Kundenordner verschoben wurde oder die Datei neu erstellt werden muss.",
        )
