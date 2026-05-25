# Layer Organization

Use this after a Figma page capture or reconstruction creates an editable frame. The goal is a design file a human can edit without spelunking through a landfill of rectangles.

## Grouping Model

Create hierarchy from the page layout in two passes. First build the page skeleton; then group the real editable controls inside it. Stopping after the first pass creates a pretty outline and an unusable layer tree.

- Top-level frame: one editable page or viewport, named with page purpose and viewport.
- App shell groups: sidebar, top header, visited tabs, page tabs, footer or fixed warning bars.
- Content groups: page title, filters/search form, action toolbar, data table/list/cards, pagination, empty/loading state, detail drawer, modal, toast.
- Atomic component groups: form field, button, tab item, menu item, alert, file chip, tag/status badge, amount input with suffix, operation link, upload control, pagination item.
- Repeated structure groups: table, table header row, header cell, table body, table row, table cell, table operation cell, summary/footer row, list item, card item.
- Reference groups: pixel screenshots or comparison images, named separately and kept outside the editable app frame when possible.
- Similar business sections should mirror each other's hierarchy when they represent the same pattern, such as a detail-section header plus table, filter field plus input, or table header plus body rows.

Use groups for visual units whose children should move together. Use frames when the unit has a meaningful rectangular boundary, clipping, background, or repeated layout contract. Keep the original pixels unchanged either way.

## Naming

Use stable, sortable names:

```text
00 Pixel Reference
01 App Shell
02 Sidebar Navigation
03 Top Header
04 Page Tabs
05 Content Card
05.01 Filter Panel
05.02 Action Toolbar
05.03 Data Table
05.03.01 Table Header
05.03.01.01 Header Cell / 上传凭证
05.03.02 Table Body
05.03.02.01 Row / <business key>
05.03.02.01.01 Cell / 上传凭证
05.03.02.01.01 File Chip / <file name>
05.03.02.01.02 Cell / 净采购额
05.03.02.01.02 Input / Amount
05.03.03 Add Row Button
05.03.04 Summary Row
90 Overlays
```

Prefer names that describe user-facing purpose over implementation trivia. `field / 公司名称`, `button / 查询`, and `table row / U202605001` are useful. `Rectangle 239` and `Container 17` are trash.

When the raw capture already names children with prefixes like `row 1 / amount / box`, use those prefixes as evidence for regrouping. The prefix is not the final hierarchy; it is a clue to build the hierarchy.

## Boundaries

- Group elements that move together or represent one UI control.
- Keep visual coordinates unchanged while regrouping.
- Preserve parent-relative coordinates when reparenting. After moving nodes into semantic groups, verify both local `x/y` and absolute bounds.
- Do not group unrelated elements only because they overlap on the x/y axis.
- Do not put global navigation, page content, and reference screenshots in the same group.
- Use shallow hierarchy for simple pages; use deeper hierarchy only for dense admin pages, tables, drawers, or repeated cards.
- A standalone text label can stay standalone when it truly acts alone. Any label plus box/icon/value/status combination should be grouped as the control it represents.
- Keep table grid lines in a `Table Chrome` or equivalent group when they span multiple rows/columns. Do not attach a shared divider to one random row just because its bounding box crosses that row.

## Atomic Component Rules

After macro grouping, inspect each region for multi-node controls. Group these before final QA:

- **Button**: background/border, label, leading/trailing icon, loading spinner, dropdown caret, and disabled overlay. Name as `button / <label>`.
- **Input or select field**: label, required mark, box, value or placeholder, prefix/suffix, clear icon, dropdown arrow, help text, validation text. Name as `field / <label>` or `select / <label>`.
- **Amount input**: input box, numeric value, currency suffix/prefix, disabled fill, status outline, and validation mark. Name as `input / amount / <currency or purpose>`.
- **File chip/upload control**: chip background, filename, remove icon, upload button, upload label, progress/status icon, OCR/AI status text. Name as `file chip / <filename>` or `upload control / <purpose>`.
- **Alert/notice**: notice background, icon, title, body copy, link, close icon. Name as `notice / <purpose>`.
- **Status/tag/link controls**: tag background plus text, link text plus icon, operation link clusters such as `查看 / 编辑 / 删除`.
- **Navigation/menu/tab item**: item container, label, icon, badge, active indicator, expand arrow.

Do not group purely decorative one-off primitives into fake components. The test is simple: if a human would drag, hide, rename, duplicate, or edit those parts as one control, group them.

## Table and List Rules

Tables are where lazy grouping goes to die. Build a hierarchy that matches how a human edits table content:

```text
Data Table / <business purpose>
  Table Chrome
    table border
    column dividers
    row dividers
    header background
  Header Row
    Header Cell / 上传凭证
    Header Cell / 净采购额（欧元）
    Header Cell / 供应商税号
    Header Cell / 操作
  Body
    Row / <row number or business key>
      Cell / 上传凭证
        File Chip / <file name>
        Upload Button / 上传凭证
        Status / AI识别中
      Cell / 净采购额
        Input / amount
      Cell / 供应商税号
        Select / supplier tax
      Cell / 供应商公司名
        Select / supplier company
      Cell / 操作
        Link / 删除
  Add Row Button
  Summary Row
  Pagination
```

Use this structure when the page has editable table fields, upload chips, row actions, or summary rows. For simple read-only tables, header/body/row groups may be enough, but row content should still be grouped when cells contain multiple child nodes.

Specific table grouping requirements:

- Header text and header-only icons belong inside header cell groups.
- A body row group should contain all cells and row-scoped controls for one visual row.
- A cell group should contain the text/input/select/chip/action nodes that live in that cell.
- Operation cells should group related action links and icons; `删除` should not float as a naked text node beside row fields.
- Add-row controls such as `+ 继续添加` are buttons and must group background plus label.
- Summary/footer rows should group label, disabled input/value, currency suffix, and related notes.
- Repeated rows should share the same child structure whenever the visual pattern matches, even when some cells are empty.
- Avoid thousands of tiny groups for a massive table. If the table has many rows, group sampled visible rows and repeated cell controls in the captured viewport; keep the hierarchy practical but not useless.

## Figma Regrouping Procedure

1. Inspect metadata for child names, absolute bounds, node types, and repeated prefixes.
2. Draft a layer plan before writing: page regions, component groups, table/list hierarchy, and reference groups.
3. Regroup existing generated nodes with `use_figma`; prefer preserving nodes over recreating visuals.
4. For groups, use the Figma API grouping operation so absolute bounds stay stable.
5. For frames, compute bounds from children, create the frame at that absolute position, move children into it, and update child coordinates relative to the new parent.
6. After every significant group/frame creation, compare absolute bounds before and after. If nodes moved, fix coordinates immediately.
7. Rename groups/frames after creation; do not leave `Group 12` or `Frame 88` in the final tree.

## Reproducer Rules

- Build the layer plan from DOM landmarks, visible layout regions, and Figma metadata.
- After `generate_figma_design`, inspect the generated frame. If it is flat, run a regroup pass with `use_figma`.
- Prefer grouping existing generated nodes over recreating visuals.
- Do not treat a top-level table frame as sufficient. If its children are loose header texts, row values, input boxes, and action links, the table still needs header/body/row/cell/component grouping.
- Keep table/list hierarchy practical: header group, body group, row groups, meaningful cell groups, and grouped controls inside cells.
- Avoid one group per tiny text/line unless the source design already uses it or the node is part of a larger component/control group.
- When a generated table or repeated section has a nearby analogue, mirror that analogue's grouping and naming before doing style cleanup.

## QA

Before final response, inspect metadata and confirm:

- The editable frame has semantic child groups or frames.
- Top-level child count is reasonable for the page complexity.
- Major layout regions are named and discoverable.
- Multi-node controls are grouped: buttons, fields, selects, notices, file chips, upload controls, tabs, tags, status badges, and operation links.
- Tables/lists are not just one wrapper with loose primitive children. They have header/body/row/cell structure where the UI needs row or cell editing.
- Repeated rows or cards have parallel child hierarchy.
- Regrouping did not shift visible coordinates or hide nodes.
- Reference screenshots are clearly separated from editable content.
- Repeated sections with the same visual role have parallel hierarchy and parent-relative coordinates.

Failure examples that must be fixed before delivery:

- A button rectangle and its text label are siblings of unrelated content.
- A select box, selected value, and dropdown arrow are siblings instead of one field/select group.
- A table frame contains all header labels, row values, dividers, and operation links directly.
- Row 1 has useful groups but Row 2 is flat, even though both rows use the same visual pattern.
- A file chip background, filename, remove icon, and upload status are four loose nodes.
