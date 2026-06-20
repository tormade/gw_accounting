from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    base_dir: Path

    @property
    def database_path(self) -> Path:
        return self.base_dir / "data" / "getraenkeladen.db"
