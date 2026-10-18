from importlib.metadata import PackageNotFoundError

from zen_profile_selector.version import installed_version


def test_installed_version_reads_the_package_metadata():
    assert installed_version(lambda name: "1.2.3") == "1.2.3"


def test_installed_version_is_none_without_metadata():
    def missing(name):
        raise PackageNotFoundError(name)

    assert installed_version(missing) is None
