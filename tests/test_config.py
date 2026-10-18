import sys
from pathlib import Path

import pytest

from zen_profile_selector.config import Settings, config_dir, load_settings, save_settings, validate_settings


def test_config_dir_follows_xdg_config_home(tmp_path):
    env = {"XDG_CONFIG_HOME": str(tmp_path / "xdg")}
    assert config_dir(env, home=tmp_path, system="linux") == tmp_path / "xdg" / "zen-profile-selector"


def test_config_dir_defaults_to_dot_config(tmp_path):
    assert config_dir({}, home=tmp_path, system="linux") == tmp_path / ".config" / "zen-profile-selector"


def test_config_dir_on_windows_is_in_appdata(tmp_path):
    env = {"APPDATA": str(tmp_path / "Roaming"), "XDG_CONFIG_HOME": str(tmp_path / "xdg")}
    assert config_dir(env, home=tmp_path, system="win32") == tmp_path / "Roaming" / "zen-profile-selector"
    assert config_dir({}, home=tmp_path, system="win32") == tmp_path / "AppData/Roaming/zen-profile-selector"


def test_missing_config_gives_defaults(tmp_path):
    assert load_settings(tmp_path) == Settings()


def test_corrupt_config_gives_defaults(tmp_path):
    (tmp_path / "config.json").write_text("{not json")
    assert load_settings(tmp_path) == Settings()


def test_unknown_keys_and_wrong_types_are_ignored(tmp_path):
    (tmp_path / "config.json").write_text('{"language": "it", "zen_command": 42, "theme": "dark"}')
    assert load_settings(tmp_path) == Settings(language="it")


def test_settings_round_trip_creates_the_folder(tmp_path):
    folder = tmp_path / "new" / "zen-profile-selector"
    settings = Settings(language="en", zen_command="/opt/zen/zen", profiles_dir="/data/zen")
    save_settings(folder, settings)
    assert load_settings(folder) == settings


def test_profiles_dir_path_is_none_when_empty():
    assert Settings().profiles_dir_path is None
    assert Settings(profiles_dir="~/zen").profiles_dir_path == Path("~/zen").expanduser()


def zen_on_path(name):
    return "/usr/bin/zen" if name == "zen" else None


def test_empty_settings_are_valid_because_they_mean_detect():
    assert validate_settings("", "", which=zen_on_path) is None


def test_profiles_dir_must_contain_profiles_ini(tmp_path):
    assert validate_settings("", str(tmp_path), which=zen_on_path) == "profiles_dir_invalid"
    (tmp_path / "profiles.ini").write_text("[General]\n")
    assert validate_settings("", str(tmp_path), which=zen_on_path) is None


def test_zen_command_must_exist(tmp_path):
    assert validate_settings("zen --no-remote", "", which=zen_on_path) is None
    assert validate_settings("firefox-zen", "", which=zen_on_path) == "zen_command_not_found"
    assert validate_settings(str(tmp_path / "missing"), "", which=zen_on_path) == "zen_command_not_found"


@pytest.mark.skipif(sys.platform == "win32", reason="Windows has no executable bit")
def test_zen_command_with_a_path_must_be_executable(tmp_path):
    binary = tmp_path / "zen"
    binary.write_text("#!/bin/sh\n")
    assert validate_settings(str(binary), "", which=zen_on_path) == "zen_command_not_found"
    binary.chmod(0o755)
    assert validate_settings(str(binary), "", which=zen_on_path) is None


def test_unbalanced_quotes_are_an_invalid_command():
    assert validate_settings('zen "--profile', "", which=zen_on_path) == "zen_command_invalid"


def test_update_check_is_on_by_default_and_can_be_turned_off(tmp_path):
    assert Settings().check_updates is True
    (tmp_path / "config.json").write_text('{"check_updates": false}')
    assert load_settings(tmp_path) == Settings(check_updates=False)
    (tmp_path / "config.json").write_text('{"check_updates": "no", "language": true}')
    assert load_settings(tmp_path) == Settings()


def test_windows_command_with_a_missing_path_is_not_found(tmp_path):
    command = r'"C:\Program Files\Missing\zen.exe" --no-remote'
    assert validate_settings(command, "", which=zen_on_path, system="win32") == "zen_command_not_found"
