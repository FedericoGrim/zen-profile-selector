import subprocess
import sys
from configparser import ConfigParser

import pytest

from zen_profile_selector.profiles import (
    DEFAULT_ICON,
    icon_for,
    load_icons,
    profile_in_use,
    read_profiles,
    remove_icon,
    remove_profile,
    rename_icon,
    rename_profile,
    save_icon,
    validate_profile_name,
)

PROFILES_INI = """[General]
StartWithLastProfile=1
Version=2

[Profile1]
Name=Home
IsRelative=1
Path=a1b2c3d4.Home
Default=1

[Profile0]
Name=Office
IsRelative=1
Path=e5f6g7h8.default-release

[Profile3]
Name=University
IsRelative=0
Path=/data/zen/university

[Profile2]
Name=Gaming
IsRelative=1
Path=i9j0k1l2.Gaming

[Install0123456789ABCDEF]
Default=/data/zen/university
Locked=1
"""


def parse(ini_text):
    parser = ConfigParser(interpolation=None)
    parser.optionxform = str  # type: ignore[assignment,method-assign]
    parser.read_string(ini_text)
    return parser


def profile_sections(parser):
    return {parser[s]["Name"]: parser[s] for s in parser.sections() if s.startswith("Profile")}


def test_read_profiles_resolves_relative_and_absolute_paths(tmp_path):
    (tmp_path / "profiles.ini").write_text(PROFILES_INI)
    assert read_profiles(tmp_path) == {
        "Gaming": str(tmp_path / "i9j0k1l2.Gaming"),
        "Home": str(tmp_path / "a1b2c3d4.Home"),
        "Office": str(tmp_path / "e5f6g7h8.default-release"),
        "University": "/data/zen/university",
    }
    assert list(read_profiles(tmp_path)) == ["Gaming", "Home", "Office", "University"]


def test_read_profiles_without_profiles_ini_is_empty(tmp_path):
    assert read_profiles(tmp_path) == {}


def test_profile_name_must_not_be_empty():
    assert validate_profile_name("", ["Office"]) is not None
    assert validate_profile_name("   ", ["Office"]) is not None


def test_profile_name_must_be_new():
    assert validate_profile_name("Office", ["Office"]) is not None
    assert validate_profile_name(" office ", ["Office"]) is not None


def test_valid_profile_name_has_no_error():
    assert validate_profile_name("Travel", ["Office"]) is None


def test_icons_round_trip_and_default(tmp_path):
    icons_file = tmp_path / "config" / "profile_icons.json"
    assert load_icons(icons_file) == {}
    save_icon(icons_file, "Gaming", "🎮")
    icons = load_icons(icons_file)
    assert icon_for(icons, "Gaming") == "🎮"
    assert icon_for(icons, "Unknown") == DEFAULT_ICON


def test_icons_follow_rename_and_remove(tmp_path):
    icons_file = tmp_path / "profile_icons.json"
    save_icon(icons_file, "University", "🎓")
    rename_icon(icons_file, "University", "Academy")
    assert load_icons(icons_file) == {"Academy": "🎓"}
    remove_icon(icons_file, "Academy")
    assert load_icons(icons_file) == {}


def test_rename_profile_changes_only_the_name():
    profiles = profile_sections(parse(rename_profile(PROFILES_INI, "Gaming", "Games")))
    assert "Gaming" not in profiles
    assert profiles["Games"]["Path"] == "i9j0k1l2.Gaming"
    assert len(profiles) == 4


def test_rename_unknown_profile_fails():
    with pytest.raises(ValueError):
        rename_profile(PROFILES_INI, "Nope", "New")


def test_remove_profile_renumbers_sections_without_gaps():
    parser = parse(remove_profile(PROFILES_INI, "Office"))
    sections = [s for s in parser.sections() if s.startswith("Profile")]
    assert sorted(sections) == ["Profile0", "Profile1", "Profile2"]
    assert set(profile_sections(parser)) == {"Home", "University", "Gaming"}
    assert parser["Install0123456789ABCDEF"]["Default"] == "/data/zen/university"


def test_removing_default_profiles_moves_the_default():
    parser = parse(remove_profile(remove_profile(PROFILES_INI, "Home"), "University"))
    profiles = profile_sections(parser)
    defaults = [name for name, section in profiles.items() if section.get("Default") == "1"]
    assert len(defaults) == 1
    assert parser["Install0123456789ABCDEF"]["Default"] == profiles[defaults[0]]["Path"]


def test_last_profile_cannot_be_removed():
    ini = PROFILES_INI
    for name in ("Home", "Office", "University"):
        ini = remove_profile(ini, name)
    with pytest.raises(ValueError):
        remove_profile(ini, "Gaming")


@pytest.mark.skipif(sys.platform == "win32", reason="Zen uses parent.lock on Windows")
def test_profile_in_use_follows_zen_lock(tmp_path):
    assert not profile_in_use(tmp_path)
    (tmp_path / ".parentlock").touch()
    assert not profile_in_use(tmp_path)
    holder = subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import fcntl, sys, time; f = open(sys.argv[1], 'w'); fcntl.lockf(f, fcntl.LOCK_EX); "
            "print('locked', flush=True); time.sleep(10)",
            str(tmp_path / ".parentlock"),
        ],
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout.readline().strip() == "locked"
        assert profile_in_use(tmp_path)
    finally:
        holder.kill()
        holder.wait()
    assert not profile_in_use(tmp_path)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows file sharing")
def test_profile_in_use_follows_zen_lock_on_windows(tmp_path):
    import _winapi

    assert not profile_in_use(tmp_path)
    lock = tmp_path / "parent.lock"
    lock.touch()
    assert not profile_in_use(tmp_path)
    # Zen opens parent.lock without sharing while the profile is running
    handle = _winapi.CreateFile(str(lock), _winapi.GENERIC_WRITE, 0, 0, _winapi.OPEN_EXISTING, 0, 0)
    try:
        assert profile_in_use(tmp_path)
    finally:
        _winapi.CloseHandle(handle)
    assert not profile_in_use(tmp_path)
