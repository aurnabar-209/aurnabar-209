"""
make_info_card.py

Hand-authors a small neofetch-style SVG: a title bar plus colored
key/value rows that fade + slide in on a stagger.

Set STATIC=1 to emit a frozen (non-animated) frame, handy for local
Quick Look previews.

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py
"""
import os
from pathlib import Path

# ---- edit this block to describe yourself -------------------------------
USERNAME = "aurnabar-209"
TITLE_BAR = f"{USERNAME}@github"
ROWS = [
    ("Now", "Building things & shipping code"),
    ("Prev", "Add your previous role / focus here"),
    ("Stack", "Python . JavaScript . SQL . ..."),
    ("Highlights", "Add a stat or achievement here"),
]
# ---------------------------------------------------------------------------

WIDTH = 490
ROW_H = 34
TOP_PAD = 70
STAGGER = 0.18
KEY_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"

STATIC = os.environ.get("STATIC") == "1"


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_svg() -> str:
    height = TOP_PAD + len(ROWS) * ROW_H + 20

    animation_css = "" if STATIC else f"""
      .row {{
        opacity: 0;
        transform: translateX(-12px);
        animation: rowIn 0.5s ease-out forwards;
      }}
      @keyframes rowIn {{
        to {{ opacity: 1; transform: translateX(0); }}
      }}
    """

    style = f"""
    <style>
      .card-bg {{ fill: {BG}; stroke: {BORDER}; stroke-width: 1; }}
      .titlebar {{ fill: {BORDER}; }}
      .title-text {{
        font-family: 'SFMono-Regular', Consolas, Menlo, monospace;
        font-size: 13px; fill: #8b949e;
      }}
      .key {{
        font-family: 'SFMono-Regular', Consolas, Menlo, monospace;
        font-size: 14px; font-weight: bold; fill: {KEY_COLOR};
      }}
      .value {{
        font-family: 'SFMono-Regular', Consolas, Menlo, monospace;
        font-size: 14px; fill: {VALUE_COLOR};
      }}
      {animation_css}
    </style>
    """

    dots = f"""
    <circle cx="20" cy="17" r="6" fill="#ff5f56"/>
    <circle cx="40" cy="17" r="6" fill="#ffbd2e"/>
    <circle cx="60" cy="17" r="6" fill="#27c93f"/>
    """

    rows_svg = []
    for i, (key, value) in enumerate(ROWS):
        y = TOP_PAD + i * ROW_H
        delay = "" if STATIC else f'style="animation-delay:{round(i * STAGGER, 2)}s"'
        rows_svg.append(f"""
    <g class="row" {delay}>
      <text x="24" y="{y}" class="key">{escape_xml(key)}</text>
      <text x="24" y="{y + 18}" class="value">{escape_xml(value)}</text>
    </g>""")

    svg = f"""<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg">
{style}
  <rect class="card-bg" x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8"/>
  <path class="titlebar" d="M0.5,8 a8,8 0 0 1 8,-8 h{WIDTH - 17} a8,8 0 0 1 8,8 v26 h-{WIDTH - 1} z"/>
  {dots}
  <text x="{WIDTH / 2}" y="22" class="title-text" text-anchor="middle">{escape_xml(TITLE_BAR)}</text>
  {''.join(rows_svg)}
</svg>"""
    return svg


if __name__ == "__main__":
    Path("info-card.svg").write_text(build_svg())
    print("wrote info-card.svg" + (" (static)" if STATIC else ""))

