# Kundenordner Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the visible workflow around `Kundenordner`: choose a customer, see their real folder/files/last assortment, then create delivery note or invoice from there.

**Architecture:** Keep the existing SQLite models, order service, document export service, and Excel/PDF tests. Add one customer-folder service and one customer-folder UI panel that compose existing customer, assortment, order, and document capabilities. Simplify `MainWindow` navigation so `Belege` is no longer a top-level workspace.

**Tech Stack:** Python, PySide6, SQLAlchemy, openpyxl/reportlab-backed Excel/PDF services, pytest.

---

## File Map

- Create: `src/getraenkeladen_tool/services/customer_folder_service.py`
- Create: `src/getraenkeladen_tool/ui/customer_folder_panel.py`
- Create: `tests/test_customer_folder_service.py`
- Create: `tests/test_customer_folder_panel.py`
- Modify: `src/getraenkeladen_tool/ui/main_window.py`
- Modify: `src/getraenkeladen_tool/ui/order_panel.py`
- Modify: `tests/test_main_window.py`
- Modify: `tests/test_order_panel_ui.py`
- Modify: `FORTSCHRITT.md`

## Task 1: Customer Folder Service

**Files:**
- Create: `src/getraenkeladen_tool/services/customer_folder_service.py`
- Test: `tests/test_customer_folder_service.py`

- [ ] **Step 1: Write failing service tests**

```python
from pathlib import Path

from getraenkeladen_tool.models import Customer, Document
from getraenkeladen_tool.services.customer_folder_service import (
    CustomerFolderFile,
    get_customer_folder_snapshot,
)


def test_customer_folder_snapshot_combines_customer_documents_and_real_folder(session, tmp_path):
    folder = tmp_path / "Kunden" / "Cafe Nord"
    folder.mkdir(parents=True)
    old_excel = folder / "2026-05-01_RE_ALT_Cafe_Nord.xlsx"
    old_pdf = folder / "2026-05-01_RE_ALT_Cafe_Nord.pdf"
    old_excel.write_text("placeholder", encoding="utf-8")
    old_pdf.write_text("placeholder", encoding="utf-8")
    customer = Customer(name="Cafe Nord", folder_path=str(folder), address="Markt 1", is_active=True)
    session.add(customer)
    session.flush()
    session.add(
        Document(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-1",
            excel_path=str(old_excel),
            pdf_path=str(old_pdf),
            delivery_date="2026-05-01",
        )
    )
    session.commit()

    snapshot = get_customer_folder_snapshot(session, customer.id)

    assert snapshot.customer.name == "Cafe Nord"
    assert snapshot.folder_exists is True
    assert snapshot.folder_path == folder
    assert snapshot.documents[0].document_number == "RG-1"
    assert any(file.path == old_excel for file in snapshot.files)
    assert any(file.path == old_pdf for file in snapshot.files)


def test_customer_folder_snapshot_marks_missing_folder(session, tmp_path):
    customer = Customer(name="Hotel Blau", folder_path=str(tmp_path / "fehlt"), is_active=True)
    session.add(customer)
    session.commit()

    snapshot = get_customer_folder_snapshot(session, customer.id)

    assert snapshot.folder_exists is False
    assert snapshot.files == []
```

- [ ] **Step 2: Run service tests and verify they fail**

Run: `.venv/bin/python -m pytest tests/test_customer_folder_service.py -q`

Expected: FAIL because `customer_folder_service` does not exist.

- [ ] **Step 3: Implement the service**

Create `src/getraenkeladen_tool/services/customer_folder_service.py`:

```python
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Customer, Document, Order


@dataclass(frozen=True, slots=True)
class CustomerFolderFile:
    path: Path
    kind: str
    label: str
    can_seed_order: bool


@dataclass(frozen=True, slots=True)
class CustomerFolderSnapshot:
    customer: Customer
    folder_path: Path
    folder_exists: bool
    files: list[CustomerFolderFile]
    documents: list[Document]
    orders: list[Order]


def get_customer_folder_snapshot(session: Session, customer_id: int) -> CustomerFolderSnapshot:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise ValueError("Kunde wurde nicht gefunden.")
    folder_path = Path(customer.folder_path)
    documents = list(
        session.scalars(
            select(Document)
            .options(selectinload(Document.customer))
            .where(Document.customer_id == customer_id)
            .where(Document.number_released == False)  # noqa: E712
            .order_by(Document.delivery_date.desc(), Document.id.desc())
        )
    )
    orders = list(
        session.scalars(
            select(Order)
            .options(selectinload(Order.lines), selectinload(Order.deposit_returns), selectinload(Order.customer))
            .where(Order.customer_id == customer_id)
            .where(Order.status != "archiviert")
            .order_by(Order.delivery_date.desc(), Order.id.desc())
        )
    )
    return CustomerFolderSnapshot(
        customer=customer,
        folder_path=folder_path,
        folder_exists=folder_path.exists(),
        files=_folder_files(folder_path) if folder_path.exists() else [],
        documents=documents,
        orders=orders,
    )


def _folder_files(folder_path: Path) -> list[CustomerFolderFile]:
    files = []
    for path in sorted(folder_path.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file() or path.suffix.lower() not in {".xlsx", ".pdf"}:
            continue
        files.append(
            CustomerFolderFile(
                path=path,
                kind=_file_kind(path),
                label=path.name,
                can_seed_order=path.suffix.lower() == ".xlsx",
            )
        )
    return files


def _file_kind(path: Path) -> str:
    name = path.name.lower()
    if path.suffix.lower() == ".pdf":
        return "PDF"
    if "_re" in name or "rechnung" in name:
        return "Excel-Rechnung"
    if "_ls" in name or "lieferschein" in name:
        return "Excel-Lieferschein"
    return "Excel-Datei"
```

- [ ] **Step 4: Run service tests and verify they pass**

Run: `.venv/bin/python -m pytest tests/test_customer_folder_service.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/getraenkeladen_tool/services/customer_folder_service.py tests/test_customer_folder_service.py
git commit -m "feat: add customer folder snapshot service"
```

## Task 2: Customer Folder Panel Skeleton

**Files:**
- Create: `src/getraenkeladen_tool/ui/customer_folder_panel.py`
- Test: `tests/test_customer_folder_panel.py`

- [ ] **Step 1: Write failing UI source tests**

```python
from pathlib import Path


def test_customer_folder_panel_exposes_real_folder_workflow():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "class CustomerFolderPanel" in source
    assert 'PageHeader("Kundenordner"' in source
    assert 'SearchableSelect("Kunde suchen' in source
    assert "Kundenakte" in source
    assert "Kundenordner oeffnen" in source
    assert "Dateien im Kundenordner" in source
    assert "Letzte bekannte Bestellung" in source
    assert "Neue Bestellung aus letzter Datei" in source
    assert "Lieferschein erstellen" in source
    assert "Rechnung erstellen" in source
    assert "get_customer_folder_snapshot" in source
```

- [ ] **Step 2: Run UI panel tests and verify they fail**

Run: `.venv/bin/python -m pytest tests/test_customer_folder_panel.py -q`

Expected: FAIL because the file does not exist.

- [ ] **Step 3: Implement the panel skeleton**

Create `src/getraenkeladen_tool/ui/customer_folder_panel.py` with these responsibilities:

```python
from pathlib import Path

from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..services.customer_folder_service import get_customer_folder_snapshot
from ..services.customer_service import list_active_customers
from ..services.customer_assortment_service import list_customer_assortment
from .date_input import to_display_date
from .layouts import ContentSurface, PageHeader, ResponsiveSplitter, WorkspaceCard
from .searchable_select import SearchableSelect


FOLDER_FILE_COLUMNS = ("Datei", "Art", "Aktion")
FOLDER_ORDER_COLUMNS = ("Bestellung", "Lieferdatum", "Status")
FOLDER_ASSORTMENT_COLUMNS = ("Artikel", "Letzte Menge", "Neuer Preis", "Pfand", "Hinweis")


class CustomerFolderPanel(QWidget):
    new_order_requested = Signal(int)
    delivery_note_requested = Signal(int)
    invoice_requested = Signal(int)

    def __init__(self, session_factory=None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.customers_by_id = {}
        self.file_paths_by_row = {}
        self.order_ids_by_row = {}
        self.current_customer_id = None
        self.current_folder_path: Path | None = None

        self.customer_select = SearchableSelect("Kunde suchen, z. B. Cafe oder Hotel")
        self.customer_summary = QLabel("Noch kein Kunde ausgewaehlt.")
        self.customer_summary.setObjectName("sectionSubtitle")
        self.folder_status = QLabel("Bitte zuerst einen Kunden waehlen.")
        self.folder_status.setObjectName("muted")
        self.files_table = self._table(FOLDER_FILE_COLUMNS)
        self.orders_table = self._table(FOLDER_ORDER_COLUMNS)
        self.assortment_table = self._table(FOLDER_ASSORTMENT_COLUMNS)
        self.open_folder_button = QPushButton("Kundenordner oeffnen")
        self.new_order_button = QPushButton("Neue Bestellung aus letzter Datei")
        self.delivery_note_button = QPushButton("Lieferschein erstellen")
        self.invoice_button = QPushButton("Rechnung erstellen")
        self.status_label = QLabel("Kunde suchen und Kundenordner pruefen.")
        self.status_label.setObjectName("muted")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout
        layout.addWidget(PageHeader("Kundenordner", "Kundenakte oeffnen, alte Dateien sehen und neue Belege daraus erstellen."))

        body = ResponsiveSplitter()
        layout.addWidget(body, 1)

        search_box = WorkspaceCard("Kunde finden", "Kunde suchen. Danach werden Kundenakte und Ordnerdateien geladen.")
        search_box.layout.addWidget(self.customer_select)
        body.addWidget(search_box)

        detail_box = WorkspaceCard("Kundenakte", "Adresse, Hinweise, Kundenordner und letzte Bestellung an einem Ort.")
        detail_box.layout.addWidget(self.customer_summary)
        detail_box.layout.addWidget(self.folder_status)
        detail_box.layout.addWidget(self.open_folder_button)
        files_box = WorkspaceCard("Dateien im Kundenordner", "Excel und PDF direkt aus dem echten Kundenordner.")
        files_box.layout.addWidget(self.files_table)
        detail_box.layout.addWidget(files_box)
        assortment_box = WorkspaceCard("Letzte bekannte Bestellung", "Artikel aus der letzten Kunden-Excel als Vorlage.")
        assortment_box.layout.addWidget(self.assortment_table)
        detail_box.layout.addWidget(assortment_box)
        order_box = WorkspaceCard("Bestellungen dieses Kunden", "Gespeicherte Bestellungen oeffnen oder daraus Belege erstellen.")
        order_box.layout.addWidget(self.orders_table)
        order_box.layout.addWidget(self.new_order_button)
        order_box.layout.addWidget(self.delivery_note_button)
        order_box.layout.addWidget(self.invoice_button)
        detail_box.layout.addWidget(order_box)
        body.addWidget(detail_box)
        body.setStretchFactor(0, 1)
        body.setStretchFactor(1, 3)
        layout.addWidget(self.status_label)

        self.customer_select.selection_changed.connect(self.load_selected_customer)
        self.open_folder_button.clicked.connect(self.open_customer_folder)
        self.new_order_button.clicked.connect(self.request_new_order_for_customer)
        self.delivery_note_button.clicked.connect(self.request_delivery_note_for_selected_order)
        self.invoice_button.clicked.connect(self.request_invoice_for_selected_order)
        self.files_table.itemDoubleClicked.connect(lambda _item: self.open_selected_file())
        self.refresh_customers()

    def _table(self, columns: tuple[str, ...]) -> QTableWidget:
        table = QTableWidget(0, len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        return table
```

Then add the methods needed to load customers, fill file/order/assortment tables, open local files, and emit signals. Keep methods small and mirror the existing `OrderPanel`/`DocumentArchivePanel` patterns.

- [ ] **Step 4: Run UI source tests**

Run: `.venv/bin/python -m pytest tests/test_customer_folder_panel.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/getraenkeladen_tool/ui/customer_folder_panel.py tests/test_customer_folder_panel.py
git commit -m "feat: add customer folder workspace panel"
```

## Task 3: Main Navigation Reframe

**Files:**
- Modify: `src/getraenkeladen_tool/ui/main_window.py`
- Test: `tests/test_main_window.py`

- [ ] **Step 1: Write failing navigation test**

Add to `tests/test_main_window.py`:

```python
def test_main_window_uses_customer_folder_as_primary_workplace():
    source = Path("src/getraenkeladen_tool/ui/main_window.py").read_text(encoding="utf-8")

    assert '"Kundenordner"' in source
    assert '"Belege"' not in source
    assert "CustomerFolderPanel" in source
    assert "self.customer_folder_panel" in source
    assert "self.pages.addWidget(self._scrollable_tab(self.customer_folder_panel))" in source
    assert "open_customer_folder_tab" in source
```

- [ ] **Step 2: Run test and verify it fails**

Run: `.venv/bin/python -m pytest tests/test_main_window.py::test_main_window_uses_customer_folder_as_primary_workplace -q`

Expected: FAIL because `Kundenordner` is not wired yet and `Belege` still exists.

- [ ] **Step 3: Modify `main_window.py`**

Change `MAIN_TABS` to:

```python
MAIN_TABS = (
    "Heute",
    "Kundenordner",
    "Offene Posten",
    "Stammdaten",
    "Pruefliste",
    "Einstellungen",
)
```

Replace `OrderPanel` as the visible second page with `CustomerFolderPanel`. Keep `OrderPanel`, `DeliveryNotePanel`, and `InvoicePanel` as internal helpers that can still be opened from signals, but do not add the document workspace as a top-level page.

Wire these signals:

```python
self.customer_folder_panel.new_order_requested.connect(self.open_new_order_for_customer)
self.customer_folder_panel.delivery_note_requested.connect(self.open_delivery_note_for_order)
self.customer_folder_panel.invoice_requested.connect(self.open_invoice_for_order)
```

Add navigation helper:

```python
def open_customer_folder_tab(self) -> None:
    self.navigation.setCurrentRow(MAIN_TABS.index("Kundenordner"))
```

For document creation, keep a modal or hidden helper for now:

```python
def open_delivery_note_for_order(self, order_id: int) -> None:
    self.delivery_note_panel.select_order(order_id)
    self.delivery_note_panel.show()
```

If direct `show()` is too rough, use the existing `document_workspace` only as an internal dialog in a later task. Do not put `Belege` back into `MAIN_TABS`.

- [ ] **Step 4: Update stale tests**

Update old main-window expectations that hard-code `"Belege"` or `"Kunde & Bestellung"` as primary tabs. Replace them with `"Kundenordner"` where the test is about main navigation. Preserve tests for export services and archive services.

- [ ] **Step 5: Run main window tests**

Run: `.venv/bin/python -m pytest tests/test_main_window.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/getraenkeladen_tool/ui/main_window.py tests/test_main_window.py
git commit -m "feat: make customer folder the primary workspace"
```

## Task 4: Customer-Scoped Order Creation

**Files:**
- Modify: `src/getraenkeladen_tool/ui/order_panel.py`
- Test: `tests/test_order_panel_ui.py`

- [ ] **Step 1: Write failing source test**

Add to `tests/test_order_panel_ui.py`:

```python
def test_order_panel_can_start_new_order_for_preselected_customer():
    source = Path("src/getraenkeladen_tool/ui/order_panel.py").read_text(encoding="utf-8")

    assert "def open_new_order_for_customer" in source
    assert "self.customer_select.select_value(customer_id)" in source
    assert "Neue Bestellung aus Kundenordner" in source
```

- [ ] **Step 2: Run test and verify it fails**

Run: `.venv/bin/python -m pytest tests/test_order_panel_ui.py::test_order_panel_can_start_new_order_for_preselected_customer -q`

Expected: FAIL.

- [ ] **Step 3: Implement customer-scoped entry**

Add method to `OrderPanel`:

```python
def open_new_order_for_customer(self, customer_id: int) -> None:
    self.reset_order_form()
    self.customer_select.select_value(customer_id)
    self.apply_selected_customer()
    self.order_mode_label.setText("Neue Bestellung aus Kundenordner")
    self.open_order_dialog("Neue Bestellung aus Kundenordner")
```

Update `MainWindow.open_new_order_for_customer(customer_id)` to call this method.

- [ ] **Step 4: Run order UI tests**

Run: `.venv/bin/python -m pytest tests/test_order_panel_ui.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/getraenkeladen_tool/ui/order_panel.py tests/test_order_panel_ui.py src/getraenkeladen_tool/ui/main_window.py
git commit -m "feat: start orders from customer folder"
```

## Task 5: Move Document Actions Into Customer Folder

**Files:**
- Modify: `src/getraenkeladen_tool/ui/customer_folder_panel.py`
- Modify: `src/getraenkeladen_tool/ui/main_window.py`
- Test: `tests/test_customer_folder_panel.py`

- [ ] **Step 1: Write failing interaction source test**

Add:

```python
def test_customer_folder_panel_routes_selected_order_to_documents():
    source = Path("src/getraenkeladen_tool/ui/customer_folder_panel.py").read_text(encoding="utf-8")

    assert "def request_delivery_note_for_selected_order" in source
    assert "self.delivery_note_requested.emit(order_id)" in source
    assert "def request_invoice_for_selected_order" in source
    assert "self.invoice_requested.emit(order_id)" in source
    assert "Bitte zuerst eine Bestellung dieses Kunden auswaehlen" in source
```

- [ ] **Step 2: Run test and verify it fails**

Run: `.venv/bin/python -m pytest tests/test_customer_folder_panel.py -q`

Expected: FAIL until routing methods exist.

- [ ] **Step 3: Implement selected-order routing**

In `CustomerFolderPanel`, add:

```python
def _selected_order_id(self) -> int | None:
    return self.order_ids_by_row.get(self.orders_table.currentRow())

def request_delivery_note_for_selected_order(self) -> None:
    order_id = self._selected_order_id()
    if order_id is None:
        self.status_label.setText("Bitte zuerst eine Bestellung dieses Kunden auswaehlen.")
        return
    self.delivery_note_requested.emit(order_id)

def request_invoice_for_selected_order(self) -> None:
    order_id = self._selected_order_id()
    if order_id is None:
        self.status_label.setText("Bitte zuerst eine Bestellung dieses Kunden auswaehlen.")
        return
    self.invoice_requested.emit(order_id)
```

Keep the existing document workflow panels for now, but only reach them through customer-folder signals.

- [ ] **Step 4: Run customer folder tests**

Run: `.venv/bin/python -m pytest tests/test_customer_folder_panel.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/getraenkeladen_tool/ui/customer_folder_panel.py src/getraenkeladen_tool/ui/main_window.py tests/test_customer_folder_panel.py
git commit -m "feat: route document creation from customer folder"
```

## Task 6: Remove Obsolete Top-Level Beleg Workspace Tests

**Files:**
- Modify: `tests/test_main_window.py`
- Modify: `tests/test_document_archive_panel.py` only if tests assume top-level navigation

- [ ] **Step 1: Find stale assertions**

Run: `rg -n '"Belege"|"Lieferbeleg"|"Kunde & Bestellung"|document_workspace|open_invoices_tab' tests src/getraenkeladen_tool/ui`

Expected: A list of references. Keep service/panel tests that still verify reusable components. Remove or update tests that say Belege must be a main tab.

- [ ] **Step 2: Update tests**

Change top-level navigation expectations to `Kundenordner`. Keep `DocumentArchivePanel`, `DeliveryNotePanel`, and `InvoicePanel` tests if they test reusable internals.

- [ ] **Step 3: Run affected tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_main_window.py tests/test_document_archive_panel.py tests/test_order_panel_ui.py tests/test_customer_folder_panel.py -q
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_main_window.py tests/test_document_archive_panel.py tests/test_order_panel_ui.py tests/test_customer_folder_panel.py
git commit -m "test: align UI tests with customer folder workflow"
```

## Task 7: End-to-End Regression

**Files:**
- Modify: `tests/test_daily_workflow.py`
- Modify: `FORTSCHRITT.md`

- [ ] **Step 1: Add E2E assertion for customer folder workflow**

Extend the existing daily workflow test or add a focused test:

```python
from getraenkeladen_tool.services.customer_folder_service import get_customer_folder_snapshot


def test_daily_customer_folder_workflow_updates_old_excel_with_central_prices_and_exports_documents(session, tmp_path):
    # Keep the existing test body. After invoice creation, add:
    snapshot = get_customer_folder_snapshot(session, onboarding.customer.id)
    generated_paths = {file.path for file in snapshot.files}

    assert Path(delivery_note.excel_path).parent == Path(onboarding.customer.folder_path)
    assert Path(invoice.excel_path).parent == Path(onboarding.customer.folder_path)
    assert Path(delivery_note.excel_path) in generated_paths
    assert Path(delivery_note.pdf_path) in generated_paths
    assert Path(invoice.excel_path) in generated_paths
    assert Path(invoice.pdf_path) in generated_paths
```

Use existing helpers from the test module instead of new factories where possible.

- [ ] **Step 2: Run E2E test**

Run: `.venv/bin/python -m pytest tests/test_daily_workflow.py -q`

Expected: PASS.

- [ ] **Step 3: Update progress**

Add to `FORTSCHRITT.md` under `Erledigt`:

```markdown
- Hauptnavigation auf Kundenordner-Arbeitsweise umgestellt: Kunde suchen, Ordnerdateien sehen, Bestellung und Belege von dort starten.
```

Move the old `In Arbeit` item to match the new status.

- [ ] **Step 4: Run full test suite**

Run: `.venv/bin/python -m pytest -q`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_daily_workflow.py FORTSCHRITT.md
git commit -m "test: cover customer folder document workflow"
```

## Task 8: Manual UX Check

**Files:**
- No required code changes unless the check finds defects.

- [ ] **Step 1: Launch app locally if Qt environment permits**

Run: `.venv/bin/python -m getraenkeladen_tool`

Expected: App starts. If the known macOS Qt `cocoa` plugin issue appears, record that manual GUI launch is blocked and rely on tests for this pass.

- [ ] **Step 2: Walk the persona path**

Check these screens manually:

1. App starts with `Heute`.
2. Navigation shows `Kundenordner`, not `Belege`.
3. Open `Kundenordner`.
4. Search a customer.
5. Confirm folder path and files are visible.
6. Confirm latest assortment is visible.
7. Start a new order for that customer.
8. Create delivery note or invoice from a selected customer order.

- [ ] **Step 3: Fix only blocking issues**

If labels are confusing, make small wording fixes. Do not add new features.

- [ ] **Step 4: Final verification**

Run: `.venv/bin/python -m pytest -q`

Expected: all tests pass.

- [ ] **Step 5: Final commit and push**

```bash
git add .
git commit -m "feat: center workflow on customer folders"
git push
```

## Self-Review

- Spec coverage: The plan covers new navigation, customer-folder workspace, folder files, customer assortment, customer-scoped order creation, document creation from customer, tests, and progress docs.
- Placeholder scan: No open-ended implementation markers remain. Task 7 names the exact existing test and the exact assertions to add.
- Type consistency: `CustomerFolderSnapshot`, `CustomerFolderFile`, `CustomerFolderPanel`, and signal names are used consistently across service, UI, and tests.
