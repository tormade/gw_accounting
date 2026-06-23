from datetime import date

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from ..services.report_service import DashboardSummary, get_dashboard_summary
from .layouts import ActionCard, ContentSurface, PageHeader


DASHBOARD_ACTIONS = {
    "dashboardHelpButton": "?",
    "newDeliveryButton": "Kundenordner oeffnen",
    "refreshDashboardButton": "Heute aktualisieren",
}
DASHBOARD_CARDS = ("Heute zu liefern", "Offene Posten", "Faellige Kontakte")
DASHBOARD_GUIDANCE_STEPS = (
    "Kunde suchen oder aus der Wiedervorlage oeffnen.",
    "Letzte Mengen pruefen und nur Abweichungen eintragen.",
    "Lieferschein oder Rechnung aus der Bestellung erzeugen.",
)
DASHBOARD_HELP_TEXT = (
    "Start: Hier sehen Sie die wichtigsten Tageszahlen.\n\n"
    "Kundenordner oeffnen: Startet den normalen Arbeitsablauf mit Kunde, alter Excel/PDF und neuer Bestellung.\n\n"
    "Alle wichtigen Wege fuehren jetzt auf unterschiedliche Arbeitsbereiche. "
    "Die Karten zeigen, ob heute Lieferungen, offene Posten oder Kontaktanfragen anstehen."
)


class DashboardPanel(QWidget):
    new_delivery_requested = Signal()
    open_items_requested = Signal()
    checklist_requested = Signal()

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.target_date = date.today().isoformat()
        self.card_values: list[QLabel] = []
        self.quick_actions: list[ActionCard] = []

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        self.help_button = QPushButton(DASHBOARD_ACTIONS["dashboardHelpButton"])
        self.help_button.setObjectName("helpButton")
        layout.addWidget(PageHeader("Heute", "Liefern, anrufen, kassieren: der Arbeitstag auf einen Blick.", self.help_button))

        self.new_delivery_card = ActionCard(
            "Kundenordner oeffnen",
            "Kunde oeffnen, alte Excel/PDF sehen und neue Bestellung eintragen.",
            DASHBOARD_ACTIONS["newDeliveryButton"],
        )
        self.open_items_card = ActionCard(
            "Offene Posten pruefen",
            "Zahlungen, SEPA und offene Rechnungen kontrollieren.",
            "Zu offenen Posten",
        )
        self.checklist_card = ActionCard(
            "Preis-/Importpruefung",
            "Unklare Artikel, Preise und Kundenhinweise abarbeiten.",
            "Zur Pruefliste",
        )
        self.quick_actions = [self.new_delivery_card, self.open_items_card, self.checklist_card]
        quick_action_grid = QGridLayout()
        quick_action_grid.setSpacing(14)
        for column, card in enumerate(self.quick_actions):
            quick_action_grid.addWidget(card, 0, column)
            quick_action_grid.setColumnStretch(column, 1)
        layout.addLayout(quick_action_grid)

        layout.addLayout(self._cards_grid())
        layout.addWidget(self._daily_flow_preview())

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

        self.new_delivery_card.button.clicked.connect(self.new_delivery_requested.emit)
        self.open_items_card.button.clicked.connect(self.open_items_requested.emit)
        self.checklist_card.button.clicked.connect(self.checklist_requested.emit)
        self.help_button.clicked.connect(self.show_help)
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
            card.setObjectName("dailyCockpitCard")
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

    def _daily_flow_preview(self) -> QWidget:
        box = QWidget()
        box.setObjectName("heroSearchPanel")
        layout = QGridLayout(box)
        layout.setSpacing(16)

        hero = QWidget()
        hero.setObjectName("customerSearchHero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setSpacing(14)
        hero_title = QLabel("Heute starten")
        hero_title.setObjectName("heroTitle")
        hero_title.setWordWrap(True)
        hero_layout.addWidget(hero_title)
        hero_text = QLabel(
            "Im Kundenordner suchen Sie den Kunden, sehen alte Excel/PDF-Dateien "
            "und starten aus den letzten Mengen eine neue Bestellung."
        )
        hero_text.setObjectName("sectionSubtitle")
        hero_text.setWordWrap(True)
        hero_layout.addWidget(hero_text)
        hero_button = QPushButton("Kundenordner oeffnen")
        hero_button.setObjectName("newDeliveryButton")
        hero_layout.addWidget(hero_button)
        hero_layout.addStretch()
        hero_button.clicked.connect(self.new_delivery_requested.emit)

        contacts = QWidget()
        contacts.setObjectName("todayContactList")
        contacts_layout = QVBoxLayout(contacts)
        contacts_layout.setSpacing(10)
        contacts_title = QLabel("Beispiel: Heute anrufen")
        contacts_title.setObjectName("sectionTitle")
        contacts_layout.addWidget(contacts_title)
        for customer, note in (
            ("Metzgerei Karl", "bis 13 Uhr und ab 15 Uhr, SEPA"),
            ("ADC Distribution GmbH", "Rechnung per E-Mail pruefen"),
            ("1. Poolbillardclub e.V.", "Pfand-Rueckgabe nachfragen"),
        ):
            row = QLabel(f"{customer}\n{note}")
            row.setObjectName("contactPreviewRow")
            row.setWordWrap(True)
            contacts_layout.addWidget(row)
        contacts_layout.addStretch()

        layout.addWidget(hero, 0, 0)
        layout.addWidget(contacts, 0, 1)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)
        return box

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
