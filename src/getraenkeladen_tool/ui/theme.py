APP_STYLESHEET = """
QMainWindow {
    background: #f5f5f7;
    color: #1d1d1f;
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 14px;
}

QWidget {
    color: #1d1d1f;
}

QWidget#appShell,
QScrollArea,
QWidget#contentSurface {
    background: #f5f5f7;
}

QWidget#contentSurface {
    padding: 0;
}

QWidget#inspectorPanel {
    background: #ffffff;
    border-left: 1px solid #d2d2d7;
}

QLabel#inspectorTitle {
    color: #1d1d1f;
    font-size: 21px;
    font-weight: 760;
}

QLabel#inspectorSubtitle,
QLabel#inspectorValue {
    color: #6e6e73;
    font-size: 14px;
}

QLabel#nextStepValue {
    background: #f5f5f7;
    border: 1px solid #e1e1e6;
    border-radius: 8px;
    color: #1d1d1f;
    font-size: 14px;
    font-weight: 650;
    padding: 10px;
}

QLabel#inspectorSection {
    color: #1d1d1f;
    font-size: 13px;
    font-weight: 760;
    padding-top: 8px;
}

QWidget#pageHeader {
    background: transparent;
    border: 0;
    padding: 0;
}

QLabel#pageKicker,
QLabel#cardKicker {
    color: #6e6e73;
    font-size: 12px;
    font-weight: 700;
}

QLabel#headline {
    color: #1d1d1f;
    font-size: 27px;
    font-weight: 800;
}

QLabel#muted,
QLabel#sectionSubtitle {
    color: #6e6e73;
    font-size: 14px;
}

QLabel#sectionTitle,
QLabel#workflowBoardTitle {
    color: #1d1d1f;
    font-size: 17px;
    font-weight: 800;
}

QLabel#stepTitle {
    color: #1d1d1f;
    font-size: 18px;
    font-weight: 800;
}

QLabel#stepText {
    color: #515154;
    font-size: 14px;
}

QListWidget#sidebarNavigation {
    background: #f5f5f7;
    border: 0;
    border-right: 1px solid #d2d2d7;
    color: #1d1d1f;
    font-size: 15px;
    font-weight: 650;
    outline: 0;
    padding: 14px 10px;
}

QListWidget#sidebarNavigation::item {
    border: 1px solid transparent;
    border-radius: 8px;
    margin: 2px 0;
    min-height: 38px;
    padding: 7px 12px;
}

QListWidget#sidebarNavigation::item:selected {
    background: #ffffff;
    border-left: 4px solid #c4312f;
    color: #1d1d1f;
}

QListWidget#sidebarNavigation::item:hover {
    background: #ffffff;
    border-color: #d2d2d7;
}

QWidget#workspaceCard,
QWidget#sectionBox,
QWidget#documentHeaderCard,
QWidget#actionCard,
QWidget#metricCard,
QWidget#dailyCockpitCard,
QWidget#todayContactList,
QWidget#liveSummaryCard,
QWidget#guidanceBox,
QWidget#workflowBoard,
QWidget#workflowStep,
QWidget#todayTaskQueue,
QWidget#todayTaskRow {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 10px;
    padding: 16px;
}

QWidget#workspaceCard[tone="route"],
QWidget#actionCard[tone="route"],
QWidget#dailyCockpitCard[tone="route"],
QWidget#workspaceCard[tone="cash"],
QWidget#actionCard[tone="cash"],
QWidget#dailyCockpitCard[tone="cash"],
QWidget#workspaceCard[tone="audit"],
QWidget#actionCard[tone="audit"],
QWidget#dailyCockpitCard[tone="audit"],
QWidget#workspaceCard[tone="document"] {
    border-top: 1px solid #d2d2d7;
    border-left: 1px solid #d2d2d7;
}

QWidget#workspaceCard:hover,
QWidget#actionCard:hover {
    background: #ffffff;
    border-color: #b9b9bf;
}

QWidget#pageToolbar {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 10px;
    padding: 10px;
}

QWidget#totalBar,
QWidget#documentFinishBar,
QLabel#statusBox {
    background: #eef6ff;
    border: 1px solid #c8ddf4;
    border-radius: 10px;
    color: #1d1d1f;
    padding: 11px;
    font-size: 14px;
    font-weight: 700;
}

QLabel#totalAmount {
    color: #1d1d1f;
    font-size: 17px;
    font-weight: 800;
}

QPushButton#disclosureButton {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    color: #1d1d1f;
    font-size: 15px;
    font-weight: 760;
    min-height: 42px;
    padding: 8px 14px;
    text-align: left;
}

QPushButton#disclosureButton:checked {
    background: #f5f5f7;
    border-color: #b9b9bf;
}

QWidget#disclosurePanel {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    padding: 12px;
}

QGroupBox {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    color: #1d1d1f;
    font-weight: 700;
    margin-top: 12px;
    padding: 14px 10px 10px 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
}

QGroupBox:unchecked {
    color: #6e6e73;
}

QWidget#dailyCockpitCard {
    min-height: 70px;
    max-height: 86px;
}

QWidget#todaySummaryPanel {
    background: transparent;
    border: 0;
    padding: 0;
}

QLabel#summaryPanelTitle {
    color: #1d1d1f;
    font-size: 17px;
    font-weight: 800;
    padding: 0 2px 2px 2px;
}

QWidget#heroSearchPanel {
    background: transparent;
    border: 0;
    padding: 0;
}

QLabel#workflowNumber {
    background: #f5f5f7;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    color: #6e6e73;
    font-size: 16px;
    font-weight: 800;
    min-height: 38px;
    min-width: 46px;
    padding: 6px;
}

QLabel#workflowStepTitle,
QLabel#actionCardTitle {
    color: #1d1d1f;
    font-size: 17px;
    font-weight: 800;
}

QLabel#workflowStepText,
QLabel#actionCardSubtitle {
    color: #6e6e73;
    font-size: 14px;
}

QWidget#customerSearchHero {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 10px;
    padding: 20px;
}

QLabel#heroTitle {
    color: #1d1d1f;
    font-size: 24px;
    font-weight: 800;
}

QWidget#customerSearchHero QLabel#sectionSubtitle {
    color: #6e6e73;
}

QLabel#heroSearchQuery {
    background: #f5f5f7;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    color: #1d1d1f;
    font-size: 18px;
    font-weight: 700;
    padding: 12px;
}

QLabel#contactPreviewRow {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    color: #1d1d1f;
    padding: 10px;
}

QLabel#metricValue {
    color: #1d1d1f;
    font-size: 34px;
    font-weight: 800;
    min-width: 52px;
}

QLabel#metricLabel {
    color: #1d1d1f;
    font-size: 15px;
    font-weight: 800;
}

QLabel#metricHint {
    color: #6e6e73;
    font-size: 13px;
    font-weight: 650;
}

QLineEdit,
QComboBox,
QSpinBox,
QDateEdit {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    color: #1d1d1f;
    font-size: 14px;
    min-height: 38px;
    padding: 7px 10px;
    selection-background-color: #d9ebff;
    selection-color: #1d1d1f;
}

QComboBox,
QDateEdit {
    padding-right: 40px;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDateEdit:focus {
    background: #ffffff;
    border: 2px solid #0a84ff;
    padding: 6px 9px;
}

QLineEdit[state="error"] {
    background: #fff7f7;
    border: 2px solid #c4312f;
    padding: 6px 9px;
}

QComboBox:on,
QDateEdit:on {
    background: #ffffff;
    border: 2px solid #0a84ff;
}

QComboBox:disabled,
QDateEdit:disabled,
QLineEdit:disabled,
QSpinBox:disabled {
    background: #f0f0f2;
    border-color: #d2d2d7;
    color: #8e8e93;
}

QComboBox::drop-down,
QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    background: #f5f5f7;
    border-left: 1px solid #d2d2d7;
    border-top-right-radius: 7px;
    border-bottom-right-radius: 7px;
    width: 34px;
}

QComboBox::drop-down:hover,
QDateEdit::drop-down:hover {
    background: #eeeeef;
}

QComboBox::down-arrow,
QDateEdit::down-arrow {
    image: none;
    border: 0;
    width: 0;
    height: 0;
    margin-top: 4px;
    margin-right: 12px;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #6e6e73;
}

QComboBox::down-arrow:on,
QDateEdit::down-arrow:on {
    margin-top: 0;
    border-top: 0;
    border-bottom: 6px solid #6e6e73;
}

QLineEdit#tableSearchField {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    color: #1d1d1f;
    min-height: 38px;
    padding: 7px 10px;
}

QLineEdit#tableSearchField:focus {
    border: 2px solid #0a84ff;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    color: #1d1d1f;
    outline: 0;
    padding: 6px;
    selection-background-color: #d9ebff;
    selection-color: #1d1d1f;
}

QCalendarWidget {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 10px;
    color: #1d1d1f;
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background: #f5f5f7;
    min-height: 38px;
}

QCalendarWidget QToolButton {
    background: transparent;
    border: 0;
    border-radius: 8px;
    color: #1d1d1f;
    font-weight: 700;
    margin: 5px;
    padding: 7px 9px;
}

QCalendarWidget QToolButton:hover {
    background: #eeeeef;
}

QCalendarWidget QMenu,
QCalendarWidget QSpinBox,
QCalendarWidget QAbstractItemView {
    background: #ffffff;
    color: #1d1d1f;
    selection-background-color: #0a84ff;
    selection-color: #ffffff;
}

QListWidget {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 10px;
    color: #1d1d1f;
    outline: 0;
    selection-background-color: #d9ebff;
    selection-color: #1d1d1f;
}

QListWidget::item {
    border-radius: 7px;
    min-height: 34px;
    padding: 7px 9px;
}

QListWidget::item:selected {
    background: #d9ebff;
    color: #1d1d1f;
}

QListWidget::item:hover {
    background: #f5f5f7;
}

QTableWidget {
    alternate-background-color: #fbfbfd;
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 10px;
    color: #1d1d1f;
    font-size: 14px;
    gridline-color: #e5e5ea;
    selection-background-color: #d9ebff;
    selection-color: #1d1d1f;
}

QTableWidget::item {
    padding: 8px;
    min-height: 32px;
}

QTableWidget::item:selected {
    background: #d9ebff;
    color: #1d1d1f;
}

QTableWidget QLineEdit {
    background: #ffffff;
    border: 2px solid #0a84ff;
    color: #1d1d1f;
    selection-background-color: #d9ebff;
    selection-color: #1d1d1f;
}

QHeaderView::section {
    background: #f5f5f7;
    border: 0;
    border-bottom: 1px solid #d2d2d7;
    color: #6e6e73;
    font-size: 13px;
    font-weight: 750;
    padding: 9px;
}

QPushButton {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    color: #1d1d1f;
    font-size: 14px;
    font-weight: 650;
    min-height: 38px;
    padding: 7px 14px;
}

QPushButton:hover {
    background: #f5f5f7;
    border-color: #b9b9bf;
}

QPushButton:pressed {
    background: #eeeeef;
}

QPushButton:disabled {
    background: #f0f0f2;
    border-color: #d2d2d7;
    color: #8e8e93;
}

QPushButton#primaryAction,
QPushButton#newDeliveryButton,
QPushButton#newOrderButton,
QPushButton#addOrderLineButton,
QPushButton#saveOrderButton,
QPushButton#createOrderDocumentsButton,
QPushButton#workflowStepButton {
    background: #0a84ff;
    border: 1px solid #0a84ff;
    color: #ffffff;
}

QPushButton#primaryAction:hover,
QPushButton#newDeliveryButton:hover,
QPushButton#newOrderButton:hover,
QPushButton#addOrderLineButton:hover,
QPushButton#saveOrderButton:hover,
QPushButton#createOrderDocumentsButton:hover,
QPushButton#workflowStepButton:hover {
    background: #0071e3;
    border-color: #0071e3;
}

QPushButton#primaryAction:disabled,
QPushButton#newDeliveryButton:disabled,
QPushButton#newOrderButton:disabled,
QPushButton#addOrderLineButton:disabled,
QPushButton#saveOrderButton:disabled,
QPushButton#createOrderDocumentsButton:disabled,
QPushButton#workflowStepButton:disabled {
    background: #f0f0f2;
    border-color: #d2d2d7;
    color: #8e8e93;
}

QPushButton#helpButton {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    color: #6e6e73;
    font-weight: 800;
    max-height: 38px;
    max-width: 38px;
    min-height: 38px;
    min-width: 38px;
    padding: 0;
}

QPushButton#helpButton:hover {
    background: #f5f5f7;
    color: #1d1d1f;
}

QPushButton#actionCardButton {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    color: #1d1d1f;
}

QPushButton#actionCardButton:hover {
    background: #f5f5f7;
    border-color: #b9b9bf;
}

QPushButton#dangerAction,
QPushButton#removeOrderLineButton,
QPushButton#removeDepositReturnButton,
QPushButton#removeDocumentLineButton,
QPushButton#removeDocumentDepositReturnButton {
    background: #fff7f7;
    border: 1px solid #f1c5c5;
    color: #b42318;
}

QPushButton#dangerAction:hover,
QPushButton#removeOrderLineButton:hover,
QPushButton#removeDepositReturnButton:hover,
QPushButton#removeDocumentLineButton:hover,
QPushButton#removeDocumentDepositReturnButton:hover {
    background: #ffeded;
    border-color: #d92d20;
}

QSplitter#workspaceSplitter::handle {
    background: #d2d2d7;
    border-radius: 2px;
    margin: 8px 4px;
}

QTabWidget::pane {
    border: 0;
}

QTabBar::tab {
    background: #ffffff;
    border: 1px solid #d2d2d7;
    border-radius: 8px;
    color: #1d1d1f;
    font-weight: 650;
    margin-right: 6px;
    min-height: 34px;
    padding: 8px 14px;
}

QTabBar::tab:selected {
    background: #f5f5f7;
    border-color: #b9b9bf;
    color: #1d1d1f;
}

QDialog {
    background: #f5f5f7;
}
"""
