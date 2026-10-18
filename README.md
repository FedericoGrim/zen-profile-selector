# zen-profile-selector

A small, fast profile picker for [Zen Browser](https://zen-browser.app) on Linux.

Click a profile and Zen opens with it. Create, rename, re-icon and delete profiles without ever opening Zen's `about:profiles` page.

> **Unofficial project.** Not affiliated with, endorsed by or supported by the Zen Browser team.

![The profile grid](https://raw.githubusercontent.com/FedericoGrim/zen-profile-selector/main/docs/screenshots/profiles.png)

## Features

- **Profile grid**: one card per Zen profile, each with its own emoji icon. Up to five cards share a row, then the grid switches to rows of three. The window sizes itself to its content and opens centered on your primary monitor.
- **Create profiles**: the "＋ New" card asks for a name and an icon, then creates the profile through Zen itself (`--CreateProfile`), even while Zen is running.
- **Edit profiles**: hover a card and click ✎ to rename it or change its icon. Renaming only changes the displayed name; the profile folder, with your bookmarks, passwords and history, is not touched.
- **Safe deletion**: you must type the profile name to confirm. Profiles that are open in Zen cannot be deleted, the last profile cannot be deleted, and the profile folder goes to your **Trash**, so it can be restored. A backup of `profiles.ini` is written before every change.
- **Works with any Zen install**: detects the Flatpak (`app.zen_browser.zen`) and native installs (`zen` / `zen-browser` on your `PATH`) automatically. If detection fails, set the Zen command and profiles folder by hand in **Settings** (⚙, top right).
- **English and Italian**: pick the language from the menu next to ⚙. The choice is remembered.
- **Update notice**: once a day the selector checks PyPI in the background and, when a newer version exists, shows a small banner. Click **Update** to run `pipx upgrade` for you, then **Restart**; installs not made with pipx get the command to copy instead. Turn it off in **Settings**, where you can also see the installed version.

| Edit a profile | Settings |
|---|---|
| ![Edit profile dialog](https://raw.githubusercontent.com/FedericoGrim/zen-profile-selector/main/docs/screenshots/edit-profile.png) | ![Settings dialog](https://raw.githubusercontent.com/FedericoGrim/zen-profile-selector/main/docs/screenshots/settings.png) |

## Requirements

- Linux with X11 or XWayland, or Windows 10/11 (Windows support is in beta)
- Python 3.9 or newer, with Tk (`sudo apt install python3-tk` on Debian, Ubuntu and Mint; included in the python.org installer for Windows)
- [pipx](https://pipx.pypa.io)
- Zen Browser
- Optional on Linux: `xrandr`, to center the window on the primary monitor. It ships with most desktops.

## Install

```bash
pipx install zen-profile-selector
```

To try the latest development version instead, install from GitHub with `pipx install git+https://github.com/FedericoGrim/zen-profile-selector`.

Add it to your applications menu:

```bash
zen-profile-selector --install-desktop
```

Update with `pipx upgrade zen-profile-selector`. Remove it from the menu with `--uninstall-desktop`, and uninstall it with `pipx uninstall zen-profile-selector`.

## Configuration

Everything is stored in `~/.config/zen-profile-selector/` (or `$XDG_CONFIG_HOME/zen-profile-selector/`):

| File | Contents |
|------|----------|
| `config.json` | Language, and the Zen command and profiles folder if you set them by hand |
| `profile_icons.json` | The icon of each profile, by name |
| `update_check.json` | Date of the last update check, the latest version found and the one you dismissed |

Leave the Zen command and profiles folder empty to let the selector detect them.

## Privacy

The selector sends no data about you. Its only network request is the update check: at most once a day it downloads the public `https://pypi.org/pypi/zen-profile-selector/json` page to read the latest version number. Untick **Check for updates at startup** in Settings to turn it off. It only updates when you click **Update**, and then it simply runs `pipx upgrade zen-profile-selector`.

## How it works

The selector reads Zen's `profiles.ini` from the detected profiles folder:

- Flatpak: `~/.var/app/app.zen_browser.zen/.zen`, or `~/.var/app/app.zen_browser.zen/config/zen` on installs that follow the XDG layout
- Native: `~/.zen`, or `~/.config/zen` (`$XDG_CONFIG_HOME/zen`) on installs made with Zen 1.18.6b or newer
- Windows: `%APPDATA%\zen`, with `zen.exe` found on the `PATH`, in `%ProgramFiles%\Zen Browser` or in `%LOCALAPPDATA%\Zen Browser`

On Linux, like Zen itself, it keeps using the old `.zen` folder while it exists. On Windows its own settings live in `%APPDATA%\zen-profile-selector`.

Creating a profile is delegated to Zen (`--CreateProfile`). Renaming and deleting edit `profiles.ini` directly, because Zen has no command for them; the previous version is kept as `profiles.ini.selector-bak`. In that case the selector keeps the `[ProfileN]` sections numbered without gaps (Zen stops reading at the first gap), and moves the default profile to another one if needed.

## Limitations

- Windows support is in beta, and `--install-desktop` is Linux only. macOS is not supported yet.
- On native Wayland, Tk cannot choose where the window opens, so centering depends on your window manager.
- Zen's newer experimental profile system ("Profile Groups") is not supported. Zen currently keeps it disabled.

## Contributing

Contributions are welcome: bug reports, translations, packaging and code. Start with [CONTRIBUTING.md](https://github.com/FedericoGrim/zen-profile-selector/blob/main/CONTRIBUTING.md), browse the [roadmap](https://github.com/FedericoGrim/zen-profile-selector/labels/roadmap) and the [`good first issue`](https://github.com/FedericoGrim/zen-profile-selector/labels/good%20first%20issue) label, and ask anything in [Discussions](https://github.com/FedericoGrim/zen-profile-selector/discussions).

Please follow the [Code of Conduct](https://github.com/FedericoGrim/zen-profile-selector/blob/main/CODE_OF_CONDUCT.md) and report security problems privately as described in [SECURITY.md](https://github.com/FedericoGrim/zen-profile-selector/blob/main/SECURITY.md). Design decisions are recorded in [docs/decisions.md](https://github.com/FedericoGrim/zen-profile-selector/blob/main/docs/decisions.md).

## Author

Made by Federico Grimaldi — federico.grimaldi2006@gmail.com

## License

[GNU General Public License v3.0 or later](https://github.com/FedericoGrim/zen-profile-selector/blob/main/LICENSE).
