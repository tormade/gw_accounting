from pathlib import Path

from getraenkeladen_tool.models import Customer, Document, Order
from getraenkeladen_tool.services.customer_folder_service import (
    CustomerFolderFile,
    get_customer_folder_snapshot,
)


def test_customer_folder_snapshot_combines_customer_documents_orders_and_real_folder_files(
    session,
    tmp_path: Path,
):
    folder = tmp_path / "Kunden" / "Cafe Nord"
    folder.mkdir(parents=True)
    old_excel = folder / "2026-05-01_RE_ALT_Cafe_Nord.xlsx"
    old_pdf = folder / "2026-05-01_RE_ALT_Cafe_Nord.pdf"
    ignored_text = folder / "notiz.txt"
    old_excel.write_text("placeholder", encoding="utf-8")
    old_pdf.write_text("placeholder", encoding="utf-8")
    ignored_text.write_text("ignored", encoding="utf-8")
    customer = Customer(name="Cafe Nord", folder_path=str(folder), address="Markt 1", is_active=True)
    other_customer = Customer(name="Hotel Blau", folder_path=str(tmp_path / "Hotel Blau"), is_active=True)
    session.add_all([customer, other_customer])
    session.flush()
    active_document = Document(
        customer_id=customer.id,
        document_type="Rechnung",
        document_number="RG-1",
        excel_path=str(old_excel),
        pdf_path=str(old_pdf),
        delivery_date="2026-05-01",
    )
    released_document = Document(
        customer_id=customer.id,
        document_type="Rechnung",
        document_number="RG-FREI",
        excel_path=str(old_excel),
        pdf_path=str(old_pdf),
        delivery_date="2026-05-02",
        number_released=True,
    )
    foreign_document = Document(
        customer_id=other_customer.id,
        document_type="Rechnung",
        document_number="RG-FREMD",
        excel_path=str(old_excel),
        pdf_path=str(old_pdf),
        delivery_date="2026-05-03",
    )
    active_order = Order(
        order_number="AUF-1",
        customer_id=customer.id,
        order_date="2026-05-01",
        delivery_date="2026-05-04",
        status="geplant",
    )
    archived_order = Order(
        order_number="AUF-ARCHIV",
        customer_id=customer.id,
        order_date="2026-05-01",
        delivery_date="2026-05-05",
        status="archiviert",
    )
    foreign_order = Order(
        order_number="AUF-FREMD",
        customer_id=other_customer.id,
        order_date="2026-05-01",
        delivery_date="2026-05-06",
        status="geplant",
    )
    session.add_all(
        [
            active_document,
            released_document,
            foreign_document,
            active_order,
            archived_order,
            foreign_order,
        ]
    )
    session.commit()

    snapshot = get_customer_folder_snapshot(session, customer.id)

    assert snapshot.customer.name == "Cafe Nord"
    assert snapshot.folder_exists is True
    assert snapshot.folder_path == folder
    assert [document.document_number for document in snapshot.documents] == ["RG-1"]
    assert [order.order_number for order in snapshot.orders] == ["AUF-1"]
    assert CustomerFolderFile(old_excel, "Excel-Rechnung", old_excel.name, True) in snapshot.files
    assert CustomerFolderFile(old_pdf, "PDF", old_pdf.name, False) in snapshot.files
    assert all(file.path != ignored_text for file in snapshot.files)
    assert next(file for file in snapshot.files if file.path == old_excel).can_seed_order is True
    assert next(file for file in snapshot.files if file.path == old_pdf).can_seed_order is False


def test_customer_folder_snapshot_marks_missing_folder_and_returns_empty_files(session, tmp_path: Path):
    customer = Customer(name="Hotel Blau", folder_path=str(tmp_path / "fehlt"), is_active=True)
    session.add(customer)
    session.commit()

    snapshot = get_customer_folder_snapshot(session, customer.id)

    assert snapshot.folder_exists is False
    assert snapshot.files == []
