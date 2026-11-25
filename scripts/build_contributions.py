#!/usr/bin/env python3
"""Render the GitHub contribution calendar as an animated satellite-pass tile matching the README theme.

A satellite crosses the year and images each week (pushbroom: top to bottom), a ring pings the peak
week, and the footer reads: scanning -> peak week -> downlink complete, each held >= 3s.

Runs daily in CI (.github/workflows/contributions.yml). Stdlib only.
Local run:  GH_TOKEN=$(gh auth token) python3 scripts/build_contributions.py out.svg
"""
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path
from xml.etree import ElementTree

from build_assets import EDGE, LIME, MONO, MUTED, SHAPE, TEXT, svg, text, tile

QUERY = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar {
  totalContributions weeks { contributionDays { date weekday contributionCount contributionLevel } } } } } }"""

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 0.3, "SECOND_QUARTILE": 0.55, "THIRD_QUARTILE": 0.8, "FOURTH_QUARTILE": 1}
PITCH, CELL, TOP = 14, 11, 86  # cell + 3px gap; grid top edge
GRID_H = 7 * PITCH - 3
SWEEP, HOLD = 9.0, 3.0  # satellite crossing time; minimum seconds each footer phase stays up
STARS = [(118, 58, 1.0, 0.0), (210, 24, 0.8, 1.3), (262, 64, 1.1, 2.1), (330, 30, 0.9, 0.6), (402, 56, 0.8, 2.7),
         (455, 22, 1.2, 1.7), (518, 62, 0.9, 0.4), (566, 34, 0.8, 3.1), (612, 54, 1.1, 1.1), (668, 66, 0.8, 2.4),
         (724, 58, 1.0, 0.9), (780, 64, 0.8, 1.9), (160, 66, 0.8, 3.4), (380, 18, 0.7, 2.9)]


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


def keyframes(name, stops):
    """stops: [(percent or tuple of percents, 'css')] -> @keyframes rule."""
    parts = []
    for pct, css in stops:
        pcts = pct if isinstance(pct, tuple) else (pct,)
        parts.append(",".join(f"{p:.2f}%" for p in pcts) + "{" + css + "}")
    return f"@keyframes {name}{{{''.join(parts)}}}"


def short(d):
    return date.fromisoformat(d).strftime("%b %-d")


def render(cal):
    weeks = cal["weeks"]
    n = len(weeks)
    assert 1 <= n <= 54, f"unexpected week count {n}"
    grid_w = n * PITCH - 3
    x0 = 6 + (828 - grid_w) / 2
    total = cal["totalContributions"]

    delay = [i / max(n - 1, 1) * SWEEP for i in range(n)]  # when the satellite is over week i
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
    peak = max(range(n), key=lambda i: weekly[i])
    peak_end = max(delay[peak] + HOLD, SWEEP)  # peak line holds >= 3s, and at least until the pass ends
    period = round(peak_end + HOLD, 2)  # then "downlink complete" holds >= 3s
    span = SWEEP / period

    body = [text(30, 44, "contributions", 12, MUTED, MONO),
            text(810, 44, f"{total:,} in the last year", 12, TEXT, MONO, anchor="end")]
    body += [f'<circle cx="{x}" cy="{y}" r="{r}" fill="{TEXT}" class="tw" style="animation-delay:{d}s"/>'
             for x, y, r, d in STARS]
    body.append(f'<line x1="30" y1="59.5" x2="810" y2="59.5" stroke="{EDGE}" stroke-dasharray="2 5"/>'
                f'<rect class="track" x="{x0}" y="59" width="{grid_w}" height="1" fill="{LIME}" fill-opacity=".6"/>')

    last_label_x = -99
    base, imaged = [], []
    for i, week in enumerate(weeks):
        x = x0 + i * PITCH
        first = next((d for d in week["contributionDays"] if d["date"].endswith("-01")), None)
        if first and x - last_label_x >= 28:  # month label where a month starts, without crowding
            body.append(text(x, 76, date.fromisoformat(first["date"]).strftime("%b"), 10, MUTED, MONO))
            last_label_x = x
        for d in week["contributionDays"]:
            assert 0 <= d["weekday"] <= 6
            y, level = TOP + d["weekday"] * PITCH, LEVELS[d["contributionLevel"]]
            base.append(cell(x, y, level * 0.3))
            if level:  # pushbroom: each cell develops a beat after the one above it
                imaged.append(cell(x, y, level, f' class="img" style="animation-delay:{delay[i] + d["weekday"] * 0.05:.2f}s"'))
    body += base + imaged

    body.append(f'<circle cx="{x0 + peak * PITCH + CELL / 2}" cy="{TOP + GRID_H / 2}" r="10" fill="none" stroke="{LIME}" '
                f'stroke-width="2" class="ping" style="animation-delay:{delay[peak]:.2f}s"/>')
    sx = x0 + 5  # satellite starts over the first column
    body.append(f'<g class="sat">'
                f'<polygon points="{sx},66 {sx - 9},{TOP + GRID_H + 2} {sx + 9},{TOP + GRID_H + 2}" fill="{LIME}" fill-opacity=".09"/>'
                f'<rect x="{sx - 15}" y="57" width="10" height="5" fill="{LIME}" class="glint"/>'
                f'<rect x="{sx + 5}" y="57" width="10" height="5" fill="{LIME}" class="glint"/>'
                f'<rect x="{sx - 4}" y="55" width="8" height="9" rx="1.5" fill="{TEXT}"/>'
                f'<line x1="{sx}" y1="55" x2="{sx}" y2="50" stroke="{TEXT}" stroke-width="1.2"/>'
                f'<circle cx="{sx}" cy="49.5" r="1.6" fill="{LIME}" class="nav"/></g>')

    days = weeks[peak]["contributionDays"]
    # GitHub weeks start on Sunday; ISO weeks on Monday, so number the week by its Monday
    iso_week = date.fromisoformat(days[min(1, len(days) - 1)]["date"]).isocalendar()[1]
    peak_line = f"peak · wk {iso_week:02d} · {short(days[0]['date'])}–{short(days[-1]['date'])} · {weekly[peak]} contributions"
    body.append(f'<g class="pa">{text(30, 210, "scanning the last 12 months", 10, MUTED, MONO)}</g>'
                f'<g class="pb">{text(30, 210, peak_line, 10, LIME, MONO)}</g>'
                f'<g class="pc">{text(30, 210, f"downlink complete · {total:,} contributions", 10, TEXT, MONO)}</g>'
                f'<g class="static">{text(30, 210, f"{total:,} contributions imaged", 10, MUTED, MONO)}</g>')

    lx = 810 - 5 * PITCH - 30
    body.append(text(lx - 8, 210, "less", 10, MUTED, MONO, anchor="end"))
    body += [cell(lx + j * PITCH, 200, level) for j, level in enumerate([0, 0.3, 0.55, 0.8, 1])]
    body.append(text(lx + 5 * PITCH + 5, 210, "more", 10, MUTED, MONO))

    a, b = delay[peak] / period * 100, peak_end / period * 100
    css = "".join(  # footer phases: scanning -> peak -> downlink complete
        f".{name}{{opacity:0;animation:{name} {period}s linear infinite}}"
        + keyframes(name, [((0, start), "opacity:0")] * (start > 0)
                    + [((start + 0.01 * (start > 0), end), "opacity:1"), ((end + 0.01, 100), "opacity:0")])
        for name, start, end in (("pa", 0, a), ("pb", a, b), ("pc", b, 99.5)))
    css += (f".img{{opacity:0;animation:img {period}s linear infinite}}"
            + keyframes("img", [(0, "opacity:0"), (0.6, f"opacity:1;fill:{TEXT}"), (3, f"fill:{LIME}"),
                                (92, "opacity:1"), ((97, 100), "opacity:0")])
            + f".sat{{animation:sat {period}s linear infinite}}"
            + keyframes("sat", [(0, "transform:translateX(0)"), (span * 100, f"transform:translateX({grid_w - 11}px)"),
                                ((span * 100 + 0.5, 100), f"transform:translateX({grid_w - 11}px);opacity:0")])
            + f".track{{transform-box:fill-box;transform-origin:left;animation:track {period}s linear infinite}}"
            + keyframes("track", [(0, "transform:scaleX(0)"), (span * 100, "transform:scaleX(1);opacity:1"),
                                  (100, "transform:scaleX(1);opacity:0")])
            + f".ping{{opacity:0;transform-box:fill-box;transform-origin:center;animation:ping {period}s ease-out infinite}}"
            + keyframes("ping", [(0, "opacity:1;transform:scale(.3)"), (14, "opacity:0;transform:scale(4)"), (100, "opacity:0")])
            + ".tw{animation:tw 3.6s ease-in-out infinite}" + keyframes("tw", [((0, 100), "opacity:.25"), (50, "opacity:.9")])
            + ".nav{animation:nav 1.2s steps(1) infinite}" + keyframes("nav", [(0, "opacity:1"), (50, "opacity:.15")])
            + ".glint{animation:glint 2.5s ease-in-out infinite}"
            + keyframes("glint", [((0, 80, 100), f"fill:{LIME}"), (88, f"fill:{TEXT}")])
            + ".static{display:none}"
            # reduced motion: no animation, full grid shown, a static footer line
            + "@media (prefers-reduced-motion:reduce){*{animation:none!important}.img{opacity:1}"
              ".sat,.track,.ping,.pa,.pb,.pc{display:none}.static{display:inline}}")

    return svg(840, 236, f"<style>{css}</style>" + tile(6, 6, 828, 224) + "".join(body),
               f"{total:,} GitHub contributions in the last year; peak week {short(days[0]['date'])} with {weekly[peak]}")


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
