from datetime import date

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ..services.report_service import DashboardSummary, get_dashboard_summary


DASHBOARD_ACTIONS = {
    "newDeliveryButton": "Neue Lieferung erfassen",
    "refreshDashboardButton": "Heute aktualisieren",
}
DASHBOARD_CARDS = ("Lieferungen heute", "Offene Posten", "Kontaktanfragen heute")
DASHBOARD_GUIDANCE_STEPS = (
    "Neue Lieferung erfassen starten.",
    "Kunde auswaehlen und bei Bedarf letzte Bestellung uebernehmen.",
    "PDF-Belege erzeugen oder offene Aufgaben ueber die Karten pruefen.",
)


class DashboardPanel(QWidget):
    new_delivery_requested = Signal()

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.target_date = date.today().isoformat()
        self.card_values: list[QLabel] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        headline = QLabel("Start")
        headline.setObjectName("headline")
        layout.addWidget(headline)

        muted = QLabel("Tagesueberblick: Was ist heute wichtig?")
        muted.setObjectName("muted")
        layout.addWidget(muted)

        layout.addWidget(self._guidance_box())

        self.new_delivery_button = QPushButton(DASHBOARD_ACTIONS["newDeliveryButton"])
        self.new_delivery_button.setObjectName("newDeliveryButton")
        layout.addWidget(self.new_delivery_button)

        layout.addLayout(self._cards_grid())

        action_row = QHBoxLayout()
        self.refresh_button = QPushButton(DASHBOARD_ACTIONS["refreshDashboardButton"])
        self.refresh_button.setObjectName("refreshDashboardButton")
        action_row.addWidget(self.refresh_button)
        action_row.addStretch()
        layout.addLayout(action_row)

        self.next_steps_label = QLabel("Noch keine Tagesdaten geladen.")
        self.next_steps_label.setObjectName("statusBox")
        self.next_steps_label.setWordWrap(True)
        layout.addWidget(self.next_steps_label)
        layout.addStretch()

        self.new_delivery_button.clicked.connect(self.new_delivery_requested.emit)
        self.refresh_button.clicked.connect(self.refresh_dashboard)
        self.refresh_dashboard()

    def _guidance_box(self) -> QWidget:
        box = QWidget()
        box.setObjectName("guidanceBox")
        layout = QVBoxLayout(box)
        layout.setSpacing(8)

        title = QLabel("So starten Sie den Arbeitstag")
        title.setObjectName("stepTitle")
        layout.addWidget(title)

        for index, step in enumerate(DASHBOARD_GUIDANCE_STEPS, start=1):
            label = QLabel(f"{index}. {step}")
            label.setObjectName("stepText")
            layout.addWidget(label)

        return box

    def _cards_grid(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(14)
        for column, title in enumerate(DASHBOARD_CARDS):
            card = QWidget()
            card.setObjectName("metricCard")
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(8)

            value = QLabel("0")
            value.setObjectName("metricValue")
            self.card_values.append(value)
            card_layout.addWidget(value)

            label = QLabel(title)
            label.setObjectName("metricLabel")
            label.setWordWrap(True)
            card_layout.addWidget(label)
            grid.addWidget(card, 0, column)
        return grid

    def refresh_dashboard(self) -> None:
        if self.session_factory is None:
            self._show_empty_summary("Keine Datenbankverbindung vorhanden.")
            return

        session = self.session_factory()
        try:
            summary = get_dashboard_summary(session, self.target_date)
        finally:
            session.close()
        self.show_summary(summary)

    def show_summary(self, summary: DashboardSummary) -> None:
        values = (summary.delivery_count, summary.open_item_count, summary.due_contact_count)
        for label, value in zip(self.card_values, values, strict=True):
            label.setText(str(value))
        self.next_steps_label.setText("Naechste Schritte: " + " ".join(summary.next_steps))

    def _show_empty_summary(self, message: str) -> None:
        for label in self.card_values:
            label.setText("0")
        self.next_steps_label.setText(message)
