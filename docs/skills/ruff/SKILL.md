---
name: ruff
description: Run the ruff linter and formatter for the Python files of this project. Use this skill when you lint, format, or fix Python code in scripts/ and tests/.
---

# Ruff

`ruff` lints and formats the Python files. The configuration is in `ruff.toml` at the project root (ADR-7). The pinned version is in `requirements.txt`.

## Commands

Run the commands through the CMake targets (see the [cmake skill](../cmake/SKILL.md)):

```bash
cmake --build build --target lint          # ruff check .
cmake --build build --target format        # ruff format .
cmake --build build --target format-check  # ruff format --check .
```

To fix auto-repairable lint findings:

```bash
.venv/bin/ruff check --fix .
```

## Configuration

- `line-length = 100`
- `target-version = "py314"`
- Lint rule groups: `E`, `F`, `W`, `I`, `UP`, `B`

Do not add parameters without a clear cause. Record each deviation from the defaults as an ADR.

## Rules

- Run the `format` target before the `format-check` target, so that the formatter repairs the files first.
- A lint finding that you cannot repair with a code change needs an ADR if you silence it (for example with `# noqa`). Prefer a code change.
