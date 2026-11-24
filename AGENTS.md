# AI Agent Governance

This file has the highest authority for AI agents that work in **posix-issue8-os-dev**. The skill files in [docs/skills/](docs/skills/) have the procedures with more information. This file links to them, and it does not give the same information again.

---

## Commit Mode

`operations.commit_mode` in `.agent-scaffolding.yml` is the single source of truth for the commit mode and for the signature behavior of the commits. Read the mode from there. The [git skill](docs/skills/git/SKILL.md) defines the behavior of the modes and their typical work. This file does not define the modes.

---

## Predict → Act → Verify

1. **Predict:** examine the task, plan the steps, and find the possible failures before you act.
2. **Act:** do the planned steps. Make an atomic commit after each phase.
3. **Verify:** run the checks (validation, tests, format, lint), and confirm that they are correct.

If verification is not correct, go back to Act, repair the problem, and verify again. Do not start the next phase until the current phase is correct.

---

## Failure Modes

| Failure | Step | If it continues |
|---|---|---|
| The build is not correct | Find the root cause. Repair the scaffolding (not the boilerplate). Run the build again. | After three attempts with no success, stop, and get the approval of the human |
| A test is not correct | Find the source of the failure, and repair it. Then run the tests again. | After three attempts with no success, stop, and get the approval of the human |
| The formatter or the linter does not accept its config | Remove one parameter at a time. Do a test again. Record an ADR. | If the config is not correct after that, use a config with no parameters, and record the uncertainty |
| A tool is not installed | Write in the skill of the tool that the tool must be installed. Record an ADR. | None |
| A git conflict | Stop the operation. Get the changes from the remote. Resolve the conflict. Attempt it again. | Put the decision to the human |
| The context or token limit is close | Give a summary of the earlier context. Link to files. Do not copy their content. | None |
| A validation gate fails because the Open Group site is unreachable | Run the gate in offline mode if it has one. Record the result as "not run". | Retry later, or get the approval of the human to skip |

---

## Boundaries for CLI Commands

| Command | Permitted | Approval necessary |
|---|---|---|
| Read files. Run `--version` checks. | ✓ | — |
| Run build, test, and formatter scripts | ✓ | — |
| Install the project dependencies in the venv (`make venv`) | ✓ | — |
| Fetch identifier indexes from `pubs.opengroup.org` (rate limited, cached) | ✓ | — |
| Commit | the commit mode in `.agent-scaffolding.yml` gives the rules | — |
| Install system packages | ✗ | ✓ |
| Erase project files | ✗ | ✓ |
| Change IMMUTABLE documents | ✗ | ✗ (not permitted) |
| Create `.github/`, `.agents/`, `.claude/`, `.cursor/`, or other platform directories | ✗ | ✓ |
| Push to a remote | ✗ | ✓ |

---

## Token and Context Management

- Load a skill only when it is necessary for the task.
- Link to skill files and documents. Do not copy their content.
- Give a summary of the earlier context. Do not give it again.
- Read connected files in one batch.
- Write `~` or `$HOME`. Do not write an absolute home path.
- Do not fetch whole Open Group specification pages into the context. Extract only the identifier facts that the task needs.

---

## Git Protocol

Read the identity from `.agent-scaffolding.yml` (`identity.git_author_name`, `identity.git_author_email`). The value `current_user` means the identity of the current user. Take the name and the email from the git configuration of the environment (`git config user.name`, `git config user.email`). Give the identity inline for each commit. Do not change git config:

```bash
git -c user.name="<name>" -c user.email="<email>" commit -F <message-file>
```

Each commit message obeys Conventional Commits. It has an empty line and an `Assisted-by:` footer at the end. The footer gives the names of the agent and the model **of the current session**. Do not copy them from earlier commits:

```
<type>[scope]: <description>

Assisted-by: <AgentName>:<Model> [+ <Tool> ...]
```

For the full procedure, see the [git skill](docs/skills/git/SKILL.md).

---

## Pre-Commit Checklist

Before each commit, verify:

- [ ] The commit message obeys Conventional Commits, and it has the `Assisted-by:` footer
- [ ] The build and the tests are correct (if applicable)
- [ ] The formatter reports no findings (if applicable)
- [ ] You updated `docs/TASKS.md` (`[x] COMPLETE YYYY-MM-DD`)
- [ ] `CHANGELOG.md` has an entry in `## [Unreleased]` for the change
- [ ] `docs/DECISIONS.md` has an ADR for each new decision
- [ ] `docs/THIRD-PARTY-NOTICES.md` has attribution for each new third-party component
- [ ] All new and changed source files have the copyright header
- [ ] New and changed text uses goal-oriented POSIX.1-2024 wording, makes no compliance or certification claims, and keeps the IEEE trademark notice intact (ADR-14)
- [ ] You did not change an IMMUTABLE document

For the update procedures, see the [state-management skill](docs/skills/state-management/SKILL.md).

---

## Rules for This Project

Rules that apply only to this project. Each rule links to the skill or the document with more information.

- `docs/init-prompt.md` and `docs/validation-plan.md` are immutable (ADR-4). Ask the user to authorize an edit.
- The repository root is the installable skill. Do not create `.agents/`, `.claude/`, `.cursor/`, `.github/`, or other platform directories (ADR-3 and ADR-5).
- The root `SKILL.md` stays under 400 lines, uses no em-dashes, and links only to the skill surface (`references/`, `scripts/`), never to `docs/` (ADR-3).
- Never copy specification prose from IEEE or The Open Group into any file. Fetch only bare identifier names, relative `href` paths, and option codes (ADR-8).
- If a Simplified Technical English skill is present, use it when writing or editing documents (with `technical_terms.txt` and `allowed_phrases.txt`); otherwise skip it (ADR-13).
- Run `cmake --build build --target lint`, `cmake --build build --target format-check`, and, when registered, `ctest --test-dir build --output-on-failure` before each commit (see the [cmake skill](docs/skills/cmake/SKILL.md)).

### POSIX Wording and Trademark Rules (ADR-14)

Apply these rules to all new and changed prose, comments, docstrings, and documentation:

- **Use work-in-progress, goal-oriented phrasing:** Frame support as an ongoing effort, using phrases such as "aims to follow POSIX.1-2024", "working toward POSIX.1-2024 compatibility", or "targets interfaces from IEEE Std 1003.1-2024".
- **Make no compliance or certification claims:** Never use phrases such as "POSIX certified", "POSIX conformant", "POSIX compliant", "POSIX-compliant", "Base-conformant", or "implements POSIX". Imply no certification or endorsement by the IEEE or The Open Group.
- **Pin references to the 2024 edition:** Reference POSIX.1-2024 (IEEE Std 1003.1-2024 / ISO/IEC/IEEE 9945:2026). Do not cite older editions (such as POSIX.1-2008 or POSIX.1-2017) unless explicitly documenting legacy compatibility or historical differences.
- **Keep "POSIX" out of names:** Do not use "POSIX" in prose titles or in target OS, project, or binary names. The existing repository and skill identifier `posix-issue8-os-dev` is the sole exception (ADR-14).
- **Author original documentation only:** Write all comments, docstrings, and man pages from scratch. Never copy text verbatim from IEEE or Open Group specifications (ADR-8).
- **Include trademark attribution:** Whenever "POSIX" appears in `SKILL.md`, `README.md`, or other public-facing documentation, include: `POSIX® is a registered trademark of the Institute of Electrical and Electronic Engineers, Inc.` (and `UNIX® is a registered trademark of The Open Group.` where UNIX is referenced).
