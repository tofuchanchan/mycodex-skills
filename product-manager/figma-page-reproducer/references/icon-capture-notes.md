# Icon Capture Notes

## Why Icons Disappear

Many enterprise web apps render icons through SVG sprites:

```html
<svg><use href="#icon-goumaizhinan1"></use></svg>
<symbol id="icon-goumaizhinan1" viewBox="0 0 1024 1024">
  <path d="..." />
</symbol>
```

Figma HTML capture may serialize only the visible `<svg>` and lose the hidden `<symbol>`. The result is an empty image frame in Figma. Converting the visible SVG to a `data:image/svg+xml` URL is not enough if the serialized SVG still contains unresolved `<use>` references.

## Reliable Fix

Before capture:

1. Find every visible `svg`.
2. If it contains `<use href="#id">`, find `document.getElementById(id)`.
3. Build a standalone SVG using the symbol children.
4. Copy computed `fill`, `stroke`, and `color`.
5. Draw the standalone SVG into a canvas.
6. Replace the icon with a PNG `<img>`.

Validate rasterization with pixel stats:

- `nonTransparent > 0` means something was drawn.
- `nonWhite = 0` can still be valid for a white icon sitting on a colored background.
- `blankAfterRasterize = 0` is the target.

## Ant Design Arrows

Ant Design submenu arrows can be CSS pseudo-elements or tiny rotated borders. Replace them with a simple standalone arrow SVG and rasterize to PNG. This is usually more faithful than hoping the capture tool understands pseudo-elements.

## Review Rule

Always call `get_screenshot` on the captured Figma frame and inspect it. Metadata that says `imageFillNodes > 0` does not prove icons are visible; empty PNGs still count as image fills. Trust pixels, not vibes.
