# POSIX.1-2024 (Issue 8) Skill & OS Conformance Validation Plan

## 1. Purpose and Scope

This document defines a two-tier validation architecture to guarantee complete, verifiable coverage of **The Open Group Base Specifications Issue 8 (IEEE Std 1003.1-2024)** across two repositories:

1. **Skill Repository (`posix-issue8-os-dev`):** Proves that the AI agent skill indexes and routes deterministically to 100% of Issue 8 chapters, system headers, C interfaces, utilities, and rationale sections without redistributing copyrighted specification prose.
2. **Target OS Repository (Kernel, `libc`, Headers, Shell, Core Utilities):** Proves that operating system components developed with the skill satisfy Issue 8 compile-time, link-time, and runtime requirements.

> **Copyright & Trademark Boundary:** All manifest files and automated validation scripts in the skill repository must index **uncopyrightable technical facts only** (identifier names, header paths, option group codes, and canonical `pubs.opengroup.org` URLs). Never store or mirror verbatim prose or tables from IEEE or The Open Group. POSIX® is a registered trademark of the IEEE, and UNIX® is a registered trademark of The Open Group.

---

## 2. Layer 1: Skill-Level Coverage Validation (Skill Repository CI)

Because `posix-issue8-os-dev` uses deterministic URL routing (`https://pubs.opengroup.org/onlinepubs/9799919799/...`) rather than bundled specification text, completeness can be verified programmatically in CI.

### 2.1 Master Index Diffing (`idx/` Completeness Gate)

The Open Group publishes master index pages listing every standardized identifier across all four volumes of Issue 8:

* **Base Definitions (XBD):** `https://pubs.opengroup.org/onlinepubs/9799919799/idx/xbd.html`
* **System Interfaces (XSH):** `https://pubs.opengroup.org/onlinepubs/9799919799/idx/xsh.html`
* **Shell & Utilities (XCU):** `https://pubs.opengroup.org/onlinepubs/9799919799/idx/xcu.html`
* **Rationale (XRAT):** `https://pubs.opengroup.org/onlinepubs/9799919799/idx/xrat.html`

**Validation Procedure:**
1. Maintain a machine-readable manifest (`references/issue8-manifest.tsv`) with columns:
   `volume | identifier | category | conformance_group | canonical_url`
2. Run a CI script that fetches the HTML index listings (`idx/*.html`), extracts only the identifier names and relative `href` paths, and diffs them against `references/issue8-manifest.tsv`.
3. **Pass Criteria:** Zero missing headers (~83 headers), zero missing functions/macros/types (~1,400+ interfaces), and zero missing utilities (~160+ utilities).

### 2.2 Canonical URL Liveness & Slug-Exception Verification

Simple string-to-URL interpolation fails on special characters and subdirectory paths. Run an automated link-verification script across every entry in `references/issue8-manifest.tsv`:

* **HTTP Status Check:** Every routed URL must return `HTTP 200 OK` (with rate-limited, cached CI runs so `pubs.opengroup.org` is not hammered on every commit).
* **Mandatory Slug-Exception Tests:** Explicitly assert URL resolution for Open Group naming edge cases:
  * **Subdirectory Headers:** `/` converts to `_` (e.g., `<sys/mman.h>` -> `basedefs/sys_mman.h.html`, `<netinet/in.h>` -> `basedefs/netinet_in.h.html`).
  * **Special Shell Built-ins:** Punctuation commands map to word slugs (e.g., `:` -> `utilities/colon.html`, `.` -> `utilities/dot.html`).
  * **Volume-Prefixed Chapters:** Verify `V1_chap<NN>.html` (XBD), `V2_chap<NN>.html` (XSH), `V3_chap<NN>.html` (XCU), and `V4_<vol>_chap<NN>.html` (XRAT).

### 2.3 Mandatory Base vs. Option Group Classification Audit

Issue 8 promotes several former Issue 7 option groups (such as threads, barriers, spinlocks, read-write locks, monotonic clocks, timers, `mmap`, shared memory objects, and `posix_spawn`) into the mandatory **Base**.

* **Validation Procedure:** Cross-check the `conformance_group` column in `references/issue8-manifest.tsv` against XBD Chapter 2 (`V1_chap02.html`).
* **Pass Criteria:**
  * 100% of mandatory Issue 8 Base interfaces are tagged `BASE`.
  * 100% of optional interfaces (e.g., `XSI`, `ADV`, `ML`, `TPI`, `TMR`) map to their corresponding `_POSIX_*` or `_XOPEN_*` feature-test macro in `<unistd.h>`.

### 2.4 Context-Budget & Copyright Linting

* **Context Window Guard:** Fail CI if `SKILL.md` exceeds 400 lines or 4,000 tokens.
* **Anti-Scraping Linter:** Scan all Markdown and data files in the repository to confirm no multi-sentence prose blocks or HTML fragments from `pubs.opengroup.org` were committed.

---

## 3. Layer 2: OS & Component Conformance Validation (Target OS CI)

To prove that an OS kernel, `libc`, header tree, and shell built with the skill implement the full standard, integrate the following four verification stages into the OS build pipeline.

### 3.1 Standalone Header & Feature-Test Macro Matrix

Per XSH Section 2.2, every POSIX header must be self-contained and expose exact conformance constants when requested via feature-test macros.

**Validation Procedure:**
1. Auto-generate one minimal `.c` translation unit per Issue 8 header (~83 files), containing only `#include <header.h>` and `_Static_assert` checks on version constants.
2. Compile every file under strict ISO C17 and Issue 8 flags:
   ```sh
   cc -std=c17 -D_POSIX_C_SOURCE=202405L -Wall -Wextra -Werror -pedantic -c test_<header>.c
   ```
3. Run a second pass with `-D_XOPEN_SOURCE=800` for XSI conformance.
4. **Pass Criteria:**
   * All ~83 translation units compile cleanly with zero warnings or prior-include dependencies.
   * `<unistd.h>` defines `_POSIX_VERSION == 202405L`, `_POSIX2_VERSION == 202405L`, and (when XSI is enabled) `_XOPEN_VERSION == 800`.

### 3.2 AST & Binary Symbol-Table ABI Diffing (`libclang` & `nm`)

Compiling headers alone does not catch missing function declarations or leaked vendor extensions.

* **Header AST Audit (`libclang`):**
  * Parse the OS header tree with `-D_POSIX_C_SOURCE=202405L` and extract all exposed typedefs, struct/union members, enum constants, macros, and function prototypes.
  * Diff against `references/issue8-manifest.tsv` to flag:
    1. **Missing Symbols:** Any `BASE` interface absent from its designated header.
    2. **Namespace Pollution (XSH 2.2):** Any non-standard identifier exposed outside the reserved `_` / `__` implementation namespace when `_POSIX_C_SOURCE=202405L` is active.
* **Binary Linkage Audit (`nm` / `readelf`):**
  * Extract all global defined symbols from `libc.a`, `libm.a`, `libpthread.a` (or unified `libc.so`) using `nm -g --defined-only`.
  * **Pass Criteria:** Every function declared in the Issue 8 headers resolves to an exported symbol in the C runtime libraries with matching ABI signatures.

### 3.3 Async-Signal-Safety & Cancellation Point Verification

* **Async-Signal-Safety (XSH 2.4):** Maintain a call-graph check (via compiler `-fcallgraph-info` or static analysis) over all functions listed on the Issue 8 async-signal-safe table to verify none call `malloc`, `free`, or non-reentrant `FILE` locks.
* **Thread Cancellation Points (XSH 2.9.5):** Verify via static annotations or runtime cancellation tests that every mandatory cancellation point (e.g., `read`, `write`, `open`, `close`, `nanosleep`, `pthread_cond_wait`, `ppoll`) checks pending thread cancellation state.

### 3.4 Automated Runtime Conformance Suites

While official POSIX branding requires The Open Group's commercial certification suites (`VSX-PCTS`, `VSTH`, `VSC`), combine these open-source suites in CI for broad behavioral coverage:

| Test Suite | Target OS Layer | What It Validates |
| :--- | :--- | :--- |
| **`libc-test` (musl)** | `libc`, headers, `libm` | Header types, math precision, `stdio`, `string`, `stdlib`, `pthread`, and subtle `errno` edge cases |
| **Open POSIX Test Suite (OPTS)** | Kernel + `pthread` / RT | Threads, mutexes, condvars, barriers, semaphores, clocks, timers, signals, and message queues |
| **Linux Test Project (LTP)** | Kernel syscalls + VFS | Syscall boundary conditions, file descriptors, permissions, and mandatory vs. optional `errno` precedence |
| **POSIX Shell Spec Suites (`yash` / `dash` / `oil`)** | `/bin/sh` + core utilities | XCU Ch. 2 grammar, quoting (`$'...'`), `set -o pipefail`, redirections, special built-ins, and exit codes (`0`, `1-125`, `126`, `127`, `>128`) |

---

## 4. Summary Checklist & CI Gate Policy

| Gate Stage | Frequency | Repository | Blocking Criteria |
| :--- | :--- | :--- | :--- |
| **1. Manifest & URL Audit** | Every PR + Weekly Cron | Skill Repo | Any unmapped Issue 8 item, dead URL, or prose leak |
| **2. Header Matrix & AST Diff** | Every PR | OS Repo | Any header compile error, missing `BASE` symbol, or namespace leak |
| **3. Binary Symbol Linkage** | Every PR | OS Repo | Any declared Issue 8 API missing from linked `libc` |
| **4. Runtime POSIX Suites** | Nightly / Release | OS Repo | Any regression in `libc-test`, OPTS, syscall `errno` tests, or `sh` spec tests |