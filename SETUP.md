# Setup — profile dashboard

Everything here goes into your **profile repo**: `github.com/BusyDenis/BusyDenis`
(the repo whose name == your username — its `README.md` shows on your profile).

```
README.md
SETUP.md
assets/header.svg   # hand-crafted hero (edit text/values directly)
assets/skills.svg   # hand-crafted gauges (edit %/labels directly)
```

The GitHub stat cards and the Claude token panel (tokscale) are **live external
embeds** — nothing to host or schedule. They update on their own.

## 1. Drop it in

```bash
cp -r README.md SETUP.md assets  /path/to/BusyDenis/BusyDenis/
cd /path/to/BusyDenis/BusyDenis
git add -A && git commit -m "feat: new dashboard README" && git push
```

Confirm it renders at `https://github.com/BusyDenis`.

## 2. Edit the static panels

- **header.svg** — name, role, region, age, the prompt line. Plain text in the SVG.
- **skills.svg** — each gauge is a `%` number + a label + an arc `d=""`. To change
  a value, edit the number text *and* regenerate the arc endpoint (the formula is
  `x = cx + 58·cos(θ)`, `y = 130 − 58·sin(θ)`, with `θ = 180 − 1.8·percent`). Easiest:
  ask Claude to "set the Go gauge to 90%" and it'll recompute the path.

## Notes / gotchas

- **Animations**: CSS `@keyframes`/SMIL inside the SVGs animate in Chrome & Firefox
  when GitHub serves them. If a viewer freezes them, the first frame still looks right.
- **Paths are relative** (`assets/header.svg`) — they only resolve once committed to
  the profile repo. Don't rename `assets/`.
- **Theme-proof**: panels carry their own dark background, so they look the same in
  GitHub light or dark mode.
- **tokscale**: the token panel reads from your tokscale.ai account. Tweak the embed
  query (`template`, `graph`, `tokens`, `cost`) in `README.md` to restyle it.
- **Swap the scrape-targets table** in `README.md` for whatever you want public.
