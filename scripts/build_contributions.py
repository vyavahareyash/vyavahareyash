#!/usr/bin/env python3
"""Render the GitHub contribution calendar as a tile matching the README theme.

Runs daily in CI (.github/workflows/contributions.yml). Stdlib only.
Local run:  GH_TOKEN=$(gh auth token) GH_LOGIN=vyavahareyash python3 scripts/build_contributions.py out.svg
"""
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree

from build_assets import LIME, MONO, MUTED, SHAPE, TEXT, svg, text, tile

QUERY = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar {
  totalContributions weeks { contributionDays { date weekday contributionLevel } } } } } }"""

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 0.3, "SECOND_QUARTILE": 0.55, "THIRD_QUARTILE": 0.8, "FOURTH_QUARTILE": 1}
PITCH, CELL = 14, 11  # cell + 3px gap

CSS = ("<style>.now{animation:now 2s ease-in-out infinite}@keyframes now{50%{opacity:.25}}"
       "@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>")


def fetch_calendar(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-readme-builder"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit(f"GitHub API error: {payload['errors']}")  # fail the job; the previous tile stays published
    return payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def cell(x, y, level, extra=""):
    if level == 0:
        return f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{SHAPE}"{extra}/>'
    return f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{LIME}" fill-opacity="{level}"{extra}/>'


def render(calendar):
    weeks = calendar["weeks"]
    assert 1 <= len(weeks) <= 54, f"unexpected week count {len(weeks)}"
    grid_w = len(weeks) * PITCH - 3
    x0, top = 6 + (828 - grid_w) / 2, 86

    body = [CSS, tile(6, 6, 828, 224), text(30, 44, "contributions", 12, MUTED, MONO),
            text(810, 44, f"{calendar['totalContributions']:,} in the last year", 12, TEXT, MONO, anchor="end")]

    last_label_x = -99
    for i, week in enumerate(weeks):
        x = x0 + i * PITCH
        first = next((d for d in week["contributionDays"] if d["date"].endswith("-01")), None)
        if first and x - last_label_x >= 28:  # month label where a month starts, without crowding
            body.append(text(x, 76, date.fromisoformat(first["date"]).strftime("%b"), 10, MUTED, MONO))
            last_label_x = x
        for day in week["contributionDays"]:
            assert 0 <= day["weekday"] <= 6
            body.append(cell(x, top + day["weekday"] * PITCH, LEVELS[day["contributionLevel"]]))

    today = weeks[-1]["contributionDays"][-1]  # pulse a lime ring on the latest day
    body.append(f'<rect x="{x0 + (len(weeks) - 1) * PITCH - 1.5}" y="{top + today["weekday"] * PITCH - 1.5}" '
                f'width="{CELL + 3}" height="{CELL + 3}" rx="4" fill="none" stroke="{LIME}" stroke-width="1.5" class="now"/>')

    body.append(text(30, 210, "updated daily", 10, MUTED, MONO))
    lx = 810 - 5 * PITCH - 30
    body.append(text(lx - 8, 210, "less", 10, MUTED, MONO, anchor="end"))
    for j, level in enumerate([0, 0.3, 0.55, 0.8, 1]):
        body.append(cell(lx + j * PITCH, 200, level))
    body.append(text(lx + 5 * PITCH + 5, 210, "more", 10, MUTED, MONO))

    return svg(840, 236, "".join(body), f"{calendar['totalContributions']:,} GitHub contributions in the last year")


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "contributions.svg")
    token, login = os.environ.get("GH_TOKEN"), os.environ.get("GH_LOGIN", "vyavahareyash")
    if not token:
        sys.exit("GH_TOKEN is not set")
    content = render(fetch_calendar(login, token))
    ElementTree.fromstring(content)  # self-check: well-formed XML
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(f"wrote {out} ({len(content) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
