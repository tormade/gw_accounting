from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Customer, Document, Order, Product
from ..schemas import CustomerCreate, DocumentCreate, DocumentLineItem, OrderCreate, OrderLineCreate, ProductCreate
from .customer_service import create_customer
from .document_service import create_document
from .order_service import create_order
from .product_service import create_product


@dataclass(slots=True)
class DemoSeedResult:
    created_customers: int
    created_products: int
    created_orders: int
    created_documents: int


def seed_demo_workflow(session: Session, base_output_dir: Path, target_date: str) -> DemoSeedResult:
    created_customers = _seed_customers(session, base_output_dir, target_date)
    created_products = _seed_products(session)
    created_orders = _seed_orders(session, target_date)
    created_documents = _seed_documents(session, target_date)
    return DemoSeedResult(
        created_customers=created_customers,
        created_products=created_products,
        created_orders=created_orders,
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
        CustomerCreate(
            name="Archivkunde Beispiel",
            folder_path=str(base_output_dir / "Kunden" / "Archivkunde Beispiel"),
            address="Alte Str. 99",
            payment_method="Ueberweisung",
            delivery_notes="Beispiel fuer versehentlich archivierten Kunden",
            is_active=False,
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
        ProductCreate(
            name="Archivprodukt Beispiel",
            unit="Kiste",
            standard_price_cents=999,
            article_number="ALT-1",
            is_active=False,
        ),
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
    hotel_blau = _customer_by_name(session, "Hotel Blau")
    if cafe_nord is not None and not _document_exists(session, "RG-3001"):
        create_document(
            session,
            DocumentCreate(
                customer_id=cafe_nord.id,
                document_type="Rechnung",
                document_number="RG-3001",
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
    if hotel_blau is not None and not _document_exists(session, "RG-3002"):
        create_document(
            session,
            DocumentCreate(
                customer_id=hotel_blau.id,
                document_type="Rechnung",
                document_number="RG-3002",
                delivery_date=target_date,
                line_items=[
                    DocumentLineItem(
                        name="Helles 20x0,5",
                        quantity=5,
                        unit_price_cents=1899,
                        deposit_cents=310,
                    )
                ],
            ),
        )
        created += 1
    if gasthof_sued is not None and not _document_exists(session, "LS-3001"):
        create_document(
            session,
            DocumentCreate(
                customer_id=gasthof_sued.id,
                document_type="Lieferschein",
                document_number="LS-3001",
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
    if cafe_nord is not None and not _document_exists(session, "LS-3002"):
        create_document(
            session,
            DocumentCreate(
                customer_id=cafe_nord.id,
                document_type="Lieferschein",
                document_number="LS-3002",
                delivery_date=target_date,
                delivery_slot="vormittag",
                line_items=[
                    DocumentLineItem(
                        name="Wasser 12x0,7",
                        quantity=8,
                        unit_price_cents=1299,
                        deposit_cents=330,
                    )
                ],
            ),
        )
        created += 1
    return created


def _seed_orders(session: Session, target_date: str) -> int:
    customers = [
        _customer_by_name(session, "Cafe Nord"),
        _customer_by_name(session, "Gasthof Sued"),
        _customer_by_name(session, "Hotel Blau"),
    ]
    products = [
        _product_by_name(session, "Wasser 12x0,7"),
        _product_by_name(session, "Apfelschorle 12x1,0"),
        _product_by_name(session, "Helles 20x0,5"),
    ]
    customers = [customer for customer in customers if customer is not None]
    products = [product for product in products if product is not None]
    if not customers or not products:
        return 0

    created = 0
    for index in range(40):
        order_number = f"AUF-{1001 + index}"
        if _order_exists(session, order_number):
            continue
        customer = customers[index % len(customers)]
        first_product = products[index % len(products)]
        second_product = products[(index + 1) % len(products)]
        create_order(
            session,
            OrderCreate(
                order_number=order_number,
                customer_id=customer.id,
                order_date=target_date,
                delivery_date=target_date,
                delivery_slot="vormittag" if index % 2 == 0 else "nachmittag",
                lines=[
                    OrderLineCreate(product_id=first_product.id, quantity=2 + (index % 8), deposit_cents=330),
                    OrderLineCreate(product_id=second_product.id, quantity=1 + (index % 5), deposit_cents=330),
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


def _product_by_name(session: Session, name: str) -> Product | None:
    return session.scalar(select(Product).where(Product.name == name))


def _document_exists(session: Session, document_number: str) -> bool:
    return session.scalar(select(Document).where(Document.document_number == document_number)) is not None


def _order_exists(session: Session, order_number: str) -> bool:
    return (
        session.scalar(
            select(Order)
            .where(Order.order_number == order_number)
            .where(Order.status != "archiviert")
            .where(Order.number_released == False)  # noqa: E712
        )
        is not None
    )
