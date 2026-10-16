from pathlib import Path

from zen_profile_selector.config import Settings, config_dir, load_settings, save_settings


def test_config_dir_follows_xdg_config_home(tmp_path):
    env = {"XDG_CONFIG_HOME": str(tmp_path / "xdg")}
    assert config_dir(env, home=tmp_path) == tmp_path / "xdg" / "zen-profile-selector"


def test_config_dir_defaults_to_dot_config(tmp_path):
    assert config_dir({}, home=tmp_path) == tmp_path / ".config" / "zen-profile-selector"


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
