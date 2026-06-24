#!/usr/bin/env python3
"""Transform `ccusage daily --json` (on stdin) into data/usage.json.

ccusage (https://github.com/ryoppippi/ccusage) reads Claude Code's local
logs and prints usage JSON. This normalizes it into the small, stable shape
that render_metrics.py expects, so the SVG renderer never has to track
ccusage's schema.

Usage:
    ccusage daily --json | python3 scripts/from_ccusage.py [--sessions N] [--window "last 30 days"]

Defensive by design: ccusage key names have shifted across versions, so every
read falls back gracefully. If a number looks wrong, inspect raw `ccusage`
output and adjust the .get() keys below.
"""
import argparse
import datetime
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "usage.json"


def day_tokens(day: dict) -> int:
    if isinstance(day.get("totalTokens"), (int, float)):
        return int(day["totalTokens"])
    return int(sum(day.get(k, 0) or 0 for k in
               ("inputTokens", "outputTokens", "cacheCreationTokens", "cacheReadTokens")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", type=int, default=0)
    ap.add_argument("--window", default="last 30 days")
    args = ap.parse_args()

    raw = json.load(sys.stdin)
    days = raw.get("daily") or raw.get("data") or []
    totals = raw.get("totals", {})

    daily = [{"date": d.get("date", "?"), "tokens": day_tokens(d)} for d in days][-30:]
    total = totals.get("totalTokens")
    if not isinstance(total, (int, float)):
        total = sum(d["tokens"] for d in daily)
    cost = totals.get("totalCost") or sum(d.get("totalCost", 0) or 0 for d in days)

    models = Counter()
    for d in days:
        for m in d.get("modelsUsed", []) or []:
            models[m] += 1
    primary = models.most_common(1)[0][0] if models else "claude"

    out = {
        "updated": datetime.date.today().isoformat(),
        "window": args.window,
        "total_tokens": int(total),
        "total_cost_usd": round(float(cost), 2),
        "sessions": args.sessions,
        "primary_model": primary,
        "models": [m for m, _ in models.most_common()],
        "daily": daily,
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {out['total_tokens']:,} tokens over {len(daily)} days, ${out['total_cost_usd']:,.2f}")


if __name__ == "__main__":
    main()
