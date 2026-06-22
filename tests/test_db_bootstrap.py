from pathlib import Path
import sqlite3

from getraenkeladen_tool.config import AppConfig
from getraenkeladen_tool.db import bootstrap_database


def test_bootstrap_database_creates_sqlite_file(tmp_path: Path):
    config = AppConfig(base_dir=tmp_path)
    bootstrap_database(config)
    assert config.database_path.exists()


def test_bootstrap_database_adds_missing_document_columns(tmp_path: Path):
    config = AppConfig(base_dir=tmp_path)
    config.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(config.database_path)
    connection.execute(
        "CREATE TABLE documents ("
        "id INTEGER PRIMARY KEY, "
        "customer_id INTEGER NOT NULL, "
        "document_type VARCHAR(30) NOT NULL, "
        "document_number VARCHAR(50) NOT NULL, "
        "excel_path VARCHAR(500) NOT NULL, "
        "pdf_path VARCHAR(500) NOT NULL, "
        "delivery_date VARCHAR(20), "
        "delivery_slot VARCHAR(30)"
        ")"
    )
    connection.commit()
    connection.close()

    bootstrap_database(config)

    connection = sqlite3.connect(config.database_path)
    columns = {row[1] for row in connection.execute("PRAGMA table_info(documents)").fetchall()}
    connection.close()
    assert "datev_export_path" in columns
    assert "order_id" in columns
    assert "number_released" in columns


def test_bootstrap_database_adds_order_number_released_column(tmp_path: Path):
    config = AppConfig(base_dir=tmp_path)
    config.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(config.database_path)
    connection.execute(
        "CREATE TABLE orders ("
        "id INTEGER PRIMARY KEY, "
        "order_number VARCHAR(50) NOT NULL, "
        "customer_id INTEGER NOT NULL, "
        "order_date VARCHAR(20) NOT NULL, "
        "delivery_date VARCHAR(20) NOT NULL, "
        "status VARCHAR(30) NOT NULL"
        ")"
    )
    connection.commit()
    connection.close()

    bootstrap_database(config)

    connection = sqlite3.connect(config.database_path)
    columns = {row[1] for row in connection.execute("PRAGMA table_info(orders)").fetchall()}
    connection.close()
    assert "number_released" in columns


def test_bootstrap_database_normalizes_legacy_delivery_order_document_type(tmp_path: Path):
    config = AppConfig(base_dir=tmp_path)
    config.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(config.database_path)
    connection.execute(
        "CREATE TABLE documents ("
        "id INTEGER PRIMARY KEY, "
        "customer_id INTEGER NOT NULL, "
        "document_type VARCHAR(30) NOT NULL, "
        "document_number VARCHAR(50) NOT NULL, "
        "excel_path VARCHAR(500) NOT NULL, "
        "pdf_path VARCHAR(500) NOT NULL, "
        "delivery_date VARCHAR(20), "
        "delivery_slot VARCHAR(30)"
        ")"
    )
    connection.execute(
        "INSERT INTO documents "
        "(customer_id, document_type, document_number, excel_path, pdf_path) "
        "VALUES (1, 'Lieferauftrag', 'LS-3999', 'legacy.xlsx', 'legacy.pdf')"
    )
    connection.commit()
    connection.close()

    bootstrap_database(config)

    connection = sqlite3.connect(config.database_path)
    document_type = connection.execute("SELECT document_type FROM documents WHERE document_number = 'LS-3999'").fetchone()[0]
    connection.close()
    assert document_type == "Lieferschein"


def test_bootstrap_database_adds_customer_active_column(tmp_path: Path):
    config = AppConfig(base_dir=tmp_path)
    config.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(config.database_path)
    connection.execute(
        "CREATE TABLE customers ("
        "id INTEGER PRIMARY KEY, "
        "name VARCHAR(200) NOT NULL, "
        "folder_path VARCHAR(500) NOT NULL"
        ")"
    )
    connection.commit()
    connection.close()

    bootstrap_database(config)

    connection = sqlite3.connect(config.database_path)
    columns = {row[1] for row in connection.execute("PRAGMA table_info(customers)").fetchall()}
    active_default = connection.execute("SELECT is_active FROM customers").fetchall()
    connection.close()
    assert "is_active" in columns
    assert active_default == []


def test_bootstrap_database_adds_import_and_change_tracking_columns(tmp_path: Path):
    config = AppConfig(base_dir=tmp_path)
    config.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(config.database_path)
    connection.execute(
        "CREATE TABLE customers ("
        "id INTEGER PRIMARY KEY, "
        "name VARCHAR(200) NOT NULL, "
        "folder_path VARCHAR(500) NOT NULL, "
        "is_active BOOLEAN DEFAULT 1 NOT NULL"
        ")"
    )
    connection.execute(
        "CREATE TABLE products ("
        "id INTEGER PRIMARY KEY, "
        "name VARCHAR(200) NOT NULL, "
        "unit VARCHAR(50) NOT NULL, "
        "standard_price_cents INTEGER NOT NULL, "
        "is_active BOOLEAN DEFAULT 1 NOT NULL"
        ")"
    )
    connection.commit()
    connection.close()

    bootstrap_database(config)

    connection = sqlite3.connect(config.database_path)
    customer_columns = {row[1] for row in connection.execute("PRAGMA table_info(customers)").fetchall()}
    product_columns = {row[1] for row in connection.execute("PRAGMA table_info(products)").fetchall()}
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    connection.close()

    assert {"source_file", "source_row"}.issubset(customer_columns)
    assert {"default_deposit_cents", "source_file", "source_row"}.issubset(product_columns)
    assert "master_data_changes" in tables


def test_bootstrap_database_creates_dropdown_options_with_units(tmp_path: Path):
    config = AppConfig(base_dir=tmp_path)
    bootstrap_database(config)

    connection = sqlite3.connect(config.database_path)
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    units = [
        row[0]
        for row in connection.execute(
            "SELECT value FROM dropdown_options WHERE category = 'product_unit' ORDER BY sort_order, value"
        ).fetchall()
    ]
    connection.close()

    assert "dropdown_options" in tables
    assert units[:3] == ["Kiste", "Flasche", "Fass"]
