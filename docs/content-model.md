# Content Model

Canonical metadata schemas for all content types. `scripts/validate.py` enforces this document; when the two disagree, fix the script to match this document in the same commit.

## Controlled vocabulary: `research-area`

The three research axes are the edges of the Human–Environment–Information triad. Every value used anywhere on the site must be one of:

| Slug | Axis | Accent |
|---|---|---|
| `human-environment` | Human × Environment (heat risk, mobility, spatial exposure) | `#D75B32` |
| `environment-information` | Environment × Information (conservation culturomics, biodiversity perception) | `#4F7651` |
| `human-information` | Human × Information (multilingual Wikipedia, NLP, knowledge graphs) | `#5367A5` |

`research-area` is always a YAML list, and one item may carry multiple areas.

## Publication (`publications/items/*.qmd`)

Required: `title`, `author` (list), `year` (int), `type`. Recommended: `venue` (journal / conference name; the key `journal` is reserved by Quarto's scholarly front-matter schema and must not be used), `doi` (bare DOI, no URL prefix), `research-area`, `featured` (bool; top page shows `featured: true`, max 4 by recency).

`type` ∈ `article` | `preprint` | `proceedings` | `chapter` | `other`.

Body: one short paragraph at most; the page exists to carry metadata and link out via DOI.

## Research project (`research/<slug>/index.qmd`)

Required: `title`, `subtitle`, `research-area`, `status` (`active` | `paused` | `completed`). Body follows the section order of the template (`research/heat-mobility/index.qmd`): Research Question → Background → Approach → Representative Findings → Related Publications → Data & Code → Related Projects.

## Data & Software (`data-software/items/*.qmd`)

Required: `title`, `subtitle`, `type`. Recommended: `repository` (URL), `doi` (versioned archive DOI, e.g. Figshare/Zenodo), `research-area`, `related-publications` (list of DOIs).

`type` ∈ `dataset` | `software` | `visualization` | `documentation`.

This section is the single source of truth for datasets and software; research project pages link here rather than restating the details.

## Funding (prose section on `research/index.qmd`)

Grants are a curated prose section (`## Funding`) on the research index, not per-item pages. List **awarded and held grants only** — never pending applications, planned submissions, rejected proposals, or grants declined after award, and never internal detail (budgets beyond public records, effort shares, application strategy). Each entry: official English title, funder + scheme, grant number linked to its public record (e.g., KAKEN), period, role, one- or two-sentence public-abstract-level description, and a link to the related research project page.

## Research note (`notes/<slug>/index.qmd` or `notes/<slug>.qmd`)

Required: `title`, `date`, `description`. Recommended: `research-area`, `categories`. Notes may execute R / Python; they are rendered locally and frozen (see `docs/architecture.md`). Computational figures must carry `fig-alt`.
