---
name: figma-page-reproducer
description: Reproduce an existing logged-in web page as a static Figma prototype with high visual fidelity and explicit editability/scope choices. Use when the user asks Codex to call Figma to restore, capture, copy, recreate, reproduce, or prototype a real system page, especially pages requiring manual login, effective business-content height detection, full-page or current-viewport capture decisions, long inner-scroll containers, editable module splitting, desktop viewport capture, Figma html-to-design capture, layout-based Figma layer grouping, style-consistent repeated tables/sections, capture-artifact cleanup such as unintended black strokes, watermark exclusion, or icon-safe handling for SVG iconfont, Ant Design icons, inline SVG, remote images, and CSS pseudo-element arrows.
---

# Figma Page Reproducer

## Goal

Create a Figma prototype from the actual rendered web page, not from imagination. Prioritize visual fidelity first, then editability. For logged-in systems, reuse the user's authenticated browser page whenever possible.

## Required Workflow

1. Confirm inputs: target page URL, target Figma file URL/key, scope, viewport, and whether the user will log in manually.
2. Verify the active Figma account with `whoami`. If multiple Figma MCP namespaces are available, use the one whose email matches the user's expected account.
3. Open a visible Chrome page with remote debugging when manual login is required. Let the user log in, then continue from that same authenticated tab.
4. Inspect the live page dimensions, scroll containers, effective business-content bounds, watermark overlays, and icon sources before capture.
   - Run `analyze-effective-bounds` for admin/SaaS pages before choosing frame height.
   - Do not blindly use `documentElement.scrollHeight`, `body.scrollHeight`, or `#app.scrollHeight` as the Figma frame height. These often include side navigation, footers, watermark overlays, and other shell content that should not define a page prototype.
   - If the analysis recommends `current-viewport`, use the requested desktop viewport height, usually `900`, unless the user explicitly wants full shell scroll.
5. If the page or a primary inner container is significantly taller than the viewport, stop and offer the user a scope choice before capture. Do not hard-code a full-page or first-screen strategy for long list/detail pages.
   - If editability is required, do not use a full-page screenshot as the fallback. Split the page into editable modules and rebuild failed modules with Figma primitives/components.
6. Preprocess icons before Figma capture:
   - Resolve `<svg><use href="#icon-...">` into real `symbol/path` content.
   - Rasterize visible inline SVG and iconfont symbols to PNG data URLs in the browser.
   - Convert Ant Design menu arrows or pseudo-element arrows to real PNG image nodes.
   - Verify `blankAfterRasterize = 0` or explain any intentional white-on-color icons.
7. Hide unrelated transient overlays that were not part of the requested state, such as tutorials, chat popups, cookie banners, onboarding tips, theme/config drawers, and dev-only panels.
8. Hide product watermarks before screenshot/capture. Admin systems often display username watermarks for security; they are real in the page but usually noise in a prototype unless the user explicitly asks to preserve them.
9. Capture a local screenshot for the chosen scope as the pixel reference and visually inspect it before sending anything to Figma.
10. Use Figma `generate_figma_design` with `outputMode: "existingFile"` for normal-size editable capture. Inject the Figma capture script into the already-authenticated page through CDP so auth state is preserved. For very long pages that require editability, skip whole-page capture and use the editable long-page strategy instead.
11. Poll the capture ID until Figma returns a completed node URL. Do not abandon polling just because the submit command times out; large pages often submit successfully after a terminal timeout.
12. Rename the generated frame clearly, for example `Editable capture - <page name> - icons fixed PNG`.
13. Load `references/layer-organization.md` and run a semantic layer organization pass. Group captured nodes by page layout region and component purpose instead of leaving all generated rectangles/text/images flat at the frame root.
14. Load `references/style-artifact-qa.md` and run a capture cleanup pass for repeated-module style consistency, semantic color scope, parent-relative coordinates, and unintended dark strokes.
15. Add or keep a pixel reference screenshot frame when useful, especially for review or fidelity comparison.
16. Validate the Figma result with `get_screenshot` and metadata. Check icon presence, viewport size, effective height, missing images, accidental overlays/watermarks, obvious layout drift, similar section consistency, accidental dark borders, and layer tree organization.
17. Clean up local capture artifacts after validation so one-off browser profiles, helper scripts, logs, and process screenshots do not linger in the repo.

## Tooling Pattern

Use the bundled helper script when driving an authenticated Chrome tab via the Chrome DevTools Protocol:

```powershell
node path\to\skill\scripts\cdp-page-tools.mjs eval --target-host example.com --expr "({url: location.href, title: document.title})"
node path\to\skill\scripts\cdp-page-tools.mjs analyze-effective-bounds --target-host example.com --viewport-height 900
node path\to\skill\scripts\cdp-page-tools.mjs hide-watermarks --target-host example.com
node path\to\skill\scripts\cdp-page-tools.mjs preprocess-icons-png --target-host example.com
node path\to\skill\scripts\cdp-page-tools.mjs hide-text --target-host example.com --text "申报操作教程" --text "观看教程" --min-x 900 --min-y 650
node path\to\skill\scripts\cdp-page-tools.mjs screenshot --target-host example.com --out artifacts/page-full.png --viewport-width 1440 --viewport-height 900
node path\to\skill\scripts\cdp-page-tools.mjs submit-figma-capture --target-host example.com --capture-id <id> --endpoint <endpoint>
```

Use `--cdp-port` if Chrome was launched on a non-default port. If a helper needs adjustment for a specific app, patch the script rather than rewriting fragile CDP code in chat.

## Effective Viewport Height

For admin and SaaS pages, distinguish **shell height** from **business-content height**. Sidebars, footers, watermarks, drawers, and hidden menus can make `#app.scrollHeight` much larger than the visible business page. A Figma prototype should normally use the effective business viewport, not the shell's full scroll height.

Run:

```powershell
node path\to\skill\scripts\cdp-page-tools.mjs analyze-effective-bounds --target-host example.com --viewport-height 900
```

Use the returned data this way:

- `meaningfulBottom`: bottom edge of visible, non-ignored business content.
- `recommendedFrameHeight`: frame height after adding a small buffer; if it is `900` or near the requested viewport, use a `1440 x 900` style frame.
- `ignoredBottomElements`: explains what would have inflated height, such as side navigation, footer, drawers, or watermark containers.
- `scrollCandidates`: identifies real document or inner scroll containers. If the primary business container is over `4x` viewport height or over `6000px`, ask for scope and consider segmented/module reconstruction.

If the table/form/card content ends near the viewport bottom but a sidebar or footer continues far below, create a current-viewport prototype and mention that the full shell scroll was intentionally ignored. Do not create a tall blank frame just because `#app.scrollHeight` is tall.

## Watermark Handling

Backend systems often add security watermarks such as repeated usernames. Treat these as capture noise by default.

Before screenshots and Figma capture, run:

```powershell
node path\to\skill\scripts\cdp-page-tools.mjs hide-watermarks --target-host example.com
```

Then verify screenshots and Figma output contain no repeated watermark nodes/text. Preserve account names in the actual header/avatar area; only remove repeated low-emphasis page watermarks or watermark containers. If the user explicitly asks to keep watermarks for compliance review, keep them and label the decision in the final response.

## Long Page Scope Choices

For pages with long document scroll or large inner scroll containers, ask the user how to handle the capture before submitting anything to Figma. Explain the tradeoff briefly and wait for a choice.

- **Current viewport / first screen**: best for quick page-state prototypes and header/filter/list-top review. Captures exactly what the user sees now.
- **Selected section only**: best when the user cares about a specific modal, filter panel, table, card group, or business area.
- **Segmented frames**: best for long product lists, dashboards, and inner-scroll containers. Capture consecutive viewport chunks as separate labeled frames, for example `Buy page - segment 01`, `segment 02`.
- **Full long frame**: only use when the page is reasonably sized and the user explicitly wants a single tall frame. Warn that very tall pages can be slow, heavy, and less editable in Figma.
- **Representative sample**: best for repetitive lists. Capture filters/header plus the first N rows/cards and one or two representative variants instead of thousands of repeated items.
- **Editable module split**: required when the user says Figma editability cannot be compromised. Detect repeated sections/cards from DOM, create separate labeled frames per module, and draw text, cards, buttons, tabs, filters, and layout with editable Figma nodes.

When an inner scroll container is the primary content surface, report its selector or identifying class/id, viewport height, and scroll height. Do not assume `document.documentElement.scrollHeight` tells the whole story.

## Editable Long-Page Strategy

For very long pages, especially catalog/list pages with repeated cards, do not submit the whole page to `generate_figma_design`.

1. Detect the module boundaries from DOM selectors, layout roles, repeated class names, or visible headings.
2. Extract a compact data model: navigation shell, filter rows, section headings, item counts, representative card text/prices/tags/states, and key button labels.
3. Generate a Figma board with separate editable frames:
   - first viewport shell;
   - reusable filter/header module;
   - one frame per repeated business section;
   - card state/component anatomy when useful.
4. Keep repeated lists sampled. Do not create hundreds or thousands of identical cards unless the user explicitly asks for full coverage.
5. If `generate_figma_design` succeeds for a small module, it may be used as a layout reference. If it times out or creates a bitmap-heavy/raw capture, replace it with structured Figma nodes.
6. When a module cannot be auto-captured, fall back to structured reconstruction with Figma primitives, text nodes, and reusable components. Do not fall back to a full-frame screenshot unless the user explicitly asks for a pixel reference.

For editable-delivery tasks, screenshots are allowed only as a temporary local reference or as a separately labeled `Pixel reference`. They are not an acceptable replacement for the editable deliverable.

Use this strategy by default when any of these are true:

- the primary scroll surface is an inner container over `4x` the viewport height or over `6000px`;
- the page contains hundreds of repeated list/card/table items;
- the user says editability cannot be compromised;
- `generate_figma_design` for the whole page is still pending/processing after one reasonable submit/poll cycle.

Do not wait on a stuck whole-page capture while the user is expecting progress. Continue with module extraction and structured Figma generation. Keep polling or clean up the old capture separately so a late result does not pollute the final canvas.

## Module Extraction Pattern

When splitting a long page, extract data from the authenticated DOM before drawing in Figma.

Suggested compact model:

```json
{
  "meta": {
    "url": "...",
    "innerScroller": "#contentBoxer",
    "scrollHeight": 50603,
    "sectionCount": 32,
    "totalCards": 1172
  },
  "nav": { "side": ["..."], "top": ["..."] },
  "filters": { "types": ["..."], "countries": ["..."] },
  "sections": [
    {
      "title": "英国",
      "cardCount": 32,
      "cards": [
        {
          "name": "商品名",
          "price": "￥900/年起",
          "oldPrice": "￥1280/年起",
          "tag": "买送",
          "disabled": false,
          "consult": false
        }
      ]
    }
  ]
}
```

Draw the compact model as editable Figma nodes:

- one first-viewport shell frame;
- one reusable filter/header frame;
- one labeled frame per repeated business section;
- representative item/card frames with text, buttons, badges, disabled state, consultation state, and promo state;
- optional component anatomy frame showing card states.

For list/card pages, sample the first major section more heavily, then sample each additional section lightly unless the user asks for full coverage. Always report the sampling policy in the final response.

## Figma API Implementation Notes

`use_figma` runs inside a constrained plugin sandbox. Avoid assuming browser or Node APIs exist.

- Always load and pass the `figma-use` skill before `use_figma`.
- `fetch` may be unavailable. Do not depend on a local HTTP server from inside `use_figma`.
- If data is too large to inline in one script, store compact JSON in `setSharedPluginData(namespace, key, value)` first, then read it in a second `use_figma` call.
- Use valid Figma enum values, for example `CENTER`, `LEFT`, `RIGHT`; CSS-style lowercase values like `center` fail validation.
- Load fonts before creating/editing text. Prefer available CJK-capable fonts such as `Noto Sans SC` when the original web font is not available.
- If the Figma URL node id points to a text node or leaf node, inspect the parent chain and create the new prototype as a sibling/top-level board near the intended area. Do not append a full screen into a text node.
- Return all created and removed node IDs from each write call.

## Capture Queue Hygiene

Figma capture jobs can complete late. Treat old capture IDs as possible delayed side effects.

- If a whole-page or screenshot/reference capture was started and the final deliverable switches to editable module reconstruction, continue checking that capture ID briefly.
- If a delayed raw capture creates a node and it is not part of the accepted deliverable, delete it immediately.
- Keep the final canvas free of stale bitmap/reference captures unless the user explicitly wants a pixel reference.
- Mention any still-processing capture ID only as residual risk when it has not produced a node by final cleanup time.

## Figma Capture Rules

- For external authenticated sites, do not open a fresh unauthenticated URL for capture. Inject the capture script into the live logged-in tab.
- Prefer `generate_figma_design` for the initial editable conversion, but treat it as a raw-frame capture, not a design-system-quality final component library.
- Always use `figma-use` before `use_figma` calls.
- `generate_figma_design` captures raw frames. If the user wants reusable production-quality prototypes later, replace repeated controls with design-system components after the raw capture is accepted.
- Rename captured nodes immediately. Default names like `uat`, `Body`, and `Container` are useless.
- Do not use bitmap screenshots as a fallback when the requested deliverable must be editable. Use screenshots only as explicit pixel references.
- Do not leave a generated page as a flat pile of sibling nodes. After capture, create layout-based groups or frames with clear names such as `01 App Shell`, `02 Header`, `03 Navigation Tabs`, `04 Filter Panel`, `05 Action Toolbar`, `06 Data Table`, `07 Pagination`, and `90 Reference`.
- Do not normalize every divider into a full `1px` box border. Preserve the source page's actual divider model, including one-sided strokes and thinner table grid lines.
- Treat unexpected `#000000` strokes on large app-shell containers, top headers, sidebars, and table wrappers as capture artifacts unless the pixel reference clearly shows black dividers.
- When reconstructing editable repeated sections, derive their style contract from an existing sibling section or row. Do not rebuild a matching table with a different border model, text padding, or header typography.

## Layer Organization

Read `references/layer-organization.md` before modifying the captured Figma node after `generate_figma_design` completes. The organization pass is required for editable reproductions unless the user explicitly asks for a raw capture only.

At minimum:

- Preserve the top-level frame dimensions and visual coordinates.
- Group by semantic page regions, not by node type. A filter field's label, box, placeholder, suffix icon, and dropdown arrow belong together; they should not live as unrelated siblings beside table cells.
- Keep repeated structures readable without over-nesting. For large tables, group at table/header/body/row level when useful, but do not create thousands of microscopic cell groups unless the user needs cell-level editability.
- Report the layer organization strategy in the final answer.

## Style and Artifact Cleanup

Read `references/style-artifact-qa.md` after capture and before final validation. Use it when the generated frame contains repeated tables, detail sections, card lists, app-shell containers, or dark divider artifacts.

At minimum:

- Pick source analogues for repeated modules and compare row heights, cell widths, typography, fills, divider color, and individual side stroke weights.
- Confirm text and icons use coordinates relative to their actual parent groups after regrouping.
- Verify semantic emphasis colors only appear on the intended labels, values, rows, or badges.
- Remove or replace unintended black strokes on sidebar/header/table boundaries while preserving real black text and icons.

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
- Frame height follows the selected scope. For admin list/form pages, report the effective business-content height decision instead of claiming it matches `scrollHeight`.
- If the page uses an inner scroll container, validation uses that container's `scrollHeight` and the `analyze-effective-bounds` result, not only `document.documentElement.scrollHeight`.
- For module-split deliverables, the final frame reports section count, item/card sample count, and confirms whether bitmap image fills were avoided.
- A pixel reference screenshot exists or the editable capture has been visually inspected.
- Main icons are visible in the Figma screenshot, not empty image boxes.
- Repeated page watermarks are absent unless explicitly requested.
- No accidental tutorial/chat/cookie overlay is present unless requested.
- Top-level editable frame contains semantic layout groups, not only dozens or hundreds of flat primitive siblings.
- Important repeated regions have useful names and hierarchy: navigation, header, tabs, filters, toolbars, table/list, modal/drawer, and reference screenshot.
- Similar repeated sections and tables share the same style contract unless the pixel reference shows a deliberate difference.
- Shell containers and table wrappers do not have unexplained dark borders or black capture artifacts.
- Final answer links directly to the new Figma node and names the frame.

## Common Failure Modes

- **Figma account mismatch**: call all available `whoami` tools; use the namespace with the correct email.
- **Submit command timeout**: poll the capture ID anyway.
- **Late capture pollution**: a previously started capture may finish after the structured result is done. Delete stale nodes that are not part of the accepted deliverable.
- **Unbounded long-page capture**: do not send huge inner-scroll pages as one capture. Switch to editable module split.
- **`use_figma` sandbox API mismatch**: browser APIs such as `fetch` may not exist; use inline compact data or shared plugin data.
- **Figma enum validation errors**: normalize enum values to Figma's expected uppercase values.
- **Target node is not a container**: inspect parent chain and place the generated board as a sibling/top-level frame instead of nesting into text/vector nodes.
- **Blank icon images**: rasterize resolved symbols to PNG, not SVG data URLs.
- **Blank lower half**: shell scroll height was probably used as prototype height. Re-run `analyze-effective-bounds`, ignore sidebars/footer/watermarks/drawers, and rebuild or resize to the effective viewport.
- **Watermark pollution**: run `hide-watermarks` before capture and remove any generated `watermark / <user>` nodes from structured Figma output.
- **Page state changed after refresh**: restore the requested UI state before capture.
- **Floating overlay appeared**: hide it and recapture.
- **Text mojibake in CDP JSON**: visual screenshot is authoritative; do not infer page quality from garbled console output.
- **Generated black borders**: inspect large `Container` frames and table wrappers for `#000000` strokes; replace with the local divider color on the intended side or remove the stroke.
- **Repeated section drift**: compare the generated section against its sibling source block; repair mismatched row height, padding, individual stroke weights, font style, and parent-relative text coordinates.
