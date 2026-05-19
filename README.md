# mycodex-skills

A personal collection of Codex skills for AI-assisted workflows.

## Skills

| Skill | Description | Install URL |
| --- | --- | --- |
| `figma-page-reproducer` | Reproduce logged-in web pages in Figma with high visual fidelity, including full-page capture and icon-safe preprocessing. | https://github.com/tofuchanchan/mycodex-skills/tree/main/figma-page-reproducer |
| `figma-page-reviser` | Revise reproduced Figma pages with scoped edits, semantic layer grouping, style consistency checks, text-fit QA, and capture-artifact cleanup. | https://github.com/tofuchanchan/mycodex-skills/tree/main/figma-page-reviser |

## Install

The easiest way is to ask Codex to install a skill from its GitHub URL:

```text
Install this skill:
https://github.com/tofuchanchan/mycodex-skills/tree/main/figma-page-reproducer
```

Or install the reviser skill:

```text
Install this skill:
https://github.com/tofuchanchan/mycodex-skills/tree/main/figma-page-reviser
```

Then restart Codex so the new skill is loaded.

You can also install it manually with the bundled skill installer:

```powershell
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --url https://github.com/tofuchanchan/mycodex-skills/tree/main/figma-page-reproducer
```

Or install by repository and path:

```powershell
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo tofuchanchan/mycodex-skills --path figma-page-reproducer
```

For the reviser:

```powershell
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo tofuchanchan/mycodex-skills --path figma-page-reviser
```

## Repository Layout

Each skill should live in its own top-level directory:

```text
mycodex-skills/
  figma-page-reproducer/
    SKILL.md
    agents/
    references/
    scripts/
  figma-page-reviser/
    SKILL.md
    agents/
    references/
```

A valid skill directory should include at least `SKILL.md`. Extra helper files can live under directories such as `agents/`, `references/`, `scripts/`, or `assets/` when the skill needs them.

## Updating A Skill

1. Edit the skill directory locally.
2. Keep generated artifacts, screenshots, logs, and temporary browser profiles out of the repository.
3. Push the updated skill directory to this repository.
4. Ask users to reinstall the skill or update their local copy, then restart Codex.

## Notes

- This repository is intended for Codex skills, not general project code.
- Prefer one focused skill per directory.
- Keep install links pointing to the skill directory, not just the repository root.
