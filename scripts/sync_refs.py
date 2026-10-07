# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Sync publication metadata from Crossref (the only script here that uses the network).

For every `publications/items/*.qmd` with a `doi`, fetch Crossref CSL-JSON into
`publications/references.json`, then rewrite the item's machine-owned front matter
fields (bibref.GENERATED_FIELDS, with publications/overrides.yml applied) and its
"Published in ..." body line. Hand-owned fields and the summary are left untouched.

Run as:
  uv run scripts/sync_refs.py            # fetch DOIs not yet cached, rewrite items
  uv run scripts/sync_refs.py --refresh  # re-fetch every DOI from Crossref
  uv run scripts/sync_refs.py --check    # report what would change; exit 1 if anything would

Set CROSSREF_MAILTO to an e-mail address to use Crossref's polite pool (optional).
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

import yaml

from bibref import (
    CITATION_LINE,
    CITATION_LINE_RE,
    ITEMS_DIR,
    REFERENCES_PATH,
    ROOT,
    expected_fields,
    load_overrides,
    load_references,
    split_front_matter,
)

CSL_KEYS = ["id", "DOI", "type", "title", "container-title", "author", "issued",
            "volume", "issue", "page", "article-number", "publisher"]
NAME_KEYS = ["given", "family", "literal", "name", "suffix",
             "non-dropping-particle", "dropping-particle"]


def fetch_csl(doi: str) -> dict:
    url = ("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")
           + "/transform/application/vnd.citationstyles.csl+json")
    agent = "uribo.github.io-sync_refs (https://uribo.github.io)"
    if mailto := os.environ.get("CROSSREF_MAILTO"):
        agent += f" mailto:{mailto}"
    req = urllib.request.Request(url, headers={"User-Agent": agent})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = json.load(resp)
    return trim(raw, doi)


def trim(raw: dict, doi: str) -> dict:
    """Keep bibliographic fields only (volatile counts etc. would churn diffs) and
    undo Crossref's HTML entities once, here."""

    def clean(value):
        if isinstance(value, str):
            return html.unescape(value)
        if isinstance(value, list) and value and isinstance(value[0], str):
            return html.unescape(value[0])  # CSL scalar delivered as a 1-element list
        return value

    item = {k: clean(raw[k]) for k in CSL_KEYS if raw.get(k) not in (None, "", [])}
    item["id"] = doi
    item["DOI"] = doi
    item["issued"] = {"date-parts": raw["issued"]["date-parts"]}
    item["author"] = [
        {k: html.unescape(p[k]) for k in NAME_KEYS if p.get(k)} for p in raw.get("author", [])
    ]
    return item


def yaml_str(value: str, always_quote: bool) -> str:
    if not always_quote and value.strip() == value:
        try:
            if yaml.safe_load(value) == value:
                return value
        except yaml.YAMLError:
            pass
    return json.dumps(value, ensure_ascii=False)


def set_field(block: str, key: str, value) -> str:
    if key == "author":
        rendered = "author:\n" + "".join(f"  - {yaml_str(n, False)}\n" for n in value)
        pattern = re.compile(r"^author:\n(?:  - .*\n)+", re.MULTILINE)
    else:
        text = str(value) if isinstance(value, int) else yaml_str(value, True)
        rendered = f"{key}: {text}\n"
        pattern = re.compile(rf"^{re.escape(key)}:.*\n", re.MULTILINE)
    if pattern.search(block):
        return pattern.sub(lambda _: rendered, block, count=1)
    # Missing key: insert after `venue` (or `year`) to keep a stable order.
    anchor = re.search(r"^(venue|year):.*\n", block, re.MULTILINE)
    pos = anchor.end() if anchor else len(block)
    return block[:pos] + rendered + block[pos:]


def sync_item(text: str, fields: dict) -> str:
    block, body = split_front_matter(text)
    for key, value in fields.items():
        block = set_field(block, key, value)
    if CITATION_LINE_RE.search(body):
        body = CITATION_LINE_RE.sub(lambda _: CITATION_LINE, body, count=1)
    else:
        body = "\n" + CITATION_LINE + "\n" + body.lstrip("\n")
    return f"---\n{block}---\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="re-fetch every DOI")
    parser.add_argument("--check", action="store_true", help="report changes, write nothing")
    args = parser.parse_args()

    items = {}
    for path in sorted(ITEMS_DIR.glob("*.qmd")):
        block, _ = split_front_matter(path.read_text(encoding="utf-8"))
        doi = (yaml.safe_load(block) or {}).get("doi")
        if doi:
            items[path] = str(doi).lower()

    references = load_references()
    old_references = dict(references)
    for doi in sorted(set(items.values())):
        if args.refresh or doi not in references:
            print(f"fetch {doi}")
            references[doi] = fetch_csl(doi)
            time.sleep(0.2)
    references = {d: references[d] for d in sorted(set(items.values()))}  # prune unused

    overrides = {k.lower(): v for k, v in load_overrides().items()}
    changed = []
    if references != old_references:
        changed.append(REFERENCES_PATH)
        if not args.check:
            REFERENCES_PATH.write_text(
                json.dumps(list(references.values()), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    for path, doi in items.items():
        text = path.read_text(encoding="utf-8")
        new = sync_item(text, expected_fields(references[doi], overrides.get(doi)))
        if new != text:
            changed.append(path)
            if not args.check:
                path.write_text(new, encoding="utf-8")

    for path in changed:
        print(("would update " if args.check else "updated ") + str(path.relative_to(ROOT)))
    print(f"sync_refs: {len(items)} item(s), {len(changed)} file(s) changed")
    return 1 if (args.check and changed) else 0


if __name__ == "__main__":
    sys.exit(main())
