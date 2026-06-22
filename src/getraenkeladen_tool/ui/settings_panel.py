from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..services.master_data_import_service import import_master_data_from_folder
from ..services.numbering_service import list_number_sequence_statuses, set_next_number
from .layouts import ContentSurface, PageHeader, WorkspaceCard, configure_form_layout


SETTINGS_PANEL_ACTIONS = {
    "settingsHelpButton": "?",
    "refreshNumberSequencesButton": "Nummernkreise laden",
    "saveNumberSequencesButton": "Nummernkreise speichern",
    "chooseInputFolderButton": "Input-Ordner waehlen",
    "importMasterDataButton": "Stammdaten importieren",
}
SETTINGS_PANEL_SECTIONS = ("Nummernkreise bearbeiten", "Stammdaten aus Excel importieren")
SETTINGS_HELP_TEXT = (
    "Einstellungen: Hier legen Sie fest, welche Nummer als naechstes vorgeschlagen wird.\n\n"
    "Die App verhindert dabei, dass eine Nummer unter bereits vorhandene Belege zurueckfaellt."
)


class SettingsPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory

        self.sequence_inputs: dict[str, QLineEdit] = {}
        self.sequence_prefixes: dict[str, str] = {}
        self.input_folder = QLineEdit(str(Path.cwd().parent / "Input"))
        self.input_folder.setPlaceholderText("Ordner mit Artikel Liste Preise.xlsx und Lieferkunden Liste.xlsx")
        self.status_label = QLabel("Nummernkreise laden oder anpassen.")
        self.status_label.setObjectName("muted")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        self.help_button = QPushButton(SETTINGS_PANEL_ACTIONS["settingsHelpButton"])
        self.help_button.setObjectName("helpButton")
        layout.addWidget(
            PageHeader(
                "Einstellungen",
                "Nummernkreise und Stammdatenimport.",
                self.help_button,
            )
        )

        box = WorkspaceCard(
            SETTINGS_PANEL_SECTIONS[0],
            "Hier sehen Sie die naechsten Vorschlaege fuer Auftrag, Lieferschein und Rechnung.",
        )
        box_layout = box.layout
        sequence_grid = QGridLayout()
        sequence_grid.setHorizontalSpacing(12)
        sequence_grid.setVerticalSpacing(8)
        sequence_grid.addWidget(QLabel("Bereich"), 0, 0)
        sequence_grid.addWidget(QLabel("Naechste Nummer"), 0, 1)
        for row, sequence_key in enumerate(("order", "delivery_note", "invoice"), start=1):
            label = QLabel("")
            label.setObjectName(f"{sequence_key}SequenceLabel")
            number_input = QLineEdit()
            number_input.setObjectName(f"{sequence_key}SequenceInput")
            number_input.setPlaceholderText("z. B. RG-3001")
            self.sequence_inputs[sequence_key] = number_input
            sequence_grid.addWidget(label, row, 0)
            sequence_grid.addWidget(number_input, row, 1)
        self.sequence_labels = {
            "order": sequence_grid.itemAtPosition(1, 0).widget(),
            "delivery_note": sequence_grid.itemAtPosition(2, 0).widget(),
            "invoice": sequence_grid.itemAtPosition(3, 0).widget(),
        }
        box_layout.addLayout(sequence_grid)

        action_row = QHBoxLayout()
        self.refresh_number_sequences_button = self._button("refreshNumberSequencesButton")
        self.save_number_sequences_button = self._button("saveNumberSequencesButton")
        action_row.addWidget(self.refresh_number_sequences_button)
        action_row.addWidget(self.save_number_sequences_button)
        action_row.addStretch()
        box_layout.addLayout(action_row)
        layout.addWidget(box)

        import_box = WorkspaceCard(
            SETTINGS_PANEL_SECTIONS[1],
            "Die Excel-Dateien werden nur gelesen. Aenderungen landen in der Datenbank und werden protokolliert.",
        )
        import_layout = import_box.layout
        import_form = QFormLayout()
        configure_form_layout(import_form)
        import_form.addRow("Input-Ordner", self._input_folder_row())
        import_layout.addLayout(import_form)
        self.import_master_data_button = self._button("importMasterDataButton")
        import_actions = QHBoxLayout()
        import_actions.addWidget(self.import_master_data_button)
        import_actions.addStretch()
        import_layout.addLayout(import_actions)
        layout.addWidget(import_box)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.help_button.clicked.connect(self.show_help)
        self.refresh_number_sequences_button.clicked.connect(self.refresh_number_sequences)
        self.save_number_sequences_button.clicked.connect(self.save_number_sequences)
        self.import_master_data_button.clicked.connect(self.import_master_data)
        self.refresh_number_sequences()

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(SETTINGS_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return button

    def _input_folder_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.input_folder)
        self.choose_input_folder_button = self._button("chooseInputFolderButton")
        self.choose_input_folder_button.clicked.connect(self.choose_input_folder)
        layout.addWidget(self.choose_input_folder_button)
        return row

    def show_help(self) -> None:
        QMessageBox.information(self, "Hilfe: Einstellungen", SETTINGS_HELP_TEXT)

    def refresh_number_sequences(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            statuses = list_number_sequence_statuses(session)
        finally:
            session.close()
        for status in statuses:
            label = self.sequence_labels[status.sequence_key]
            label.setText(status.label)
            self.sequence_inputs[status.sequence_key].setText(status.next_number)
            self.sequence_prefixes[status.sequence_key] = status.prefix
        self.status_label.setText("Nummernkreise geladen.")

    def save_number_sequences(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            for sequence_key, input_field in self.sequence_inputs.items():
                set_next_number(
                    session,
                    sequence_key=sequence_key,
                    prefix=self.sequence_prefixes[sequence_key],
                    value=input_field.text(),
                )
            statuses = list_number_sequence_statuses(session)
        except ValueError as error:
            self.status_label.setText(str(error))
            return
        finally:
            session.close()
        for status in statuses:
            self.sequence_inputs[status.sequence_key].setText(status.next_number)
        self.status_label.setText("Nummernkreise erfolgreich gespeichert.")

    def choose_input_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Input-Ordner waehlen", self.input_folder.text())
        if folder:
            self.input_folder.setText(folder)

    def import_master_data(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        input_dir = Path(self.input_folder.text()).expanduser()
        if not input_dir.exists():
            self.status_label.setText("Input-Ordner wurde nicht gefunden.")
            return
        session = self.session_factory()
        try:
            result = import_master_data_from_folder(session, input_dir)
        finally:
            session.close()
        self.status_label.setText(
            "Import abgeschlossen: "
            f"{result.customers_created} Kunden neu, {result.customers_updated} Kunden aktualisiert, "
            f"{result.products_created} Produkte neu, {result.products_updated} Produkte aktualisiert."
        )
