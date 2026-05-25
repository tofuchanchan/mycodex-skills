---
name: figma-page-reviser
description: Revise an existing Figma page or frame, especially one created by figma-page-reproducer, with scoped edits, semantic layer organization, explicit user confirmation, suggestion-by-suggestion approval, and post-edit design QA. Use when the user asks Codex to modify, adjust, refine, revise, optimize, or review a reproduced Figma page while preserving untouched areas, deciding whether to copy or edit the original frame, identifying OST后台/admin vs OST商户端/user page standards, applying ost-admin-system-guidelines or ost-user-system-guidelines as appropriate, maintaining layout-based Figma layer grouping, component-level grouping for buttons/fields/file chips/tabs, table-level grouping for header/body/rows/cells/operation links, checking similar-module style consistency, auditing semantic colors, and removing accidental capture artifacts such as wrong black strokes after changes.
---

# Figma Page Reviser

## Goal

Modify an existing Figma page with controlled scope. Treat the user's requested changes as the source of authority, preserve everything outside the approved scope, ask before filling gaps the user did not mention, and verify the finished design before responding.

This skill is intended to run after `figma-page-reproducer`, but it also applies to any static Figma page/frame that needs careful revision.

## Required Workflow

1. Confirm inputs: target Figma file URL/key, target node/frame, requested changes, source page URL when available, and whether the page came from `figma-page-reproducer`.
2. Load `references/page-type-detection.md` and identify page type before drafting the edit contract:
   - For OST internal admin/operations/backend pages, use `ost-admin-system-guidelines`.
   - For OST merchant-facing/user/customer pages, use `ost-user-system-guidelines`.
   - Treat URL/domain and app shell as stronger evidence than table density. For example, `uat-user.evatmaster.com` is merchant/user even when it contains dense VAT tables.
   - If page type is unclear, ask the user to confirm before using a design standard for revisions or QA.
3. Load `references/scope-contract.md` and create a concise modification contract that records the detected page type and selected design standard.
4. Ask the user to confirm the contract before editing. Include the required question: copy the frame first, or directly modify the original? If page type is unclear, include the admin/user standard choice in the same confirmation.
5. Before any Figma write action, read current metadata and take or request a screenshot for the target node. Identify existing semantic layer groups for the requested edit area.
6. Use `figma-use` before every `use_figma` write or inspection call.
7. Load `references/layer-organization.md` before creating, moving, deleting, or regrouping Figma nodes. Execute only the user-approved modifications in the approved node or coordinate range, and place new or changed nodes in the matching semantic group instead of flattening them at the frame root. When the approved scope includes layer optimization, run the same two-level organization model as `figma-page-reproducer`: first group major regions, then group atomic controls and table/list structures such as buttons, fields, file chips, table header/body/rows/cells, and operation links.
8. When adding or changing a section similar to an existing one, load `references/style-consistency-audit.md`. Choose the nearest existing analogue as the style donor and copy or match its typography, fills, strokes, individual stroke weights, row heights, padding, and parent-relative coordinates before inventing new styling.
9. Load `references/confirmation-rules.md` and list inferred completion suggestions. Do not execute any suggestion until the user approves that exact item.
10. After approved edits are complete, load `references/text-overflow-audit.md` and run a text overflow audit on the modified node, including nearby visible single-line controls affected by the layout.
11. Run the style consistency and visual artifact audits from `references/style-consistency-audit.md` on modified repeated sections, emphasis colors, table geometry, and shell divider strokes.
12. Run the layer organization audit from `references/layer-organization.md` on the modified node or the approved edit area.
13. Load `references/figma-qa-checklist.md` and inspect the modified design with Figma screenshot, metadata, text overflow audit results, style consistency findings, artifact findings, and layer organization audit results.
14. Report the modified node link, executed changes, approved suggestions, unexecuted suggestions, QA result, and remaining questions.

## Hard Gates

- Do not edit until the user confirms whether to copy the frame or directly modify the original.
- Do not edit until the page type and selected design standard are recorded, or explicitly confirmed when unclear.
- Do not execute inferred or "helpful" additions until the user approves each item.
- Do not apply `ost-admin-system-guidelines` to merchant/user pages, and do not apply `ost-user-system-guidelines` to internal admin pages. Classify first; if genuinely unclear, ask.
- Do not change navigation, sidebar, header, footer, unrelated tables, unrelated modals, or global styles unless they are part of the confirmed scope.
- Do not silently resize the top-level frame, change page-wide spacing, or restyle repeated components outside the approved area.
- Do not hand-roll a table, card, title block, or detail section when a visually similar sibling already exists. Use the sibling as a style donor and verify the match with node properties.
- Do not apply semantic emphasis colors such as red, warning, success, or primary blue to adjacent rows by range selection. Audit the exact text node IDs that should receive the color.
- Do not use coordinates copied from one parent frame inside another parent frame. Figma `x` and `y` are parent-relative; wrong coordinate space is how text teleports into the next postcode.
- Do not leave unintended `#000000` strokes on shell containers, table headers, sidebars, or top bars unless the source design visibly uses black dividers.
- Do not treat a successful API response as enough. Always inspect the result visually or state why visual inspection could not be completed.
- Do not mark QA as `Pass` while likely text wrapping, clipping, or overflow findings remain unresolved. Fix findings inside the approved edit area as `Visual repair`; if the fix touches a frozen area, report `Needs confirmation`.
- Do not append newly created primitives directly under the top-level page frame when a matching semantic group exists. Flat root-layer dumping is a bug, not a workflow.
- Do not call layer organization complete when only large page sections are grouped. If buttons, form controls, file chips, table rows, table cells, add-row buttons, summary rows, or operation links remain loose siblings inside the approved edit area, run another local regroup pass.
- Do not regroup outside the approved scope just to make the whole file prettier. If global layer cleanup is needed, list it as a suggestion and wait for approval. Heroic unsolicited cleanup is how people accidentally ship haunted Figma files.

## Scope Control

Prefer three constraints together when targeting edits:

- Node identity: selected node, node ID, stable layer name, or frame name.
- Spatial boundary: x/y/width/height range inside the frame.
- Semantic boundary: user-facing area name, such as "filter bar", "detail drawer", "invoice table", or "submit modal".
- Layer boundary: existing semantic group or frame that owns the area, such as `Filter Panel`, `Action Toolbar`, `Data Table`, `Table Body`, `Row / <business key>`, `Cell / 操作`, `Modal`, or `Sidebar Navigation`.

If these constraints disagree, stop and ask. Do not guess by vibes; vibes are how sidebars get deleted.

## Suggestion Policy

Classify inferred follow-up work before asking the user:

- `Must confirm`: changes that alter business meaning, content structure, workflow, permissions, data fields, or copy.
- `Should confirm`: states or companion elements that improve completeness, such as empty state, loading state, error message, success toast, or mobile/long-text variant.
- `Visual repair`: local alignment, overflow, icon color, or spacing fixes inside the already-approved edit area.

Ask the user to approve suggestions by ID, for example `S1`, `S2`, `S3`. Only execute approved IDs. If a visual repair would touch frozen areas, promote it to `Must confirm`.

## QA Expectations

Review at least:

- Scope: only approved areas changed; frozen areas preserved.
- Layout: alignment, spacing, text overflow, icon/image visibility, table geometry, modal/drawer containment.
- Text fit: run the text overflow audit for fixed-size text in single-line controls such as input placeholders, tabs, buttons, table headers, and table cells. Do not rely on scaled screenshots alone; short overflows are easy to miss.
- Consistency: typography, color, border, radius, shadow, copy tone, and component density match the detected page type and selected OST standard.
- Similar-module parity: if two blocks have the same role, such as VAT detail and B2B detail, compare titles, header rows, body rows, cell fills, divider weights, padding, text alignment, and table frame strokes against the source block.
- Semantic emphasis: verify alert or payable rows are the only nodes using alert colors; nearby normal rows must keep normal body color.
- Visual artifacts: scan shell containers, table headers, and layout boundaries for accidental dark strokes or thin black fills introduced by capture or repair scripts.
- Structure: top-level frame size, nested frame bounds, clipping, z-order, and accidental overlays.
- Layer organization: new and changed nodes live under the correct semantic group; root-level child count does not grow with loose primitives.
- Component grouping: multi-node buttons, fields, selects, file chips, upload controls, tabs, tags, status badges, and operation links are grouped as the controls a human would edit together.
- Table grouping: edited or optimized tables/lists have practical hierarchy: table chrome, header row/cells, body, row groups, meaningful cell groups, operation cells, add-row controls, summary/footer rows, and pagination when present.
- Content: requested text and data labels are present; unapproved copy was not invented.

If QA finds a problem inside the approved scope, fix it and re-check. If the fix requires expanding scope, ask the user first.

## References

- Read `references/scope-contract.md` before drafting the modification contract.
- Read `references/confirmation-rules.md` before proposing inferred completion work.
- Read `references/page-type-detection.md` when deciding whether the page is OST admin/backend, OST user/merchant-facing, or unclear.
- Read `references/layer-organization.md` before editing or creating Figma nodes and before final QA whenever the target frame may be flat or partially flat.
- Read `references/style-consistency-audit.md` before editing repeated modules, tables, sections with matching titles, semantic color emphasis, or any captured frame that shows unexplained dark dividers.
- Read `references/text-overflow-audit.md` before final QA whenever text, tables, filters, buttons, tabs, or column widths are created, moved, resized, or edited.
- Read `references/figma-qa-checklist.md` before final inspection.

## Final Response

Include:

- Modified Figma node link.
- Modification mode: copied frame or original frame.
- Page type and selected design standard.
- Completed user-requested changes.
- Approved suggestions that were executed.
- Suggestions not executed.
- QA result and any unresolved issues.
