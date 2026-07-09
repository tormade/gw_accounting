from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
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

from ..resources import development_default_dir
from ..services.master_data_import_service import import_master_data_from_folder
from ..services.master_data_import_service import CUSTOMER_FILE_NAME
from ..services.onboarding_service import onboard_customer_workbook_folder
from .checklist_panel import ChecklistPanel
from .background_task import BackgroundTask
from .layouts import ContentSurface, PageHeader, WorkspaceCard, configure_form_layout


SETTINGS_PANEL_ACTIONS = {
    "settingsHelpButton": "?",
    "chooseInputFolderButton": "Input-Ordner waehlen",
    "importMasterDataButton": "Stammdaten importieren",
    "chooseCustomerFolderButton": "Kundenordner waehlen",
    "importCustomerFolderButton": "Kundenordner importieren",
    "openChecklistButton": "Pruefpunkte ansehen",
}
SETTINGS_PANEL_SECTIONS = ("Stammdaten aus Excel importieren", "Kundenordner einlesen")
SETTINGS_HELP_TEXT = (
    "Einstellungen: Hier koennen Sie die erhaltenen Excel-Stammdaten und spaeter die Kundenordner einlesen.\n\n"
    "Die Originaldateien werden nicht veraendert. Unsichere Treffer landen in der Pruefliste."
)


class SettingsPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.checklist_dialogs: list[QDialog] = []
        self.background_task: BackgroundTask | None = None

        self.input_folder = QLineEdit(str(development_default_dir("Input")))
        self.input_folder.setPlaceholderText("Ordner mit Artikel Liste Preise.xlsx und Lieferkunden Liste.xlsx")
        self.customer_folder = QLineEdit(str(development_default_dir("Kunden")))
        self.customer_folder.setPlaceholderText("Ordner mit den Kundenunterordnern")
        self.status_label = QLabel("Input-Ordner waehlen und Stammdaten importieren.")
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
                "Stammdatenimport und grundlegende App-Einstellungen.",
                self.help_button,
            )
        )

        import_box = WorkspaceCard(
            SETTINGS_PANEL_SECTIONS[0],
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

        folder_box = WorkspaceCard(
            SETTINGS_PANEL_SECTIONS[1],
            "Liest alte Kunden-Excel aus den Kundenordnern. Pro Kunde wird nur die neueste Belegdatei als letzte Menge genutzt.",
        )
        folder_layout = folder_box.layout
        folder_form = QFormLayout()
        configure_form_layout(folder_form)
        folder_form.addRow("Kundenordner", self._customer_folder_row())
        folder_layout.addLayout(folder_form)
        self.import_customer_folder_button = self._button("importCustomerFolderButton")
        self.open_checklist_button = self._button("openChecklistButton")
        folder_actions = QHBoxLayout()
        folder_actions.addWidget(self.import_customer_folder_button)
        folder_actions.addWidget(self.open_checklist_button)
        folder_actions.addStretch()
        folder_layout.addLayout(folder_actions)
        layout.addWidget(folder_box)

        layout.addWidget(self.status_label)
        layout.addStretch()

        self.help_button.clicked.connect(self.show_help)
        self.import_master_data_button.clicked.connect(self.import_master_data)
        self.import_customer_folder_button.clicked.connect(self.import_customer_folder)
        self.open_checklist_button.clicked.connect(self.open_checklist_dialog)

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

    def _customer_folder_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.customer_folder)
        self.choose_customer_folder_button = self._button("chooseCustomerFolderButton")
        self.choose_customer_folder_button.clicked.connect(self.choose_customer_folder)
        layout.addWidget(self.choose_customer_folder_button)
        return row

    def show_help(self) -> None:
        QMessageBox.information(self, "Hilfe: Einstellungen", SETTINGS_HELP_TEXT)

    def choose_input_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Input-Ordner waehlen", self.input_folder.text())
        if folder:
            self.input_folder.setText(folder)

    def choose_customer_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Kundenordner waehlen", self.customer_folder.text())
        if folder:
            self.customer_folder.setText(folder)

    def import_master_data(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        input_dir = Path(self.input_folder.text()).expanduser()
        if not input_dir.exists():
            self.status_label.setText("Input-Ordner wurde nicht gefunden.")
            return
        self._start_background_task(
            lambda: self._run_master_data_import(input_dir),
            "Stammdaten werden importiert …",
            lambda result: self.status_label.setText(
                "Import abgeschlossen: "
                f"{result.customers_created} Kunden neu, {result.customers_updated} Kunden aktualisiert, "
                f"{result.products_created} Produkte neu, {result.products_updated} Produkte aktualisiert."
            ),
        )

    def import_customer_folder(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        input_dir = Path(self.input_folder.text()).expanduser()
        customer_list_path = input_dir / CUSTOMER_FILE_NAME
        customer_folder = Path(self.customer_folder.text()).expanduser()
        if not customer_list_path.exists():
            self.status_label.setText("Lieferkunden Liste.xlsx wurde im Input-Ordner nicht gefunden.")
            return
        if not customer_folder.exists():
            self.status_label.setText("Kundenordner wurde nicht gefunden.")
            return
        self._start_background_task(
            lambda: self._run_customer_folder_import(customer_list_path, customer_folder),
            "Kundenordner werden eingelesen …",
            lambda result: self.status_label.setText(
                "Kundenordner-Import abgeschlossen: "
                f"{result.report.customers_read} Kunden gelesen, "
                f"{result.report.assortment_lines} Sortiment-Zeilen, "
                f"{result.report.conflicts} Pruefpunkte, "
                f"{result.report.unreadable_files} nicht lesbare Dateien. "
                "Mit 'Pruefpunkte ansehen' koennen offene Entscheidungen bearbeitet werden."
            ),
        )

    def _run_master_data_import(self, input_dir: Path):
        session = self.session_factory()
        try:
            return import_master_data_from_folder(session, input_dir)
        finally:
            session.close()

    def _run_customer_folder_import(self, customer_list_path: Path, customer_folder: Path):
        session = self.session_factory()
        try:
            return onboard_customer_workbook_folder(session, customer_list_path, customer_folder)
        finally:
            session.close()

    def _start_background_task(self, operation, running_message: str, on_success) -> None:
        if self.background_task is not None:
            return
        self.status_label.setText(running_message)
        self.import_master_data_button.setEnabled(False)
        self.import_customer_folder_button.setEnabled(False)
        task = BackgroundTask(operation, self)
        self.background_task = task
        task.succeeded.connect(on_success)
        task.failed.connect(self._show_background_task_error)
        task.finished.connect(self._finish_background_task)
        task.start()

    def _show_background_task_error(self, error: Exception) -> None:
        message = f"Vorgang fehlgeschlagen: {error}"
        self.status_label.setText(message)
        QMessageBox.critical(self, "Vorgang fehlgeschlagen", message)

    def _finish_background_task(self) -> None:
        self.import_master_data_button.setEnabled(True)
        self.import_customer_folder_button.setEnabled(True)
        self.background_task = None

    def open_checklist_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Pruefpunkte ansehen")
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        dialog.resize(1120, 760)
        layout = QVBoxLayout(dialog)
        layout.addWidget(ChecklistPanel(session_factory=self.session_factory))
        dialog.finished.connect(lambda _result, active_dialog=dialog: self._forget_checklist_dialog(active_dialog))
        self.checklist_dialogs.append(dialog)
        dialog.show()

    def _forget_checklist_dialog(self, dialog: QDialog) -> None:
        if dialog in self.checklist_dialogs:
            self.checklist_dialogs.remove(dialog)
