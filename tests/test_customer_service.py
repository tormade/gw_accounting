from getraenkeladen_tool.schemas import CustomerCreate
from getraenkeladen_tool.services.customer_service import create_customer


def test_create_customer_requires_name_and_folder(session):
    customer = create_customer(
        session,
        CustomerCreate(name="Hotel Blau", folder_path="Kunden/Hotel Blau"),
    )

    assert customer.name == "Hotel Blau"
