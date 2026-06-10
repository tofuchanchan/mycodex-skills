# mycodex-skills

Personal Codex skills grouped by use case.

## Categories

### Product Manager Skills

Skills for product, UI, Figma, OST system design, and DingTalk document workflows.

| Skill | Description | Install URL |
| --- | --- | --- |
| `figma-page-reproducer` | Reproduce logged-in web pages in Figma with high visual fidelity, semantic layers, and OST page-standard routing. | https://github.com/tofuchanchan/mycodex-skills/tree/main/product-manager/figma-page-reproducer |
| `figma-page-reviser` | Revise reproduced Figma pages with scoped edits, style consistency checks, text-fit QA, and artifact cleanup. | https://github.com/tofuchanchan/mycodex-skills/tree/main/product-manager/figma-page-reviser |
| `figma-page-artifact-cleaner` | Safely clean screenshots, artifact files, and temporary Chrome/CDP profiles from Figma page workflows. | https://github.com/tofuchanchan/mycodex-skills/tree/main/product-manager/figma-page-artifact-cleaner |
| `dingtalk-doc-mcp-guidelines` | Use DingTalk Doc MCP safely for Alidocs read/write operations with JsonML structure and post-write verification. | https://github.com/tofuchanchan/mycodex-skills/tree/main/product-manager/dingtalk-doc-mcp-guidelines |
| `ost-admin-system-guidelines` | OST admin/internal system design guidelines for operations, finance, support, VAT, orders, and system pages. | https://github.com/tofuchanchan/mycodex-skills/tree/main/product-manager/ost-admin-system-guidelines |
| `ost-user-system-guidelines` | OST merchant/user system design guidelines for workbench, purchase, orders, VAT, declarations, login, and 404 pages. | https://github.com/tofuchanchan/mycodex-skills/tree/main/product-manager/ost-user-system-guidelines |

### VAT Tools

Skills for VAT XML parsing, audit, reconciliation, and tax-risk diagnostics.

| Skill | Description | Install URL |
| --- | --- | --- |
| `poland-vat-xml-auditor` | Audit Polish JPK_V7M and VAT-UE XML files, extract B2B/transfer transactions, reconcile the files, and flag risks. | https://github.com/tofuchanchan/mycodex-skills/tree/main/vat-tools/poland-vat-xml-auditor |

## Install

Ask Codex to install a skill from its GitHub URL:

```text
Install this skill:
https://github.com/tofuchanchan/mycodex-skills/tree/main/vat-tools/poland-vat-xml-auditor
```

Or use the bundled skill installer:

```powershell
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --url https://github.com/tofuchanchan/mycodex-skills/tree/main/vat-tools/poland-vat-xml-auditor
```

Install by repository and path:

```powershell
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo tofuchanchan/mycodex-skills --path vat-tools/poland-vat-xml-auditor
```

For another skill, replace `--path` with its category path, such as:

```powershell
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo tofuchanchan/mycodex-skills --path product-manager/ost-user-system-guidelines
```

Restart Codex after installing or updating a skill.

## Repository Layout

```text
mycodex-skills/
  product-manager/
    figma-page-reproducer/
      SKILL.md
      agents/
      references/
      scripts/
    figma-page-reviser/
      SKILL.md
      agents/
      references/
    figma-page-artifact-cleaner/
      SKILL.md
      agents/
      scripts/
    dingtalk-doc-mcp-guidelines/
      SKILL.md
      agents/
    ost-admin-system-guidelines/
      SKILL.md
      agents/
      references/
    ost-user-system-guidelines/
      SKILL.md
      evals/
      references/
  vat-tools/
    poland-vat-xml-auditor/
      SKILL.md
      agents/
      evals/
      references/
      scripts/
```

A valid skill directory must include `SKILL.md`. Optional helper files belong under `agents/`, `references/`, `scripts/`, `evals/`, or `assets/`.

## Updating A Skill

1. Edit the skill directory locally.
2. Keep generated artifacts, screenshots, logs, audit outputs, and temporary browser profiles out of the repository.
3. Push the updated skill directory to this repository.
4. Ask users to reinstall the skill or update their local copy, then restart Codex.
