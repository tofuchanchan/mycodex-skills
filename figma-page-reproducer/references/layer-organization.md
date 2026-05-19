# Layer Organization

Use this after a Figma page capture or reconstruction creates an editable frame. The goal is a design file a human can edit without spelunking through a landfill of rectangles.

## Grouping Model

Create hierarchy from the page layout:

- Top-level frame: one editable page or viewport, named with page purpose and viewport.
- App shell groups: sidebar, top header, visited tabs, page tabs, footer or fixed warning bars.
- Content groups: page title, filters/search form, action toolbar, data table/list/cards, pagination, empty/loading state, detail drawer, modal, toast.
- Repeated component groups: form field, button, tab item, menu item, table row, table header, table operation cell.
- Reference groups: pixel screenshots or comparison images, named separately and kept outside the editable app frame when possible.
- Similar business sections should mirror each other's hierarchy when they represent the same pattern, such as a detail-section header plus table, filter field plus input, or table header plus body rows.

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
05.03.02 Row / <business key>
90 Overlays
```

Prefer names that describe user-facing purpose over implementation trivia. `field / 公司名称`, `button / 查询`, and `table row / U202605001` are useful. `Rectangle 239` and `Container 17` are trash.

## Boundaries

- Group elements that move together or represent one UI control.
- Keep visual coordinates unchanged while regrouping.
- Preserve parent-relative coordinates when reparenting. After moving nodes into semantic groups, verify both local `x/y` and absolute bounds.
- Do not group unrelated elements only because they overlap on the x/y axis.
- Do not put global navigation, page content, and reference screenshots in the same group.
- Use shallow hierarchy for simple pages; use deeper hierarchy only for dense admin pages, tables, drawers, or repeated cards.

## Reproducer Rules

- Build the layer plan from DOM landmarks, visible layout regions, and Figma metadata.
- After `generate_figma_design`, inspect the generated frame. If it is flat, run a regroup pass with `use_figma`.
- Prefer grouping existing generated nodes over recreating visuals.
- Keep table/list hierarchy practical:
  - Header group
  - Body group
  - Row groups when row-level editing matters
  - Avoid one group per tiny text/line unless the source design already uses it.
- When a generated table or repeated section has a nearby analogue, mirror that analogue's grouping and naming before doing style cleanup.

## QA

Before final response, inspect metadata and confirm:

- The editable frame has semantic child groups or frames.
- Top-level child count is reasonable for the page complexity.
- Major layout regions are named and discoverable.
- Regrouping did not shift visible coordinates or hide nodes.
- Reference screenshots are clearly separated from editable content.
- Repeated sections with the same visual role have parallel hierarchy and parent-relative coordinates.
