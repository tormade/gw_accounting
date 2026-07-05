from dataclasses import dataclass

from ..schemas import DepositReturnCreate, OrderCreate


@dataclass(frozen=True, slots=True)
class DepositPreset:
    label: str
    deposit_cents: int


@dataclass(frozen=True, slots=True)
class DepositWarning:
    code: str
    message: str


DEPOSIT_RETURN_PRESETS: tuple[DepositPreset, ...] = (
    DepositPreset("Pfand 1,50 EUR", 150),
    DepositPreset("Pfand 3,10 EUR", 310),
    DepositPreset("Pfand 4,50 EUR", 450),
)


def build_deposit_return_line(deposit_cents: int, quantity: int) -> DepositReturnCreate:
    preset = _preset_for_cents(deposit_cents)
    if preset is None:
        raise ValueError("Unbekannte Pfandstufe.")
    return DepositReturnCreate(name=preset.label, quantity=quantity, deposit_cents=preset.deposit_cents)


def validate_deposit_returns(order: OrderCreate) -> list[DepositWarning]:
    warnings: list[DepositWarning] = []
    known_stages = {preset.deposit_cents for preset in DEPOSIT_RETURN_PRESETS}
    delivered_carriers = sum(line.quantity for line in order.lines if line.deposit_cents > 0)
    for deposit_return in order.deposit_returns:
        if deposit_return.deposit_cents not in known_stages:
            warnings.append(
                DepositWarning(
                    "unknown_deposit_stage",
                    f"Unbekannte Pfandstufe: {deposit_return.deposit_cents} Cent.",
                )
            )
        if delivered_carriers and deposit_return.quantity > delivered_carriers * 3:
            warnings.append(
                DepositWarning(
                    "high_deposit_return",
                    f"Sehr hohe Pfandrueckgabe: {deposit_return.quantity} x {deposit_return.deposit_cents / 100:.2f} EUR.",
                )
            )
    return warnings


def _preset_for_cents(deposit_cents: int) -> DepositPreset | None:
    for preset in DEPOSIT_RETURN_PRESETS:
        if preset.deposit_cents == deposit_cents:
            return preset
    return None
