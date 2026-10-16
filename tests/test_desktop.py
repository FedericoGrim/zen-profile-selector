from pathlib import Path

from zen_profile_selector.desktop import (
    desktop_entry,
    desktop_file,
    install_desktop_entry,
    uninstall_desktop_entry,
)


def test_desktop_file_follows_xdg_data_home(tmp_path):
    env = {"XDG_DATA_HOME": str(tmp_path / "data")}
    assert desktop_file(env, home=tmp_path) == tmp_path / "data/applications/zen-profile-selector.desktop"


def test_desktop_file_defaults_to_local_share(tmp_path):
    assert (
        desktop_file({}, home=tmp_path) == tmp_path / ".local/share/applications/zen-profile-selector.desktop"
    )


def test_desktop_entry_runs_the_package_with_its_python(tmp_path):
    entry = desktop_entry(Path("/venv/bin/python"), Path("/venv/assets/icon.png"))
    assert "[Desktop Entry]" in entry
    assert 'Exec="/venv/bin/python" -m zen_profile_selector' in entry
    assert "Icon=/venv/assets/icon.png" in entry
    assert "Type=Application" in entry


def test_install_then_uninstall(tmp_path):
    target = tmp_path / "applications" / "zen-profile-selector.desktop"
    install_desktop_entry(target, Path("/venv/bin/python"), Path("/venv/assets/icon.png"))
    assert target.read_text().startswith("[Desktop Entry]")
    assert uninstall_desktop_entry(target) is True
    assert not target.exists()
    assert uninstall_desktop_entry(target) is False
