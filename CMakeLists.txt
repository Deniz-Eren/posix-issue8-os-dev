# Copyright (c) 2026 Deniz Eren <deniz.eren@outlook.com>
# SPDX-License-Identifier: MIT
#
# Task runner for the Python tooling of this skill repository. No compiler is
# needed: the project() command declares no language. The tools run from the
# venv that requirements.txt pins (ADR-6). The build directory is out of
# source (ADR-11).

cmake_minimum_required(VERSION 3.28)
project(posix-issue8-os-dev NONE)

find_program(PYTHON3_EXECUTABLE NAMES python3 REQUIRED)

set(VENV_DIR "${CMAKE_SOURCE_DIR}/.venv")
set(PIP "${VENV_DIR}/bin/pip")
set(PYTEST "${VENV_DIR}/bin/pytest")
set(RUFF "${VENV_DIR}/bin/ruff")
set(PYTHON "${VENV_DIR}/bin/python")

# The venv installation runs only when the sentinel is missing. After a
# change to requirements.txt, remove .venv and run the venv target again.
add_custom_command(
  OUTPUT "${PYTEST}"
  COMMAND "${PYTHON3_EXECUTABLE}" -m venv "${VENV_DIR}"
  COMMAND "${PIP}" install --upgrade pip
  COMMAND "${PIP}" install -r "${CMAKE_SOURCE_DIR}/requirements.txt"
  USES_TERMINAL
  VERBATIM
)
add_custom_target(venv DEPENDS "${PYTEST}")

add_custom_target(lint
  COMMAND "${RUFF}" check .
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
  DEPENDS "${RUFF}"
  USES_TERMINAL
  VERBATIM
)

add_custom_target(format
  COMMAND "${RUFF}" format .
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
  DEPENDS "${RUFF}"
  USES_TERMINAL
  VERBATIM
)

add_custom_target(format-check
  COMMAND "${RUFF}" format --check .
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
  DEPENDS "${RUFF}"
  USES_TERMINAL
  VERBATIM
)

# The skill validation gates. The quick target runs the offline gates; the
# full target adds the live idx diff and the URL liveness check (ADR-5).
add_custom_target(validate
  COMMAND "${PYTHON}" "${CMAKE_SOURCE_DIR}/scripts/validate_skill.py"
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
  DEPENDS "${PYTHON}"
  USES_TERMINAL
  VERBATIM
)

add_custom_target(validate-full
  COMMAND "${PYTHON}" "${CMAKE_SOURCE_DIR}/scripts/validate_skill.py" --full
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
  DEPENDS "${PYTHON}"
  USES_TERMINAL
  VERBATIM
)

enable_testing()
add_test(
  NAME validate-quick
  COMMAND "${PYTHON}" "${CMAKE_SOURCE_DIR}/scripts/validate_skill.py"
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
)
add_test(
  NAME pytest
  COMMAND "${PYTEST}" "${CMAKE_SOURCE_DIR}/tests" -v
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
)
