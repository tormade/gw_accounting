from getraenkeladen_tool.models import Customer, Product


def test_customer_and_product_models_expose_required_fields():
    customer = Customer(name="Cafe Nord", folder_path="Kunden/Cafe Nord")
    product = Product(name="Wasser 0,7", unit="Kiste", standard_price_cents=1299)
    assert customer.name == "Cafe Nord"
    assert product.standard_price_cents == 1299
