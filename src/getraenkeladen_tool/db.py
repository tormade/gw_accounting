from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect, text

from .config import AppConfig
from .models import Base


def bootstrap_database(config: AppConfig) -> None:
    db_path = config.database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    _add_missing_columns(engine)


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
        if "customers" in table_names:
            customer_columns = {column["name"] for column in inspector.get_columns("customers")}
            if "is_active" not in customer_columns:
                connection.execute(text("ALTER TABLE customers ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL"))
