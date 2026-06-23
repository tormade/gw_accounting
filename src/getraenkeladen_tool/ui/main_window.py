from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea, QStackedWidget, QTabWidget, QVBoxLayout, QWidget

from .checklist_panel import ChecklistPanel
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
    "Heute",
    "Kunde & Bestellung",
    "Belege",
    "Offene Posten",
    "Tagesliste",
    "Stammdaten",
    "Pruefliste",
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
        self.open_items_panel = ReportPanel(session_factory=session_factory)
        self.daily_list_panel = ReportPanel(session_factory=session_factory)
        self.settings_panel = SettingsPanel(session_factory=session_factory)
        self.document_workspace = self._document_workspace()
        self.master_data_workspace = self._master_data_workspace()
        self.checklist_panel = ChecklistPanel(session_factory=session_factory)
        self.refreshable_panels = {
            "Heute": (self.dashboard_panel.refresh_dashboard,),
            "Kunde & Bestellung": (self.order_panel.refresh_master_data, self.order_panel.refresh_orders),
            "Belege": (
                self.document_archive_panel.refresh_archive,
                self.delivery_note_panel.refresh_master_data,
                self.delivery_note_panel.refresh_orders,
                self.invoice_panel.refresh_master_data,
                self.invoice_panel.refresh_orders,
            ),
            "Offene Posten": (self.open_items_panel.refresh_all_lists,),
            "Tagesliste": (self.daily_list_panel.refresh_all_lists,),
            "Stammdaten": (self.customer_panel.refresh_customers, self.product_panel.refresh_products),
            "Pruefliste": (self.checklist_panel.refresh_issues,),
            "Einstellungen": (),
        }

        self.dashboard_panel.new_delivery_requested.connect(self.open_new_order_dialog)
        self.dashboard_panel.manage_orders_requested.connect(self.open_orders_tab)
        self.dashboard_panel.invoice_requested.connect(self.open_invoices_tab)
        self.order_panel.delivery_note_requested.connect(self.open_delivery_note_for_order)
        self.order_panel.invoice_requested.connect(self.open_invoice_for_order)
        self.document_archive_panel.document_open_requested.connect(self.open_document_from_archive)
        self.document_archive_panel.order_open_requested.connect(self.open_order_for_id)

        app_shell = QWidget()
        app_shell.setObjectName("appShell")
        shell_layout = QHBoxLayout(app_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        self.navigation = SidebarNavigation(MAIN_TABS)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._scrollable_tab(self.dashboard_panel))
        self.pages.addWidget(self._scrollable_tab(self.order_panel))
        self.pages.addWidget(self._scrollable_tab(self.document_workspace))
        self.pages.addWidget(self._scrollable_tab(self.open_items_panel))
        self.pages.addWidget(self._scrollable_tab(self.daily_list_panel))
        self.pages.addWidget(self._scrollable_tab(self.master_data_workspace))
        self.pages.addWidget(self._scrollable_tab(self.checklist_panel))
        self.pages.addWidget(self._scrollable_tab(self.settings_panel))
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.currentRowChanged.connect(self.refresh_current_tab)
        shell_layout.addWidget(self.navigation)
        shell_layout.addWidget(self.pages, 1)
        root_layout.addWidget(app_shell, 1)
        self.setCentralWidget(root)

    def open_orders_tab(self) -> None:
        self.navigation.setCurrentRow(MAIN_TABS.index("Kunde & Bestellung"))

    def open_new_order_dialog(self) -> None:
        self.open_orders_tab()
        self.order_panel.open_new_order_dialog()

    def open_order_for_id(self, order_id: int) -> None:
        self.open_orders_tab()
        self.order_panel.load_order_by_id(order_id)

    def open_invoices_tab(self) -> None:
        self.navigation.setCurrentRow(MAIN_TABS.index("Belege"))
        self.document_workspace.setCurrentWidget(self.invoice_panel)

    def open_delivery_note_for_order(self, order_id: int) -> None:
        self.navigation.setCurrentRow(MAIN_TABS.index("Belege"))
        self.document_workspace.setCurrentWidget(self.delivery_note_panel)
        self.delivery_note_panel.select_order(order_id)

    def open_invoice_for_order(self, order_id: int) -> None:
        self.navigation.setCurrentRow(MAIN_TABS.index("Belege"))
        self.document_workspace.setCurrentWidget(self.invoice_panel)
        self.invoice_panel.select_order(order_id)

    def open_document_from_archive(self, document_type: str, order_id: int) -> None:
        if document_type == "Rechnung":
            self.open_invoice_for_order(order_id)
        else:
            self.open_delivery_note_for_order(order_id)

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

    def _document_workspace(self) -> QTabWidget:
        tabs = QTabWidget()
        tabs.setObjectName("workspaceTabs")
        tabs.addTab(self.document_archive_panel, "Archiv")
        tabs.addTab(self.delivery_note_panel, "Lieferbeleg")
        tabs.addTab(self.invoice_panel, "Rechnung")
        return tabs

    def _master_data_workspace(self) -> QTabWidget:
        tabs = QTabWidget()
        tabs.setObjectName("workspaceTabs")
        tabs.addTab(self.customer_panel, "Kunden")
        tabs.addTab(self.product_panel, "Artikel")
        return tabs

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
