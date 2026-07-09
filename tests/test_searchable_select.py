from getraenkeladen_tool.ui.searchable_select import SearchableSelectItem, filter_searchable_items


def _app():
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def test_searchable_select_filters_items_while_typing():
    items = [
        SearchableSelectItem("Adelholzener Wasser 12x0,7", 1, "Kiste"),
        SearchableSelectItem("Paulaner Spezi 20x0,5", 2, "Kiste"),
        SearchableSelectItem("Augustiner Helles 20x0,5", 3, "Kiste"),
    ]

    matches = filter_searchable_items(items, "spezi")

    assert [item.label for item in matches] == ["Paulaner Spezi 20x0,5"]


def test_searchable_select_filters_against_detail_text():
    items = [
        SearchableSelectItem("Adelholzener Wasser 12x0,7", 1, "Artikel W-070"),
        SearchableSelectItem("Paulaner Spezi 20x0,5", 2, "Artikel S-050"),
    ]

    matches = filter_searchable_items(items, "w-070")

    assert [item.value for item in matches] == [1]


def test_searchable_select_returns_all_items_without_search_text():
    items = [
        SearchableSelectItem("Cafe Nord", 10, "Muenchen"),
        SearchableSelectItem("Hotel Sued", 11, "Rosenheim"),
    ]

    matches = filter_searchable_items(items, "")

    assert [item.label for item in matches] == ["Cafe Nord", "Hotel Sued"]


def test_order_searchable_select_is_exposed_as_widget_contract():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "SearchableSelect(\"Kunde suchen" in source
    assert "SearchableSelect(\"Produkt suchen" in source
    assert "selection_changed.connect(self.apply_selected_customer)" in source
    assert "selection_changed.connect(self.apply_selected_product)" in source


def test_searchable_select_guides_uncertain_users_to_click_a_result():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Kunde suchen")
    select.set_items([("Cafe Nord", 1, "Muenchen"), ("Hotel Sued", 2, "Rosenheim")])

    assert select.help_label.text() == "Kundenliste scrollen oder oben Namen tippen."

    select.set_search_text("xyz")

    assert select.result_list.count() == 1
    assert select.result_list.item(0).text() == "Kein Treffer gefunden"
    assert select.result_list.item(0).flags().value & 1 == 0


def test_searchable_select_shows_scrollable_list_without_search_text():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Kunde suchen")
    select.set_items([("Cafe Nord", 1, "Muenchen"), ("Hotel Sued", 2, "Rosenheim")])

    assert select.current_value() is None
    assert select.visible_labels() == ["Cafe Nord", "Hotel Sued"]
    assert select.result_list.maximumHeight() == 130
    assert select.help_label.text() == "Kundenliste scrollen oder oben Namen tippen."


def test_searchable_select_can_use_article_list_language():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Artikel suchen", list_label="Artikelliste")
    select.set_items([("Paulaner Spezi 20x0,5", 1, "12,50 EUR")])

    assert select.help_label.text() == "Artikelliste scrollen oder oben Namen tippen."


def test_searchable_select_collapses_results_after_selection_and_only_expands_for_multiple_matches():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Kunde suchen")
    select.set_items([("Cafe Nord", 1, "Muenchen"), ("Hotel Sued", 2, "Rosenheim")])

    select.select_value(1)

    assert select.search_input.text() == "Cafe Nord"
    assert select.help_label.text() == "Ausgewaehlt: Cafe Nord"
    assert select.result_list.maximumHeight() == 0

    select.set_search_text("Hotel")

    assert select.help_label.text() == "Treffer in der Liste anklicken."
    assert select.result_list.maximumHeight() == 130
    assert select.visible_labels() == ["Hotel Sued"]


def test_searchable_select_enter_accepts_first_visible_result():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Kunde suchen")
    select.set_items([("Cafe Nord", 1, "Muenchen"), ("Cafe Sued", 2, "Rosenheim")])
    select.set_search_text("Cafe")

    select.select_first_visible_item()

    assert select.current_value() == 1
    assert select.search_input.text() == "Cafe Nord"
    assert select.result_list.maximumHeight() == 0
    assert select.help_label.text() == "Ausgewaehlt: Cafe Nord"


def test_searchable_select_explains_single_match_is_ready_to_use():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Produkt suchen")
    select.set_items([("Adelholzener Classic 12x0,5 PET", 1, "7,90 EUR")])

    select.set_search_text("Classic")

    assert select.current_value() is None
    assert select.help_label.text() == "Treffer in der Liste anklicken."
    assert select.result_list.maximumHeight() == 130


def test_searchable_select_clearing_text_after_selection_shows_full_list_again():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Kunde suchen")
    select.set_items([("Cafe Nord", 1, "Muenchen"), ("Hotel Sued", 2, "Rosenheim")])
    select.select_value(1)

    select.set_search_text("")

    assert select.current_value() is None
    assert select.visible_labels() == ["Cafe Nord", "Hotel Sued"]
    assert select.result_list.maximumHeight() == 130
    assert select.help_label.text() == "Kundenliste scrollen oder oben Namen tippen."


def test_searchable_select_keeps_list_visible_for_multiple_matches():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Kunde suchen")
    select.set_items([("Cafe Nord", 1, "Muenchen"), ("Cafe Sued", 2, "Rosenheim")])

    select.set_search_text("Cafe")

    assert select.current_value() is None
    assert select.result_list.maximumHeight() == 130
    assert select.visible_labels() == ["Cafe Nord", "Cafe Sued"]
