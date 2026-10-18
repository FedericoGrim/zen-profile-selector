import sys

import pytest

from zen_profile_selector.emoji import WINDOWS_EMOJI_FONT, emoji_image


def test_missing_font_or_pillow_gives_no_image():
    assert emoji_image("👤", 32, font_file="missing-emoji-font.ttf") is None


@pytest.mark.skipif(sys.platform != "win32", reason="Segoe UI Emoji ships with Windows")
def test_windows_emoji_are_rendered_in_color():
    image = emoji_image("💼", 32, font_file=WINDOWS_EMOJI_FONT)
    assert image is not None
    colors = {color[:3] for _, color in image.getcolors(image.width * image.height) if color[3]}
    assert len(colors) > 10


@pytest.mark.skipif(sys.platform != "win32", reason="Segoe UI Emoji ships with Windows")
def test_windows_emoji_images_are_square():
    for emoji in ("🎓", "📌", "✈️"):
        image = emoji_image(emoji, 32)
        assert image is not None
        assert image.width == image.height
