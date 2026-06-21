# Getraenkeladen Tool

Local Windows desktop app for a beverage store, built with Python 3.12 and PySide6.

## Development

Install the app with development dependencies:

```bash
python -m pip install -e ".[dev]"
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
