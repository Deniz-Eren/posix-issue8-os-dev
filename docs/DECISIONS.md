# Decisions

## Purpose

Record the decisions about the architecture and the strategy of posix-issue8-os-dev. Give the context, the alternatives, and the consequences.

## Structure

Each decision is a block with the sections `Context`, `Decision`, `Alternatives`, and `Consequences`. You can read the block alone. The blocks are in groups by category. The ADRs are newest first (git log order).

## Formatting Rules

- Heading: `## ADR-N (YYYY-MM-DD): Title`, where N is the next sequential number.
- Subsections: `### Context`, `### Decision`, `### Alternatives`, `### Consequences`.
- The ADRs are newest first (git log order). Put a new ADR at the top of the file, below the `<!-- [CAT] Category -->` comment of its category.
- To replace a decision, add a new ADR that supersedes it. Do not change the old ADR.

<!-- [CAT] Content -->

## ADR-15 (2026-11-23): Compound synopsis option tags and per-identifier shared-page classification

### Context

`scripts/build_manifest.py` originally matched only a single bracketed code (`^\[\s*([A-Z][A-Z0-9]*)\s*\]`) in the first `<div class="box">` of each page. Auditing all 1,520 cached Issue 8 pages exposed two classification bugs:

1. **Compound option tags fell through to `BASE`:** 17 XSH interfaces carry space-separated (AND) or pipe-separated (OR) compound tags in their synopsis boxes: `encrypt` and `setkey` (`[ OB XSI ]`), `posix_spawnattr_{get,set}sched{param,policy}` (`[ SPN PS ]`), `aio_fsync` (`[ FSC|SIO ]`), `msync` (`[ XSI|SIO ]`), `pthread_attr_{get,set}stack` (`[ TSA TSS ]`), `pthread_mutex{,attr}_{get,set}prioceiling` (`[ RPP|TPP ]`), and `sched_get_priority_{max,min}` plus `sched_rr_get_interval` (`[ PS|TPS ]`). All 17 were silently tagged `BASE`, inflating the Base interface denominator and causing `SKILL.md` and `scripts/validate_skill.py` to list `msync` and `aio_fsync` as mandatory Base.
2. **Shared-page Base interfaces inherited a sibling's `[ XSI ]` box:** 7 Base XSH interfaces share a reference page with an XSI sibling whose box appears first in `SYNOPSIS`: `futimens` and `utimensat` (plain Base alongside `[ XSI ] utimes`), `lgamma`, `lgammaf`, and `lgammal` (ISO C alongside `[ XSI ] signgam`), and `tzname` and `tzset` (`[ CX ]` box after `[ XSI ] daylight`/`timezone`). All 7 were misclassified as `XSI`.

### Decision

- Extend `scripts/build_manifest.py` to parse single and compound margin tags (`[ A B ]` and `[ A|B ]`) and record the first non-marking option code as `conformance_group` (skipping pure markings such as `OB`, so `[ OB XSI ]` maps to `XSI`, `[ SPN PS ]` to `SPN`, `[ FSC|SIO ]` to `FSC`, `[ XSI|SIO ]` to `XSI`, `[ TSA TSS ]` to `TSA`, `[ RPP|TPP ]` to `RPP`, and `[ PS|TPS ]` to `PS`).
- For XSH interfaces, match the specific `SYNOPSIS` box or non-boxed declaration containing the identifier so shared pages classify each interface independently. When an interface is declared outside any option box in `SYNOPSIS`, preserve only a page-level pure marking (such as `CX`) from `DESCRIPTION` and otherwise emit `BASE`.
- Update `SKILL.md` to move `msync` and `aio_fsync` from the mandatory Base list to the option groups list, and expand `MUST_BE_BASE` and `MUST_BE_OPTIONAL` in `scripts/validate_skill.py` to guard all 17 compound-tagged optional interfaces and the 7 shared-page Base interfaces against regression.

### Alternatives

- Store raw compound expressions (such as `SPN PS` or `FSC|SIO`) in `conformance_group` (rejected: downstream manifest consumers and `KNOWN_CODES` expect a single margin code per row, and primary-code selection preserves single-token compatibility while keeping every optional interface out of the Base class).
- Hand-edit only the six initially reported rows in `references/issue8-manifest.tsv` (rejected: rebuilding the manifest would overwrite manual edits and leave the other 11 compound-tagged optionals and 7 shared-page Base interfaces misclassified).

### Consequences

- Regenerating `references/issue8-manifest.tsv` mechanically produces the exact Issue 8 Base-class XSH interface set (1,037 interfaces: 1,047 minus 17 compound-tagged optionals plus 7 shared-page Base interfaces).
- `SKILL.md`, `references/issue8-manifest.tsv`, and `scripts/validate_skill.py` agree with the live Issue 8 pages (consistent with ADR-12).

## ADR-14 (2026-11-22): Work-in-progress POSIX.1-2024 phrasing, naming, and trademark attribution

### Context

The repository and the root `SKILL.md` guide agents that write operating system components targeting The Open Group Base Specifications Issue 8 (POSIX.1-2024 / IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026). Earlier prose used phrases such as "POSIX-compliant" and "Base-conformant", and `README.md` and `references/issue8-url-map.md` omitted the IEEE trademark attribution for POSIX.

### Decision

All editable repository prose, comments, and documentation follow these rules:

- Frame OS support as ongoing work toward POSIX.1-2024 compatibility (for example, "targets interfaces from IEEE Std 1003.1-2024" or "working toward POSIX.1-2024 compatibility") and remove completed compliance or certification claims ("POSIX certified", "POSIX conformant", "POSIX compliant", "implements POSIX").
- Pin standard references to POSIX.1-2024 / IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026 unless explicitly documenting legacy compatibility.
- Keep `posix-issue8-os-dev` as the existing repository and skill identifier so that it matches the repository directory, installation path, and the immutable `docs/init-prompt.md` (ADR-4). Remove "POSIX" from prose titles (such as `# Issue 8 OS Development`) and instruct agents in `SKILL.md` to keep "POSIX" out of target OS, project, and binary names.
- Author all comments, docstrings, and man pages from scratch without copying IEEE or Open Group specification text (reinforcing ADR-8).
- Include the attribution "POSIX® is a registered trademark of the Institute of Electrical and Electronic Engineers, Inc." in public-facing documentation (`SKILL.md`, `README.md`, `references/issue8-url-map.md`, `docs/VISION.md`, and `docs/ARCHITECTURE.md`).
- Leave `docs/init-prompt.md` and `docs/validation-plan.md` untouched per ADR-4.

### Alternatives

- Rename the repository and skill identifier from `posix-issue8-os-dev` to a POSIX-free identifier (rejected by user decision: keeping the existing identifier avoids breaking the install path and diverges less from the immutable `docs/init-prompt.md`)
- Edit `docs/init-prompt.md` and `docs/validation-plan.md` in place (rejected: both documents are immutable under ADR-4)

### Consequences

- `scripts/validate_skill.py` checks `SKILL.md` and `README.md` for prohibited compliance claims and verifies the trademark notice in both files.
- `SKILL.md` includes a checklist section for target OS documentation, naming, and trademark hygiene.

## ADR-13 (2026-11-20): Optional Simplified Technical English for repository prose

### Context

The documents of this repository are for AI agents and for humans. Contributors write with different styles and different vocabulary. Using Simplified Technical English helps keep documentation concise and consistent, while not every environment has a Simplified Technical English skill installed. Because general Simplified Technical English dictionaries do not cover operating system terminology, a project glossary records the approved technical nouns, technical verbs, and multi-word phrases of this field.

### Decision

If a Simplified Technical English skill is present, use it when writing or editing repository documents; otherwise skip it. Keep the project domain glossary in `technical_terms.txt` and `allowed_phrases.txt` at the repository root so a Simplified Technical English checker can read them when available.

### Alternatives

- Require a specific external checker unconditionally (rejected: not all agent environments have a Simplified Technical English skill installed)
- Keep no shared domain glossary (rejected: domain terms for operating system development would be flagged repeatedly when a checker is used)

### Consequences

- Contributors and agents with a Simplified Technical English skill use it on new and changed documents, and skip it otherwise.
- Domain terms absent from a general dictionary go into `technical_terms.txt` or `allowed_phrases.txt`.
- The glossary files are plain text data files with `#` comments, and they carry the MIT copyright header.

## ADR-12 (2026-11-19): Live page data takes precedence for the conformance baseline

### Context

`docs/init-prompt.md` states that shared memory objects and posix_spawn are mandatory in the Issue 8 Base. The live Issue 8 pages disagree: the `shm_open` and `posix_spawn` pages carry the option tags `SHM` and `SPN`, and XBD chapter 2 lists `_POSIX_SHARED_MEMORY_OBJECTS` and `_POSIX_SPAWN` among the may-support constants. The same pages show that asynchronous I/O (`aio_*`, `lio_listio`) lost its option tag and is mandatory Base, which the init prompt does not list. The init prompt also names `arc4random` as a new Issue 8 interface, but no `arc4random` page exists in the publication.

### Decision

The user authorized the live page data as the ground truth. `SKILL.md` states the baseline with the accurate wording: threads, semaphores, monotonic clocks and timers, memory-mapped files, and asynchronous I/O are mandatory Base; shared memory objects and posix_spawn stay optional with their `SHM` and `SPN` tags; `arc4random` is absent from Issue 8. `docs/init-prompt.md` stays untouched with its immutable policy.

### Alternatives

- Copy the init prompt wording into `SKILL.md` (rejected: it contradicts the specification pages)
- Edit the init prompt (rejected: immutable without separate authorization)

### Consequences

- The skill teaches implementers to gate `shm_open` and `posix_spawn` behind their option macros.
- The manifest tags and the `SKILL.md` baseline agree, and the validator audits both against the same data.

<!-- [CAT] Tooling -->

## ADR-11 (2026-11-19): CMake and CTest drive the build and the tests

### Context

The first scaffolding used a Makefile. The user asked for CMake and CTest for the nicer test output, even though the repository builds no C or C++ program.

### Decision

CMake is the build system and the task runner. `project(posix-issue8-os-dev NONE)` declares no language, so no compiler is needed. The build convention is out of source (`build/`). CTest runs the registered tests and gates with `ctest --test-dir build --output-on-failure`. The `make` skill is replaced by the `cmake` skill. This supersedes the Makefile mechanism of ADR-5; the decision to run validation through build targets instead of a CI platform stays.

### Alternatives

- Keep the Makefile (rejected: the user wants the CTest output format)
- CMake with a language enabled (rejected: the repository builds no C or C++ program)

### Consequences

- `CMakeLists.txt` replaces the Makefile.
- The build convention in `.agent-scaffolding.yml` is `out-of-source`.
- The venv installs on demand through a CMake sentinel, so a tool target works after a fresh clone with one configure step.

<!-- [CAT] Content -->

## ADR-9 (2026-11-19): Manifest derivation from the Open Group pages

### Context

`references/issue8-manifest.tsv` needs complete coverage of the Issue 8 identifiers with conformance tags, but the repository stores no specification prose.

### Decision

`scripts/build_manifest.py` derives the manifest mechanically from the publication 9799919799 pages:

- Identifier names and relative `href` paths come from the `idx/` index pages (`head.html`, `functions.html`, `utilities.html`, and the rationale index pages).
- The `conformance_group` comes from the leading option tag of the synopsis box of each identifier page (for example `[ XSI ]`, `[ SPN ]`, `[ SHM ]`); a page with no tag is `BASE`.
- The chapter ranges (XBD ch1 to ch14, XSH ch1 to ch2, XCU ch1 to ch3) are canonical constants, because the `idx/` navigation pages do not link every chapter page directly.
- The punctuation utilities `:` and `.` (word slugs `colon.html` and `dot.html`) are curated additions, because the alphabetical utilities index omits them. The validator treats them as the only allowed extras over the index.
- The utilities `c17` plus the XSI Development Utilities set from XBD Chapter 2 (`admin`, `cflow`, `ctags`, `cxref`, `delta`, `get`, `nm`, `prs`, `rmdel`, `sact`, `sccs`, `unget`, `val`, `what`) are tagged `XSI` from the chapter text, because their pages carry no leading tag.
- In Issue 8 the XRAT has one rationale page per volume (`V4_xbd_chap01`, `V4_xsh_chap01`, `V4_xcu_chap01`) plus `V4_port` and `V4_subprofiles`.

The first build produced 1510 rows: 19 chapters, 86 headers, 1243 interfaces, 157 utilities, and 5 rationale pages.

### Alternatives

- A hand-written manifest (rejected: not auditable at this scale)
- Tags from memory or from the Issue 7 option lists (rejected: Issue 8 moved many interfaces between groups)

### Consequences

- The tags reflect the live Issue 8 pages, including the `CX` (ISO C) and `OB` (obsolescent) markings.
- A full rebuild fetches about 1500 pages once; the cache makes later runs fast.

## ADR-8 (2026-11-19): Original content only; identifier facts are the permitted data

### Context

The skill routes to The Open Group specification instead of redistributing it. `docs/init-prompt.md` forbids copied, scraped, or bundled specification text, and permits fetching bare identifier names and relative `href` paths from the `idx/` index pages.

### Decision

All checklists, rules, and guidance in this repository are original writing. The only data fetched from `pubs.opengroup.org` is uncopyrightable fact data: identifier names, relative `href` paths, option group codes, and HTTP status codes. The manifest stores only this fact data. No prose, tables, or verbatim definitions from the specification enter any file.

### Alternatives

- Bundling specification excerpts with a license agreement (rejected: the license is not available for redistribution)
- Linking without a manifest (rejected: the validation plan requires verifiable completeness)

### Consequences

- The anti-scraping linter can fail the build when it finds HTML fragments or long verbatim prose blocks.
- The manifest is a factual index, so the MIT license of this repository covers it.

## ADR-7 (2026-11-19): ruff configuration parameters

### Context

The tool-config module starts from the tool defaults and adds only parameters with a clear cause.

### Decision

`ruff.toml` sets `line-length = 100`, `target-version = "py314"`, and the lint rule groups `["E", "F", "W", "I", "UP", "B"]`. The version is pinned to 0.17.5. `ruff format` with the same `line-length` is the formatter.

### Alternatives

- The ruff default line length of 88 (rejected: 100 gives room for long identifier names in the manifest code without wrapping)
- A stricter rule set with `lint.select = ["ALL"]` (rejected: too many findings for a small tooling code base)

### Consequences
- All agents format and lint with the same parameters.
- New parameters need a clear cause and an ADR.

## ADR-6 (2026-11-19): Python tooling with a venv, ruff, and pytest

### Context

The validation tooling is Python. The project needs pinned tool versions so that all contributors and agents run the same tools.

### Decision

The tools run in a Python venv that `requirements.txt` pins. `ruff` is the linter and the formatter, and `pytest` is the test framework. The venv setup and the tool commands are Makefile targets (see ADR-5).

### Alternatives

- `pyproject.toml` with dependency groups
- Unpinned tools from the host system

### Consequences

- `requirements.txt` pins exact versions.
- `.venv/` is gitignored and is not part of the repository.
- The dev environment module of agent-scaffolding stays off; the venv procedure lives in the tool skills and the Makefile.

## ADR-5 (2026-11-19): Validation runs through Makefile targets, not a CI platform

### Context

`docs/validation-plan.md` asks for automated runs of the skill validation script. The user decided to not create `.github/` or any other CI platform directory.

### Decision

The Makefile provides the `validate` and `validate-full` targets that run `scripts/validate_skill.py`. This uses the Makefile alternative that `docs/init-prompt.md` allows.

### Alternatives

- `.github/workflows/validate.yml` (rejected by the user decision)
- No automation target

### Consequences

- No `.github/` directory exists.
- Anyone can run the gates with `make validate` or `make validate-full`.
- A future CI platform can call the same Makefile targets.

<!-- [CAT] Governance -->

## ADR-4 (2026-11-19): Pre-existing specification documents are immutable

### Context

`docs/init-prompt.md` and `docs/validation-plan.md` are the specifications for this repository. They were in the working tree before the scaffolding started.

### Decision

Both documents are imported with the policy `immutable`. Automated work does not change them. If an issue is found in them, the agent asks the user to authorize the edit.

### Alternatives

- `append-only`
- `editable`

### Consequences

- The documents keep their original text.
- The pre-commit checklist treats a change to them as not permitted without user approval.

## ADR-3 (2026-11-19): No agent platform directories; the repository root is the installable skill

### Context

`docs/init-prompt.md` forbids `.agents/`, `.claude/`, `.cursor/`, and other agent-specific skills directories. The user installs the skill from the repository. At the same time, this repository is developed as a project, so the governance skills must stay available for its own development.

### Decision

The repository root is the skill root with `SKILL.md` at the top level. The project keeps its governance skills in `docs/skills/` for the development of this repository. The standard `.agents/skills` symlink and all agent platform links are not created. The root `SKILL.md` does not link to `docs/`, so the installed skill surface contains no governance content.

### Alternatives

- The standard agent-scaffolding layout with the `.agents/skills` symlink (rejected: `docs/init-prompt.md` forbids it)
- Governance skills outside the repository

### Consequences

- `scripts/verify.sh` reports a FAIL for the missing standard agent link. The user approved this deviation.
- Agents that develop this repository read `AGENTS.md` and `docs/skills/` directly.
- The installed skill is only `SKILL.md`, `references/`, and the validation tooling.

## ADR-2 (2026-11-19): Project type, languages, and MIT license

### Context

The interview found no license, no tooling, and no build files. The repository combines skill documentation with Python validation tooling.

### Decision

The project type is `mixed` with the languages Python 3 and Markdown. The license is the MIT License with the copyright line `Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>`, resolved from `identity.current_user`. File headers carry an SPDX line (`SPDX-License-Identifier: MIT`) below the copyright line.

### Alternatives

- Type `documentation` (rejected: the repository ships executable validation tooling)
- A proprietary license or no license

### Consequences

- `LICENSE.md` contains the full MIT text.
- Source files start with the copyright line and the SPDX identifier.

## ADR-1 (2026-11-19): Adopt agent-scaffolding

### Context

The project must have governance, documentation, and agent instructions that work with all AI agents.

### Decision

Apply the agent-scaffolding agent skill 0.2.0 with the configuration in `.agent-scaffolding.yml`. The commit mode is AUTONOMOUS.

### Alternatives

- Documents and agent instructions that you write for each project
- Instructions for one platform only (for example only `CLAUDE.md` or only `.github/copilot-instructions.md`)

### Consequences

- `AGENTS.md` is the supreme authority for agent behavior.
- Procedures are only in `docs/skills/`.
- The state documents (`TASKS.md`, `CHANGELOG.md`, and `DECISIONS.md`) are up to date before each commit.
