from pathlib import Path

from zen_profile_selector.zen import (
    FLATPAK_ID,
    ZenInstall,
    create_profile_command,
    detect_zen,
    launch_command,
)

FLATPAK_COMMAND = ("flatpak", "run", FLATPAK_ID)


def flatpak_profiles(home: Path) -> Path:
    return home / ".var/app/app.zen_browser.zen/.zen"


def add_profiles_ini(profiles_dir: Path) -> None:
    profiles_dir.mkdir(parents=True)
    (profiles_dir / "profiles.ini").write_text("[General]\n")


def no_binaries(name: str) -> None:
    return None


def zen_binary(name: str):
    return "/usr/bin/zen" if name == "zen" else None


def detect(home, which=no_binaries, flatpak=False, **overrides):
    return detect_zen(home, which=which, flatpak_installed=lambda: flatpak, **overrides)


def test_detects_flatpak_install(tmp_path):
    add_profiles_ini(flatpak_profiles(tmp_path))
    assert detect(tmp_path, flatpak=True) == ZenInstall(FLATPAK_COMMAND, flatpak_profiles(tmp_path))


def test_detects_native_install(tmp_path):
    assert detect(tmp_path, which=zen_binary) == ZenInstall(("/usr/bin/zen",), tmp_path / ".zen")


def test_detects_native_install_named_zen_browser(tmp_path):
    install = detect(tmp_path, which=lambda name: "/opt/zen-browser" if name == "zen-browser" else None)
    assert install == ZenInstall(("/opt/zen-browser",), tmp_path / ".zen")


def test_prefers_the_install_that_has_profiles(tmp_path):
    add_profiles_ini(tmp_path / ".zen")
    assert detect(tmp_path, which=zen_binary, flatpak=True).command == ("/usr/bin/zen",)


def test_prefers_flatpak_when_no_install_has_profiles_yet(tmp_path):
    assert detect(tmp_path, which=zen_binary, flatpak=True).command == FLATPAK_COMMAND


def test_returns_none_without_zen(tmp_path):
    assert detect(tmp_path) is None


def test_command_override_replaces_detected_command(tmp_path):
    install = detect(tmp_path, flatpak=True, command="/home/me/zen/zen --no-remote")
    assert install == ZenInstall(("/home/me/zen/zen", "--no-remote"), flatpak_profiles(tmp_path))


def test_profiles_dir_override_replaces_detected_folder(tmp_path):
    install = detect(tmp_path, which=zen_binary, profiles_dir=tmp_path / "custom")
    assert install == ZenInstall(("/usr/bin/zen",), tmp_path / "custom")


def test_full_override_works_without_any_detected_install(tmp_path):
    install = detect(tmp_path, command="/opt/zen/zen", profiles_dir=tmp_path / "profiles")
    assert install == ZenInstall(("/opt/zen/zen",), tmp_path / "profiles")


def test_partial_override_without_detected_install_is_not_enough(tmp_path):
    assert detect(tmp_path, command="/opt/zen/zen") is None
    assert detect(tmp_path, profiles_dir=tmp_path / "profiles") is None


def test_launch_and_create_commands_use_the_install_command(tmp_path):
    install = ZenInstall(FLATPAK_COMMAND, tmp_path)
    assert launch_command(install, "/p/abc.Work") == [*FLATPAK_COMMAND, "--profile", "/p/abc.Work"]
    assert create_profile_command(install, "Gaming") == [*FLATPAK_COMMAND, "--CreateProfile", "Gaming"]
