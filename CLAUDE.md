# zen-profile-selector

## Overview
- Unofficial desktop profile picker for Zen Browser on Linux: open, create, rename, re-icon and delete Zen profiles.
- Public open source project (GPL-3.0-or-later), distributed with pipx. Must stay independent from any specific machine.

## Tech stack
- Python 3.9+ (`from __future__ import annotations` for modern type syntax)
- customtkinter + tkinter for the UI; standard library for everything else
- pytest, ruff, mypy, pre-commit, gitleaks; GitHub Actions; release-please (python release type); releases published to PyPI with trusted publishing (decision 004)

## Architecture
Simple layering (no tactical DDD: small tool without complex domain rules).
- `zen.py`: Zen detection (Flatpak `app.zen_browser.zen`, native `zen`/`zen-browser`) and command building
- `profiles.py`: pure logic on `profiles.ini` text, icons file, profile lock check
- `config.py`: settings in `$XDG_CONFIG_HOME/zen-profile-selector/` and their validation
- `i18n.py`: English/Italian strings and system language detection
- `layout.py`: grid columns and primary monitor parsing
- `desktop.py`: applications menu entry
- `app.py`: customtkinter UI and CLI entry point; the only module with side effects on the UI
- Keep logic out of `app.py`: new behavior goes in a pure, tested module first.

## Commands
- Setup: `python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"`
- Hooks: `.venv/bin/pre-commit install --hook-type pre-commit --hook-type commit-msg`
- Tests: `.venv/bin/pytest`
- All checks: `.venv/bin/pre-commit run --all-files`
- Run: `.venv/bin/zen-profile-selector`

## Environment
- No secrets or env files. Optional system tools: `flatpak`, `gio` (Trash), `xrandr` (monitor).
- Respected variables: `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `LANGUAGE`/`LC_ALL`/`LC_MESSAGES`/`LANG`.

## Domain glossary
- Profile: a Zen profile listed in `profiles.ini` (`Name`, `Path`, `IsRelative`, `Default`)
- Install: how Zen runs on the machine (`ZenInstall`: command + profiles folder)
- Settings: manual overrides for the Zen command and profiles folder, plus the language

## Project conventions
- User-facing text only through `i18n.py`; every key exists in every language (enforced by a test). Error results are translation keys.
- Never hardcode user paths, profile names or the Flatpak command outside `zen.py`.
- Tests use made-up profiles and temporary folders, never real user data.
- Pull requests into `develop` are merged with "Rebase and merge" (decision 003); merge commits only for release and back-merge PRs.

## Security & constraints
- Never delete profile data permanently: deletion moves the folder to the Trash with `gio trash`, refuses profiles in use (`.parentlock` lock) and the last profile.
- Back up `profiles.ini` (`profiles.ini.selector-bak`) before every write and keep `[ProfileN]` sections numbered without gaps.
- Profile creation goes through Zen (`--CreateProfile`), not by writing folders by hand.

## Definition of Done (extra)
- New UI text added in both languages.
- Behavior checked manually against a real Zen install when it touches `profiles.ini`, using a backup and test profiles.

## Decisions
See [docs/decisions.md](docs/decisions.md).

## Do not
- Do not add Windows/macOS code paths without a decision record.
- Do not commit screenshots or fixtures containing real profile names or home paths.
