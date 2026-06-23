from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..services.document_archive_service import list_documents_by_type
from .date_input import to_display_date
from .layouts import ContentSurface, PageHeader, WorkspaceCard


DOCUMENT_ARCHIVE_COLUMNS = ("Lieferdatum", "Belegnummer", "Kunde", "Excel-Datei", "PDF-Datei", "Kundenordner", "Status")
DOCUMENT_ARCHIVE_ACTIONS = {
    "openExcelButton": "Excel oeffnen",
    "openPdfButton": "PDF oeffnen",
    "openFolderButton": "Ordner oeffnen",
}


class DocumentArchivePanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.invoice_ids_by_row = {}
        self.delivery_note_ids_by_row = {}
        self.documents_by_id = {}
        self.invoice_action_buttons = []
        self.delivery_note_action_buttons = []

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout
        layout.addWidget(
            PageHeader(
                "Belegarchiv",
                "Bisher erstellte Rechnungen und Lieferscheine finden, Excel/PDF oeffnen oder direkt in den Kundenordner springen.",
            )
        )

        self.search_field = QLineEdit()
        self.search_field.setObjectName("tableSearchField")
        self.search_field.setPlaceholderText("Kunde, Nummer oder Datum suchen")
        search_box = WorkspaceCard("Suchen", "Tippen reicht: Kunde, Rechnungsnummer, Lieferscheinnummer oder Datum.")
        search_box.layout.addWidget(self.search_field)
        layout.addWidget(search_box)

        self.invoice_table = self._document_table()
        invoice_box = WorkspaceCard(
            "Bereits erstellte Rechnungen",
            "Eine Rechnung markieren und dann Excel, PDF oder Ordner oeffnen.",
        )
        invoice_box.layout.addWidget(self.invoice_table)
        invoice_box.layout.addLayout(self._action_row(self.invoice_table, self.invoice_ids_by_row, self.invoice_action_buttons))
        layout.addWidget(invoice_box)

        self.delivery_note_table = self._document_table()
        delivery_box = WorkspaceCard(
            "Bereits erstellte Lieferscheine",
            "Einen Lieferschein markieren und dann Excel, PDF oder Ordner oeffnen.",
        )
        delivery_box.layout.addWidget(self.delivery_note_table)
        delivery_box.layout.addLayout(
            self._action_row(self.delivery_note_table, self.delivery_note_ids_by_row, self.delivery_note_action_buttons)
        )
        layout.addWidget(delivery_box)

        self.status_label = QLabel("Noch keine Belege geladen.")
        self.status_label.setObjectName("muted")
        layout.addWidget(self.status_label)

        self.search_field.textChanged.connect(self.apply_search)
        self.invoice_table.itemSelectionChanged.connect(self.update_action_buttons)
        self.delivery_note_table.itemSelectionChanged.connect(self.update_action_buttons)
        self.refresh_archive()

    def _document_table(self) -> QTableWidget:
        table = QTableWidget(0, len(DOCUMENT_ARCHIVE_COLUMNS))
        table.setHorizontalHeaderLabels(DOCUMENT_ARCHIVE_COLUMNS)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
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
                }
                for document in [*invoices, *delivery_notes]
            }
            self._show_documents(self.invoice_table, self.invoice_ids_by_row, invoices)
            self._show_documents(self.delivery_note_table, self.delivery_note_ids_by_row, delivery_notes)
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
        visible_counts = []
        for table in (self.invoice_table, self.delivery_note_table):
            table.clearSelection()
            visible_count = 0
            for row in range(table.rowCount()):
                row_matches = self._row_matches_query(table, row, query)
                table.setRowHidden(row, not row_matches)
                if row_matches:
                    visible_count += 1
            visible_counts.append(visible_count)
        self.update_action_buttons()
        if query:
            total = sum(visible_counts)
            self.status_label.setText(
                f"{total} Belege gefunden: {visible_counts[0]} Rechnungen und {visible_counts[1]} Lieferscheine."
            )

    def _row_matches_query(self, table: QTableWidget, row: int, query: str) -> bool:
        if not query:
            return True
        for column in range(table.columnCount()):
            item = table.item(row, column)
            if item is not None and query in item.text().lower():
                return True
        return False

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

    def _open_selected_path(self, table: QTableWidget, row_map: dict[int, int], path_key: str, error_message: str) -> None:
        document = self._selected_document(table, row_map)
        if document is None:
            return
        path = document[path_key]
        if not path.exists():
            self._show_missing_file(error_message)
            return
        self._open_url(path, path.name)

    def _selected_document(self, table: QTableWidget, row_map: dict[int, int]) -> dict | None:
        row = table.currentRow()
        document_id = row_map.get(row)
        if document_id is None or not table.selectedItems() or table.isRowHidden(row):
            QMessageBox.warning(self, "Beleg auswaehlen", "Bitte zuerst einen Beleg in der Tabelle auswaehlen.")
            return None
        document = self.documents_by_id.get(document_id)
        if document is None:
            QMessageBox.warning(self, "Beleg nicht gefunden", "Der Beleg wurde nicht gefunden. Bitte die Liste aktualisieren.")
            return None
        return document

    def update_action_buttons(self) -> None:
        self._set_action_buttons_enabled(
            self.invoice_action_buttons,
            self._has_visible_selection(self.invoice_table, self.invoice_ids_by_row),
        )
        self._set_action_buttons_enabled(
            self.delivery_note_action_buttons,
            self._has_visible_selection(self.delivery_note_table, self.delivery_note_ids_by_row),
        )

    def _has_visible_selection(self, table: QTableWidget, row_map: dict[int, int]) -> bool:
        row = table.currentRow()
        return bool(table.selectedItems()) and row in row_map and not table.isRowHidden(row)

    def _set_action_buttons_enabled(self, buttons: list[QPushButton], enabled: bool) -> None:
        for button in buttons:
            button.setEnabled(enabled)

    def _open_url(self, path: Path, label: str) -> None:
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):
            self._show_missing_file(f"{label} konnte nicht geoeffnet werden.")
            return
        self.status_label.setText(f"Geoeffnet: {label}")

    def _show_missing_file(self, message: str) -> None:
        self.status_label.setText(message)
        QMessageBox.warning(
            self,
            "Datei nicht gefunden",
            f"{message}\n\nBitte pruefen, ob der Kundenordner verschoben wurde oder die Datei neu erstellt werden muss.",
        )
