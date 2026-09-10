#!/usr/bin/env python3
"""Stack the before/after PNGs into a single hero image for the README + LinkedIn post."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
BEFORE = HERE / "_before_mock.png"
AFTER = HERE / "example_body.png"
OUT = HERE / "before_after.png"

W, H = 2200, 1000
LABEL_H = 90
GAP = 30
HERO_W = W
HERO_H = LABEL_H + H + GAP + LABEL_H + H

hero = Image.new("RGB", (HERO_W, HERO_H), (253, 253, 253))
draw = ImageDraw.Draw(hero)

# Try to use a real font, fall back to default
def load_font(size):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Geneva.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()

label_font = load_font(48)
caption_font = load_font(28)

def draw_label(y, label, caption, label_color):
    # Label
    draw.text((60, y + 14), label, fill=label_color, font=label_font)
    # Caption to the right of the label
    label_bbox = draw.textbbox((60, y + 14), label, font=label_font)
    label_w = label_bbox[2] - label_bbox[0]
    draw.text((60 + label_w + 28, y + 30), caption,
              fill=(92, 107, 128), font=caption_font)

# BEFORE block
draw_label(0, "BEFORE",
           "raw python-pptx primitives — no arrowhead, missing shadows, generic icons",
           (180, 60, 60))
before_img = Image.open(BEFORE).convert("RGB")
hero.paste(before_img, (0, LABEL_H))

# AFTER block
y_after_label = LABEL_H + H + GAP
draw_label(y_after_label, "AFTER",
           "HTML/SVG → headless Chrome → PNG → embed in pptx",
           (61, 130, 90))
after_img = Image.open(AFTER).convert("RGB")
hero.paste(after_img, (0, y_after_label + LABEL_H))

hero.save(OUT, "PNG", optimize=True)
print(f"wrote: {OUT}  ({HERO_W}x{HERO_H})")
