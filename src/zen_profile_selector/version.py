from __future__ import annotations

from collections.abc import Callable
from importlib import metadata

from .config import APP_NAME


def installed_version(read_version: Callable[[str], str] = metadata.version) -> str | None:
    """Version of the installed package, None when it runs from a source tree without metadata."""
    try:
        return read_version(APP_NAME)
    except metadata.PackageNotFoundError:
        return None
