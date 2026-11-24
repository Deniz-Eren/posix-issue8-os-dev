# Changelog

## Purpose

Record the important changes of posix-issue8-os-dev. The format follows [Keep a Changelog](https://keepachangelog.com).

## Structure

- The `## [Unreleased]` section is at the top. Below it, the releases are newest first (git log order).
- Category headings of level 3 in each section: `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, and `### Security`. Put a heading into the file only when the section has content for it.

## Formatting Rules

- Release heading: `## [x.y.z] - YYYY-MM-DD`.
- The entries in each category are newest first (git log order).
- Write each entry as a complete sentence with a final period.

## [Unreleased]

### Fixed

- Fixed `scripts/build_manifest.py` to parse compound synopsis option tags (`[ OB XSI ]`, `[ SPN PS ]`, `[ FSC|SIO ]`, `[ XSI|SIO ]`, `[ TSA TSS ]`, `[ RPP|TPP ]`, `[ PS|TPS ]`) and match per-identifier declarations on shared XSH pages, regenerated `references/issue8-manifest.tsv` (reclassifying 17 compound-tagged optional interfaces out of `BASE` and 7 shared-page Base interfaces out of `XSI`), updated `SKILL.md` to move `msync` and `aio_fsync` to option groups, and expanded `scripts/validate_skill.py` and `tests/test_validate_skill.py` to guard against regressions (ADR-15).

### Changed

- Updated POSIX references across `SKILL.md`, `README.md`, `AGENTS.md`, `references/`, `docs/`, and `.agent-scaffolding.yml` to use work-in-progress POSIX.1-2024 (IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026) phrasing without compliance claims, added IEEE trademark attribution to public documentation, and added compliance-claim and trademark checks to `scripts/validate_skill.py` (ADR-14).
- Adopted optional Simplified Technical English guidance for repository prose: if a Simplified Technical English skill is present, use it when writing documents; otherwise skip it (ADR-13).
- The file `.gitignore` contains the CMake build directory `build/` (ADR-11).
- CMake and CTest replace the Makefile as the build system and the test runner. The build convention is out of source (ADR-11).

### Added

- The project domain glossary files `technical_terms.txt` and `allowed_phrases.txt` at the repository root for use when a Simplified Technical English skill is present.
- The validator `scripts/validate_skill.py` with the four skill-level gates of the validation plan, the `validate` and `validate-full` CMake targets, and the `validate-quick` CTest test. The first full run passes all six gates: the manifest covers the 1460 index identifiers and all 1510 routed URLs are live.
- The pytest suite `tests/` with ten offline tests for the validation tooling, registered as the `pytest` CTest test.
- The installable skill `SKILL.md` at the repository root, with the Issue 8 conformance baseline, the URL lookup protocol, the OS implementation checklists, and the gotchas.
- The URL routing and chapter index `references/issue8-url-map.md` for the four volumes of Issue 8.
- The factual manifest `references/issue8-manifest.tsv` with 1510 rows that map every Issue 8 chapter, header, interface, and utility to its canonical URL and option tag, with the generator `scripts/build_manifest.py`.
- Scaffolding with the agent-scaffolding agent skill 0.2.0. The configuration is in `.agent-scaffolding.yml`.
- The pre-existing documents `docs/init-prompt.md` and `docs/validation-plan.md` as immutable specifications.
