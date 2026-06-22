from getraenkeladen_tool.app import configure_qt_plugin_path, create_app, create_runtime


class FakeApplication:
    _instance = None

    def __init__(self, _args):
        self._application_name = ""
        FakeApplication._instance = self

    @classmethod
    def instance(cls):
        return cls._instance

    def setApplicationName(self, name):
        self._application_name = name

    def setStyleSheet(self, _stylesheet):
        pass

    def applicationName(self):
        return self._application_name


def test_create_app_returns_qapplication(monkeypatch):
    monkeypatch.setattr("getraenkeladen_tool.app.QApplication", FakeApplication)

    app = create_app()

    assert app.applicationName() == "Getraenkeladen Tool"


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
