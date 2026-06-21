from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QTabWidget, QVBoxLayout, QWidget

from .customer_panel import CustomerPanel
from .document_panel import DocumentPanel
from .order_panel import OrderPanel
from .product_panel import ProductPanel
from .report_panel import ReportPanel


MAIN_TABS = ("Kunden", "Produkte", "Auftraege", "Belege", "Listen")
BRAND_DIR = Path(__file__).resolve().parents[3] / "assets" / "brand"
LOGO_PATH = BRAND_DIR / "logo_winklmeier.png"
CLAIM_PATH = BRAND_DIR / "wir-bringens-einfach-schwarz.png"


class MainWindow(QMainWindow):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.setWindowTitle("Getraenke Winklmeier")
        self.resize(1040, 680)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._header())

        self.tabs = QTabWidget()
        self.tabs.addTab(CustomerPanel(session_factory=session_factory), "Kunden")
        self.tabs.addTab(ProductPanel(session_factory=session_factory), "Produkte")
        self.tabs.addTab(OrderPanel(session_factory=session_factory), "Auftraege")
        self.tabs.addTab(DocumentPanel(session_factory=session_factory), "Belege")
        self.tabs.addTab(ReportPanel(session_factory=session_factory), "Listen")
        root_layout.addWidget(self.tabs)
        self.setCentralWidget(root)

    def _header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("brandHeader")
        layout = QVBoxLayout(header)
        layout.setContentsMargins(28, 20, 28, 18)
        layout.setSpacing(8)

        logo = QLabel("Getraenke Winklmeier")
        logo.setObjectName("brandLogo")
        if LOGO_PATH.exists():
            logo.setPixmap(QPixmap(str(LOGO_PATH)))
        layout.addWidget(logo)

        claim = QLabel("Wir bringen's einfach")
        claim.setObjectName("brandClaim")
        if CLAIM_PATH.exists():
            claim_pixmap = QPixmap(str(CLAIM_PATH)).scaledToWidth(220, Qt.TransformationMode.SmoothTransformation)
            claim.setPixmap(claim_pixmap)
        layout.addWidget(claim)

        return header

    def _panel(self, title: str, subtitle: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        headline = QLabel(title)
        headline.setObjectName("headline")
        layout.addWidget(headline)

        muted = QLabel(subtitle)
        muted.setObjectName("muted")
        layout.addWidget(muted)

        action = QPushButton("Neu anlegen")
        action.setObjectName("primaryAction")
        action.setFixedWidth(160)
        layout.addWidget(action)

        layout.addStretch()

        return widget
