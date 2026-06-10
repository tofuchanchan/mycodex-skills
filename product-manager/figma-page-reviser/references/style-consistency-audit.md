# Style Consistency and Artifact Audit

Use this before and after revising repeated modules, tables, detail sections, semantic emphasis colors, or captured app-shell boundaries. A nearby matching block is the design system until proven otherwise.

## Failure Modes Captured

- A newly added B2B detail table looked unlike the VAT detail table because it used full `1px` cell borders while the source table used thinner right/bottom divider strokes.
- Right-aligned text was positioned with coordinates from the table frame even though its parent was the amount cell. Figma coordinates are parent-relative, so the text landed in the wrong place.
- `进项税 / Input VAT` inherited red emphasis even though only `应缴VAT / VAT Payable` should be red.
- Captured shell containers kept `#000000` strokes, creating black borders on the sidebar and top header.

## Source Analogue Rule

When the requested edit creates or changes something similar to an existing block:

1. Pick the closest visible source analogue, such as the table above, sibling detail section, existing filter field, or current action button.
2. Inspect the source and target node properties with `use_figma`, not only screenshots.
3. Copy or match:
   - font family, style, size, line height, text fill, text alignment, and `textAutoResize`
   - row height, column width, padding, and parent-relative `x/y`
   - fills, strokes, `strokeWeight`, and individual side stroke weights
   - corner radius, effects, opacity, and clipping where relevant
4. Keep the new nodes inside the same semantic owner group as the edited area.
5. Re-run the comparison after writing.

## Table Repair Rules

- Prefer cloning an existing table row/header/cell structure and changing text over building a visually similar table from scratch.
- If cloning is not practical, match the source table's geometry exactly: table frame, header row, body row, cell widths, row heights, padding, and right-aligned amount text.
- Match individual stroke weights. A source cell with only right/bottom dividers is not equivalent to a full box border.
- Treat header text and body text separately. Header text commonly uses bold `#333333`; body text commonly uses regular `#666666`.
- Verify text node coordinates are relative to their immediate parent cell. Right column text should usually have `x = padding`, fixed width, and `textAlignHorizontal = "RIGHT"` inside the right cell.

## Semantic Color Audit

- Before applying an emphasis color, list the exact node IDs that should change and why.
- After writing, scan adjacent rows and labels for the same emphasis color.
- If an amount row is red because it is payable or overdue, verify normal rows above and below are still normal body color.
- Do not use row-range or broad subtree recoloring when only one row or one label should be emphasized.

## Dark Stroke Artifact Audit

Captured pages can contain accidental black strokes on large `Container` frames or table/header wrappers.

Inspect these boundaries after revisions:

- sidebar right edge
- top header bottom edge
- table frame and table header wrappers
- card/panel edges around modified content

If a dark stroke is not part of the source design:

- replace it with the local divider color, commonly a light grey such as `#e8e8e8`, and apply it only on the intended side; or
- remove it entirely when the actual dividers are owned by child cells.

Do not delete or recolor legitimate black text or icons while scanning for black artifacts. The target is thin borders, strokes, and accidental divider fills.

## QA Output

Report the style donor and the comparison result:

```text
Style donor: VAT申报明细 / Table
Matched: row height, column width, fills, right/bottom divider weights, header/body typography, text padding
Fixed artifacts: sidebar right stroke, top header bottom stroke
Semantic color check: only 应缴VAT row remains red
```
