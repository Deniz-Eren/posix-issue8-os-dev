# Tasks

## Purpose

Record all the tasks of posix-issue8-os-dev. Give the status and the date for each task.

## Structure

Each task is a checkbox. The checkbox can have a date. The tasks are in groups by category.

## Formatting Rules

- Use `- [ ] <type>: <description>` for the other tasks.
- Use `- [x] COMPLETE YYYY-MM-DD <type>: <description>` for complete tasks.
- Put the tasks below `<!-- [CAT] Category -->` comments.
- Do not remove completed tasks.

<!-- [CAT] Scaffolding -->

- [x] COMPLETE 2026-11-19 scaffold: apply agent-scaffolding 0.2.0

<!-- [CAT] Development -->

- [x] COMPLETE 2026-11-19 feat: write the root SKILL.md and references/issue8-url-map.md
- [x] COMPLETE 2026-11-19 feat: generate references/issue8-manifest.tsv from the Open Group idx pages
- [x] COMPLETE 2026-11-19 feat: implement scripts/validate_skill.py with the four validation gates
- [x] COMPLETE 2026-11-19 build: add the validate targets and the CTest registration to the CMake build
- [x] COMPLETE 2026-11-19 test: add pytest coverage for the validator
- [x] COMPLETE 2026-11-19 docs: run the full validation and finalize the skill
- [x] COMPLETE 2026-11-20 docs: refine root SKILL.md prose and add the Simplified Technical English glossary
- [x] COMPLETE 2026-11-22 docs: audit and update POSIX references to work-in-progress POSIX.1-2024 phrasing
- [x] COMPLETE 2026-11-23 fix: parse compound option tags and per-identifier shared-page declarations in scripts/build_manifest.py and regenerate references/issue8-manifest.tsv
