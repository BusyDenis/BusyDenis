# Setup — profile dashboard

Everything here goes into your **profile repo**: `github.com/BusyDenis/BusyDenis`
(the repo whose name == your username — its `README.md` shows on your profile).

```
README.md
SETUP.md
assets/header.svg        # hand-crafted hero (edit text/values directly)
assets/skills.svg        # hand-crafted gauges (edit %/labels directly)
assets/claude.svg        # GENERATED — don't hand-edit, it gets overwritten
data/usage.json          # Claude usage data (your laptop writes this)
scripts/render_metrics.py # usage.json -> claude.svg
scripts/from_ccusage.py   # ccusage output -> usage.json
scripts/update-usage.sh   # run on your machine to refresh + push
.github/workflows/update-metrics.yml  # re-renders claude.svg in CI
```

## 1. Drop it in

```bash
# from this folder:
cp -r README.md SETUP.md assets data scripts .github  /path/to/BusyDenis/BusyDenis/
cd /path/to/BusyDenis/BusyDenis
chmod +x scripts/*.sh scripts/*.py
git add -A && git commit -m "feat: new dashboard README" && git push
```

Confirm the README renders at `https://github.com/BusyDenis`. The hero, gauges,
and Claude panel are local SVGs; the GitHub stat cards are live third-party
widgets reskinned to the palette.

## 2. Wire up the Claude token panel

The number can't be pulled in CI — your Claude Code logs live on your laptop.
So your laptop pushes the data, and a GitHub Action turns it into the SVG.

**On your machine:**

```bash
npm i -g ccusage          # or use `bunx ccusage` in the script
./scripts/update-usage.sh # pulls ccusage -> usage.json -> renders -> commits -> pushes
```

Then schedule it (every 6h):

```bash
crontab -e
0 */6 * * * cd ~/path/to/BusyDenis && ./scripts/update-usage.sh >> ~/.cache/usage.log 2>&1
```

**Enable the Action to push back:** repo → Settings → Actions → General →
*Workflow permissions* → **Read and write**. (Needed so `update-metrics.yml`
can commit the re-rendered SVG.)

> If `ccusage`'s JSON keys differ in your version, run `ccusage daily --json`
> and tweak the `.get()` keys in `scripts/from_ccusage.py`. Defaults are defensive.

## 3. Edit the static panels

- **header.svg** — name, role, region, age, the prompt line. Plain text in the SVG.
- **skills.svg** — each gauge is a `%` number + a label + an arc `d=""`. To change
  a value, edit the number text *and* regenerate the arc endpoint (the formula is
  `x = cx + 58·cos(θ)`, `y = 130 − 58·sin(θ)`, with `θ = 180 − 1.8·percent`). Easiest:
  ask Claude to "set the Go gauge to 90%" and it'll recompute the path.

## Notes / gotchas

- **Animations**: CSS `@keyframes`/SMIL inside the SVGs animate in Chrome & Firefox
  when GitHub serves them. If a viewer freezes them, the first frame still looks right.
- **Paths are relative** (`assets/header.svg`) — they only resolve once the files are
  committed to the profile repo. Don't rename `assets/`.
- **Theme-proof**: panels carry their own dark background, so they look the same in
  GitHub light or dark mode.
- **Swap the scrape-targets table** in `README.md` for whatever you want public.
