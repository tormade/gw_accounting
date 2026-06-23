APP_STYLESHEET = """
QMainWindow {
    background: #f4f1ea;
    color: #1f2a24;
    font-size: 14px;
}

QWidget {
    color: #1f2a24;
}

QWidget#brandHeader {
    background: #ffffff;
    border-bottom: 1px solid #e3ded4;
}

QLabel#brandLogo {
    color: #123326;
    font-size: 22px;
    font-weight: 800;
}

QLabel#brandClaim {
    color: #6b5b3f;
    font-size: 16px;
    font-style: italic;
}

QWidget#appShell {
    background: #f4f1ea;
}

QListWidget#sidebarNavigation {
    background: #ffffff;
    border-right: 1px solid #e3ded4;
    color: #33443a;
    font-size: 15px;
    font-weight: 700;
    outline: 0;
    padding: 14px 10px;
}

QListWidget#sidebarNavigation::item {
    border-radius: 12px;
    margin: 3px 0;
    min-height: 38px;
    padding: 8px 12px;
}

QListWidget#sidebarNavigation::item:selected {
    background: #e8f3ee;
    color: #116149;
    border-left: 4px solid #116149;
}

QListWidget#sidebarNavigation::item:hover {
    background: #f5f1e8;
    color: #123326;
}

QScrollArea {
    background: #f4f1ea;
}

QWidget#contentSurface {
    background: #f4f1ea;
}

QWidget#pageHeader {
    background: transparent;
}

QLabel#headline {
    color: #123326;
    font-size: 24px;
    font-weight: 800;
}

QLabel#muted,
QLabel#sectionSubtitle {
    color: #67736b;
    font-size: 13px;
}

QWidget#workspaceCard,
QWidget#sectionBox,
QWidget#documentHeaderCard,
QWidget#actionCard,
QWidget#metricCard {
    background: #ffffff;
    border: 1px solid #e1ddd3;
    border-radius: 18px;
    padding: 18px;
}

QWidget#workspaceCard {
    border-color: #ded7ca;
}

QWidget#workspaceCard:hover,
QWidget#actionCard:hover {
    border-color: #c6d9cf;
}

QWidget#pageToolbar {
    background: #ffffff;
    border: 1px solid #e1ddd3;
    border-radius: 14px;
    padding: 10px;
}

QWidget#totalBar {
    background: #eef7f2;
    border: 1px solid #cfe3d9;
    border-radius: 14px;
    padding: 10px 12px;
}

QLabel#sectionTitle {
    color: #123326;
    font-size: 15px;
    font-weight: 800;
}

QLabel#stepTitle {
    color: #116149;
    font-size: 18px;
    font-weight: 800;
}

QLabel#stepText {
    color: #33443a;
    font-size: 14px;
}

QWidget#guidanceBox {
    background: #ffffff;
    border: 1px solid #e1ddd3;
    border-radius: 14px;
    padding: 14px;
}

QLabel#actionCardTitle {
    color: #123326;
    font-size: 18px;
    font-weight: 900;
}

QLabel#actionCardSubtitle {
    color: #67736b;
    font-size: 13px;
}

QLabel#metricValue {
    color: #116149;
    font-size: 36px;
    font-weight: 900;
}

QLabel#metricLabel {
    color: #123326;
    font-size: 15px;
    font-weight: 800;
}

QLabel#statusBox {
    background: #eef7f2;
    border: 1px solid #cfe3d9;
    border-radius: 14px;
    color: #123326;
    padding: 12px;
    font-size: 14px;
    font-weight: 700;
}

QLineEdit,
QComboBox,
QSpinBox,
QDateEdit {
    background: #fffdf8;
    border: 1px solid #d8ded9;
    border-radius: 12px;
    color: #1f2a24;
    font-size: 14px;
    min-height: 36px;
    padding: 8px 12px;
    selection-background-color: #d7ebe2;
    selection-color: #123326;
}

QComboBox,
QDateEdit {
    padding-right: 42px;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDateEdit:focus {
    background: #ffffff;
    border: 2px solid #116149;
    padding: 7px 11px;
}

QComboBox:on,
QDateEdit:on {
    background: #f7fbf8;
    border: 2px solid #116149;
}

QComboBox:disabled,
QDateEdit:disabled,
QLineEdit:disabled,
QSpinBox:disabled {
    background: #eeeae2;
    border-color: #ddd6ca;
    color: #8a928c;
}

QComboBox::drop-down,
QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    background: #eef7f2;
    border-left: 1px solid #d8ded9;
    border-top-right-radius: 11px;
    border-bottom-right-radius: 11px;
    width: 34px;
}

QComboBox::drop-down:hover,
QDateEdit::drop-down:hover {
    background: #dceee6;
    border-left-color: #bcd7cb;
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
    border-top: 6px solid #116149;
}

QComboBox::down-arrow:on,
QDateEdit::down-arrow:on {
    margin-top: 0;
    border-top: 0;
    border-bottom: 6px solid #116149;
}

QLineEdit#tableSearchField {
    background: #fbfaf6;
    border: 1px solid #e1ddd3;
    border-radius: 12px;
    color: #123326;
    min-height: 34px;
    padding: 8px 12px;
}

QLineEdit#tableSearchField:focus {
    background: #ffffff;
    border: 2px solid #116149;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #cfd7d2;
    border-radius: 12px;
    color: #1f2a24;
    outline: 0;
    padding: 6px;
    selection-background-color: #d7ebe2;
    selection-color: #123326;
}

QCalendarWidget {
    background: #ffffff;
    border: 1px solid #d8ded9;
    border-radius: 16px;
    color: #1f2a24;
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background: #eef7f2;
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
    min-height: 42px;
}

QCalendarWidget QToolButton {
    background: transparent;
    border: 0;
    border-radius: 10px;
    color: #116149;
    font-weight: 900;
    margin: 6px;
    padding: 6px 10px;
}

QCalendarWidget QToolButton:hover {
    background: #dceee6;
}

QCalendarWidget QMenu {
    background: #ffffff;
    border: 1px solid #d8ded9;
    border-radius: 12px;
    color: #1f2a24;
}

QCalendarWidget QSpinBox {
    background: #ffffff;
    border: 1px solid #bcd7cb;
    border-radius: 10px;
    min-height: 28px;
    padding: 4px 8px;
}

QCalendarWidget QAbstractItemView {
    background: #ffffff;
    border: 0;
    border-radius: 0;
    color: #1f2a24;
    outline: 0;
    selection-background-color: #116149;
    selection-color: #ffffff;
}

QListWidget {
    background: #ffffff;
    border: 1px solid #e1ddd3;
    border-radius: 12px;
    color: #1f2a24;
    outline: 0;
    selection-background-color: #d7ebe2;
    selection-color: #123326;
}

QListWidget::item {
    border-radius: 8px;
    min-height: 28px;
    padding: 7px 9px;
}

QListWidget::item:selected {
    background: #d7ebe2;
    color: #123326;
}

QListWidget::item:hover {
    background: #f5f1e8;
}

QTableWidget {
    alternate-background-color: #fbfaf6;
    background: #ffffff;
    border: 1px solid #e1ddd3;
    border-radius: 14px;
    color: #1f2a24;
    gridline-color: #ebe6dc;
    selection-background-color: #d7ebe2;
    selection-color: #123326;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background: #d7ebe2;
    color: #123326;
}

QTableWidget QLineEdit {
    background: #ffffff;
    border: 1px solid #116149;
    color: #123326;
    selection-background-color: #d7ebe2;
    selection-color: #123326;
}

QHeaderView::section {
    background: #f5f1e8;
    border: 0;
    border-bottom: 1px solid #e1ddd3;
    color: #33443a;
    font-weight: 800;
    padding: 9px;
}

QPushButton {
    background: #fffdf8;
    border: 1px solid #cfd7d2;
    border-radius: 12px;
    color: #123326;
    font-weight: 800;
    min-height: 34px;
    padding: 9px 16px;
}

QPushButton:hover {
    background: #f5f1e8;
    border-color: #bfcac3;
}

QPushButton:pressed {
    background: #e8f3ee;
}

QPushButton:disabled {
    background: #eeeae2;
    border-color: #ddd6ca;
    color: #8a928c;
}

QPushButton#primaryAction,
QPushButton#newDeliveryButton,
QPushButton#actionCardButton,
QPushButton#addOrderLineButton,
QPushButton#saveOrderButton {
    background: #116149;
    border: 0;
    color: #ffffff;
    font-weight: 900;
}

QPushButton#primaryAction:hover,
QPushButton#newDeliveryButton:hover,
QPushButton#actionCardButton:hover,
QPushButton#addOrderLineButton:hover,
QPushButton#saveOrderButton:hover {
    background: #0d4d3a;
}

QPushButton#helpButton {
    background: #ffffff;
    border: 1px solid #d6d1c8;
    border-radius: 18px;
    color: #116149;
    font-size: 16px;
    font-weight: 900;
    max-height: 36px;
    max-width: 36px;
    min-height: 36px;
    min-width: 36px;
    padding: 0;
}

QPushButton#helpButton:hover {
    background: #e8f3ee;
    border-color: #116149;
}

QPushButton#createOrderDocumentsButton {
    background: #c4312f;
    border: 0;
    color: #ffffff;
}

QPushButton#createOrderDocumentsButton:hover {
    background: #a72826;
}

QPushButton#dangerAction,
QPushButton#removeOrderLineButton,
QPushButton#removeDepositReturnButton,
QPushButton#removeDocumentLineButton,
QPushButton#removeDocumentDepositReturnButton {
    background: #fff8f6;
    border: 1px solid #efc9c3;
    color: #9e2f28;
}

QPushButton#dangerAction:hover,
QPushButton#removeOrderLineButton:hover,
QPushButton#removeDepositReturnButton:hover,
QPushButton#removeDocumentLineButton:hover,
QPushButton#removeDocumentDepositReturnButton:hover {
    background: #fdecea;
    border-color: #d98b82;
    color: #7f241f;
}

QSplitter#workspaceSplitter::handle {
    background: #e1ddd3;
    border-radius: 3px;
    margin: 8px 4px;
}

QTabWidget::pane {
    border: 0;
}

QTabBar::tab {
    background: #ffffff;
    border: 1px solid #e1ddd3;
    border-radius: 10px;
    color: #33443a;
    font-weight: 800;
    margin-right: 8px;
    padding: 10px 16px;
}

QTabBar::tab:selected {
    background: #e8f3ee;
    border-color: #cfe3d9;
    color: #116149;
}
"""
