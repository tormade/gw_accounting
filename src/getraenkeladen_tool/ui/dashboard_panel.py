from datetime import date

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from ..services.report_service import DashboardSummary, get_dashboard_summary
from .layouts import ContentSurface, PageHeader


DASHBOARD_ACTIONS = {
    "dashboardHelpButton": "?",
    "newDeliveryButton": "Kunden oeffnen",
    "refreshDashboardButton": "Heute aktualisieren",
}
DASHBOARD_CARDS = ("Lieferungen", "Rechnungen", "Kontakte")
DASHBOARD_GUIDANCE_STEPS = (
    "Faellige Aufgabe auswaehlen.",
    "Kunde oder Rechnung im Kontext pruefen.",
    "Naechste Aktion direkt ausfuehren.",
)
DASHBOARD_HELP_TEXT = (
    "Heute: Hier stehen die Aufgaben, die jetzt Aufmerksamkeit brauchen.\n\n"
    "Kunden oeffnen: Kunde suchen, Kontext pruefen und Bestellung starten.\n\n"
    "Rechnungen oeffnen: Faellige Rechnungen pruefen und Zahlung markieren."
)


class DashboardPanel(QWidget):
    new_delivery_requested = Signal()
    orders_requested = Signal()
    open_items_requested = Signal()
    checklist_requested = Signal()

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.target_date = date.today().isoformat()
        self.card_values: list[QLabel] = []
        self.quick_action_buttons: list[QPushButton] = []

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        self.help_button = QPushButton(DASHBOARD_ACTIONS["dashboardHelpButton"])
        self.help_button.setObjectName("helpButton")
        layout.addWidget(PageHeader("Heute", "Was heute wichtig ist: Lieferungen, Rechnungen und offene Klärungen.", self.help_button))

        top_grid = QGridLayout()
        top_grid.setSpacing(16)
        top_grid.addWidget(self._task_queue(), 0, 0)
        top_grid.addLayout(self._cards_grid(), 0, 1)
        top_grid.setColumnStretch(0, 3)
        top_grid.setColumnStretch(1, 2)
        layout.addLayout(top_grid)

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

        self.help_button.clicked.connect(self.show_help)
        self.refresh_button.clicked.connect(self.refresh_dashboard)
        self.refresh_dashboard()

    def _task_queue(self) -> QWidget:
        board = QWidget()
        board.setObjectName("todayTaskQueue")
        layout = QVBoxLayout(board)
        layout.setSpacing(10)

        title = QLabel("Tagesliste")
        title.setObjectName("workflowBoardTitle")
        layout.addWidget(title)

        for tone, title_text, body_text, button_text, signal in (
            (
                "route",
                "Kunde oder Lieferung starten",
                "Kunden suchen, Hinweise sehen, Bestellung beginnen.",
                "Kunden oeffnen",
                self.new_delivery_requested,
            ),
            (
                "document",
                "Bestellung weiterbearbeiten",
                "Entwurf oeffnen, Mengen pruefen, Beleg vorbereiten.",
                "Bestellungen oeffnen",
                self.orders_requested,
            ),
            (
                "cash",
                "Rechnung oder Zahlung pruefen",
                "Faelligkeit, Zahlart und Zahlungseingang kontrollieren.",
                "Rechnungen oeffnen",
                self.open_items_requested,
            ),
            (
                "audit",
                "Blocker klaeren",
                "Unklare Artikel, Preise oder Kundendaten entscheiden.",
                "Pruefpunkte oeffnen",
                self.checklist_requested,
            ),
        ):
            row = QWidget()
            row.setObjectName("todayTaskRow")
            row.setProperty("tone", tone)
            row_layout = QGridLayout(row)
            row_layout.setContentsMargins(14, 12, 10, 12)
            row_layout.setHorizontalSpacing(14)
            row_layout.setVerticalSpacing(6)

            title_label = QLabel(title_text)
            title_label.setObjectName("workflowStepTitle")
            row_layout.addWidget(title_label, 0, 0)

            body_label = QLabel(body_text)
            body_label.setObjectName("workflowStepText")
            body_label.setWordWrap(True)
            row_layout.addWidget(body_label, 1, 0)

            button = QPushButton(button_text)
            button.setObjectName("workflowStepButton")
            button.clicked.connect(signal.emit)
            self.quick_action_buttons.append(button)
            row_layout.addWidget(button, 0, 1, 2, 1)
            row_layout.setColumnStretch(0, 1)
            layout.addWidget(row)

        return board

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
            card.setObjectName("dailyCockpitCard")
            card.setProperty("tone", ("route", "cash", "audit")[column])
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

    def show_help(self) -> None:
        QMessageBox.information(self, "Hilfe: Start", DASHBOARD_HELP_TEXT)
