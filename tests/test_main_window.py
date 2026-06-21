from getraenkeladen_tool.ui.main_window import MAIN_TABS
from getraenkeladen_tool.ui.theme import APP_STYLESHEET


def test_main_window_exposes_first_version_tabs():
    assert MAIN_TABS == ("Kunden", "Produkte", "Belege", "Listen")


def test_theme_uses_winklmeier_work_tool_direction():
    assert "#111111" in APP_STYLESHEET
    assert "#f5f5f2" in APP_STYLESHEET
