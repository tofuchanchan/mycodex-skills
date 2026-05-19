# Style and Artifact QA

Use this after `generate_figma_design` creates the editable frame and before the final screenshot review. Capture output can be visually close but structurally wrong, which is the fun part where a prototype quietly becomes a prank.

## What To Check

- App shell: sidebar, top header, page tabs, fixed footer, and major content panels.
- Repeated modules: tables, detail sections, filter fields, cards, toolbar buttons, menu items, and modal sections.
- Semantic colors: red/payable/error, green/success, orange/warning, blue/primary actions.
- Captured artifacts: unintended dark strokes, stray black lines, thin black rectangles, duplicated dividers, or blank image frames.

## Repeated Module Style Contract

For each repeated region, choose a nearby source analogue and compare:

- title font family, size, weight, fill, and height
- header row height, body row height, and column widths
- cell padding and text alignment
- fills and divider colors
- `strokeWeight` and individual side stroke weights
- row grouping and cell parenting
- `textAutoResize` and parent-relative `x/y`

If the source table uses right/bottom dividers, do not replace it with full box borders. If the source amount text is right aligned inside a cell, keep the text node inside that cell with local padding.

## Dark Stroke Cleanup

Search metadata or `use_figma` output for dark strokes and thin dark fills on layout containers. Prioritize:

- sidebar right edge
- top header bottom edge
- table frame and table header wrappers
- panel/card borders

If the pixel reference does not show a black divider:

- use the local divider color from nearby real dividers; or
- remove the wrapper stroke when child cells already own the visible grid.

Do not recolor legitimate black text, icons, logos, or menu labels. This audit targets borders and artifact lines only.

## Coordinate Safety

Generated and regrouped nodes can keep their visible bounds while having surprising parents. Before changing a text node:

- inspect its immediate parent
- calculate `x/y` inside that parent
- verify absolute bounds after writing

Do not paste coordinates from the page frame into a child cell. That is how a right-column value wanders off while looking completely innocent in code.

## Final Report Notes

Mention any cleanup performed:

```text
Style QA: matched repeated table sections against source table.
Artifact cleanup: removed unintended black strokes from app-shell boundaries.
Semantic color QA: payable/error colors are scoped to intended rows only.
```
