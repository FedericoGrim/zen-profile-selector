from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields
from pathlib import Path

APP_NAME = "zen-profile-selector"
SETTINGS_FILE = "config.json"


@dataclass(frozen=True)
class Settings:
    language: str | None = None
    zen_command: str = ""
    profiles_dir: str = ""

    @property
    def profiles_dir_path(self) -> Path | None:
        return Path(self.profiles_dir).expanduser() if self.profiles_dir else None


def config_dir(env: Mapping[str, str], home: Path) -> Path:
    base = env.get("XDG_CONFIG_HOME") or home / ".config"
    return Path(base) / APP_NAME


def load_settings(folder: Path) -> Settings:
    """Settings saved in the folder; missing, corrupt or mistyped values fall back to the defaults."""
    try:
        data = json.loads((folder / SETTINGS_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Settings()
    if not isinstance(data, dict):
        return Settings()
    defaults = Settings()
    valid = {}
    for field in fields(Settings):
        value = data.get(field.name)
        default = getattr(defaults, field.name)
        if isinstance(value, str) and (default is None or isinstance(default, str)):
            valid[field.name] = value
    return Settings(**valid)


def save_settings(folder: Path, settings: Settings) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / SETTINGS_FILE).write_text(json.dumps(asdict(settings), indent=2) + "\n", encoding="utf-8")


def validate_settings(zen_command, profiles_dir, which):
    raise NotImplementedError
