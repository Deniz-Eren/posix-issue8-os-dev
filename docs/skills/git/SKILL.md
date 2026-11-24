---
name: git
description: Git conventions for this project. They include the commit identity, Conventional Commits messages, the Assisted-by footer, the commit modes, and the branch strategy. Use this skill when you make commits or write commit messages. Use it also when you tag releases or manage branches.
---

# Git

## Commit mode

The mode is `operations.commit_mode` in `.agent-scaffolding.yml` at the project root.

| Mode | Signature | Behavior | Typical work |
|---|---|---|---|
| AUTONOMOUS | `--no-gpg-sign` | The agent commits and does not stop | Usual maintenance and document changes |
| HITL | the default signature | Print `WAITING FOR GPG SIGNATURE`, and wait for the human | Important changes, security work, and releases |

## Identity

Read the identity from `.agent-scaffolding.yml` (`identity.git_author_name`, `identity.git_author_email`). The value `current_user` means the identity of the current user. Take the name and the email from the git configuration of the environment (`git config user.name`, `git config user.email`). Give it inline. Do not run `git config` to change the identity:

```bash
git -c user.name="<name>" -c user.email="<email>" commit -F <message-file>
```

In AUTONOMOUS mode, add `--no-gpg-sign`.

## Message format

Obey [Conventional Commits](references/COMMITS.md):

```
<type>[(scope)][!]: <description>

[body]

Assisted-by: <AgentName>:<Model> [+ <Tool> ...]
```

- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`, `scaffold`.
- Breaking changes: put `!` after the type, or add a `BREAKING CHANGE:` footer.
- `Assisted-by:` is necessary for commits with help from AI. It gives the names of the agent and the model **of the current session**. Do not copy the footer from earlier commits.

Example:

```
feat(parser): support nested tables

Assisted-by: agent-name:model-name
```

## Workflow

1. Run `git status`, and stage only the files for this change.
2. Look at the staged diff with `git diff --staged`.
3. Complete the pre-commit checklist in [AGENTS.md](../../../AGENTS.md). For the state documents, see the [state-management skill](../state-management/SKILL.md).
4. Commit with the identity command above.
5. Do not push without clear approval from the human.

## Versions and releases

- Obey [Semantic Versioning](references/semver.md). This project has no build configuration with a version field, so the version lives in [CHANGELOG.md](../../../CHANGELOG.md).
- Tag releases as `vX.Y.Z`. Move the content of `## [Unreleased]` in the changelog into the new version section (see the [keepachangelog skill](../keepachangelog/SKILL.md)).

## Branches

- The default branch is `main`. When a remote exists, protect it, and make your changes on feature branches that start from it.
- Squash-merge feature branches into `main`. The squashed message obeys Conventional Commits.
