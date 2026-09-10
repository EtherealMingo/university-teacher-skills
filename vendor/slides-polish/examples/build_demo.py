#!/usr/bin/env python3
"""Build a 2-slide before/after deck demonstrating the polished-slide-visuals pipeline.

- Slide 1 (BEFORE): one slide drawn with raw python-pptx primitives. Drop shadows are
  fake offset rects, the arrow uses python-pptx's connector (which renders WITHOUT an
  arrowhead in Keynote/Google Slides), the icons are basic unicode glyphs.

- Slide 2 (AFTER): the same content, rendered as an HTML page (example_body.html) and
  embedded as a PNG via slide.shapes.add_picture(). Real soft drop shadows, a true
  arrow with arrowhead, smooth SVG iconography.

Usage:
  # 1. Render the polished body via headless Chrome:
  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\
    --headless --disable-gpu --no-sandbox --hide-scrollbars \\
    --screenshot=$(pwd)/example_body.png \\
    --window-size=2200,1000 \\
    file://$(pwd)/example_body.html
  # 2. Generate the deck:
  python3 build_demo.py
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

HERE = Path(__file__).parent
OUT = HERE / "demo.pptx"
BODY_PNG = HERE / "example_body.png"  # must be pre-rendered (see header)

# Palette
BG = RGBColor(0xFD, 0xFD, 0xFD)
INK = RGBColor(0x1B, 0x2B, 0x4A)
GRAPHITE = RGBColor(0x5C, 0x6B, 0x80)
BLUE = RGBColor(0x70, 0xB4, 0xFF)
BLUE_DEEP = RGBColor(0x3D, 0x82, 0xD0)
GREEN = RGBColor(0x79, 0xDF, 0x4D)
GREEN_DEEP = RGBColor(0x4D, 0xA8, 0x2A)
PALE_BLUE = RGBColor(0xE9, 0xF1, 0xFC)
SHADOW = RGBColor(0xCF, 0xD6, 0xE2)

SLIDE_W = 13.333
SLIDE_H = 7.5

prs = Presentation()
prs.slide_width = Inches(SLIDE_W)
prs.slide_height = Inches(SLIDE_H)
BLANK = prs.slide_layouts[6]


def add_text(slide, l, t, w, h, text, size, color, font="Calibri",
             bold=False, italic=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.color.rgb = color
    r.font.bold = bold
    r.font.italic = italic


def set_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


# ───────────────────────────── SLIDE 1: BEFORE (raw python-pptx) ──

s = prs.slides.add_slide(BLANK)
set_bg(s, BG)

# Big "BEFORE" badge top-left
add_text(s, 0.4, 0.25, 4.0, 0.5,
         "BEFORE  ·  raw python-pptx",
         size=14, color=GRAPHITE, bold=True)

# Title
add_text(s, 0.6, 0.85, SLIDE_W - 1.2, 1.0, "Atoms compose into Units",
         size=40, color=INK, font="Georgia", anchor=MSO_ANCHOR.TOP)

# Left card with a FAKE drop shadow (offset rect underneath — the python-pptx hack)
shadow = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                            Inches(0.66), Inches(2.66),
                            Inches(4.5), Inches(3.5))
shadow.fill.solid()
shadow.fill.fore_color.rgb = SHADOW
shadow.line.fill.background()
shadow.shadow.inherit = False

card1 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                           Inches(0.6), Inches(2.6),
                           Inches(4.5), Inches(3.5))
card1.fill.solid()
card1.fill.fore_color.rgb = PALE_BLUE
card1.line.fill.background()
card1.shadow.inherit = False

add_text(s, 0.9, 2.85, 3.9, 0.4, "VOCAB",
         size=12, color=BLUE_DEEP, bold=True)
add_text(s, 0.9, 3.5, 3.9, 1.2, "perro",
         size=44, color=INK, italic=True, font="Georgia",
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, 0.9, 5.0, 3.9, 0.4, "(dog)",
         size=18, color=GRAPHITE, italic=True, align=PP_ALIGN.CENTER)

# Right card (same hack)
shadow2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                             Inches(8.26), Inches(2.66),
                             Inches(4.5), Inches(3.5))
shadow2.fill.solid()
shadow2.fill.fore_color.rgb = SHADOW
shadow2.line.fill.background()
shadow2.shadow.inherit = False

card2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                           Inches(8.2), Inches(2.6),
                           Inches(4.5), Inches(3.5))
card2.fill.solid()
card2.fill.fore_color.rgb = PALE_BLUE
card2.line.fill.background()
card2.shadow.inherit = False

add_text(s, 8.5, 2.85, 3.9, 0.4, "UNIT",
         size=12, color=BLUE_DEEP, bold=True)
add_text(s, 8.5, 3.6, 3.9, 1.0, "Ordering food",
         size=32, color=INK, font="Georgia",
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(s, 8.5, 4.9, 3.9, 0.4, "a real-world ability",
         size=16, color=GRAPHITE, italic=True, align=PP_ALIGN.CENTER)

# Connector arrow between cards. In python-pptx, add_connector(2, ...) is supposed to
# be an arrow connector — but in Keynote and Google Slides the ARROWHEAD DOES NOT RENDER.
# It just shows up as a plain line.
connector = s.shapes.add_connector(2,
                                   Inches(5.2), Inches(4.35),
                                   Inches(8.15), Inches(4.35))
connector.line.color.rgb = GREEN
connector.line.width = Pt(6)

add_text(s, 5.0, 4.5, 3.3, 0.4, "composes into",
         size=12, color=GREEN_DEEP, italic=True, align=PP_ALIGN.CENTER)

add_text(s, 0.6, 6.6, SLIDE_W - 1.2, 0.5,
         "Drop shadows are offset-rect ghosts. The connector arrow has no arrowhead in Keynote.",
         size=14, color=GRAPHITE, italic=True, font="Georgia", align=PP_ALIGN.CENTER)


# ───────────────────────────── SLIDE 2: AFTER (HTML/SVG embed) ──

s = prs.slides.add_slide(BLANK)
set_bg(s, BG)

add_text(s, 0.4, 0.25, 4.0, 0.5,
         "AFTER  ·  HTML/SVG → PNG → embed",
         size=14, color=GREEN_DEEP, bold=True)

# Title (same as before)
add_text(s, 0.6, 0.85, SLIDE_W - 1.2, 1.0, "Atoms compose into Units",
         size=40, color=INK, font="Georgia", anchor=MSO_ANCHOR.TOP)

# Embed the pre-rendered HTML body PNG.
# Canvas is 2200x1000 px; embedded at 12.5" wide preserves aspect (h = 5.68")
# and lands exactly in the space between the headline and the bottom edge.
if BODY_PNG.exists():
    img_w = 12.5
    img_h = img_w * (1000 / 2200)
    img_x = (SLIDE_W - img_w) / 2
    img_y = 1.50
    s.shapes.add_picture(str(BODY_PNG),
                         Inches(img_x), Inches(img_y),
                         Inches(img_w), Inches(img_h))
else:
    add_text(s, 0.6, 3.0, SLIDE_W - 1.2, 1.0,
             "(Render example_body.html to example_body.png first — see header.)",
             size=18, color=GRAPHITE, italic=True, align=PP_ALIGN.CENTER)


prs.save(OUT)
print(f"wrote: {OUT}")
