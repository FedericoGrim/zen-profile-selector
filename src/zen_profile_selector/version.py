from __future__ import annotations

import http.client
import json
import shutil
import sys
import urllib.request
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import date
from importlib import metadata
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import IO, Any

from .config import APP_NAME

PYPI_URL = f"https://pypi.org/pypi/{APP_NAME}/json"
UPGRADE_COMMAND = f"pipx upgrade {APP_NAME}"
UPDATE_FILE = "update_check.json"


def installed_version(read_version: Callable[[str], str] = metadata.version) -> str | None:
    """Version of the installed package, None when it runs from a source tree without metadata."""
    try:
        return read_version(APP_NAME)
    except metadata.PackageNotFoundError:
        return None


def pipx_upgrade_command(
    executable: str, which: Callable[[str], str | None] = shutil.which, system: str = sys.platform
) -> list[str] | None:
    """Command that upgrades this install in place; None unless it runs from a pipx virtual environment."""
    parts = (PureWindowsPath if system == "win32" else PurePosixPath)(executable).parts
    in_pipx = any(parts[index : index + 3] == ("pipx", "venvs", APP_NAME) for index in range(len(parts)))
    pipx = which("pipx")
    if pipx is None or not in_pipx:
        return None
    return [pipx, "upgrade", APP_NAME]


def parse_version(text: str) -> tuple[int, ...] | None:
    """Numeric parts of a plain release version (0.1.10); None for pre-releases or anything else."""
    parts = text.split(".")
    if not all(part.isascii() and part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)


def is_newer(candidate: str, current: str) -> bool:
    new, old = parse_version(candidate), parse_version(current)
    return new is not None and old is not None and new > old


def fetch_latest_version(
    open_url: Callable[..., IO[bytes]] = urllib.request.urlopen, timeout: float = 3
) -> str | None:
    """Latest release on PyPI; None when offline or when the answer is not what we expect."""
    try:
        with open_url(PYPI_URL, timeout=timeout) as response:
            data: Any = json.load(response)
        version = data["info"]["version"]
    except (OSError, ValueError, KeyError, TypeError, http.client.HTTPException):
        return None
    return version if isinstance(version, str) else None


@dataclass(frozen=True)
class UpdateState:
    checked: str = ""  # ISO date of the last successful check
    latest: str = ""
    dismissed: str = ""


def load_update_state(folder: Path) -> UpdateState:
    try:
        data = json.loads((folder / UPDATE_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return UpdateState()
    if not isinstance(data, dict):
        return UpdateState()
    known = asdict(UpdateState())
    return UpdateState(
        **{key: value for key, value in data.items() if key in known and isinstance(value, str)}
    )


def save_update_state(folder: Path, state: UpdateState) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / UPDATE_FILE).write_text(json.dumps(asdict(state), indent=2) + "\n", encoding="utf-8")


def update_check_due(state: UpdateState, today: date) -> bool:
    return state.checked != today.isoformat()


def version_to_announce(state: UpdateState, current: str | None) -> str | None:
    """The latest version when it is newer than the running one and the user has not dismissed it."""
    if current and state.latest != state.dismissed and is_newer(state.latest, current):
        return state.latest
    return None
