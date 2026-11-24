# Issue 8 URL Map

URL routing and chapter index for The Open Group Base Specifications Issue 8 (POSIX.1-2024 / IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026), publication `9799919799`. This file routes to the canonical pages. It has no specification text. The authoritative identifier list is `issue8-manifest.tsv` in this directory.

Trademark notice: POSIX® is a registered trademark of the Institute of Electrical and Electronic Engineers, Inc. UNIX® is a registered trademark of The Open Group.

Base URL: `https://pubs.opengroup.org/onlinepubs/9799919799/`

## URL Patterns

| Content | Pattern (path after the base URL) | Rules |
|---|---|---|
| XBD chapter | `basedefs/V1_chapNN.html` | `NN` is the zero-padded chapter number |
| Header page | `basedefs/<slug>.h.html` | `/` in the header name becomes `_`: `sys/mman.h` gives `sys_mman.h.html`, `netinet/in.h` gives `netinet_in.h.html` |
| XSH chapter | `functions/V2_chapNN.html` | `V2` is the XSH volume prefix |
| Function page | `functions/<name>.html` | `name` is the exact interface name, case sensitive: `_Exit`, `FD_CLR`, `a64l` |
| XCU chapter | `utilities/V3_chapNN.html` | `V3` is the XCU volume prefix |
| Utility page | `utilities/<name>.html` | Punctuation built-ins use word slugs: `:` gives `colon.html`, `.` gives `dot.html` |
| Rationale page | `xrat/V4_<vol>_chapNN.html` | One rationale page per volume: `V4_xbd_chap01.html`, `V4_xsh_chap01.html`, `V4_xcu_chap01.html` |
| Index pages | `idx/<page>.html` | `xbd.html`, `head.html`, `xsh.html`, `functions.html`, `xcu.html`, `shell.html`, `utilities.html`, `xrat.html` |

## XBD Chapters (Base Definitions)

| Chapter | Title | Path |
|---|---|---|
| 1 | Introduction | `basedefs/V1_chap01.html` |
| 2 | Conformance | `basedefs/V1_chap02.html` |
| 3 | Definitions | `basedefs/V1_chap03.html` |
| 4 | General Concepts | `basedefs/V1_chap04.html` |
| 5 | File Format Notation | `basedefs/V1_chap05.html` |
| 6 | Character Set | `basedefs/V1_chap06.html` |
| 7 | Locale | `basedefs/V1_chap07.html` |
| 8 | Environment Variables | `basedefs/V1_chap08.html` |
| 9 | Regular Expressions | `basedefs/V1_chap09.html` |
| 10 | Directory Structure and Devices | `basedefs/V1_chap10.html` |
| 11 | General Terminal Interface | `basedefs/V1_chap11.html` |
| 12 | Utility Conventions | `basedefs/V1_chap12.html` |
| 13 | Namespace and Future Directions | `basedefs/V1_chap13.html` |
| 14 | Headers | `basedefs/V1_chap14.html` |

## XSH Chapters (System Interfaces)

| Chapter | Title | Path |
|---|---|---|
| 1 | Introduction | `functions/V2_chap01.html` |
| 2 | General Information | `functions/V2_chap02.html` |

Chapter 2 of XSH carries the rules that govern every function page: header namespace rules (2.2), errno conventions (2.3), signal concepts (2.4), thread interaction, and the cancellation points (2.9).

## XCU Chapters (Shell and Utilities)

| Chapter | Title | Path |
|---|---|---|
| 1 | Introduction | `utilities/V3_chap01.html` |
| 2 | Shell Command Language | `utilities/V3_chap02.html` |
| 3 | Utilities | `utilities/V3_chap03.html` |

The utility entries of chapter 3 are the individual pages `utilities/<name>.html`. The section index of chapter 2 is `idx/shell.html`; the alphabetical utility index is `idx/utilities.html`.

## XRAT Pages (Rationale)

| Page | Content | Path |
|---|---|---|
| XBD rationale | One page for all XBD chapters, sections A.1 to A.14 | `xrat/V4_xbd_chap01.html` |
| XSH rationale | One page for all XSH chapters | `xrat/V4_xsh_chap01.html` |
| XCU rationale | One page for all XCU chapters | `xrat/V4_xcu_chap01.html` |
| Portability | Portability considerations (informative) | `xrat/V4_port.html` |
| Subprofiling | Subprofiling considerations (informative) | `xrat/V4_subprofiles.html` |

## Header Count and Index Omissions

The header index `idx/head.html` lists 86 headers. The alphabetical utility index `idx/utilities.html` lists 155 utilities and omits the two punctuation built-ins `:` and `.`; their pages exist at `utilities/colon.html` and `utilities/dot.html`. The manifest contains both, so its utility count is 157.
