from getraenkeladen_tool.schemas import ProductCreate
from getraenkeladen_tool.services.product_service import create_product, deactivate_product, list_active_products


def test_create_product_uses_cent_prices(session):
    product = create_product(
        session,
        ProductCreate(name="Cola", unit="Kiste", standard_price_cents=1899),
    )

    assert product.standard_price_cents == 1899


def test_list_active_products_excludes_deactivated_products(session):
    active = create_product(
        session,
        ProductCreate(name="Apfelschorle", unit="Kiste", standard_price_cents=1499),
    )
    inactive = create_product(
        session,
        ProductCreate(name="Altes Produkt", unit="Kiste", standard_price_cents=999),
    )

    deactivate_product(session, inactive.id)

    products = list_active_products(session)
    assert products == [active]
