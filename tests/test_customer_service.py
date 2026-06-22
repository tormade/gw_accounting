from getraenkeladen_tool.schemas import CustomerCreate
from getraenkeladen_tool.services.customer_service import (
    archive_customer,
    create_customer,
    list_customer_changes,
    list_active_customers,
    list_customers,
    revert_customer_change,
    restore_customer,
    update_customer,
)


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


def test_update_customer_changes_existing_master_data(session):
    customer = create_customer(
        session,
        CustomerCreate(name="Cafe Nord", folder_path="Kunden/Cafe Nord"),
    )

    updated = update_customer(
        session,
        customer.id,
        CustomerCreate(
            name="Cafe Nord GmbH",
            folder_path="Kunden/Cafe Nord GmbH",
            payment_method="SEPA",
        ),
    )

    assert updated.id == customer.id
    assert updated.name == "Cafe Nord GmbH"
    assert updated.folder_path == "Kunden/Cafe Nord GmbH"
    assert updated.payment_method == "SEPA"

    changes = list_customer_changes(session, customer.id)
    assert {change.field_name for change in changes} >= {"name", "folder_path", "payment_method"}


def test_revert_customer_change_restores_previous_field_value(session):
    customer = create_customer(
        session,
        CustomerCreate(name="Cafe Nord", folder_path="Kunden/Cafe Nord", address="Alte Str. 1"),
    )
    update_customer(
        session,
        customer.id,
        CustomerCreate(name="Cafe Nord", folder_path="Kunden/Cafe Nord", address="Neue Str. 7"),
    )
    change = [change for change in list_customer_changes(session, customer.id) if change.field_name == "address"][0]

    reverted = revert_customer_change(session, change.id)

    assert reverted.address == "Alte Str. 1"


def test_archive_customer_hides_from_active_list_and_restore_reactivates(session):
    customer = create_customer(
        session,
        CustomerCreate(name="Cafe Nord", folder_path="Kunden/Cafe Nord"),
    )

    archived = archive_customer(session, customer.id)

    assert archived.is_active is False
    assert list_active_customers(session) == []

    restored = restore_customer(session, customer.id)

    assert restored.is_active is True
    assert list_active_customers(session) == [restored]
