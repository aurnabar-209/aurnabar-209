"""
fetch_contributions.py

Pulls your real contribution calendar from GitHub's public HTML fragment
(no GraphQL API, no personal access token needed) and writes
data/contributions.json with raw days plus derived stats.

Usage:
    python scripts/fetch_contributions.py
"""
import json
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "aurnabar-209"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = Path("data/contributions.json")


def fetch_days() -> list[dict]:
    resp = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=30,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    # GitHub renders each day as a <td> (or <rect> in newer markup) with
    # data-date and either data-level or a data-count/tooltip we can parse.
    cells = soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day")

    if not cells:
        raise RuntimeError(
            "No contribution cells found -- GitHub may have changed its "
            "markup. Inspect the fetched HTML and update the selector."
        )

    tooltip_map = {}
    for tt in soup.select("tool-tip"):
        tid = tt.get("for")
        if tid:
            tooltip_map[tid] = tt.get_text(strip=True)

    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue
        level = cell.get("data-level")
        level = int(level) if level is not None else None

        count = 0
        tip_id = cell.get("id")
        tip_text = tooltip_map.get(tip_id, "")
        m = re.search(r"([\d,]+)\s+contribution", tip_text)
        if m:
            count = int(m.group(1).replace(",", ""))
        elif "No contributions" in tip_text:
            count = 0

        days.append({"date": date, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    # current streak: walk backward from the most recent day
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    # longest streak anywhere in the window
    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly_totals: dict[str, int] = {}
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly_totals[month] = monthly_totals.get(month, 0) + d["count"]

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


if __name__ == "__main__":
    days = fetch_days()
    stats = derive_stats(days)
    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps({"days": days, "stats": stats}, indent=2))
    print(f"wrote {OUT_PATH} ({len(days)} days, {stats['total_contributions']} contributions)")
