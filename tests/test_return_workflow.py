from pathlib import Path

from getraenkeladen_tool.schemas import CustomerCreate, DepositReturnCreate, OrderCreate, OrderLineCreate, ProductCreate
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.order_service import create_order, create_order_delivery_order, create_order_invoice, update_order
from getraenkeladen_tool.services.product_service import create_product
from getraenkeladen_tool.services.report_service import list_open_delivery_returns, list_open_items


def test_full_return_flow_adjusts_order_then_creates_invoice_and_open_item(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(name="Metzgerei Karl", folder_path=str(tmp_path / "Kunden" / "Metzgerei Karl")),
    )
    water = create_product(session, ProductCreate(name="Wasser 12x0,7", unit="Kiste", standard_price_cents=1299))
    spezi = create_product(session, ProductCreate(name="Spezi 20x0,5", unit="Kiste", standard_price_cents=1490))
    order = create_order(
        session,
        OrderCreate(
            order_number="B-UAT-1",
            customer_id=customer.id,
            order_date="2026-07-06",
            delivery_date="2026-07-06",
            delivery_slot="vormittag",
            lines=[
                OrderLineCreate(product_id=water.id, quantity=4, deposit_cents=330),
                OrderLineCreate(product_id=spezi.id, quantity=0, deposit_cents=310),
            ],
        ),
    )

    create_order_delivery_order(session, order.id, "LS-UAT-1", assets={"excel"})
    assert [item.order_number for item in list_open_delivery_returns(session)] == ["B-UAT-1"]

    update_order(
        session,
        order.id,
        OrderCreate(
            order_number="B-UAT-1",
            customer_id=customer.id,
            order_date="2026-07-06",
            delivery_date="2026-07-06",
            delivery_slot="vormittag",
            status="lieferauftrag_erstellt",
            lines=[
                OrderLineCreate(product_id=water.id, quantity=3, deposit_cents=330),
                OrderLineCreate(product_id=spezi.id, quantity=0, deposit_cents=310),
            ],
            deposit_returns=[DepositReturnCreate(name="Kasten 3,10 EUR", quantity=2, deposit_cents=310)],
        ),
    )
    invoice = create_order_invoice(session, order.id, "RG-UAT-1", assets={"excel"})

    assert invoice.document_number == "RG-UAT-1"
    assert list_open_delivery_returns(session) == []
    open_items = list_open_items(session)
    assert [(item.customer_name, item.document_number, item.status) for item in open_items] == [
        ("Metzgerei Karl", "RG-UAT-1", "offen")
    ]
    assert Path(invoice.excel_path).exists()
