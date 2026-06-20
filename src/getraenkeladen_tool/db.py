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
