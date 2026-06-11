# Layer Organization

Use this before editing a Figma page and again during final QA. A revision should improve or preserve the layer tree; it should not add another layer of chaos to a captured page that is already doing its best impression of a junk drawer.

## Edit Rules

- Locate the semantic owner before writing:
  - sidebar/navigation
  - top header
  - page tabs
  - filter/search panel
  - action toolbar
  - data table/list/card grid
  - pagination
  - modal/drawer/toast/overlay
  - pixel reference
- Append new nodes to the semantic owner group/frame, not to the top-level frame, when that owner exists.
- If the owner does not exist and the edit area is approved, create a local group or frame for the approved region before adding new nodes.
- If grouping would touch frozen areas, ask before regrouping. Do not reorganize the whole file as a drive-by cleanup.
- Preserve visual coordinates and z-order while regrouping.
- Use a two-level model when the approved scope includes layer cleanup: first identify the major owner region, then group the controls and repeated table/list structures inside it. Big section groups with loose buttons, table cell parts, tags, badges, or stepper segments are still incomplete layer organization.
- If the current target was produced by `figma-page-reproducer`, prefer improving existing captured nodes over recreating visuals.

## Naming

Use stable, purpose-first names:

```text
Filter Panel
field / 公司名称
field / 公司名称 / label
field / 公司名称 / input
Action Toolbar
button / 查询
Data Table
table header
table row / U202605001
table cell / 注册号
Table Structure
Table Chrome
Header Row
Header Cell / 上传凭证
Table Body
Row / 1-58522.pdf
Cell / 上传凭证
File Chip / 1-58522.pdf
Input / 净采购额（欧元）
Select / 供应商税号
Cell / 操作
Button / 继续添加
Summary Row / B2B Purchase Amount Total
promo tag / 购买服务 / 618狂欢
count bubble / VAT信件 / 60
Segmented Stepper / 申报流程
stepper segment / 1 填写数据
```

Avoid raw generated names for newly created or repaired nodes. `Rectangle 143:2` is not a layer name; it is a cry for help.

## Local Regrouping

When an approved edit area is flat:

1. Identify all visible nodes inside the coordinate range and semantic boundary.
2. Split them into groups by user-facing purpose, not by node type.
3. Move existing nodes into those groups without changing absolute page position.
4. Keep the hierarchy shallow unless the region is dense or repeated.
5. Return created or mutated group IDs so follow-up edits can target them.
6. For every created group/frame, compare absolute bounds before and after regrouping. If the visible position drifted, fix it before continuing.

## Practical Group Shapes

- Filter panel: one group for the panel, one group per field, and one group for filter actions.
- Toolbar: one group for left batch controls and one for right export/settings controls when both exist.
- Table: table group, table chrome, header row, body group, row groups, meaningful cell groups, operation cells, add-row controls, summary/footer rows, and pagination when present.
- Similar detail sections: one section group per business block, with a header sub-group and a table/card sub-group that mirrors the sibling section's hierarchy.
- Modal/drawer: container, header, body, footer actions.
- Sidebar: menu section groups and active item group.
- Segmented stepper: outer stepper group, segment groups, dividers, check icons, active pointer, and step labels. The first segment owns left radii, the last segment owns right radii, and middle segments stay square unless the source shows otherwise.

## Atomic Component Rules

Within the approved edit area, group multi-node controls as editable units:

- **Button**: background/border, label, icon, loading mark, dropdown caret, disabled overlay. Name as `Button / <label>`.
- **Field or select**: label, required mark, input/select box, value or placeholder, prefix/suffix, clear icon, dropdown arrow, help text, validation text. Name as `Field / <label>` or `Select / <label>`.
- **Amount input**: numeric text, box, currency suffix/prefix, disabled fill, status outline, and validation marker. Name as `Input / <business purpose>`.
- **File chip/upload control**: chip background, filename, remove icon, upload button, upload label, OCR/status icon, and progress text. Name as `File Chip / <file name>` or `Upload Control / <purpose>`.
- **Alert/notice**: background, icon, title, body copy, link, and close icon. Name as `Notice / <purpose>`.
- **Status/tag/badge/link controls**: tag or badge background plus text, link text plus icon, and operation link clusters such as `查看 / 编辑 / 删除`. Name promo labels as `promo tag / <owner> / <text>` and count bubbles as `count bubble / <owner> / <number>`.
- **Navigation/menu/tab item**: item container, label, icon, badge, active indicator, and expand arrow.
- **Segmented stepper**: outer track, segment backgrounds, text labels, check/status icons, dividers, and active pointer. Do not group each segment as a standalone pill when the source is one connected segmented control.

A standalone text node can remain standalone when it truly acts alone. Once a box, icon, value, or status marker belongs with it, group the control. This is not philosophy; it is basic layer hygiene.

## Table and List Rules

Use this structure when the approved scope touches or optimizes a table/list:

```text
Data Table / <business purpose>
  Table Structure
    Table Chrome
      table border
      column dividers
      row dividers
      header background
    Header Row
      Header Cell / 上传凭证
      Header Cell / 净采购额（欧元）
      Header Cell / 操作
    Table Body
      Row / <business key>
        Cell / 上传凭证
          File Chip / <file name>
          Button / 上传凭证
          Status / AI识别中
        Cell / 净采购额
          Input / amount
        Cell / 操作
          Link / 删除
      Button / 继续添加
      Summary Row / <purpose>
      Pagination
```

Specific table requirements:

- Header text and header-only icons belong inside header cell groups when header cells are being edited or organized.
- A row group contains all cells and row-scoped controls for one visual row.
- A cell group contains the content/control nodes that live in that cell.
- Operation links should live under `Cell / 操作`, not float beside row fields like they escaped from prison.
- Add-row controls are buttons and group their background plus label.
- Summary/footer rows group their label, disabled input/value, currency suffix, and related notes.
- Repeated rows should use parallel child structure when their visual pattern matches.
- Keep shared table dividers in `Table Chrome` or a similar table-level group when they span rows/columns. Do not assign a shared divider to one random cell.
- Avoid microscopic group spam for massive tables. Use practical row/cell/control hierarchy in the approved viewport or edit area.

## Coordinate Discipline

- Remember that `x` and `y` are relative to the node's immediate parent, not the top-level frame.
- When moving text into a cell, calculate padding inside that cell. Do not reuse absolute page coordinates or coordinates from the table frame.
- After regrouping or reparenting nodes, inspect their absolute bounds and local `x/y` to confirm the visible position did not drift.

## Audit Rules

Before final response, inspect metadata and check:

- New/changed nodes are not loose primitives under the top-level frame.
- Major layout regions are discoverable by name.
- Top-level child count did not grow because of new primitive nodes.
- Repaired areas have useful local grouping without over-nesting.
- Multi-node controls in the approved edit area are grouped: buttons, fields, selects, notices, file chips, upload controls, tabs, tags, count badges, status badges, segmented steppers, and operation links.
- Edited or optimized tables/lists are not just one wrapper with loose primitive children. They have table chrome/header/body/row/cell structure where row or cell editing matters.
- Repeated rows or repeated cards have parallel child hierarchy when their visual pattern matches.
- No frozen navigation/header/global areas were regrouped without approval.
- Text, icons, and divider nodes use the coordinate system of their actual parent group or cell.

Fix these before reporting `Pass`:

- A button rectangle and its text label are siblings of unrelated content.
- A select/input box, value, suffix, and dropdown arrow are loose siblings instead of one field/select/input group.
- A table frame directly contains all headers, row values, dividers, and operation links.
- Row 1 has useful groups but Row 2 remains flat despite sharing the same pattern.
- A file chip background, filename, remove icon, and upload/OCR status are loose nodes.
- A promo tag such as `618狂欢` is merged into its menu label instead of living as a rounded tag child.
- A count bubble such as `60` is merged into `VAT信件` text instead of living as a badge child.
- A segmented stepper is rebuilt as independent pill buttons with incorrect internal rounded corners.
