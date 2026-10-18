from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image

WINDOWS_EMOJI_FONT = "seguiemj.ttf"


@cache
def emoji_image(emoji: str, size: int, font_file: str = WINDOWS_EMOJI_FONT) -> Image.Image | None:
    """The emoji drawn in color, cropped to its glyph; None without Pillow or the font.

    Tk on Windows draws emoji in a single color, so the selector shows them as images there.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont

        font = ImageFont.truetype(font_file, size)
    except (ImportError, OSError):
        return None
    left, top, right, bottom = font.getbbox(emoji)
    image = Image.new("RGBA", (right - left, bottom - top))
    ImageDraw.Draw(image).text((-left, -top), emoji, font=font, embedded_color=True)
    return image
