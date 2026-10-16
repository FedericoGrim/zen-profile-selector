from __future__ import annotations


def desktop_file(env, home):
    raise NotImplementedError


def desktop_entry(python, icon):
    raise NotImplementedError


def install_desktop_entry(target, python, icon):
    raise NotImplementedError


def uninstall_desktop_entry(target):
    raise NotImplementedError
