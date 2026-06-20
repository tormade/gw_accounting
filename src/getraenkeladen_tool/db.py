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
