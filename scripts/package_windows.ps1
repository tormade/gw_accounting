Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

pyinstaller `
  --name GetraenkeladenTool `
  --windowed `
  --icon assets/app-icon.ico `
  --add-data "templates;templates" `
  --add-data "assets/brand;assets/brand" `
  --collect-all PySide6 `
  src/getraenkeladen_tool/__main__.py
