# Figma QA Checklist

Run this after edits and after approved suggestions.

## Required Inputs

- Current screenshot of the modified node.
- Visual-semantic inventory for the approved or affected area: logo/wordmark, icons, promo tags, count badges, status chips, segmented steppers, warning/notice bars, and whether each item is in-scope or frozen.
- Metadata for the modified node and important child nodes.
- Text overflow audit findings for fixed-size single-line text.
- Layer organization audit findings for the modified node or approved edit area.
- Style consistency findings for repeated modules or similar sections.
- Visual artifact findings for unintended dark strokes, stray borders, or capture leftovers.
- The confirmed scope contract.
- The recorded page type and selected design standard.
- List of approved suggestion IDs.

## Scope QA

- Approved areas changed as requested.
- Frozen areas are unchanged.
- No new unapproved content, states, or components were added.
- If a copy was requested, the original frame still exists.
- If direct modification was requested, the final response clearly says so.

## Visual QA

- Text fits inside containers; no clipped labels, buttons, table cells, or titles.
- Fixed-size `TEXT` nodes in single-line controls do not wrap or clip. Check input placeholders, select values, tab labels, buttons, table headers, and table cells with the text overflow audit.
- Alignment follows the local grid and nearby components.
- Spacing is consistent with surrounding controls.
- Typography, colors, borders, radius, shadows, and icon sizing match the existing design system.
- Similar sections share the same title typography, table/card structure, row heights, padding, text alignment, fills, divider colors, and individual stroke weights.
- Semantic colors are scoped to their intended meaning. Alert/payable red, success green, warning orange, and primary blue should not leak into neighboring normal rows or labels.
- App-shell boundaries and table wrappers do not contain accidental dark strokes or thin black fills from capture or repair scripts.
- Icons and images render; no blank placeholders or broken fills.
- Logos and wordmarks in the approved or affected area are present; placeholder marks are failures unless they match the source.
- Promo tags and count badges remain separate rounded child nodes. Do not merge `618狂欢` into a menu label or `60` into `VAT信件` text.
- Segmented steppers keep the source corner model: first segment left radii, last segment right radii, middle segments square, plus original dividers, check icons, active indicators, and pointer shapes.
- Tables keep coherent row height, column width, headers, dividers, and action alignment.
- Modals/drawers/cards contain their content without overlap.

## Structure QA

- Top-level frame dimensions are unchanged unless approved.
- Child nodes remain inside expected parent frames.
- New or modified nodes live inside semantic layout groups instead of loose top-level primitive layers.
- Multi-node controls in the approved edit area are grouped as editable components: buttons, fields, selects, file chips, upload controls, notices, tabs, tags, count badges, status badges, segmented steppers, and operation links.
- Edited or optimized tables/lists have practical hierarchy: table chrome, header row/cells, body, row groups, meaningful cell groups, operation cells, add-row controls, summary/footer rows, and pagination when present.
- Repeated rows or cards with the same visual pattern use parallel child hierarchy.
- Z-order does not hide important controls.
- Clipping, scroll areas, and fixed headers/footers remain coherent.
- Auto layout changes, if any, do not collapse or stretch unrelated sections.
- Text overflow fixes stay inside the approved area. If a required fix touches frozen areas, mark QA as `Needs confirmation`.
- Layer regrouping stays inside the approved area. If the frame is globally flat but only a small area was approved, report the global layer issue separately instead of reorganizing everything.
- QA cannot be `Pass` when a table wrapper still directly contains loose header texts, row values, field boxes, and operation links in the approved edit area. That is not layer organization; that is drawer stuffing with extra steps.
- QA cannot be `Pass` when metadata/text shows flattened component strings such as `购买服务 618狂欢`, `续费服务 618狂欢`, or `VAT信件 60` as one text node in the approved or affected area.

## Page-Type QA

- OST admin/backend pages keep dense, work-focused layouts and follow `ost-admin-system-guidelines` when selected.
- OST user/merchant-facing pages keep user-facing guidance, readable form hierarchy, service/purchase/申报 page patterns, and follow `ost-user-system-guidelines` when selected.
- Dense tables inside an OST user/merchant-facing page do not override the selected `ost-user-system-guidelines` standard.
- If page type was unclear, the chosen review standard is recorded.

## Response Summary

Report:

- `Pass`: no material issues found.
- `Fixed`: issues found and repaired within approved scope.
- `Needs confirmation`: issues found but repair would expand scope.
- `Could not verify`: explain which screenshot/metadata step failed.
