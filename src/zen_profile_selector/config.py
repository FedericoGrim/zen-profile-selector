from __future__ import annotations

import json
import os
import shlex
import shutil
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any

APP_NAME = "zen-profile-selector"
SETTINGS_FILE = "config.json"


@dataclass(frozen=True)
class Settings:
    language: str | None = None
    zen_command: str = ""
    profiles_dir: str = ""
    check_updates: bool = True

    @property
    def profiles_dir_path(self) -> Path | None:
        return Path(self.profiles_dir).expanduser() if self.profiles_dir else None


def xdg_config_home(env: Mapping[str, str], home: Path) -> Path:
    return Path(env.get("XDG_CONFIG_HOME") or home / ".config")


def config_dir(env: Mapping[str, str], home: Path) -> Path:
    return xdg_config_home(env, home) / APP_NAME


def load_settings(folder: Path) -> Settings:
    """Settings saved in the folder; missing, corrupt or mistyped values fall back to the defaults."""
    try:
        data = json.loads((folder / SETTINGS_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Settings()
    if not isinstance(data, dict):
        return Settings()
    defaults = Settings()
    valid: dict[str, Any] = {}
    for field in fields(Settings):
        value = data.get(field.name)
        default = getattr(defaults, field.name)
        if isinstance(value, str if default is None else type(default)):
            valid[field.name] = value
    return Settings(**valid)


def save_settings(folder: Path, settings: Settings) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / SETTINGS_FILE).write_text(json.dumps(asdict(settings), indent=2) + "\n", encoding="utf-8")


def validate_settings(
    zen_command: str, profiles_dir: str, which: Callable[[str], str | None] = shutil.which
) -> str | None:
    """Translation key of the first problem in the manual settings, None when they are usable."""
    if profiles_dir and not (Path(profiles_dir).expanduser() / "profiles.ini").is_file():
        return "profiles_dir_invalid"
    if zen_command:
        try:
            program = shlex.split(zen_command)[0]
        except (ValueError, IndexError):
            return "zen_command_invalid"
        if "/" in program:
            path = Path(program).expanduser()
            if not (path.is_file() and os.access(path, os.X_OK)):
                return "zen_command_not_found"
        elif which(program) is None:
            return "zen_command_not_found"
    return None
