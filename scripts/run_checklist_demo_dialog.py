from __future__ import annotations

from pathlib import Path
import tempfile

from PySide6.QtWidgets import QDialog, QVBoxLayout

from getraenkeladen_tool.app import create_app, create_runtime
from getraenkeladen_tool.services.master_data_import_service import import_master_data_from_folder
from getraenkeladen_tool.services.onboarding_service import onboard_customer_workbook_folder
from getraenkeladen_tool.ui.checklist_panel import ChecklistPanel


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "Demo_Pruefliste"


def main() -> int:
    app = create_app()
    base_dir = Path(tempfile.mkdtemp(prefix="getraenkeladen_pruefliste_dialog_"))
    runtime = create_runtime(base_dir=base_dir)
    session = runtime.session_factory()
    try:
        import_master_data_from_folder(session, DEMO_DIR / "Input")
        onboard_customer_workbook_folder(session, DEMO_DIR / "Input" / "Lieferkunden Liste.xlsx", DEMO_DIR / "Kundenordner")
    finally:
        session.close()

    dialog = QDialog()
    dialog.setWindowTitle(f"Pruefliste Demo ({base_dir.name})")
    dialog.resize(1180, 820)
    layout = QVBoxLayout(dialog)
    layout.addWidget(ChecklistPanel(session_factory=runtime.session_factory))
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
