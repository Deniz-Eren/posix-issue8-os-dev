---
name: cmake
description: Configure the CMake build of this project and run its targets for the venv, lint, format, validation, and tests. Use this skill when you prepare the environment, run checks, or run the test suite with CTest.
---

# CMake and CTest

CMake drives the development tools as a task runner. The project declares no language, so no compiler is needed. The build directory is `build/` (out of source). The tools run from the venv that `requirements.txt` pins (ADR-6), and CMake creates the venv on demand. The build system decision is ADR-11.

## Commands

```bash
cmake -S . -B build                      # configure (add -G Ninja for the Ninja generator)
cmake --build build --target venv        # create .venv and install the pinned tools
cmake --build build --target lint        # ruff check .
cmake --build build --target format      # ruff format .
cmake --build build --target format-check
ctest --test-dir build --output-on-failure   # run the registered tests and gates
cmake --build build --target validate        # quick validation gates
cmake --build build --target validate-full   # all gates with live URL checks
```

The `validate-quick` CTest test runs the offline gates. The pytest suite registers its own CTest test when the tests are in the repository.

## Procedure

1. Configure once per clone: `cmake -S . -B build`.
2. The venv installs automatically when a tool target needs it and `.venv/` is missing. After a change to `requirements.txt`, remove `.venv/` and run the `venv` target again.
3. Before each commit, run `lint`, `format-check`, and, when they exist, `ctest --test-dir build --output-on-failure` and `validate`.
4. A failing target or test is a build failure. Repair the cause, and run it again.

## Notes

- `validate-full` needs network access to `pubs.opengroup.org` and uses the cache in `.url-cache/`.
- CTest prints one line per test and the full output of failures with `--output-on-failure`.
