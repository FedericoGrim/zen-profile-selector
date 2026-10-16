# zen-profile-selector

A small, fast profile picker for [Zen Browser](https://zen-browser.app) on Linux.

Click a profile and Zen opens with it. Create, rename, re-icon and delete profiles without ever opening Zen's `about:profiles` page.

> **Unofficial project.** Not affiliated with, endorsed by or supported by the Zen Browser team.

> **Status: in development.** The first release (0.1.0) is being assembled from a working personal tool. Until it is tagged, the install command below may not work yet. Follow the [pull requests](https://github.com/FedericoGrim/zen-profile-selector/pulls) to see progress.

## Features

- **Profile grid**: one card per Zen profile, each with its own emoji icon. Up to five cards share a row, then the grid switches to rows of three. The window sizes itself to its content and opens centered on your primary monitor.
- **Create profiles**: the "＋ New" card asks for a name and an icon, then creates the profile through Zen itself (`--CreateProfile`), even while Zen is running.
- **Edit profiles**: hover a card and click ✎ to rename it or change its icon. Renaming only changes the displayed name; the profile folder, with your bookmarks, passwords and history, is not touched.
- **Safe deletion**: you must type the profile name to confirm. Profiles that are open in Zen cannot be deleted, the last profile cannot be deleted, and the profile folder goes to your **Trash**, so it can be restored. A backup of `profiles.ini` is written before every change.
- **Works with any Zen install**: detects the Flatpak (`app.zen_browser.zen`) and native installs (`zen` / `zen-browser` on your `PATH`) automatically. If detection fails, set the Zen command and profiles folder by hand in **Settings** (⚙, top right).
- **English and Italian**: pick the language from the menu next to ⚙. The choice is remembered.

## Requirements

- Linux with X11 or XWayland
- Python 3.9 or newer, with Tk (`sudo apt install python3-tk` on Debian, Ubuntu and Mint)
- [pipx](https://pipx.pypa.io)
- Zen Browser
- Optional: `gio` (to move deleted profiles to the Trash) and `xrandr` (to center the window on the primary monitor). Both ship with most desktops.

## Install

```bash
pipx install git+https://github.com/FedericoGrim/zen-profile-selector
```

Add it to your applications menu:

```bash
zen-profile-selector --install-desktop
```

Remove it from the menu with `--uninstall-desktop`, and uninstall it with `pipx uninstall zen-profile-selector`.

## Configuration

Everything is stored in `~/.config/zen-profile-selector/` (or `$XDG_CONFIG_HOME/zen-profile-selector/`):

| File | Contents |
|------|----------|
| `config.json` | Language, and the Zen command and profiles folder if you set them by hand |
| `profile_icons.json` | The icon of each profile, by name |

Leave the Zen command and profiles folder empty to let the selector detect them.

## How it works

The selector reads Zen's `profiles.ini` from the detected profiles folder:

- Flatpak: `~/.var/app/app.zen_browser.zen/.zen`
- Native: `~/.zen`

Creating a profile is delegated to Zen (`--CreateProfile`). Renaming and deleting edit `profiles.ini` directly, because Zen has no command for them. In that case the selector keeps the `[ProfileN]` sections numbered without gaps (Zen stops reading at the first gap), and moves the default profile to another one if needed.

## Limitations

- Linux only. Windows and macOS are not supported.
- On native Wayland, Tk cannot choose where the window opens, so centering depends on your window manager.
- Zen's newer experimental profile system ("Profile Groups") is not supported. Zen currently keeps it disabled.

## Contributing

Issues and pull requests are welcome.

- The project uses Git Flow: open pull requests against `develop`.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org).
- Set up the development environment and the checks that run on every commit:

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
```

```bash
.venv/bin/pre-commit install --hook-type pre-commit --hook-type commit-msg
```

- Run the tests with `.venv/bin/pytest`.

Design decisions are recorded in [docs/decisions.md](docs/decisions.md).

## License

[GNU General Public License v3.0 or later](LICENSE).
