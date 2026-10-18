from __future__ import annotations

import shlex
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

FLATPAK_ID = "app.zen_browser.zen"
NATIVE_BINARIES = ("zen", "zen-browser")


@dataclass(frozen=True)
class ZenInstall:
    command: tuple[str, ...]
    profiles_dir: Path


def flatpak_zen_installed() -> bool:
    try:
        result = subprocess.run(["flatpak", "info", FLATPAK_ID], capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def zen_profiles_dir(legacy: Path, xdg: Path) -> Path:
    """Zen's own rule: it keeps the old ~/.zen folder while it exists, new installs use the XDG one."""
    return legacy if legacy.is_dir() else xdg


def detect_zen(
    home: Path,
    which: Callable[[str], str | None] = shutil.which,
    flatpak_installed: Callable[[], bool] = flatpak_zen_installed,
    command: str | None = None,
    profiles_dir: Path | None = None,
    config_home: Path | None = None,
) -> ZenInstall | None:
    """Find Zen: Flatpak first, then a native binary; manual settings override what is detected."""
    candidates = []
    if flatpak_installed():
        sandbox = home / ".var/app" / FLATPAK_ID
        profiles = zen_profiles_dir(sandbox / ".zen", sandbox / "config/zen")
        candidates.append(ZenInstall(("flatpak", "run", FLATPAK_ID), profiles))
    native = next((path for path in map(which, NATIVE_BINARIES) if path), None)
    if native:
        xdg = (config_home or home / ".config") / "zen"
        candidates.append(ZenInstall((native,), zen_profiles_dir(home / ".zen", xdg)))

    detected = next(
        (install for install in candidates if (install.profiles_dir / "profiles.ini").exists()),
        candidates[0] if candidates else None,
    )

    if command and profiles_dir:
        return ZenInstall(tuple(shlex.split(command)), profiles_dir)
    if detected is None:
        return None
    if command:
        detected = replace(detected, command=tuple(shlex.split(command)))
    if profiles_dir:
        detected = replace(detected, profiles_dir=profiles_dir)
    return detected


def launch_command(install: ZenInstall, profile_path: str) -> list[str]:
    return [*install.command, "--profile", profile_path]


def create_profile_command(install: ZenInstall, name: str) -> list[str]:
    return [*install.command, "--CreateProfile", name]
