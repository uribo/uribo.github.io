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

**Bibliographic fields are machine-owned when the item has a `doi`.** `title`, `author`, `year`, `venue` and `locator` (e.g. `vol. 27, no. 3, pp. 789–795`) are written by `uv run scripts/sync_refs.py` from Crossref and must not be hand-edited; `scripts/validate.py` fails on any mismatch. The rest (`type`, `research-area`, `featured`, `image`, `image-alt`, the summary) is hand-owned.

- Source of truth: `publications/references.json`, the bibliographic fields of Crossref's CSL-JSON record for each DOI (citation key = DOI; usable directly as a Pandoc `bibliography`). `sync_refs.py` keeps only the fields listed in `CSL_KEYS` (dropping volatile ones such as citation counts, so diffs stay readable), decodes Crossref's HTML entities, and sets `id`/`DOI` to the item's bare DOI. Values are otherwise kept as Crossref returned them; content corrections never go here.
- Corrections: when Crossref itself is wrong (e.g. a footnote marker fused into a title), add an entry to `publications/overrides.yml` keyed by DOI with the corrected `title` / `venue` / `year` / `locator` or an `author-rename` mapping, plus a required `reason`. Otherwise Crossref wins, including its punctuation, capitalization and name forms.
- `year` is Crossref's `issued` year (the earliest publication date, usually online), not the print issue year.
- The body's first line is the generated `Published in *{{< meta venue >}}*, {{< meta locator >}}. [doi:…](…)` line; extra links (e.g. arXiv) may follow it on the same line.
- Items without a DOI (books, some preprints) keep hand-written fields and are exempt from the check.
- Link text elsewhere that restates a publication is checked against the item: `Title (YEAR, Venue)` (the title may be shortened but must be a prefix of the item title), `Surname et al. YEAR, Venue` (first author), and free-text links of three or more words that only differ from the title in capitalization.

Recommended for all listed content types: `image` (site-absolute path to an `assets/illustrations/*.svg` matching the item's primary research area; `neutral.svg` when none fits) and `image-alt`. Every item in a listing should carry one so no placeholder thumbnails appear.

## Research project (`research/<slug>/index.qmd`)

Required: `title`, `subtitle`, `research-area`, `status` (`active` | `paused` | `completed`). Body follows the section order of the template (`research/heat-mobility/index.qmd`): Research Question → Background → Approach → Representative Findings → Related Publications → Data & Code → Related Projects.

## Data & Software (`data-software/items/*.qmd`)

Required: `title`, `subtitle`, `type`. Recommended: `repository` (URL), `doi` (versioned archive DOI, e.g. Figshare/Zenodo), `research-area`, `related-publications` (list of DOIs).

`type` ∈ `dataset` | `software` | `visualization` | `documentation`.

R packages: `title` is the package name, `repository` the GitHub repository, and `cran` ∈ `available` | `archived` records the CRAN status. The body opens with the badge line that `rpkg_badges()` in `scripts/validate.py` generates from `title` and `cran` (Shields.io CRAN version badge, or a static "CRAN archived" badge because Shields.io keeps showing the last version after archival, plus the r-universe development version); validate fails if the line is missing or does not match. When a package is archived or returns to CRAN, change `cran` and `doi` and paste the new line from the validate error. A package on CRAN carries CRAN's package DOI (`10.32614/CRAN.package.<name>`, unversioned) and a CRAN link in the body. A package archived from CRAN carries no CRAN DOI (it would resolve to the archive notice), though a version-archive DOI such as Zenodo is allowed; the body states "Archived from CRAN in <year>" and links GitHub instead. Do not put version numbers in the body; they go stale.

This section is the single source of truth for datasets and software; research project pages link here rather than restating the details.

## About (`about/index.qmd`)

Hand-maintained prose page: portrait photo (`about/shinya-uryu.jpg`), short English bio, Positions / Education / Books / Talks & Outreach lists, and public profile links. No schema; keep facts consistent with researchmap.

Talks & Outreach lists invited talks, society seminars and tutorials, regional and industry talks, and public courses, newest first; conference presentations and internal university events are left to researchmap. Name the host only for publicly advertised events; for closed trainings and commissioned briefings describe the audience instead (e.g. "for court staff"). Recurring series take one line with a year range. The portrait is the owner's current profile photo — replace the file in place (same path) when updating it.

## Funding (prose section on `research/index.qmd`)

Grants are a curated prose section (`## Funding`) on the research index, not per-item pages. List **awarded and held grants only** — never pending applications, planned submissions, rejected proposals, or grants declined after award, and never internal detail (budgets beyond public records, effort shares, application strategy). Each entry: official English title, funder + scheme, grant number linked to its public record (e.g., KAKEN), period, role, one- or two-sentence public-abstract-level description, and a link to the related research project page.

## Research note (`notes/<slug>/index.qmd` or `notes/<slug>.qmd`)

Required: `title`, `date`, `description`. Recommended: `research-area`, `categories`. Notes may execute R / Python; they are rendered locally and frozen (see `docs/architecture.md`). Computational figures must carry `fig-alt`.
