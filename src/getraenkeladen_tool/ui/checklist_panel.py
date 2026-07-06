from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ..services.checklist_service import (
    confirm_product_alias,
    list_checklist_issues,
    mark_issue_resolved,
    reopen_issue,
    resolve_customer_conflict,
    resolve_price_mismatch,
)
from ..services.product_service import list_active_products
from .layouts import ContentSurface, InspectorPanel, PageHeader, ResponsiveSplitter, WorkspaceCard
from .searchable_select import SearchableSelect


CHECKLIST_COLUMNS = ("Priorität", "Kunde", "Problem", "Nächster Schritt")
CHECKLIST_ACTIONS = {
    "refreshChecklistButton": "Prüfpunkte aktualisieren",
    "resolveChecklistButton": "Als erledigt markieren",
    "reopenChecklistButton": "Wieder öffnen",
    "useCentralPriceButton": "Zentralen Preis nutzen",
    "keepExcelPriceButton": "Excel-Preis behalten",
    "confirmProductAliasButton": "Artikel zuordnen",
    "useListValueButton": "Zentrale Liste nutzen",
    "useFolderValueButton": "Kunden-Excel nutzen",
}


class ChecklistPanel(QWidget):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.issue_ids_by_row = {}
        self.issue_rows_by_id = {}
        self.has_loaded = False

        self.summary_label = QLabel("Prüfpunkte werden nach Blockerwirkung gesammelt und priorisiert.")
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
        self.use_central_price_button = QPushButton(CHECKLIST_ACTIONS["useCentralPriceButton"])
        self.keep_excel_price_button = QPushButton(CHECKLIST_ACTIONS["keepExcelPriceButton"])
        self.confirm_product_alias_button = QPushButton(CHECKLIST_ACTIONS["confirmProductAliasButton"])
        self.use_list_value_button = QPushButton(CHECKLIST_ACTIONS["useListValueButton"])
        self.use_folder_value_button = QPushButton(CHECKLIST_ACTIONS["useFolderValueButton"])
        self.product_select = SearchableSelect("Zentralen Artikel suchen")
        self.product_select.setMinimumWidth(360)
        self.action_help_label = QLabel(
            "Prüfpunkt auswählen. Nur die passenden Aktionen werden angezeigt. "
            "Diese Entscheidung ändert Stammdaten oder Kundensortiment dauerhaft."
        )
        self.action_help_label.setObjectName("sectionSubtitle")
        self.action_help_label.setWordWrap(True)
        self.status_label = QLabel("Prüfpunkte bereit.")
        self.status_label.setObjectName("muted")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout
        layout.addWidget(PageHeader("Prüfpunkte", "Blockierende Konflikte bewusst entscheiden, bevor sie Bestellungen stören."))

        workspace = ResponsiveSplitter()
        layout.addWidget(workspace, 1)

        card = WorkspaceCard(
            "Offene Punkte",
            "Blocker, Preisabweichungen, Artikelzuordnungen und Kundendaten-Konflikte.",
            tone="audit",
            kicker="ADMIN",
        )
        toolbar = QHBoxLayout()
        toolbar.addWidget(self.refresh_button)
        toolbar.addStretch()
        decision_toolbar = QHBoxLayout()
        decision_toolbar.addWidget(self.use_central_price_button)
        decision_toolbar.addWidget(self.keep_excel_price_button)
        decision_toolbar.addWidget(self.use_list_value_button)
        decision_toolbar.addWidget(self.use_folder_value_button)
        decision_toolbar.addStretch()
        alias_toolbar = QHBoxLayout()
        alias_toolbar.addWidget(self.product_select)
        alias_toolbar.addWidget(self.confirm_product_alias_button)
        alias_toolbar.addStretch()
        card.layout.addWidget(self.summary_label)
        card.layout.addWidget(self.action_help_label)
        card.layout.addLayout(toolbar)
        card.layout.addWidget(self.issue_table)
        workspace.addWidget(card)

        self.issue_detail_panel = InspectorPanel(
            "Prüfpunkt auswählen",
            "Details, Vergleichswerte und passende Aktionen erscheinen hier.",
        )
        self.issue_detail_panel.setMaximumWidth(420)
        self.issue_detail_panel.add_section_label("Details")
        self.issue_field_label = self.issue_detail_panel.add_value_label("Feld")
        self.issue_folder_label = self.issue_detail_panel.add_value_label("Kunden-Excel")
        self.issue_list_label = self.issue_detail_panel.add_value_label("Zentrale Daten")
        self.issue_message_label = self.issue_detail_panel.add_value_label("Nächster Schritt")
        self.issue_detail_panel.add_section_label("Aktionen")
        self.issue_detail_panel.body.addWidget(self.resolve_button)
        self.issue_detail_panel.body.addWidget(self.reopen_button)
        self.issue_detail_panel.body.addLayout(decision_toolbar)
        self.issue_detail_panel.body.addLayout(alias_toolbar)
        workspace.addWidget(self.issue_detail_panel)
        workspace.setStretchFactor(0, 3)
        workspace.setStretchFactor(1, 2)
        layout.addWidget(self.status_label)

        self.refresh_button.clicked.connect(self.refresh_issues)
        self.resolve_button.clicked.connect(self.resolve_selected_issue)
        self.reopen_button.clicked.connect(self.reopen_selected_issue)
        self.use_central_price_button.clicked.connect(self.use_central_price_for_selected_issue)
        self.keep_excel_price_button.clicked.connect(self.keep_excel_price_for_selected_issue)
        self.confirm_product_alias_button.clicked.connect(self.confirm_product_alias_for_selected_issue)
        self.use_list_value_button.clicked.connect(self.use_list_value_for_selected_issue)
        self.use_folder_value_button.clicked.connect(self.use_folder_value_for_selected_issue)
        self.issue_table.itemSelectionChanged.connect(self.update_issue_context)
        self.update_issue_context()

    def ensure_loaded(self) -> None:
        if self.has_loaded:
            return
        self.refresh_products()
        self.refresh_issues()
        self.has_loaded = True

    def refresh_products(self) -> None:
        if self.session_factory is None:
            return
        session = self.session_factory()
        try:
            products = list_active_products(session)
        finally:
            session.close()
        self.product_select.set_items(
            [
                (
                    product.name,
                    product.id,
                    " | ".join(
                        value
                        for value in (
                            product.article_number or "",
                            product.unit,
                            f"{product.standard_price_cents / 100:.2f} EUR",
                        )
                        if value
                    ),
                )
                for product in products
            ]
        )

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
        self.issue_rows_by_id = {row.id: row for row in rows}
        open_count = sum(1 for row in rows if row.status != "erledigt")
        self.issue_table.setUpdatesEnabled(False)
        try:
            self.issue_table.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                self.issue_ids_by_row[row_index] = row.id
                priority = self._priority_label(row)
                values = (
                    priority,
                    row.customer_name,
                    row.issue_type_label,
                    row.message,
                )
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if row.status == "erledigt":
                        item.setForeground(Qt.GlobalColor.darkGreen)
                    self.issue_table.setItem(row_index, column, item)
        finally:
            self.issue_table.setUpdatesEnabled(True)
        self.summary_label.setText(f"{open_count} offene Prüfpunkte, {len(rows)} insgesamt.")
        self.status_label.setText("Prüfpunkte aktualisiert.")
        self.update_issue_context()

    def update_issue_context(self) -> None:
        issue_id = self._selected_issue_id()
        row = self.issue_rows_by_id.get(issue_id)
        if row is None:
            self.issue_detail_panel.set_heading(
                "Prüfpunkt auswählen",
                "Nur die passenden Aktionen werden angezeigt.",
            )
            self.issue_field_label.setText("Feld: -")
            self.issue_folder_label.setText("Kunden-Excel: -")
            self.issue_list_label.setText("Zentrale Daten: -")
            self.issue_message_label.setText("Nächster Schritt: -")
            self._set_issue_action_visibility(None)
            return
        self.issue_detail_panel.set_heading(row.issue_type_label, f"{row.customer_name} | Status: {row.status}")
        self.issue_field_label.setText(f"Feld: {row.field_name or '-'}")
        self.issue_folder_label.setText(f"Kunden-Excel: {row.folder_value or '-'}")
        self.issue_list_label.setText(f"Zentrale Daten: {row.list_value or '-'}")
        self.issue_message_label.setText(f"Nächster Schritt: {row.message or '-'}")
        self._set_issue_action_visibility(getattr(row, "issue_type", ""))

    def _set_issue_action_visibility(self, issue_type: str | None) -> None:
        is_price = issue_type == "price_mismatch"
        is_alias = issue_type == "product_alias"
        is_customer = bool(issue_type and issue_type.startswith("customer_"))
        has_issue = issue_type is not None
        self.resolve_button.setVisible(has_issue)
        self.reopen_button.setVisible(has_issue)
        self.use_central_price_button.setVisible(is_price)
        self.keep_excel_price_button.setVisible(is_price)
        self.product_select.setVisible(is_alias)
        self.confirm_product_alias_button.setVisible(is_alias)
        self.use_list_value_button.setVisible(is_customer)
        self.use_folder_value_button.setVisible(is_customer)

    def resolve_selected_issue(self) -> None:
        self._update_selected_issue("erledigt")

    def reopen_selected_issue(self) -> None:
        self._update_selected_issue("offen")

    def use_central_price_for_selected_issue(self) -> None:
        self._resolve_price_decision("zentraler_preis", "Zentraler Preis wurde für diesen Artikel gespeichert.")

    def keep_excel_price_for_selected_issue(self) -> None:
        self._resolve_price_decision("excel_preis", "Excel-Preis wurde für diesen Artikel gespeichert.")

    def use_list_value_for_selected_issue(self) -> None:
        self._resolve_customer_conflict("list", "Wert aus zentraler Liste wurde übernommen.")

    def use_folder_value_for_selected_issue(self) -> None:
        self._resolve_customer_conflict("folder", "Wert aus Kunden-Excel wurde übernommen.")

    def confirm_product_alias_for_selected_issue(self) -> None:
        issue_id = self._selected_issue_id()
        product_id = self.product_select.current_value()
        if issue_id is None:
            QMessageBox.warning(self, "Prüfpunkt auswählen", "Bitte zuerst einen Artikel-Prüfpunkt auswählen.")
            return
        if product_id is None:
            QMessageBox.warning(self, "Artikel auswählen", "Bitte zuerst einen zentralen Artikel auswählen.")
            return
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            confirm_product_alias(session, issue_id, product_id)
            rows = list_checklist_issues(session, include_done=True)
        except Exception as error:
            QMessageBox.warning(self, "Artikel nicht zugeordnet", f"Der Artikel konnte nicht zugeordnet werden.\n\nGrund: {error}")
            return
        finally:
            session.close()
        self.show_issues(rows)
        self.status_label.setText("Artikel wurde zugeordnet und als Alias bestätigt.")

    def _resolve_price_decision(self, decision: str, status_message: str) -> None:
        issue_id = self._selected_issue_id()
        if issue_id is None:
            QMessageBox.warning(self, "Prüfpunkt auswählen", "Bitte zuerst einen Preis-Prüfpunkt auswählen.")
            return
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            resolve_price_mismatch(session, issue_id, decision)
            rows = list_checklist_issues(session, include_done=True)
        except Exception as error:
            QMessageBox.warning(self, "Preisentscheidung nicht gespeichert", f"Die Preisentscheidung konnte nicht gespeichert werden.\n\nGrund: {error}")
            return
        finally:
            session.close()
        self.show_issues(rows)
        self.status_label.setText(status_message)

    def _resolve_customer_conflict(self, source: str, status_message: str) -> None:
        issue_id = self._selected_issue_id()
        if issue_id is None:
            QMessageBox.warning(self, "Prüfpunkt auswählen", "Bitte zuerst einen Kundendaten-Prüfpunkt auswählen.")
            return
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            resolve_customer_conflict(session, issue_id, source)
            rows = list_checklist_issues(session, include_done=True)
        except Exception as error:
            QMessageBox.warning(self, "Kundendaten nicht übernommen", f"Die Kundendaten konnten nicht übernommen werden.\n\nGrund: {error}")
            return
        finally:
            session.close()
        self.show_issues(rows)
        self.status_label.setText(status_message)

    def _update_selected_issue(self, status: str) -> None:
        issue_id = self._selected_issue_id()
        if issue_id is None:
            QMessageBox.warning(self, "Prüfpunkt auswählen", "Bitte zuerst einen Prüfpunkt in der Tabelle auswählen.")
            return
        if self.session_factory is None:
            self.status_label.setText("Keine Datenbankverbindung vorhanden.")
            return
        session = self.session_factory()
        try:
            if status == "erledigt":
                mark_issue_resolved(session, issue_id)
                self.status_label.setText("Prüfpunkt als erledigt markiert.")
            else:
                reopen_issue(session, issue_id)
                self.status_label.setText("Prüfpunkt wieder geöffnet.")
            rows = list_checklist_issues(session, include_done=True)
        finally:
            session.close()
        self.show_issues(rows)

    def _priority_label(self, row) -> str:
        if row.status == "erledigt":
            return "Erledigt"
        issue_type = getattr(row, "issue_type", "") or ""
        if issue_type in {"product_alias", "price_mismatch"}:
            return "Blocker"
        if issue_type.startswith("customer_"):
            return "Prüfen"
        return "Hinweis"

    def _selected_issue_id(self) -> int | None:
        row = self.issue_table.currentRow()
        return self.issue_ids_by_row.get(row)
