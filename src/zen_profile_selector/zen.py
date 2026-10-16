from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FLATPAK_ID = "app.zen_browser.zen"


@dataclass(frozen=True)
class ZenInstall:
    command: tuple[str, ...]
    profiles_dir: Path


def detect_zen(home, which, flatpak_installed, command=None, profiles_dir=None):
    raise NotImplementedError


def launch_command(install, profile_path):
    raise NotImplementedError


def create_profile_command(install, name):
    raise NotImplementedError
