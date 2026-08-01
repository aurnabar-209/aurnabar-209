"""
render_heatmap_svg.py

Reads data/contributions.json and draws the classic 53-week x 7-day
calendar as rounded, colored boxes that slide in diagonally once, then
freeze (no looping "glow").

Usage:
    python scripts/render_heatmap_svg.py
"""
import json
from pathlib import Path

DATA_PATH = Path("data/contributions.json")
OUT_PATH = Path("contrib-heatmap.svg")

# none -> brightest (level 5 is a neon top end)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

BOX = 11
GAP = 3
CELL = BOX + GAP
LEFT_PAD = 30
TOP_PAD = 20
REVEAL_STEP = 0.012  # seconds per diagonal step, keyed on (col + row)
REVEAL_DUR = 0.25


def level_from_count(count: int) -> int:
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    if count <= 15:
        return 4
    return 5


def build_svg(days: list[dict], stats: dict) -> str:
    # bucket days into 53 columns x 7 rows (Sun-Sat), most recent last
    weeks: list[list[dict]] = []
    week: list[dict] = []
    for d in days:
        from datetime import datetime
        dow = datetime.strptime(d["date"], "%Y-%m-%d").weekday()  # Mon=0
        dow = (dow + 1) % 7  # convert to Sun=0
        if dow == 0 and week:
            weeks.append(week)
            week = []
        week.append({**d, "dow": dow})
    if week:
        weeks.append(week)

    n_cols = len(weeks)
    width = LEFT_PAD + n_cols * CELL + 20
    height = TOP_PAD + 7 * CELL + 60

    style = f"""
    <style>
      .box {{
        opacity: 0;
        animation: reveal {REVEAL_DUR}s ease-out forwards;
      }}
      @keyframes reveal {{
        from {{ opacity: 0; transform: translate(-4px, -4px); }}
        to   {{ opacity: 1; transform: translate(0, 0); }}
      }}
      .legend-text, .footer-text {{
        font-family: 'SFMono-Regular', Consolas, Menlo, monospace;
        font-size: 11px; fill: #8b949e;
      }}
    </style>
    """

    boxes = []
    for col, wk in enumerate(weeks):
        for cell in wk:
            row = cell["dow"]
            level = cell["level"] if cell.get("level") is not None else level_from_count(cell["count"])
            level = max(0, min(5, level))
            x = LEFT_PAD + col * CELL
            y = TOP_PAD + row * CELL
            delay = round((col + row) * REVEAL_STEP, 3)
            boxes.append(
                f'<rect class="box" x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                f'rx="2" fill="{PALETTE[level]}" style="animation-delay:{delay}s">'
                f'<title>{cell["date"]}: {cell["count"]} contributions</title></rect>'
            )

    legend_x = width - 160
    legend_y = height - 22
    legend_boxes = "".join(
        f'<rect x="{legend_x + 40 + i * (BOX + 2)}" y="{legend_y - 9}" '
        f'width="{BOX}" height="{BOX}" rx="2" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )

    total = stats.get("total_contributions", 0)
    footer = f'<text x="{LEFT_PAD}" y="{height - 12}" class="footer-text">{total:,} contributions in the last year</text>'
    legend = (
        f'<text x="{legend_x}" y="{legend_y}" class="legend-text">Less</text>'
        f"{legend_boxes}"
        f'<text x="{legend_x + 40 + len(PALETTE) * (BOX + 2) + 6}" y="{legend_y}" class="legend-text">More</text>'
    )

    svg = f"""<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
{style}
{''.join(boxes)}
{footer}
{legend}
</svg>"""
    return svg


if __name__ == "__main__":
    if not DATA_PATH.exists():
        raise SystemExit(f"{DATA_PATH} not found. Run fetch_contributions.py first.")
    payload = json.loads(DATA_PATH.read_text())
    svg = build_svg(payload["days"], payload["stats"])
    OUT_PATH.write_text(svg)
    print(f"wrote {OUT_PATH}")
