from getraenkeladen_tool.schemas import ProductCreate
from getraenkeladen_tool.services.product_service import (
    create_product,
    deactivate_product,
    list_active_products,
    list_products,
    restore_product,
    update_product,
)


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


def test_update_product_changes_existing_master_data(session):
    product = create_product(
        session,
        ProductCreate(name="Cola", unit="Kiste", standard_price_cents=1899),
    )

    updated = update_product(
        session,
        product.id,
        ProductCreate(
            name="Cola Zero",
            unit="Kiste",
            standard_price_cents=1999,
            article_number="C-200",
            is_active=True,
        ),
    )

    assert updated.id == product.id
    assert updated.name == "Cola Zero"
    assert updated.standard_price_cents == 1999
    assert updated.article_number == "C-200"


def test_list_products_includes_inactive_and_restore_product_reactivates(session):
    product = create_product(
        session,
        ProductCreate(name="Altes Produkt", unit="Kiste", standard_price_cents=999),
    )
    deactivate_product(session, product.id)

    assert list_products(session)[0].is_active is False

    restored = restore_product(session, product.id)

    assert restored.is_active is True
    assert list_active_products(session) == [restored]
