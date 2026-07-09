from getraenkeladen_tool.app import configure_qt_plugin_path, create_app, create_runtime, main
from getraenkeladen_tool.errors import ApplicationStartupError


class FakeApplication:
    _instance = None

    def __init__(self, _args):
        self._application_name = ""
        self._style = ""
        self._palette = None
        self._stylesheet = ""
        FakeApplication._instance = self

    @classmethod
    def instance(cls):
        return cls._instance

    def setApplicationName(self, name):
        self._application_name = name

    def setStyleSheet(self, _stylesheet):
        self._stylesheet = _stylesheet

    def setStyle(self, style):
        self._style = style

    def setPalette(self, palette):
        self._palette = palette

    def applicationName(self):
        return self._application_name


def test_create_app_returns_qapplication(monkeypatch):
    monkeypatch.setattr("getraenkeladen_tool.app.QApplication", FakeApplication)

    app = create_app()

    assert app.applicationName() == "Getraenkeladen Tool"
    assert app._style == "Fusion"
    assert app._palette is not None
    assert app._stylesheet


def test_configure_qt_plugin_path_sets_existing_pyside_plugin_root(monkeypatch):
    monkeypatch.delenv("QT_QPA_PLATFORM_PLUGIN_PATH", raising=False)
    monkeypatch.delenv("QT_PLUGIN_PATH", raising=False)

    plugin_path = configure_qt_plugin_path()

    assert plugin_path is not None
    assert plugin_path.exists()
    assert plugin_path.name == "plugins"
    assert (plugin_path / "platforms" / "libqcocoa.dylib").exists()


def test_create_runtime_bootstraps_local_database(tmp_path):
    runtime = create_runtime(base_dir=tmp_path)

    assert runtime.config.database_path.exists()
    assert runtime.session_factory is not None


def test_main_shows_a_clear_dialog_for_startup_storage_errors(monkeypatch):
    messages = []
    monkeypatch.setattr("getraenkeladen_tool.app.create_app", lambda: object())
    monkeypatch.setattr(
        "getraenkeladen_tool.app.create_runtime",
        lambda: (_ for _ in ()).throw(ApplicationStartupError("Datenordner nicht verfuegbar")),
    )
    monkeypatch.setattr("getraenkeladen_tool.app.QMessageBox.critical", lambda *_args: messages.append(_args))

    assert main() == 1
    assert "Datenordner nicht verfuegbar" in messages[0][-1]
