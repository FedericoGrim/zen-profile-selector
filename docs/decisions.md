# Decision Log

Significant decisions for this project. Newest at the bottom. Entries are never deleted.

---

## 001 — License: GPL-3.0-or-later
- **Date:** 2026-10-16
- **Status:** Accepted
- **Context:** The project is published as an open source desktop tool, independent from Zen Browser.
- **Decision:** Release under the GNU General Public License v3.0 or later.
- **Alternatives:** AGPL-3.0 (its network-use clause never applies to a local desktop app); MIT (does not keep modified versions open).
- **Consequences:** Anyone distributing modified versions must publish their source under the same license. Compatible with the MIT-licensed dependency (customtkinter).

## 002 — Distribution with pipx, XDG configuration, Linux only
- **Date:** 2026-10-16
- **Status:** Accepted
- **Context:** Users need a one-command install that works with both the Flatpak and the native Zen builds.
- **Decision:** Ship a Python package installable with `pipx`, exposing the `zen-profile-selector` command; store settings in `$XDG_CONFIG_HOME/zen-profile-selector/`; support Linux only.
- **Alternatives:** Flatpak or AppImage of the selector (it must run `flatpak`/`zen` on the host, which a sandbox makes harder); config next to the code (breaks on upgrades and shared installs).
- **Consequences:** Requires Python 3.9+ and Tk on the host. Windows and macOS are out of scope.

## 003 — Rebase merge for pull requests into develop
- **Date:** 2026-10-16
- **Status:** Accepted
- **Context:** With merge commits, GitHub always puts the pull request title in the merge commit, and release-please listed every change twice in the 0.1.0 changelog (once from the commit, once from the PR title).
- **Decision:** Merge pull requests into `develop` with "Rebase and merge"; keep merge commits only for release (`develop` → `main`) and back-merge (`main` → `develop`) pull requests, whose `chore:` titles are not listed in the changelog. Squash merging is disabled.
- **Alternatives:** Blank merge commit messages (not allowed by GitHub with merge commits); squash merges (lose the micro commits); non-conventional PR titles (easy to get wrong for contributors).
- **Consequences:** Each change appears once in the changelog and micro commits stay visible. The 0.1.0 section keeps its duplicates, since the changelog is never edited by hand.
