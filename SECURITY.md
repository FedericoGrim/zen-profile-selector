# Security Policy

## Supported versions

Only the latest release receives security fixes.

| Version | Supported |
|---------|-----------|
| latest release | ✅ |
| older releases | ❌ |

## What counts as a security issue

zen-profile-selector edits Zen's `profiles.ini` and moves profile folders to the Trash, so please report privately anything that could:

- delete, overwrite or expose profile data (bookmarks, passwords, history) without the user asking;
- run unexpected commands through the Zen command setting or the menu entry;
- read or write files outside the Zen profiles folder and the selector's own config folder.

Ordinary bugs (a crash, a wrong layout, a profile that does not open) belong in a normal [issue](https://github.com/FedericoGrim/zen-profile-selector/issues/new/choose).

## Reporting a vulnerability

Please **do not** open a public issue.

- Preferred: open a private report with [GitHub security advisories](https://github.com/FedericoGrim/zen-profile-selector/security/advisories/new).
- Or email **federico.grimaldi2006@gmail.com** with "zen-profile-selector security" in the subject.

Include the version, how Zen is installed (Flatpak or native), the steps to reproduce and what an attacker could achieve.

You will get an answer within 7 days. Once a fix is released, the report is published with credit to you, unless you prefer to stay anonymous.
