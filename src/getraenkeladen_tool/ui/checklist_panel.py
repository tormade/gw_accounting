from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ..services.checklist_service import list_checklist_issues, mark_issue_resolved, reopen_issue
from .layouts import ContentSurface, PageHeader, WorkspaceCard


CHECKLIST_COLUMNS = ("Status", "Kunde", "Art", "Feld", "Excel/Kundenordner", "Zentrale Liste", "Hinweis")
CHECKLIST_ACTIONS = {
    "refreshChecklistButton": "Pruefliste aktualisieren",
    "resolveChecklistButton": "Als erledigt markieren",
    "reopenChecklistButton": "Wieder oeffnen",
}


class ChecklistPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.issue_ids_by_row = {}

        self.summary_label = QLabel("Offene Pruefpunkte werden automatisch aus Import und Kundenordnern gesammelt.")
        self.summary_label.setObjectName("muted")
        self.issue_table = QTableWidget(0, len(CHECKLIST_COLUMNS))
        self.issue_table.setHorizontalHeaderLabels(CHECKLIST_COLUMNS)
        self.issue_table.setMinimumHeight(420)
        self.issue_table.setAlternatingRowColors(True)
        self.issue_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.issue_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.issue_table.horizontalHeader().setStretchLastSection(True)

        self.refresh_button = QPushButton(CHECKLIST_ACTIONS["refreshChecklistButton"])
        self.resolve_button = QPushButton(CHECKLIST_ACTIONS["resolveChecklistButton"])
        self.reopen_button = QPushButton(CHECKLIST_ACTIONS["reopenChecklistButton"])
        self.status_label = QLabel("Pruefliste bereit.")
        self.status_label.setObjectName("muted")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout
        layout.addWidget(PageHeader("Pruefliste", "Offene Konflikte bewusst entscheiden, statt sie im Alltag zu uebersehen."))

        card = WorkspaceCard("Offene Punkte", "Preisabweichungen, Artikelzuordnungen und Kundendaten-Konflikte.")
        toolbar = QHBoxLayout()
        toolbar.addWidget(self.refresh_button)
        toolbar.addWidget(self.resolve_button)
        toolbar.addWidget(self.reopen_button)
        toolbar.addStretch()
        card.layout.addWidget(self.summary_label)
        card.layout.addLayout(toolbar)
        card.layout.addWidget(self.issue_table)
        layout.addWidget(card, 1)
        layout.addWidget(self.status_label)

        self.refresh_button.clicked.connect(self.refresh_issues)
        self.resolve_button.clicked.connect(self.resolve_selected_issue)
        self.reopen_button.clicked.connect(self.reopen_selected_issue)
        self.refresh_issues()

    def refresh_issues(self) -> None:
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            rows = list_checklist_issues(session, include_done=True)
        finally:
            session.close()
        self.show_issues(rows)

    def show_issues(self, rows: list) -> None:
        self.issue_ids_by_row = {}
        self.issue_table.setRowCount(len(rows))
        open_count = sum(1 for row in rows if row.status != "erledigt")
        for row_index, row in enumerate(rows):
            self.issue_ids_by_row[row_index] = row.id
            values = (
                row.status,
                row.customer_name,
                row.issue_type_label,
                row.field_name,
                row.folder_value,
                row.list_value,
                row.message,
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0 and row.status == "erledigt":
                    item.setForeground(Qt.GlobalColor.darkGreen)
                self.issue_table.setItem(row_index, column, item)
        self.summary_label.setText(f"{open_count} offene Pruefpunkte, {len(rows)} insgesamt.")
        self.status_label.setText("Pruefliste aktualisiert.")

    def resolve_selected_issue(self) -> None:
        self._update_selected_issue("erledigt")

    def reopen_selected_issue(self) -> None:
        self._update_selected_issue("offen")

    def _update_selected_issue(self, status: str) -> None:
        issue_id = self._selected_issue_id()
        if issue_id is None:
            QMessageBox.warning(self, "Pruefpunkt auswaehlen", "Bitte zuerst einen Pruefpunkt in der Tabelle auswaehlen.")
            return
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            if status == "erledigt":
                mark_issue_resolved(session, issue_id)
                self.status_label.setText("Pruefpunkt als erledigt markiert.")
            else:
                reopen_issue(session, issue_id)
                self.status_label.setText("Pruefpunkt wieder geoeffnet.")
            rows = list_checklist_issues(session, include_done=True)
        finally:
            session.close()
        self.show_issues(rows)

    def _selected_issue_id(self) -> int | None:
        row = self.issue_table.currentRow()
        return self.issue_ids_by_row.get(row)
