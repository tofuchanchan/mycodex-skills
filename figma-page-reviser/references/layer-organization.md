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
```

Avoid raw generated names for newly created or repaired nodes. `Rectangle 143:2` is not a layer name; it is a cry for help.

## Local Regrouping

When an approved edit area is flat:

1. Identify all visible nodes inside the coordinate range and semantic boundary.
2. Split them into groups by user-facing purpose, not by node type.
3. Move existing nodes into those groups without changing absolute page position.
4. Keep the hierarchy shallow unless the region is dense or repeated.
5. Return created or mutated group IDs so follow-up edits can target them.

## Practical Group Shapes

- Filter panel: one group for the panel, one group per field, and one group for filter actions.
- Toolbar: one group for left batch controls and one for right export/settings controls when both exist.
- Table: table group, header group, body group, row groups only when row-level editing matters.
- Similar detail sections: one section group per business block, with a header sub-group and a table/card sub-group that mirrors the sibling section's hierarchy.
- Modal/drawer: container, header, body, footer actions.
- Sidebar: menu section groups and active item group.

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
- No frozen navigation/header/global areas were regrouped without approval.
- Text, icons, and divider nodes use the coordinate system of their actual parent group or cell.
