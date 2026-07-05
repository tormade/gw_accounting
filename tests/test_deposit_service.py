from getraenkeladen_tool.schemas import DepositReturnCreate, OrderCreate, OrderLineCreate
from getraenkeladen_tool.services.deposit_service import (
    DEPOSIT_RETURN_PRESETS,
    build_deposit_return_line,
    validate_deposit_returns,
)


def test_build_deposit_return_line_uses_fixed_winklmeier_presets():
    line = build_deposit_return_line(310, 4)

    assert line == DepositReturnCreate(name="Pfand 3,10 EUR", quantity=4, deposit_cents=310)
    assert [preset.deposit_cents for preset in DEPOSIT_RETURN_PRESETS] == [150, 310, 450]


def test_validate_deposit_returns_warns_for_unknown_stage_and_high_return():
    order = OrderCreate(
        order_number="AUF-PFAND",
        customer_id=1,
        order_date="2026-07-05",
        delivery_date="2026-07-05",
        lines=[OrderLineCreate(product_id=1, quantity=2, unit_price_cents=1000, deposit_cents=310)],
        deposit_returns=[
            DepositReturnCreate(name="Pfand unbekannt", quantity=1, deposit_cents=999),
            DepositReturnCreate(name="Pfand 3,10 EUR", quantity=12, deposit_cents=310),
        ],
    )

    warnings = validate_deposit_returns(order)

    assert [warning.code for warning in warnings] == ["unknown_deposit_stage", "high_deposit_return"]
    assert "999" in warnings[0].message
    assert "12" in warnings[1].message
