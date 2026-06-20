from PySide6.QtWidgets import QApplication


def create_app() -> QApplication:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Getraenkeladen Tool")
    return app
