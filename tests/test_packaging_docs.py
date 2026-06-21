from pathlib import Path
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


def test_package_discovery_uses_src_layout():
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert project["build-system"]["build-backend"] == "setuptools.build_meta"
    assert project["tool"]["setuptools"]["packages"]["find"]["where"] == ["src"]
