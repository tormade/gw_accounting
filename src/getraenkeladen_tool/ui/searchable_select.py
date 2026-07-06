from collections.abc import Iterable
from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QLabel, QLineEdit, QListWidget, QListWidgetItem, QSizePolicy, QVBoxLayout, QWidget


@dataclass(slots=True)
class SearchableSelectItem:
    label: str
    value: object
    detail: str = ""
    group: str = ""


def filter_searchable_items(items: Iterable[SearchableSelectItem], search_text: str) -> list[SearchableSelectItem]:
    normalized = search_text.strip().casefold()
    if not normalized:
        return list(items)
    return [item for item in items if normalized in f"{item.label} {item.detail}".casefold()]


class SearchableSelect(QWidget):
    selection_changed = Signal()
    DEFAULT_LIST_HEIGHT = 190

    def __init__(self, placeholder: str = "Suchen") -> None:
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self._items: list[SearchableSelectItem] = []
        self._current_value = None
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.help_label = QLabel("Aus Liste wählen oder Namen tippen.")
        self.help_label.setObjectName("sectionSubtitle")
        self.result_list = QListWidget()
        self.result_list.setMaximumHeight(0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.search_input)
        layout.addWidget(self.help_label)
        layout.addWidget(self.result_list)

        self.search_input.textChanged.connect(self._filter_items)
        self.search_input.returnPressed.connect(self.select_first_visible_item)
        self.result_list.itemClicked.connect(self._select_item)
        self.result_list.itemDoubleClicked.connect(self._select_item)

    def set_items(self, items: Iterable[tuple]) -> None:
        self._items = [
            SearchableSelectItem(
                item[0],
                item[1],
                item[2] if len(item) >= 3 else "",
                item[3] if len(item) >= 4 else "",
            )
            for item in items
        ]
        self._current_value = None
        self._filter_items(self.search_input.text())

    def current_value(self):
        return self._current_value

    def set_search_text(self, text: str) -> None:
        self.search_input.setText(text)

    def clear_selection(self, help_text: str | None = None) -> None:
        self._current_value = None
        self.search_input.setText("")
        if help_text is not None:
            self.help_label.setText(help_text)

    def visible_labels(self) -> list[str]:
        return [
            self.result_list.item(row).text()
            for row in range(self.result_list.count())
            if not self.result_list.item(row).isHidden()
        ]

    def select_value(self, value: object) -> None:
        for searchable_item in self._items:
            if searchable_item.value == value:
                self._current_value = searchable_item.value
                self.search_input.blockSignals(True)
                self.search_input.setText(searchable_item.label)
                self.search_input.blockSignals(False)
                self.result_list.clear()
                self.result_list.setMaximumHeight(0)
                self.help_label.setText("Ausgewählt. Zum Ändern einfach neuen Namen tippen.")
                self.selection_changed.emit()
                return
        for row in range(self.result_list.count()):
            item = self.result_list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == value:
                self.result_list.setCurrentRow(row)
                self._select_item(item)
                return
        self._current_value = None
        self.selection_changed.emit()

    def select_first_visible_item(self) -> None:
        for row in range(self.result_list.count()):
            item = self.result_list.item(row)
            if item.flags() & Qt.ItemFlag.ItemIsEnabled:
                self._select_item(item)
                return
        self.help_label.setText("Kein Treffer gefunden. Bitte Suchtext prüfen.")

    def _filter_items(self, text: str) -> None:
        self.result_list.clear()
        self.result_list.setMaximumHeight(self.DEFAULT_LIST_HEIGHT)
        self.help_label.setText("Treffer in der Liste anklicken." if text.strip() else "Aus Liste wählen oder Namen tippen.")
        matches = filter_searchable_items(self._items, text)
        current_group = None
        for item in matches:
            if item.group and item.group != current_group:
                current_group = item.group
                group_item = QListWidgetItem(item.group)
                group_item.setFlags(Qt.ItemFlag.NoItemFlags)
                group_item.setData(Qt.ItemDataRole.UserRole, None)
                group_font = QFont(group_item.font())
                group_font.setBold(True)
                group_font.setPointSize(10)
                group_item.setFont(group_font)
                group_item.setForeground(QColor("#1d1d1f"))
                group_item.setBackground(QColor("#f5f5f7"))
                self.result_list.addItem(group_item)
            list_item = QListWidgetItem(item.label)
            list_item.setToolTip(item.detail)
            list_item.setData(Qt.ItemDataRole.UserRole, item.value)
            self.result_list.addItem(list_item)
        if not matches and text.strip():
            empty_item = QListWidgetItem("Kein Treffer gefunden")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled)
            self.result_list.addItem(empty_item)

        self._current_value = matches[0].value if len(matches) == 1 and text.strip() else None
        if len(matches) == 1 and text.strip():
            self.help_label.setText("Eindeutiger Treffer. Sie können direkt weiterarbeiten.")
        self.selection_changed.emit()

    def _select_item(self, item: QListWidgetItem) -> None:
        if not (item.flags() & Qt.ItemFlag.ItemIsEnabled) or item.data(Qt.ItemDataRole.UserRole) is None:
            return
        self._current_value = item.data(Qt.ItemDataRole.UserRole)
        self.search_input.blockSignals(True)
        self.search_input.setText(item.text())
        self.search_input.blockSignals(False)
        self.result_list.setMaximumHeight(0)
        self.help_label.setText("Ausgewählt. Zum Ändern einfach neuen Namen tippen.")
        self.selection_changed.emit()
