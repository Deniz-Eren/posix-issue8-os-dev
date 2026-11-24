---
name: pytest
description: Run the pytest test suite of this project through CTest. Use this skill when you run the tests, add tests, or debug a test failure for the validation tooling.
---

# Pytest

The test suite is in `tests/`. It tests the validation tooling with local fixtures, so the tests need no network access. The pinned version is in `requirements.txt`. CTest runs the suite (ADR-11).

## Commands

```bash
ctest --test-dir build --output-on-failure
```

To run the suite directly, or one test file or one test:

```bash
.venv/bin/pytest tests -v
.venv/bin/pytest tests/test_validate_skill.py
.venv/bin/pytest tests/test_validate_skill.py::test_name -v
```

## Rules

- The tests use only local fixtures. Do not write tests that fetch from `pubs.opengroup.org`.
- A new feature in `scripts/` gets a test for its pure functions (parsing, URL construction, counting, diffing).
- A test that fails is a build failure. Repair the code or the test before you commit.
