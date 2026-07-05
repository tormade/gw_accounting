from datetime import date, datetime

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit


DISPLAY_DATE_FORMAT = "dd.MM.yyyy"


def parse_display_date(value: str) -> str | None:
    text = value.strip()
    if not text:
        return None
    for pattern in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue
    return None


def to_display_date(value: str | None) -> str:
    if not value:
        return ""
    parsed = parse_display_date(value)
    if parsed is None:
        return value
    return datetime.strptime(parsed, "%Y-%m-%d").strftime("%d.%m.%Y")


def to_iso_date(value: str | None) -> str | None:
    if value is None:
        return None
    return parse_display_date(value)


class DateInput(QDateEdit):
    def __init__(self, iso_date: str | None = None) -> None:
        super().__init__()
        self.setCalendarPopup(True)
        self.setDisplayFormat(DISPLAY_DATE_FORMAT)
        self.setSpecialValueText("kein Termin")
        self.setMinimumDate(QDate(1900, 1, 1))
        self.setMaximumDate(QDate(2999, 12, 31))
        self.set_iso_date(iso_date)

    def iso_date(self) -> str:
        if self.date() == self.minimumDate():
            return ""
        return self.date().toString("yyyy-MM-dd")

    def set_iso_date(self, value: str | None) -> None:
        if value:
            self.setDate(_qdate_from_iso(value))
        else:
            self.setDate(self.minimumDate())


def _qdate_from_iso(value: str) -> QDate:
    parsed = parse_display_date(value) or date.today().isoformat()
    year, month, day = (int(part) for part in parsed.split("-"))
    return QDate(year, month, day)
