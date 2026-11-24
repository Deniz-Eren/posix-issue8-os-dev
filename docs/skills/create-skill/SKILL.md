---
name: create-skill
description: Make a new agent skill in this project. Obey the Agent Skills specification. Use this skill when you add a new tool, a new workflow, or a new task to docs/skills/.
---

# Make a Skill

## Before you start

1. Look at `docs/skills/`. Make sure that no existing skill has the same task.
2. If the new skill shares more than 30 percent of its instructions with an existing skill, extend that skill.

## Steps

1. **Name the skill:** 1 to 64 characters. Use lowercase letters, digits, and single hyphens. Do not put a hyphen at the start or the end. The directory name must be the same as the name.
2. **Write the description:** 1 to 1024 characters. It tells what the skill does **and** when to use it, because agents read the description to know when to load the skill.
3. **Make `docs/skills/<name>/SKILL.md`:**

   ```markdown
   ---
   name: <name>
   description: <what it does>. Use when <trigger>.
   ---

   # <Title>

   <Short instructions, written for an agent. Keep the body under 500 lines.>
   ```

4. **Add other files if they are necessary:** `scripts/` (executables), `references/` (documents with more information, loaded when necessary), and `assets/` (templates). Link to them with paths from the skill directory. Keep the references one level deep.
5. **Validate:** the name is the same as the directory name, the frontmatter is correct YAML, and the description obeys the length limit. If `skills-ref` is installed, run `skills-ref validate docs/skills/<name>`.
6. **Add the skill to the project:** add the skill to `docs/ARCHITECTURE.md` and to the skill index in `README.md`. Add an entry to `CHANGELOG.md` in `## [Unreleased]`. Then commit (see the [git skill](../git/SKILL.md)).

## Note about the root skill

This repository is itself an installable agent skill. The root `SKILL.md` is the product. Do not mix it with the governance skills in `docs/skills/`. The root skill follows the same Agent Skills specification, with the extra limits from `docs/init-prompt.md` (under 400 lines, no em-dashes, no links to `docs/`).

## Reference

- Specification: [references/SKILLS.mdx](references/SKILLS.mdx)
