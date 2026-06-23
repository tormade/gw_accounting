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

    assert select.help_label.text() == "Namen tippen und unten einen Treffer anklicken."

    select.set_search_text("xyz")

    assert select.result_list.count() == 1
    assert select.result_list.item(0).text() == "Kein Treffer gefunden"
    assert select.result_list.item(0).flags().value & 1 == 0
