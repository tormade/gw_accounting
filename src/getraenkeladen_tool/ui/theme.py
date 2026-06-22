APP_STYLESHEET = """
QMainWindow {
    background: #f4f1ea;
    font-size: 14px;
}

QWidget#brandHeader {
    background: #111111;
    border-bottom: 0;
}

QLabel#brandLogo {
    color: #ffffff;
    font-size: 22px;
    font-weight: 800;
}

QLabel#brandClaim {
    color: #f4efe4;
    font-size: 16px;
    font-style: italic;
}

QWidget#appShell {
    background: #f4f1ea;
}

QListWidget#sidebarNavigation {
    background: #151515;
    border: 0;
    color: #e8e2d8;
    font-size: 15px;
    font-weight: 800;
    padding: 14px 10px;
}

QListWidget#sidebarNavigation::item {
    border-radius: 10px;
    margin: 3px 0;
    min-height: 38px;
    padding: 8px 12px;
}

QListWidget#sidebarNavigation::item:selected {
    background: #b91c1c;
    color: #ffffff;
}

QListWidget#sidebarNavigation::item:hover {
    background: #2a2a2a;
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
    background: #ffffff;
    border: 1px solid #e7e2d6;
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

QWidget#sectionBox,
QWidget#documentHeaderCard {
    background: #ffffff;
    border: 1px solid #dedbd2;
    border-radius: 16px;
    padding: 16px;
}

QWidget#pageHeader {
    background: transparent;
}

QWidget#pageToolbar {
    background: #ffffff;
    border: 1px solid #dedbd2;
    border-radius: 12px;
    padding: 10px;
}

QWidget#actionCard {
    background: #ffffff;
    border: 1px solid #dedbd2;
    border-radius: 16px;
    padding: 18px;
}

QWidget#actionCard:hover {
    border-color: #b91c1c;
}

QLabel#actionCardTitle {
    color: #111111;
    font-size: 18px;
    font-weight: 900;
}

QLabel#actionCardSubtitle {
    color: #5f625c;
    font-size: 13px;
}

QPushButton#actionCardButton {
    background: #111111;
    border: 0;
    color: #ffffff;
    font-weight: 900;
}

QPushButton#actionCardButton:hover {
    background: #333333;
}

QSplitter#workspaceSplitter::handle {
    background: #e6e0d3;
    border-radius: 2px;
}

QWidget#documentHeaderCard {
    background: #fbfaf7;
}

QLabel#sectionTitle {
    color: #111111;
    font-size: 15px;
    font-weight: 800;
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
    border: 1px solid #dedbd2;
    border-radius: 10px;
    alternate-background-color: #fbfaf7;
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
    font-size: 15px;
    font-weight: 900;
    min-height: 34px;
    padding: 10px 16px;
}

QPushButton#newDeliveryButton:hover {
    background: #941616;
}

QPushButton#helpButton {
    background: #ffffff;
    border: 1px solid #d8d6cf;
    border-radius: 17px;
    color: #111111;
    font-size: 16px;
    font-weight: 900;
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    padding: 0;
}

QPushButton#helpButton:hover {
    background: #f3efe6;
    border-color: #b91c1c;
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
