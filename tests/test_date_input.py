from getraenkeladen_tool.ui.date_input import DISPLAY_DATE_FORMAT, parse_display_date, to_display_date, to_iso_date


def test_display_date_format_is_german_day_month_year():
    assert DISPLAY_DATE_FORMAT == "dd.MM.yyyy"


def test_parse_display_date_accepts_german_and_iso_values():
    assert parse_display_date("21.06.2026") == "2026-06-21"
    assert parse_display_date("2026-06-21") == "2026-06-21"
    assert parse_display_date("") is None


def test_to_display_date_formats_iso_values_for_users():
    assert to_display_date("2026-06-21") == "21.06.2026"
    assert to_display_date("") == ""


def test_to_iso_date_returns_none_for_missing_values():
    assert to_iso_date("") is None
    assert to_iso_date("21.06.2026") == "2026-06-21"
