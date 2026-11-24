#!/usr/bin/env python3
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# SPDX-License-Identifier: MIT
"""Build the Issue 8 factual manifest from the Open Group index pages.

The script fetches the ``idx/`` index pages of publication 9799919799 and each
identifier page that they reference. From the pages it extracts only
uncopyrightable fact data (ADR-8):

- identifier names and relative ``href`` paths from the index pages
- the leading option tag (for example ``[ XSI ]`` or the primary option code
  from compound tags such as ``[ OB XSI ]``, ``[ SPN PS ]``, or ``[ FSC|SIO ]``)
  from the synopsis box that declares each function, header, or utility

It writes ``references/issue8-manifest.tsv`` with the columns::

    volume  identifier  category  conformance_group  canonical_url

Usage::

    python3 scripts/build_manifest.py [--cache DIR] [--rate SECONDS]

The fetch cache is a plain directory of files named after the URL path. A
fresh full run fetches about 1500 pages and takes a few minutes.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = "https://pubs.opengroup.org/onlinepubs/9799919799"
REPO = Path(__file__).resolve().parent.parent
DEFAULT_CACHE = REPO / ".url-cache"
MANIFEST = REPO / "references" / "issue8-manifest.tsv"

# Header subdirectories in the basedefs tree. The slash in the header name
# becomes an underscore in the URL slug (sys/mman.h -> sys_mman.h.html).
HEADER_DIRS = ("arpa", "net", "netinet", "sys")

INDEX_PAGES = {
    "xbd": "idx/xbd.html",
    "head": "idx/head.html",
    "xsh": "idx/xsh.html",
    "functions": "idx/functions.html",
    "xcu": "idx/xcu.html",
    "utilities": "idx/utilities.html",
    "xrat": "idx/xrat.html",
    "xrat_xbd": "idx/xrat_xbd.html",
    "xrat_xsh": "idx/xrat_xsh.html",
    "xrat_xcu": "idx/xrat_xcu.html",
}

# Utilities that XBD Chapter 2 assigns to the XSI Development Utilities
# option and to the XSI-mandatory C development utility. Their pages carry no
# leading option tag, so the assignment comes from the chapter text (ADR-9).
XSI_UTILITIES = frozenset(
    "admin cflow ctags cxref delta get nm prs rmdel sact sccs unget val what c17".split()
)

# Chapter pages per volume. The idx/ navigation pages link most chapters
# directly; the ranges here complete the set (XSH ch2 General Information and
# the XCU ch2 and ch3 pages are only reachable through TOC links).
CHAPTER_PAGES = {
    "XBD": [f"basedefs/V1_chap{n:02d}.html" for n in range(1, 15)],
    "XSH": [f"functions/V2_chap{n:02d}.html" for n in range(1, 3)],
    "XCU": [f"utilities/V3_chap{n:02d}.html" for n in range(1, 4)],
}

# Punctuation utilities with word-slug pages. The alphabetical utilities
# index omits them, so the generator adds them from this map (ADR-9). The
# validator treats them as the only allowed extras over the index.
PUNCTUATION_UTILITIES = {
    ":": "utilities/colon.html",
    ".": "utilities/dot.html",
}

ANCHOR_RE = re.compile(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
BOX_RE = re.compile(r'<div\s+class="box"[^>]*>(.*?)</div>', re.S)
SYNOPSIS_RE = re.compile(r"SYNOPSIS(.*?)DESCRIPTION", re.S | re.I)
# Matches single ([ XSI ]) and compound ([ OB XSI ], [ SPN PS ], [ FSC|SIO ])
# margin codes. Lowercase text like [ Option Start ] does not match.
TAG_RE = re.compile(r"^\[\s*([A-Z][A-Z0-9]*(?:[\s|]+[A-Z][A-Z0-9]*)*)\s*\]")
# Pure markings that carry no optionality; skipped when a compound tag also
# names an option group (for example [ OB XSI ] -> XSI).
MARKING_CODES = frozenset({"CX", "OB", "OF", "OH"})


class Fetcher:
    """Fetch URLs with a file cache, retries, and a polite rate limit."""

    def __init__(self, cache: Path, rate: float) -> None:
        self.cache = cache
        self.rate = rate
        self.cache.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._last = 0.0
        self.hits = 0
        self.misses = 0

    def _path(self, url: str) -> Path:
        slug = re.sub(r"[^A-Za-z0-9._-]", "_", url.removeprefix(BASE + "/"))
        return self.cache / slug

    def get(self, url: str, attempts: int = 3) -> str:
        path = self._path(url)
        if path.exists():
            self.hits += 1
            return path.read_text(errors="replace")
        for attempt in range(1, attempts + 1):
            with self._lock:
                gap = self.rate - (time.monotonic() - self._last)
                if gap > 0:
                    time.sleep(gap)
                self._last = time.monotonic()
            try:
                request = urllib.request.Request(
                    url, headers={"User-Agent": "posix-issue8-os-dev-manifest/1.0"}
                )
                with urllib.request.urlopen(request, timeout=30) as response:
                    body = response.read().decode("utf-8", errors="replace")
                path.write_text(body)
                self.misses += 1
                return body
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                if attempt == attempts:
                    msg = f"fetch failed after {attempts} attempts: {url}: {exc}"
                    raise RuntimeError(msg) from exc
                time.sleep(2 * attempt)
        msg = f"unreachable: {url}"  # pragma: no cover - defensive
        raise RuntimeError(msg)


def strip_tags(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def normalize_href(href: str) -> str:
    """Normalize a relative href to a publication-root path."""
    href = html.unescape(href).split("#", 1)[0]
    parts: list[str] = []
    for part in href.split("/"):
        if part == "..":
            if parts:
                parts.pop()
        elif part not in ("", "."):
            parts.append(part)
    return "/".join(parts)


def extract_links(page: str) -> list[tuple[str, str]]:
    return [(normalize_href(h), strip_tags(label)) for h, label in ANCHOR_RE.findall(page)]


def parse_box_tag(text: str) -> str | None:
    """Extract the primary conformance code from a stripped box text, or None.

    Compound tags such as ``[ OB XSI ]``, ``[ SPN PS ]``, and ``[ FSC|SIO ]``
    yield their first non-marking option code so optionality is never lost to a
    pure marking (``OB``) and every manifest row carries a single margin code.
    """
    match = TAG_RE.match(text)
    if not match:
        return None
    codes = re.findall(r"[A-Z][A-Z0-9]*", match.group(1))
    for code in codes:
        if code not in MARKING_CODES:
            return code
    return codes[0]


def _scan_boxes(fragment: str) -> str:
    """Return the tag of the first leading box in an HTML fragment, or BASE."""
    for box in BOX_RE.findall(fragment):
        text = strip_tags(box)
        tag = parse_box_tag(text)
        if tag:
            return tag
        if text:
            break
    return "BASE"


def leading_tag(page: str, identifier: str | None = None) -> str:
    """Return the option tag for the page or for ``identifier`` on shared pages.

    When ``identifier`` is given and the page has a SYNOPSIS section, match the
    specific synopsis box that declares ``identifier``. If ``identifier`` is
    declared in SYNOPSIS outside any option box, keep only a page-level pure
    marking (such as ``CX``) from DESCRIPTION and otherwise return ``BASE``.
    """
    if identifier is not None:
        syn_match = SYNOPSIS_RE.search(page)
        if syn_match:
            syn = syn_match.group(1)
            id_re = re.compile(rf"\b{re.escape(identifier)}\b")
            for box in BOX_RE.findall(syn):
                text = strip_tags(box)
                if id_re.search(text):
                    return parse_box_tag(text) or "BASE"
            outside = strip_tags(BOX_RE.sub(" ", syn))
            if id_re.search(outside):
                after_tag = _scan_boxes(page[syn_match.end() :])
                return after_tag if after_tag in MARKING_CODES else "BASE"
    return _scan_boxes(page)


def header_identifier(path: str) -> str | None:
    """Map a basedefs slug to a header name, or None for non-headers."""
    match = re.fullmatch(r"basedefs/([A-Za-z0-9_]+\.h)\.html", path)
    if not match:
        return None
    slug = match.group(1)
    for directory in HEADER_DIRS:
        prefix = directory + "_"
        if slug.startswith(prefix):
            rest = slug[len(prefix) :]
            if rest in (f"{directory}.h",) or "." in rest:
                return f"{directory}/{rest}"
    return slug


def collect(fetcher: Fetcher) -> list[dict[str, str]]:
    pages = {name: fetcher.get(f"{BASE}/{path}") for name, path in INDEX_PAGES.items()}

    rows: dict[tuple[str, str], dict[str, str]] = {}

    def add(volume: str, identifier: str, category: str, path: str) -> None:
        url = f"{BASE}/{path}"
        key = (volume, identifier)
        if key in rows and rows[key]["canonical_url"] != url:
            msg = f"conflicting URLs for {volume}:{identifier}"
            raise RuntimeError(msg)
        rows[key] = {
            "volume": volume,
            "identifier": identifier,
            "category": category,
            "canonical_url": url,
        }

    # Chapters of XBD, XSH, and XCU: the canonical ranges. Gate 2 of the
    # validator checks the liveness of every chapter URL.
    for volume, paths in CHAPTER_PAGES.items():
        for path in paths:
            add(volume, Path(path).stem, "chapter", path)

    # XBD headers from the header index (it also repeats V1_chap14).
    for path, _label in extract_links(pages["head"]):
        if re.fullmatch(r"basedefs/V1_chap\d+\.html", path):
            add("XBD", Path(path).stem, "chapter", path)
            continue
        identifier = header_identifier(path)
        if identifier:
            add("XBD", identifier, "header", path)

    # XSH system interfaces.
    for path, _label in extract_links(pages["functions"]):
        if re.fullmatch(r"functions/[A-Za-z0-9_]+\.html", path):
            add("XSH", Path(path).stem, "interface", path)

    # XCU utilities.
    for path, _label in extract_links(pages["utilities"]):
        if re.fullmatch(r"utilities/[A-Za-z0-9_]+\.html", path):
            add("XCU", Path(path).stem, "utility", path)
    for identifier, path in PUNCTUATION_UTILITIES.items():
        add("XCU", identifier, "utility", path)

    # XRAT rationale pages from the four rationale index pages.
    for name in ("xrat", "xrat_xbd", "xrat_xsh", "xrat_xcu"):
        for path, _label in extract_links(pages[name]):
            if re.fullmatch(r"xrat/V4_[A-Za-z0-9_]+\.html", path):
                add("XRAT", Path(path).stem, "rationale", path)

    # Conformance groups from the leading option tag of each identifier page.
    # The pages are fetched with a small worker pool; the fetcher keeps the
    # rate limit so that the Open Group server sees a polite request rate.
    total = len(rows)

    def tag_row(row: dict[str, str]) -> None:
        page = fetcher.get(row["canonical_url"])
        identifier = row["identifier"] if row["category"] == "interface" else None
        row["conformance_group"] = leading_tag(page, identifier)
        if row["category"] == "utility" and row["identifier"] in XSI_UTILITIES:
            row["conformance_group"] = "XSI"

    ordered = sorted(rows.values(), key=lambda r: r["identifier"])
    with ThreadPoolExecutor(max_workers=8) as pool:
        for position, _ in enumerate(pool.map(tag_row, ordered), 1):
            if position % 100 == 0:
                print(f"  tagged {position}/{total}", file=sys.stderr)

    return sorted(rows.values(), key=lambda r: (r["volume"], r["category"], r["identifier"]))


def write_manifest(rows: list[dict[str, str]]) -> None:
    lines = [
        "# The Open Group Base Specifications Issue 8 (POSIX.1-2024 /",
        "# IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026).",
        "# POSIX® is a registered trademark of the Institute of Electrical and",
        "# Electronic Engineers, Inc.",
        "# Publication 9799919799. Factual index only (ADR-8): identifier names,",
        "# canonical URLs, and option tags. No specification prose.",
        "# Columns: volume <TAB> identifier <TAB> category <TAB> conformance_group",
        "#          <TAB> canonical_url",
        "# conformance_group BASE means no option marking on the declaration;",
        "# otherwise the value is the primary option code of the declaration's",
        "# synopsis box (skipping pure markings like OB in compound tags).",
    ]
    for row in rows:
        lines.append(
            "\t".join(
                (
                    row["volume"],
                    row["identifier"],
                    row["category"],
                    row["conformance_group"],
                    row["canonical_url"],
                )
            )
        )
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--rate", type=float, default=0.1, help="seconds between fetches")
    args = parser.parse_args()
    fetcher = Fetcher(args.cache, args.rate)
    print(f"collecting identifiers from {BASE}", file=sys.stderr)
    rows = collect(fetcher)
    write_manifest(rows)
    groups: dict[str, int] = {}
    categories: dict[str, int] = {}
    for row in rows:
        groups[row["conformance_group"]] = groups.get(row["conformance_group"], 0) + 1
        categories[row["category"]] = categories.get(row["category"], 0) + 1
    print(f"rows: {len(rows)}  fetches: {fetcher.misses}  cache hits: {fetcher.hits}")
    print(f"categories: {dict(sorted(categories.items()))}")
    print(f"conformance groups: {dict(sorted(groups.items()))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
