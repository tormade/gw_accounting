# Getraenkeladen Tool

Local Windows desktop app for a beverage store, built with Python 3.12 and PySide6.

## Development

Install the app with development dependencies:

```bash
python -m pip install ".[dev]"
```

Start the app from the installed package:

```bash
python -m getraenkeladen_tool
```

If you want VS Code to run the current source files directly while developing,
use the included "Getraenkeladen Tool" launch configuration. From the terminal,
the equivalent command is:

```bash
PYTHONPATH=src python -m getraenkeladen_tool
```

Run tests:

```bash
pytest
```

## Windows Packaging

Use `pyinstaller` on a Windows machine to build the operator executable:

```powershell
pwsh -File scripts/package_windows.ps1
```

The resulting executable should be tested against:

- local SQLite storage creation
- customer-folder document output
- invoice Excel generation from the Winklmeier template
- invoice PDF generation with the configured letterhead
- open-items updates after invoice creation and payment marking

The first production rollout should stay local to one Windows PC. If the data folder is later moved to a NAS or network share, test customer-folder paths and SQLite access carefully before using it in daily work.
