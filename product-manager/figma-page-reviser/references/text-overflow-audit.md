# Text Overflow Audit

Run this before final QA whenever a revision changes or moves text, filters, buttons, tabs, tables, column widths, or their nearby containers.

## Failure Mode

Figma metadata can look valid while the rendered design is broken. A fixed-size `TEXT` node with `textAutoResize: "NONE"` may wrap when its one-line content is wider than `node.width`. If the node height is only one line, the second line is clipped or spills into nearby UI. This is common for CJK labels, placeholders, tabs, and table cells.

## Audit Rules

- Treat input placeholders, select values, tab labels, buttons, table headers, and compact table cells as single-line controls unless the existing design clearly uses multi-line text.
- For fixed-size text, compare `node.width` with an estimated one-line width:
  - CJK character: about `fontSize`
  - Latin letter or digit: about `fontSize * 0.58`
  - Space or narrow punctuation: about `fontSize * 0.33`
- Flag the node when the estimate is greater than `node.width`, especially when `node.height <= lineHeight + 2`.
- Inspect the screenshot at the target node, not only a scaled full-page screenshot. Small wrapping bugs are easy to miss after downscaling.

## Fix Rules

- Prefer preserving the local component style: widen the parent container or column when the approved scope allows it.
- For label-like text that should hug its content, set `textAutoResize = "WIDTH_AND_HEIGHT"` after loading fonts.
- For text inside a bounded field, keep the text within the parent padding. If needed, widen the field only inside the approved edit area.
- Do not shrink typography below the local pattern or rewrite business copy just to make it fit unless the user explicitly approves.
- If the overflowing node is in a frozen area, report `Needs confirmation` instead of silently editing it.

## use_figma Snippet

Use this read-only snippet after edits. Replace `FRAME_ID` with the modified frame ID.

```js
const frame = await figma.getNodeByIdAsync('FRAME_ID');
if (!frame) throw new Error('Frame not found');

function lineHeightPx(node) {
  if (typeof node.lineHeight === 'object' && node.lineHeight.unit === 'PIXELS') return node.lineHeight.value;
  return Number(node.fontSize) * 1.2;
}

function estimatedOneLineWidth(node) {
  const size = Number(node.fontSize);
  let width = 0;
  for (const ch of node.characters) {
    if (ch === '\n') continue;
    if (/[\u4e00-\u9fff]/.test(ch)) width += size;
    else if (/\s|[.,:;'"`|!()\[\]{}]/.test(ch)) width += size * 0.33;
    else width += size * 0.58;
  }
  return width;
}

const findings = [];
const textNodes = frame.findAll((node) => node.type === 'TEXT');
for (const node of textNodes) {
  const estimate = estimatedOneLineWidth(node);
  const lineHeight = lineHeightPx(node);
  if (node.textAutoResize === 'NONE' && estimate > node.width && node.height <= lineHeight + 2) {
    findings.push({
      id: node.id,
      name: node.name,
      characters: node.characters,
      width: Math.round(node.width),
      height: Math.round(node.height),
      estimatedOneLineWidth: Math.round(estimate),
      lineHeight: Math.round(lineHeight),
      textAutoResize: node.textAutoResize,
    });
  }
}

return { findingCount: findings.length, findings };
```
