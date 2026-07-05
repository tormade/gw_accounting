from ..services.deposit_service import DEPOSIT_RETURN_PRESETS as SERVICE_DEPOSIT_RETURN_PRESETS


DEPOSIT_RETURN_PRESETS = tuple((preset.label, preset.deposit_cents) for preset in SERVICE_DEPOSIT_RETURN_PRESETS)
