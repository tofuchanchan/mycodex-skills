---
name: figma-page-reproducer
description: Reproduce an existing logged-in web page as a static Figma prototype with high visual fidelity and semantic layer organization. Use when the user asks Codex to call Figma to restore, capture, copy, recreate, reproduce, or prototype a real system page, especially pages requiring manual login, OST admin-vs-user page-type detection, full-page scrolling, desktop viewport capture, Figma html-to-design capture, layout-based Figma layer grouping, style-consistent repeated tables/sections, capture-artifact cleanup such as unintended black strokes, or icon-safe handling for SVG iconfont, Ant Design icons, inline SVG, remote images, and CSS pseudo-element arrows. Use `ost-admin-system-guidelines` for OST后台/admin pages and `ost-user-system-guidelines` for OST商户端/user pages.
---

# Figma Page Reproducer

## Goal

Create a Figma prototype from the actual rendered web page, not from imagination. Prioritize visual fidelity first, then editability and layer hygiene. For logged-in systems, reuse the user's authenticated browser page whenever possible.

## Required Workflow

1. Confirm inputs: target page URL, target Figma file URL/key, scope, viewport, and whether the user will log in manually.
2. Verify the active Figma account with `whoami`. If multiple Figma MCP namespaces are available, use the one whose email matches the user's expected account.
3. Open a visible Chrome page with remote debugging when manual login is required. Let the user log in, then continue from that same authenticated tab.
4. Load `references/page-type-standards.md` and identify page type before applying design standards:
   - For OST internal admin/operations/backend pages, use `ost-admin-system-guidelines` as the review and reconstruction standard.
   - For OST merchant-facing/user/customer pages, use `ost-user-system-guidelines` as the review and reconstruction standard.
   - Treat URL/domain and app shell as stronger evidence than table density. For example, `uat-user.evatmaster.com` is merchant/user even when it contains dense VAT tables.
   - If page type is unclear, ask the user to confirm the standard before restyling, reconstructing, or judging style compliance.
5. Inspect the live page dimensions and icon sources before capture.
   - Also identify major layout regions before capture: app shell, sidebar, top header, tab bars, content panels, filters, toolbars, tables/lists, cards, forms, modals/drawers, overlays, and reference screenshots.
6. Preprocess icons before Figma capture:
   - Resolve `<svg><use href="#icon-...">` into real `symbol/path` content.
   - Rasterize visible inline SVG and iconfont symbols to PNG data URLs in the browser.
   - Convert Ant Design menu arrows or pseudo-element arrows to real PNG image nodes.
   - Verify `blankAfterRasterize = 0` or explain any intentional white-on-color icons.
7. Hide unrelated transient overlays that were not part of the requested state, such as tutorials, chat popups, cookie banners, or onboarding tips.
8. Capture a local full-page screenshot as the pixel reference and visually inspect it before sending anything to Figma.
9. Use Figma `generate_figma_design` with `outputMode: "existingFile"` for the editable capture. Inject the Figma capture script into the already-authenticated page through CDP so auth state is preserved.
10. Poll the capture ID until Figma returns a completed node URL. Do not abandon polling just because the submit command times out; large pages often submit successfully after a terminal timeout.
11. Rename the generated frame clearly, for example `Editable capture - <page name> - icons fixed PNG`.
12. Load `references/layer-organization.md` and run a semantic layer organization pass. Group captured nodes by page layout region and component purpose instead of leaving all generated rectangles/text/images flat at the frame root.
13. Load `references/style-artifact-qa.md` and run a capture cleanup pass for repeated-module style consistency, semantic color scope, parent-relative coordinates, and unintended dark strokes.
14. Add or keep a pixel reference screenshot frame when useful, especially for review or fidelity comparison; keep it outside the editable app frame or under a clearly named reference group.
15. Validate the Figma result with `get_screenshot` and metadata. Check icon presence, viewport size, scroll height, missing images, accidental overlays, obvious layout drift, page-type standard compliance, similar section consistency, accidental dark borders, and layer tree organization.

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

## Figma Capture Rules

- For external authenticated sites, do not open a fresh unauthenticated URL for capture. Inject the capture script into the live logged-in tab.
- Decide the page type before applying design standards. OST admin pages should use `ost-admin-system-guidelines`; OST user/merchant pages should use `ost-user-system-guidelines`. If the exact guideline skill is unavailable, preserve the captured page's current visual system and record the fallback.
- Prefer `generate_figma_design` for the initial editable conversion, but treat it as a raw-frame capture, not a design-system-quality final component library.
- Always use `figma-use` before `use_figma` calls.
- `generate_figma_design` captures raw frames. If the user wants reusable production-quality prototypes later, replace repeated controls with design-system components after the raw capture is accepted.
- Rename captured nodes immediately. Default names like `uat`, `Body`, and `Container` are useless.
- Do not leave a generated page as a flat pile of sibling nodes. After capture, create layout-based groups or frames with clear names such as `01 App Shell`, `02 Header`, `03 Navigation Tabs`, `04 Filter Panel`, `05 Action Toolbar`, `06 Data Table`, `07 Pagination`, and `90 Reference`.
- Do not normalize every divider into a full `1px` box border. Preserve the source page's actual divider model, including one-sided strokes and thinner table grid lines.
- Treat unexpected `#000000` strokes on large app-shell containers, top headers, sidebars, and table wrappers as capture artifacts unless the pixel reference clearly shows black dividers.
- When reconstructing editable repeated sections, derive their style contract from an existing sibling section or row. Do not rebuild a matching table with a different border model, text padding, or header typography.

## Icon Handling

Most missing-icon failures are caused by SVG `<use>` references. Capturing only the visible `<svg>` element often loses the referenced `<symbol>`, so Figma receives an empty image. The reliable fix is:

1. Read the referenced `symbol` by ID.
2. Build a standalone SVG with actual child paths.
3. Apply computed color/fill/stroke.
4. Rasterize it in browser canvas.
5. Replace the original icon with a PNG `<img>`.

Do this before Figma capture. Do not settle for `data:image/svg+xml` if Figma renders blank image fills. PNG is less editable but much more reliable.

Read `references/icon-capture-notes.md` when icon capture fails or the page uses iconfont, SVG sprites, Ant Design icons, or pseudo-element arrows.

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

## Verification Checklist

Before final response, confirm:

- Figma account is the expected account.
- Captured frame has the requested viewport width, usually `1440`.
- Full page height matches `document.documentElement.scrollHeight`; if more than one screen, capture full scroll height.
- A pixel reference screenshot exists or the editable capture has been visually inspected.
- Main icons are visible in the Figma screenshot, not empty image boxes.
- No accidental tutorial/chat/cookie overlay is present unless requested.
- Page type is recorded. If the page is OST admin/operations/backend, final QA uses `ost-admin-system-guidelines` for layout density, colors, typography, forms, tables, buttons, and app-shell consistency. If the page is OST user/merchant-facing, final QA uses `ost-user-system-guidelines` for user-facing navigation, service cards, purchase/申报 flows, readable form hierarchy, status wording, and merchant-side component patterns.
- Top-level editable frame contains semantic layout groups, not only dozens or hundreds of flat primitive siblings.
- Important repeated regions have useful names and hierarchy: navigation, header, tabs, filters, toolbars, table/list, modal/drawer, and reference screenshot.
- Similar repeated sections and tables share the same style contract unless the pixel reference shows a deliberate difference.
- Shell containers and table wrappers do not have unexplained dark borders or black capture artifacts.
- Final answer links directly to the new Figma node and names the frame.

## Common Failure Modes

- **Figma account mismatch**: call all available `whoami` tools; use the namespace with the correct email.
- **Submit command timeout**: poll the capture ID anyway.
- **Blank icon images**: rasterize resolved symbols to PNG, not SVG data URLs.
- **Page state changed after refresh**: restore the requested UI state before capture.
- **Floating overlay appeared**: hide it and recapture.
- **Text mojibake in CDP JSON**: visual screenshot is authoritative; do not infer page quality from garbled console output.
- **Generated black borders**: inspect large `Container` frames and table wrappers for `#000000` strokes; replace with the local divider color on the intended side or remove the stroke.
- **Repeated section drift**: compare the generated section against its sibling source block; repair mismatched row height, padding, individual stroke weights, font style, and parent-relative text coordinates.
- **Wrong page standard**: do not apply `ost-admin-system-guidelines` to merchant/user pages, and do not apply `ost-user-system-guidelines` to internal admin pages. Classify first, then pick the matching OST standard; ask when classification is genuinely unclear.
