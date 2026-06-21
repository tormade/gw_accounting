from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Customer, Document, Product
from ..schemas import CustomerCreate, DocumentCreate, DocumentLineItem, ProductCreate
from .customer_service import create_customer
from .document_service import create_document
from .product_service import create_product


@dataclass(slots=True)
class DemoSeedResult:
    created_customers: int
    created_products: int
    created_documents: int


def seed_demo_workflow(session: Session, base_output_dir: Path, target_date: str) -> DemoSeedResult:
    created_customers = _seed_customers(session, base_output_dir, target_date)
    created_products = _seed_products(session)
    created_documents = _seed_documents(session, target_date)
    return DemoSeedResult(
        created_customers=created_customers,
        created_products=created_products,
        created_documents=created_documents,
    )


def _seed_customers(session: Session, base_output_dir: Path, target_date: str) -> int:
    customers = [
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(base_output_dir / "Kunden" / "Cafe Nord"),
            address="Marktplatz 4",
            contact_email="bestellung@cafe-nord.test",
            payment_method="SEPA",
            next_contact_date=target_date,
            delivery_notes="Anlieferung ueber Seiteneingang",
            opening_hours="Mo-Fr 08:00-18:00",
        ),
        CustomerCreate(
            name="Gasthof Sued",
            folder_path=str(base_output_dir / "Kunden" / "Gasthof Sued"),
            address="Dorfstr. 1",
            contact_email="info@gasthof-sued.test",
            payment_method="Ueberweisung",
            next_contact_date=target_date,
            delivery_notes="Hofeinfahrt nutzen",
            opening_hours="ab 9 Uhr",
        ),
        CustomerCreate(
            name="Hotel Blau",
            folder_path=str(base_output_dir / "Kunden" / "Hotel Blau"),
            address="Seestr. 8",
            contact_email="bestellung@hotel-blau.test",
            payment_method="SEPA",
            next_contact_date=target_date,
            delivery_notes="Bestellung per Mail anfragen",
            opening_hours="Rezeption durchgehend besetzt",
        ),
    ]
    created = 0
    for customer in customers:
        if _customer_exists(session, customer.name):
            continue
        create_customer(session, customer)
        created += 1
    return created


def _seed_products(session: Session) -> int:
    products = [
        ProductCreate(name="Apfelschorle 12x1,0", unit="Kiste", standard_price_cents=1499, article_number="A-100"),
        ProductCreate(name="Helles 20x0,5", unit="Kiste", standard_price_cents=1899, article_number="B-200"),
        ProductCreate(name="Wasser 12x0,7", unit="Kiste", standard_price_cents=1299, article_number="W-070"),
    ]
    created = 0
    for product in products:
        if _product_exists(session, product.name):
            continue
        create_product(session, product)
        created += 1
    return created


def _seed_documents(session: Session, target_date: str) -> int:
    created = 0
    cafe_nord = _customer_by_name(session, "Cafe Nord")
    gasthof_sued = _customer_by_name(session, "Gasthof Sued")
    if cafe_nord is not None and not _document_exists(session, "RG-DEMO-1"):
        create_document(
            session,
            DocumentCreate(
                customer_id=cafe_nord.id,
                document_type="Rechnung",
                document_number="RG-DEMO-1",
                delivery_date=target_date,
                line_items=[
                    DocumentLineItem(
                        name="Wasser 12x0,7",
                        quantity=10,
                        unit_price_cents=1299,
                        deposit_cents=330,
                    ),
                    DocumentLineItem(
                        name="Helles 20x0,5",
                        quantity=4,
                        unit_price_cents=1899,
                        deposit_cents=310,
                    ),
                ],
            ),
        )
        created += 1
    if gasthof_sued is not None and not _document_exists(session, "LS-DEMO-1"):
        create_document(
            session,
            DocumentCreate(
                customer_id=gasthof_sued.id,
                document_type="Lieferschein",
                document_number="LS-DEMO-1",
                delivery_date=target_date,
                delivery_slot="nachmittag",
                line_items=[
                    DocumentLineItem(
                        name="Apfelschorle 12x1,0",
                        quantity=6,
                        unit_price_cents=1499,
                        deposit_cents=330,
                    )
                ],
            ),
        )
        created += 1
    return created


def _customer_exists(session: Session, name: str) -> bool:
    return _customer_by_name(session, name) is not None


def _customer_by_name(session: Session, name: str) -> Customer | None:
    return session.scalar(select(Customer).where(Customer.name == name))


def _product_exists(session: Session, name: str) -> bool:
    return session.scalar(select(Product).where(Product.name == name)) is not None


def _document_exists(session: Session, document_number: str) -> bool:
    return session.scalar(select(Document).where(Document.document_number == document_number)) is not None
