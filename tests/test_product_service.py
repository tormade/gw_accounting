from getraenkeladen_tool.schemas import ProductCreate
from getraenkeladen_tool.services.product_service import create_product


def test_create_product_uses_cent_prices(session):
    product = create_product(
        session,
        ProductCreate(name="Cola", unit="Kiste", standard_price_cents=1899),
    )

    assert product.standard_price_cents == 1899
