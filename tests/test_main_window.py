from getraenkeladen_tool.ui.main_window import CLAIM_PATH, LOGO_PATH, MAIN_TABS, MAIN_WINDOW_INITIAL_SIZE, MAIN_WINDOW_MINIMUM_SIZE
from getraenkeladen_tool.ui.theme import APP_STYLESHEET


def test_main_window_exposes_first_version_tabs():
    assert MAIN_TABS == (
        "Heute",
        "Kunden",
        "Bestellungen",
        "Belege",
        "Rechnungen",
        "Stammdaten",
    )


def test_main_window_uses_resizable_screen_friendly_size():
    assert MAIN_WINDOW_INITIAL_SIZE == (1180, 760)
    assert MAIN_WINDOW_MINIMUM_SIZE == (900, 560)


def test_main_window_wraps_large_tabs_in_scroll_areas():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "QScrollArea" in source
    assert "setWidgetResizable(True)" in source
    assert "setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)" in source
    assert "self.pages.addWidget(self._scrollable_tab(" in source


def test_main_window_uses_sidebar_app_shell_instead_of_top_tabs():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "QStackedWidget" in source
    assert "SidebarNavigation" in source
    assert "self.navigation = SidebarNavigation(MAIN_TABS)" in source
    assert "self.pages = QStackedWidget()" in source
    assert "self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)" in source
    assert "self.tabs = QTabWidget()" not in source


def test_dashboard_quick_actions_open_customer_folder_workspace():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "self.dashboard_panel.new_delivery_requested.connect(self.open_customer_folder_tab)" in source
    assert "self.dashboard_panel.open_items_requested.connect(self.open_open_items_tab)" in source
    assert "self.dashboard_panel.checklist_requested.connect(self.open_checklist_tab)" in source
    assert "def open_customer_folder_tab" in source
    assert "def open_open_items_tab" in source
    assert "def open_checklist_tab" in source
    assert 'MAIN_TABS.index("Kunden")' in source
    assert 'MAIN_TABS.index("Rechnungen")' in source
    assert 'MAIN_TABS.index("Stammdaten")' in source


def test_main_window_removes_global_header_toolbar_in_favor_of_page_headers():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "def _toolbar" not in source
    assert 'setObjectName("appToolbar")' not in source
    assert "toolbarSearch" not in source
    assert "Kunde, Rechnung oder Artikel suchen" not in source
    assert "handle_toolbar_search" not in source
    assert "show_toolbar_help" not in source
    assert "update_toolbar_primary_action" not in source
    assert "root_layout.addWidget(self._toolbar())" not in source
    assert "brandService" not in source


def test_theme_uses_winklmeier_work_tool_direction():
    assert "#f5f5f7" in APP_STYLESHEET
    assert "#0a84ff" in APP_STYLESHEET
    assert "#c4312f" in APP_STYLESHEET
    assert "guidanceBox" in APP_STYLESHEET
    assert "sectionBox" in APP_STYLESHEET
    assert "helpButton" in APP_STYLESHEET
    assert "sectionTitle" in APP_STYLESHEET
    assert "documentHeaderCard" in APP_STYLESHEET
    assert "QPushButton#newOrderButton" in APP_STYLESHEET
    assert "QWidget#heroSearchPanel" in APP_STYLESHEET
    assert "QWidget#dailyCockpitCard" in APP_STYLESHEET
    assert "QWidget#liveSummaryCard" in APP_STYLESHEET
    assert "pageHeader" in APP_STYLESHEET
    assert "actionCard" in APP_STYLESHEET
    assert "workspaceSplitter" in APP_STYLESHEET
    assert "appShell" in APP_STYLESHEET
    assert "sidebarNavigation" in APP_STYLESHEET
    assert "pageToolbar" in APP_STYLESHEET


def test_theme_uses_light_apple_like_shell_without_global_header_bar():
    assert "QWidget#appToolbar" not in APP_STYLESHEET
    assert "QLineEdit#toolbarSearch" not in APP_STYLESHEET
    assert "QListWidget#sidebarNavigation {\n    background: #f5f5f7;" in APP_STYLESHEET
    assert "background: #111111;" not in APP_STYLESHEET
    assert "QWidget#brandHeader" not in APP_STYLESHEET
    assert "QListWidget#sidebarNavigation::item:selected {\n    background: #ffffff;" in APP_STYLESHEET


def test_theme_uses_workshop_not_ai_card_geometry():
    assert "border-radius: 18px" not in APP_STYLESHEET
    assert "border-radius: 24px" not in APP_STYLESHEET
    assert "QWidget#workspaceCard" in APP_STYLESHEET
    assert "border-radius: 8px;" in APP_STYLESHEET
    assert "min-height: 38px" in APP_STYLESHEET


def test_layouts_support_apple_like_sidebar_labels_without_numbering():
    from pathlib import Path

    layouts = Path("src/getraenkeladen_tool/ui/layouts.py").read_text(encoding="utf-8")

    assert 'QListWidgetItem(label)' in layouts
    assert 'QListWidgetItem(f"{index:02d}  {label}")' not in layouts


def test_forms_and_tables_have_clean_work_area_treatment():
    assert "QWidget#contentSurface" in APP_STYLESHEET
    assert "QLineEdit#tableSearchField" in APP_STYLESHEET
    assert "QWidget#totalBar" in APP_STYLESHEET
    assert "QLineEdit:focus" in APP_STYLESHEET
    assert "QTableWidget::item:selected" in APP_STYLESHEET
    assert "selection-background-color: #d9ebff" in APP_STYLESHEET
    assert "selection-color: #1d1d1f" in APP_STYLESHEET
    assert "QTableWidget QLineEdit" in APP_STYLESHEET


def test_theme_modernizes_dropdown_buttons_and_calendar_popups():
    assert "QComboBox::drop-down" in APP_STYLESHEET
    assert "QDateEdit::drop-down" in APP_STYLESHEET
    assert "QComboBox::down-arrow" in APP_STYLESHEET
    assert "QDateEdit::down-arrow" in APP_STYLESHEET
    assert "QComboBox:on" in APP_STYLESHEET
    assert "QDateEdit:on" in APP_STYLESHEET
    assert "QCalendarWidget" in APP_STYLESHEET
    assert "QCalendarWidget QToolButton" in APP_STYLESHEET
    assert "QPushButton:disabled" in APP_STYLESHEET
    assert "QPushButton#dangerAction" in APP_STYLESHEET


def test_shared_layout_widgets_are_available():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/layouts.py").read_text(encoding="utf-8")

    assert "class PageHeader" in source
    assert "class ActionCard" in source
    assert "class ResponsiveSplitter" in source
    assert "class SidebarNavigation" in source
    assert "class PageToolbar" in source
    assert "class ContentSurface" in source
    assert "class InspectorPanel" in source
    assert 'setObjectName("pageHeader")' in source
    assert 'setObjectName("actionCard")' in source
    assert 'setObjectName("workspaceSplitter")' in source
    assert 'setObjectName("sidebarNavigation")' in source
    assert 'setObjectName("pageToolbar")' in source
    assert 'setObjectName("contentSurface")' in source
    assert 'setObjectName("inspectorPanel")' in source
    assert "class WorkspaceCard" in source
    assert 'setObjectName("workspaceCard")' in source


def test_sidebar_navigation_is_named_for_keyboard_and_accessibility():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/layouts.py").read_text(encoding="utf-8")

    assert 'self.setAccessibleName("Hauptnavigation")' in source
    assert "Qt.FocusPolicy.StrongFocus" in source
    assert 'item.setToolTip(f"{label} oeffnen")' in source
    assert "item.setData(Qt.ItemDataRole.AccessibleTextRole, label)" in source
    assert "item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, f\"{label} oeffnen\")" in source


def test_order_and_document_workspaces_use_named_layout_regions():
    from pathlib import Path

    order_source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")
    document_source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "ContentSurface" in order_source
    assert "WorkspaceCard" in order_source
    assert "tableSearchField" in order_source
    assert 'setObjectName("totalBar")' in order_source
    assert "ContentSurface" in document_source
    assert "WorkspaceCard" in document_source
    assert "tableSearchField" in document_source
    assert 'setObjectName("totalBar")' in document_source


def test_master_data_panels_use_modern_list_with_detail_layout():
    from pathlib import Path

    customer_source = Path("src/getraenkeladen_tool/ui/customer_panel.py").read_text(encoding="utf-8")
    product_source = Path("src/getraenkeladen_tool/ui/product_panel.py").read_text(encoding="utf-8")

    assert "ContentSurface" in customer_source
    assert "WorkspaceCard" in customer_source
    assert 'kicker="KUNDENKARTE"' in customer_source
    assert 'kicker="KUNDENSTAMM"' in customer_source
    assert "layout.addWidget(edit_box)" in customer_source
    assert "layout.addWidget(list_box, 1)" in customer_source
    assert "ContentSurface" in product_source
    assert "WorkspaceCard" in product_source
    assert 'kicker="PREISKARTE"' in product_source
    assert 'kicker="ARTIKELSTAMM"' in product_source
    assert "layout.addWidget(edit_box)" in product_source
    assert "layout.addWidget(list_box, 1)" in product_source


def test_dashboard_uses_guided_workflow_board():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/dashboard_panel.py").read_text(encoding="utf-8")

    assert "ContentSurface" in source
    assert "QGridLayout" in source
    assert "def _task_queue" in source
    assert "workflowStepButton" in source
    assert "Tagesliste" in source
    assert "setColumnStretch" in source
    assert "Demo-Beispiele" not in source


def test_order_form_gives_selection_fields_room_to_grow():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.customer_select.setMinimumWidth(420)" in source
    assert "self.product_select.setMinimumWidth(420)" in source


def test_target_state_navigation_prioritizes_customer_folder_path():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert '"Heute"' in source
    assert '"Kunden"' in source
    assert '"Bestellungen"' in source
    assert '"Belege"' in source
    assert '"Rechnungen"' in source
    assert '"Kunde & Bestellung"' not in source
    assert '"Auftraege"' not in source
    assert 'MAIN_TABS.index("Kunden")' in source


def test_main_window_uses_real_checklist_panel_for_migration_conflicts():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "from .checklist_panel import ChecklistPanel" in source
    assert "self.checklist_panel = ChecklistPanel(session_factory=session_factory)" in source
    assert 'tabs.addTab(self.checklist_panel, "Pruefpunkte")' in source
    assert 'self._panel(\n            "Pruefliste"' not in source


def test_checklist_panel_exposes_concrete_resolution_actions():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/checklist_panel.py").read_text(encoding="utf-8")

    assert "resolve_price_mismatch" in source
    assert "confirm_product_alias" in source
    assert "self.product_select = SearchableSelect" in source
    assert '"useCentralPriceButton": "Zentralen Preis nutzen"' in source
    assert '"keepExcelPriceButton": "Excel-Preis behalten"' in source
    assert '"confirmProductAliasButton": "Artikel zuordnen"' in source
    assert '"useListValueButton": "Zentrale Liste nutzen"' in source
    assert '"useFolderValueButton": "Kunden-Excel nutzen"' in source
    assert 'CHECKLIST_COLUMNS = ("Prioritaet", "Kunde", "Problem", "Naechster Schritt")' in source
    assert "self.issue_detail_panel = InspectorPanel" in source
    assert "def update_issue_context" in source
    assert "def _set_issue_action_visibility" in source
    assert "def _priority_label" in source
    assert "def use_central_price_for_selected_issue" in source
    assert "def keep_excel_price_for_selected_issue" in source
    assert "def confirm_product_alias_for_selected_issue" in source
    assert "def use_list_value_for_selected_issue" in source
    assert "def use_folder_value_for_selected_issue" in source


def test_checklist_panel_explains_data_changing_actions_for_uncertain_users():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/checklist_panel.py").read_text(encoding="utf-8")

    assert "Pruefpunkt auswaehlen" in source
    assert "Nur die passenden Aktionen werden angezeigt." in source
    assert "Diese Entscheidung aendert Stammdaten oder Kundensortiment dauerhaft." in source


def test_date_fields_use_calendar_input():
    from getraenkeladen_tool.ui.customer_panel import DATE_FIELD_WIDGETS as CUSTOMER_DATE_FIELDS
    from getraenkeladen_tool.ui.order_panel import DATE_FIELD_WIDGETS as ORDER_DATE_FIELDS
    from getraenkeladen_tool.ui.report_panel import DATE_FIELD_WIDGETS as REPORT_DATE_FIELDS

    assert CUSTOMER_DATE_FIELDS == ("next_contact_date",)
    assert ORDER_DATE_FIELDS == ("delivery_date",)
    assert REPORT_DATE_FIELDS == ("target_date",)


def test_open_items_surface_shows_due_date_and_payment_method():
    from getraenkeladen_tool.ui.report_panel import OPEN_ITEMS_COLUMNS

    assert OPEN_ITEMS_COLUMNS == (
        "Kunde",
        "Rechnungsnr.",
        "Datum",
        "Faelligkeit",
        "Zahlart",
        "Betrag",
        "Status",
    )


def test_brand_assets_are_available():
    assert LOGO_PATH.exists()
    assert CLAIM_PATH.exists()


def test_main_window_keeps_document_workflows_as_internal_helpers():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "DocumentPanel" not in source
    assert "self.document_workspace =" not in source
    assert "self.pages.addWidget(self._scrollable_tab(self.document_workspace))" not in source
    assert "DocumentArchivePanel" in source
    assert "DeliveryNotePanel" in source
    assert "InvoicePanel" in source


def test_order_tab_exposes_guided_order_actions():
    from getraenkeladen_tool.ui.order_panel import (
        ORDER_CONTEXT_ACTIONS,
        ORDER_GUIDANCE_STEPS,
        ORDER_HELP_TEXT,
        ORDER_PANEL_ACTIONS,
        ORDER_PANEL_SECTIONS,
    )

    assert ORDER_PANEL_ACTIONS == {
        "orderHelpButton": "?",
        "newOrderButton": "Neue Bestellung",
        "copyOrderButton": "Als Vorlage kopieren",
        "refreshOrderDataButton": "Daten neu laden",
        "suggestOrderNumberButton": "Nummer vorschlagen",
        "addOrderLineButton": "Position hinzufuegen",
        "removeOrderLineButton": "Position entfernen",
        "addDepositReturnButton": "Pfand-Rueckgabe eintragen",
        "removeDepositReturnButton": "Pfand-Rueckgabe entfernen",
        "saveOrderButton": "Bestellung speichern",
        "refreshOrdersButton": "Bestellungen laden",
        "createDeliveryNoteFromOrderButton": "Lieferschein erstellen",
        "createInvoiceFromOrderButton": "Rechnung erstellen",
    }
    assert ORDER_PANEL_SECTIONS == (
        "Kunde und Lieferdatum",
        "Mengen erfassen",
        "Bestellungen",
    )
    assert "Kunde und Lieferdatum" in ORDER_HELP_TEXT
    assert "Mengen erfassen" in ORDER_HELP_TEXT
    assert ORDER_GUIDANCE_STEPS == (
        "Kunde suchen und letzte Mengen als Vorlage sehen.",
        "Neue Mengen, neue Artikel und Pfand-Rueckgabe erfassen.",
        "Bestellung speichern und daraus Lieferschein oder Rechnung erzeugen.",
    )
    assert ORDER_CONTEXT_ACTIONS == {
        "open": "Bestellung oeffnen",
        "copy": "Als neue Bestellung kopieren",
        "create_delivery_note": "Lieferschein erstellen",
        "create_invoice": "Rechnung erstellen",
        "archive": "Bestellung archivieren",
    }


def test_main_window_has_dedicated_delivery_and_invoice_tabs():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "DeliveryNotePanel" in source
    assert "InvoicePanel" in source
    assert "self.delivery_note_panel" in source


def test_main_window_embeds_customer_folder_as_second_page_and_wires_actions():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "from .customer_folder_panel import CustomerFolderPanel" in source
    assert "self.customer_folder_panel = CustomerFolderPanel(session_factory=session_factory)" in source
    assert "self.pages.addWidget(self._scrollable_tab(self.customer_folder_panel))" in source
    assert "self.customer_folder_panel.new_order_requested.connect(self.open_new_order_for_customer)" in source
    assert "self.order_panel.open_new_order_for_customer(customer_id)" in source
    assert "self.customer_folder_panel.delivery_note_requested.connect(self.open_delivery_note_for_order)" in source
    assert "self.customer_folder_panel.invoice_requested.connect(self.open_invoice_for_order)" in source
    assert "self.customer_folder_panel.new_order_requested.connect(self.open_new_order_for_customer)" in source
    assert '"Lieferscheine"' not in source
    assert '"Rechnungen"' in source


def test_customer_folder_request_opens_order_tab_not_customer_tab():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "def open_new_order_for_customer" in source
    assert "self.open_orders_tab()" in source
    assert "self.order_panel.open_new_order_for_customer(customer_id)" in source
    assert "self.open_customer_folder_tab()\n        self.order_panel.open_new_order_for_customer(customer_id)" not in source


def test_main_window_opens_document_workflows_as_visible_dialogs_from_customer_folder():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "QDialog" in source
    assert "self.document_dialogs" in source
    assert "def _open_document_dialog" in source
    assert "dialog.show()" in source
    assert "panel.select_order(order_id)" in source
    assert "self._open_document_dialog(DeliveryNotePanel, order_id, \"Lieferschein erstellen\")" in source
    assert "self._open_document_dialog(InvoicePanel, order_id, \"Rechnung erstellen\")" in source


def test_customer_tab_exposes_master_data_actions():
    from getraenkeladen_tool.ui.customer_panel import (
        CUSTOMER_COLUMNS,
        CUSTOMER_CONTEXT_ACTIONS,
        CUSTOMER_GUIDANCE_STEPS,
        CUSTOMER_PANEL_ACTIONS,
        CUSTOMER_PANEL_SECTIONS,
    )

    assert CUSTOMER_PANEL_ACTIONS == {
        "customerHelpButton": "?",
        "newCustomerButton": "Neu",
        "saveCustomerButton": "Kunde speichern",
        "discardCustomerChangesButton": "Verwerfen",
        "undoCustomerChangeButton": "Rueckgaengig",
        "refreshCustomersButton": "Kundenliste laden",
        "loadCustomerButton": "Auswahl bearbeiten",
        "archiveCustomerButton": "Kunde archivieren",
        "restoreCustomerButton": "Kunde wiederherstellen",
        "chooseCustomerFolderButton": "Ordner waehlen",
    }
    assert CUSTOMER_PANEL_SECTIONS == ("1. Kunden erfassen", "2. Bestehende Kunden pruefen")
    assert CUSTOMER_GUIDANCE_STEPS == (
        "Neuen Kunden links eintragen oder unten einen Kunden auswaehlen.",
        "Mit Auswahl bearbeiten Stammdaten in das Formular laden.",
        "Aenderungen koennen vor dem Speichern verworfen werden.",
    )
    assert CUSTOMER_CONTEXT_ACTIONS == {
        "edit": "Kunde bearbeiten",
        "archive": "Kunde archivieren",
        "restore": "Kunde wiederherstellen",
    }
    assert CUSTOMER_COLUMNS == ("Name", "Adresse", "Naechster Kontakt", "Status")


def test_product_tab_exposes_price_list_actions():
    from getraenkeladen_tool.ui.product_panel import (
        PRODUCT_CONTEXT_ACTIONS,
        PRODUCT_GUIDANCE_STEPS,
        PRODUCT_PANEL_ACTIONS,
        PRODUCT_PANEL_SECTIONS,
    )

    assert PRODUCT_PANEL_ACTIONS == {
        "productHelpButton": "?",
        "newProductButton": "Neu",
        "saveProductButton": "Produkt speichern",
        "discardProductChangesButton": "Verwerfen",
        "undoProductChangeButton": "Rueckgaengig",
        "refreshProductsButton": "Produktliste laden",
        "loadProductButton": "Auswahl bearbeiten",
        "deactivateProductButton": "Produkt deaktivieren",
        "restoreProductButton": "Produkt wiederherstellen",
    }
    assert PRODUCT_PANEL_SECTIONS == ("1. Produkt erfassen", "2. Preisliste pruefen")
    assert PRODUCT_GUIDANCE_STEPS == (
        "Artikel mit Standardpreis pflegen.",
        "Vorhandene Artikel unten auswaehlen und zur Bearbeitung laden.",
        "Aenderungen koennen vor dem Speichern verworfen werden.",
    )
    assert PRODUCT_CONTEXT_ACTIONS == {
        "edit": "Produkt bearbeiten",
        "deactivate": "Produkt deaktivieren",
        "restore": "Produkt wiederherstellen",
    }


def test_settings_tab_focuses_on_master_data_import_without_number_sequences():
    from pathlib import Path

    from getraenkeladen_tool.ui.settings_panel import SETTINGS_PANEL_ACTIONS, SETTINGS_PANEL_SECTIONS

    assert SETTINGS_PANEL_ACTIONS == {
        "settingsHelpButton": "?",
        "chooseInputFolderButton": "Ordner waehlen",
        "previewMasterDataButton": "Import pruefen",
        "importMasterDataButton": "Import starten",
    }
    assert SETTINGS_PANEL_SECTIONS == ("Excel-Stammdaten importieren",)
    source = Path("src/getraenkeladen_tool/ui/settings_panel.py").read_text(encoding="utf-8")
    assert "preview_master_data_from_folder" in source
    assert "Import bestaetigen" in source
    assert "preview.safety_report_text" in source


def test_product_panel_hides_unit_maintenance_from_user():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/product_panel.py").read_text(encoding="utf-8")

    assert 'form.addRow("Einheit", self.unit)' not in source
    assert 'PRODUCT_COLUMNS = ("Produkt", "Artikelnummer", "Preis", "Pfand", "Status")' in source


def test_dashboard_tab_exposes_daily_guidance():
    from getraenkeladen_tool.ui.dashboard_panel import DASHBOARD_ACTIONS, DASHBOARD_CARDS, DASHBOARD_GUIDANCE_STEPS

    assert DASHBOARD_ACTIONS == {
        "dashboardHelpButton": "?",
        "newDeliveryButton": "Kunden oeffnen",
        "refreshDashboardButton": "Heute aktualisieren",
    }
    assert DASHBOARD_CARDS == ("Lieferungen", "Rechnungen", "Kontakte")
    assert DASHBOARD_GUIDANCE_STEPS == (
        "Faellige Aufgabe auswaehlen.",
        "Kunde oder Rechnung im Kontext pruefen.",
        "Naechste Aktion direkt ausfuehren.",
    )


def test_dashboard_uses_cockpit_quick_actions_without_calendar():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/dashboard_panel.py").read_text(encoding="utf-8")

    assert "QCalendarWidget" not in source
    assert "ActionCard" not in source
    assert "self.quick_action_buttons" in source
    assert "Kunde oder Lieferung starten" in source
    assert "Bestellung weiterbearbeiten" in source
    assert "Rechnung oder Zahlung pruefen" in source
    assert "Blocker klaeren" in source
    assert "heroSearchPanel" not in source
    assert "todayContactList" not in source
    assert "Heute starten" not in source
    assert "Im Kundenordner suchen Sie den Kunden" not in source
    assert "Metz..." not in source
    assert "heroSearchQuery" not in source
    assert "Kunde & Bestellung" not in source
    assert "Zu Belegen" not in source


def test_dashboard_uses_compact_summary_rows_instead_of_tall_metric_cards():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/dashboard_panel.py").read_text(encoding="utf-8")

    assert "def _summary_panel" in source
    assert "todaySummaryPanel" in source
    assert "Ueberblick" in source
    assert "metricHint" in source
    assert "addLayout(self._cards_grid()" not in source


def test_dashboard_copy_matches_customer_folder_workflow():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/dashboard_panel.py").read_text(encoding="utf-8")

    assert "Kundenordner öffnen: Startet den normalen Arbeitsablauf" not in source
    assert "Kundenordner oeffnen: Startet den normalen Arbeitsablauf" not in source
    assert "Kunden suchen, Hinweise sehen, Bestellung beginnen." in source
    assert "Kundenordner" not in source
    assert "Heute: Hier stehen die Aufgaben" in source


def test_dashboard_primary_action_opens_customer_folder_tab():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "new_delivery_requested.connect(self.open_customer_folder_tab)" in source
    assert 'MAIN_TABS.index("Kunden")' in source


def test_dashboard_quick_actions_open_customer_folder_workspace_signals():
    from pathlib import Path

    dashboard_source = Path("src/getraenkeladen_tool/ui/dashboard_panel.py").read_text(encoding="utf-8")
    main_source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "open_items_requested = Signal()" in dashboard_source
    assert "checklist_requested = Signal()" in dashboard_source
    assert "button.clicked.connect(signal.emit)" in dashboard_source
    assert "manage_orders_requested" not in dashboard_source
    assert "invoice_requested = Signal()" not in dashboard_source
    assert "open_items_requested.connect(self.open_open_items_tab)" in main_source
    assert "checklist_requested.connect(self.open_checklist_tab)" in main_source
    assert 'MAIN_TABS.index("Kunden")' in main_source


def test_order_manage_actions_open_delivery_or_invoice_with_selected_order():
    from pathlib import Path

    order_source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")
    main_source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")
    document_source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "delivery_note_requested = Signal(int)" in order_source
    assert "invoice_requested = Signal(int)" in order_source
    assert '"createDeliveryNoteFromOrderButton": "Lieferschein erstellen"' in order_source
    assert '"createInvoiceFromOrderButton": "Rechnung erstellen"' in order_source
    assert "self.create_delivery_note_button.clicked.connect(self.request_delivery_note_for_selected_order)" in order_source
    assert "self.create_invoice_button.clicked.connect(self.request_invoice_for_selected_order)" in order_source
    assert "delivery_note_requested.connect(self.open_delivery_note_for_order)" in main_source
    assert "invoice_requested.connect(self.open_invoice_for_order)" in main_source
    assert "def open_delivery_note_for_order" in main_source
    assert "def open_invoice_for_order" in main_source
    assert "def select_order" in document_source


def test_main_window_refreshes_tab_data_when_user_switches_tabs():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "currentRowChanged.connect(self.refresh_current_tab)" in source
    assert "def refresh_current_tab" in source
    assert "refresh_products" in source
    assert "refresh_customers" in source


def test_main_window_refreshes_only_active_master_data_panel():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert '"Stammdaten": (self.refresh_active_master_data_panel,)' in source
    assert "self.master_data_workspace.currentChanged.connect(self.refresh_active_master_data_panel)" in source
    assert "def refresh_active_master_data_panel" in source
    assert '"Stammdaten": (self.customer_panel.refresh_customers, self.product_panel.refresh_products)' not in source


def test_master_data_panels_load_lazily_once_to_keep_tab_switch_fast():
    import ast
    from pathlib import Path

    def init_calls_refresh(source: str, class_name: str, refresh_name: str) -> bool:
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        for call in ast.walk(item):
                            if (
                                isinstance(call, ast.Call)
                                and isinstance(call.func, ast.Attribute)
                                and call.func.attr == refresh_name
                            ):
                                return True
        return False

    main_source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")
    customer_source = Path("src/getraenkeladen_tool/ui/customer_panel.py").read_text(encoding="utf-8")
    product_source = Path("src/getraenkeladen_tool/ui/product_panel.py").read_text(encoding="utf-8")
    checklist_source = Path("src/getraenkeladen_tool/ui/checklist_panel.py").read_text(encoding="utf-8")

    assert "self._loaded_master_data_panels: set[QWidget] = set()" in main_source
    assert "if current_panel in self._loaded_master_data_panels:" in main_source
    assert "current_panel.ensure_loaded()" in main_source
    assert "self._loaded_master_data_panels.add(current_panel)" in main_source

    assert "self.has_loaded = False" in customer_source
    assert "def ensure_loaded" in customer_source
    assert not init_calls_refresh(customer_source, "CustomerPanel", "refresh_customers")

    assert "self.has_loaded = False" in product_source
    assert "def ensure_loaded" in product_source
    assert not init_calls_refresh(product_source, "ProductPanel", "refresh_products")

    assert "self.has_loaded = False" in checklist_source
    assert "def ensure_loaded" in checklist_source
    assert not init_calls_refresh(checklist_source, "ChecklistPanel", "refresh_products")
    assert not init_calls_refresh(checklist_source, "ChecklistPanel", "refresh_issues")


def test_checklist_shortcut_selects_subtab_before_master_data_refresh():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")
    method_start = source.index("    def open_checklist_tab")
    method_end = source.index("    def open_orders_tab", method_start)
    method_source = source[method_start:method_end]

    assert method_source.index("self.master_data_workspace.setCurrentWidget(self.checklist_panel)") < method_source.index(
        'self.navigation.setCurrentRow(MAIN_TABS.index("Stammdaten"))'
    )


def test_master_data_tables_pause_repaints_during_bulk_fill():
    from pathlib import Path

    customer_source = Path("src/getraenkeladen_tool/ui/customer_panel.py").read_text(encoding="utf-8")
    product_source = Path("src/getraenkeladen_tool/ui/product_panel.py").read_text(encoding="utf-8")
    checklist_source = Path("src/getraenkeladen_tool/ui/checklist_panel.py").read_text(encoding="utf-8")

    assert "self.customers_table.setUpdatesEnabled(False)" in customer_source
    assert "self.customers_table.setUpdatesEnabled(True)" in customer_source
    assert "finally:" in customer_source

    assert "self.products_table.setUpdatesEnabled(False)" in product_source
    assert "self.products_table.setUpdatesEnabled(True)" in product_source
    assert "finally:" in product_source

    assert "self.issue_table.setUpdatesEnabled(False)" in checklist_source
    assert "self.issue_table.setUpdatesEnabled(True)" in checklist_source
    assert "finally:" in checklist_source


def test_report_tab_exposes_reporting_actions():
    from pathlib import Path

    from getraenkeladen_tool.ui.report_panel import REPORT_PANEL_ACTIONS

    assert REPORT_PANEL_ACTIONS == {
        "seedDemoDataButton": "Beispieldaten anlegen",
        "refreshOpenItemsButton": "Aktualisieren",
        "markPaidButton": "Bezahlt",
        "markPartialButton": "Teilzahlung",
        "refreshDeliveriesButton": "Lieferliste laden",
        "refreshContactsButton": "Kontaktliste laden",
        "exportOpenItemsButton": "Exportieren",
        "exportDeliveriesButton": "Lieferliste exportieren",
        "exportContactsButton": "Kontaktliste exportieren",
    }
    source = Path("src/getraenkeladen_tool/ui/report_panel.py").read_text(encoding="utf-8")
    assert "self.invoice_status_filter = QComboBox()" in source
    assert "list_invoice_worklist" in source
    assert "mark_open_item_partially_paid" in source
    assert "invoice_action_row = QHBoxLayout()" in source
    assert "self.invoice_inspector.body.addLayout(invoice_action_row)" in source
    assert "self.refresh_button.setMinimumWidth(220)" in source


def test_report_mark_paid_requires_confirmation_and_does_not_auto_jump_selection():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/report_panel.py").read_text(encoding="utf-8")

    assert "QMessageBox.question" in source
    assert "Zahlung markieren" in source
    assert "Diese Rechnung wirklich als bezahlt markieren?" in source
    assert "self._select_open_item_by_id(open_item_id)" in source
    assert "def _select_open_item_by_id" in source


def test_product_panel_marks_missing_required_name_inline():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/product_panel.py").read_text(encoding="utf-8")

    assert "def _validate_product_form" in source
    assert 'setProperty("state", "error")' in source
    assert "Bitte Produktnamen eintragen." in source
    assert "self.product_name.setFocus()" in source
