from dataclasses import dataclass
import os
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtCore import QLibraryInfo
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


def configure_qt_plugin_path() -> Path | None:
    configured_path = os.environ.get("QT_QPA_PLATFORM_PLUGIN_PATH")
    if configured_path and Path(configured_path).exists():
        return Path(configured_path)

    plugin_path = Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)) / "platforms"
    if (plugin_path / "libqcocoa.dylib").exists():
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugin_path)
        return plugin_path
    return None


def create_app() -> QApplication:
    configure_qt_plugin_path()
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
    QTimer.singleShot(0, window.raise_)
    QTimer.singleShot(0, window.activateWindow)
    return app.exec()
