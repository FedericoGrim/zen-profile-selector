from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

DESKTOP_FILE_NAME = "zen-profile-selector.desktop"


def desktop_file(env: Mapping[str, str], home: Path) -> Path:
    data_home = env.get("XDG_DATA_HOME") or home / ".local/share"
    return Path(data_home) / "applications" / DESKTOP_FILE_NAME


def desktop_entry(python: Path, icon: Path) -> str:
    return (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Zen Profile Selector\n"
        "Comment=Choose the Zen Browser profile to open\n"
        f'Exec="{python}" -m zen_profile_selector %u\n'
        f"Icon={icon}\n"
        "Terminal=false\n"
        "Categories=Network;WebBrowser;\n"
        "MimeType=x-scheme-handler/http;x-scheme-handler/https;text/html;\n"
    )


def install_desktop_entry(target: Path, python: Path, icon: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(desktop_entry(python, icon))


def uninstall_desktop_entry(target: Path) -> bool:
    if not target.exists():
        return False
    target.unlink()
    return True
