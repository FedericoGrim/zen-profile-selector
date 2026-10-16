from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    language: str | None = None
    zen_command: str = ""
    profiles_dir: str = ""

    @property
    def profiles_dir_path(self):
        raise NotImplementedError


def config_dir(env, home):
    raise NotImplementedError


def load_settings(folder):
    raise NotImplementedError


def save_settings(folder, settings):
    raise NotImplementedError
