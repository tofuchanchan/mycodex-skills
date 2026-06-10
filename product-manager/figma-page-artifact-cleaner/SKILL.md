---
name: figma-page-artifact-cleaner
description: Clean local byproducts from figma-page-reproducer and figma-page-reviser workflows. Use when the user asks to clean, remove, delete, audit, list, inspect, or reclaim disk space from Figma page reproduction/revision artifacts, page-full screenshots, pixel reference images, local artifacts folders, Chrome/CDP user-data profiles, DevToolsActivePort profiles, or asks in Chinese about "figma-page-reproducer/reviser 产生的副产物", "临时文件", "缓存", "截图", or "清理". Always scan first, summarize paths and risk, and get explicit confirmation before moving or deleting files.
---

# Figma Page Artifact Cleaner

## Goal

Safely clean local files produced while using `figma-page-reproducer` and `figma-page-reviser` without deleting skill source, repository code, Figma content, or useful review evidence by accident.

This skill cleans local byproducts only. It does not delete Figma frames, Figma files, installed skill directories, source code, or Git history.

## Naming and Scope

This skill is the cleanup companion for:

- `figma-page-reproducer`
- `figma-page-reviser`

Use `figma-page-artifact-cleaner` for Figma page capture/revision cleanup. Do not use it for unrelated browser automation caches or `ost-user-system-guidelines` sampling artifacts unless the user explicitly includes those paths.

## Required Workflow

1. Identify cleanup scope:
   - current workspace or user-provided workspace path
   - explicit artifact paths
   - whether `C:\tmp` Chrome profiles should be included
2. Run a dry-run scan first with `scripts/clean-figma-page-artifacts.ps1`.
3. Classify findings before cleanup:
   - `safe`: page capture screenshots, old pixel references, task-specific artifact files, closed Chrome/CDP profiles
   - `retain`: screenshots still needed for visual comparison, current QA evidence, user-provided source files
   - `skip`: active Chrome profiles, Git repositories, installed skills, source directories, dependencies, unknown directories
4. Report the candidate list and ask for explicit confirmation before moving or deleting anything.
5. Prefer quarantine over permanent deletion:
   - Default cleanup should move candidates to a timestamped quarantine folder.
   - Permanent deletion is allowed only when the user explicitly asks for permanent deletion after seeing the scan result.
6. After cleanup, run the scan again and report:
   - cleaned paths
   - skipped paths and reason
   - retained paths and reason
   - quarantine location, if used

## Cleanup Script

Use the bundled script from this skill directory.

Dry-run scan:

```powershell
powershell -ExecutionPolicy Bypass -File path\to\skill\scripts\clean-figma-page-artifacts.ps1 -Root "C:\path\to\workspace"
```

Include likely temporary Chrome profiles under `C:\tmp`:

```powershell
powershell -ExecutionPolicy Bypass -File path\to\skill\scripts\clean-figma-page-artifacts.ps1 -Root "C:\path\to\workspace" -IncludeTmpProfiles
```

Move approved candidates to quarantine:

```powershell
powershell -ExecutionPolicy Bypass -File path\to\skill\scripts\clean-figma-page-artifacts.ps1 -Root "C:\path\to\workspace" -IncludeTmpProfiles -Apply
```

Clean only explicit paths approved by the user:

```powershell
powershell -ExecutionPolicy Bypass -File path\to\skill\scripts\clean-figma-page-artifacts.ps1 -ExtraPath "C:\path\to\artifact" -Apply
```

Permanent deletion requires explicit user approval:

```powershell
powershell -ExecutionPolicy Bypass -File path\to\skill\scripts\clean-figma-page-artifacts.ps1 -ExtraPath "C:\path\to\artifact" -Apply -Permanent
```

## Candidate Rules

Treat these as likely cleanup candidates:

- `artifacts/page-full.png`
- `artifacts/*page-full*.png`
- `artifacts/*full-page*.png`
- `artifacts/*pixel-reference*.png`
- `artifacts/*figma*screenshot*.png`
- directories named `chrome-cdp-profile`, `chrome-cdp-profile-*`, or `*-chrome-profile` that contain Chrome profile markers such as `Default`, `Local State`, `Last Version`, or `DevToolsActivePort`

Treat these as protected unless the user explicitly names them and confirms:

- `.git`
- `node_modules`
- source folders such as `src`, `app`, `pages`, `components`
- installed skill directories under `.codex\skills` or `.agents\skills`
- Figma skill source directories
- output files the user still needs for review or audit

## Chrome Profile Safety

Chrome profiles can contain cookies, local storage, cached app data, and login state.

- Skip a profile if it appears active, especially if it contains `DevToolsActivePort`, `SingletonLock`, `SingletonCookie`, or `SingletonSocket`.
- Ask the user to close the related Chrome window before cleaning active profiles.
- If the user confirms the profile is stale, clean it only by explicit path.

## Final Response

Use this concise structure:

```text
Scanned:
- <root/path>

Cleaned:
- <path> -> <quarantine/deleted>

Skipped:
- <path>: <reason>

Retained:
- <path>: <reason>

Quarantine:
- <path or "none">
```

If nothing was cleaned, say so directly and explain what confirmation or path is needed next.
