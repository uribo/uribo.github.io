# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Validate content metadata against docs/content-model.md.

Fails (exit 1) on schema violations; prints non-fatal warnings for TODO markers.
Run as: uv run scripts/validate.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import re

import yaml

import bibref

ROOT = Path(__file__).resolve().parent.parent

RESEARCH_AREAS = {"human-environment", "environment-information", "human-information"}
PUBLICATION_TYPES = {"article", "preprint", "proceedings", "chapter", "other"}
DATA_SOFTWARE_TYPES = {"dataset", "software", "visualization", "documentation"}
PROJECT_STATUSES = {"active", "paused", "completed"}

errors: list[str] = []
warnings: list[str] = []


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append(f"{path.relative_to(ROOT)}: missing YAML front matter")
        return {}
    try:
        block = text.split("---", 2)[1]
        meta = yaml.safe_load(block)
    except (IndexError, yaml.YAMLError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: unparseable front matter ({exc})")
        return {}
    return meta if isinstance(meta, dict) else {}


def check_required(path: Path, meta: dict, fields: list[str]) -> None:
    for field in fields:
        if field not in meta or meta[field] in (None, "", []):
            errors.append(f"{path.relative_to(ROOT)}: missing required field '{field}'")


def check_enum(path: Path, meta: dict, field: str, allowed: set[str]) -> None:
    value = meta.get(field)
    if value is None:
        return
    values = value if isinstance(value, list) else [value]
    for v in values:
        if v not in allowed:
            errors.append(
                f"{path.relative_to(ROOT)}: '{field}: {v}' not in {sorted(allowed)}"
            )


def check_todo(path: Path, meta: dict) -> None:
    if "TODO" in str(meta.get("title", "")):
        warnings.append(f"{path.relative_to(ROOT)}: title still contains TODO")


def check_bibliography(path: Path, meta: dict, references: dict, overrides: dict) -> None:
    """Machine-owned fields must equal Crossref (+ overrides); see scripts/sync_refs.py."""
    rel = path.relative_to(ROOT)
    doi = str(meta["doi"]).lower()
    if doi not in references:
        errors.append(f"{rel}: DOI not in publications/references.json (run: uv run scripts/sync_refs.py)")
        return
    expected = bibref.expected_fields(references[doi], overrides.get(doi))
    for field in bibref.GENERATED_FIELDS:
        if meta.get(field) != expected[field]:
            errors.append(
                f"{rel}: '{field}' differs from Crossref/overrides "
                f"(have {meta.get(field)!r}, expected {expected[field]!r}; "
                "fix publications/overrides.yml or run sync_refs.py, do not hand-edit)"
            )
    _, body = bibref.split_front_matter(path.read_text(encoding="utf-8"))
    if bibref.CITATION_LINE not in body:
        errors.append(f"{rel}: body lacks the generated 'Published in ...' line (run sync_refs.py)")


def check_overrides(overrides: dict, used_dois: set[str]) -> None:
    for doi, entry in overrides.items():
        where = f"publications/overrides.yml: {doi}"
        if not isinstance(entry, dict) or not entry.get("reason"):
            errors.append(f"{where}: every override needs a 'reason'")
            continue
        unknown = set(entry) - bibref.OVERRIDE_KEYS
        if unknown:
            errors.append(f"{where}: unknown key(s) {sorted(unknown)}")
        if doi not in used_dois:
            warnings.append(f"{where}: no publication item uses this DOI")


PUB_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]*publications/items/[^)\s#]+\.qmd)[^)]*\)")
TITLED_LINK_RE = re.compile(r"(.+) \((\d{4}), (.+)\)")  # "Title (2025, Venue)"
AUTHOR_LINK_RE = re.compile(r"(\S+)(?: et al\.)? (\d{4}), (.+)")  # "Kubo et al. 2025, Venue"


def check_publication_links(pub_meta: dict[Path, dict]) -> None:
    """Titles, years and venues restated in link text must match the linked item."""
    for path in sorted(ROOT.rglob("*.qmd")):
        rel = path.relative_to(ROOT)
        if rel.parts[0].startswith(("_", ".")) or rel.parts[:2] == ("publications", "items"):
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for text, target in PUB_LINK_RE.findall(line):
                item = (ROOT / target.lstrip("/")) if target.startswith("/") else (path.parent / target)
                meta = pub_meta.get(item.resolve())
                where = f"{rel}:{lineno}: link '{text}'"
                if meta is None:
                    errors.append(f"{where}: target {target} does not exist")
                    continue
                title, year, venue = meta.get("title", ""), meta.get("year"), meta.get("venue")
                authors = meta.get("author") or [""]
                if m := TITLED_LINK_RE.fullmatch(text):
                    if not title.startswith(m[1]):
                        errors.append(f"{where}: title is not a prefix of {title!r}")
                    if (int(m[2]), m[3]) != (year, venue):
                        errors.append(f"{where}: expected ({year}, {venue})")
                elif m := AUTHOR_LINK_RE.fullmatch(text):
                    if (m[1], int(m[2]), m[3]) != (authors[0].split()[-1], year, venue):
                        errors.append(f"{where}: expected '{authors[0].split()[-1]} ... {year}, {venue}'")
                elif (
                    len(text.split()) >= 3
                    and title.lower().startswith(text.lower())
                    and not title.startswith(text)
                ):
                    errors.append(f"{where}: casing differs from title {title!r}")


def main() -> int:
    references = bibref.load_references()
    overrides = {str(k).lower(): v for k, v in bibref.load_overrides().items()}
    pub_meta: dict[Path, dict] = {}
    for path in sorted((ROOT / "publications" / "items").glob("*.qmd")):
        meta = frontmatter(path)
        check_required(path, meta, ["title", "author", "year", "type"])
        check_enum(path, meta, "type", PUBLICATION_TYPES)
        check_enum(path, meta, "research-area", RESEARCH_AREAS)
        if not isinstance(meta.get("year"), int):
            errors.append(f"{path.relative_to(ROOT)}: 'year' must be an integer")
        doi = meta.get("doi")
        if doi and str(doi).startswith("http"):
            errors.append(f"{path.relative_to(ROOT)}: 'doi' must be bare (no URL prefix)")
        elif doi:
            check_bibliography(path, meta, references, overrides)
        check_todo(path, meta)
        pub_meta[path.resolve()] = meta

    used_dois = {str(m["doi"]).lower() for m in pub_meta.values() if m.get("doi")}
    check_overrides(overrides, used_dois)
    for doi in sorted(set(references) - used_dois):
        warnings.append(f"publications/references.json: unused entry {doi} (run sync_refs.py to prune)")
    check_publication_links(pub_meta)

    for path in sorted((ROOT / "research").glob("*/index.qmd")):
        meta = frontmatter(path)
        check_required(path, meta, ["title", "subtitle", "research-area", "status"])
        check_enum(path, meta, "research-area", RESEARCH_AREAS)
        check_enum(path, meta, "status", PROJECT_STATUSES)
        check_todo(path, meta)

    for path in sorted((ROOT / "data-software" / "items").glob("*.qmd")):
        meta = frontmatter(path)
        check_required(path, meta, ["title", "subtitle", "type"])
        check_enum(path, meta, "type", DATA_SOFTWARE_TYPES)
        check_enum(path, meta, "research-area", RESEARCH_AREAS)
        check_todo(path, meta)

    notes_dir = ROOT / "notes"
    note_paths = [p for p in notes_dir.glob("*/index.qmd")] + [
        p for p in notes_dir.glob("*.qmd") if p.name != "index.qmd"
    ]
    for path in sorted(note_paths):
        meta = frontmatter(path)
        check_required(path, meta, ["title", "date", "description"])
        check_enum(path, meta, "research-area", RESEARCH_AREAS)

    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"ERROR {error}")
    print(f"validate: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
