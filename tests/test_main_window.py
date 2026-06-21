from getraenkeladen_tool.ui.main_window import CLAIM_PATH, LOGO_PATH, MAIN_TABS
from getraenkeladen_tool.ui.theme import APP_STYLESHEET


def test_main_window_exposes_first_version_tabs():
    assert MAIN_TABS == ("Kunden", "Produkte", "Belege", "Listen")


def test_theme_uses_winklmeier_work_tool_direction():
    assert "#111111" in APP_STYLESHEET
    assert "#f5f5f2" in APP_STYLESHEET
    assert "#b91c1c" in APP_STYLESHEET


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


def test_customer_tab_exposes_master_data_actions():
    from getraenkeladen_tool.ui.customer_panel import CUSTOMER_PANEL_ACTIONS

    assert CUSTOMER_PANEL_ACTIONS == {
        "saveCustomerButton": "Kunde speichern",
        "chooseCustomerFolderButton": "Ordner waehlen",
    }


def test_product_tab_exposes_price_list_actions():
    from getraenkeladen_tool.ui.product_panel import PRODUCT_PANEL_ACTIONS

    assert PRODUCT_PANEL_ACTIONS == {
        "saveProductButton": "Produkt speichern",
        "deactivateProductButton": "Produkt deaktivieren",
    }


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
