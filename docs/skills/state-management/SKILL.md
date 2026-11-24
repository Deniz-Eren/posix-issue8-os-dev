---
name: state-management
description: Procedures to update the state documents of the project, TASKS.md, DECISIONS.md, and THIRD-PARTY-NOTICES.md. Use this skill before each commit. Use it also when you complete a task or make a decision. Use it also when you add a third-party file or dependency.
---

# State Management

All state documents are in `docs/`. Do not erase entries. Write dates in ISO format (`YYYY-MM-DD`).

## TASKS.md

- **Add a task** in its `<!-- [CAT] ... -->` group: `- [ ] <type>: <description>`
- **Complete a task:** `- [x] COMPLETE YYYY-MM-DD <type>: <description>`

## CHANGELOG.md

The [keepachangelog skill](../keepachangelog/SKILL.md) gives the procedure for `CHANGELOG.md`. Put each important change into its `## [Unreleased]` section.

## DECISIONS.md

Add an ADR when you make an important decision, when you change a decision, or when you cancel a decision. This includes decisions about tools, deviations from defaults, and missing tools.

1. Find the highest ADR number and add 1.
2. Put the new ADR at the top of the file, below the `<!-- [CAT] Category -->` comment of its category. The ADRs are newest first (git log order):

   ```markdown
   ## ADR-N (YYYY-MM-DD): Title

   ### Context
   ### Decision
   ### Alternatives
   ### Consequences
   ```

3. To cancel a decision, add a new ADR with the words "Supersedes ADR-M". Do not edit that ADR.

## THIRD-PARTY-NOTICES.md

- For a **copied file or snippet**, add a Template A entry to Section 1.
- For a **package dependency**, add a Template B entry to Section 2.
- Include the source URL and the full license text.

## Immutable documents

`docs/init-prompt.md` and `docs/validation-plan.md` are immutable (ADR-4). Do not change them. If you find an issue in them, ask the user to authorize the edit, and record the authorization in the commit message.

## Before each commit

1. Update TASKS.md.
2. Add a CHANGELOG.md entry in `## [Unreleased]` for an important change (see the [keepachangelog skill](../keepachangelog/SKILL.md)).
3. Add an ADR if you made a decision.
4. Add a notice if you added a third-party component.
5. Make sure that all new and changed source files have the copyright header (see [CONVENTIONS.md](../../CONVENTIONS.md)).
