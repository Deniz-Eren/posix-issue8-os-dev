---
name: posix-issue8-os-dev
description: Write and audit operating systems working toward POSIX.1-2024 compatibility against The Open Group Base Specifications Issue 8 (IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026). Use this skill when you write or review OS kernels, syscall interfaces, libc functions, system headers, sh, or core utilities that target IEEE Std 1003.1-2024 interfaces. Use it for compatibility checks, canonical specification URLs, feature test macros, option groups, errno rules, cancellation points, async-signal-safety, and test suites for POSIX.1-2024 components.
---

# Issue 8 OS Development

Trademark notice: POSIX® is a registered trademark of the Institute of Electrical and Electronic Engineers, Inc. UNIX® is a registered trademark of The Open Group. This skill is not a certification, and it implies no endorsement by the IEEE or The Open Group.

Use this skill to write and audit operating systems that target interfaces from POSIX.1-2024 (IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026): kernel syscalls, libc, headers, the shell (`sh`), and core utilities. It routes to the canonical specification pages. It has no specification text. Two data files do the routing:

- `references/issue8-url-map.md`: URL patterns and the chapter index for the four volumes.
- `references/issue8-manifest.tsv`: each chapter, header, interface, and utility with its canonical URL and its conformance tag.

## Target Standard and Interface Baseline

The default target is Issue 8 (POSIX.1-2024 / IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026), publication `9799919799`:

`https://pubs.opengroup.org/onlinepubs/9799919799/`

A system that targets the Issue 8 Base exposes these constants in `<unistd.h>` and `<limits.h>`:

| Constant | Value | Meaning |
|---|---|---|
| `_POSIX_VERSION` | `202405L` | The Base targets POSIX.1-2024 |
| `_POSIX2_VERSION` | `202405L` | The Shell and Utilities volume targets POSIX.1-2024 |
| `_XOPEN_VERSION` | `800` | X/Open System Interfaces (XSI), when the system has XSI |

### Mandatory in the Issue 8 Base

Issue 8 makes these former option groups mandatory in the Base. The pages of their interfaces show no option tag in the manifest:

- The full thread suite: `pthread_*` with mutexes, condition variables, barriers, spinlocks, and reader-writer locks.
- Semaphores: `sem_*`.
- Monotonic clocks and timers: `clock_gettime`, `clock_nanosleep`, `clock_settime`, `timer_create`, `timer_settime`, and related functions.
- Memory-mapped files: `mmap`, `mprotect`, `munmap`.
- Asynchronous I/O: `aio_cancel`, `aio_error`, `aio_read`, `aio_return`, `aio_suspend`, `aio_write`, `lio_listio`.

A libc that targets the Issue 8 Base must give `pthread_create`, `sem_open`, `aio_read`, and `mmap` with no feature-test gate for the Base feature set.

### The Remaining Option Groups

These stay option groups with their manifest tags. Gate their declarations and behavior behind the `_POSIX_*` or `_XOPEN_*` macros for each group in `<unistd.h>`:

- Shared memory objects: `shm_open`, `shm_unlink` (`SHM`).
- Process spawn: `posix_spawn`, `posix_spawnp` and the `posix_spawn_*` helpers (`SPN`).
- Process and range memory locking: `mlockall`, `munlockall` (`ML`), `mlock`, `munlock` (`MLR`).
- Synchronized I/O and file synchronization: `fsync` (`FSC`), `fdatasync` (`SIO`), `aio_fsync` (`FSC|SIO`, manifest tag `FSC`), `msync` (`XSI|SIO`, manifest tag `XSI`).
- Message passing: `mq_*` (`MSG`), process scheduling: `sched_*` (`PS`), typed memory (`TYM`), device control (`DC`), and the remaining groups in the manifest.

The `conformance_group` column of the manifest gives the tag of each interface: `BASE` or the primary option tag of its declaration. For compound tags such as `[ OB XSI ]` or `[ SPN PS ]`, the manifest records the primary option code (`XSI`, `SPN`). `CX` marks an ISO C extension that the standard includes in the Base, so a `CX` interface is Base. `OB` marks an obsolescent interface that is also Base.

### New in Issue 8

Issue 8 adds these interfaces that Issue 7 did not have (each is in the manifest): `strlcpy`, `strlcat`, `reallocarray`, `getentropy`, `pipe2`, `dup3`, `accept4`, `ppoll`, `secure_getenv`, `posix_spawn_file_actions_addchdir`, `pthread_cond_clockwait`, `dladdr`, the headers `<stdatomic.h>`, `<stdalign.h>`, `<uchar.h>`, and the gettext message-catalog interfaces. The shell adds `$'...'` quoting, `set -o pipefail`, and `read -d`. `arc4random` is missing from Issue 8. `getentropy` is the Issue 8 interface for this task.

## Workflow and Specification Lookup Protocol

Follow these steps for each subsystem that you write or review.

### Step 1: Design and Edge-Case Audit

Before you write or review an OS subsystem, apply the checklist below for that subsystem (headers and namespaces, syscalls and errno, signals and concurrency, shell and utilities). List the edge conditions for the subsystem. Include each mandatory and optional error number, each cancellation point, the async-signal-safety of each exported function, and the exit statuses of each utility.

### Step 2: Canonical Issue 8 URL Resolution

Resolve the accurate specification page before you commit to a behavior:

1. Look up the identifier in `references/issue8-manifest.tsv`. The row gives the canonical URL and the conformance tag.
2. For chapter-level rules, use the patterns in `references/issue8-url-map.md`.
3. Open only that page. Extract only the contract facts for the task: mandatory errors and optional errors, cancellation points, async-signal-safety, or utility exit statuses. Give the URL in the code review or the commit.

The canonical patterns:

- XBD chapters: `basedefs/V1_chapNN.html`
- Headers: `basedefs/<header>.h.html`, with `/` replaced by `_` (`sys_types.h.html`, `netinet_in.h.html`)
- XSH general rules: `functions/V2_chap02.html`
- Functions: `functions/<name>.html` (the name as the manifest shows it: `_Exit.html`, `FD_CLR.html`)
- XCU chapters: `utilities/V3_chap02.html`
- Utilities: `utilities/<name>.html`, with word slugs for punctuation built-ins (`colon.html`, `dot.html`)
- Rationale: `xrat/V4_xbd_chap01.html`, `xrat/V4_xsh_chap01.html`, `xrat/V4_xcu_chap01.html`

### Step 3: OS Compatibility Verification Gates

Check the target OS with four gates. These gates run in the target OS repository, with the manifest as the symbol reference:

1. **Standalone header matrix:** compile one translation unit for each Issue 8 header with `-std=c17 -D_POSIX_C_SOURCE=202405L -Wall -Wextra -Werror -pedantic`, and a second run with `-D_XOPEN_SOURCE=800`. Each header must compile with no warnings and no prior-include dependency.
2. **AST and symbol diff:** parse the header tree with `libclang` and `-D_POSIX_C_SOURCE=202405L`, and compare the exported symbols (`nm`, `readelf`) with `references/issue8-manifest.tsv`. Flag missing `BASE` interfaces and each non-standard identifier that is not in the reserved `__` or `_[A-Z]` namespace.
3. **Async-signal-safety and cancellation:** examine the call graph of each async-signal-safe function for `malloc`, `free`, or `FILE` locks. Examine each mandatory cancellation point for the pending-cancellation state.
4. **Runtime suites:** run `libc-test` (musl), the Open POSIX Test Suite, the LTP syscall and open-posix subsets, and a shell test suite (`yash`, `dash`, or `oil`).

## OS and Component Implementation Checklists

### Header and Namespace Hygiene (XSH 2.2)

- Each Issue 8 header compiles standalone. The header includes what it must have. It has no dependency on a prior include.
- Guard extensions with feature test macros. With `_POSIX_C_SOURCE=202405L`, expose the Issue 8 Base. With `_XOPEN_SOURCE=800`, add the XSI interfaces. Hide all else when the macros are missing or strict.
- Keep internal identifiers in the reserved namespaces: `__name` or `_Name` (underscore plus uppercase) for each scope, `_name` (underscore plus lowercase) for file scope only.
- Expose only the macros, typedefs, and declarations that the standard gives to that header. Look at the manifest for the symbol set of the header.
- Option-group contents stay behind their macros: for example, `<mqueue.h>` exposes `mq_open` only when `_POSIX_MESSAGE_PASSING` is active.

### Kernel Syscalls, Libc Wrappers, and errno (XSH 2.3)

- Do not set `errno` to `0`. Set `errno` only on the failure path. Do not clear it on success.
- The specification has two error classes: mandatory ("shall fail") and optional ("may fail"). Check the precedence when some errors apply. It names the error that wins.
- Keep `errno` thread-local in the full stack: the raw syscall layer returns the kernel error, and the wrapper keeps it. A wrapper that retries on `EINTR` documents the retry.
- Implement each mandatory cancellation point (`read`, `write`, `open`, `close`, `nanosleep`, `ppoll`, `pthread_cond_wait`, and the remaining list). It honors deferred cancellation at the safe point. No lock or resource stays held.
- Isolate raw syscalls from the `errno` machinery, from `FILE` stream locking, and from the cancellation state.

### Signals and Concurrency (XSH 2.4 and 2.9)

- Keep each async-signal-safe function free of `malloc`, `free`, non-reentrant interfaces, `FILE` locks, and mutable static state.
- Give `pthread_*`, `sem_*`, and `<stdatomic.h>` operations their specified memory ordering. Synchronization occurs at the acquire and release points. Plain loads and stores do not synchronize.
- In a multithreaded process, a signal handler and a fork child can call only async-signal-safe functions until `execve` or exit.
- Route signal disposition changes through the manifest-verified interfaces. Check the new Issue 8 interfaces such as `pthread_cond_clockwait` for their clock-selection semantics.

### Shell and Core Utilities (XCU and XBD 12)

- Follow the Utility Syntax Guidelines of XBD chapter 12. The option sequence is not important, unless the utility says so. `--` ends the options. Operands follow the options.
- Use the standard exit-status contract: `0` success, `1` to `125` failure, `126` found but not executable, `127` not found, greater than `128` death by signal.
- Special built-ins are different from regular built-ins. The special built-ins are `:`, `.`, `break`, `continue`, `eval`, `exec`, `exit`, `export`, `readonly`, `return`, `set`, `shift`, `times`, `trap`, and `unset`. A syntax error in a special built-in stops a non-interactive shell. A missing regular built-in gives exit status `127`.
- Implement the word-expansion sequence accurately: tilde, parameter, command substitution, arithmetic, field splitting, pathname expansion, quote removal.
- Include the new Issue 8 shell features as Base features: `$'...'` quoting, `set -o pipefail`, and `read -d`.

### Documentation, Names, and Trademark Hygiene

- Write goal-oriented wording for target OS status, such as "aims to follow POSIX.1-2024", "works toward POSIX.1-2024 compatibility", or "targets interfaces from IEEE Std 1003.1-2024". Do not claim certification, official conformance, or full compliance.
- Pin standard references to POSIX.1-2024 (IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026), unless a note explicitly documents legacy compatibility.
- Keep "POSIX" out of OS, project, and binary names.
- Write all comments, docstrings, and man pages from the ground up. Do not copy text from the IEEE or Open Group specification.
- Add the trademark note "POSIX® is a registered trademark of the Institute of Electrical and Electronic Engineers, Inc." to public documentation that names POSIX.

## Gotchas

- Do not put a fetched Open Group page into the context. Extract the one contract fact that the task must have, and cite the canonical `9799919799` URL.
- Use the manifest `conformance_group` column to tell the mandatory Base from the option groups. Expose the `_POSIX_*` or `_XOPEN_*` macros for each group in `<unistd.h>`. A `CX` tag is Base. `XSI`, `SHM`, `SPN`, `MSG`, and the remaining tags are options.
- Refer to the rationale pages in `xrat/` when a requirement looks ambiguous. Do that before you invent custom OS behavior.
- The `idx/` indexes and this manifest are the completeness reference. When the publication updates, regenerate the manifest with `scripts/build_manifest.py`, and run `scripts/validate_skill.py` to keep the routing verified.
