from dataclasses import dataclass
from functools import partial
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

from ..services.master_data_import_service import (
    MasterDataImportPreview,
    import_master_data_from_folder,
    preview_master_data_from_folder,
)
from .background_task import BackgroundTask
from .layouts import ContentSurface, PageHeader, WorkspaceCard, configure_form_layout, set_button_role


SETTINGS_PANEL_ACTIONS = {
    "chooseInputFolderButton": "Ordner wählen",
    "previewMasterDataButton": "Import prüfen",
    "importMasterDataButton": "Import starten",
}
SETTINGS_BUTTON_ROLES = {
    "chooseInputFolderButton": "quiet",
    "previewMasterDataButton": "secondary",
    "importMasterDataButton": "primary",
}
SETTINGS_PANEL_SECTIONS = ("Excel-Stammdaten importieren",)


@dataclass(frozen=True, slots=True)
class MasterDataImportSummary:
    products_created: int
    products_updated: int
    customers_created: int
    customers_updated: int


def _preview_master_data_in_background(session_factory, input_dir: Path) -> MasterDataImportPreview:
    if not input_dir.is_dir():
        raise FileNotFoundError("Input-Ordner wurde nicht gefunden.")
    session = session_factory()
    try:
        return preview_master_data_from_folder(session, input_dir)
    finally:
        session.close()


def _import_master_data_in_background(session_factory, input_dir: Path) -> MasterDataImportSummary:
    if not input_dir.is_dir():
        raise FileNotFoundError("Input-Ordner wurde nicht gefunden.")
    session = session_factory()
    try:
        result = import_master_data_from_folder(session, input_dir)
        return MasterDataImportSummary(
            products_created=result.products_created,
            products_updated=result.products_updated,
            customers_created=result.customers_created,
            customers_updated=result.customers_updated,
        )
    finally:
        session.close()


class SettingsPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self._preview_task = BackgroundTask(self)
        self._master_data_task = BackgroundTask(self)

        self.input_folder = QLineEdit(str(Path.cwd().parent / "Input"))
        self.input_folder.setPlaceholderText("Ordner mit Artikel Liste Preise.xlsx und Lieferkunden Liste.xlsx")
        self.status_label = QLabel("Input-Ordner wählen und Import prüfen.")
        self.status_label.setObjectName("muted")
        self.preview_label = QLabel("Nach „Import prüfen“ erscheint hier eine kurze Vorschau der Änderungen.")
        self.preview_label.setObjectName("sectionSubtitle")
        self.preview_label.setWordWrap(True)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        layout.addWidget(
            PageHeader(
                "Excel-Import",
                "Stammdaten prüfen und erst danach bewusst übernehmen.",
            )
        )

        import_box = WorkspaceCard(
            SETTINGS_PANEL_SECTIONS[0],
            "Die Excel-Dateien werden nur gelesen. Änderungen landen in der Datenbank und werden protokolliert.",
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
        layout.addWidget(self.preview_label)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.preview_master_data_button.clicked.connect(self.preview_master_data)
        self.import_master_data_button.clicked.connect(self.import_master_data)

    def _button(self, object_name: str) -> QPushButton:
        button = QPushButton(SETTINGS_PANEL_ACTIONS[object_name])
        button.setObjectName(object_name)
        return set_button_role(button, SETTINGS_BUTTON_ROLES[object_name])

    def _input_folder_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.input_folder)
        self.choose_input_folder_button = self._button("chooseInputFolderButton")
        self.choose_input_folder_button.clicked.connect(self.choose_input_folder)
        layout.addWidget(self.choose_input_folder_button)
        return row

    def choose_input_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Input-Ordner wählen", self.input_folder.text())
        if folder:
            self.input_folder.setText(folder)

    def import_master_data(self) -> None:
        input_dir = self._input_directory()
        if input_dir is not None:
            self._start_preview(input_dir, confirm_import=True)

    def preview_master_data(self) -> None:
        input_dir = self._input_directory()
        if input_dir is not None:
            self._start_preview(input_dir, confirm_import=False)

    def _input_directory(self) -> Path | None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return None
        input_text = self.input_folder.text().strip()
        if not input_text:
            self.status_label.setText("Bitte einen Input-Ordner auswählen.")
            return None
        return Path(input_text).expanduser()

    def _start_preview(self, input_dir: Path, *, confirm_import: bool) -> None:
        self._set_import_running(True)
        if not self._preview_task.start(
            partial(_preview_master_data_in_background, self.session_factory, input_dir),
            on_success=lambda preview: self._show_preview(preview, input_dir, confirm_import=confirm_import),
            on_error=self._show_import_error,
            on_finished=self._refresh_import_running_state,
        ):
            self.status_label.setText("Ein Excel-Vorgang läuft bereits.")
            self._refresh_import_running_state()

    def _show_preview(self, preview: object, input_dir: Path, *, confirm_import: bool) -> None:
        if not isinstance(preview, MasterDataImportPreview):
            self._show_import_error("Import-Vorschau konnte nicht gelesen werden.")
            return
        examples = "\n".join(f"- {item.name or 'Zeile ' + str(item.source_row)}: {item.action}" for item in preview.items[:8])
        details = f"\n\nBeispiele:\n{examples}" if examples else ""
        self.preview_label.setText(preview.safety_report_text + details)
        self.status_label.setText(f"Import-Vorschau: {preview.summary_text}")
        if not confirm_import:
            return
        if not preview.can_import:
            self.status_label.setText("Import nicht ausgeführt: Benötigte Excel-Dateien fehlen.")
            return
        answer = QMessageBox.question(
            self,
            "Import bestätigen",
            "Diese Änderungen wurden gefunden:\n\n"
            f"{preview.safety_report_text}\n\n"
            "Import jetzt ausführen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.status_label.setText(f"Import nicht ausgeführt. Vorschau: {preview.summary_text}")
            return
        self._start_import(input_dir)

    def _start_import(self, input_dir: Path) -> None:
        self._set_import_running(True)
        if not self._master_data_task.start(
            partial(_import_master_data_in_background, self.session_factory, input_dir),
            on_success=self._show_import_result,
            on_error=self._show_import_error,
            on_finished=self._refresh_import_running_state,
        ):
            self.status_label.setText("Ein Excel-Vorgang läuft bereits.")
            self._refresh_import_running_state()

    def _show_import_result(self, result: object) -> None:
        if not isinstance(result, MasterDataImportSummary):
            self._show_import_error("Import-Ergebnis konnte nicht gelesen werden.")
            return
        self.status_label.setText(
            "Import abgeschlossen: "
            f"{result.customers_created} Kunden neu, {result.customers_updated} Kunden aktualisiert, "
            f"{result.products_created} Produkte neu, {result.products_updated} Produkte aktualisiert."
        )

    def _show_import_error(self, error: Exception | str) -> None:
        self.status_label.setText(f"Excel-Vorgang fehlgeschlagen: {str(error).strip() or type(error).__name__}")

    def _refresh_import_running_state(self) -> None:
        self._set_import_running(self._preview_task.is_running or self._master_data_task.is_running)

    def _set_import_running(self, is_running: bool) -> None:
        self.input_folder.setReadOnly(is_running)
        self.choose_input_folder_button.setEnabled(not is_running)
        self.preview_master_data_button.setEnabled(not is_running)
        self.import_master_data_button.setEnabled(not is_running)
        if is_running:
            self.status_label.setText("Excel-Dateien werden verarbeitet...")
