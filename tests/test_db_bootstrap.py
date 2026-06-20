from pathlib import Path

from getraenkeladen_tool.config import AppConfig
from getraenkeladen_tool.db import bootstrap_database


def test_bootstrap_database_creates_sqlite_file(tmp_path: Path):
    config = AppConfig(base_dir=tmp_path)
    bootstrap_database(config)
    assert config.database_path.exists()
