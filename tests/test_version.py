from unittest.mock import patch

from zen_profile_selector.version import get_version


def test_get_version_returns_installed_version():
    with patch("importlib.metadata.version", return_value="1.2.3") as mocked:
        assert get_version() == "1.2.3"
        mocked.assert_called_once_with("zen-profile-selector")


def test_get_version_falls_back_when_package_missing():
    from importlib.metadata import PackageNotFoundError

    with patch("importlib.metadata.version", side_effect=PackageNotFoundError("zen-profile-selector")):
        assert get_version() == "unknown"
