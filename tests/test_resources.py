from pathlib import Path

from getraenkeladen_tool.resources import resource_path


def test_resource_path_resolves_project_template_in_development():
    path = resource_path("templates", "vorlage_liefern_bar.xlsx")

    assert path == Path("templates/vorlage_liefern_bar.xlsx").resolve()
    assert path.exists()
