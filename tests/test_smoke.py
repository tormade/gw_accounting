from getraenkeladen_tool.app import create_app


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

    def applicationName(self):
        return self._application_name


def test_create_app_returns_qapplication(monkeypatch):
    monkeypatch.setattr("getraenkeladen_tool.app.QApplication", FakeApplication)

    app = create_app()

    assert app.applicationName() == "Getraenkeladen Tool"
