# Operations

## Local workflow

```sh
quarto preview                      # live preview while editing
uv run scripts/validate.py          # metadata validation (also runs in CI)
quarto render                       # full build; commit _freeze/ changes if any
```

Work on a branch and open a PR; `main` is the deployment branch. CI must be green before merge.

## Content recipes

These are the manual procedures; they are the intended basis for future project skills (`add-publication`, `add-project`, `add-dataset`, `add-note`, `site-qa`).

**Add a publication**: look up the DOI (OpenAlex/Crossref) → create `publications/items/<year>-<slug>.qmd` with schema-conformant front matter (`docs/content-model.md`) → set `featured` deliberately (top page shows at most 4) → link it from the related research project page → validate + render.

**Add a research project**: create `research/<slug>/index.qmd` from the template structure → choose the slug as if permanent (it is) → assign `research-area` from the closed vocabulary → link related publications and datasets.

**Add a dataset / software**: create `data-software/items/<slug>.qmd` → include repository URL and a versioned archive DOI (Figshare/Zenodo) when one exists → cross-link from project pages (this section is the single source of truth; do not restate dataset details elsewhere).

**Add a research note**: create under `notes/` → if it executes R / Python, render locally and commit the `_freeze/` output together with the source.

## Quarto upgrade procedure

1. Upgrade locally; run `quarto render`; inspect the site visually (top page and one page per section).
2. Fix any SCSS/layout breakage.
3. Bump the pinned version in both workflow files in the same PR as the fixes.

## GitHub Pages settings (one-time)

Repository → Settings → Pages → Source: **GitHub Actions**.
