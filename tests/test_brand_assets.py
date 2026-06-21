from pathlib import Path


def test_brand_readme_mentions_original_logo_requirement():
    text = Path("assets/brand/README.md").read_text(encoding="utf-8")

    assert "Originaldatei" in text
    assert "getraenke-winklmeier.de" in text


def test_letterhead_config_uses_winklmeier_identity():
    text = Path("templates/briefkopf.json").read_text(encoding="utf-8")

    assert "Getraenke Winklmeier" in text
    assert "Wir bringen" in text
