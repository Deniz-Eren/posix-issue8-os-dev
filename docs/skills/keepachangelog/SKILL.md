---
name: keepachangelog
description: Keep CHANGELOG.md in the Keep a Changelog format. Use it when you record a change, when you make a release, or when the user wants an update.
license: MIT
---

# Keep a Changelog

The file `CHANGELOG.md` at the project root records the important changes of the project for its users. The format follows [Keep a Changelog](https://keepachangelog.com).

## Structure

- The file starts with the sections `## Purpose`, `## Structure`, and `## Formatting Rules`. The release sections come below them.
- One section for each version: `## [VERSION] - YYYY-MM-DD`. The newest version is first.
- An `## [Unreleased]` section at the top. It contains the changes with no release.
- Category headings of level 3 in each section: `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, and `### Security`. Put a heading into the file only when the section has content for it.
- The entries in each category are newest first (git log order).

## Procedure

1. Put each important change into `## [Unreleased]`, at the top of the correct category. One item for each change. Write for the users of the project, not for git.
2. When you make a release, change the heading `## [Unreleased]` to `## [VERSION] - YYYY-MM-DD`. VERSION is the new version of the project. Then start a new empty `## [Unreleased]` section above it.
3. The version numbers follow [Semantic Versioning](https://semver.org). When the project has a build configuration, the version there is the same as the version in the new heading.
4. Do not copy the git commit log into the file. One item can group many commits.

## Attribution

This skill gives the format of keepachangelog.com with its own words. When you copy this skill into a target project, add this entry to Section 1 of `docs/THIRD-PARTY-NOTICES.md` of the target:

```markdown
### keepachangelog.com
* **Component(s) Used:** [skills/keepachangelog/SKILL.md](skills/keepachangelog/SKILL.md)
* **Source:** [keepachangelog.com](https://keepachangelog.com)
* **Note:** The skill describes the Keep a Changelog format with its own words. No text is copied from the source.
```
