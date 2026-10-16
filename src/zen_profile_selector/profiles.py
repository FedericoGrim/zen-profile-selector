from __future__ import annotations

import fcntl
import io
import json
import os
from collections.abc import Iterable
from configparser import ConfigParser, SectionProxy
from pathlib import Path

DEFAULT_ICON = "📌"
ICON_CHOICES = ["👤", "💼", "🏫", "🎓", "📚", "🎮", "🎵", "🛒", "💻", "🏠", "✈️", "📌"]


def _parse_profiles_ini(ini_text: str) -> ConfigParser:
    parser = ConfigParser(interpolation=None)
    parser.optionxform = str  # type: ignore[assignment,method-assign]
    parser.read_string(ini_text)
    return parser


def _write_profiles_ini(parser: ConfigParser) -> str:
    output = io.StringIO()
    parser.write(output, space_around_delimiters=False)
    return output.getvalue()


def _profile_sections(parser: ConfigParser) -> list[SectionProxy]:
    return [parser[section] for section in parser.sections() if section.startswith("Profile")]


def _find_profile(parser: ConfigParser, name: str) -> SectionProxy:
    for section in _profile_sections(parser):
        if section.get("Name") == name:
            return section
    raise ValueError(f"Profile not found: {name}")


def read_profiles(profiles_dir: Path) -> dict[str, str]:
    """Profile name -> absolute profile folder, sorted by name."""
    try:
        parser = _parse_profiles_ini((profiles_dir / "profiles.ini").read_text())
    except OSError:
        return {}
    profiles = {}
    for section in _profile_sections(parser):
        name, path = section.get("Name"), section.get("Path")
        if name and path:
            profiles[name] = path if section.get("IsRelative") == "0" else str(profiles_dir / path)
    return dict(sorted(profiles.items(), key=lambda item: item[0].casefold()))


def validate_profile_name(name: str, existing_names: Iterable[str]) -> str | None:
    """Translation key of the error for an invalid name, None when it is fine."""
    name = name.strip()
    if not name:
        return "empty_name"
    if name.lower() in (existing.lower() for existing in existing_names):
        return "duplicate_name"
    return None


def rename_profile(ini_text: str, old_name: str, new_name: str) -> str:
    """profiles.ini with the profile renamed; its folder does not change."""
    parser = _parse_profiles_ini(ini_text)
    _find_profile(parser, old_name)["Name"] = new_name
    return _write_profiles_ini(parser)


def remove_profile(ini_text: str, name: str) -> str:
    """profiles.ini without the profile: ProfileN sections renumbered, default moved if needed."""
    parser = _parse_profiles_ini(ini_text)
    removed = _find_profile(parser, name)
    if len(_profile_sections(parser)) == 1:
        raise ValueError("last_profile")

    result = ConfigParser(interpolation=None)
    result.optionxform = str  # type: ignore[assignment,method-assign]
    number = 0
    for section in parser.sections():
        if section.startswith("Profile"):
            if parser[section] is removed:
                continue
            result[f"Profile{number}"] = dict(parser[section])
            number += 1
        else:
            result[section] = dict(parser[section])

    profiles = _profile_sections(result)
    if removed.get("Default") == "1":
        profiles[0]["Default"] = "1"
    default = next((profile for profile in profiles if profile.get("Default") == "1"), profiles[0])
    for section in result.sections():
        if section.startswith("Install") and result[section].get("Default") == removed["Path"]:
            result[section]["Default"] = default["Path"]
    return _write_profiles_ini(result)


def profile_in_use(profile_dir: Path) -> bool:
    """Zen holds a lock on .parentlock while the profile is open."""
    try:
        lock_fd = os.open(profile_dir / ".parentlock", os.O_WRONLY)
    except FileNotFoundError:
        return False
    try:
        fcntl.lockf(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.lockf(lock_fd, fcntl.LOCK_UN)
        return False
    except OSError:
        return True
    finally:
        os.close(lock_fd)


def load_icons(icons_file: Path) -> dict[str, str]:
    try:
        icons = json.loads(icons_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return icons if isinstance(icons, dict) else {}


def icon_for(icons: dict[str, str], name: str) -> str:
    return icons.get(name, DEFAULT_ICON)


def _write_icons(icons_file: Path, icons: dict[str, str]) -> None:
    icons_file.parent.mkdir(parents=True, exist_ok=True)
    icons_file.write_text(json.dumps(icons, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_icon(icons_file: Path, name: str, icon: str) -> None:
    icons = load_icons(icons_file)
    icons[name] = icon
    _write_icons(icons_file, icons)


def rename_icon(icons_file: Path, old_name: str, new_name: str) -> None:
    icons = load_icons(icons_file)
    if old_name in icons:
        icons[new_name] = icons.pop(old_name)
        _write_icons(icons_file, icons)


def remove_icon(icons_file: Path, name: str) -> None:
    icons = load_icons(icons_file)
    if icons.pop(name, None) is not None:
        _write_icons(icons_file, icons)
