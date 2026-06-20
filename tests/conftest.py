from collections.abc import Iterator

import pytest

from getraenkeladen_tool.config import AppConfig
from getraenkeladen_tool.db import bootstrap_database, create_session_factory


@pytest.fixture
def session(tmp_path) -> Iterator:
    config = AppConfig(base_dir=tmp_path)
    bootstrap_database(config)
    session_factory = create_session_factory(config)
    db_session = session_factory()
    try:
        yield db_session
    finally:
        db_session.close()
