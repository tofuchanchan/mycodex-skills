#!/usr/bin/env node
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

function usage() {
  console.log(`Usage:
  cdp-page-tools.mjs eval --target-host <host> --expr <js>
  cdp-page-tools.mjs eval --target-host <host> --expr-file <file>
  cdp-page-tools.mjs preprocess-icons-png --target-host <host>
  cdp-page-tools.mjs hide-text --target-host <host> --text <text> [--text <text>] [--min-x 0] [--min-y 0]
  cdp-page-tools.mjs screenshot --target-host <host> --out <png> [--viewport-width 1440] [--viewport-height 900]
  cdp-page-tools.mjs submit-figma-capture --target-host <host> --capture-id <id> --endpoint <url>

Options:
  --cdp-port <port>      Chrome DevTools Protocol port. Default: 9223
  --target-host <host>   Substring used to choose the page tab, e.g. uat-user.evatmaster.com
`);
}

function parseArgs(argv) {
  const command = argv[2];
  const opts = { text: [] };
  for (let i = 3; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg.startsWith("--")) continue;
    const key = arg.slice(2);
    const value = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : "true";
    if (key === "text") opts.text.push(value);
    else opts[key] = value;
  }
  return { command, opts };
}

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status} while fetching ${url}`);
  return response.json();
}

class CdpClient {
  constructor(webSocketUrl) {
    this.nextId = 1;
    this.pending = new Map();
    this.ws = new WebSocket(webSocketUrl);
    this.ws.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (!message.id) return;
      const request = this.pending.get(message.id);
      if (!request) return;
      this.pending.delete(message.id);
      if (message.error) request.reject(new Error(JSON.stringify(message.error)));
      else request.resolve(message.result);
    });
  }

  async ready() {
    if (this.ws.readyState === WebSocket.OPEN) return;
    await new Promise((resolveReady, rejectReady) => {
      this.ws.addEventListener("open", resolveReady, { once: true });
      this.ws.addEventListener("error", rejectReady, { once: true });
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolveSend, rejectSend) => {
      this.pending.set(id, { resolve: resolveSend, reject: rejectSend });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  close() {
    this.ws.close();
  }
}

async function connect(opts) {
  const port = Number(opts["cdp-port"] || process.env.CDP_PORT || 9223);
  const targetHost = opts["target-host"];
  if (!targetHost) throw new Error("--target-host is required");
  const targets = await getJson(`http://127.0.0.1:${port}/json/list`);
  const target =
    targets.find((item) => item.type === "page" && item.url.includes(targetHost)) ||
    targets.find((item) => item.type === "page");
  if (!target?.webSocketDebuggerUrl) {
    throw new Error(`No debuggable page found on port ${port} for host ${targetHost}`);
  }
  const cdp = new CdpClient(target.webSocketDebuggerUrl);
  await cdp.ready();
  await cdp.send("Runtime.enable");
  await cdp.send("Page.enable").catch(() => {});
  return cdp;
}

async function evalExpression(cdp, expression) {
  const result = await cdp.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (result.exceptionDetails) return result;
  return result.result?.value ?? result.result ?? result;
}

function jsString(value) {
  return JSON.stringify(value).replace(/</g, "\\u003c");
}

const preprocessIconsExpression = `(${async function preprocessIconsAsPng() {
  const stats = {
    visibleSvgBefore: 0,
    svgConvertedToPng: 0,
    arrowsConvertedToPng: 0,
    failed: 0,
    blankAfterRasterize: 0,
    visibleSvgAfter: 0,
    pngIconImages: 0,
    samples: [],
  };

  const NS = 'http://www.w3.org/2000/svg';

  function svgDataUrl(source) {
    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(source)
      .replace(/'/g, '%27')
      .replace(/"/g, '%22')}`;
  }

  function waitImage(img) {
    if (img.complete && img.naturalWidth > 0 && img.naturalHeight > 0) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('image decode timeout')), 5000);
      img.onload = () => {
        clearTimeout(timeout);
        resolve();
      };
      img.onerror = () => {
        clearTimeout(timeout);
        reject(new Error('image decode error'));
      };
    });
  }

  function pixelStats(ctx, width, height) {
    const { data } = ctx.getImageData(0, 0, width, height);
    let nonTransparent = 0;
    let nonWhite = 0;
    for (let i = 0; i < data.length; i += 4) {
      const a = data[i + 3];
      if (a > 0) nonTransparent += 1;
      if (a > 0 && !(data[i] > 245 && data[i + 1] > 245 && data[i + 2] > 245)) nonWhite += 1;
    }
    return { nonTransparent, nonWhite };
  }

  async function rasterize(svgSource, width, height) {
    const scale = Math.max(1, window.devicePixelRatio || 1);
    const canvasWidth = Math.max(1, Math.ceil(width * scale));
    const canvasHeight = Math.max(1, Math.ceil(height * scale));
    const img = new Image();
    img.src = svgDataUrl(svgSource);
    await waitImage(img);
    const canvas = document.createElement('canvas');
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    ctx.drawImage(img, 0, 0, canvasWidth, canvasHeight);
    return { url: canvas.toDataURL('image/png'), ...pixelStats(ctx, canvasWidth, canvasHeight) };
  }

  function resolvedSvgSource(svg, width, height) {
    const computed = getComputedStyle(svg);
    const color = computed.color || 'rgb(51, 51, 51)';
    const fill = computed.fill && computed.fill !== 'none' ? computed.fill : color;
    const stroke = computed.stroke && computed.stroke !== 'none' ? computed.stroke : '';
    const use = svg.querySelector('use');
    const ref = use?.getAttribute('href') || use?.getAttribute('xlink:href');
    let clone;

    if (ref && ref.startsWith('#')) {
      const target = document.getElementById(ref.slice(1));
      if (target) {
        clone = document.createElementNS(NS, 'svg');
        clone.setAttribute('xmlns', NS);
        clone.setAttribute('viewBox', target.getAttribute('viewBox') || svg.getAttribute('viewBox') || `0 0 ${width} ${height}`);
        for (const child of [...target.childNodes]) clone.appendChild(child.cloneNode(true));
      }
    }

    if (!clone) {
      clone = svg.cloneNode(true);
      clone.querySelectorAll('use').forEach((node) => {
        const href = node.getAttribute('href') || node.getAttribute('xlink:href');
        const target = href?.startsWith('#') ? document.getElementById(href.slice(1)) : null;
        if (!target) return;
        const group = document.createElementNS(NS, 'g');
        for (const child of [...target.childNodes]) group.appendChild(child.cloneNode(true));
        node.replaceWith(group);
      });
    }

    clone.setAttribute('xmlns', NS);
    clone.setAttribute('width', String(Math.max(1, Math.round(width))));
    clone.setAttribute('height', String(Math.max(1, Math.round(height))));
    if (!clone.getAttribute('viewBox')) clone.setAttribute('viewBox', `0 0 ${Math.max(1, Math.round(width))} ${Math.max(1, Math.round(height))}`);
    clone.setAttribute('fill', fill);
    if (stroke) clone.setAttribute('stroke', stroke);
    clone.style.color = color;
    clone.style.fill = fill;
    clone.style.display = 'block';

    clone.querySelectorAll('*').forEach((node) => {
      if (!(node instanceof Element)) return;
      node.removeAttribute('class');
      const nodeFill = node.getAttribute('fill');
      const nodeStroke = node.getAttribute('stroke');
      if (!nodeFill || nodeFill === 'currentColor' || nodeFill === 'inherit') node.setAttribute('fill', fill);
      if (stroke && (!nodeStroke || nodeStroke === 'currentColor' || nodeStroke === 'inherit')) node.setAttribute('stroke', stroke);
    });

    return new XMLSerializer().serializeToString(clone);
  }

  function arrowSource(color, isOpen) {
    const d = isOpen ? 'M2 7 L5 4 L8 7' : 'M2 3 L5 6 L8 3';
    return `<svg xmlns="${NS}" width="10" height="10" viewBox="0 0 10 10"><path d="${d}" fill="none" stroke="${color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  }

  const visibleSvgs = [...document.querySelectorAll('svg')].filter((svg) => {
    const r = svg.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  });
  stats.visibleSvgBefore = visibleSvgs.length;

  for (const svg of visibleSvgs) {
    try {
      const rect = svg.getBoundingClientRect();
      const width = Math.max(1, rect.width);
      const height = Math.max(1, rect.height);
      const source = resolvedSvgSource(svg, width, height);
      const png = await rasterize(source, width, height);
      if (png.nonTransparent === 0) stats.blankAfterRasterize += 1;
      const img = document.createElement('img');
      img.dataset.codexIconFixed = 'png';
      img.alt = svg.getAttribute('aria-label') || svg.querySelector('use')?.getAttribute('href')?.replace(/^#icon-?/, '') || svg.querySelector('use')?.getAttribute('xlink:href')?.replace(/^#icon-?/, '') || 'icon';
      img.src = png.url;
      img.style.width = `${Math.round(width)}px`;
      img.style.height = `${Math.round(height)}px`;
      img.style.minWidth = `${Math.round(width)}px`;
      img.style.minHeight = `${Math.round(height)}px`;
      img.style.maxWidth = `${Math.round(width)}px`;
      img.style.maxHeight = `${Math.round(height)}px`;
      img.style.display = getComputedStyle(svg).display === 'block' ? 'block' : 'inline-block';
      img.style.verticalAlign = getComputedStyle(svg).verticalAlign || '-0.125em';
      img.style.objectFit = 'contain';
      img.style.flex = '0 0 auto';
      svg.replaceWith(img);
      stats.svgConvertedToPng += 1;
      if (stats.samples.length < 16) {
        stats.samples.push({ alt: img.alt, width: Math.round(width), height: Math.round(height), nonTransparent: png.nonTransparent, nonWhite: png.nonWhite });
      }
    } catch (error) {
      stats.failed += 1;
      if (stats.samples.length < 16) stats.samples.push({ error: error.message });
    }
  }

  for (const arrow of [...document.querySelectorAll('.ant-menu-submenu-arrow')]) {
    try {
      const computed = getComputedStyle(arrow);
      const submenu = arrow.closest('.ant-menu-submenu');
      const isOpen = !!submenu?.className?.includes('open');
      const png = await rasterize(arrowSource(computed.color || 'rgb(51,51,51)', isOpen), 10, 10);
      arrow.dataset.codexIconFixed = 'png';
      arrow.innerHTML = '';
      const img = document.createElement('img');
      img.alt = 'menu arrow';
      img.dataset.codexIconFixed = 'png';
      img.src = png.url;
      img.style.width = '10px';
      img.style.height = '10px';
      img.style.display = 'block';
      arrow.appendChild(img);
      arrow.style.width = '10px';
      arrow.style.height = '10px';
      arrow.style.display = 'inline-flex';
      arrow.style.alignItems = 'center';
      arrow.style.justifyContent = 'center';
      arrow.style.lineHeight = '10px';
      stats.arrowsConvertedToPng += 1;
    } catch {
      stats.failed += 1;
    }
  }

  stats.visibleSvgAfter = [...document.querySelectorAll('svg')].filter((svg) => {
    const r = svg.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }).length;
  stats.pngIconImages = document.querySelectorAll('img[data-codex-icon-fixed="png"]').length;
  return stats;
}.toString()})()`;

function hideTextExpression(texts, minX, minY) {
  return `(${function hideTextInPage(config) {
    const hidden = [];
    const textsToMatch = config.texts || [];
    for (const node of [...document.querySelectorAll('body *')]) {
      const text = (node.innerText || '').trim();
      if (!textsToMatch.some((item) => text.includes(item))) continue;
      const rect = node.getBoundingClientRect();
      if (rect.width < 20 || rect.height < 10) continue;
      if (rect.x < config.minX || rect.y < config.minY) continue;
      node.style.display = 'none';
      hidden.push({
        tag: node.tagName,
        className: String(node.className || ''),
        text: text.slice(0, 100),
        rect: { x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height) },
      });
    }
    return hidden;
  }.toString()})(${jsString({ texts, minX, minY })})`;
}

async function runScreenshot(cdp, opts) {
  const out = opts.out;
  if (!out) throw new Error("--out is required");
  const viewportWidth = Number(opts["viewport-width"] || 1440);
  const viewportHeight = Number(opts["viewport-height"] || 900);
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: viewportWidth,
    height: viewportHeight,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await evalExpression(cdp, "new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))");
  const metrics = await cdp.send("Page.getLayoutMetrics");
  const contentSize = metrics.cssContentSize || metrics.contentSize;
  const width = Math.ceil(Math.max(viewportWidth, contentSize.width));
  const height = Math.ceil(contentSize.height);
  const pageInfo = await evalExpression(cdp, `({
    url: location.href,
    title: document.title,
    devicePixelRatio: window.devicePixelRatio,
    scrollWidth: document.documentElement.scrollWidth,
    scrollHeight: document.documentElement.scrollHeight
  })`);
  const screenshot = await cdp.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: true,
    clip: { x: 0, y: 0, width, height, scale: 1 },
  });
  const outPath = resolve(out);
  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(outPath, Buffer.from(screenshot.data, "base64"));
  return { ...pageInfo, width, height, out: outPath };
}

async function runSubmitFigmaCapture(cdp, opts) {
  const captureId = opts["capture-id"];
  const endpoint = opts.endpoint;
  if (!captureId || !endpoint) throw new Error("--capture-id and --endpoint are required");
  const scriptResponse = await fetch("https://mcp.figma.com/mcp/html-to-design/capture.js");
  if (!scriptResponse.ok) {
    throw new Error(`Failed to fetch Figma capture script: HTTP ${scriptResponse.status}`);
  }
  const captureScript = await scriptResponse.text();
  await evalExpression(cdp, `
    (() => {
      const old = document.querySelector('script[data-codex-figma-capture]');
      if (old) old.remove();
      const el = document.createElement('script');
      el.dataset.codexFigmaCapture = '1';
      el.textContent = ${jsString(captureScript)};
      document.head.appendChild(el);
    })()
  `);
  await evalExpression(cdp, "new Promise(resolve => setTimeout(resolve, 1000))");
  return evalExpression(cdp, `
    window.figma.captureForDesign({
      captureId: ${jsString(captureId)},
      endpoint: ${jsString(endpoint)},
      selector: 'body'
    })
  `);
}

async function main() {
  const { command, opts } = parseArgs(process.argv);
  if (!command || command === "--help" || command === "help") {
    usage();
    return;
  }

  const cdp = await connect(opts);
  try {
    let output;
    if (command === "eval") {
      const expression = opts.expr ?? (opts["expr-file"] ? readFileSync(opts["expr-file"], "utf8") : null);
      if (!expression) throw new Error("--expr or --expr-file is required");
      output = await evalExpression(cdp, expression);
    } else if (command === "preprocess-icons-png") {
      output = await evalExpression(cdp, preprocessIconsExpression);
    } else if (command === "hide-text") {
      if (!opts.text.length) throw new Error("At least one --text is required");
      output = await evalExpression(cdp, hideTextExpression(opts.text, Number(opts["min-x"] || 0), Number(opts["min-y"] || 0)));
    } else if (command === "screenshot") {
      output = await runScreenshot(cdp, opts);
    } else if (command === "submit-figma-capture") {
      output = await runSubmitFigmaCapture(cdp, opts);
    } else {
      throw new Error(`Unknown command: ${command}`);
    }
    console.log(JSON.stringify(output, null, 2));
  } finally {
    cdp.close();
  }
}

main().catch((error) => {
  console.error(error?.stack || String(error));
  process.exit(1);
});
