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

## 004 — Publish releases to PyPI with trusted publishing
- **Date:** 2026-10-17
- **Status:** Accepted
- **Context:** Installing from the Git URL works but gives no download statistics and a longer install command.
- **Decision:** Every release created by release-please is built from its tag, checked with `twine check`, and uploaded to PyPI as `zen-profile-selector` by the `publish` job in the `pypi` environment, authenticated with PyPI trusted publishing (OIDC). The README recommends `pipx install zen-profile-selector`.
- **Alternatives:** A PyPI API token stored as a repository secret (a long-lived credential to leak and rotate); keeping Git-only installs (no stats, longer command).
- **Consequences:** No publishing secret exists in the repository. A version number can be uploaded only once, so a broken upload is fixed with a new patch release.

## 005 — Automatic back-merge after each release
- **Date:** 2026-10-18
- **Status:** Accepted
- **Context:** After every release `main` must be merged back into `develop`. Doing it by hand was repetitive and easy to get wrong (a rebase merge in #36 left `develop` behind `main`).
- **Decision:** The `back-merge` job of the release workflow creates `chore/back-merge-X.Y.Z` from `main`, merges `develop` into it, opens the pull request into `develop` and enables auto-merge with a merge commit. Pull requests opened by the GitHub Actions bot wait for a manual approval before their `pull_request` CI starts, so the job also starts CI on the branch with `workflow_dispatch`; its checks satisfy the `develop` branch protection.
- **Alternatives:** Keeping the manual back-merge; a personal access token so the bot's pull request triggers CI normally (a long-lived secret to manage).
- **Consequences:** No manual step after a release and no new secret. The back-merge only carries changes already merged and checked on `main`. "Allow auto-merge" is enabled in the repository settings. If the merge of `develop` conflicts, the job fails and the back-merge is done by hand.
