from PySide6.QtCore import Qt

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

    assert select.help_label.text() == "Aus Liste waehlen oder Namen tippen."

    select.set_search_text("xyz")

    assert select.result_list.count() == 1
    assert select.result_list.item(0).text() == "Kein Treffer gefunden"
    assert select.result_list.item(0).flags().value & 1 == 0


def test_searchable_select_shows_initial_options_before_typing():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Kunde suchen")
    select.set_items([("Cafe Nord", 1, "Muenchen"), ("Hotel Sued", 2, "Rosenheim")])

    assert select.current_value() is None
    assert select.result_list.count() == 2
    assert select.result_list.maximumHeight() == 190
    assert select.visible_labels() == ["Cafe Nord", "Hotel Sued"]
    assert select.help_label.text() == "Aus Liste waehlen oder Namen tippen."


def test_searchable_select_does_not_auto_select_single_initial_option():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Produkt suchen")
    select.set_items([("Adelholzener Classic 12x0,5 PET", 1, "7,90 EUR")])

    assert select.current_value() is None
    assert select.visible_labels() == ["Adelholzener Classic 12x0,5 PET"]


def test_searchable_select_collapses_results_after_selection_and_reopens_while_typing():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Kunde suchen")
    select.set_items([("Cafe Nord", 1, "Muenchen"), ("Hotel Sued", 2, "Rosenheim")])

    select.select_value(1)

    assert select.search_input.text() == "Cafe Nord"
    assert select.help_label.text() == "Ausgewaehlt. Zum Aendern einfach neuen Namen tippen."
    assert select.result_list.maximumHeight() == 0

    select.set_search_text("Hotel")

    assert select.help_label.text() == "Eindeutiger Treffer. Sie koennen direkt weiterarbeiten."
    assert select.result_list.maximumHeight() == 190
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
    assert select.help_label.text() == "Ausgewaehlt. Zum Aendern einfach neuen Namen tippen."


def test_searchable_select_explains_single_match_is_ready_to_use():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Produkt suchen")
    select.set_items([("Adelholzener Classic 12x0,5 PET", 1, "7,90 EUR")])

    select.set_search_text("Classic")

    assert select.current_value() == 1
    assert select.help_label.text() == "Eindeutiger Treffer. Sie koennen direkt weiterarbeiten."


def test_searchable_select_can_show_grouped_recommendations_before_all_items():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Produkt suchen")
    select.set_items(
        [
            ("Wasser 12x0,7", 1, "letzte Menge 4", "Empfohlen fuer diesen Kunden"),
            ("Spezi 20x0,5", 2, "14,90 EUR", "Alle Artikel"),
        ]
    )

    assert select.visible_labels() == [
        "Empfohlen fuer diesen Kunden",
        "Wasser 12x0,7",
        "Alle Artikel",
        "Spezi 20x0,5",
    ]

    select.set_search_text("Spezi")

    assert select.visible_labels() == ["Alle Artikel", "Spezi 20x0,5"]


def test_searchable_select_group_headers_are_visual_separators_not_choices():
    _app()
    from getraenkeladen_tool.ui.searchable_select import SearchableSelect

    select = SearchableSelect("Produkt suchen")
    select.set_items(
        [
            ("Wasser 12x0,7", 1, "letzte Menge 4", "Empfohlen fuer diesen Kunden"),
            ("Spezi 20x0,5", 2, "14,90 EUR", "Alle Artikel"),
        ]
    )

    header = select.result_list.item(0)
    assert header.text() == "Empfohlen fuer diesen Kunden"
    assert header.data(Qt.ItemDataRole.UserRole) is None
    assert not (header.flags() & Qt.ItemFlag.ItemIsSelectable)
    assert not (header.flags() & Qt.ItemFlag.ItemIsEnabled)
    assert header.font().bold()
    assert header.font().pointSize() <= 11

    select._select_item(header)

    assert select.current_value() is None
    assert select.search_input.text() == ""
    assert select.result_list.maximumHeight() == select.DEFAULT_LIST_HEIGHT
