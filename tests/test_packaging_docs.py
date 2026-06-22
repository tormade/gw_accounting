from pathlib import Path
import json
import tomllib


def test_readme_mentions_windows_packaging():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "pyinstaller" in readme.lower()
    assert "windows" in readme.lower()
    assert "scripts/package_windows.ps1" in readme


def test_windows_packaging_script_includes_required_assets():
    script = Path("scripts/package_windows.ps1").read_text(encoding="utf-8")

    assert "--name GetraenkeladenTool" in script
    assert "--windowed" in script
    assert "templates" in script
    assert "assets/brand" in script
    assert Path("assets/app-icon.ico").exists()


def test_pyside_dependency_is_pinned_below_known_bad_cocoa_plugin_version():
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert "PySide6>=6.10,<6.11" in project["project"]["dependencies"]


def test_project_supports_python_311_for_stable_macos_qt_startup():
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    readme = Path("README.md").read_text(encoding="utf-8")

    assert project["project"]["requires-python"] == ">=3.11"
    assert "brew install python@3.11" in readme
    assert "/opt/homebrew/bin/python3.11 -m venv .venv" in readme


def test_package_discovery_uses_src_layout():
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert project["build-system"]["build-backend"] == "setuptools.build_meta"
    assert project["tool"]["setuptools"]["packages"]["find"]["where"] == ["src"]


def test_vscode_launch_uses_project_venv_with_debugpy():
    launch = json.loads(Path(".vscode/launch.json").read_text(encoding="utf-8"))
    config = launch["configurations"][0]

    assert config["type"] == "debugpy"
    assert config["python"] == "${workspaceFolder}/.venv/bin/python"
    assert config["module"] == "getraenkeladen_tool"
    assert "QT_QPA_PLATFORM_PLUGIN_PATH" not in config.get("env", {})


def test_vscode_task_runs_app_without_debug_adapter():
    tasks = json.loads(Path(".vscode/tasks.json").read_text(encoding="utf-8"))
    task = tasks["tasks"][0]

    assert task["label"] == "Getraenkeladen Tool starten"
    assert task["command"] == (
        "PYTHONPATH=src "
        ".venv/bin/python -m getraenkeladen_tool"
    )
    assert task["type"] == "shell"


def test_user_guide_explains_guided_daily_workflow():
    guide = Path("docs/bedienhilfe.md").read_text(encoding="utf-8")

    assert "Startseite" in guide
    assert "Auftrag erfassen" in guide
    assert "Archivieren statt loeschen" in guide
    assert "Windows" in guide


def test_project_docs_include_approved_ux_guidelines_and_roadmap():
    ux = Path("docs/ux-leitlinien.md").read_text(encoding="utf-8")
    roadmap = Path("docs/roadmap.md").read_text(encoding="utf-8")

    assert "Neue Lieferung erfassen" in ux
    assert "Letzte Bestellung uebernehmen" in ux
    assert "PDF + E-Mail" in ux
    assert "vorerst ausgeklammert" in ux
    assert "Meilenstein 2" in roadmap
    assert "ZUGFeRD" in roadmap
    assert "Status" in roadmap
