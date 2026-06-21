from getraenkeladen_tool.schemas import CustomerCreate
from getraenkeladen_tool.services.customer_service import create_customer, list_customers


def test_create_customer_requires_name_and_folder(session):
    customer = create_customer(
        session,
        CustomerCreate(name="Hotel Blau", folder_path="Kunden/Hotel Blau"),
    )

    assert customer.name == "Hotel Blau"


def test_list_customers_returns_customers_sorted_by_name(session):
    create_customer(session, CustomerCreate(name="Zoo Bar", folder_path="Kunden/Zoo Bar"))
    create_customer(session, CustomerCreate(name="Cafe Nord", folder_path="Kunden/Cafe Nord"))

    customers = list_customers(session)

    assert [customer.name for customer in customers] == ["Cafe Nord", "Zoo Bar"]
