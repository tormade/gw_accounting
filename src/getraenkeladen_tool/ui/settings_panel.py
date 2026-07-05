from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..services.master_data_import_service import import_master_data_from_folder, preview_master_data_from_folder
from .layouts import ContentSurface, PageHeader, WorkspaceCard, configure_form_layout


SETTINGS_PANEL_ACTIONS = {
    "settingsHelpButton": "?",
    "chooseInputFolderButton": "Ordner waehlen",
    "previewMasterDataButton": "Import pruefen",
    "importMasterDataButton": "Import starten",
}
SETTINGS_PANEL_SECTIONS = ("Excel-Stammdaten importieren",)
SETTINGS_HELP_TEXT = (
    "Import: Hier koennen Sie die erhaltenen Excel-Stammdaten einlesen.\n\n"
    "Die Originaldateien werden nicht veraendert. Aenderungen in der App werden intern protokolliert."
)


class SettingsPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory

        self.input_folder = QLineEdit(str(Path.cwd().parent / "Input"))
        self.input_folder.setPlaceholderText("Ordner mit Artikel Liste Preise.xlsx und Lieferkunden Liste.xlsx")
        self.status_label = QLabel("Input-Ordner waehlen und Import pruefen.")
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
                "Excel-Dateien einlesen und Pruefpunkte erzeugen.",
                self.help_button,
            )
        )

        import_box = WorkspaceCard(
            SETTINGS_PANEL_SECTIONS[0],
            "Die Excel-Dateien werden nur gelesen. Aenderungen landen in der Datenbank und werden protokolliert.",
            tone="audit",
            kicker="IMPORT",
        )
        import_layout = import_box.layout
        import_form = QFormLayout()
        configure_form_layout(import_form)
        import_form.addRow("Input-Ordner", self._input_folder_row())
        import_layout.addLayout(import_form)
        self.preview_master_data_button = self._button("previewMasterDataButton")
        self.import_master_data_button = self._button("importMasterDataButton")
        import_actions = QHBoxLayout()
        import_actions.addWidget(self.preview_master_data_button)
        import_actions.addWidget(self.import_master_data_button)
        import_actions.addStretch()
        import_layout.addLayout(import_actions)
        layout.addWidget(import_box)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.help_button.clicked.connect(self.show_help)
        self.preview_master_data_button.clicked.connect(self.preview_master_data)
        self.import_master_data_button.clicked.connect(self.import_master_data)

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
            preview = preview_master_data_from_folder(session, input_dir)
            answer = QMessageBox.question(
                self,
                "Import bestaetigen",
                "Diese Aenderungen wurden gefunden:\n\n"
                f"{preview.safety_report_text}\n\n"
                "Import jetzt ausfuehren?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self.status_label.setText(f"Import nicht ausgefuehrt. Vorschau: {preview.summary_text}")
                return
            result = import_master_data_from_folder(session, input_dir)
        finally:
            session.close()
        self.status_label.setText(
            "Import abgeschlossen: "
            f"{result.customers_created} Kunden neu, {result.customers_updated} Kunden aktualisiert, "
            f"{result.products_created} Produkte neu, {result.products_updated} Produkte aktualisiert."
        )

    def preview_master_data(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        input_dir = Path(self.input_folder.text()).expanduser()
        if not input_dir.exists():
            self.status_label.setText("Input-Ordner wurde nicht gefunden.")
            return
        session = self.session_factory()
        try:
            preview = preview_master_data_from_folder(session, input_dir)
        finally:
            session.close()
        examples = "\n".join(f"- {item.name or 'Zeile ' + str(item.source_row)}: {item.action}" for item in preview.items[:8])
        details = f"\n\nBeispiele:\n{examples}" if examples else ""
        QMessageBox.information(self, "Import-Vorschau", preview.safety_report_text + details)
        self.status_label.setText(f"Import-Vorschau: {preview.summary_text}")
