---
name: polished-slide-visuals
description: Build designer-quality .pptx slides with real drop shadows, smooth bezier curves, gradient fills, true arrowheads, and rich SVG iconography — visual treatments python-pptx's native shapes can't render reliably in Keynote or Google Slides. Use this skill whenever the user wants slides that "look great", asks for a "modern deck", "polished presentation", "designer-quality" slides, mentions a designer-provided palette, or pushes back on the visual quality of a python-pptx-generated deck. Also prefer this over raw python-pptx for any slide beyond plain text + bullets — the visual delta is large and the iteration cost is small. Layers an HTML/SVG → headless-Chrome PNG → python-pptx embed pipeline on top of Anthropic's `document-skills:pptx` skill.
---

# Polished slide visuals via HTML/SVG → PNG → pptx

This skill layers a rich-visual pipeline on top of Anthropic's `document-skills:pptx` skill. Use the **pptx skill** for the .pptx scaffolding (creating the file, slide layouts, headlines, footers, page numbers, the Keynote/LibreOffice conversion-to-images workflow). Use **this skill's** HTML/SVG → headless-Chrome → PNG pipeline for the **body** of any visually rich slide.

## Why we don't draw the body in python-pptx

python-pptx exposes basic shapes (`MSO_SHAPE.RECTANGLE`, `ROUNDED_RECTANGLE`, `OVAL`, etc.) and you can attach OOXML effects (`<a:outerShdw>`) to fake polished design. In practice, the moment a slide needs any of the following, the python-pptx path produces output that looks wrong in Keynote/Google Slides — and Keynote/Google Slides are how most people open .pptx files:

- **Real drop shadows.** OOXML `<a:outerShdw>` renders in PowerPoint but degrades visibly in Keynote. Fake offset rects look like misaligned border ghosts.
- **Smooth curves.** Bezier decay curves (e.g. a forgetting-curve chart), arcs with arrowheads, gradient-filled areas under a chart. Python-pptx has no good primitive for these.
- **True arrowheads.** `slide.shapes.add_connector(2, ...)` arrows in python-pptx do **not** render arrowheads when the .pptx is opened in Keynote or imported into Google Slides. They render as plain lines. Filled block arrows (`MSO_SHAPE.RIGHT_ARROW`) work but look wedge-y when you actually want a connector-style flow with a clean tip.
- **Gradient fills, marker-based SVG arrowheads, soft Gaussian shadows** on individual elements.
- **Real iconography.** Hand-crafted SVG icons (book, scales, person, globe, feedback-loop, code-brackets-with-check) read as design; unicode glyphs and generic Office shapes read as a draft.
- **Typography polish.** Italic Lora/Georgia headlines, mixed serif + sans, color-coded inline emphasis (e.g. ser in green, estar in blue inside a Spanish sentence).

The fix is to render the slide's body as an HTML page with inline SVG, screenshot it with headless Chrome, and embed the PNG into the .pptx slide via `slide.shapes.add_picture()`. The headline, footer, and page number stay as native python-pptx text so they're still editable in PowerPoint.

## The pipeline

```
HTML + inline SVG  ──▶  headless Chrome screenshot  ──▶  PNG  ──▶  python-pptx add_picture()
```

### 1. Slide layout — the dimensions that work

A 16:9 .pptx slide is 13.333" × 7.5". Headline, footer, and page-number chrome eat vertical room. Use these positions:

| Element        | Position                                | Why                                                            |
|----------------|------------------------------------------|----------------------------------------------------------------|
| Headline text  | `x=0.6, y=0.40, w=SLIDE_W-1.2, h=0.95`   | Pushed up vs. the natural `y=0.65` so the body image gets more room |
| Green underline rule | `y=1.32`, length `1.5"`            | Tight rule under the headline — the deck's repeating motif       |
| Embedded image | `x=0.42, y=1.50, w=12.50, h=5.68`        | Fills 94% of slide width, sits between underline and footer band  |
| Footer band    | `y=7.18–7.50`                             | Pale-blue strip with company name + page number                  |

`img_h = 5.68` comes from preserving the HTML canvas aspect: `12.5 * (1000/2200) = 5.68`. The image ends at `1.50 + 5.68 = 7.18`, exactly meeting the footer band — no overlap, no gap.

### 2. HTML canvas

```html
<div class="wrap" style="width: 2200px; height: 1000px; padding: 25px 40px; box-sizing: border-box;">
  …
</div>
```

`2200 × 1000` (2.2:1) matches the embedded image's aspect exactly, so Chrome's screenshot fills the canvas with no letterboxing. The `padding: 25px 40px` is intentionally tight — see the "Trust Keynote, not the browser" section below.

### 3. Rendering with headless Chrome (via Bash, not Playwright MCP)

Use Chrome directly via the `Bash` tool:

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --screenshot=/tmp/slide_05_body.png \
  --window-size=2200,1000 \
  file:///tmp/slide_05_body.html
```

Chrome reads `file://` URLs in headless mode — no HTTP server required.

**Don't use Playwright MCP for this.** In practice we hit recurring `claude-opus-4-7 is temporarily unavailable` safety-classifier failures on Playwright MCP that blocked the whole workflow. Chrome via Bash has no such issue, is faster, and is one less moving part.

### 4. Embedding in python-pptx

```python
img_w = 12.5
img_h = img_w * (1000 / 2200)  # 5.68 — preserve canvas aspect
img_x = (SLIDE_W - img_w) / 2  # 0.42 — center horizontally
img_y = 1.50
slide.shapes.add_picture("/tmp/slide_05_body.png",
                          Inches(img_x), Inches(img_y),
                          Inches(img_w), Inches(img_h))
```

The headline + footer stay as native python-pptx text using the scaffolding from `document-skills:pptx` (or your own helpers).

## Trust Keynote, not the browser

The browser preview of the HTML and the Keynote-rendered slide differ in ways that consistently catch you out. Internalize these or you'll waste an iteration on every slide:

- **Fonts in the browser preview look much larger than they read on the slide.** Bump every font size 15–30% beyond what feels right in Chrome.
- **Whitespace inside the HTML canvas reads as huge dead zones on the slide.** Tighten wrap padding aggressively — `25–30px` on a 2200px canvas, not the `50–80px` you'd default to.
- **Content that looks vertically centered in the browser drifts to the top in Keynote.** Use `justify-content: center` or `flex: 1` on inner sections explicitly; don't assume.

The only reliable verification is to render the .pptx, export to PNG via Keynote, downsample, and look at the actual rendered slide:

```bash
# Export the deck to per-slide PNGs via Keynote AppleScript
osascript <<'EOF'
tell application "Keynote"
    activate
    set theDoc to open POSIX file "/path/to/presentation.pptx"
    delay 3
    export theDoc to POSIX file "/tmp/deck_slides" as slide images with properties {image format:PNG, skipped slides:false}
    delay 2
    close theDoc saving no
end tell
EOF

# Downsample for the Read tool (which caps at 2000px per dimension)
sips -Z 1800 /tmp/deck_slides/disneylingo_slides.005.png --out /tmp/preview_05.png
```

Then `Read` the downsampled PNG. **This is the only ground-truth view.** Browser previews lie about font scale, content density, and vertical centering. Never declare a slide done from a browser preview alone.

## HTML/CSS pitfalls (real bugs, not theory)

These tripped us up repeatedly. Internalize them before writing more HTML.

### Flex children only stretch when both conditions hold

A `.card` inside `.wrap` will only stretch to fill `.wrap`'s height when:
1. `.wrap` has an explicit `height` (or is a flex item that's growing), AND
2. `.wrap` has `align-items: stretch` (the default, but easy to clobber with `center` or `flex-start` upstream).

When your cards look stranded in the middle of the canvas — content tight in the center, big empty top and bottom — this is almost always why.

### Content drifts to the top by default

A `display: flex; flex-direction: column;` container with content that doesn't fill its height stacks content at the top, leaving empty bottom space. Pick the fix that matches the visual intent:

- `justify-content: center` on the container — centers everything as a block.
- `justify-content: space-between` — pushes first/last to top/bottom, distributes middle items.
- `flex: 1` on the section that should absorb the slack — keeps the others at natural height.

### Global SVG-over-canvas connectors are fragile

We tried this for a hub-and-spoke unit diagram (one absolutely-positioned SVG layered over the whole canvas, with paths from atoms on the right to a unit card on the left). The coordinate math kept misaligning because:

- `position: absolute; inset: 0;` resolves relative to the nearest positioned ancestor's *padding box*, not its content box.
- `preserveAspectRatio="none"` non-uniformly stretches the viewBox, so paths that look right in the source coordinates land in unexpected places after rendering.

**Prefer per-component inline SVG arrows.** Put a small left/right arrow SVG next to each row that needs an arrow, sized in CSS, with no global coordinate system:

```html
<div class="atom-row">
  <div class="arrow">
    <svg width="120" height="52" viewBox="0 0 92 40">
      <polygon points="0,20 28,4 28,14 92,14 92,26 28,26 28,36" fill="#79DF4D"/>
    </svg>
  </div>
  <div class="atom">…</div>
</div>
```

Reserve global-SVG-over-canvas for cases where you genuinely need it — a trident connector spanning the whole slide, or a forgetting-curve chart that *is* the body. Even then, render the SVG at a fixed `viewBox` matching the actual layout dimensions and verify with the Read tool after every change.

## Design-system discipline

Designers will hand you a palette. Stick to it exactly. Supporting tones (navy ink for body text, graphite grey for captions, pale-blue / pale-green for card fills derived from the brand colors) are fine — they're hierarchy, not new brand colors.

Two rules:

1. **Never invent a fourth brand color.** If the designer gave you green + blue + background, do not introduce coral, peach, yellow, or any other warm tone "for visual interest". When the deck needs more punch, find it through typography, layout density, contrast, or motion (drop shadows, gradients within the existing palette) — not new hues. Users notice palette drift instantly.

2. **Pick one repeating motif and use it everywhere.** Our deck used a thick green underline under every content headline. That single motif — visible on every slide — built coherence the user recognized immediately. Other options: a small colored dot in a fixed corner, icons in colored circles of a single color, a single accent stripe weight. Pick one. Repeat it on every content slide.

## Iteration loop

Don't ship after one render. The loop is:

1. **Draft** HTML, render to PNG via headless Chrome, eyeball with `Read`.
2. **Embed** the PNG in .pptx via `add_picture()`; regenerate the .pptx.
3. **Export** the .pptx to PNGs via Keynote AppleScript.
4. **Downsample** with `sips -Z 1800`.
5. **Inspect** the downsampled slide PNG via `Read`. Check for: content drift to top/bottom, font readability, empty dead zones, alignment with headline + footer, palette discipline.
6. **Adjust** HTML padding/fonts/flex and return to step 1.

Expect 2–4 cycles per slide before the visuals click. The browser preview will lead you astray on every cycle — only the Keynote export tells the truth.

## File layout

Keep things organized so each slide iterates independently:

```
/tmp/slide_02_problem.html     # source HTML for slide 2 body
/tmp/slide_02_problem.png      # rendered 2200×1000 PNG
/tmp/slide_03_personal.html
/tmp/slide_03_personal.png
…
/tmp/generate_deck.py          # python-pptx generator (embeds each PNG)
~/path/to/presentation.pptx    # final output
/tmp/deck_slides/              # Keynote-exported PNGs (one per slide)
/tmp/preview_02.png            # downsampled for Read-tool inspection
```

Re-rendering one slide is `chrome --screenshot ... slide_02.html` → `python3 generate_deck.py` → Keynote export → `sips` → `Read`. Each slide's HTML lives on its own; the generator references each PNG by path.

## What to take from `document-skills:pptx`

Use that skill for:
- Creating the .pptx file structure, sizing the slide (`prs.slide_width = Inches(13.333)`).
- Headline + footer + page-number scaffolding (or write your own helpers in the same spirit).
- The Keynote / LibreOffice slide-to-PNG conversion pattern (this skill's `osascript` block is one variant — `soffice --headless --convert-to pdf` + `pdftoppm` is another).
- Text extraction with `markitdown` when reading an existing deck.

Don't follow that skill's "Design Ideas" section verbatim. Its palette table and font pairings are good starting points, but the design-system discipline above (single motif, no fourth color, designer-provided palette only) is stricter and produces better results when a real designer is involved — which is the case any time this skill is the right tool.
