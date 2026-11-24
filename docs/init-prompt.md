Make an Agent Skill with the name `posix-issue8-os-dev` in a Git repository that is only for this skill. The root of this repository is the root of the skill. Thus, `SKILL.md` is in the root directory of the repository. Do not write the skill into a skills directory of an agent environment (for example `.agents/skills/` or `.claude/skills/`). The user installs the skill from the repository.

Read `docs/validation-plan.md` in the repository root first. In addition to creating the skill itself, implement the validation infrastructure and conformance workflows specified in `docs/validation-plan.md`.

The skill must be dedicated to developing a POSIX-compliant operating system and OS components (kernel syscalls, C standard library/libc, system headers, POSIX shell, and core utilities), targeting **The Open Group Base Specifications Issue 8 (IEEE Std 1003.1-2024)** by default.

### 1. Repository & File Layout
- Create `./SKILL.md` directly at the repository root. Keep it concise (under 400 lines) to preserve context window budget.
- Create `./references/issue8-url-map.md` containing a compact URL routing and chapter index for XBD, XSH, XCU, and XRAT in publication `9799919799` (with zero copied specification text).
- Implement the **Skill-Level Coverage Validation** tooling from `./validation-plan.md`:
  - `./references/issue8-manifest.tsv`: Canonical manifest mapping all Issue 8 headers, system interfaces, utilities, and chapters to their relative `9799919799` URLs and conformance profile tags (`BASE`, `XSI`, `ADV`, `ML`, `TPI`, etc.).
  - `./scripts/validate_skill.py` (or equivalent CLI script): Implements the four skill-repo validation gates from `./validation-plan.md` (diffing identifiers against Open Group `idx/` indices, verifying HTTP `200 OK` liveness and slug exceptions like `colon.html` and `sys_*.h.html`, verifying Base vs. Option Group tags, and enforcing the `SKILL.md` line limit and zero-copied-prose check).
  - `./.github/workflows/validate.yml` (or `Makefile` target): Runs the skill validation script automatically.
- Keep `./validation-plan.md` at the repository root as the reference specification for the validation architecture.
- Do **not** create `.agents/`, `.claude/`, `.cursor/`, or any other agent-specific skills subdirectories.
- If the current directory is not yet initialized as a Git repository, run `git init` so the repository root cleanly represents the installable skill root.

### 2. Strict Copyright, Licensing, and Trademark Constraints
- **Do NOT copy, scrape, or bundle specification text:** Never download, mirror, or paste prose, tables, or verbatim definitions from `pubs.opengroup.org` or IEEE into any file in this repository. (Fetching only bare identifier names and relative `href` paths from `idx/` pages to populate or verify `references/issue8-manifest.tsv` is permitted, as factual index lists are not copyrightable.)
- **Use deterministic URL routing instead:** Map Issue 8 chapters, headers, system interfaces, utilities, and rationale sections to their canonical Open Group URLs (`https://pubs.opengroup.org/onlinepubs/9799919799/...`) so the agent can look up or cite exact specification pages on demand during development without redistributing copyrighted text.
- **Author original engineering guidance only:** All checklists, implementation rules, namespace guards, and conformance test patterns in the skill must be newly written summaries of technical requirements, not copied specification prose.
- **Trademark compliance:** Include a brief notice in `SKILL.md` stating that POSIX® is a registered trademark of the IEEE and UNIX® is a registered trademark of The Open Group, without implying official certification or endorsement.

### 3. Required `SKILL.md` Contents

1. **YAML Frontmatter:**
   - `name: posix-issue8-os-dev`
   - `description:` Specific trigger description covering implementing or auditing POSIX-compliant OS kernels, syscalls, libc functions, system headers, POSIX `sh`, core CLI utilities, feature test macros, and conformance tests against The Open Group Base Specifications Issue 8 (IEEE Std 1003.1-2024).

2. **Target Standard & Conformance Baseline:**
   - Default to **Issue 8 (IEEE Std 1003.1-2024)** (`https://pubs.opengroup.org/onlinepubs/9799919799/`).
   - Define the core conformance constants that OS headers (`<unistd.h>`, `<limits.h>`) must expose:
     - `_POSIX_VERSION` = `202405L`
     - `_POSIX2_VERSION` = `202405L`
     - `_XOPEN_VERSION` = `800` (when supporting the X/Open System Interfaces / XSI option)
   - Highlight key Issue 8 baseline shifts for OS implementers: features previously optional in Issue 7 (threads, barriers, spinlocks, read-write locks, monotonic clocks, timers, memory-mapped files, shared memory objects, and `posix_spawn`) are mandatory in the Issue 8 Base, alongside new required APIs (`strlcpy`, `strlcat`, `reallocarray`, `getentropy`, `arc4random`, `pipe2`, `dup3`, `accept4`, `ppoll`, `secure_getenv`, `posix_spawn_file_actions_addchdir`, `pthread_cond_clockwait`, `dladdr`, `<stdatomic.h>`, `<stdalign.h>`, `<uchar.h>`, `gettext` interfaces) and shell additions (`$'...'`, `set -o pipefail`, `read -d`).

3. **Workflow & Specification Lookup Protocol:**
   - **Step 1 (Design & Edge-Case Audit):** Before writing or reviewing an OS subsystem, check the domain-specific OS implementation rules in `SKILL.md`.
   - **Step 2 (Canonical Issue 8 URL Resolution):** Look up exact paths in `./references/issue8-manifest.tsv` and `./references/issue8-url-map.md`, or construct the canonical Open Group Issue 8 URL to verify mandatory vs. optional error codes, cancellation points, async-signal-safety, or utility exit statuses:
     - Base Definitions (XBD) Chapters: `https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap<NN>.html`
     - System Headers (XBD): `https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/<header>.h.html` (replace `/` with `_` for subdirectory headers, e.g., `sys_types.h.html`, `sys_stat.h.html`, `netinet_in.h.html`)
     - System Interfaces General Rules (XSH Ch. 2): `https://pubs.opengroup.org/onlinepubs/9799919799/functions/V2_chap02.html`
     - C Functions & Syscall Wrappers (XSH): `https://pubs.opengroup.org/onlinepubs/9799919799/functions/<function>.html`
     - Shell & Utilities (XCU): `https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html` and `https://pubs.opengroup.org/onlinepubs/9799919799/utilities/<utility>.html` (using word slugs for special built-ins such as `colon.html` and `dot.html`)
     - Rationale (XRAT): `https://pubs.opengroup.org/onlinepubs/9799919799/xrat/V4_xbd_chap<NN>.html`, `V4_xsh_chap<NN>.html`, `V4_xcu_chap<NN>.html`
   - **Step 3 (OS Conformance Verification Gates — from `./validation-plan.md`):**
     - **Standalone Header Matrix:** Compile every Issue 8 header (~83 headers) in isolation with `-std=c17 -D_POSIX_C_SOURCE=202405L -Wall -Wextra -Werror -pedantic` (and a second pass with `-D_XOPEN_SOURCE=800`).
     - **AST & Symbol-Table ABI Diff:** Parse headers via `libclang` and diff exported `libc` symbols via `nm`/`readelf` against `references/issue8-manifest.tsv` to catch missing required symbols or leaked non-standard identifiers.
     - **Runtime Conformance Suites:** Validate behavioral, `errno`, signal-safety, concurrency, and shell compliance using `libc-test` (musl), Open POSIX Test Suite (OPTS), LTP syscall/open-posix subsets, and POSIX shell conformance suites (`yash`/`dash`/`oil`).

4. **OS & Component Implementation Checklists (Author Concisely):**
   - **Header & Namespace Hygiene (XSH 2.2):** Guard extensions when `_POSIX_C_SOURCE == 202405L` is defined; keep internal identifiers in `__` or `_[A-Z]`; ensure every POSIX header compiles standalone.
   - **Kernel Syscalls, Libc Wrappers & `errno` (XSH 2.3):** Never set `errno = 0`; distinguish mandatory ("shall fail") vs. optional ("may fail") error codes and verify `errno` precedence; isolate raw syscalls from thread-local `errno`, `EINTR` rules, cancellation points, and `FILE` stream locking.
   - **Signals & Concurrency (XSH 2.4 & 2.9):** Keep Issue 8 async-signal-safe functions free of non-reentrant locks, `malloc`, and static state; enforce memory ordering rules on `pthread_*`, `sem_*`, and `<stdatomic.h>`.
   - **Shell & Core Utilities (XCU):** Implement Utility Syntax Guidelines (XBD Ch. 12), mandatory `--` handling, standard exit codes (`0`, `1-125`, `126`, `127`, `>128`), and special vs. regular built-in semantics.

5. **Gotchas:**
   - Never dump entire fetched Open Group HTML pages into context; extract only the specific contract detail needed and cite the canonical `9799919799` URL.
   - Distinguish mandatory Issue 8 Base features from Option Groups (such as XSI, Advice, or Process Memory Locking) and expose the matching `_POSIX_*` / `_XOPEN_*` macros in `<unistd.h>`.
   - Consult Rationale (`xrat/`) whenever a requirement appears ambiguous before inventing custom OS behavior.

### 4. Post-Creation Validation
Before finishing:
1. Run `./scripts/validate_skill.py` (and fix any missing manifest entries, broken URL slugs, or linting errors until all skill-level checks in `./validation-plan.md` pass).
2. Verify that `./SKILL.md` exists at the repository root (not inside `.agents/skills/` or `.claude/skills/`), has valid YAML frontmatter with `name: posix-issue8-os-dev`, uses no em-dashes, stays under 400 lines, and contains zero verbatim text from IEEE or The Open Group.
