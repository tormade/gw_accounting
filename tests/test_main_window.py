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
        "createDocumentButton": "Excel erstellen",
    }
