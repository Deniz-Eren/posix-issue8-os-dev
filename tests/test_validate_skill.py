# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# SPDX-License-Identifier: MIT
"""Unit tests for the validation tooling with local fixtures only.

No test in this suite fetches from the network (see the pytest skill).
"""

from __future__ import annotations

import build_manifest as bm
import validate_skill as vs

# A page whose synopsis box carries an option tag, with informative sections.
PAGE_XSI = """
<html><body>
<div class="box">[ XSI ] #include &lt;unistd.h&gt;<br>char *crypt(const char *key);</div>
<div class="box">The following sections are informative.</div>
<div class="box">End of informative text.</div>
</body></html>
"""

# A Base page: the first box has no leading option tag.
PAGE_BASE = """
<html><body>
<div class="box">The following sections are informative.</div>
<div class="box">End of informative text.</div>
</body></html>
"""

# A page with an option block marker that is not a page-level tag.
PAGE_BLOCK = """
<html><body>
<div class="box">[ Option Start ] If prioritized I/O is supported.</div>
<div class="box">[ Option End ]</div>
</body></html>
"""


class CapturingReport(vs.Report):
    """A report that records failures instead of only counting them."""

    def __init__(self) -> None:
        super().__init__()
        self.fails: list[str] = []

    def fail(self, gate: str, message: str) -> None:
        super().fail(gate, message)
        self.fails.append(f"{gate}: {message}")


def test_load_manifest_skips_comments_and_reads_columns(tmp_path) -> None:
    manifest = tmp_path / "m.tsv"
    manifest.write_text(
        "# a comment\n"
        "XSH\ta64l\tinterface\tXSI\thttps://pubs.opengroup.org/onlinepubs/9799919799/functions/a64l.html\n"
        "XCU\t.\tutility\tBASE\thttps://pubs.opengroup.org/onlinepubs/9799919799/utilities/dot.html\n"
    )
    rows = vs.load_manifest(manifest)
    assert len(rows) == 2
    assert rows[0]["identifier"] == "a64l"
    assert rows[0]["conformance_group"] == "XSI"
    assert rows[1]["identifier"] == "."


def test_header_identifier_maps_slugs_and_rejects_chapters() -> None:
    assert bm.header_identifier("basedefs/aio.h.html") == "aio.h"
    assert bm.header_identifier("basedefs/arpa_inet.h.html") == "arpa/inet.h"
    assert bm.header_identifier("basedefs/sys_mman.h.html") == "sys/mman.h"
    assert bm.header_identifier("basedefs/netinet_in.h.html") == "netinet/in.h"
    assert bm.header_identifier("basedefs/V1_chap02.html") is None
    assert bm.header_identifier("functions/read.html") is None


def test_leading_tag_reads_the_synopsis_box() -> None:
    assert bm.leading_tag(PAGE_XSI) == "XSI"
    assert bm.leading_tag(PAGE_BASE) == "BASE"
    assert bm.leading_tag(PAGE_BLOCK) == "BASE"


def test_leading_tag_parses_compound_option_tags() -> None:
    cases = [
        ("[ OB XSI ] void encrypt(char block[64], int edflag);", "XSI"),
        ("[ SPN PS ] int posix_spawnattr_getschedparam(void);", "SPN"),
        ("[ FSC|SIO ] int aio_fsync(int op, struct aiocb *aiocbp);", "FSC"),
        ("[ XSI|SIO ] int msync(void *addr, size_t len, int flags);", "XSI"),
        ("[ TSA TSS ] int pthread_attr_getstack(void);", "TSA"),
        ("[ RPP|TPP ] int pthread_mutex_getprioceiling(void);", "RPP"),
        ("[ PS|TPS ] int sched_get_priority_max(int policy);", "PS"),
        ("[ OB ] int ob_only(void);", "OB"),
    ]
    for box_body, expected in cases:
        page = f'<html><body><div class="box">{box_body}</div></body></html>'
        assert bm.leading_tag(page) == expected, box_body


def test_leading_tag_matches_per_identifier_on_shared_pages() -> None:
    shared_tz = """
    <html><body>
    <h4>SYNOPSIS</h4>
    #include &lt;time.h&gt;
    <div class="box">[ XSI ] extern int daylight; extern long timezone;</div>
    <div class="box">[ CX ] extern char *tzname[2]; void tzset(void);</div>
    <h4>DESCRIPTION</h4>
    <div class="box">The following sections are informative.</div>
    </body></html>
    """
    assert bm.leading_tag(shared_tz, "daylight") == "XSI"
    assert bm.leading_tag(shared_tz, "timezone") == "XSI"
    assert bm.leading_tag(shared_tz, "tzname") == "CX"
    assert bm.leading_tag(shared_tz, "tzset") == "CX"

    shared_utimens = """
    <html><body>
    <h4>SYNOPSIS</h4>
    int futimens(int fd);
    int utimensat(int fd);
    <div class="box">[ XSI ] int utimes(const char *path);</div>
    <h4>DESCRIPTION</h4>
    <div class="box">[ XSI ] Optional note for utimes.</div>
    </body></html>
    """
    assert bm.leading_tag(shared_utimens, "futimens") == "BASE"
    assert bm.leading_tag(shared_utimens, "utimensat") == "BASE"
    assert bm.leading_tag(shared_utimens, "utimes") == "XSI"

    shared_lgamma = """
    <html><body>
    <h4>SYNOPSIS</h4>
    double lgamma(double x);
    <div class="box">[ XSI ] extern int signgam;</div>
    <h4>DESCRIPTION</h4>
    <div class="box">[ CX ] ISO C alignment note.</div>
    </body></html>
    """
    assert bm.leading_tag(shared_lgamma, "lgamma") == "CX"
    assert bm.leading_tag(shared_lgamma, "signgam") == "XSI"


def test_normalize_href_resolves_parents_and_fragments() -> None:
    assert bm.normalize_href("../basedefs/aio.h.html") == "basedefs/aio.h.html"
    assert bm.normalize_href("functions/read.html#tag_17") == "functions/read.html"
    assert bm.normalize_href("idx/../functions/read.html") == "functions/read.html"


def test_is_base_class_treats_markings_as_base() -> None:
    assert vs.is_base_class("BASE")
    assert vs.is_base_class("CX")
    assert vs.is_base_class("OB")
    assert not vs.is_base_class("XSI")
    assert not vs.is_base_class("SHM")


def test_slug_exceptions_agree_with_the_committed_manifest() -> None:
    rows = vs.load_manifest(vs.MANIFEST)
    by_id = {r["identifier"]: r for r in rows}
    for identifier, expected in vs.SLUG_EXCEPTIONS.items():
        assert identifier in by_id, identifier
        assert by_id[identifier]["canonical_url"].endswith("/" + expected), identifier


def test_committed_manifest_rows_are_well_formed() -> None:
    report = CapturingReport()
    rows = vs.load_manifest(vs.MANIFEST)
    vs.gate_manifest_structure(rows, report)
    assert report.failures == 0, report.fails
    assert len(rows) == 1510


def test_committed_manifest_tags_pass_the_audit() -> None:
    report = CapturingReport()
    vs.gate_tags(vs.load_manifest(vs.MANIFEST), report)
    assert report.failures == 0, report.fails


def test_skill_lint_flags_dashes_and_limits(tmp_path, monkeypatch) -> None:
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: posix-issue8-os-dev\n---\n\n# T\n\nbad \u2014 dash\n")
    monkeypatch.setattr(vs, "SKILL", skill)
    report = CapturingReport()
    vs.gate_skill_lint(report)
    assert any("dashes" in message for message in report.fails)


def test_originality_lint_flags_html_and_skips_fences(tmp_path, monkeypatch) -> None:
    (tmp_path / "bad.md").write_text("<p>scraped prose</p>\n")
    (tmp_path / "good.md").write_text("text\n\n```html\n<div>example</div>\n```\n\nmore `text`\n")
    monkeypatch.setattr(vs, "REPO", tmp_path)
    report = CapturingReport()
    vs.gate_originality(report)
    assert report.failures == 1, report.fails
    assert "bad.md" in report.fails[0]


def test_skill_lint_flags_compliance_claims_and_missing_readme_trademark(
    tmp_path, monkeypatch
) -> None:
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "---\nname: posix-issue8-os-dev\n---\n\n"
        "# Issue 8 OS Development\n\n"
        "POSIX\u00ae is a registered trademark of the "
        "Institute of Electrical and Electronic Engineers, Inc. "
        "UNIX\u00ae is a registered trademark of The Open Group.\n\n"
        "This OS is POSIX-compliant.\n"
    )
    readme = tmp_path / "README.md"
    readme.write_text("# posix-issue8-os-dev\n\nImplements POSIX.\n")
    monkeypatch.setattr(vs, "SKILL", skill)
    monkeypatch.setattr(vs, "README", readme)
    report = CapturingReport()
    vs.gate_skill_lint(report)
    assert any("compliance claim" in message for message in report.fails)
    assert any("README.md" in message and "trademark" in message for message in report.fails)
    assert any("README.md" in message and "compliance" in message for message in report.fails)
