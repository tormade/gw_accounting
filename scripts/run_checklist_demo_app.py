from __future__ import annotations

from pathlib import Path
import tempfile

from getraenkeladen_tool.app import create_app, create_runtime
from getraenkeladen_tool.ui.main_window import MainWindow


def main() -> int:
    app = create_app()
    base_dir = Path(tempfile.mkdtemp(prefix="getraenkeladen_pruefliste_ui_"))
    runtime = create_runtime(base_dir=base_dir)
    window = MainWindow(session_factory=runtime.session_factory)
    window.setWindowTitle(f"Getraenkeladen Tool - Prueflisten-Demo ({base_dir.name})")
    window.show()
    window.raise_()
    window.activateWindow()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
