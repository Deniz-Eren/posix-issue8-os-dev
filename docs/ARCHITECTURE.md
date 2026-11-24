# Architecture

## Purpose

Write the architecture of posix-issue8-os-dev in this document. Write the files, their structure, and the task of each component.

## Structure

The document has a system overview, the directory structure, component descriptions, and the integration points.

## Formatting Rules

- Write about the current condition only. Put decisions in [DECISIONS.md](DECISIONS.md).
- Use code blocks for directory trees.
- Link to skill files for procedures. Do not write the procedures here.

---

## System Overview

The repository is an installable agent skill for operating systems that target interfaces from POSIX.1-2024 (The Open Group Base Specifications Issue 8 / IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026). The root `SKILL.md` is the skill that agents load. It routes to the canonical Open Group URLs through a factual manifest, so the repository has no specification prose.

The validation tooling guards the skill data: a Python script compares the manifest against the live Open Group indexes, checks the URL liveness and the slug rules, audits the conformance tags, and lints the context budget and the originality of the content. The Makefile runs the tooling through the venv.

## Directory Structure

```
/
├── SKILL.md              ← The installable skill (the product)
├── AGENTS.md             ← Governance for AI agents (supreme authority)
├── README.md             ← Entry point
├── CHANGELOG.md          ← Changes between versions
├── LICENSE.md            ← MIT License
├── CMakeLists.txt        ← Task runner: venv, lint, format, validate, CTest
├── requirements.txt      ← Pinned development tools
├── ruff.toml             ← Linter and formatter configuration
├── .agent-scaffolding.yml ← Scaffolding configuration
├── references/
│   ├── issue8-url-map.md ← URL routing and chapter index for the four volumes
│   └── issue8-manifest.tsv ← Factual manifest of identifiers and canonical URLs
├── scripts/
│   └── validate_skill.py ← The four skill-level validation gates
├── tests/                ← Pytest suite for the validation tooling
└── docs/
    ├── ARCHITECTURE.md   ← This file
    ├── DECISIONS.md      ← ADRs
    ├── CONVENTIONS.md    ← Names, formatting, copyright
    ├── TASKS.md          ← Task records
    ├── THIRD-PARTY-NOTICES.md
    ├── VISION.md         ← Mission and principles
    ├── init-prompt.md    ← Immutable specification (input)
    ├── validation-plan.md ← Immutable specification (input)
    └── skills/           ← Governance skills for the development of this repository
```

## Component Descriptions

| Component | Purpose |
|---|---|
| `SKILL.md` | The agent skill: standard baseline, URL lookup protocol, OS implementation checklists, and gotchas |
| `references/issue8-url-map.md` | Compact URL routing and chapter index for XBD, XSH, XCU, and XRAT |
| `references/issue8-manifest.tsv` | The factual index of all Issue 8 identifiers with conformance tags and canonical URLs |
| `scripts/validate_skill.py` | Implements the four validation gates of `docs/validation-plan.md` |
| `tests/` | Local pytest fixtures and unit tests for the validator |
| `CMakeLists.txt` | Task runner that runs the venv setup, the tools, the validation gates, and the CTest suite |
| `docs/skills/` | Governance skills for the development of this repository; not part of the installed skill |

## Integration Points

| Component | References | Used By |
|---|---|---|
| `SKILL.md` | `references/issue8-url-map.md`, `references/issue8-manifest.tsv` | Agent platforms that install the skill |
| `scripts/validate_skill.py` | `references/issue8-manifest.tsv`, `docs/validation-plan.md` | `make validate`, `make validate-full` |
| `CMakeLists.txt` | `requirements.txt`, `.venv/`, `scripts/validate_skill.py` | Agents and contributors |
| `AGENTS.md` | `docs/skills/git`, `docs/skills/state-management` | All agents that develop this repository |

There is no `.agents/skills` symlink and no platform directory. The repository root is the installable skill root (ADR-3).

POSIX® is a registered trademark of the Institute of Electrical and Electronic Engineers, Inc.
