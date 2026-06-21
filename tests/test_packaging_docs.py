from pathlib import Path


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
