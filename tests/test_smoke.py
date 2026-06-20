from getraenkeladen_tool.app import create_app


def test_create_app_returns_qapplication():
    app = create_app()
    assert app.applicationName() == "Getraenkeladen Tool"
