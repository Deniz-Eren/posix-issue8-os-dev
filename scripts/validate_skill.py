#!/usr/bin/env python3
# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# SPDX-License-Identifier: MIT
"""Run the skill-level validation gates of docs/validation-plan.md.

The four gates of Layer 1 (skill repository):

1. Master index diffing: the manifest must cover every identifier of the
   ``idx/`` index pages (full mode, live).
2. URL liveness and slug exceptions: every routed URL must answer HTTP 200,
   and the known slug edge cases must resolve to the manifest URLs (full
   mode, live and cached).
3. Conformance tag audit: the manifest tags must be valid Issue 8 margin
   codes, and the interfaces that Issue 8 promotes to the Base must carry
   the ``BASE`` class (offline).
4. Context budget and copyright lint: ``SKILL.md`` must stay under 400 lines
   and an estimated 4000 tokens, must use no em-dashes, and no repository
   file may carry specification HTML fragments (offline).

Modes:

- default: the offline gates (3 and 4) plus the manifest structure checks.
- ``--full``: adds gates 1 and 2 with live, rate-limited, cached fetches.

The exit code is 0 when all selected gates pass, 1 when a gate fails, and 2
on an environment error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import build_manifest as bm

REPO = bm.REPO
MANIFEST = bm.MANIFEST
SKILL = REPO / "SKILL.md"
README = REPO / "README.md"

# The margin codes of XBD chapter 1, section 1.8.1, plus BASE. CX, OB, OF,
# and OH are markings that carry no optionality: a CX or OB interface is
# mandatory Base. Every other code is an option group.
KNOWN_CODES = frozenset(
    """BASE ADV CD CPT CX DC FR FSC IP6 MC1 ML MLR MSG MX MXC MXX OB OF OH
    PIO PS RPI RPP RS SD SHM SIO SPN SS TCT TPI TPP TPS TSA TSH TSP TSS TYM
    UP UU XSI""".split()
)
MARKING_CODES = frozenset({"CX", "OB", "OF", "OH"})
VOLUMES = frozenset({"XBD", "XSH", "XCU", "XRAT"})
CATEGORIES = frozenset({"chapter", "header", "interface", "utility", "rationale"})

# Interfaces that Issue 8 promotes to the mandatory Base, plus Base interfaces
# that share a page with an XSI sibling (ADR-12, ADR-15). Their manifest tag
# must be BASE or a base marking, and the audit fails if a rebuild regresses
# their status.
MUST_BE_BASE = (
    "pthread_create",
    "pthread_mutex_lock",
    "pthread_cond_wait",
    "pthread_barrier_wait",
    "pthread_spin_lock",
    "pthread_rwlock_rdlock",
    "sem_open",
    "sem_init",
    "aio_read",
    "aio_write",
    "lio_listio",
    "mmap",
    "mprotect",
    "munmap",
    "clock_gettime",
    "clock_nanosleep",
    "timer_create",
    "timer_settime",
    "futimens",
    "utimensat",
    "lgamma",
    "lgammaf",
    "lgammal",
    "tzname",
    "tzset",
)

# Interfaces that stay optional in Issue 8, with their primary option codes
# (ADR-12, ADR-15). Includes all compound-tagged optional interfaces so the
# manifest builder can never silently drop compound tags back to BASE.
MUST_BE_OPTIONAL = {
    "shm_open": "SHM",
    "shm_unlink": "SHM",
    "posix_spawn": "SPN",
    "posix_spawnp": "SPN",
    "posix_spawnattr_getschedparam": "SPN",
    "posix_spawnattr_setschedparam": "SPN",
    "posix_spawnattr_getschedpolicy": "SPN",
    "posix_spawnattr_setschedpolicy": "SPN",
    "mq_open": "MSG",
    "mlock": "MLR",
    "mlockall": "ML",
    "sched_setscheduler": "PS",
    "sched_get_priority_max": "PS",
    "sched_get_priority_min": "PS",
    "sched_rr_get_interval": "PS",
    "encrypt": "XSI",
    "setkey": "XSI",
    "aio_fsync": "FSC",
    "msync": "XSI",
    "pthread_attr_getstack": "TSA",
    "pthread_attr_setstack": "TSA",
    "pthread_mutex_getprioceiling": "RPP",
    "pthread_mutex_setprioceiling": "RPP",
    "pthread_mutexattr_getprioceiling": "RPP",
    "pthread_mutexattr_setprioceiling": "RPP",
}

# Slug edge cases from docs/validation-plan.md section 2.2: identifier to the
# expected publication-root path.
SLUG_EXCEPTIONS = {
    "sys/mman.h": "basedefs/sys_mman.h.html",
    "netinet/in.h": "basedefs/netinet_in.h.html",
    "arpa/inet.h": "basedefs/arpa_inet.h.html",
    ":": "utilities/colon.html",
    ".": "utilities/dot.html",
    "V1_chap02": "basedefs/V1_chap02.html",
    "V2_chap02": "functions/V2_chap02.html",
    "V3_chap02": "utilities/V3_chap02.html",
    "V4_xbd_chap01": "xrat/V4_xbd_chap01.html",
}

# The utilities index omits exactly these two punctuation built-ins.
INDEX_EXTRA_ALLOWLIST = frozenset({":", "."})

MAX_SKILL_LINES = 400
MAX_SKILL_TOKENS = 4000

URL_RE = re.compile(r"^https://pubs\.opengroup\.org/onlinepubs/9799919799/\S+$")
HTML_TAG_RE = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*(\s[^<>]*)?/?>")
FENCE_RE = re.compile(r"^[ \t]*(```|~~~)")
EM_DASHES = ("\u2014", "\u2013")
POSIX_TRADEMARK = (
    "POSIX\u00ae is a registered trademark of the "
    "Institute of Electrical and Electronic Engineers, Inc."
)
COMPLIANCE_CLAIM_RE = re.compile(
    r"\b(?:POSIX[- ]+(?:certified|conformant|compliant)|implements\s+POSIX)\b",
    re.IGNORECASE,
)


class Report:
    """Collects gate results and prints them with a gate prefix."""

    def __init__(self) -> None:
        self.failures = 0

    def ok(self, gate: str, message: str) -> None:
        print(f"PASS [{gate}] {message}")

    def fail(self, gate: str, message: str) -> None:
        self.failures += 1
        print(f"FAIL [{gate}] {message}")

    def check(self, gate: str, condition: bool, ok_message: str, fail_message: str) -> bool:
        if condition:
            self.ok(gate, ok_message)
        else:
            self.fail(gate, fail_message)
        return condition


def load_manifest(path: Path) -> list[dict[str, str]]:
    rows = []
    for raw in path.read_text().splitlines():
        if not raw or raw.startswith("#"):
            continue
        columns = raw.split("\t")
        keys = ("volume", "identifier", "category", "conformance_group", "canonical_url")
        row = {key: (columns[i] if len(columns) > i else "") for i, key in enumerate(keys)}
        rows.append(row)
    return rows


def is_base_class(tag: str) -> bool:
    """A tag carries the Base class when it is BASE or a pure marking."""
    return tag == "BASE" or tag in MARKING_CODES


def gate_manifest_structure(rows: list[dict[str, str]], report: Report) -> None:
    """Structural lint of the manifest (part of gate 4)."""
    gate = "manifest"
    seen: set[tuple[str, str]] = set()
    problems = 0
    for row in rows:
        where = f"{row['volume']}:{row['identifier']}"
        if row["volume"] not in VOLUMES or row["category"] not in CATEGORIES:
            report.fail(gate, f"{where}: unknown volume or category")
            problems += 1
            continue
        key = (row["volume"], row["identifier"])
        if key in seen:
            report.fail(gate, f"{where}: duplicate row")
            problems += 1
        seen.add(key)
        if not row["identifier"] or not URL_RE.match(row["canonical_url"]):
            report.fail(gate, f"{where}: malformed identifier or URL")
            problems += 1
        if row["category"] == "header" and not row["identifier"].endswith(".h"):
            report.fail(gate, f"{where}: header identifier without .h")
            problems += 1
        mechanical = row["category"] in ("header", "interface") or (
            row["category"] == "utility" and row["identifier"] not in INDEX_EXTRA_ALLOWLIST
        )
        if mechanical:
            slug = row["identifier"].replace("/", "_") + ".html"
            if not row["canonical_url"].endswith("/" + slug):
                report.fail(gate, f"{where}: URL slug does not match the identifier")
                problems += 1
    if not problems:
        report.ok(gate, f"structure of {len(rows)} rows is well formed")


def gate_tags(rows: list[dict[str, str]], report: Report) -> None:
    """Gate 3: the conformance tag audit."""
    gate = "tags"
    by_id = {(r["volume"], r["identifier"]): r for r in rows}
    unknown = sorted({r["conformance_group"] for r in rows} - KNOWN_CODES)
    report.check(
        gate,
        not unknown,
        "every conformance tag is a known Issue 8 margin code or BASE",
        f"unknown conformance tags: {unknown}",
    )
    optionals = [r for r in rows if not is_base_class(r["conformance_group"])]
    bad_option = [
        r["conformance_group"] for r in optionals if r["conformance_group"] not in KNOWN_CODES
    ]
    report.check(
        gate,
        not bad_option,
        "optional tags use valid option codes",
        f"invalid option tags: {bad_option}",
    )

    missing_base = []
    for identifier in MUST_BE_BASE:
        row = by_id.get(("XSH", identifier))
        if row is None:
            missing_base.append(identifier)
        elif not is_base_class(row["conformance_group"]):
            missing_base.append(f"{identifier}={row['conformance_group']}")
    message = f"all {len(MUST_BE_BASE)} promoted interfaces carry the Base class"
    report.check(
        gate,
        not missing_base,
        message,
        f"promoted interfaces lost the Base class: {missing_base}",
    )

    wrong_optional = []
    for identifier, code in MUST_BE_OPTIONAL.items():
        row = by_id.get(("XSH", identifier))
        if row is None or row["conformance_group"] != code:
            wrong_optional.append(f"{identifier}!={code}")
    report.check(
        gate,
        not wrong_optional,
        "the still-optional interfaces keep their option tags",
        f"optional interfaces changed status: {wrong_optional}",
    )
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["conformance_group"]] = counts.get(row["conformance_group"], 0) + 1
    summary = ", ".join(f"{code}={n}" for code, n in sorted(counts.items()))
    report.ok(gate, f"tag distribution: {summary}")


def gate_skill_lint(report: Report) -> None:
    """Gate 4: context budget, frontmatter, trademark, and surface lint."""
    gate = "skill"
    if not SKILL.exists():
        report.fail(gate, "SKILL.md is missing at the repository root")
        return
    text = SKILL.read_text()
    lines = text.count("\n")
    report.check(
        gate,
        lines < MAX_SKILL_LINES,
        f"SKILL.md has {lines} lines (< {MAX_SKILL_LINES})",
        f"SKILL.md has {lines} lines",
    )
    tokens = len(text) // 4
    report.check(
        gate,
        tokens < MAX_SKILL_TOKENS,
        f"SKILL.md token estimate is {tokens} (< {MAX_SKILL_TOKENS})",
        f"SKILL.md token estimate is {tokens}",
    )
    frontmatter = text.split("---", 2)
    pattern = r"^name: posix-issue8-os-dev$"
    name_ok = len(frontmatter) >= 3 and re.search(pattern, frontmatter[1], re.M) is not None
    report.check(
        gate,
        name_ok,
        "frontmatter name is posix-issue8-os-dev",
        "frontmatter name is missing or wrong",
    )
    dashes = [ch for ch in EM_DASHES if ch in text]
    report.check(
        gate,
        not dashes,
        "SKILL.md uses no em-dashes or en-dashes",
        f"SKILL.md contains dashes: {dashes}",
    )
    trademark = POSIX_TRADEMARK in text and "UNIX\u00ae" in text and "registered trademark" in text
    report.check(
        gate,
        trademark,
        "SKILL.md carries the POSIX and UNIX trademark notice",
        "the trademark notice is missing",
    )
    links = re.findall(r"\]\((?!https?://)[^)]+\)", text)
    report.check(
        gate,
        not links,
        "SKILL.md links only to the skill surface",
        f"SKILL.md has relative links: {links}",
    )
    claims = COMPLIANCE_CLAIM_RE.findall(text)
    report.check(
        gate,
        not claims,
        "SKILL.md makes no POSIX compliance or certification claims",
        f"SKILL.md contains prohibited compliance claims: {claims}",
    )
    if README.exists():
        readme_text = README.read_text()
        readme_tm = POSIX_TRADEMARK in readme_text
        report.check(
            gate,
            readme_tm,
            "README.md carries the IEEE POSIX trademark attribution",
            "README.md is missing the IEEE POSIX trademark attribution",
        )
        readme_claims = COMPLIANCE_CLAIM_RE.findall(readme_text)
        report.check(
            gate,
            not readme_claims,
            "README.md makes no POSIX compliance or certification claims",
            f"README.md contains prohibited compliance claims: {readme_claims}",
        )


def gate_originality(report: Report) -> None:
    """Gate 4: the anti-scraping lint over the repository text files.

    The scan covers the documents and the data files. Python source is out of
    scope because its regular expressions legitimately contain HTML-like
    literals. The copied specification references under docs/skills/*/ are
    third-party artifacts, not scraped Open Group content.
    """
    gate = "prose"
    skip_dirs = {".git", ".venv", ".url-cache", "build", "__pycache__", "references"}
    offenders = []
    files = 0
    for path in sorted(REPO.rglob("*")):
        relative = path.relative_to(REPO)
        if not path.is_file() or skip_dirs & set(relative.parts):
            continue
        suffix = path.suffix.lower()
        if suffix not in (".md", ".mdx", ".tsv", ".txt") and path.name != "CMakeLists.txt":
            continue
        if len(relative.parts) >= 2 and relative.parts[:2] == ("docs", "skills"):
            continue
        files += 1
        text = path.read_text(errors="replace")
        if suffix in (".md", ".mdx"):
            fence = False
            clean = []
            for line in text.splitlines():
                if FENCE_RE.match(line):
                    fence = not fence
                    continue
                if not fence:
                    clean.append(line)
            text = "\n".join(clean)
            text = re.sub(r"`[^`]*`", " ", text)  # drop inline code spans
        if HTML_TAG_RE.search(text):
            offenders.append(str(relative))
    report.check(
        gate,
        not offenders,
        f"no specification HTML fragments in {files} repository files",
        f"HTML fragments found in: {offenders}",
    )


def gate_index_diff(fetcher: bm.Fetcher, rows: list[dict[str, str]], report: Report) -> None:
    """Gate 1: diff the manifest against the live idx identifier indexes."""
    gate = "idx"
    manifest_ids = {
        r["identifier"]: r for r in rows if r["category"] in ("header", "interface", "utility")
    }
    index_ids: dict[str, str] = {}
    for index_name in ("head", "functions", "utilities"):
        page = fetcher.get(f"{bm.BASE}/{bm.INDEX_PAGES[index_name]}")
        for path, _label in bm.extract_links(page):
            identifier = None
            if index_name == "head":
                identifier = bm.header_identifier(path)
            elif index_name == "functions" and re.fullmatch(r"functions/[A-Za-z0-9_]+\.html", path):
                identifier = Path(path).stem
            elif index_name == "utilities" and re.fullmatch(r"utilities/[A-Za-z0-9_]+\.html", path):
                identifier = Path(path).stem
            if identifier:
                index_ids[identifier] = path
    missing = sorted(set(index_ids) - set(manifest_ids))
    extra = sorted(set(manifest_ids) - set(index_ids) - INDEX_EXTRA_ALLOWLIST)
    report.check(
        gate,
        not missing,
        f"manifest covers all {len(index_ids)} index identifiers",
        f"missing from the manifest: {missing[:20]}",
    )
    report.check(
        gate,
        not extra,
        "no unexplained extra identifiers",
        f"extra identifiers: {extra[:20]}",
    )
    report.check(
        gate,
        INDEX_EXTRA_ALLOWLIST <= set(manifest_ids),
        "the punctuation built-ins ':' and '.' are in the manifest",
        "the punctuation built-ins are missing",
    )


def gate_url_liveness(fetcher: bm.Fetcher, rows: list[dict[str, str]], report: Report) -> None:
    """Gate 2: every routed URL answers HTTP 200; slug exceptions resolve."""
    gate = "urls"
    dead = []
    for row in rows:
        try:
            fetcher.get(row["canonical_url"])
        except RuntimeError:
            dead.append(row["identifier"])
    report.check(
        gate,
        not dead,
        f"all {len(rows)} routed URLs are live",
        f"dead URLs for: {dead[:20]}",
    )
    by_id = {r["identifier"]: r for r in rows}
    bad_slugs = []
    for identifier, expected in SLUG_EXCEPTIONS.items():
        row = by_id.get(identifier)
        if row is None or not row["canonical_url"].endswith("/" + expected):
            bad_slugs.append(f"{identifier} -> {expected}")
    report.check(
        gate,
        not bad_slugs,
        "all slug exceptions resolve to the manifest URLs",
        f"broken slugs: {bad_slugs}",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full",
        action="store_true",
        help="run the live gates (idx diff and URL liveness)",
    )
    parser.add_argument("--cache", type=Path, default=bm.DEFAULT_CACHE)
    parser.add_argument("--rate", type=float, default=0.1, help="seconds between live fetches")
    args = parser.parse_args()

    if not MANIFEST.exists():
        print(f"error: {MANIFEST} is missing; run scripts/build_manifest.py first", file=sys.stderr)
        return 2
    rows = load_manifest(MANIFEST)
    report = Report()

    gate_manifest_structure(rows, report)
    gate_tags(rows, report)
    gate_skill_lint(report)
    gate_originality(report)

    if args.full:
        fetcher = bm.Fetcher(args.cache, args.rate)
        gate_index_diff(fetcher, rows, report)
        gate_url_liveness(fetcher, rows, report)
    else:
        print("INFO [mode] live gates skipped (use --full for gates 1 and 2)")

    print()
    if report.failures:
        print(f"VALIDATION: FAILED with {report.failures} failing check(s)")
        return 1
    suffix = " (6 gates)" if args.full else " (offline gates)"
    print("VALIDATION: all gates passed" + suffix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
