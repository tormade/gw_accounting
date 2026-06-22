from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QPushButton, QSplitter, QVBoxLayout, QWidget


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


def configure_form_layout(form: QFormLayout) -> None:
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
    form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
