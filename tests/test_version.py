import io
import urllib.error
from datetime import date
from importlib.metadata import PackageNotFoundError

from zen_profile_selector.version import (
    PYPI_URL,
    UpdateState,
    fetch_latest_version,
    installed_version,
    is_newer,
    load_update_state,
    pipx_upgrade_command,
    save_update_state,
    update_check_due,
    version_to_announce,
)


def test_installed_version_reads_the_package_metadata():
    assert installed_version(lambda name: "1.2.3") == "1.2.3"


def test_installed_version_is_none_without_metadata():
    def missing(name):
        raise PackageNotFoundError(name)

    assert installed_version(missing) is None


def test_newer_versions_compare_by_number_not_text():
    assert is_newer("0.1.10", "0.1.9")
    assert is_newer("0.2.0", "0.1.12")
    assert is_newer("1.0", "0.9.9")
    assert not is_newer("0.1.2", "0.1.2")
    assert not is_newer("0.1.1", "0.1.2")


def test_unparsable_versions_are_never_newer():
    assert not is_newer("0.2.0rc1", "0.1.2")
    assert not is_newer("", "0.1.2")
    assert not is_newer("0.2.0", "")


def pypi_answer(body):
    def open_url(url, timeout):
        assert url == PYPI_URL
        assert timeout <= 5
        return io.BytesIO(body)

    return open_url


def test_latest_version_comes_from_the_pypi_json():
    assert fetch_latest_version(pypi_answer(b'{"info": {"version": "0.2.0"}}')) == "0.2.0"


def test_invalid_pypi_answers_give_none():
    assert fetch_latest_version(pypi_answer(b"<html>")) is None
    assert fetch_latest_version(pypi_answer(b'{"info": {}}')) is None
    assert fetch_latest_version(pypi_answer(b'{"info": {"version": 2}}')) is None
    assert fetch_latest_version(pypi_answer(b"[]")) is None


def test_network_errors_give_none():
    def offline(url, timeout):
        raise urllib.error.URLError("offline")

    assert fetch_latest_version(offline) is None


def test_missing_or_corrupt_update_state_gives_defaults(tmp_path):
    assert load_update_state(tmp_path) == UpdateState()
    (tmp_path / "update_check.json").write_text('{"checked": 3, "latest": "0.2.0"')
    assert load_update_state(tmp_path) == UpdateState()
    (tmp_path / "update_check.json").write_text('{"checked": 3, "latest": "0.2.0"}')
    assert load_update_state(tmp_path) == UpdateState(latest="0.2.0")


def test_update_state_round_trip(tmp_path):
    state = UpdateState(checked="2026-10-18", latest="0.2.0", dismissed="0.1.9")
    save_update_state(tmp_path / "new", state)
    assert load_update_state(tmp_path / "new") == state


def test_check_runs_at_most_once_a_day():
    today = date(2026, 10, 18)
    assert update_check_due(UpdateState(), today)
    assert update_check_due(UpdateState(checked="2026-10-17"), today)
    assert not update_check_due(UpdateState(checked="2026-10-18"), today)


def test_only_a_newer_not_dismissed_version_is_announced():
    assert version_to_announce(UpdateState(latest="0.2.0"), "0.1.2") == "0.2.0"
    assert version_to_announce(UpdateState(latest="0.1.2"), "0.1.2") is None
    assert version_to_announce(UpdateState(latest="0.2.0", dismissed="0.2.0"), "0.1.2") is None
    assert version_to_announce(UpdateState(latest="0.2.1", dismissed="0.2.0"), "0.1.2") == "0.2.1"
    assert version_to_announce(UpdateState(latest="0.2.0"), None) is None


def pipx_on_path(name):
    return "/usr/bin/pipx" if name == "pipx" else None


def test_pipx_installs_can_update_themselves():
    python = "/home/user/.local/share/pipx/venvs/zen-profile-selector/bin/python"
    assert pipx_upgrade_command(python, which=pipx_on_path) == [
        "/usr/bin/pipx",
        "upgrade",
        "zen-profile-selector",
    ]


def test_other_installs_or_missing_pipx_cannot_update_themselves():
    assert pipx_upgrade_command("/home/user/project/.venv/bin/python", which=pipx_on_path) is None
    python = "/home/user/.local/share/pipx/venvs/zen-profile-selector/bin/python"
    assert pipx_upgrade_command(python, which=lambda name: None) is None
