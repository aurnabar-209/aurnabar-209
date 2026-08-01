"""
make_ascii_svg.py

Converts source-prepped.png into avi-ascii.svg (here: an ASCII portrait
that "types" itself in, row by row, then freezes). Monochrome on purpose
-- per-character rainbow coloring is what makes ASCII art look noisy.

Usage:
    python scripts/make_ascii_svg.py
"""
from pathlib import Path

from PIL import Image

# bright (sparse) -> dark (dense). Leading space clears background to nothing.
RAMP = " .`:-=+*cs#%@"

COLS = 100                 # character columns
FONT_SIZE = 8               # px
CHAR_W = FONT_SIZE * 0.6    # approx monospace advance width
LINE_H = FONT_SIZE * 1.0
FILL_COLOR = "#9aa5b1"      # single light-gray fill -- keep it monochrome
ROW_DELAY = 0.045           # seconds between each row starting to type
WIPE_DUR = 0.35             # seconds for a single row's wipe


def image_to_ascii_rows(img_path: str, cols: int = COLS) -> list[str]:
    img = Image.open(img_path).convert("L")
    w, h = img.size
    # characters are roughly twice as tall as they are wide, so compensate
    aspect_correction = 0.5
    rows = max(1, round(cols * (h / w) * aspect_correction))
    img = img.resize((cols, rows))

    pixels = list(img.getdata())
    ramp_len = len(RAMP)
    lines = []
    for r in range(rows):
        row_pixels = pixels[r * cols:(r + 1) * cols]
        line = "".join(
            RAMP[min(ramp_len - 1, int((255 - p) / 256 * ramp_len))]
            for p in row_pixels
        )
        lines.append(line)
    return lines


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_svg(rows: list[str]) -> str:
    n_rows = len(rows)
    n_cols = max(len(r) for r in rows)
    width = n_cols * CHAR_W + 10
    height = n_rows * LINE_H + 10

    style = f"""
    <style>
      text {{
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: {FONT_SIZE}px;
        fill: {FILL_COLOR};
        white-space: pre;
      }}
      .cursor {{
        fill: {FILL_COLOR};
      }}
    </style>
    """

    body_parts = []
    for i, line in enumerate(rows):
        y = 8 + i * LINE_H
        begin = round(i * ROW_DELAY, 3)
        row_w = len(line) * CHAR_W
        clip_id = f"clip{i}"

        # clip rect wipes left -> right, then freezes at full width (fill="freeze")
        body_parts.append(f"""
    <clipPath id="{clip_id}">
      <rect x="0" y="{y - FONT_SIZE}" width="0" height="{LINE_H + 2}">
        <animate attributeName="width" from="0" to="{row_w}"
                 begin="{begin}s" dur="{WIPE_DUR}s" fill="freeze" />
      </rect>
    </clipPath>
    <g clip-path="url(#{clip_id})">
      <text x="5" y="{y}">{escape_xml(line)}</text>
    </g>
    <rect class="cursor" y="{y - FONT_SIZE + 1}" width="{CHAR_W * 0.8}" height="{FONT_SIZE}">
      <animate attributeName="x" from="5" to="{5 + row_w}"
               begin="{begin}s" dur="{WIPE_DUR}s" fill="freeze" />
      <animate attributeName="opacity" values="1;0" begin="{begin + WIPE_DUR}s"
               dur="0.01s" fill="freeze" />
    </rect>""")

    svg = f"""<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg">
{style}
{''.join(body_parts)}
</svg>"""
    return svg


if __name__ == "__main__":
    src = "source-prepped.png"
    if not Path(src).exists():
        raise SystemExit(
            f"'{src}' not found. Run prep_photo.py on your photo first."
        )
    rows = image_to_ascii_rows(src)
    svg = build_svg(rows)
    Path("avi-ascii.svg").write_text(svg)
    print("wrote avi-ascii.svg")
