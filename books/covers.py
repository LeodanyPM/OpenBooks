import io
import random

from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile

COVER_COLORS = [
    (52, 73, 94), (44, 62, 80), (39, 174, 96), (41, 128, 185),
    (142, 68, 173), (192, 57, 43), (211, 84, 0), (22, 160, 133),
    (127, 140, 141), (30, 58, 95), (120, 60, 30), (70, 50, 100),
]


def _load_font(size):
    return ImageFont.load_default(size)


def _wrap_text(draw, text, font, max_width):
    lines = []
    current = ""
    for word in text.split():
        test = f"{current} {word}".strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def create_placeholder_cover(book):
    width, height = 600, 900
    color = random.choice(COVER_COLORS)

    img = Image.new("RGB", (width, height), color)
    draw = ImageDraw.Draw(img)

    draw.rectangle([25, 25, width - 26, height - 26], outline=(255, 255, 255), width=2)

    font_title = _load_font(46)
    title_lines = _wrap_text(draw, book.title, font_title, width - 120)
    y = 180
    for line in title_lines[:6]:
        draw.text((60, y), line, font=font_title, fill=(255, 255, 255))
        y += 62

    draw.line([(60, height - 200), (width - 60, height - 200)], fill=(255, 255, 255), width=2)

    font_author = _load_font(30)
    draw.text((60, height - 160), book.author[:40], font=font_author, fill=(255, 255, 255))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    book.cover.save(f"cover_{book.pk}.png", ContentFile(buffer.getvalue()), save=True)
