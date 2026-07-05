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
    def __init__(
        self,
        title: str,
        subtitle: str = "",
        action: QWidget | None = None,
        kicker: str = "",
    ) -> None:
        super().__init__()
        self.setObjectName("pageHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        title_column = QVBoxLayout()
        title_column.setSpacing(4)
        if kicker:
            kicker_label = QLabel(kicker)
            kicker_label.setObjectName("pageKicker")
            title_column.addWidget(kicker_label)
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
        self.layout.setContentsMargins(28, 26, 28, 28)
        self.layout.setSpacing(20)


class InspectorPanel(QWidget):
    def __init__(self, title: str = "Kontext", subtitle: str = "") -> None:
        super().__init__()
        self.setObjectName("inspectorPanel")
        self.setMinimumWidth(300)
        self.setMaximumWidth(360)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(14)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("inspectorTitle")
        self.title_label.setWordWrap(True)
        self.layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("inspectorSubtitle")
        self.subtitle_label.setWordWrap(True)
        self.layout.addWidget(self.subtitle_label)

        self.body = QVBoxLayout()
        self.body.setSpacing(10)
        self.layout.addLayout(self.body)
        self.layout.addStretch()

    def set_heading(self, title: str, subtitle: str = "") -> None:
        self.title_label.setText(title)
        self.subtitle_label.setText(subtitle)

    def add_section_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("inspectorSection")
        self.body.addWidget(label)
        return label

    def add_value_label(self, label: str, value: str = "-") -> QLabel:
        value_label = QLabel(f"{label}: {value}")
        value_label.setObjectName("inspectorValue")
        value_label.setWordWrap(True)
        self.body.addWidget(value_label)
        return value_label


class ActionCard(QWidget):
    def __init__(self, title: str, subtitle: str, button_text: str = "", kicker: str = "", tone: str = "default") -> None:
        super().__init__()
        self.setObjectName("actionCard")
        self.setProperty("tone", tone)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        if kicker:
            kicker_label = QLabel(kicker)
            kicker_label.setObjectName("cardKicker")
            layout.addWidget(kicker_label)

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
        self.setAccessibleName("Hauptnavigation")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedWidth(220)
        self.setSpacing(4)
        for label in labels:
            item = QListWidgetItem(label)
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
            item.setToolTip(f"{label} oeffnen")
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
    def __init__(self, title: str, subtitle: str = "", tone: str = "default", kicker: str = "") -> None:
        super().__init__()
        self.setObjectName("workspaceCard")
        self.setProperty("tone", tone)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(12)

        if kicker:
            kicker_label = QLabel(kicker)
            kicker_label.setObjectName("cardKicker")
            self.layout.addWidget(kicker_label)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        self.layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("sectionSubtitle")
            subtitle_label.setWordWrap(True)
            self.layout.addWidget(subtitle_label)


def configure_form_layout(form: QFormLayout) -> None:
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
    form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
