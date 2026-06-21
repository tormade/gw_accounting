from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.theme import APP_STYLESHEET


def create_app() -> QApplication:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Getraenkeladen Tool")
    app.setStyleSheet(APP_STYLESHEET)
    return app


def create_main_window() -> MainWindow:
    create_app()
    return MainWindow()


def main() -> int:
    app = create_app()
    window = MainWindow()
    window.show()
    return app.exec()
