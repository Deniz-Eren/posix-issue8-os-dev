# Vision

## Purpose

Define the long-term vision and the principles of posix-issue8-os-dev.

## Structure

The document has the mission, the principles, and the target result.

## Formatting Rules

- Use short and clear language.
- Look at the vision again and update it when the direction of the project changes. Record the change as an ADR in [DECISIONS.md](DECISIONS.md).

## Mission

Write and audit OS kernels, syscalls, libc, system headers, `sh`, and core utilities working toward POSIX.1-2024 compatibility against The Open Group Base Specifications Issue 8 (IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026), with deterministic URL routing and automated skill-level coverage validation.

## Principles

- **Single source of truth:** each procedure is in one skill file.
- **Always correct:** you do not commit a change that breaks the build, the tests, or the checks of the documents.
- **Traceable:** each decision is an ADR, and you give each AI-assisted commit the tag `Assisted-by:`.
- **No copied specification text:** the repository routes to canonical Open Group URLs. It stores only uncopyrightable facts such as identifier names, paths, and option codes.
- **Complete coverage:** every Issue 8 chapter, header, interface, and utility has a manifest entry that an automated gate can verify.

## Target Result

- `references/issue8-manifest.tsv` maps 100 percent of the Issue 8 chapters, headers, system interfaces, utilities, and rationale sections to their canonical `9799919799` URLs with conformance profile tags.
- `scripts/validate_skill.py` passes all four validation gates of [docs/validation-plan.md](validation-plan.md), and `make validate-full` is green.
- The skill at the repository root guides an agent to write and audit OS components that target interfaces from IEEE Std 1003.1-2024 (Issue 8), with original guidance only.

POSIX® is a registered trademark of the Institute of Electrical and Electronic Engineers, Inc.
