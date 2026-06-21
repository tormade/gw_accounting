from dataclasses import dataclass
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .config import AppConfig
from .db import bootstrap_database, create_session_factory
from .ui.main_window import MainWindow
from .ui.theme import APP_STYLESHEET


@dataclass(slots=True)
class AppRuntime:
    config: AppConfig
    session_factory: object


def create_runtime(base_dir: Path | None = None) -> AppRuntime:
    config = AppConfig(base_dir=base_dir or Path.home() / ".getraenkeladen_tool")
    bootstrap_database(config)
    return AppRuntime(config=config, session_factory=create_session_factory(config))


def create_app() -> QApplication:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Getraenkeladen Tool")
    app.setStyleSheet(APP_STYLESHEET)
    return app


def create_main_window() -> MainWindow:
    create_app()
    runtime = create_runtime()
    return MainWindow(session_factory=runtime.session_factory)


def main() -> int:
    app = create_app()
    runtime = create_runtime()
    window = MainWindow(session_factory=runtime.session_factory)
    window.show()
    return app.exec()
