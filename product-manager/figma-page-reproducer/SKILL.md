---
name: figma-page-reproducer
description: Reproduce an existing logged-in web page as a static Figma prototype with high visual fidelity and semantic layer organization. Use when the user asks Codex to call Figma to restore, capture, copy, recreate, reproduce, or prototype a real system page, especially pages requiring manual login, OST admin-vs-user page-type detection, full-page scrolling, desktop viewport capture, Figma html-to-design capture, layout-based Figma layer grouping, component-level grouping for buttons/fields/file chips/tabs, visual-semantic inventory for logos, menu/top-header icons, promo tags, count badges, segmented steppers, style-consistent repeated tables/sections, capture-artifact cleanup such as unintended black strokes, or icon-safe handling for SVG iconfont, Ant Design icons, inline SVG, remote images, and CSS pseudo-element arrows. Use `ost-admin-system-guidelines` for OST后台/admin pages and `ost-user-system-guidelines` for OST商户端/user pages.
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
   - Build a visual-semantic component inventory before capture: logo/wordmark, sidebar and top-header icons, promo tags, count badges, segmented steppers, table status chips, floating tools, and warning bars. Record expected counts and component roles so small UI elements cannot be silently dropped or flattened into text.
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
12. Load `references/layer-organization.md` and run a semantic layer organization pass. This is a two-level pass: first group major page regions, then group atomic controls and repeated table/list structures inside those regions. A result that only has large section groups while buttons, fields, table rows, table cells, tags, badges, file chips, and operation links remain loose siblings is not complete.
13. Load `references/style-artifact-qa.md` and run a capture cleanup pass for repeated-module style consistency, semantic color scope, parent-relative coordinates, and unintended dark strokes.
14. Add or keep a pixel reference screenshot frame when useful, especially for review or fidelity comparison; keep it outside the editable app frame or under a clearly named reference group.
15. Validate the Figma result with `get_screenshot` and metadata. Check logo presence, icon counts, promo tags, count badges, segmented stepper corner radii, viewport size, scroll height, missing images, accidental overlays, obvious layout drift, page-type standard compliance, similar section consistency, accidental dark borders, and layer tree organization.

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

## Visual Semantic Inventory and Component Contracts

Before capture or manual reconstruction, build a visible-component inventory from the rendered screenshot plus visible DOM bounding boxes. Do not trust `document.body.innerText` alone: SPA pages often keep stale login text, hidden modals, zero-size popups, or off-screen notices in the DOM. The screenshot is the source of truth for what must be reproduced.

Inventory these components explicitly:

- Brand/logo: logo mark, wordmark, subtitle, whether it is an image or editable vector/text, and its bounding box.
- Navigation icons: every sidebar menu item and top-header action that has an icon in the screenshot; record expected counts.
- Tags and badges: small rounded color-backed labels such as `618狂欢`, status chips, red count bubbles such as `VAT信件 60`, notification dots, and warning/price labels.
- Segmented steppers: segment count, labels, check icons, active pointer, and exact corner model. First segment only has left radii, last segment only has right radii, middle segments are square unless the screenshot proves otherwise.
- Tables/lists: header/body/footer rows, summary rows, operation cells, right-aligned amount cells, and semantic red/green/orange emphasis.
- Floating tools and environment warnings: decide whether to preserve, hide, or remove them based on user scope. Sandbox/UAT warning bars should not be reproduced when the user asks to remove them.

Component contracts:

- Logo is never optional. Use the captured image when available, or rebuild it as editable `logo mark`, `wordmark`, and subtitle nodes. A generic colored circle is a failure unless the source logo is literally a colored circle.
- Icons are never optional when visible in the pixel reference. If capture loses them, rasterize them to PNG or rebuild simple editable vector icons. Count expected icons before final QA.
- Do not merge adjacent text into one label when the screenshot shows separate visual roles. A small colored rounded label next to menu text is a tag, not part of the menu string. A red number next to a menu label is a count badge, not part of the menu string.
- Group tags and badges with their owning component but keep them as separate named child nodes, e.g. `promo tag / 购买服务 / 618狂欢` and `count bubble / VAT信件 / 60`.
- Stepper segments must preserve the source corner model and dividers. Do not draw every step as an independent pill; that creates wrong internal rounded corners.
- When `generate_figma_design` fails and you manually rebuild with `use_figma`, the same inventory and component contracts still apply. Manual fallback is not permission to omit small UI elements because they are annoying.

Post-build QA gates:

- Screenshot the Figma frame and inspect the specific inventory items: logo, icon counts, promo tags, count badges, stepper radii, table rows, and removed warnings.
- Query metadata/text for failure patterns such as `购买服务 618狂欢`, `续费服务 618狂欢`, or `VAT信件 60` as single text nodes. These indicate tag/badge semantics were flattened and must be fixed.
- Reject the result before final delivery if any visible source logo/icon/tag/badge/stepper detail is missing or semantically flattened.

## Figma Capture Rules

- For external authenticated sites, do not open a fresh unauthenticated URL for capture. Inject the capture script into the live logged-in tab.
- Decide the page type before applying design standards. OST admin pages should use `ost-admin-system-guidelines`; OST user/merchant pages should use `ost-user-system-guidelines`. If the exact guideline skill is unavailable, preserve the captured page's current visual system and record the fallback.
- Prefer `generate_figma_design` for the initial editable conversion, but treat it as a raw-frame capture, not a design-system-quality final component library.
- Always use `figma-use` before `use_figma` calls.
- `generate_figma_design` captures raw frames. If the user wants reusable production-quality prototypes later, replace repeated controls with design-system components after the raw capture is accepted.
- Rename captured nodes immediately. Default names like `uat`, `Body`, and `Container` are useless.
- Do not leave a generated page as a flat pile of sibling nodes. After capture, create layout-based groups or frames with clear names such as `01 App Shell`, `02 Header`, `03 Navigation Tabs`, `04 Filter Panel`, `05 Action Toolbar`, `06 Data Table`, `07 Pagination`, and `90 Reference`.
- Macro groups alone are not enough. Inside every major region, group multi-node controls into editable component units: buttons should contain backgrounds, labels, icons, and loading marks; fields should contain labels, boxes, values/placeholders, suffix icons, clear icons, and validation text; tags and badges should remain named child nodes rather than being merged into text.
- Tables and repeated lists need their own hierarchy instead of one giant table frame with loose text nodes. Create table chrome, header row, body, row groups, cell groups, operation cells, add-row buttons, summary/footer rows, and pagination groups when those structures exist.
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
- Group atomic UI controls after region grouping. Buttons, inputs, selects, segmented controls, tabs, tags, badges, alerts, file chips, status badges, amount inputs with suffixes, and operation links should become named groups or frames when they have more than one visual child.
- Keep tags and badges separate from text labels inside their parent component. Examples: `promo tag / 购买服务 / 618狂欢` and `count bubble / VAT信件 / 60`.
- Keep repeated structures readable without over-nesting. For large tables, group at table/header/body/row level, then group meaningful cell controls inside each row. Do not create one group per standalone text node or divider unless it is part of a cell/control that needs to move together.
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
- Component-level groups exist inside major regions. Buttons are not split into separate rectangle/text siblings; fields are not split into box/value/icon siblings; table rows and operation cells are not loose children of the table frame.
- Visual-semantic inventory checks pass: source logo is present, expected sidebar/top-header icons are present, promo tags are separate tag nodes, count badges are separate badge nodes, and segmented steppers preserve first/last corner radii.
- Metadata/text checks do not show flattened component strings such as `购买服务 618狂欢`, `续费服务 618狂欢`, or `VAT信件 60` as single text nodes.
- Similar repeated sections and tables share the same style contract unless the pixel reference shows a deliberate difference.
- Shell containers and table wrappers do not have unexplained dark borders or black capture artifacts.
- Final answer links directly to the new Figma node and names the frame.

## Common Failure Modes

- **Figma account mismatch**: call all available `whoami` tools; use the namespace with the correct email.
- **Submit command timeout**: poll the capture ID anyway.
- **Blank icon images**: rasterize resolved symbols to PNG, not SVG data URLs.
- **Dropped logo or icons in manual fallback**: if auto-capture fails and you rebuild manually, recreate the visible logo and every inventoried sidebar/top-header/stepper icon. Placeholder marks are not acceptable unless they match the pixel reference.
- **Flattened tags or badges**: if `618狂欢` becomes part of a menu label or `60` becomes part of `VAT信件` text, split it into a rounded tag/badge node and group it under the owning menu item.
- **Wrong stepper corner radii**: do not make each step a pill. The first segment owns left radii, the last segment owns right radii, and middle segments stay square unless the screenshot proves otherwise.
- **Page state changed after refresh**: restore the requested UI state before capture.
- **Floating overlay appeared**: hide it and recapture.
- **Text mojibake in CDP JSON**: visual screenshot is authoritative; do not infer page quality from garbled console output.
- **Only macro grouping**: if the frame has groups for big blocks but loose child nodes for buttons, form controls, table rows, table cells, tags, badges, file chips, or operation links, run another organization pass. Big boxes with scattered parts are still not editable component groups.
- **Generated black borders**: inspect large `Container` frames and table wrappers for `#000000` strokes; replace with the local divider color on the intended side or remove the stroke.
- **Repeated section drift**: compare the generated section against its sibling source block; repair mismatched row height, padding, individual stroke weights, font style, and parent-relative text coordinates.
- **Wrong page standard**: do not apply `ost-admin-system-guidelines` to merchant/user pages, and do not apply `ost-user-system-guidelines` to internal admin pages. Classify first, then pick the matching OST standard; ask when classification is genuinely unclear.
