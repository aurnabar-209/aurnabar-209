# Setup — aurnabar-209 profile README

## 0. Create the magic repo (skip if it already exists)
```
gh repo create aurnabar-209 --public --clone
cd aurnabar-209
```
Copy everything from this bundle into that repo (scripts/, .github/, README.md).

## 1. Install dependencies (local machine only — the daily workflow only needs requests + beautifulsoup4)
```
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
```

## 2. Generate the ASCII portrait (one time, or whenever your photo changes)
```
python scripts/prep_photo.py your-photo.jpg
python scripts/make_ascii_svg.py        # -> avi-ascii.svg
```
Rename the output if you'd like, just keep the README's <img src> in sync.

## 3. Generate the info card
Open `scripts/make_info_card.py` and edit the `ROWS` list near the top —
that's your Now / Prev / Stack / Highlights content. Then:
```
python scripts/make_info_card.py        # -> info-card.svg
```

## 4. Generate the heatmap (this is the part the daily Action re-runs)
```
python scripts/fetch_contributions.py   # -> data/contributions.json
python scripts/render_heatmap_svg.py    # -> contrib-heatmap.svg
```

## 5. Commit and push
```
git add .
git commit -m "profile art: ascii portrait + info card + heatmap"
git push
```

## 6. Turn on the daily refresh
The workflow at `.github/workflows/update-profile-art.yml` is already wired
to your username. After pushing, go to the repo's **Actions** tab and run
"Update profile art" once manually (workflow_dispatch) to confirm it
commits a fresh `contrib-heatmap.svg`. After that it runs on its own
every day at ~06:17 UTC.

## Notes
- `USERNAME` is already set to `aurnabar-209` in `fetch_contributions.py`
  and `make_info_card.py` — change it there if you ever rename your account.
- GitHub strips `<script>` and most inline CSS from READMEs, but it does
  render SVG `<img>` and plays the SMIL/CSS-keyframe animations inside
  them — that's why all motion lives inside the SVG files, not the README.
- Inline `style="margin-top:..."` on README elements is stripped; use
  `<br>` for vertical spacing, and `<h3>` instead of `<h1>`/`<h2>` when
  you don't want the full-width underline rule.
