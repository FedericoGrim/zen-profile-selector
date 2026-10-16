from zen_profile_selector.layout import grid_columns, primary_monitor

TWO_MONITORS = """Monitors: 2
 0: +*HDMI-0 1920/527x1080/296+1080+840  HDMI-0
 1: +DP-2 1080/527x1920/296+0+0  DP-2
"""

NO_PRIMARY = """Monitors: 1
 0: +DP-2 1080/527x1920/296+0+0  DP-2
"""


def test_up_to_five_cells_share_one_row():
    for count in range(1, 6):
        assert grid_columns(count) == count


def test_six_or_more_cells_use_three_columns():
    for count in (6, 7, 9, 12):
        assert grid_columns(count) == 3


def test_primary_monitor_is_read_from_xrandr():
    assert primary_monitor(TWO_MONITORS) == (1080, 840, 1920, 1080)


def test_no_primary_monitor_gives_none():
    assert primary_monitor(NO_PRIMARY) is None
    assert primary_monitor("") is None
