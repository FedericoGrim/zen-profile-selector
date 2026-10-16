from __future__ import annotations

LANGUAGES: dict[str, str] = {}
TRANSLATIONS: dict[str, dict[str, str]] = {}


def detect_language(env):
    raise NotImplementedError


def translate(language, key, **values):
    raise NotImplementedError
