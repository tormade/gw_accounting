from pathlib import Path

from getraenkeladen_tool.services.customer_service import list_customers
from getraenkeladen_tool.services.product_service import list_active_products
from getraenkeladen_tool.services.report_service import list_daily_deliveries, list_open_items
from getraenkeladen_tool.services.sample_data_service import seed_demo_workflow


def test_seed_demo_workflow_creates_reusable_customer_product_document_data(session, tmp_path: Path):
    result = seed_demo_workflow(session, base_output_dir=tmp_path, target_date="2026-06-21")

    customers = list_customers(session)
    products = list_active_products(session)
    deliveries = list_daily_deliveries(session, "2026-06-21")
    open_items = list_open_items(session)

    assert result.created_customers == 3
    assert result.created_products == 3
    assert result.created_documents == 2
    assert [customer.name for customer in customers] == ["Cafe Nord", "Gasthof Sued", "Hotel Blau"]
    assert [product.name for product in products] == ["Apfelschorle 12x1,0", "Helles 20x0,5", "Wasser 12x0,7"]
    assert [delivery.document_number for delivery in deliveries] == ["LS-DEMO-1"]
    assert [item.document_number for item in open_items] == ["RG-DEMO-1"]


def test_seed_demo_workflow_is_idempotent(session, tmp_path: Path):
    seed_demo_workflow(session, base_output_dir=tmp_path, target_date="2026-06-21")
    result = seed_demo_workflow(session, base_output_dir=tmp_path, target_date="2026-06-21")

    assert result.created_customers == 0
    assert result.created_products == 0
    assert result.created_documents == 0
    assert len(list_customers(session)) == 3
    assert len(list_active_products(session)) == 3
    assert len(list_open_items(session)) == 1
