from getraenkeladen_tool.ui.searchable_select import SearchableSelectItem, filter_searchable_items


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
