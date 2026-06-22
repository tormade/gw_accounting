from PySide6.QtCore import Qt
from collections.abc import Iterable

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


class PageHeader(QWidget):
    def __init__(self, title: str, subtitle: str = "", action: QWidget | None = None) -> None:
        super().__init__()
        self.setObjectName("pageHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        title_column = QVBoxLayout()
        title_column.setSpacing(4)
        headline = QLabel(title)
        headline.setObjectName("headline")
        title_column.addWidget(headline)
        if subtitle:
            muted = QLabel(subtitle)
            muted.setObjectName("muted")
            muted.setWordWrap(True)
            title_column.addWidget(muted)
        layout.addLayout(title_column)
        layout.addStretch()
        if action is not None:
            layout.addWidget(action)


class ContentSurface(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("contentSurface")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(18)


class ActionCard(QWidget):
    def __init__(self, title: str, subtitle: str, button_text: str = "") -> None:
        super().__init__()
        self.setObjectName("actionCard")
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("actionCardTitle")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("actionCardSubtitle")
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)
        layout.addStretch()

        self.button = QPushButton(button_text or title)
        self.button.setObjectName("actionCardButton")
        layout.addWidget(self.button)


class ResponsiveSplitter(QSplitter):
    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal) -> None:
        super().__init__(orientation)
        self.setObjectName("workspaceSplitter")
        self.setChildrenCollapsible(False)


class SidebarNavigation(QListWidget):
    def __init__(self, labels: Iterable[str]) -> None:
        super().__init__()
        self.setObjectName("sidebarNavigation")
        self.setFixedWidth(220)
        self.setSpacing(4)
        for label in labels:
            item = QListWidgetItem(label)
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            self.addItem(item)
        self.setCurrentRow(0)


class PageToolbar(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("pageToolbar")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.layout.addStretch()

    def add_action(self, button: QPushButton) -> None:
        self.layout.insertWidget(max(0, self.layout.count() - 1), button)


class WorkspaceCard(QWidget):
    def __init__(self, title: str, subtitle: str = "") -> None:
        super().__init__()
        self.setObjectName("workspaceCard")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        self.layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("sectionSubtitle")
            subtitle_label.setWordWrap(True)
            self.layout.addWidget(subtitle_label)


class FilterBar(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("filterBar")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)


def configure_form_layout(form: QFormLayout) -> None:
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
    form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
