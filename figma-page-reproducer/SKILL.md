---
name: figma-page-reproducer
description: Reproduce an existing logged-in web page as a static Figma prototype with high visual fidelity. Use when the user asks Codex to call Figma to restore, capture, copy, recreate, reproduce, or prototype a real system page, especially pages requiring manual login, full-page scrolling, desktop viewport capture, Figma html-to-design capture, or icon-safe handling for SVG iconfont, Ant Design icons, inline SVG, remote images, and CSS pseudo-element arrows.
---

# Figma Page Reproducer

## Goal

Create a Figma prototype from the actual rendered web page, not from imagination. Prioritize visual fidelity first, then editability. For logged-in systems, reuse the user's authenticated browser page whenever possible.

## Required Workflow

1. Confirm inputs: target page URL, target Figma file URL/key, scope, viewport, and whether the user will log in manually.
2. Verify the active Figma account with `whoami`. If multiple Figma MCP namespaces are available, use the one whose email matches the user's expected account.
3. Open a visible Chrome page with remote debugging when manual login is required. Let the user log in, then continue from that same authenticated tab.
4. Inspect the live page dimensions, scroll containers, and icon sources before capture.
5. If the page or a primary inner container is significantly taller than the viewport, stop and offer the user a scope choice before capture. Do not hard-code a full-page or first-screen strategy for long list/detail pages.
6. Preprocess icons before Figma capture:
   - Resolve `<svg><use href="#icon-...">` into real `symbol/path` content.
   - Rasterize visible inline SVG and iconfont symbols to PNG data URLs in the browser.
   - Convert Ant Design menu arrows or pseudo-element arrows to real PNG image nodes.
   - Verify `blankAfterRasterize = 0` or explain any intentional white-on-color icons.
7. Hide unrelated transient overlays that were not part of the requested state, such as tutorials, chat popups, cookie banners, or onboarding tips.
8. Capture a local screenshot for the chosen scope as the pixel reference and visually inspect it before sending anything to Figma.
9. Use Figma `generate_figma_design` with `outputMode: "existingFile"` for the editable capture. Inject the Figma capture script into the already-authenticated page through CDP so auth state is preserved.
10. Poll the capture ID until Figma returns a completed node URL. Do not abandon polling just because the submit command times out; large pages often submit successfully after a terminal timeout.
11. Rename the generated frame clearly, for example `Editable capture - <page name> - icons fixed PNG`.
12. Add or keep a pixel reference screenshot frame when useful, especially for review or fidelity comparison.
13. Validate the Figma result with `get_screenshot` and metadata. Check icon presence, viewport size, scroll height, missing images, accidental overlays, and obvious layout drift.
14. Clean up local capture artifacts after validation so one-off browser profiles, helper scripts, logs, and process screenshots do not linger in the repo.

## Tooling Pattern

Use the bundled helper script when driving an authenticated Chrome tab via the Chrome DevTools Protocol:

```powershell
node path\to\skill\scripts\cdp-page-tools.mjs eval --target-host example.com --expr "({url: location.href, title: document.title})"
node path\to\skill\scripts\cdp-page-tools.mjs preprocess-icons-png --target-host example.com
node path\to\skill\scripts\cdp-page-tools.mjs hide-text --target-host example.com --text "申报操作教程" --text "观看教程" --min-x 900 --min-y 650
node path\to\skill\scripts\cdp-page-tools.mjs screenshot --target-host example.com --out artifacts/page-full.png --viewport-width 1440 --viewport-height 900
node path\to\skill\scripts\cdp-page-tools.mjs submit-figma-capture --target-host example.com --capture-id <id> --endpoint <endpoint>
```

Use `--cdp-port` if Chrome was launched on a non-default port. If a helper needs adjustment for a specific app, patch the script rather than rewriting fragile CDP code in chat.

## Long Page Scope Choices

For pages with long document scroll or large inner scroll containers, ask the user how to handle the capture before submitting anything to Figma. Explain the tradeoff briefly and wait for a choice.

- **Current viewport / first screen**: best for quick page-state prototypes and header/filter/list-top review. Captures exactly what the user sees now.
- **Selected section only**: best when the user cares about a specific modal, filter panel, table, card group, or business area.
- **Segmented frames**: best for long product lists, dashboards, and inner-scroll containers. Capture consecutive viewport chunks as separate labeled frames, for example `Buy page - segment 01`, `segment 02`.
- **Full long frame**: only use when the page is reasonably sized and the user explicitly wants a single tall frame. Warn that very tall pages can be slow, heavy, and less editable in Figma.
- **Representative sample**: best for repetitive lists. Capture filters/header plus the first N rows/cards and one or two representative variants instead of thousands of repeated items.

When an inner scroll container is the primary content surface, report its selector or identifying class/id, viewport height, and scroll height. Do not assume `document.documentElement.scrollHeight` tells the whole story.

## Figma Capture Rules

- For external authenticated sites, do not open a fresh unauthenticated URL for capture. Inject the capture script into the live logged-in tab.
- Prefer `generate_figma_design` for the initial editable conversion, but treat it as a raw-frame capture, not a design-system-quality final component library.
- Always use `figma-use` before `use_figma` calls.
- `generate_figma_design` captures raw frames. If the user wants reusable production-quality prototypes later, replace repeated controls with design-system components after the raw capture is accepted.
- Rename captured nodes immediately. Default names like `uat`, `Body`, and `Container` are useless.

## Local Artifact Cleanup

Treat local artifacts as disposable by default once the Figma result has been validated and linked in the final response.

- Delete temporary Chrome/CDP user-data directories created for capture, such as `artifacts/*/chrome-cdp-profile`, after closing any browser process that still uses them.
- Delete one-off helper scripts, capture submit scripts, server logs, temporary HTML files, and intermediate screenshots created only to drive or debug the capture.
- Keep a local pixel reference screenshot only when it is needed for user review, fidelity comparison, or a follow-up task. If the user asks for cleanup, delete it too.
- Before any recursive deletion, resolve the absolute target path and verify it sits inside the intended workspace artifact directory. Never delete a computed path that fails this check.
- If Windows reports that a Chrome profile file is in use, identify and stop only the Chrome processes whose command line references that exact temporary profile, then retry deletion.
- Mention any artifact intentionally kept in the final response, with a short reason. If nothing is kept, say the local capture artifacts were cleaned up.

## Icon Handling

Most missing-icon failures are caused by SVG `<use>` references. Capturing only the visible `<svg>` element often loses the referenced `<symbol>`, so Figma receives an empty image. The reliable fix is:

1. Read the referenced `symbol` by ID.
2. Build a standalone SVG with actual child paths.
3. Apply computed color/fill/stroke.
4. Rasterize it in browser canvas.
5. Replace the original icon with a PNG `<img>`.

Do this before Figma capture. Do not settle for `data:image/svg+xml` if Figma renders blank image fills. PNG is less editable but much more reliable.

Read `references/icon-capture-notes.md` when icon capture fails or the page uses iconfont, SVG sprites, Ant Design icons, or pseudo-element arrows.

## Verification Checklist

Before final response, confirm:

- Figma account is the expected account.
- Captured frame has the requested viewport width, usually `1440`.
- Full page height matches `document.documentElement.scrollHeight`; if more than one screen, capture full scroll height.
- A pixel reference screenshot exists or the editable capture has been visually inspected.
- Main icons are visible in the Figma screenshot, not empty image boxes.
- No accidental tutorial/chat/cookie overlay is present unless requested.
- Final answer links directly to the new Figma node and names the frame.

## Common Failure Modes

- **Figma account mismatch**: call all available `whoami` tools; use the namespace with the correct email.
- **Submit command timeout**: poll the capture ID anyway.
- **Blank icon images**: rasterize resolved symbols to PNG, not SVG data URLs.
- **Page state changed after refresh**: restore the requested UI state before capture.
- **Floating overlay appeared**: hide it and recapture.
- **Text mojibake in CDP JSON**: visual screenshot is authoritative; do not infer page quality from garbled console output.
