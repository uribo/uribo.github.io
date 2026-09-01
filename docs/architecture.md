# Architecture

## Stack

Quarto website → GitHub Actions → GitHub Pages (user site, root URL `https://uribo.github.io/`). No JS framework, no CMS, no database. Bootstrap 5 (Quarto built-in) + `styles/theme.scss`. Observable JS / D3 only where a specific page needs interactivity.

## Execution and freeze policy

The long-term rot vector for a computational site is executing R / Python in CI. Therefore:

- `execute: freeze: auto` is set project-wide. Computational documents are rendered **locally** by a human; the results in `_freeze/` are **committed**.
- CI installs Quarto only (version pinned, see below) and runs `quarto render`, which reuses frozen results. CI never installs R or Python toolchains.
- Consequence: a broken local environment can never change the published site, and the site builds identically years from now.

## Declarative vs computational content

- **Declarative** (agent-editable): publication / project / dataset metadata, non-executing QMD prose. Validated by `scripts/validate.py`.
- **Computational** (human-rendered): `notes/`, and any Findings section embedding R / Python figures. Agents never trigger execution.

## CI / CD

- `check.yml` (pull requests): metadata validation + `quarto render`.
- `publish.yml` (push to `main`): render + deploy via `actions/deploy-pages`. GitHub Pages source must be set to **GitHub Actions** in repo settings.
- Quarto version is pinned in both workflows (currently **1.10.18**, matching the local install). Upgrades are deliberate: bump locally first, re-render, inspect the site (custom SCSS can break on Quarto upgrades), then bump the workflows in the same PR.

## URL policy

Directory names are public URLs and never change after publication. The three-axis taxonomy lives only in metadata (`research-area`), never in paths — reclassifying a project is a metadata edit, not a move.
