from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    bezeichnung: str
    menge: int
    preis_cents: int
    pfand_cents: int = 0


@dataclass(frozen=True)
class PfandRueckgabe:
    bezeichnung: str
    menge: int
    pfand_cents: int


@dataclass(frozen=True)
class BelegParameter:
    lieferpauschale_aktiv: bool = False
    lieferpauschale_cents: int = 390
    mwst_satz: float = 0.19


@dataclass(frozen=True)
class BelegSummen:
    mengen_summe: int
    positionssummen_cents: list[int]
    ruecknahme_summen_cents: list[int]
    lieferwert_cents: int
    lieferpauschale_cents: int
    pfand_rueckgabe_cents: int
    brutto_cents: int
    netto_cents: int
    mwst_cents: int


def berechne_beleg(
    positionen: list[Position],
    ruecknahmen: list[PfandRueckgabe],
    parameter: BelegParameter,
) -> BelegSummen:
    positionssummen = [
        (position.preis_cents + position.pfand_cents) * position.menge
        for position in positionen
    ]
    ruecknahme_summen = [
        -ruecknahme.pfand_cents * ruecknahme.menge
        for ruecknahme in ruecknahmen
    ]
    lieferwert_cents = sum(positionssummen)
    lieferpauschale_cents = parameter.lieferpauschale_cents if parameter.lieferpauschale_aktiv else 0
    pfand_rueckgabe_cents = sum(ruecknahme_summen)
    brutto_cents = lieferwert_cents + lieferpauschale_cents + pfand_rueckgabe_cents
    netto_cents = round(brutto_cents / (1 + parameter.mwst_satz))
    mwst_cents = brutto_cents - netto_cents
    return BelegSummen(
        mengen_summe=sum(position.menge for position in positionen),
        positionssummen_cents=positionssummen,
        ruecknahme_summen_cents=ruecknahme_summen,
        lieferwert_cents=lieferwert_cents,
        lieferpauschale_cents=lieferpauschale_cents,
        pfand_rueckgabe_cents=pfand_rueckgabe_cents,
        brutto_cents=brutto_cents,
        netto_cents=netto_cents,
        mwst_cents=mwst_cents,
    )
