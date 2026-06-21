APP_STYLESHEET = """
QMainWindow {
    background: #f5f5f2;
    font-size: 14px;
}

QWidget#brandHeader {
    background: #ffffff;
    border-bottom: 3px solid #111111;
}

QLabel#brandLogo {
    color: #111111;
    font-size: 22px;
    font-weight: 800;
}

QLabel#brandClaim {
    color: #111111;
    font-size: 16px;
    font-style: italic;
}

QTabWidget::pane {
    border: 1px solid #d8d6cf;
    background: #ffffff;
}

QTabBar::tab {
    background: #ece9e2;
    color: #111111;
    padding: 10px 18px;
}

QTabBar::tab:selected {
    background: #111111;
    color: #ffffff;
}

QLabel#headline {
    color: #111111;
    font-size: 22px;
    font-weight: 700;
}

QLabel#muted {
    color: #5f625c;
}

QWidget#guidanceBox {
    background: #fff7ed;
    border: 1px solid #f59e0b;
    border-radius: 10px;
    padding: 14px;
}

QLabel#stepTitle {
    color: #7c2d12;
    font-size: 18px;
    font-weight: 800;
}

QLabel#stepText {
    color: #3f3f3f;
    font-size: 14px;
}

QGroupBox#sectionBox {
    background: #ffffff;
    border: 1px solid #d8d6cf;
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px;
    font-size: 15px;
    font-weight: 800;
}

QGroupBox#sectionBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

QLabel#sectionSubtitle {
    color: #5f625c;
    font-size: 13px;
    font-weight: 400;
}

QWidget#metricCard {
    background: #ffffff;
    border: 1px solid #d8d6cf;
    border-radius: 12px;
    padding: 18px;
}

QLabel#metricValue {
    color: #b91c1c;
    font-size: 34px;
    font-weight: 900;
}

QLabel#metricLabel {
    color: #111111;
    font-size: 15px;
    font-weight: 800;
}

QLabel#statusBox {
    background: #eef2e6;
    border: 1px solid #c8d3b5;
    border-radius: 10px;
    color: #283618;
    padding: 12px;
    font-size: 14px;
    font-weight: 700;
}

QLineEdit,
QComboBox,
QSpinBox,
QDateEdit {
    min-height: 30px;
    font-size: 14px;
}

QTableWidget {
    background: #ffffff;
    gridline-color: #ddd8cc;
    selection-background-color: #fde68a;
    selection-color: #111111;
}

QHeaderView::section {
    background: #ece9e2;
    color: #111111;
    padding: 7px;
    font-weight: 700;
    border: 0;
}

QPushButton {
    border: 1px solid #bdb8aa;
    border-radius: 6px;
    padding: 10px 14px;
    background: #ffffff;
    color: #111111;
    font-weight: 700;
}

QPushButton:hover {
    background: #f3efe6;
}

QPushButton#primaryAction {
    background: #b91c1c;
    border: 0;
    color: #ffffff;
    padding: 10px 14px;
    font-weight: 700;
}

QPushButton#primaryAction:hover {
    background: #941616;
}

QPushButton#newDeliveryButton {
    background: #b91c1c;
    border: 0;
    color: #ffffff;
    font-size: 17px;
    font-weight: 900;
    min-height: 46px;
    padding: 14px 18px;
}

QPushButton#newDeliveryButton:hover {
    background: #941616;
}

QPushButton#addOrderLineButton,
QPushButton#saveOrderButton {
    background: #111111;
    border: 0;
    color: #ffffff;
}

QPushButton#addOrderLineButton:hover,
QPushButton#saveOrderButton:hover {
    background: #333333;
}

QPushButton#createOrderDocumentsButton {
    background: #b91c1c;
    border: 0;
    color: #ffffff;
}

QPushButton#createOrderDocumentsButton:hover {
    background: #941616;
}
"""
