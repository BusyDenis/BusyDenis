#!/usr/bin/env python3
"""Render assets/claude.svg from data/usage.json.

Pure stdlib so it runs anywhere (local + GitHub Actions, no pip install).
Reads a small normalized usage file (see data/usage.json) and draws a
Grafana-style "AI co-pilot telemetry" panel matching the profile theme.

Usage:
    python3 scripts/render_metrics.py [usage.json] [out.svg]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "usage.json"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "assets" / "claude.svg"

# ---- theme ---------------------------------------------------------------
BG, PANEL, BORDER, GRID = "#0b0e14", "#11151f", "#1f2733", "#161c27"
TEXT, MUTED, IND, IND2, CYAN, GREEN = "#e6e9ef", "#8b94a7", "#6366f1", "#818cf8", "#22d3ee", "#34d399"
FONT = "ui-monospace, 'Cascadia Code', 'JetBrains Mono', 'Courier New', monospace"


def human(n: float) -> str:
    n = float(n)
    if n >= 1e9:
        return f"{n / 1e9:.2f}B"
    if n >= 1e6:
        return f"{n / 1e6:.1f}M"
    if n >= 1e3:
        return f"{n / 1e3:.1f}K"
    return f"{int(n)}"


def load() -> dict:
    try:
        return json.loads(SRC.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        # graceful fallback so the panel always renders
        return {"updated": "—", "window": "last 30 days", "total_tokens": 0,
                "total_cost_usd": 0, "sessions": 0, "primary_model": "claude",
                "daily": []}


def sparkline(daily, x0, y0, w, h):
    """Return (area_path, line_points, last_xy) scaled into the given box."""
    pts = [d.get("tokens", 0) for d in daily][-14:]
    if not pts:
        pts = [0, 0]
    lo, hi = min(pts), max(pts)
    span = (hi - lo) or 1
    n = len(pts)
    step = w / (n - 1) if n > 1 else 0
    coords = []
    for i, v in enumerate(pts):
        x = x0 + i * step
        y = y0 + h - ((v - lo) / span) * h
        coords.append((x, y))
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    area = f"M{x0:.1f},{y0 + h:.1f} L" + line.replace(" ", " L") + f" L{x0 + (n - 1) * step:.1f},{y0 + h:.1f} Z"
    return area, line, coords[-1]


def main():
    d = load()
    tokens = human(d.get("total_tokens", 0))
    cost = d.get("total_cost_usd", 0) or 0
    sessions = d.get("sessions", 0)
    daily = d.get("daily", [])
    avg = human((d.get("total_tokens", 0) / len(daily)) if daily else 0)
    model = (d.get("primary_model") or "claude").replace("claude-", "")
    updated = d.get("updated", "—")
    window = d.get("window", "last 30 days")

    area, line, (lx, ly) = sparkline(daily, 488, 86, 372, 96)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 230" width="900" height="230" font-family="{FONT}" role="img" aria-label="Claude co-pilot telemetry">
  <defs>
    <linearGradient id="cstroke" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{IND}"/><stop offset="1" stop-color="{CYAN}"/>
    </linearGradient>
    <linearGradient id="carea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{IND}" stop-opacity="0.35"/><stop offset="1" stop-color="{IND}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="cnum" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#a5b4fc"/><stop offset="1" stop-color="{IND}"/>
    </linearGradient>
    <clipPath id="pc"><rect x="2" y="2" width="896" height="226" rx="16"/></clipPath>
    <style>
      .draw {{ stroke-dasharray: 1400; stroke-dashoffset: 1400; animation: dr 1.8s 0.2s ease-out forwards; }}
      .blip {{ animation: bp 1.8s ease-in-out infinite; transform-origin: center; }}
      @keyframes dr {{ to {{ stroke-dashoffset: 0; }} }}
      @keyframes bp {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
    </style>
  </defs>

  <g clip-path="url(#pc)">
    <rect x="2" y="2" width="896" height="226" rx="16" fill="{BG}"/>

    <!-- header strip -->
    <text x="28" y="38" fill="{TEXT}" font-size="13" letter-spacing="2">🤖 AI CO-PILOT TELEMETRY</text>
    <text x="270" y="38" fill="{MUTED}" font-size="12" letter-spacing="1.5">/ claude-code · ccusage</text>
    <rect x="700" y="22" width="172" height="22" rx="11" fill="#11151f" stroke="{BORDER}"/>
    <circle cx="716" cy="33" r="4" fill="{GREEN}" class="blip"/>
    <text x="728" y="37" fill="{MUTED}" font-size="11">updated {updated}</text>
    <line x1="28" y1="50" x2="872" y2="50" stroke="{GRID}"/>

    <!-- hero metric -->
    <text x="28" y="78" fill="{MUTED}" font-size="12" letter-spacing="2">TOKENS · {window.upper()}</text>
    <text x="26" y="138" fill="url(#cnum)" font-size="62" font-weight="700">{tokens}</text>
    <rect x="28" y="156" width="210" height="24" rx="6" fill="#11151f" stroke="{BORDER}"/>
    <text x="40" y="172" fill="{IND2}" font-size="12">primary ▸ {model}</text>

    <!-- stat tiles -->
    <g font-size="12">
      <rect x="262" y="70" width="118" height="50" rx="8" fill="{PANEL}" stroke="{BORDER}"/>
      <text x="276" y="90" fill="{MUTED}">COST</text>
      <text x="276" y="111" fill="{TEXT}" font-size="18" font-weight="700">${cost:,.0f}</text>
      <rect x="262" y="128" width="118" height="50" rx="8" fill="{PANEL}" stroke="{BORDER}"/>
      <text x="276" y="148" fill="{MUTED}">SESSIONS</text>
      <text x="276" y="169" fill="{TEXT}" font-size="18" font-weight="700">{sessions}</text>
      <rect x="388" y="70" width="86" height="108" rx="8" fill="{PANEL}" stroke="{BORDER}"/>
      <text x="402" y="90" fill="{MUTED}">AVG/DAY</text>
      <text x="402" y="116" fill="{CYAN}" font-size="17" font-weight="700">{avg}</text>
      <text x="402" y="150" fill="{MUTED}" font-size="10">tokens</text>
      <text x="402" y="164" fill="{MUTED}" font-size="10">per active</text>
      <text x="402" y="176" fill="{MUTED}" font-size="10">day</text>
    </g>

    <!-- sparkline -->
    <text x="488" y="78" fill="{MUTED}" font-size="11" letter-spacing="1.5">DAILY BURN · last {len(daily) if daily else 0}d</text>
    <line x1="488" y1="182" x2="860" y2="182" stroke="{GRID}"/>
    <path d="{area}" fill="url(#carea)"/>
    <polyline class="draw" points="{line}" fill="none" stroke="url(#cstroke)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="{CYAN}"/>
    <circle cx="{lx:.1f}" cy="{ly:.1f}" r="8" fill="none" stroke="{CYAN}" stroke-opacity="0.4" class="blip"/>
  </g>
  <rect x="2" y="2" width="896" height="226" rx="16" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
</svg>
'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT}  ({tokens} tokens, {sessions} sessions, ${cost:,.0f})")


if __name__ == "__main__":
    main()
