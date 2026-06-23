from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea, QStackedWidget, QVBoxLayout, QWidget

from .customer_panel import CustomerPanel
from .dashboard_panel import DashboardPanel
from .document_archive_panel import DocumentArchivePanel
from .document_workflow_panel import DeliveryNotePanel, InvoicePanel
from .layouts import SidebarNavigation
from .order_panel import OrderPanel
from .product_panel import ProductPanel
from .report_panel import ReportPanel
from .settings_panel import SettingsPanel


MAIN_TABS = (
    "Start",
    "Auftraege",
    "Belegarchiv",
    "Lieferscheine",
    "Rechnungen",
    "Kunden",
    "Produkte",
    "Listen",
    "Einstellungen",
)
MAIN_WINDOW_INITIAL_SIZE = (1180, 760)
MAIN_WINDOW_MINIMUM_SIZE = (900, 560)
BRAND_DIR = Path(__file__).resolve().parents[3] / "assets" / "brand"
LOGO_PATH = BRAND_DIR / "logo_winklmeier.png"
CLAIM_PATH = BRAND_DIR / "wir-bringens-einfach-schwarz.png"


class MainWindow(QMainWindow):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.setWindowTitle("Getraenke Winklmeier")
        self.resize(*MAIN_WINDOW_INITIAL_SIZE)
        self.setMinimumSize(*MAIN_WINDOW_MINIMUM_SIZE)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._header())

        self.dashboard_panel = DashboardPanel(session_factory=session_factory)
        self.order_panel = OrderPanel(session_factory=session_factory)
        self.document_archive_panel = DocumentArchivePanel(session_factory=session_factory)
        self.delivery_note_panel = DeliveryNotePanel(session_factory=session_factory)
        self.invoice_panel = InvoicePanel(session_factory=session_factory)
        self.customer_panel = CustomerPanel(session_factory=session_factory)
        self.product_panel = ProductPanel(session_factory=session_factory)
        self.report_panel = ReportPanel(session_factory=session_factory)
        self.settings_panel = SettingsPanel(session_factory=session_factory)
        self.refreshable_panels = {
            "Start": (self.dashboard_panel.refresh_dashboard,),
            "Auftraege": (self.order_panel.refresh_master_data, self.order_panel.refresh_orders),
            "Belegarchiv": (self.document_archive_panel.refresh_archive,),
            "Lieferscheine": (self.delivery_note_panel.refresh_master_data, self.delivery_note_panel.refresh_orders),
            "Rechnungen": (self.invoice_panel.refresh_master_data, self.invoice_panel.refresh_orders),
            "Kunden": (self.customer_panel.refresh_customers,),
            "Produkte": (self.product_panel.refresh_products,),
            "Listen": (self.report_panel.refresh_all_lists,),
            "Einstellungen": (),
        }

        self.dashboard_panel.new_delivery_requested.connect(self.open_orders_tab)
        self.dashboard_panel.manage_orders_requested.connect(self.open_orders_tab)
        self.dashboard_panel.invoice_requested.connect(self.open_invoices_tab)
        self.order_panel.delivery_note_requested.connect(self.open_delivery_note_for_order)
        self.order_panel.invoice_requested.connect(self.open_invoice_for_order)

        app_shell = QWidget()
        app_shell.setObjectName("appShell")
        shell_layout = QHBoxLayout(app_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        self.navigation = SidebarNavigation(MAIN_TABS)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._scrollable_tab(self.dashboard_panel))
        self.pages.addWidget(self._scrollable_tab(self.order_panel))
        self.pages.addWidget(self._scrollable_tab(self.document_archive_panel))
        self.pages.addWidget(self._scrollable_tab(self.delivery_note_panel))
        self.pages.addWidget(self._scrollable_tab(self.invoice_panel))
        self.pages.addWidget(self._scrollable_tab(self.customer_panel))
        self.pages.addWidget(self._scrollable_tab(self.product_panel))
        self.pages.addWidget(self._scrollable_tab(self.report_panel))
        self.pages.addWidget(self._scrollable_tab(self.settings_panel))
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.currentRowChanged.connect(self.refresh_current_tab)
        shell_layout.addWidget(self.navigation)
        shell_layout.addWidget(self.pages, 1)
        root_layout.addWidget(app_shell, 1)
        self.setCentralWidget(root)

    def open_orders_tab(self) -> None:
        self.navigation.setCurrentRow(MAIN_TABS.index("Auftraege"))

    def open_invoices_tab(self) -> None:
        self.navigation.setCurrentRow(MAIN_TABS.index("Rechnungen"))

    def open_delivery_note_for_order(self, order_id: int) -> None:
        self.navigation.setCurrentRow(MAIN_TABS.index("Lieferscheine"))
        self.delivery_note_panel.select_order(order_id)

    def open_invoice_for_order(self, order_id: int) -> None:
        self.navigation.setCurrentRow(MAIN_TABS.index("Rechnungen"))
        self.invoice_panel.select_order(order_id)

    def refresh_current_tab(self, index: int) -> None:
        if index < 0:
            return
        tab_name = MAIN_TABS[index]
        for refresh in self.refreshable_panels.get(tab_name, ()):
            refresh()

    def _scrollable_tab(self, panel: QWidget) -> QScrollArea:
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setWidget(panel)
        return scroll_area

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
