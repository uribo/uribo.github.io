# Design System

Concept: **Research Observatory / Scientific Data Story**. The UI stays neutral and editorial; color and visual interest belong to research figures. No card grids, no stock photography, no campus imagery.

## Palette

Neutral base: background `#F7F7F3`, text `#181818`, muted `#6B6B67`, border `rgba(24,24,24,0.16)`.

Research-area accents come in two tiers. **Graphic tier** (bands, marks, figure keys, large display text): `#D75B32` (human-environment), `#4F7651` (environment-information), `#5367A5` (human-information). **Text tier** (small text on the light background; darkened for WCAG AA): `#A8431F`, `#3D5C3F`, `#40518A`. The graphic-tier orange fails AA for body-size text on `#F7F7F3` — never use it below heading size. Verify any new color pair with a contrast checker before adding it.

Accents are used sparingly: as category markers and figure support, never as UI decoration. The site is light-mode only (deliberate; do not add a dark theme without a design pass).

## Typography and layout

Large display typography with `clamp()` sizing, hairline separators (`1px` borders) instead of boxes. Layout density is **dense editorial** (owner preference, 2026-09-01): the top page reads like a broadsheet front page — a stats strip under the hero, a dated News list, two-column publication listings, and a bottom grid for projects / funding / data — rather than a sparse landing page. Density comes from tighter spacing, multi-column grids, and more (real) content per viewport; never from decorative boxes, cards, or filler. The top page is the only custom layout (`page-layout: custom`); every other page uses Quarto's standard article layout for readability.

## Illustrations

Hand-crafted line-art SVGs in `assets/illustrations/`, one per research axis plus a neutral variant: `axis-he.svg` (heat contours × movement trajectory), `axis-ei.svg` (leaf dissolving into a network), `axis-hi.svg` (multilingual knowledge graph), `neutral.svg` (interrupted time series, for items outside the triad). Style contract: 1200×400 viewBox, transparent background, faint reference grid (`rgba(24,24,24,0.07)`), 1.5–2.5px strokes in the graphic-tier accents, no gradients, no fills except node/dot marks, `role="img"` + `aria-label` on the root element. They serve as listing thumbnails (`image` front matter) and project-page banners (`.project-banner`). Add new illustrations only in this style; item-specific artwork should still read as a member of the same family.

## Figures

Every figure carries `fig-alt` (enforced culturally, spot-checked in review). Figures reused from papers require a license check first (CC-BY is safe; publisher-owned figures are not). Top-page figures should be re-rendered with this palette for coherence rather than pasted from papers.
