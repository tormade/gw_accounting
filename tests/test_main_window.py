from getraenkeladen_tool.ui.main_window import CLAIM_PATH, LOGO_PATH, MAIN_TABS, MAIN_WINDOW_INITIAL_SIZE, MAIN_WINDOW_MINIMUM_SIZE
from getraenkeladen_tool.ui.theme import APP_STYLESHEET


def test_main_window_exposes_first_version_tabs():
    assert MAIN_TABS == (
        "Heute",
        "Kunde & Bestellung",
        "Belege",
        "Offene Posten",
        "Tagesliste",
        "Stammdaten",
        "Pruefliste",
        "Einstellungen",
    )


def test_main_window_uses_resizable_screen_friendly_size():
    assert MAIN_WINDOW_INITIAL_SIZE == (1180, 760)
    assert MAIN_WINDOW_MINIMUM_SIZE == (900, 560)


def test_main_window_wraps_large_tabs_in_scroll_areas():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "QScrollArea" in source
    assert "setWidgetResizable(True)" in source
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


def test_dashboard_new_delivery_opens_order_dialog():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "self.dashboard_panel.new_delivery_requested.connect(self.open_new_order_dialog)" in source
    assert "def open_new_order_dialog" in source
    assert "self.order_panel.open_new_order_dialog()" in source


def test_theme_uses_winklmeier_work_tool_direction():
    assert "#f4f1ea" in APP_STYLESHEET
    assert "#116149" in APP_STYLESHEET
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


def test_theme_uses_light_website_inspired_navigation_instead_of_black_bars():
    assert "QWidget#brandHeader {\n    background: #ffffff;" in APP_STYLESHEET
    assert "QListWidget#sidebarNavigation {\n    background: #ffffff;" in APP_STYLESHEET
    assert "background: #111111;" not in APP_STYLESHEET
    assert "background: #151515;" not in APP_STYLESHEET
    assert "QListWidget#sidebarNavigation::item:selected {\n    background: #e8f3ee;" in APP_STYLESHEET


def test_forms_and_tables_have_clean_work_area_treatment():
    assert "QWidget#contentSurface" in APP_STYLESHEET
    assert "QLineEdit#tableSearchField" in APP_STYLESHEET
    assert "QWidget#totalBar" in APP_STYLESHEET
    assert "QLineEdit:focus" in APP_STYLESHEET
    assert "QTableWidget::item:selected" in APP_STYLESHEET
    assert "selection-background-color: #d7ebe2" in APP_STYLESHEET
    assert "selection-color: #123326" in APP_STYLESHEET
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
    assert 'setObjectName("pageHeader")' in source
    assert 'setObjectName("actionCard")' in source
    assert 'setObjectName("workspaceSplitter")' in source
    assert 'setObjectName("sidebarNavigation")' in source
    assert 'setObjectName("pageToolbar")' in source
    assert 'setObjectName("contentSurface")' in source
    assert "class WorkspaceCard" in source
    assert 'setObjectName("workspaceCard")' in source


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
    assert "ResponsiveSplitter" in customer_source
    assert "WorkspaceCard" in customer_source
    assert "setStretchFactor(0, 3)" in customer_source
    assert "setStretchFactor(1, 2)" in customer_source
    assert "ContentSurface" in product_source
    assert "ResponsiveSplitter" in product_source
    assert "WorkspaceCard" in product_source
    assert "setStretchFactor(0, 3)" in product_source
    assert "setStretchFactor(1, 2)" in product_source


def test_dashboard_uses_modern_surface_and_action_grid():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/dashboard_panel.py").read_text(encoding="utf-8")

    assert "ContentSurface" in source
    assert "QGridLayout" in source
    assert "quick_action_grid" in source
    assert "setColumnStretch" in source


def test_order_form_gives_selection_fields_room_to_grow():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "self.customer_select.setMinimumWidth(420)" in source
    assert "self.product_select.setMinimumWidth(420)" in source


def test_target_state_navigation_prioritizes_daily_flow_and_main_order_path():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert '"Heute"' in source
    assert '"Kunde & Bestellung"' in source
    assert '"Offene Posten"' in source
    assert '"Tagesliste"' in source
    assert '"Pruefliste"' in source
    assert '"Auftraege"' not in source
    assert '"Listen"' not in source
    assert 'MAIN_TABS.index("Kunde & Bestellung")' in source
    assert 'MAIN_TABS.index("Belege")' in source


def test_main_window_uses_real_checklist_panel_for_migration_conflicts():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "from .checklist_panel import ChecklistPanel" in source
    assert "self.checklist_panel = ChecklistPanel(session_factory=session_factory)" in source
    assert '"Pruefliste": (self.checklist_panel.refresh_issues,)' in source
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
    assert "def use_central_price_for_selected_issue" in source
    assert "def keep_excel_price_for_selected_issue" in source
    assert "def confirm_product_alias_for_selected_issue" in source
    assert "def use_list_value_for_selected_issue" in source
    assert "def use_folder_value_for_selected_issue" in source


def test_date_fields_use_calendar_input():
    from getraenkeladen_tool.ui.customer_panel import DATE_FIELD_WIDGETS as CUSTOMER_DATE_FIELDS
    from getraenkeladen_tool.ui.document_panel import DATE_FIELD_WIDGETS as DOCUMENT_DATE_FIELDS
    from getraenkeladen_tool.ui.order_panel import DATE_FIELD_WIDGETS as ORDER_DATE_FIELDS
    from getraenkeladen_tool.ui.report_panel import DATE_FIELD_WIDGETS as REPORT_DATE_FIELDS

    assert CUSTOMER_DATE_FIELDS == ("next_contact_date",)
    assert DOCUMENT_DATE_FIELDS == ("delivery_date",)
    assert ORDER_DATE_FIELDS == ("delivery_date",)
    assert REPORT_DATE_FIELDS == ("target_date",)


def test_brand_assets_are_available():
    assert LOGO_PATH.exists()
    assert CLAIM_PATH.exists()


def test_main_window_groups_document_workflows_under_target_state_belege_workspace():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "DocumentPanel" not in source
    assert '"Belege"' in source
    assert "def _document_workspace" in source
    assert 'tabs.addTab(self.document_archive_panel, "Archiv")' in source


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
        "newOrderButton": "Bestellung erfassen",
        "copyOrderButton": "Aus letzter Bestellung uebernehmen",
        "refreshOrderDataButton": "Stammdaten laden",
        "addOrderLineButton": "Position hinzufuegen",
        "removeOrderLineButton": "Position entfernen",
        "addDepositReturnButton": "Pfand zurueck hinzufuegen",
        "removeDepositReturnButton": "Pfand zurueck entfernen",
        "saveOrderButton": "Bestellung speichern",
        "refreshOrdersButton": "Bestellungen laden",
        "createDeliveryNoteFromOrderButton": "Lieferschein erstellen",
        "createInvoiceFromOrderButton": "Rechnung erstellen",
    }
    assert ORDER_PANEL_SECTIONS == (
        "Kundenkopf",
        "Kundensortiment",
        "Bestellungen verwalten",
    )
    assert "Kundenkopf" in ORDER_HELP_TEXT
    assert "Kundensortiment" in ORDER_HELP_TEXT
    assert ORDER_GUIDANCE_STEPS == (
        "Kunde suchen und letzte Mengen als Vorlage sehen.",
        "Neue Mengen, neue Artikel und Pfand-Rueckgabe erfassen.",
        "Bestellung speichern und daraus Lieferschein oder Rechnung erzeugen.",
    )
    assert ORDER_CONTEXT_ACTIONS == {
        "open": "Auftrag oeffnen",
        "copy": "Als neuen Auftrag kopieren",
        "create_delivery_note": "Lieferschein erstellen",
        "create_invoice": "Rechnung erstellen",
        "archive": "Auftrag archivieren",
    }


def test_main_window_has_dedicated_delivery_and_invoice_tabs():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "DeliveryNotePanel" in source
    assert "InvoicePanel" in source
    assert "self.delivery_note_panel" in source
    assert "self.invoice_panel" in source
    assert '"Belege"' in source
    assert '"Lieferscheine"' not in source
    assert '"Rechnungen"' not in source


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
        "discardCustomerChangesButton": "Aenderungen verwerfen",
        "undoCustomerChangeButton": "Letzte Aenderung rueckgaengig",
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
        "discardProductChangesButton": "Aenderungen verwerfen",
        "undoProductChangeButton": "Letzte Aenderung rueckgaengig",
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
    from getraenkeladen_tool.ui.settings_panel import SETTINGS_PANEL_ACTIONS, SETTINGS_PANEL_SECTIONS

    assert SETTINGS_PANEL_ACTIONS == {
        "settingsHelpButton": "?",
        "chooseInputFolderButton": "Input-Ordner waehlen",
        "importMasterDataButton": "Stammdaten importieren",
    }
    assert SETTINGS_PANEL_SECTIONS == ("Stammdaten aus Excel importieren",)


def test_product_panel_hides_unit_maintenance_from_user():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/product_panel.py").read_text(encoding="utf-8")

    assert 'form.addRow("Einheit", self.unit)' not in source
    assert 'PRODUCT_COLUMNS = ("Produkt", "Artikelnummer", "Preis", "Pfand", "Status")' in source


def test_dashboard_tab_exposes_daily_guidance():
    from getraenkeladen_tool.ui.dashboard_panel import DASHBOARD_ACTIONS, DASHBOARD_CARDS, DASHBOARD_GUIDANCE_STEPS

    assert DASHBOARD_ACTIONS == {
        "dashboardHelpButton": "?",
        "newDeliveryButton": "Neue Lieferung erfassen",
        "refreshDashboardButton": "Heute aktualisieren",
    }
    assert DASHBOARD_CARDS == ("Heute zu liefern", "Offene Posten", "Faellige Kontakte")
    assert DASHBOARD_GUIDANCE_STEPS == (
        "Kunde suchen oder aus der Wiedervorlage oeffnen.",
        "Letzte Mengen pruefen und nur Abweichungen eintragen.",
        "Lieferschein oder Rechnung aus der Bestellung erzeugen.",
    )


def test_dashboard_uses_cockpit_quick_actions_without_calendar():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/dashboard_panel.py").read_text(encoding="utf-8")

    assert "QCalendarWidget" not in source
    assert "ActionCard" in source
    assert "self.quick_actions" in source
    assert "Kunde suchen" in source
    assert "Rechnung erstellen" in source
    assert "heroSearchPanel" in source
    assert "todayContactList" in source


def test_dashboard_primary_action_opens_new_order_dialog():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "new_delivery_requested.connect(self.open_new_order_dialog)" in source
    assert 'MAIN_TABS.index("Kunde & Bestellung")' in source
    assert "self.order_panel.open_new_order_dialog()" in source


def test_dashboard_quick_actions_open_order_and_invoice_workspaces():
    from pathlib import Path

    dashboard_source = Path("src/getraenkeladen_tool/ui/dashboard_panel.py").read_text(encoding="utf-8")
    main_source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "manage_orders_requested = Signal()" in dashboard_source
    assert "invoice_requested = Signal()" in dashboard_source
    assert "self.search_order_card.button.clicked.connect(self.manage_orders_requested.emit)" in dashboard_source
    assert "self.invoice_card.button.clicked.connect(self.invoice_requested.emit)" in dashboard_source
    assert "manage_orders_requested.connect(self.open_orders_tab)" in main_source
    assert "invoice_requested.connect(self.open_invoices_tab)" in main_source
    assert 'MAIN_TABS.index("Belege")' in main_source


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
    assert "refresh_master_data" in source
    assert "refresh_products" in source
    assert "refresh_customers" in source


def test_report_tab_exposes_reporting_actions():
    from getraenkeladen_tool.ui.report_panel import REPORT_PANEL_ACTIONS

    assert REPORT_PANEL_ACTIONS == {
        "seedDemoDataButton": "Beispieldaten anlegen",
        "refreshOpenItemsButton": "Offene Posten aktualisieren",
        "markPaidButton": "Zahlung markieren",
        "refreshDeliveriesButton": "Lieferliste laden",
        "refreshContactsButton": "Kontaktliste laden",
        "exportOpenItemsButton": "Offene Posten exportieren",
        "exportDeliveriesButton": "Lieferliste exportieren",
        "exportContactsButton": "Kontaktliste exportieren",
    }
