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
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..schemas import DepositReturnCreate, DocumentLineItem
from ..services.order_service import create_order_delivery_order, create_order_invoice, get_order, list_active_orders
from .date_input import to_display_date
from .deposit_return_presets import DEPOSIT_RETURN_PRESETS
from .layouts import ContentSurface, PageHeader, ResponsiveSplitter, WorkspaceCard, configure_form_layout
from .searchable_select import SearchableSelect


DOCUMENT_WORKFLOW_ACTIONS = {
    "removeDocumentLineButton": "Position entfernen",
    "addDocumentDepositReturnButton": "Pfand-Rueckgabe eintragen",
    "removeDocumentDepositReturnButton": "Pfand-Rueckgabe entfernen",
}
DOCUMENT_LINE_COLUMNS = ("Artikel", "Menge", "Preis je Einheit EUR", "Pfand je Einheit EUR", "Summe EUR")
DOCUMENT_RETURN_COLUMNS = ("Pfandart", "Menge", "Pfand EUR", "Gutschrift EUR")

class DocumentWorkflowPanel(QWidget):
    document_type = ""
    number_label = ""
    note_label = "Freitext"
    default_note_text = ""
    create_excel_button_text = ""
    create_pdf_button_text = ""
    create_both_button_text = ""

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.order_ids_by_row = {}
        self.current_order_id = None
        self.last_excel_path: Path | None = None
        self.last_pdf_path: Path | None = None

        self.order_select = SearchableSelect("Kunde, Auftragsnummer oder Lieferdatum suchen")
        self.order_select.search_input.setObjectName("tableSearchField")
        self.order_select.setMaximumHeight(180)

        self.order_summary = QLabel("Noch kein Auftrag ausgewaehlt.")
        self.order_summary.setObjectName("sectionSubtitle")
        self.order_summary.setWordWrap(True)
        self.document_number = QLineEdit()
        self.document_number.setPlaceholderText(self.number_label)
        self.delivery_fee_choice = QComboBox()
        self.delivery_fee_choice.addItem("Nein", False)
        self.delivery_fee_choice.addItem("Ja", True)
        self.document_note = QLineEdit()
        self.document_note.setPlaceholderText(self.default_note_text)
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
        self.status_label = QLabel("Auftrag auswaehlen, Positionen pruefen, dann Excel oder PDF erstellen.")
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
                "Auftrag waehlen, Positionen bei Bedarf fuer diesen Beleg anpassen und Excel oder PDF separat erzeugen.",
            )
        )

        body = ResponsiveSplitter()
        layout.addWidget(body, 1)

        order_box, order_layout = self._section(
            "1. Auftrag suchen",
            "Kunde, Auftragsnummer oder Lieferdatum eingeben. Danach passenden Auftrag uebernehmen.",
        )
        order_layout.addWidget(self.order_select)
        refresh_row = QHBoxLayout()
        self.refresh_button = QPushButton("Liste aktualisieren")
        self.load_button = QPushButton("Auftrag uebernehmen")
        self.reset_order_button = QPushButton("Suche zuruecksetzen")
        refresh_row.addWidget(self.refresh_button)
        refresh_row.addWidget(self.load_button)
        refresh_row.addWidget(self.reset_order_button)
        refresh_row.addStretch()
        order_layout.addLayout(refresh_row)
        body.addWidget(order_box)

        document_box, document_layout = self._section(
            "2. Beleg pruefen",
            "Aendert nur diesen Beleg. Die gespeicherte Bestellung bleibt als Vorlage erhalten.",
        )
        document_layout.addWidget(self.order_summary)

        self.document_tabs = QTabWidget()
        document_layout.addWidget(self.document_tabs, 1)

        positions_tab = QWidget()
        positions_layout = QVBoxLayout(positions_tab)
        positions_layout.setContentsMargins(10, 10, 10, 10)
        positions_layout.addWidget(self.lines_table)
        line_action_row = QHBoxLayout()
        self.remove_line_button = QPushButton(DOCUMENT_WORKFLOW_ACTIONS["removeDocumentLineButton"])
        self.remove_line_button.setObjectName("dangerAction")
        line_action_row.addWidget(self.remove_line_button)
        line_action_row.addStretch()
        positions_layout.addLayout(line_action_row)
        total_bar = QWidget()
        total_bar.setObjectName("totalBar")
        total_layout = QHBoxLayout(total_bar)
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)
        self.document_tabs.addTab(positions_tab, "1 Positionen")

        deposit_tab = QWidget()
        deposit_layout = QVBoxLayout(deposit_tab)
        deposit_layout.setContentsMargins(10, 10, 10, 10)
        return_form = QFormLayout()
        configure_form_layout(return_form)
        return_form.addRow("Pfandart", self.deposit_return_select)
        return_form.addRow("Menge", self.deposit_return_quantity)
        return_form.addRow("Pfandwert EUR", self.deposit_return_eur)
        deposit_layout.addLayout(return_form)
        return_action_row = QHBoxLayout()
        self.add_return_button = QPushButton(DOCUMENT_WORKFLOW_ACTIONS["addDocumentDepositReturnButton"])
        self.remove_return_button = QPushButton(DOCUMENT_WORKFLOW_ACTIONS["removeDocumentDepositReturnButton"])
        self.remove_return_button.setObjectName("dangerAction")
        return_action_row.addWidget(self.add_return_button)
        return_action_row.addWidget(self.remove_return_button)
        return_action_row.addStretch()
        deposit_layout.addLayout(return_action_row)
        deposit_layout.addWidget(self.returns_table)
        self.document_tabs.addTab(deposit_tab, "2 Pfand")

        details_tab = QWidget()
        details_layout = QVBoxLayout(details_tab)
        details_layout.setContentsMargins(10, 10, 10, 10)
        number_form = QFormLayout()
        configure_form_layout(number_form)
        number_form.addRow(self.number_label, self.document_number)
        number_form.addRow("Lieferpauschale 3,90 EUR", self.delivery_fee_choice)
        number_form.addRow(self.note_label, self.document_note)
        details_layout.addLayout(number_form)
        details_layout.addStretch()
        self.document_tabs.addTab(details_tab, "3 Belegdaten")

        output_tab = QWidget()
        output_layout = QVBoxLayout(output_tab)
        output_layout.setContentsMargins(10, 10, 10, 10)
        action_row = QHBoxLayout()
        self.create_both_button = QPushButton(self.create_both_button_text)
        self.create_excel_button = QPushButton(self.create_excel_button_text)
        self.create_pdf_button = QPushButton(self.create_pdf_button_text)
        self.open_excel_button = QPushButton("Excel oeffnen")
        self.open_pdf_button = QPushButton("PDF oeffnen")
        self.open_excel_button.setEnabled(False)
        self.open_pdf_button.setEnabled(False)
        action_row.addWidget(self.create_both_button)
        action_row.addWidget(self.create_excel_button)
        action_row.addWidget(self.create_pdf_button)
        action_row.addWidget(self.open_excel_button)
        action_row.addWidget(self.open_pdf_button)
        action_row.addStretch()
        output_layout.addLayout(action_row)
        output_layout.addWidget(self.result_label)
        output_layout.addStretch()
        self.document_tabs.addTab(output_tab, "4 Ausgabe")
        document_layout.addWidget(total_bar)

        body.addWidget(document_box)
        body.setStretchFactor(0, 1)
        body.setStretchFactor(1, 2)
        layout.addWidget(self.status_label)

        self.refresh_button.clicked.connect(self.refresh_orders)
        self.load_button.clicked.connect(self.load_selected_order)
        self.reset_order_button.clicked.connect(self.reset_order_selection)
        self.remove_line_button.clicked.connect(self.remove_selected_line)
        self.add_return_button.clicked.connect(self.add_deposit_return)
        self.remove_return_button.clicked.connect(self.remove_selected_deposit_return)
        self.deposit_return_select.currentIndexChanged.connect(self.apply_selected_deposit_return)
        self.create_both_button.clicked.connect(self.create_complete_document)
        self.create_excel_button.clicked.connect(self.create_excel_document)
        self.create_pdf_button.clicked.connect(self.create_pdf_document)
        self.open_excel_button.clicked.connect(lambda: self._open_local_file(self.last_excel_path))
        self.open_pdf_button.clicked.connect(lambda: self._open_local_file(self.last_pdf_path))
        self.lines_table.itemChanged.connect(self.update_total)
        self.returns_table.itemChanged.connect(self.update_total)
        self.refresh_master_data()
        self.refresh_orders()
        self.apply_selected_deposit_return()

    def _button(self, object_name: str) -> QPushButton:
        return QPushButton(DOCUMENT_WORKFLOW_ACTIONS[object_name])

    def _section(self, title: str, subtitle: str) -> tuple[QWidget, QVBoxLayout]:
        box = WorkspaceCard(title, subtitle)
        return box, box.layout

    def refresh_master_data(self) -> None:
        return

    def refresh_orders(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            orders = list_active_orders(session)
        finally:
            session.close()
        self.order_ids_by_row = {}
        self.order_select.set_items(
            (
                (
                    f"{order.order_number} | {order.customer.name} | Lieferung {to_display_date(order.delivery_date)}",
                    order.id,
                    f"{order.status} {order.delivery_slot or ''}",
                )
                for order in orders
            )
        )
        self.status_label.setText(f"{len(orders)} Auftraege fuer die Suche geladen.")

    def load_selected_order(self) -> None:
        order_id = self.order_select.current_value()
        if order_id is None or self.session_factory is None:
            self.status_label.setText("Bitte zuerst einen Auftrag auswaehlen.")
            return
        self.select_order(order_id)

    def reset_order_selection(self) -> None:
        self.current_order_id = None
        self.order_select.set_search_text("")
        self.order_summary.setText("Noch kein Auftrag ausgewaehlt.")
        self.status_label.setText("Bitte Auftrag suchen und uebernehmen.")

    def select_order(self, order_id: int) -> None:
        if self.session_factory is None:
            return
        session = self.session_factory()
        try:
            order = get_order(session, order_id)
            self.current_order_id = order.id
            self.order_summary.setText(
                "Ausgewaehlter Auftrag: "
                f"{order.order_number} | {order.customer.name} | Lieferung {to_display_date(order.delivery_date)} | "
                f"{len(order.lines)} Positionen"
            )
            self.lines_table.setRowCount(0)
            self.returns_table.setRowCount(0)
            self.document_note.setText(self.default_note_text)
            for line in order.lines:
                self._append_line(line.product_name, line.quantity, line.unit_price_cents, line.deposit_cents)
            for deposit_return in order.deposit_returns:
                self._append_return(deposit_return.name, deposit_return.quantity, deposit_return.deposit_cents)
            self.status_label.setText("Auftrag uebernommen. Positionen pruefen und Beleg erstellen.")
        finally:
            session.close()

    def create_excel_document(self) -> None:
        self.create_document({"excel"})

    def create_pdf_document(self) -> None:
        self.create_document({"pdf"})

    def create_complete_document(self) -> None:
        self.create_document({"excel", "pdf"})

    def create_document(self, assets: set[str]) -> None:
        asset_label = self._created_asset_label(assets)
        if self.current_order_id is None:
            self.load_selected_order()
        if self.current_order_id is None:
            message = "Bitte zuerst einen Auftrag auswaehlen."
            self.status_label.setText(message)
            QMessageBox.warning(self, f"{self.document_type} erstellen", message)
            return
        if self.session_factory is None:
            message = "Keine Datenbankverbindung vorhanden."
            self.status_label.setText(message)
            QMessageBox.critical(self, "Erstellung fehlgeschlagen", message)
            return
        session = self.session_factory()
        try:
            document = self._create_document_for_order(session, assets=assets)
        except Exception as error:
            self.status_label.setText(f"Erstellung fehlgeschlagen: {error}")
            QMessageBox.critical(
                self,
                "Erstellung fehlgeschlagen",
                f"{self.document_type} konnte nicht als {asset_label} erstellt werden.\n\nGrund: {error}",
            )
            return
        finally:
            session.close()
        self.refresh_orders()
        self.last_excel_path = Path(document.excel_path)
        self.last_pdf_path = Path(document.pdf_path)
        self.open_excel_button.setEnabled(self.last_excel_path.exists())
        self.open_pdf_button.setEnabled(self.last_pdf_path.exists())
        self.result_label.setText(self._created_asset_result(asset_label))
        self.status_label.setText(
            f"Erfolgreich erstellt: {self.document_type} {document.document_number} als {asset_label}."
        )
        QMessageBox.information(
            self,
            f"{self.document_type} erstellt",
            f"{self.document_type} {document.document_number} wurde als {asset_label} erstellt.\n\n"
            f"Datei: {self._created_asset_path(asset_label)}",
        )

    def _created_asset_label(self, assets: set[str]) -> str:
        if assets == {"excel", "pdf"}:
            return "Excel + PDF"
        return "Excel" if assets == {"excel"} else "PDF"

    def _created_asset_result(self, asset_label: str) -> str:
        if asset_label == "Excel + PDF":
            return f"Excel + PDF erstellt:\nExcel: {self.last_excel_path}\nPDF: {self.last_pdf_path}"
        if asset_label == "Excel":
            return f"Excel erstellt:\nExcel: {self.last_excel_path}"
        return f"PDF erstellt:\nPDF: {self.last_pdf_path}"

    def _created_asset_path(self, asset_label: str) -> Path | None:
        if asset_label == "Excel + PDF":
            return self.last_pdf_path
        return self.last_excel_path if asset_label == "Excel" else self.last_pdf_path

    def _create_document_for_order(self, session, assets: set[str]):
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

    def _delivery_fee_enabled(self) -> bool:
        return bool(self.delivery_fee_choice.currentData())


class DeliveryNotePanel(DocumentWorkflowPanel):
    document_type = "Lieferscheine"
    number_label = "LS-Nummer"
    note_label = "Kommentar oben rechts"
    default_note_text = ""
    create_excel_button_text = "Excel-Lieferschein erstellen"
    create_pdf_button_text = "PDF-Lieferschein erstellen"
    create_both_button_text = "Lieferschein komplett erstellen"

    def _create_document_for_order(self, session, assets: set[str]):
        return create_order_delivery_order(
            session,
            self.current_order_id,
            self.document_number.text().strip(),
            line_items=self._line_items_from_table(),
            deposit_returns=self._deposit_returns_from_table(),
            delivery_fee_enabled=self._delivery_fee_enabled(),
            delivery_comment=self.document_note.text().strip() or None,
            footer_text=None,
            assets=assets,
        )


class InvoicePanel(DocumentWorkflowPanel):
    document_type = "Rechnungen"
    number_label = "Rechnungsnummer"
    note_label = "Rechnungstext unten"
    default_note_text = "Rechnungsbetrag wird per Sepa Basis Lastschrift Mandat eingezogen."
    create_excel_button_text = "Excel-Rechnung erstellen"
    create_pdf_button_text = "PDF-Rechnung erstellen"
    create_both_button_text = "Rechnung komplett erstellen"

    def _create_document_for_order(self, session, assets: set[str]):
        return create_order_invoice(
            session,
            self.current_order_id,
            self.document_number.text().strip(),
            line_items=self._line_items_from_table(),
            deposit_returns=self._deposit_returns_from_table(),
            delivery_fee_enabled=self._delivery_fee_enabled(),
            footer_text=self.document_note.text().strip() or None,
            datev_upload_dir=Path.cwd() / "outputs" / "datev_upload",
            assets=assets,
        )
