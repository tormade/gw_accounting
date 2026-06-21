from pathlib import Path

from getraenkeladen_tool.services.customer_service import list_customers
from getraenkeladen_tool.services.order_service import list_active_orders
from getraenkeladen_tool.services.product_service import list_active_products, list_products
from getraenkeladen_tool.services.report_service import list_daily_deliveries, list_open_items
from getraenkeladen_tool.services.sample_data_service import seed_demo_workflow


def test_seed_demo_workflow_creates_reusable_customer_product_document_data(session, tmp_path: Path):
    result = seed_demo_workflow(session, base_output_dir=tmp_path, target_date="2026-06-21")

    customers = list_customers(session)
    products = list_active_products(session)
    deliveries = list_daily_deliveries(session, "2026-06-21")
    open_items = list_open_items(session)
    orders = list_active_orders(session)

    assert result.created_customers == 4
    assert result.created_products == 4
    assert result.created_orders == 2
    assert result.created_documents == 4
    assert [customer.name for customer in customers] == [
        "Archivkunde Beispiel",
        "Cafe Nord",
        "Gasthof Sued",
        "Hotel Blau",
    ]
    assert [product.name for product in products] == ["Apfelschorle 12x1,0", "Helles 20x0,5", "Wasser 12x0,7"]
    assert [delivery.document_number for delivery in deliveries] == ["LS-3001", "LS-3002"]
    assert [item.document_number for item in open_items] == ["RG-3001", "RG-3002"]
    assert [order.order_number for order in orders] == ["AUF-1001", "AUF-1002"]


def test_seed_demo_workflow_is_idempotent(session, tmp_path: Path):
    seed_demo_workflow(session, base_output_dir=tmp_path, target_date="2026-06-21")
    result = seed_demo_workflow(session, base_output_dir=tmp_path, target_date="2026-06-21")

    assert result.created_customers == 0
    assert result.created_products == 0
    assert result.created_orders == 0
    assert result.created_documents == 0
    assert len(list_customers(session)) == 4
    assert len(list_active_products(session)) == 3
    assert len(list_open_items(session)) == 2


def test_seed_demo_workflow_creates_archived_examples_for_restore_flow(session, tmp_path: Path):
    seed_demo_workflow(session, base_output_dir=tmp_path, target_date="2026-06-21")

    customers = list_customers(session)
    products = list_products(session)

    assert "Archivkunde Beispiel" in [customer.name for customer in customers]
    assert "Archivprodukt Beispiel" in [product.name for product in products]
    assert [customer.is_active for customer in customers if customer.name == "Archivkunde Beispiel"] == [False]
    assert [product.is_active for product in products if product.name == "Archivprodukt Beispiel"] == [False]
