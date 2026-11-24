# posix-issue8-os-dev

Write and audit OS kernels, syscalls, libc, system headers, `sh`, and core utilities working toward POSIX.1-2024 compatibility against The Open Group Base Specifications Issue 8 (IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026), with deterministic URL routing and automated skill-level coverage validation.

This repository is an installable agent skill. [SKILL.md](SKILL.md) at the repository root is the skill; the user installs it from this repository. The skill routes to the canonical Open Group URLs instead of bundling specification text, and `scripts/validate_skill.py` verifies the coverage of the routing data. The development of this repository follows [docs/init-prompt.md](docs/init-prompt.md) and [docs/validation-plan.md](docs/validation-plan.md).

## Commands

```bash
cmake -S . -B build
cmake --build build --target lint
cmake --build build --target format-check
cmake --build build --target validate          # offline validation gates
ctest --test-dir build --output-on-failure     # registered tests and gates
cmake --build build --target validate-full     # all gates with live URL checks
```

The pytest suite arrives with the test task.

## Documentation

- [SKILL.md](SKILL.md): the installable skill (the product of this repository)
- [AGENTS.md](AGENTS.md): governance for AI agents (modes, git protocol, pre-commit checklist)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): overview of the system and the directory structure
- [docs/CONVENTIONS.md](docs/CONVENTIONS.md): file names, document formatting, and copyright rules
- [docs/init-prompt.md](docs/init-prompt.md): the specification for this skill repository (immutable)
- [docs/validation-plan.md](docs/validation-plan.md): the validation architecture (immutable)
- Skills for the development of this repository:
  - [cmake](docs/skills/cmake/SKILL.md)
  - [create-skill](docs/skills/create-skill/SKILL.md)
  - [git](docs/skills/git/SKILL.md)
  - [keepachangelog](docs/skills/keepachangelog/SKILL.md)
  - [pytest](docs/skills/pytest/SKILL.md)
  - [ruff](docs/skills/ruff/SKILL.md)
  - [state-management](docs/skills/state-management/SKILL.md)

## Trademarks

POSIX® is a registered trademark of the Institute of Electrical and Electronic Engineers, Inc. UNIX® is a registered trademark of The Open Group. This project is not a certification, and it implies no endorsement by the IEEE or The Open Group.

## License

The MIT License governs this project. See [LICENSE.md](LICENSE.md).

Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>

For third-party attributions, see [docs/THIRD-PARTY-NOTICES.md](docs/THIRD-PARTY-NOTICES.md).
