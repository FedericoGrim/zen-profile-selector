from __future__ import annotations

import re

MAX_SINGLE_ROW = 5
MULTI_ROW_COLUMNS = 3


def grid_columns(count: int) -> int:
    """All cells share one row up to five, then rows of three."""
    return count if count <= MAX_SINGLE_ROW else MULTI_ROW_COLUMNS


def primary_monitor(xrandr_output: str) -> tuple[int, int, int, int] | None:
    """Position and size (x, y, width, height) of the primary monitor from `xrandr --listmonitors`."""
    match = re.search(r"\+\*\S+ (\d+)/\d+x(\d+)/\d+\+(\d+)\+(\d+)", xrandr_output)
    if not match:
        return None
    width, height, x, y = map(int, match.groups())
    return x, y, width, height
