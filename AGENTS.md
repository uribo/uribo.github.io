# AGENTS.md — uribo.github.io

Personal research website of Shinya Uryu (Tokushima University). Built with Quarto, published to GitHub Pages at <https://uribo.github.io/>. This file is the canonical instruction set for all coding agents (Codex, Claude Code); `CLAUDE.md` imports it — edit here, never in both.

## Golden rules

1. **Edit metadata, not machinery.** Routine content work (publications, projects, datasets, notes metadata) means editing QMD front matter / YAML that conforms to `docs/content-model.md`. Do not restructure layouts, SCSS, or the top page to accomplish a content task.
2. **Never execute R / Python.** Computational documents are rendered locally by a human and frozen (`execute: freeze: auto`; `_freeze/` is committed). Agents run `quarto render` to verify the site builds, but must not add `execute` options that force re-execution, delete `_freeze/`, or "fix" a stale figure by re-running analysis.
3. **Protected files** — change only when the change itself is explicitly requested: `includes/_hero.qmd`, `styles/theme.scss`, `index.qmd`, `_quarto.yml`, `.github/workflows/*`.
4. **Slugs are permanent.** Directory and file names under `research/`, `publications/items/`, `data-software/items/`, `notes/` become public URLs. Choose carefully once; never rename after publication.
5. **`research-area` is a closed vocabulary**: `human-environment`, `environment-information`, `human-information`. Defined in `docs/content-model.md`; validated by `scripts/validate.py`. Do not invent new values.
6. **Validate before committing**: `uv run scripts/validate.py && quarto render`.
7. **Branch + PR, never push `main` directly.** `main` deploys to the public site via GitHub Actions.
8. Site content is US English (Japanese appears only in the hero tagline and on `join/`). Do not hard-wrap prose in Markdown/QMD.

## Documentation map

- `docs/architecture.md` — build/deploy pipeline, freeze policy, URL policy, Quarto version pinning
- `docs/content-model.md` — metadata schemas and controlled vocabularies (canonical)
- `docs/design-system.md` — palette (incl. text-safe accent variants), typography, editorial rules
- `docs/operations.md` — local workflow, content-addition recipes, Quarto upgrade procedure

## Commands

```sh
uv run scripts/validate.py   # metadata schema validation
quarto preview               # local preview
quarto render                # full build (uses frozen results)
```
