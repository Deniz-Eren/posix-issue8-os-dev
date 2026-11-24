# Conventions

## Purpose

Define the conventions of posix-issue8-os-dev for file names, document formatting, and copyright headers.

## Structure

The conventions are in groups by category: file names, document formatting, document purposes, and copyright headers.

## Formatting Rules

- You must obey all conventions. A convention with the mark "recommended" is an alternative.
- Record each deviation as an ADR in [DECISIONS.md](DECISIONS.md).

---

## File Names

| Type | Rule | Examples |
|---|---|---|
| Scaffolding documents in `docs/` | UPPERCASE. One word or a hyphenated name. | `TASKS.md`, `THIRD-PARTY-NOTICES.md` |
| Other documents | A clear name | `issue8-url-map.md` |
| Skills | `docs/skills/<lowercase-name>/SKILL.md`. The directory name is the same as the frontmatter `name` | `docs/skills/ruff/SKILL.md` |
| Skill at the repository root | `SKILL.md` in uppercase, at the root. The root is the installable skill root | `SKILL.md` |

## Document Formatting

- All generated markdown files in `docs/` (but not in `docs/skills/`) start with these three headings, in this sequence:

  ```
  ## Purpose
  ## Structure
  ## Formatting Rules
  ```

- Do not put markdown links in backticks.
- Procedures are only in skill files. Other documents link to them.
- The root `SKILL.md` uses no em-dashes.
- If a Simplified Technical English skill is present, use it when writing or editing documents; otherwise skip it.

## Document Purposes

| File | Contains | Must NOT contain |
|---|---|---|
| `SKILL.md` (root) | The installable agent skill for Issue 8 OS development | Links to `docs/`, governance content |
| `ARCHITECTURE.md` | The current structure and components | Decisions or causes |
| `DECISIONS.md` | ADRs (dated, append-only) | The current structure |
| `TASKS.md` | Tasks with their status | General information |
| `CHANGELOG.md` (root) | The important changes, in groups by version | Descriptions of the current architecture |
| `VISION.md` | The mission and principles | Tasks |
| `CONVENTIONS.md` | Names, formatting, and copyright rules | Decisions |
| `THIRD-PARTY-NOTICES.md` | Third-party attribution | Internal architecture |

## Copyright Headers

License: **MIT License**. Copyright line: Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>

Each file with comments starts with the copyright line in the comment syntax of its language, with an SPDX line below it (ADR-2).

| Files | Header |
|---|---|
| Python (`.py`) | `# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>` and `# SPDX-License-Identifier: MIT` (after the shebang line) |
| `CMakeLists.txt` | `# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>` and `# SPDX-License-Identifier: MIT` |
| YAML (`.yml`, `.yaml`), TOML (`.toml`) | `# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>` and `# SPDX-License-Identifier: MIT` |
| `requirements.txt` | `# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>` and `# SPDX-License-Identifier: MIT` |

**Exclusions:** markdown, TSV data files (plain data with no comment syntax), `.gitignore`, license files, JSON, `.agent-scaffolding.yml`, and immutable or append-only imported documents.
