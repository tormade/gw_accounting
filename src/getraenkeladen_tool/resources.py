"""Stable paths for bundled assets and local development."""

import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    """Return an absolute path to a bundled resource in development or a frozen app."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    root = Path(bundle_root) if bundle_root else Path(__file__).resolve().parents[2]
    return root.joinpath(*parts)


def development_default_dir(*parts: str) -> Path:
    """Return a predictable development default without relying on the process CWD."""
    return resource_path(*parts)
