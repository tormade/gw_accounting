from pathlib import Path


def ensure_parent_folder(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
