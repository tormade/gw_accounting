from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QListWidget, QVBoxLayout, QWidget

from ..services.settings_service import add_product_unit, list_product_units


SETTINGS_PANEL_ACTIONS = {
    "settingsHelpButton": "?",
    "refreshUnitsButton": "Einheiten laden",
    "addUnitButton": "Einheit hinzufuegen",
}
SETTINGS_PANEL_SECTIONS = ("Produkteinheiten bearbeiten",)
SETTINGS_HELP_TEXT = (
    "Einstellungen: Hier pflegen Sie Listenwerte, die an anderer Stelle als Auswahlfeld erscheinen.\n\n"
    "Aktuell bearbeiten Sie die Produkteinheiten, zum Beispiel Kiste, Flasche, Fass oder Tray."
)


class SettingsPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory

        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("z. B. Tray")
        self.units_list = QListWidget()
        self.status_label = QLabel(
            "Diese Einheiten erscheinen im Feld Einheit bei Produkten, zum Beispiel Kiste oder Flasche."
        )
        self.status_label.setObjectName("muted")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        header_row = QHBoxLayout()
        title_column = QVBoxLayout()
        headline = QLabel("Einstellungen")
        headline.setObjectName("headline")
        title_column.addWidget(headline)
        muted = QLabel("Listenwerte, die an anderer Stelle als Auswahlfeld verwendet werden")
        muted.setObjectName("muted")
        title_column.addWidget(muted)
        header_row.addLayout(title_column)
        header_row.addStretch()
        self.help_button = QPushButton(SETTINGS_PANEL_ACTIONS["settingsHelpButton"])
        self.help_button.setObjectName("helpButton")
        header_row.addWidget(self.help_button)
        layout.addLayout(header_row)

        box = QWidget()
        box.setObjectName("sectionBox")
        box_layout = QVBoxLayout(box)
        title = QLabel(SETTINGS_PANEL_SECTIONS[0])
        title.setObjectName("sectionTitle")
        box_layout.addWidget(title)
        hint = QLabel("Hier bearbeiten Sie die Auswahlwerte fuer das Feld Einheit im Produkte-Reiter.")
        hint.setObjectName("sectionSubtitle")
        hint.setWordWrap(True)
        box_layout.addWidget(hint)
        form = QFormLayout()
        form.addRow("Neue Einheit", self.unit_input)
        box_layout.addLayout(form)

        action_row = QHBoxLayout()
        self.refresh_units_button = self._button("refreshUnitsButton")
        self.add_unit_button = self._button("addUnitButton")
        action_row.addWidget(self.refresh_units_button)
        action_row.addWidget(self.add_unit_button)
        action_row.addStretch()
        box_layout.addLayout(action_row)
        box_layout.addWidget(self.units_list)
        layout.addWidget(box)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.help_button.clicked.connect(self.show_help)
        self.refresh_units_button.clicked.connect(self.refresh_units)
        self.add_unit_button.clicked.connect(self.add_unit)
        self.refresh_units()

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(SETTINGS_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def show_help(self) -> None:
        QMessageBox.information(self, "Hilfe: Einstellungen", SETTINGS_HELP_TEXT)

    def refresh_units(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            units = list_product_units(session)
        finally:
            session.close()
        self.units_list.clear()
        self.units_list.addItems(units)
        self.status_label.setText(f"{len(units)} Einheiten geladen.")

    def add_unit(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            unit = add_product_unit(session, self.unit_input.text())
        finally:
            session.close()
        self.unit_input.clear()
        self.refresh_units()
        self.status_label.setText(f"Einheit gespeichert: {unit.value}")
