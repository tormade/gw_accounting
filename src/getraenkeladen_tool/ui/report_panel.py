from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


REPORT_PANEL_ACTIONS = {
    "refreshOpenItemsButton": "Offene Posten aktualisieren",
    "markPaidButton": "Zahlung markieren",
}

OPEN_ITEMS_COLUMNS = ("Kunde", "Rechnungsnr.", "Betrag", "Zahlungsart", "Status")


class ReportPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        headline = QLabel("Listen")
        headline.setObjectName("headline")
        layout.addWidget(headline)

        muted = QLabel("Offene Posten, Tageslieferungen und Kontaktliste")
        muted.setObjectName("muted")
        layout.addWidget(muted)

        self.open_items_table = QTableWidget(0, len(OPEN_ITEMS_COLUMNS))
        self.open_items_table.setHorizontalHeaderLabels(OPEN_ITEMS_COLUMNS)
        layout.addWidget(self.open_items_table)

        action_row = QHBoxLayout()
        self.refresh_button = self._button("refreshOpenItemsButton")
        self.mark_paid_button = self._button("markPaidButton")
        action_row.addWidget(self.refresh_button)
        action_row.addWidget(self.mark_paid_button)
        action_row.addStretch()
        layout.addLayout(action_row)

        self.status_label = QLabel("Noch keine offenen Posten geladen.")
        self.status_label.setObjectName("muted")
        layout.addWidget(self.status_label)

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(REPORT_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def show_open_items(self, open_items: list) -> None:
        self.open_items_table.setRowCount(len(open_items))
        for row, item in enumerate(open_items):
            amount = f"{item.amount_cents / 100:.2f} EUR"
            values = (
                item.customer_name,
                item.document_number,
                amount,
                item.payment_method,
                item.status,
            )
            for column, value in enumerate(values):
                self.open_items_table.setItem(row, column, QTableWidgetItem(value))
        self.status_label.setText(f"{len(open_items)} offene Posten geladen.")
