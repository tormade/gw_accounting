from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect, text

from .config import AppConfig
from .models import Base
from .services.settings_service import ensure_default_product_units


def bootstrap_database(config: AppConfig) -> None:
    db_path = config.database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    _add_missing_columns(engine)
    _seed_defaults(engine)


def create_session_factory(config: AppConfig) -> sessionmaker:
    engine = create_engine(f"sqlite:///{config.database_path}")
    return sessionmaker(bind=engine)


def _add_missing_columns(engine) -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    with engine.begin() as connection:
        if "documents" in table_names:
            document_columns = {column["name"] for column in inspector.get_columns("documents")}
            if "datev_export_path" not in document_columns:
                connection.execute(text("ALTER TABLE documents ADD COLUMN datev_export_path VARCHAR(500)"))
            if "order_id" not in document_columns:
                connection.execute(text("ALTER TABLE documents ADD COLUMN order_id INTEGER"))
            if "number_released" not in document_columns:
                connection.execute(text("ALTER TABLE documents ADD COLUMN number_released BOOLEAN DEFAULT 0 NOT NULL"))
            if "delivery_fee_enabled" not in document_columns:
                connection.execute(text("ALTER TABLE documents ADD COLUMN delivery_fee_enabled BOOLEAN DEFAULT 0 NOT NULL"))
            if "delivery_comment" not in document_columns:
                connection.execute(text("ALTER TABLE documents ADD COLUMN delivery_comment TEXT"))
            if "footer_text" not in document_columns:
                connection.execute(text("ALTER TABLE documents ADD COLUMN footer_text TEXT"))
            connection.execute(
                text("UPDATE documents SET document_type = 'Lieferschein' WHERE document_type = 'Lieferauftrag'")
            )
        if "orders" in table_names:
            order_columns = {column["name"] for column in inspector.get_columns("orders")}
            if "number_released" not in order_columns:
                connection.execute(text("ALTER TABLE orders ADD COLUMN number_released BOOLEAN DEFAULT 0 NOT NULL"))
        if "open_items" in table_names:
            open_item_columns = {column["name"] for column in inspector.get_columns("open_items")}
            if "document_date" not in open_item_columns:
                connection.execute(text("ALTER TABLE open_items ADD COLUMN document_date VARCHAR(20)"))
            if "due_date" not in open_item_columns:
                connection.execute(text("ALTER TABLE open_items ADD COLUMN due_date VARCHAR(20)"))
        if "customers" in table_names:
            customer_columns = {column["name"] for column in inspector.get_columns("customers")}
            if "is_active" not in customer_columns:
                connection.execute(text("ALTER TABLE customers ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL"))
            if "source_file" not in customer_columns:
                connection.execute(text("ALTER TABLE customers ADD COLUMN source_file VARCHAR(500)"))
            if "source_row" not in customer_columns:
                connection.execute(text("ALTER TABLE customers ADD COLUMN source_row INTEGER"))
            if "phone" not in customer_columns:
                connection.execute(text("ALTER TABLE customers ADD COLUMN phone VARCHAR(100)"))
        if "products" in table_names:
            product_columns = {column["name"] for column in inspector.get_columns("products")}
            if "default_deposit_cents" not in product_columns:
                connection.execute(text("ALTER TABLE products ADD COLUMN default_deposit_cents INTEGER DEFAULT 0 NOT NULL"))
            if "source_file" not in product_columns:
                connection.execute(text("ALTER TABLE products ADD COLUMN source_file VARCHAR(500)"))
            if "source_row" not in product_columns:
                connection.execute(text("ALTER TABLE products ADD COLUMN source_row INTEGER"))
        if "onboarding_issues" in table_names:
            issue_columns = {column["name"] for column in inspector.get_columns("onboarding_issues")}
            if "status" not in issue_columns:
                connection.execute(text("ALTER TABLE onboarding_issues ADD COLUMN status VARCHAR(30) DEFAULT 'offen' NOT NULL"))
        if "product_aliases" in table_names:
            alias_columns = {column["name"] for column in inspector.get_columns("product_aliases")}
            if "status" not in alias_columns:
                connection.execute(text("ALTER TABLE product_aliases ADD COLUMN status VARCHAR(30) DEFAULT 'offen' NOT NULL"))
        if "customer_assortment_items" in table_names:
            assortment_columns = {column["name"] for column in inspector.get_columns("customer_assortment_items")}
            if "is_active" not in assortment_columns:
                connection.execute(text("ALTER TABLE customer_assortment_items ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL"))
            if "source_file" not in assortment_columns:
                connection.execute(text("ALTER TABLE customer_assortment_items ADD COLUMN source_file VARCHAR(500)"))
            if "price_decision" not in assortment_columns:
                connection.execute(
                    text("ALTER TABLE customer_assortment_items ADD COLUMN price_decision VARCHAR(30) DEFAULT 'offen' NOT NULL")
                )


def _seed_defaults(engine) -> None:
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        ensure_default_product_units(session)
    finally:
        session.close()
