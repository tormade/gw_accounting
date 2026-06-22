from getraenkeladen_tool.ui.main_window import CLAIM_PATH, LOGO_PATH, MAIN_TABS, MAIN_WINDOW_INITIAL_SIZE, MAIN_WINDOW_MINIMUM_SIZE
from getraenkeladen_tool.ui.theme import APP_STYLESHEET


def test_main_window_exposes_first_version_tabs():
    assert MAIN_TABS == ("Start", "Kunden", "Produkte", "Auftraege", "Listen", "Einstellungen")


def test_main_window_uses_resizable_screen_friendly_size():
    assert MAIN_WINDOW_INITIAL_SIZE == (1180, 760)
    assert MAIN_WINDOW_MINIMUM_SIZE == (900, 560)


def test_main_window_wraps_large_tabs_in_scroll_areas():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "QScrollArea" in source
    assert "setWidgetResizable(True)" in source
    assert "self.tabs.addTab(self._scrollable_tab(" in source


def test_theme_uses_winklmeier_work_tool_direction():
    assert "#111111" in APP_STYLESHEET
    assert "#f5f5f2" in APP_STYLESHEET
    assert "#b91c1c" in APP_STYLESHEET
    assert "guidanceBox" in APP_STYLESHEET
    assert "sectionBox" in APP_STYLESHEET
    assert "helpButton" in APP_STYLESHEET
    assert "sectionTitle" in APP_STYLESHEET
    assert "documentHeaderCard" in APP_STYLESHEET


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


def test_main_window_removes_separate_document_tab_special_path():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "DocumentPanel" not in source
    assert '"Belege"' not in source


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
        "refreshOrderDataButton": "Stammdaten laden",
        "suggestOrderNumberButton": "Auftragsnummer vorschlagen",
        "suggestDeliveryNoteNumberButton": "Lieferscheinnummer vorschlagen",
        "suggestInvoiceNumberButton": "Rechnungsnummer vorschlagen",
        "addOrderLineButton": "Position hinzufuegen",
        "removeOrderLineButton": "Position entfernen",
        "saveOrderButton": "Auftrag speichern",
        "createDeliveryOrderButton": "LS Excel/PDF erstellen",
        "createInvoiceButton": "Rechnung Excel/PDF erstellen",
        "refreshOrdersButton": "Auftragsliste laden",
    }
    assert ORDER_PANEL_SECTIONS == (
        "Kopfdaten",
        "Positionen",
        "Excel/PDF aus Auftrag erstellen",
        "Bestehende Auftraege",
    )
    assert "Kopfdaten" in ORDER_HELP_TEXT
    assert "Positionen" in ORDER_HELP_TEXT
    assert ORDER_GUIDANCE_STEPS == (
        "Kunden suchen und Lieferdatum pruefen.",
        "Produkte hinzufuegen und Positionen kontrollieren.",
        "Auftrag speichern, danach Lieferauftrag oder Rechnung gezielt erstellen.",
    )
    assert ORDER_CONTEXT_ACTIONS == {
        "open": "Auftrag oeffnen",
        "create_delivery_order": "LS Excel/PDF erstellen",
        "create_invoice": "Rechnung Excel/PDF erstellen",
        "archive": "Auftrag archivieren",
    }


def test_customer_tab_exposes_master_data_actions():
    from getraenkeladen_tool.ui.customer_panel import (
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
        "Artikel mit Einheit und Standardpreis pflegen.",
        "Vorhandene Artikel unten auswaehlen und zur Bearbeitung laden.",
        "Aenderungen koennen vor dem Speichern verworfen werden.",
    )
    assert PRODUCT_CONTEXT_ACTIONS == {
        "edit": "Produkt bearbeiten",
        "deactivate": "Produkt deaktivieren",
        "restore": "Produkt wiederherstellen",
    }


def test_settings_tab_exposes_dropdown_list_actions():
    from getraenkeladen_tool.ui.settings_panel import SETTINGS_PANEL_ACTIONS, SETTINGS_PANEL_SECTIONS

    assert SETTINGS_PANEL_ACTIONS == {
        "settingsHelpButton": "?",
        "refreshUnitsButton": "Einheiten laden",
        "addUnitButton": "Einheit hinzufuegen",
        "chooseInputFolderButton": "Input-Ordner waehlen",
        "importMasterDataButton": "Stammdaten importieren",
    }
    assert SETTINGS_PANEL_SECTIONS == ("Produkteinheiten bearbeiten",)


def test_dashboard_tab_exposes_daily_guidance():
    from getraenkeladen_tool.ui.dashboard_panel import DASHBOARD_ACTIONS, DASHBOARD_CARDS, DASHBOARD_GUIDANCE_STEPS

    assert DASHBOARD_ACTIONS == {
        "dashboardHelpButton": "?",
        "newDeliveryButton": "Neue Lieferung erfassen",
        "refreshDashboardButton": "Heute aktualisieren",
    }
    assert DASHBOARD_CARDS == ("Lieferungen heute", "Offene Posten", "Kontaktanfragen heute")
    assert DASHBOARD_GUIDANCE_STEPS == (
        "Neue Lieferung erfassen starten.",
        "Kunde auswaehlen und bei Bedarf letzte Bestellung uebernehmen.",
        "PDF-Belege erzeugen oder offene Aufgaben ueber die Karten pruefen.",
    )


def test_dashboard_primary_action_opens_order_tab():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "new_delivery_requested.connect(self.open_orders_tab)" in source
    assert 'MAIN_TABS.index("Auftraege")' in source


def test_main_window_refreshes_tab_data_when_user_switches_tabs():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert "currentChanged.connect(self.refresh_current_tab)" in source
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
