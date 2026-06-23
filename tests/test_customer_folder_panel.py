from pathlib import Path


def test_customer_folder_panel_exposes_real_folder_workflow():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "class CustomerFolderPanel" in source
    assert 'PageHeader("Kundenordner"' in source
    assert 'SearchableSelect("Kunde suchen' in source
    assert "Kundenakte" in source
    assert "Kundenordner oeffnen" in source
    assert "Dateien im Kundenordner" in source
    assert "Letzte bekannte Bestellung" in source
    assert "Neue Bestellung aus letzter Datei" in source
    assert "Lieferschein erstellen" in source
    assert "Rechnung erstellen" in source
    assert "get_customer_folder_snapshot" in source
