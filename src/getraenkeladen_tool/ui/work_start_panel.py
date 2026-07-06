from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGridLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..services.customer_service import list_active_customers
from ..services.report_service import DeliveryReturnWorkItem, list_open_delivery_returns
from .date_input import to_display_date
from .layouts import ContentSurface, PageHeader, WorkspaceCard


RETURN_COLUMNS = ("Kunde", "Lieferschein", "Datum", "Zeit")


class WorkStartPanel(QWidget):
    customer_search_requested = Signal()
    return_selected = Signal(int)

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.return_items: list[DeliveryReturnWorkItem] = []

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        layout.addWidget(
            PageHeader(
                "Arbeiten",
                "Telefonische Bestellung aufnehmen oder zurückgebrachte Lieferscheine abrechnen.",
            )
        )

        task_grid = QGridLayout()
        task_grid.setSpacing(16)
        task_grid.addWidget(self._customer_task(), 0, 0)
        task_grid.addWidget(self._returns_task(), 0, 1)
        task_grid.setColumnStretch(0, 1)
        task_grid.setColumnStretch(1, 1)
        layout.addLayout(task_grid)
        layout.addStretch()

        self.refresh()

    def _customer_task(self) -> QWidget:
        card = WorkspaceCard(
            "Bestellung aufnehmen",
            "Kunde suchen, Hinweise prüfen und direkt eine neue Bestellung starten.",
            tone="route",
            kicker="KUNDENSUCHE",
        )
        self.customer_empty_label = QLabel("Bitte erst Kunden importieren oder unter Verwaltung anlegen.")
        self.customer_empty_label.setObjectName("muted")
        self.customer_empty_label.setWordWrap(True)
        card.layout.addWidget(self.customer_empty_label)

        self.customer_search_button = QPushButton("Kunde suchen und Bestellung starten")
        self.customer_search_button.setObjectName("newOrderButton")
        self.customer_search_button.clicked.connect(self.customer_search_requested.emit)
        card.layout.addWidget(self.customer_search_button)
        return card

    def _returns_task(self) -> QWidget:
        card = WorkspaceCard(
            "Offene Lieferschein-Rückläufe",
            "Zurückgebrachte Lieferscheine auswählen, Mengen prüfen und Rechnung erstellen.",
            tone="document",
            kicker="RÜCKLAUF",
        )
        self.returns_table = QTableWidget(0, len(RETURN_COLUMNS))
        self.returns_table.setHorizontalHeaderLabels(RETURN_COLUMNS)
        self.returns_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.returns_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.returns_table.verticalHeader().setVisible(False)
        self.returns_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.returns_table.setColumnWidth(1, 150)
        self.returns_table.setColumnWidth(2, 110)
        self.returns_table.setColumnWidth(3, 90)
        self.returns_table.itemSelectionChanged.connect(self.update_return_button)
        self.returns_table.doubleClicked.connect(self.open_selected_return)
        card.layout.addWidget(self.returns_table)

        self.returns_empty_label = QLabel("Keine offenen Rückläufe.")
        self.returns_empty_label.setObjectName("muted")
        self.returns_empty_label.setWordWrap(True)
        card.layout.addWidget(self.returns_empty_label)

        self.open_return_button = QPushButton("Rücklauf bearbeiten")
        self.open_return_button.setEnabled(False)
        self.open_return_button.clicked.connect(self.open_selected_return)
        card.layout.addWidget(self.open_return_button)
        return card

    def refresh(self) -> None:
        if self.session_factory is None:
            self.customer_empty_label.setText("Keine Datenbankverbindung vorhanden.")
            self.customer_empty_label.setVisible(True)
            self.show_returns([])
            return
        session = self.session_factory()
        try:
            self.customer_empty_label.setVisible(len(list_active_customers(session)) == 0)
            self.show_returns(list_open_delivery_returns(session))
        finally:
            session.close()

    def show_returns(self, items: list[DeliveryReturnWorkItem]) -> None:
        self.return_items = items
        self.returns_table.setRowCount(0)
        for row, item in enumerate(items):
            self.returns_table.insertRow(row)
            for column, value in enumerate(
                (
                    item.customer_name,
                    item.delivery_note_number,
                    to_display_date(item.delivery_date),
                    item.delivery_slot or "",
                )
            ):
                cell = QTableWidgetItem(value)
                if column == 0:
                    cell.setData(Qt.ItemDataRole.UserRole, item.order_id)
                self.returns_table.setItem(row, column, cell)
        self.returns_empty_label.setVisible(not items)
        self.returns_table.setVisible(bool(items))
        self.update_return_button()

    def update_return_button(self) -> None:
        self.open_return_button.setEnabled(self._selected_return_order_id() is not None)

    def open_selected_return(self) -> None:
        order_id = self._selected_return_order_id()
        if order_id is not None:
            self.return_selected.emit(order_id)

    def _selected_return_order_id(self) -> int | None:
        selected = self.returns_table.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        item = self.returns_table.item(row, 0)
        if item is None:
            return None
        value = item.data(Qt.ItemDataRole.UserRole)
        return int(value) if value is not None else None
