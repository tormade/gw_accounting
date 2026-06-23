from getraenkeladen_tool.kern.regeln.beleg import (
    BelegParameter,
    PfandRueckgabe,
    Position,
    berechne_beleg,
)


def test_berechne_beleg_pinnt_metzgerei_karl_golden_values():
    result = berechne_beleg(
        positionen=[
            Position("Adelholzener Classic 12x0,7", 5, 1128, 330),
            Position("Frucade Colamix 20x0,5", 3, 1048, 310),
            Position("Labertaler Apfelschorle 20x0,5", 8, 1198, 310),
        ],
        ruecknahmen=[
            PfandRueckgabe("Leergut 3,10", 8, 310),
            PfandRueckgabe("Leergut 3,30", 7, 330),
        ],
        parameter=BelegParameter(lieferpauschale_aktiv=False),
    )

    assert result.mengen_summe == 16
    assert result.lieferwert_cents == 23428
    assert result.lieferpauschale_cents == 0
    assert result.pfand_rueckgabe_cents == -4790
    assert result.brutto_cents == 18638
    assert result.netto_cents == 15662
    assert result.mwst_cents == 2976
    assert result.positionssummen_cents == [7290, 4074, 12064]
    assert result.ruecknahme_summen_cents == [-2480, -2310]


def test_berechne_beleg_rechnet_lieferpauschale_und_pfandrueckgabe():
    result = berechne_beleg(
        positionen=[
            Position("Wasser", 1, 1030, 480),
            Position("Apfelschorle", 1, 1680, 480),
        ],
        ruecknahmen=[PfandRueckgabe("Leergut Kiste 4,80", 1, 480)],
        parameter=BelegParameter(lieferpauschale_aktiv=True),
    )

    assert result.mengen_summe == 2
    assert result.lieferwert_cents == 3670
    assert result.lieferpauschale_cents == 390
    assert result.pfand_rueckgabe_cents == -480
    assert result.brutto_cents == 3580
    assert result.netto_cents == 3008
    assert result.mwst_cents == 572
