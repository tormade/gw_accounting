from getraenkeladen_tool.ui.main_window import CLAIM_PATH, LOGO_PATH, MAIN_TABS
from getraenkeladen_tool.ui.theme import APP_STYLESHEET


def test_main_window_exposes_first_version_tabs():
    assert MAIN_TABS == ("Start", "Kunden", "Produkte", "Auftraege", "Belege", "Listen", "Einstellungen")


def test_theme_uses_winklmeier_work_tool_direction():
    assert "#111111" in APP_STYLESHEET
    assert "#f5f5f2" in APP_STYLESHEET
    assert "#b91c1c" in APP_STYLESHEET
    assert "guidanceBox" in APP_STYLESHEET
    assert "sectionBox" in APP_STYLESHEET


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


def test_document_tab_exposes_first_document_form_actions():
    from getraenkeladen_tool.ui.document_panel import DOCUMENT_FORM_ACTIONS

    assert DOCUMENT_FORM_ACTIONS == {
        "sampleDocumentButton": "Beispiel laden",
        "chooseCustomerFolderButton": "Ordner waehlen",
        "refreshMasterDataButton": "Stammdaten laden",
        "addLineItemButton": "Position hinzufuegen",
        "removeLineItemButton": "Position entfernen",
        "saveOrderButton": "Auftrag speichern",
        "createOrderDocumentsButton": "Lieferschein und Rechnung aus Auftrag",
        "createDocumentButton": "Excel und PDF erstellen",
    }


def test_order_tab_exposes_guided_order_actions():
    from getraenkeladen_tool.ui.order_panel import (
        ORDER_CONTEXT_ACTIONS,
        ORDER_GUIDANCE_STEPS,
        ORDER_PANEL_ACTIONS,
        ORDER_PANEL_SECTIONS,
    )

    assert ORDER_PANEL_ACTIONS == {
        "refreshOrderDataButton": "Stammdaten laden",
        "suggestOrderNumberButton": "Auftragsnummer vorschlagen",
        "suggestDeliveryNoteNumberButton": "Lieferscheinnummer vorschlagen",
        "suggestInvoiceNumberButton": "Rechnungsnummer vorschlagen",
        "addOrderLineButton": "Position hinzufuegen",
        "removeOrderLineButton": "Position entfernen",
        "saveOrderButton": "Auftrag speichern",
        "createOrderDocumentsButton": "Lieferschein und Rechnung erzeugen",
        "refreshOrdersButton": "Auftragsliste laden",
    }
    assert ORDER_PANEL_SECTIONS == (
        "1. Kunde und Lieferung",
        "2. Produkte im Auftrag",
        "3. Speichern und Belege",
        "Offene Auftraege",
    )
    assert ORDER_GUIDANCE_STEPS == (
        "Kunden suchen und Lieferdatum pruefen.",
        "Produkte hinzufuegen und Positionen kontrollieren.",
        "Auftrag speichern, danach Lieferschein oder Rechnung vorbereiten.",
    )
    assert ORDER_CONTEXT_ACTIONS == {
        "open": "Auftrag oeffnen",
        "create_documents": "Belege erzeugen",
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
        "newCustomerButton": "Neu",
        "saveCustomerButton": "Kunde speichern",
        "discardCustomerChangesButton": "Aenderungen verwerfen",
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
        "newProductButton": "Neu",
        "saveProductButton": "Produkt speichern",
        "discardProductChangesButton": "Aenderungen verwerfen",
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
        "refreshUnitsButton": "Einheiten laden",
        "addUnitButton": "Einheit hinzufuegen",
    }
    assert SETTINGS_PANEL_SECTIONS == ("Produkteinheiten bearbeiten",)


def test_dashboard_tab_exposes_daily_guidance():
    from getraenkeladen_tool.ui.dashboard_panel import DASHBOARD_ACTIONS, DASHBOARD_CARDS, DASHBOARD_GUIDANCE_STEPS

    assert DASHBOARD_ACTIONS == {"refreshDashboardButton": "Heute aktualisieren"}
    assert DASHBOARD_CARDS == ("Lieferungen heute", "Offene Posten", "Kontaktanfragen heute")
    assert DASHBOARD_GUIDANCE_STEPS == (
        "Erst Start pruefen: Was ist heute offen?",
        "Dann Auftraege erfassen oder Listen bearbeiten.",
        "Bei Unsicherheit den passenden Reiter ueber die Karten oeffnen.",
    )


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
