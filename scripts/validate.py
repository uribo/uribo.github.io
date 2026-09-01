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

import yaml

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


def main() -> int:
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
        check_todo(path, meta)

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
