#!/usr/bin/env bash
# Pull Claude Code usage with ccusage, normalize it into data/usage.json,
# and push. Run this from YOUR machine (the logs live locally, CI can't see
# them). Set it on a schedule — e.g. a cron entry or a systemd timer:
#
#   # crontab -e  (every 6h)
#   0 */6 * * * cd ~/BusyDenis && ./scripts/update-usage.sh >> ~/.cache/usage.log 2>&1
#
# Requires: ccusage (`npm i -g ccusage` or `bunx ccusage`), python3, git.
set -euo pipefail
cd "$(dirname "$0")/.."

WINDOW="last 30 days"
SINCE="$(date -d '30 days ago' +%Y%m%d 2>/dev/null || date -v-30d +%Y%m%d)"  # GNU or BSD date

# session count is a separate ccusage report; default to 0 if unavailable
SESSIONS="$(ccusage session --json 2>/dev/null \
  | python3 -c 'import sys,json; print(len(json.load(sys.stdin).get("sessions",[])))' 2>/dev/null || echo 0)"

ccusage daily --json --since "$SINCE" \
  | python3 scripts/from_ccusage.py --sessions "$SESSIONS" --window "$WINDOW"

python3 scripts/render_metrics.py  # render locally too, so it's instant

if ! git diff --quiet -- data/usage.json assets/claude.svg; then
  git add data/usage.json assets/claude.svg
  git commit -m "chore: refresh Claude usage telemetry"
  git push
  echo "pushed updated telemetry"
else
  echo "no change"
fi
