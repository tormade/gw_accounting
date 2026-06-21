from getraenkeladen_tool.services.settings_service import DEFAULT_PRODUCT_UNITS, add_product_unit, list_product_units


def test_product_units_are_seeded_with_beverage_defaults(session):
    assert list_product_units(session) == list(DEFAULT_PRODUCT_UNITS)


def test_add_product_unit_extends_unit_dropdown_values(session):
    unit = add_product_unit(session, "Tray")

    assert unit.value == "Tray"
    assert "Tray" in list_product_units(session)


def test_add_product_unit_ignores_existing_value(session):
    add_product_unit(session, "Kiste")

    assert list_product_units(session).count("Kiste") == 1
