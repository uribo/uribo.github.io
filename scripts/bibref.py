"""Shared bibliographic logic for publications (imported by sync_refs.py and validate.py).

`publications/references.json` caches Crossref CSL-JSON keyed by bare DOI, exactly as
Crossref returned it (trimmed to bibliographic fields). `publications/overrides.yml`
records deliberate corrections of publisher errors. The machine-owned front matter
fields of an item are derived from both by `expected_fields()`; nothing here touches
the network, so validate.py stays offline.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REFERENCES_PATH = ROOT / "publications" / "references.json"
OVERRIDES_PATH = ROOT / "publications" / "overrides.yml"
ITEMS_DIR = ROOT / "publications" / "items"

# Front matter fields owned by the sync script; everything else is hand-maintained.
GENERATED_FIELDS = ["title", "author", "year", "venue", "locator"]
OVERRIDE_KEYS = {"title", "venue", "year", "locator", "author-rename", "reason"}

# Body line every DOI-bearing item must carry; Quarto fills it from front matter.
CITATION_LINE = (
    "Published in *{{< meta venue >}}*, {{< meta locator >}}. "
    "[doi:{{< meta doi >}}](https://doi.org/{{< meta doi >}})"
)
# Any earlier hand-written form of the line, up to and including the DOI link.
CITATION_LINE_RE = re.compile(r"^Published in .*?\[doi:[^\]]*\]\([^)]*\)", re.MULTILINE)


def load_references() -> dict[str, dict]:
    """Map lower-cased DOI -> CSL item. The file itself is a CSL-JSON array, so it
    also works as a Pandoc `bibliography:` (citation key = DOI)."""
    if not REFERENCES_PATH.exists():
        return {}
    items = json.loads(REFERENCES_PATH.read_text(encoding="utf-8"))
    return {item["DOI"].lower(): item for item in items}


def load_overrides() -> dict[str, dict]:
    if not OVERRIDES_PATH.exists():
        return {}
    return yaml.safe_load(OVERRIDES_PATH.read_text(encoding="utf-8")) or {}


def author_name(person: dict) -> str:
    if "family" in person:
        return " ".join(p for p in (person.get("given"), person["family"]) if p)
    return person.get("literal") or person.get("name", "")


def locator(csl: dict) -> str:
    """'vol. 27, no. 3, pp. 789–795' or 'vol. 96, article 103839'."""
    parts = []
    if csl.get("volume"):
        parts.append(f"vol. {csl['volume']}")
    if csl.get("issue"):
        parts.append(f"no. {csl['issue']}")
    page = csl.get("page") or ""
    if "-" in page:
        parts.append("pp. " + page.replace("-", "–"))
    elif csl.get("article-number") or page:
        parts.append(f"article {csl.get('article-number') or page}")
    return ", ".join(parts) or "advance online publication"


def expected_fields(csl: dict, override: dict | None = None) -> dict:
    override = override or {}
    rename = override.get("author-rename", {})
    fields = {
        "title": csl["title"],
        "author": [rename.get(n, n) for n in map(author_name, csl.get("author", []))],
        "year": csl["issued"]["date-parts"][0][0],
        "venue": csl["container-title"],
        "locator": locator(csl),
    }
    for key in ("title", "venue", "year", "locator"):
        if key in override:
            fields[key] = override[key]
    return fields


def split_front_matter(text: str) -> tuple[str, str]:
    """Return (front matter block without fences, body)."""
    _, block, body = text.split("---\n", 2)
    return block, body
