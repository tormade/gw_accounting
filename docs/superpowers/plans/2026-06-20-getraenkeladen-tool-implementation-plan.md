# Getraenkeladen Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Windows desktop app that manages customer and product master data, creates invoice and delivery-note Excel/PDF files, maintains an open-items list, and generates daily delivery and contact overviews while preserving the existing customer-folder workflow.

**Architecture:** Use a small Python desktop application with a PySide6 GUI, a local SQLite database for structured master data and workflow state, and a file-based document output layer that writes Excel and PDF artifacts into customer folders. Keep document generation isolated behind services so the UI, data model, and file output can evolve independently and a later ZUGFeRD extension can reuse the same structured document data.

**Tech Stack:** Python 3.12, PySide6, SQLite, SQLAlchemy, Alembic, Pydantic, openpyxl, reportlab, pytest, pytest-qt, pyinstaller

---

## Planned File Structure

- `pyproject.toml`
  Responsibility: project metadata, dependencies, lint/test scripts.
- `README.md`
  Responsibility: local setup, packaging, and operator notes.
- `src/getraenkeladen_tool/app.py`
  Responsibility: Qt application bootstrap.
- `src/getraenkeladen_tool/config.py`
  Responsibility: filesystem paths, environment settings, and default folders.
- `src/getraenkeladen_tool/db.py`
  Responsibility: SQLAlchemy engine, session factory, database bootstrap.
- `src/getraenkeladen_tool/models.py`
  Responsibility: ORM models for customers, products, documents, open items, and contacts.
- `src/getraenkeladen_tool/schemas.py`
  Responsibility: Pydantic request/response and validation models.
- `src/getraenkeladen_tool/services/customer_service.py`
  Responsibility: customer CRUD and validation.
- `src/getraenkeladen_tool/services/product_service.py`
  Responsibility: product CRUD and price defaults.
- `src/getraenkeladen_tool/services/document_service.py`
  Responsibility: invoice/delivery-note workflow and persistence.
- `src/getraenkeladen_tool/services/report_service.py`
  Responsibility: open-items, daily-delivery, and contact-due queries.
- `src/getraenkeladen_tool/services/file_service.py`
  Responsibility: folder creation, output paths, and file naming.
- `src/getraenkeladen_tool/services/excel_service.py`
  Responsibility: Excel file generation from templates.
- `src/getraenkeladen_tool/services/pdf_service.py`
  Responsibility: PDF rendering with letterhead.
- `src/getraenkeladen_tool/ui/main_window.py`
  Responsibility: primary navigation shell.
- `src/getraenkeladen_tool/ui/customer_panel.py`
  Responsibility: customer maintenance UI.
- `src/getraenkeladen_tool/ui/product_panel.py`
  Responsibility: product and price maintenance UI.
- `src/getraenkeladen_tool/ui/document_panel.py`
  Responsibility: invoice and delivery-note creation UI.
- `src/getraenkeladen_tool/ui/report_panel.py`
  Responsibility: open items, delivery list, and contact overview UI.
- `templates/rechnung_template.xlsx`
  Responsibility: invoice workbook template.
- `templates/lieferschein_template.xlsx`
  Responsibility: delivery-note workbook template.
- `templates/briefkopf.json`
  Responsibility: configurable PDF letterhead settings.
- `assets/brand/`
  Responsibility: provided Winklmeier logo files and brand assets for UI and document output.
- `tests/conftest.py`
  Responsibility: shared fixtures for temp directories, test DB, and Qt app.
- `tests/test_customer_service.py`
  Responsibility: customer CRUD and validation tests.
- `tests/test_product_service.py`
  Responsibility: product CRUD and price behavior tests.
- `tests/test_document_service.py`
  Responsibility: document creation and open-item side effects.
- `tests/test_excel_service.py`
  Responsibility: Excel artifact content and naming tests.
- `tests/test_pdf_service.py`
  Responsibility: PDF creation tests.
- `tests/test_report_service.py`
  Responsibility: report and filter tests.
- `tests/test_main_window.py`
  Responsibility: smoke test for the desktop UI.

### Task 1: Bootstrap The Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/getraenkeladen_tool/__init__.py`
- Create: `src/getraenkeladen_tool/app.py`
- Create: `tests/test_smoke.py`

- [ ] **Step 1: Write the failing smoke test**

```python
from getraenkeladen_tool.app import create_app


def test_create_app_returns_qapplication():
    app = create_app()
    assert app.applicationName() == "Getraenkeladen Tool"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_smoke.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'getraenkeladen_tool'`

- [ ] **Step 3: Write minimal project bootstrap**

```toml
[project]
name = "getraenkeladen-tool"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "PySide6>=6.8,<7",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3,<9",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
```

```python
from PySide6.QtWidgets import QApplication


def create_app() -> QApplication:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Getraenkeladen Tool")
    return app
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_smoke.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml README.md src/getraenkeladen_tool/__init__.py src/getraenkeladen_tool/app.py tests/test_smoke.py
git commit -m "chore: bootstrap desktop app project"
```

### Task 2: Add Local Configuration And Database Bootstrap

**Files:**
- Create: `src/getraenkeladen_tool/config.py`
- Create: `src/getraenkeladen_tool/db.py`
- Create: `tests/conftest.py`
- Create: `tests/test_db_bootstrap.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write the failing database bootstrap test**

```python
from pathlib import Path

from getraenkeladen_tool.config import AppConfig
from getraenkeladen_tool.db import bootstrap_database


def test_bootstrap_database_creates_sqlite_file(tmp_path: Path):
    config = AppConfig(base_dir=tmp_path)
    bootstrap_database(config)
    assert config.database_path.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_db_bootstrap.py -v`
Expected: FAIL with `ImportError` for missing `config` or `db` module

- [ ] **Step 3: Write minimal configuration and bootstrap code**

```toml
[project]
dependencies = [
  "PySide6>=6.8,<7",
  "SQLAlchemy>=2.0,<3",
]
```

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    base_dir: Path

    @property
    def database_path(self) -> Path:
        return self.base_dir / "data" / "getraenkeladen.db"
```

```python
from pathlib import Path

from sqlalchemy import create_engine

from .config import AppConfig


def bootstrap_database(config: AppConfig) -> None:
    db_path = config.database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    Path(db_path).touch(exist_ok=True)
    with engine.connect() as connection:
        connection.exec_driver_sql("select 1")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_db_bootstrap.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/getraenkeladen_tool/config.py src/getraenkeladen_tool/db.py tests/conftest.py tests/test_db_bootstrap.py
git commit -m "feat: add local configuration and db bootstrap"
```

### Task 3: Define Core Data Models For Customers, Products, Documents, And Open Items

**Files:**
- Create: `src/getraenkeladen_tool/models.py`
- Create: `tests/test_models.py`
- Modify: `src/getraenkeladen_tool/db.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write the failing model persistence test**

```python
from getraenkeladen_tool.models import Customer, Product


def test_customer_and_product_models_expose_required_fields():
    customer = Customer(name="Cafe Nord", folder_path="Kunden/Cafe Nord")
    product = Product(name="Wasser 0,7", unit="Kiste", standard_price_cents=1299)
    assert customer.name == "Cafe Nord"
    assert product.standard_price_cents == 1299
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL with `ImportError: cannot import name 'Customer'`

- [ ] **Step 3: Write minimal ORM models and metadata bootstrap**

```toml
[project]
dependencies = [
  "PySide6>=6.8,<7",
  "SQLAlchemy>=2.0,<3",
  "pydantic>=2.8,<3",
]
```

```python
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    folder_path: Mapped[str] = mapped_column(String(500))
    address: Mapped[str | None] = mapped_column(Text(), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    next_contact_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    delivery_notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    opening_hours: Mapped[str | None] = mapped_column(Text(), nullable=True)
    internal_notes: Mapped[str | None] = mapped_column(Text(), nullable=True)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    unit: Mapped[str] = mapped_column(String(50))
    standard_price_cents: Mapped[int] = mapped_column(Integer())
    article_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    document_type: Mapped[str] = mapped_column(String(30))
    document_number: Mapped[str] = mapped_column(String(50))
    excel_path: Mapped[str] = mapped_column(String(500))
    pdf_path: Mapped[str] = mapped_column(String(500))
    delivery_slot: Mapped[str | None] = mapped_column(String(30), nullable=True)

    customer: Mapped[Customer] = relationship()


class OpenItem(Base):
    __tablename__ = "open_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    customer_name: Mapped[str] = mapped_column(String(200))
    document_number: Mapped[str] = mapped_column(String(50))
    amount_cents: Mapped[int] = mapped_column(Integer())
    payment_method: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="offen")
```

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import AppConfig
from .models import Base


def bootstrap_database(config: AppConfig) -> None:
    db_path = config.database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)


def create_session_factory(config: AppConfig) -> sessionmaker:
    engine = create_engine(f"sqlite:///{config.database_path}")
    return sessionmaker(bind=engine)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/getraenkeladen_tool/models.py src/getraenkeladen_tool/db.py tests/test_models.py
git commit -m "feat: define core business models"
```

### Task 4: Implement Customer And Product Services With Validation

**Files:**
- Create: `src/getraenkeladen_tool/schemas.py`
- Create: `src/getraenkeladen_tool/services/customer_service.py`
- Create: `src/getraenkeladen_tool/services/product_service.py`
- Create: `tests/test_customer_service.py`
- Create: `tests/test_product_service.py`

- [ ] **Step 1: Write the failing customer and product service tests**

```python
from getraenkeladen_tool.schemas import CustomerCreate, ProductCreate
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.product_service import create_product


def test_create_customer_requires_name_and_folder(session):
    customer = create_customer(
        session,
        CustomerCreate(name="Hotel Blau", folder_path="Kunden/Hotel Blau"),
    )
    assert customer.name == "Hotel Blau"


def test_create_product_uses_cent_prices(session):
    product = create_product(
        session,
        ProductCreate(name="Cola", unit="Kiste", standard_price_cents=1899),
    )
    assert product.standard_price_cents == 1899
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_customer_service.py tests/test_product_service.py -v`
Expected: FAIL with missing schema or service imports

- [ ] **Step 3: Write minimal schemas and service implementations**

```python
from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1)
    folder_path: str = Field(min_length=1)
    address: str | None = None
    payment_method: str | None = None


class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    standard_price_cents: int = Field(ge=0)
```

```python
from sqlalchemy.orm import Session

from ..models import Customer
from ..schemas import CustomerCreate


def create_customer(session: Session, payload: CustomerCreate) -> Customer:
    customer = Customer(**payload.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer
```

```python
from sqlalchemy.orm import Session

from ..models import Product
from ..schemas import ProductCreate


def create_product(session: Session, payload: ProductCreate) -> Product:
    product = Product(**payload.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_customer_service.py tests/test_product_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/getraenkeladen_tool/schemas.py src/getraenkeladen_tool/services/customer_service.py src/getraenkeladen_tool/services/product_service.py tests/test_customer_service.py tests/test_product_service.py
git commit -m "feat: add customer and product services"
```

### Task 5: Implement File Output And Excel Generation

**Files:**
- Create: `src/getraenkeladen_tool/services/file_service.py`
- Create: `src/getraenkeladen_tool/services/excel_service.py`
- Create: `templates/rechnung_template.xlsx`
- Create: `templates/lieferschein_template.xlsx`
- Create: `tests/test_excel_service.py`

- [ ] **Step 1: Write the failing Excel generation test**

```python
from pathlib import Path

from getraenkeladen_tool.services.excel_service import build_invoice_workbook


def test_build_invoice_workbook_writes_customer_excel_file(tmp_path: Path):
    output_path = tmp_path / "Kunden" / "Cafe Nord" / "RG-1001.xlsx"
    build_invoice_workbook(
        output_path=output_path,
        customer_name="Cafe Nord",
        document_number="RG-1001",
        line_items=[{"name": "Wasser", "quantity": 10, "unit_price_cents": 1299}],
    )
    assert output_path.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_excel_service.py -v`
Expected: FAIL with missing `build_invoice_workbook`

- [ ] **Step 3: Write minimal file and Excel generation code**

```python
from pathlib import Path


def ensure_parent_folder(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
```

```python
from pathlib import Path

from openpyxl import Workbook

from .file_service import ensure_parent_folder


def build_invoice_workbook(
    output_path: Path,
    customer_name: str,
    document_number: str,
    line_items: list[dict],
) -> None:
    ensure_parent_folder(output_path)
    workbook = Workbook()
    sheet = workbook.active
    sheet["A1"] = "Rechnung"
    sheet["A2"] = customer_name
    sheet["A3"] = document_number
    row = 5
    for item in line_items:
        sheet[f"A{row}"] = item["name"]
        sheet[f"B{row}"] = item["quantity"]
        sheet[f"C{row}"] = item["unit_price_cents"] / 100
        row += 1
    workbook.save(output_path)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_excel_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/getraenkeladen_tool/services/file_service.py src/getraenkeladen_tool/services/excel_service.py templates/rechnung_template.xlsx templates/lieferschein_template.xlsx tests/test_excel_service.py
git commit -m "feat: generate excel invoice files"
```

### Task 6: Implement PDF Rendering With Letterhead

**Files:**
- Create: `src/getraenkeladen_tool/services/pdf_service.py`
- Create: `templates/briefkopf.json`
- Create: `tests/test_pdf_service.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write the failing PDF generation test**

```python
from pathlib import Path

from getraenkeladen_tool.services.pdf_service import build_invoice_pdf


def test_build_invoice_pdf_creates_pdf_file(tmp_path: Path):
    output_path = tmp_path / "Kunden" / "Cafe Nord" / "RG-1001.pdf"
    build_invoice_pdf(
        output_path=output_path,
        customer_name="Cafe Nord",
        document_number="RG-1001",
        line_items=[{"name": "Wasser", "quantity": 10, "unit_price_cents": 1299}],
    )
    assert output_path.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pdf_service.py -v`
Expected: FAIL with missing `build_invoice_pdf`

- [ ] **Step 3: Write minimal PDF rendering code**

```toml
[project]
dependencies = [
  "PySide6>=6.8,<7",
  "SQLAlchemy>=2.0,<3",
  "pydantic>=2.8,<3",
  "openpyxl>=3.1,<4",
  "reportlab>=4.2,<5",
]
```

```python
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .file_service import ensure_parent_folder


def build_invoice_pdf(
    output_path: Path,
    customer_name: str,
    document_number: str,
    line_items: list[dict],
) -> None:
    ensure_parent_folder(output_path)
    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.drawString(50, 800, "Rechnung")
    pdf.drawString(50, 785, f"Kunde: {customer_name}")
    pdf.drawString(50, 770, f"Nummer: {document_number}")
    y = 730
    for item in line_items:
        pdf.drawString(50, y, f"{item['name']} x{item['quantity']}")
        y -= 16
    pdf.save()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_pdf_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/getraenkeladen_tool/services/pdf_service.py templates/briefkopf.json tests/test_pdf_service.py
git commit -m "feat: generate invoice pdf files"
```

### Task 7: Implement Document Workflow And Automatic Open-Item Creation

**Files:**
- Create: `src/getraenkeladen_tool/services/document_service.py`
- Create: `tests/test_document_service.py`
- Modify: `src/getraenkeladen_tool/schemas.py`
- Modify: `src/getraenkeladen_tool/models.py`

- [ ] **Step 1: Write the failing document workflow test**

```python
from pathlib import Path

from getraenkeladen_tool.schemas import DocumentCreate
from getraenkeladen_tool.services.document_service import create_invoice_document


def test_create_invoice_document_writes_files_and_open_item(session, tmp_path: Path):
    payload = DocumentCreate(
        customer_id=1,
        document_number="RG-1001",
        document_type="invoice",
        output_root=str(tmp_path),
        line_items=[{"name": "Wasser", "quantity": 10, "unit_price_cents": 1299}],
    )
    result = create_invoice_document(session, payload)
    assert result.open_item_id is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_document_service.py -v`
Expected: FAIL with missing `DocumentCreate` or `create_invoice_document`

- [ ] **Step 3: Write minimal workflow implementation**

```python
from pydantic import BaseModel, Field


class DocumentLineItem(BaseModel):
    name: str
    quantity: int = Field(ge=1)
    unit_price_cents: int = Field(ge=0)


class DocumentCreate(BaseModel):
    customer_id: int
    document_number: str
    document_type: str
    output_root: str
    line_items: list[DocumentLineItem]


class DocumentResult(BaseModel):
    excel_path: str
    pdf_path: str
    open_item_id: int | None = None
```

```python
from pathlib import Path

from sqlalchemy.orm import Session

from ..models import Customer, Document, OpenItem
from ..schemas import DocumentCreate, DocumentResult
from .excel_service import build_invoice_workbook
from .pdf_service import build_invoice_pdf


def create_invoice_document(session: Session, payload: DocumentCreate) -> DocumentResult:
    customer = session.get(Customer, payload.customer_id)
    customer_dir = Path(payload.output_root) / customer.folder_path
    excel_path = customer_dir / f"{payload.document_number}.xlsx"
    pdf_path = customer_dir / f"{payload.document_number}.pdf"

    line_items = [item.model_dump() for item in payload.line_items]
    build_invoice_workbook(excel_path, customer.name, payload.document_number, line_items)
    build_invoice_pdf(pdf_path, customer.name, payload.document_number, line_items)

    document = Document(
        customer_id=customer.id,
        document_type=payload.document_type,
        document_number=payload.document_number,
        excel_path=str(excel_path),
        pdf_path=str(pdf_path),
    )
    session.add(document)
    session.flush()

    total_cents = sum(item.unit_price_cents * item.quantity for item in payload.line_items)
    open_item = OpenItem(
        document_id=document.id,
        customer_name=customer.name,
        document_number=payload.document_number,
        amount_cents=total_cents,
        payment_method=customer.payment_method or "unbekannt",
        status="offen",
    )
    session.add(open_item)
    session.commit()

    return DocumentResult(
        excel_path=str(excel_path),
        pdf_path=str(pdf_path),
        open_item_id=open_item.id,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_document_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/getraenkeladen_tool/schemas.py src/getraenkeladen_tool/services/document_service.py src/getraenkeladen_tool/models.py tests/test_document_service.py
git commit -m "feat: add invoice workflow and open item creation"
```

### Task 8: Implement Delivery, Contact, And Open-Item Reports

**Files:**
- Create: `src/getraenkeladen_tool/services/report_service.py`
- Create: `tests/test_report_service.py`
- Modify: `src/getraenkeladen_tool/models.py`

- [ ] **Step 1: Write the failing report tests**

```python
from getraenkeladen_tool.services.report_service import (
    list_due_contacts,
    list_open_items,
)


def test_list_open_items_returns_only_unpaid_entries(session):
    items = list_open_items(session)
    assert isinstance(items, list)


def test_list_due_contacts_filters_by_target_date(session):
    contacts = list_due_contacts(session, target_date="2026-06-20")
    assert isinstance(contacts, list)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_report_service.py -v`
Expected: FAIL with missing report service functions

- [ ] **Step 3: Write minimal report service implementation**

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Customer, OpenItem


def list_open_items(session: Session) -> list[OpenItem]:
    query = select(OpenItem).where(OpenItem.status == "offen")
    return list(session.scalars(query))


def list_due_contacts(session: Session, target_date: str) -> list[Customer]:
    query = select(Customer).where(Customer.next_contact_date == target_date)
    return list(session.scalars(query))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_report_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/getraenkeladen_tool/services/report_service.py tests/test_report_service.py src/getraenkeladen_tool/models.py
git commit -m "feat: add reporting queries for operations"
```

### Task 9: Build The Minimal Desktop UI

**Files:**
- Create: `src/getraenkeladen_tool/ui/main_window.py`
- Create: `src/getraenkeladen_tool/ui/customer_panel.py`
- Create: `src/getraenkeladen_tool/ui/product_panel.py`
- Create: `src/getraenkeladen_tool/ui/document_panel.py`
- Create: `src/getraenkeladen_tool/ui/report_panel.py`
- Create: `src/getraenkeladen_tool/ui/theme.py`
- Create: `assets/brand/README.md`
- Create: `tests/test_main_window.py`
- Modify: `src/getraenkeladen_tool/app.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write the failing UI smoke test**

```python
from getraenkeladen_tool.app import create_main_window


def test_main_window_exposes_core_tabs(qtbot):
    window = create_main_window()
    qtbot.addWidget(window)
    tab_titles = [window.tabs.tabText(index) for index in range(window.tabs.count())]
    assert tab_titles == ["Kunden", "Produkte", "Belege", "Listen"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_main_window.py -v`
Expected: FAIL with missing `create_main_window`

- [ ] **Step 3: Write minimal Qt main window and tabs**

```toml
[project.optional-dependencies]
dev = [
  "pytest>=8.3,<9",
  "pytest-qt>=4.4,<5",
]
```

```python
from PySide6.QtWidgets import QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.tabs = QTabWidget()
        self.tabs.addTab(self._panel("Kunden"), "Kunden")
        self.tabs.addTab(self._panel("Produkte"), "Produkte")
        self.tabs.addTab(self._panel("Belege"), "Belege")
        self.tabs.addTab(self._panel("Listen"), "Listen")
        self.setCentralWidget(self.tabs)

    def _panel(self, title: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel(title))
        return widget
```

```python
APP_STYLESHEET = """
QMainWindow {
    background: #f5f5f2;
}
QTabWidget::pane {
    border: 1px solid #d8d6cf;
}
QTabBar::tab:selected {
    background: #111111;
    color: #ffffff;
}
"""
```

```python
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.theme import APP_STYLESHEET


def create_app() -> QApplication:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("Getraenkeladen Tool")
    app.setStyleSheet(APP_STYLESHEET)
    return app


def create_main_window() -> MainWindow:
    create_app()
    return MainWindow()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_main_window.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/getraenkeladen_tool/ui/main_window.py src/getraenkeladen_tool/ui/customer_panel.py src/getraenkeladen_tool/ui/product_panel.py src/getraenkeladen_tool/ui/document_panel.py src/getraenkeladen_tool/ui/report_panel.py src/getraenkeladen_tool/ui/theme.py assets/brand/README.md src/getraenkeladen_tool/app.py tests/test_main_window.py
git commit -m "feat: add desktop navigation shell"
```

### Task 9a: Apply Winklmeier Brand Direction To UI And Documents

**Files:**
- Create: `assets/brand/README.md`
- Modify: `src/getraenkeladen_tool/ui/theme.py`
- Modify: `src/getraenkeladen_tool/services/pdf_service.py`
- Modify: `templates/briefkopf.json`
- Test: `tests/test_brand_assets.py`
- Test: `tests/test_pdf_service.py`
- Test: `tests/test_main_window.py`

- [ ] **Step 1: Write the failing brand asset note test**

```python
from pathlib import Path


def test_brand_readme_mentions_original_logo_requirement():
    text = Path("assets/brand/README.md").read_text(encoding="utf-8")
    assert "Originaldatei" in text
    assert "getraenke-winklmeier.de" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_brand_assets.py -v`
Expected: FAIL because `assets/brand/README.md` does not exist yet

- [ ] **Step 3: Add brand usage note**

```markdown
# Brand Assets

Use this folder for logo and brand assets provided by Getränke Winklmeier.

Reference: https://www.getraenke-winklmeier.de

Rules:

- Use the real logo only from an approved Originaldatei.
- Do not scrape or redraw the logo from the website for production use.
- Keep the app utilitarian and work-focused while matching the Winklmeier tone: familiar, regional, clear, service-oriented.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_brand_assets.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add assets/brand/README.md tests/test_brand_assets.py src/getraenkeladen_tool/ui/theme.py templates/briefkopf.json src/getraenkeladen_tool/services/pdf_service.py tests/test_pdf_service.py tests/test_main_window.py
git commit -m "feat: add winklmeier brand direction"
```

### Task 10: Package The App For Windows And Document Operator Workflow

**Files:**
- Modify: `README.md`
- Create: `scripts/package_windows.ps1`
- Create: `assets/app-icon.ico`
- Create: `tests/test_packaging_docs.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write the failing packaging documentation test**

```python
from pathlib import Path


def test_readme_mentions_windows_packaging():
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "pyinstaller" in readme.lower()
    assert "windows" in readme.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_packaging_docs.py -v`
Expected: FAIL because README lacks packaging guidance

- [ ] **Step 3: Write packaging docs and PowerShell wrapper**

```toml
[project.optional-dependencies]
dev = [
  "pytest>=8.3,<9",
  "pytest-qt>=4.4,<5",
  "pyinstaller>=6.10,<7",
]
```

```powershell
pyinstaller `
  --name GetraenkeladenTool `
  --windowed `
  --icon assets/app-icon.ico `
  --add-data "templates;templates" `
  src/getraenkeladen_tool/app.py
```

```markdown
## Windows Packaging

Use `pyinstaller` on a Windows machine to build the operator executable:

```powershell
pwsh -File scripts/package_windows.ps1
```

The resulting executable should be tested against:

- local SQLite storage creation
- customer-folder document output
- invoice PDF generation
- open-items updates
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_packaging_docs.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md scripts/package_windows.ps1 assets/app-icon.ico pyproject.toml tests/test_packaging_docs.py
git commit -m "chore: document windows packaging flow"
```

## Self-Review

### Spec coverage

- Customer master data: covered by Task 3 and Task 4.
- Product and price maintenance: covered by Task 3 and Task 4.
- Invoice and delivery-note generation: covered by Task 5, Task 6, and Task 7.
- Customer-folder output: covered by Task 5 and Task 7.
- Open items: covered by Task 3, Task 7, and Task 8.
- Daily delivery and contact overview: covered by Task 8 and Task 9.
- Local-only desktop architecture: covered by Task 1, Task 2, and Task 10.
- Later Windows packaging and rollout: covered by Task 10.

### Placeholder scan

No `TODO`, `TBD`, or unresolved “add later” instructions remain in the task steps.

### Type consistency

- `CustomerCreate`, `ProductCreate`, `DocumentCreate`, and `DocumentResult` are introduced before their service usage.
- `create_app()` and `create_main_window()` names are consistent between tests and implementation steps.
- `build_invoice_workbook()` and `build_invoice_pdf()` are reused consistently in document workflow tasks.
