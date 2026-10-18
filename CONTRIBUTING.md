# Contributing to zen-profile-selector

Thanks for your interest! Bug reports, translations, packaging and code are all welcome, and you do not need to be an expert: several issues are labelled [`good first issue`](https://github.com/FedericoGrim/zen-profile-selector/labels/good%20first%20issue).

By taking part you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to help

- **Report a bug** or **suggest a feature** with the [issue forms](https://github.com/FedericoGrim/zen-profile-selector/issues/new/choose).
- **Ask a question** or share an idea in [Discussions](https://github.com/FedericoGrim/zen-profile-selector/discussions) — issues are for actionable work.
- **Translate** the interface into your language (see [Adding a language](#adding-a-language)).
- **Pick an issue** from the [roadmap](https://github.com/FedericoGrim/zen-profile-selector/labels/roadmap). Comment on it first so nobody works on the same thing twice.
- **Security problems** go through the private process in [SECURITY.md](SECURITY.md), never a public issue.

## Development setup (5 minutes)

You need Linux, Python 3.9+ with Tk (`sudo apt install python3-tk` on Debian, Ubuntu and Mint) and Git. Zen Browser is only needed to try the app by hand.

```bash
git clone https://github.com/FedericoGrim/zen-profile-selector.git
cd zen-profile-selector
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pre-commit install --hook-type pre-commit --hook-type commit-msg
```

Check that everything works:

```bash
.venv/bin/pytest
.venv/bin/pre-commit run --all-files
.venv/bin/zen-profile-selector
```

## Project layout

| Module | Responsibility |
|--------|----------------|
| `zen.py` | Finding Zen (Flatpak or native) and building its commands |
| `profiles.py` | Reading and editing `profiles.ini`, profile icons, the "profile in use" check |
| `config.py` | Settings in `~/.config/zen-profile-selector/` and their validation |
| `i18n.py` | Translations and system language detection |
| `layout.py` | Grid size and primary monitor helpers |
| `desktop.py` | Applications menu entry |
| `version.py` | Installed version and the daily update check on PyPI |
| `app.py` | The customtkinter interface and the command-line entry point |

Keep logic out of `app.py`: put new behavior in a small, pure function in one of the other modules, test it there, then call it from the interface.

## Making a change

1. **Open or pick an issue** and say you are working on it. For anything bigger than a small fix, describe your approach first so we can agree before you write code.
2. **Branch from `develop`** (not `main`), named `feature/<short-name>`, `fix/<short-name>`, `docs/<short-name>`…
3. **Write a test first** when you change behavior. Tests live in `tests/`, use pytest, temporary folders and made-up profiles — never real user data or home paths.
4. **Commit in small steps** with [Conventional Commits](https://www.conventionalcommits.org) in English: `feat(profiles): …`, `fix(app): …`, `docs: …`, `test: …`. The commit-msg hook checks the format; the messages build the CHANGELOG automatically.
5. **Open a pull request against `develop`** and fill in the template. CI runs the same checks as pre-commit plus the tests on Python 3.9 and 3.12; it must be green.

Pull requests are merged with **Rebase and merge**, so every commit lands in `develop` once and appears once in the changelog. Releases (`develop` → `main`) are prepared by the maintainer with release-please.

### What makes a pull request easy to merge

- It does one thing and links its issue (`Closes #12`).
- New behavior has tests, and `pytest` plus `pre-commit run --all-files` pass.
- Every new piece of text exists in all languages in `i18n.py` (a test enforces it).
- It never deletes profile data permanently: deletions go to the Trash, and `profiles.ini` is backed up before writing.
- Screenshots, if any, use made-up profile names.

## Adding a language

1. In `src/zen_profile_selector/i18n.py`, add your language to `LANGUAGES`, for example `"de": "Deutsch"`.
2. Copy the whole `"en"` block in `TRANSLATIONS` under your language code and translate the values (keep the keys and the `{name}` placeholders).
3. Run `.venv/bin/pytest`: the test fails if any key is missing.
4. Start the app, pick your language from the menu and check that nothing is cut off.

## Questions

Ask in [Discussions](https://github.com/FedericoGrim/zen-profile-selector/discussions), or contact the maintainer, Federico Grimaldi, at federico.grimaldi2006@gmail.com.
