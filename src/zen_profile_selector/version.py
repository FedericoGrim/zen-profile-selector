from __future__ import annotations

import importlib.metadata
from importlib.metadata import PackageNotFoundError


def get_version() -> str:
    """Return the installed package version, or "unknown" if metadata is missing."""
    try:
        return importlib.metadata.version("zen-profile-selector")
    except PackageNotFoundError:
        return "unknown"
