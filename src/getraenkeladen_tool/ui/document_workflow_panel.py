from pathlib import Path
from datetime import date, timedelta

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
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

from ..kern.regeln.beleg import BelegParameter, PfandRueckgabe, Position, berechne_beleg
from ..schemas import DepositReturnCreate, DocumentLineItem
from ..services.automation_service import verify_document_assets
from ..services.number_suggestion_service import suggest_document_number
from ..services.order_service import create_order_delivery_order, create_order_invoice, get_order, list_active_orders
from .date_input import to_display_date
from .deposit_return_presets import DEPOSIT_RETURN_PRESETS
from .layouts import ContentSurface, PageHeader, ResponsiveSplitter, WorkspaceCard, configure_form_layout
from .searchable_select import SearchableSelect


DOCUMENT_WORKFLOW_ACTIONS = {
    "suggestDocumentNumberButton": "Nummer vorschlagen",
    "removeDocumentLineButton": "Position entfernen",
    "addDocumentDepositReturnButton": "Pfand-Rückgabe eintragen",
    "removeDocumentDepositReturnButton": "Pfand-Rückgabe entfernen",
}
DOCUMENT_LINE_COLUMNS = ("Artikel", "Menge", "Preis je Einheit EUR", "Pfand je Einheit EUR", "Summe EUR")
DOCUMENT_RETURN_COLUMNS = ("Pfandart", "Menge", "Pfand EUR", "Gutschrift EUR")

class DocumentWorkflowPanel(QWidget):
    back_requested = Signal()
    document_created = Signal(int)
    document_type = ""
    document_singular = ""
    page_title = ""
    number_label = ""
    note_label = "Freitext"
    default_note_text = ""
    create_excel_button_text = ""
    create_pdf_button_text = ""
    create_both_button_text = ""
    show_work_overview_button = False

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.order_ids_by_row = {}
        self.current_order_id = None
        self.last_excel_path: Path | None = None
        self.last_pdf_path: Path | None = None

        self.order_select = SearchableSelect("Kunde, Bestellnummer oder Lieferdatum suchen")
        self.order_select.search_input.setObjectName("tableSearchField")
        self.order_select.setMaximumHeight(180)

        self.order_summary = QLabel("Noch keine Bestellung ausgewählt.")
        self.order_summary.setObjectName("sectionSubtitle")
        self.order_summary.setWordWrap(True)
        self.document_number = QLineEdit()
        self.document_number.setPlaceholderText(self.number_label)
        self.suggest_document_number_button = self._button("suggestDocumentNumberButton")
        self.delivery_fee_choice = QComboBox()
        self.delivery_fee_choice.addItem("Keine Pauschale", False)
        self.delivery_fee_choice.addItem("3,90 EUR hinzufügen", True)
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
        self.total_label = QLabel("Gesamtsumme: 0,00 EUR")
        self.total_label.setObjectName("stepTitle")
        self.status_label = QLabel("Bestellung auswählen, Artikel prüfen, dann als Excel oder PDF erstellen.")
        self.status_label.setObjectName("muted")
        self.result_label = QLabel("Noch keine Datei erstellt.")
        self.result_label.setObjectName("sectionSubtitle")
        self.result_label.setWordWrap(True)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        page_action = None
        if self.show_work_overview_button:
            self.back_button = QPushButton("Zurück zur Übersicht")
            self.back_button.setObjectName("secondaryActionButton")
            self.back_button.clicked.connect(lambda _checked=False: self.back_requested.emit())
            page_action = self.back_button

        layout.addWidget(
            PageHeader(
                self.page_title or self.document_type,
                "Die Bestellung kommt aus der Kunden-Excel/Vorlage. Mengen, Preise und Pfand prüfen, dann Excel oder PDF erstellen.",
                page_action,
            )
        )

        body = ResponsiveSplitter()
        layout.addWidget(body, 1)

        order_box, order_layout = self._section(
            "1. Kundenbestellung suchen",
            "Kunde, Bestellnummer oder Lieferdatum eingeben. Danach diese Bestellung verwenden.",
            tone="route",
            kicker="AUSGANG",
        )
        self.order_box = order_box
        order_layout.addWidget(self.order_select)
        refresh_row = QHBoxLayout()
        self.refresh_button = QPushButton("Liste aktualisieren")
        self.load_button = QPushButton("Diese Bestellung verwenden")
        self.reset_order_button = QPushButton("Suche zurücksetzen")
        refresh_row.addWidget(self.refresh_button)
        refresh_row.addWidget(self.load_button)
        refresh_row.addWidget(self.reset_order_button)
        refresh_row.addStretch()
        order_layout.addLayout(refresh_row)
        body.addWidget(order_box)

        document_box, document_layout = self._section(
            "2. Artikel und Beträge prüfen",
            "Nur Beleg-Korrektur: Diese Änderungen speichern keine neue Vorlage im Kundenordner.",
            tone="document",
            kicker="BELEGWERKSTATT",
        )
        document_layout.addWidget(self.order_summary)

        self.create_both_button = QPushButton(self.create_both_button_text)
        self.create_both_button.setObjectName("primaryAction")

        self.document_tabs = QTabWidget()
        self.document_tabs.setUsesScrollButtons(False)
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
        self.document_tabs.addTab(positions_tab, "Artikel prüfen")

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
        self.document_tabs.addTab(deposit_tab, "Pfand")

        output_tab = QWidget()
        output_layout = QVBoxLayout(output_tab)
        output_layout.setContentsMargins(10, 10, 10, 10)
        self.create_excel_button = QPushButton(self.create_excel_button_text)
        self.create_pdf_button = QPushButton(self.create_pdf_button_text)
        self.open_excel_button = QPushButton("Excel öffnen")
        self.open_pdf_button = QPushButton("PDF öffnen")
        self.open_excel_button.setEnabled(False)
        self.open_pdf_button.setEnabled(False)
        normal_hint = QLabel("Normalerweise reicht der Hauptbutton: Excel und PDF zusammen erstellen.")
        normal_hint.setObjectName("sectionSubtitle")
        normal_hint.setWordWrap(True)
        output_layout.addWidget(normal_hint)
        self.more_output_box = QGroupBox("Weitere Optionen")
        self.more_output_box.setCheckable(True)
        self.more_output_box.setChecked(False)
        more_output_layout = QVBoxLayout(self.more_output_box)
        secondary_action_row = QHBoxLayout()
        secondary_action_row.addWidget(self.create_excel_button)
        secondary_action_row.addWidget(self.create_pdf_button)
        secondary_action_row.addWidget(self.open_excel_button)
        secondary_action_row.addWidget(self.open_pdf_button)
        secondary_action_row.addStretch()
        more_output_layout.addLayout(secondary_action_row)
        output_layout.addWidget(self.more_output_box)
        output_layout.addWidget(self.result_label)
        output_layout.addStretch()
        self.document_tabs.addTab(output_tab, "Ausgabe")
        document_layout.addWidget(total_bar)

        finish_bar = QWidget()
        finish_bar.setObjectName("documentFinishBar")
        finish_layout = QHBoxLayout(finish_bar)
        finish_layout.setContentsMargins(0, 0, 0, 0)
        finish_form = QFormLayout()
        configure_form_layout(finish_form)
        document_number_row = QHBoxLayout()
        document_number_row.addWidget(self.document_number)
        document_number_row.addWidget(self.suggest_document_number_button)
        finish_form.addRow(self.number_label, document_number_row)
        finish_form.addRow("Lieferpauschale hinzufügen?", self.delivery_fee_choice)
        finish_form.addRow(self.note_label, self.document_note)
        finish_layout.addLayout(finish_form, 1)
        finish_layout.addWidget(self.create_both_button)
        document_layout.addWidget(finish_bar)

        body.addWidget(document_box)
        body.setStretchFactor(0, 1)
        body.setStretchFactor(1, 2)
        layout.addWidget(self.status_label)

        self.refresh_button.clicked.connect(self.refresh_orders)
        self.load_button.clicked.connect(self.load_selected_order)
        self.reset_order_button.clicked.connect(self.reset_order_selection)
        self.suggest_document_number_button.clicked.connect(self.apply_suggested_document_number)
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

    def _section(self, title: str, subtitle: str, tone: str = "default", kicker: str = "") -> tuple[QWidget, QVBoxLayout]:
        box = WorkspaceCard(title, subtitle, tone=tone, kicker=kicker)
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
        self.status_label.setText(f"{len(orders)} Bestellungen für die Suche geladen.")

    def load_selected_order(self) -> None:
        order_id = self.order_select.current_value()
        if order_id is None or self.session_factory is None:
            self.status_label.setText("Bitte zuerst eine Bestellung auswählen.")
            return
        self.select_order(order_id)

    def reset_order_selection(self) -> None:
        self.current_order_id = None
        self.order_box.setVisible(True)
        self.order_select.set_search_text("")
        self.order_summary.setText("Noch keine Bestellung ausgewählt.")
        self.status_label.setText("Bitte Kundenbestellung suchen und verwenden.")

    def select_order(self, order_id: int) -> None:
        if self.session_factory is None:
            return
        session = self.session_factory()
        try:
            order = get_order(session, order_id)
            self.current_order_id = order.id
            self.order_box.setVisible(False)
            self.order_summary.setText(
                "Ausgewählte Bestellung: "
                f"{order.order_number} | {order.customer.name} | Lieferung {to_display_date(order.delivery_date)} | "
                f"{len(order.lines)} Positionen"
            )
            self.lines_table.setRowCount(0)
            self.returns_table.setRowCount(0)
            self.document_note.setText(self._default_note_for_order(order))
            for line in order.lines:
                self._append_line(line.product_name, line.quantity, line.unit_price_cents, line.deposit_cents)
            for deposit_return in order.deposit_returns:
                self._append_return(deposit_return.name, deposit_return.quantity, deposit_return.deposit_cents)
            self.status_label.setText("Bestellung verwendet. Artikel prüfen und danach Excel oder PDF erstellen.")
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
            message = "Bitte zuerst eine Bestellung auswählen."
            self.status_label.setText(message)
            QMessageBox.warning(self, f"{self._document_name()} erstellen", message)
            return
        if self.session_factory is None:
            message = "Keine Datenbankverbindung vorhanden."
            self.status_label.setText(message)
            QMessageBox.critical(self, "Erstellung fehlgeschlagen", message)
            return
        session = self.session_factory()
        try:
            document = self._create_document_for_order(session, assets=assets)
            verification = verify_document_assets(session, document.id, expected_assets=assets)
        except Exception as error:
            self.status_label.setText(f"Erstellung fehlgeschlagen: {error}")
            QMessageBox.critical(
                self,
                "Erstellung fehlgeschlagen",
                f"{self._document_name()} konnte nicht als {asset_label} erstellt werden.\n\nGrund: {error}",
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
        check_text = "Belegprüfung: OK." if verification.ok else "Belegprüfung: Bitte Dateien prüfen."
        self.status_label.setText(
            f"Erfolgreich erstellt: {self._document_name()} {document.document_number} als {asset_label}. {check_text}"
        )
        self.document_created.emit(document.id)
        QMessageBox.information(
            self,
            f"{self._document_name()} erstellt",
            f"{self._document_name()} {document.document_number} wurde als {asset_label} erstellt.\n\n"
            f"Datei: {self._created_asset_path(asset_label)}\n\n{check_text}",
        )

    def _document_name(self) -> str:
        return self.document_singular or self.document_type

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

    def _default_note_for_order(self, order) -> str:
        return self.default_note_text

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
            self.status_label.setText("Bitte Menge und Pfandwert größer 0 eintragen.")
            return
        self._append_return(name, quantity, deposit_cents)
        self.status_label.setText("Pfandrückgabe für diese Ausgabe hinzugefügt.")

    def apply_selected_deposit_return(self) -> None:
        cents = self.deposit_return_select.currentData()
        if cents is None:
            return
        self.deposit_return_eur.setText(f"{int(cents) / 100:.2f}".replace(".", ","))

    def apply_suggested_document_number(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            suggestion = suggest_document_number(
                session,
                self.document_singular,
                fallback_date=date.today().isoformat(),
            )
        finally:
            session.close()
        self.document_number.setText(suggestion)
        self.status_label.setText(f"Vorschlag übernommen: {suggestion}. Die Nummer kann frei geändert werden.")

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
        self.lines_table.blockSignals(True)
        self.returns_table.blockSignals(True)
        try:
            result = berechne_beleg(
                positionen=[
                    Position(
                        self._item_text(self.lines_table.item(row, 0)),
                        self._parse_int(self.lines_table.item(row, 1)),
                        self._parse_euro_cents_or_zero(self._item_text(self.lines_table.item(row, 2))),
                        self._parse_euro_cents_or_zero(self._item_text(self.lines_table.item(row, 3))),
                    )
                    for row in range(self.lines_table.rowCount())
                    if self._item_text(self.lines_table.item(row, 0)).strip()
                ],
                ruecknahmen=[
                    PfandRueckgabe(
                        self._item_text(self.returns_table.item(row, 0)),
                        self._parse_int(self.returns_table.item(row, 1)),
                        self._parse_euro_cents_or_zero(self._item_text(self.returns_table.item(row, 2))),
                    )
                    for row in range(self.returns_table.rowCount())
                    if self._item_text(self.returns_table.item(row, 0)).strip()
                ],
                parameter=BelegParameter(lieferpauschale_aktiv=self._delivery_fee_enabled()),
            )
            for row in range(self.lines_table.rowCount()):
                total = result.positionssummen_cents[row] if row < len(result.positionssummen_cents) else 0
                self._set_total_item(self.lines_table, row, 4, total)
            for row in range(self.returns_table.rowCount()):
                total = result.ruecknahme_summen_cents[row] if row < len(result.ruecknahme_summen_cents) else 0
                self._set_total_item(self.returns_table, row, 3, total)
        finally:
            self.lines_table.blockSignals(False)
            self.returns_table.blockSignals(False)
        self.total_label.setText(f"Gesamtsumme: {self._format_euro_cents(result.brutto_cents)}")

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
    document_singular = "Lieferschein"
    page_title = "Lieferschein aus Bestellung erstellen"
    number_label = "Lieferschein-Nummer"
    note_label = "Hinweis auf dem Lieferschein"
    default_note_text = ""
    create_excel_button_text = "Nur Excel-Lieferschein"
    create_pdf_button_text = "Nur PDF-Lieferschein"
    create_both_button_text = "Lieferschein als Excel + PDF erstellen"

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
    document_singular = "Rechnung"
    page_title = "Rechnung aus Bestellung erstellen"
    number_label = "Rechnungsnummer"
    note_label = "Zahlungshinweis auf Rechnung"
    default_note_text = "Rechnungsbetrag wird per Sepa Basis Lastschrift Mandat eingezogen."
    create_excel_button_text = "Nur Excel-Rechnung"
    create_pdf_button_text = "Nur PDF-Rechnung"
    create_both_button_text = "Rechnung als Excel + PDF erstellen"

    def _default_note_for_order(self, order) -> str:
        payment_method = (order.customer.payment_method or "").lower().replace("ü", "ue")
        if "ueberweisung" in payment_method:
            try:
                due_date = (date.fromisoformat(order.delivery_date) + timedelta(days=7)).isoformat()
            except ValueError:
                return "Bitte überweisen Sie den Rechnungsbetrag."
            return f"Bitte überweisen Sie den Rechnungsbetrag bis zum {due_date}."
        if "sepa" in payment_method or "lastschrift" in payment_method:
            return self.default_note_text
        return ""

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


class ReturnInvoicePanel(InvoicePanel):
    page_title = "Rücklauf bearbeiten und Rechnung erstellen"
    create_both_button_text = "Rechnung aus Rücklauf als Excel + PDF erstellen"
    show_work_overview_button = True
