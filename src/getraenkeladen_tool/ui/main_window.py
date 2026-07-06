from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .checklist_panel import ChecklistPanel
from .customer_folder_panel import CustomerFolderPanel
from .customer_panel import CustomerPanel
from .document_archive_panel import DocumentArchivePanel
from .document_workflow_panel import DeliveryNotePanel, InvoicePanel, ReturnInvoicePanel
from .layouts import SidebarNavigation
from .management_home_panel import ManagementHomePanel
from .order_panel import OrderPanel
from .product_panel import ProductPanel
from .report_panel import ReportPanel
from .settings_panel import SettingsPanel
from .work_start_panel import WorkStartPanel


MAIN_TABS = (
    "Arbeiten",
    "Rechnungen",
    "Verwaltung",
)
MAIN_WINDOW_INITIAL_SIZE = (1440, 860)
MAIN_WINDOW_MINIMUM_SIZE = (1100, 680)
BRAND_DIR = Path(__file__).resolve().parents[3] / "assets" / "brand"
LOGO_PATH = BRAND_DIR / "logo_winklmeier.png"
CLAIM_PATH = BRAND_DIR / "wir-bringens-einfach-schwarz.png"


class MainWindow(QMainWindow):
    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.setWindowTitle("Getränke Winklmeier")
        self.resize(*MAIN_WINDOW_INITIAL_SIZE)
        self.setMinimumSize(*MAIN_WINDOW_MINIMUM_SIZE)
        self.document_dialogs: list[QDialog] = []

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.work_start_panel = WorkStartPanel(session_factory=session_factory)
        self.customer_folder_panel = CustomerFolderPanel(session_factory=session_factory)
        self.order_panel = OrderPanel(session_factory=session_factory)
        self.delivery_note_panel = DeliveryNotePanel(session_factory=session_factory)
        self.invoice_panel = InvoicePanel(session_factory=session_factory)
        self.return_invoice_panel = ReturnInvoicePanel(session_factory=session_factory)
        self.customer_panel = CustomerPanel(session_factory=session_factory)
        self.product_panel = ProductPanel(session_factory=session_factory)
        self.open_items_panel = ReportPanel(session_factory=session_factory)
        self.document_archive_panel = DocumentArchivePanel(session_factory=session_factory)
        self.settings_panel = SettingsPanel(session_factory=session_factory)
        self.checklist_panel = ChecklistPanel(session_factory=session_factory)
        self.management_home_panel = ManagementHomePanel()
        self.work_workspace = self._work_workspace()
        self.management_workspace = self._management_workspace()
        self._loaded_management_panels: set[QWidget] = set()
        self.refreshable_panels = {
            "Arbeiten": (self.refresh_active_work_panel,),
            "Rechnungen": (self.open_items_panel.refresh_all_lists,),
            "Verwaltung": (self.refresh_active_management_panel,),
        }

        self.customer_folder_panel.new_order_requested.connect(self.open_new_order_for_customer)
        self.customer_folder_panel.delivery_note_requested.connect(self.open_delivery_note_for_order)
        self.customer_folder_panel.invoice_requested.connect(self.open_invoice_for_order)
        self.order_panel.delivery_note_requested.connect(self.open_delivery_note_for_order)
        self.order_panel.invoice_requested.connect(self.open_invoice_for_order)
        self.document_archive_panel.document_open_requested.connect(self.open_document_from_archive)
        self.document_archive_panel.order_open_requested.connect(self.open_order_for_id)
        self.work_start_panel.customer_search_requested.connect(self.open_customer_folder_tab)
        self.work_start_panel.customer_selected.connect(self.open_customer_focus)
        self.work_start_panel.return_selected.connect(self.open_return_for_order)
        self.return_invoice_panel.document_created.connect(self.open_work_start_tab)
        self.management_home_panel.route_requested.connect(self.open_management_section)

        app_shell = QWidget()
        app_shell.setObjectName("appShell")
        shell_layout = QHBoxLayout(app_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        self.navigation = SidebarNavigation(MAIN_TABS)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._scrollable_tab(self.work_workspace))
        self.pages.addWidget(self._scrollable_tab(self.open_items_panel))
        self.pages.addWidget(self._scrollable_tab(self.management_workspace))
        self.navigation.currentRowChanged.connect(self.show_main_page)
        self.navigation.currentRowChanged.connect(self.refresh_current_tab)
        self.management_workspace.currentChanged.connect(self.refresh_active_management_panel)
        shell_layout.addWidget(self.navigation)
        shell_layout.addWidget(self.pages, 1)
        root_layout.addWidget(app_shell, 1)
        self.setCentralWidget(root)

    def open_customer_folder_tab(self) -> None:
        self.work_workspace.setCurrentWidget(self.customer_folder_panel)
        self.navigation.setCurrentRow(MAIN_TABS.index("Arbeiten"))

    def open_customer_focus(self, customer_id: int) -> None:
        self.work_workspace.setCurrentWidget(self.customer_folder_panel)
        self.navigation.setCurrentRow(MAIN_TABS.index("Arbeiten"))
        self.customer_folder_panel.customer_select.select_value(customer_id)
        self.customer_folder_panel.load_selected_customer()

    def open_work_start_tab(self) -> None:
        self.work_workspace.setCurrentWidget(self.work_start_panel)
        self.work_start_panel.refresh()
        self.navigation.setCurrentRow(MAIN_TABS.index("Arbeiten"))

    def open_open_items_tab(self) -> None:
        self.navigation.setCurrentRow(MAIN_TABS.index("Rechnungen"))

    def open_checklist_tab(self) -> None:
        self.navigation.setCurrentRow(MAIN_TABS.index("Verwaltung"))
        self.management_workspace.setCurrentWidget(self.checklist_panel)

    def open_orders_tab(self) -> None:
        self.work_workspace.setCurrentWidget(self.order_panel)
        self.navigation.setCurrentRow(MAIN_TABS.index("Arbeiten"))

    def show_main_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        if index == MAIN_TABS.index("Verwaltung"):
            self.management_workspace.setCurrentWidget(self.management_home_panel)

    def open_management_section(self, section: str) -> None:
        panels = {
            "Kunden": self.customer_panel,
            "Artikel": self.product_panel,
            "Prüfpunkte": self.checklist_panel,
            "Import": self.settings_panel,
            "Belegarchiv": self.document_archive_panel,
        }
        panel = panels.get(section)
        if panel is None:
            return
        self.management_workspace.setCurrentWidget(panel)
        self.refresh_active_management_panel()

    def open_new_order_dialog(self) -> None:
        self.open_orders_tab()
        self.order_panel.open_new_order_dialog()

    def open_new_order_for_customer(self, customer_id: int) -> None:
        self.open_orders_tab()
        self.order_panel.open_new_order_for_customer(customer_id)

    def open_order_for_id(self, order_id: int) -> None:
        self.open_orders_tab()
        self.order_panel.load_order_by_id(order_id)

    def open_invoices_tab(self) -> None:
        self.open_open_items_tab()

    def open_delivery_note_for_order(self, order_id: int) -> None:
        self.open_orders_tab()
        self._open_document_dialog(DeliveryNotePanel, order_id, "Lieferschein erstellen")

    def open_invoice_for_order(self, order_id: int) -> None:
        self.open_orders_tab()
        self._open_document_dialog(InvoicePanel, order_id, "Rechnung erstellen")

    def open_return_for_order(self, order_id: int) -> None:
        self.work_workspace.setCurrentWidget(self.return_invoice_panel)
        self.navigation.setCurrentRow(MAIN_TABS.index("Arbeiten"))
        self.return_invoice_panel.select_order(order_id)

    def _open_document_dialog(self, panel_class, order_id: int, title: str) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        dialog.resize(1120, 760)
        layout = QVBoxLayout(dialog)
        panel = panel_class(session_factory=self.session_factory)
        layout.addWidget(panel)
        panel.select_order(order_id)
        dialog.finished.connect(lambda _result, active_dialog=dialog: self._forget_document_dialog(active_dialog))
        self.document_dialogs.append(dialog)
        dialog.show()

    def _forget_document_dialog(self, dialog: QDialog) -> None:
        if dialog in self.document_dialogs:
            self.document_dialogs.remove(dialog)

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

    def refresh_active_work_panel(self, _index: int | None = None) -> None:
        current_panel = self.work_workspace.currentWidget()
        refresh_handlers = {
            self.work_start_panel: (self.work_start_panel.refresh,),
            self.customer_folder_panel: (self.customer_folder_panel.refresh_customers,),
            self.order_panel: (self.order_panel.refresh_orders,),
            self.return_invoice_panel: (self.return_invoice_panel.refresh_orders,),
        }
        for refresh in refresh_handlers.get(current_panel, ()):
            refresh()

    def refresh_active_management_panel(self, _index: int | None = None) -> None:
        current_panel = self.management_workspace.currentWidget()
        if current_panel in self._loaded_management_panels:
            return
        if hasattr(current_panel, "ensure_loaded"):
            current_panel.ensure_loaded()
            self._loaded_management_panels.add(current_panel)
            return
        refresh_handlers = {
            self.customer_panel: (self.customer_panel.refresh_customers,),
            self.product_panel: (self.product_panel.refresh_products,),
            self.checklist_panel: (self.checklist_panel.refresh_products, self.checklist_panel.refresh_issues),
            self.document_archive_panel: (self.document_archive_panel.refresh_archive,),
        }
        for refresh in refresh_handlers.get(current_panel, ()):
            refresh()
        self._loaded_management_panels.add(current_panel)

    def _scrollable_tab(self, panel: QWidget) -> QScrollArea:
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(panel)
        return scroll_area

    def _work_workspace(self) -> QStackedWidget:
        self.work_workspace = QStackedWidget()
        self.work_workspace.setObjectName("workStateStack")
        self.work_workspace.addWidget(self.work_start_panel)
        self.work_workspace.addWidget(self.customer_folder_panel)
        self.work_workspace.addWidget(self.order_panel)
        self.work_workspace.addWidget(self.return_invoice_panel)
        self.work_workspace.currentChanged.connect(self.refresh_active_work_panel)
        return self.work_workspace

    def _management_workspace(self) -> QStackedWidget:
        stack = QStackedWidget()
        stack.setObjectName("managementStateStack")
        stack.addWidget(self.management_home_panel)
        stack.addWidget(self.customer_panel)
        stack.addWidget(self.product_panel)
        stack.addWidget(self.checklist_panel)
        stack.addWidget(self.settings_panel)
        stack.addWidget(self.document_archive_panel)
        return stack

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
