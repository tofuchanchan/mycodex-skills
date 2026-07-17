#!/usr/bin/env python3
"""Validate a visual-knowledge-explainer output directory using stdlib only."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|PLACEHOLDER|LOREM IPSUM)\b", re.IGNORECASE)
REMOTE_SCHEMES = {"http", "https"}


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for attr in ("src", "href", "poster"):
            value = values.get(attr)
            if value:
                self.refs.append((f"{tag}[{attr}]", value.strip()))


def parse_modes(raw: str) -> set[str]:
    modes = {item.strip() for item in raw.split(",") if item.strip()}
    if "all" in modes:
        modes.update({"html-bundle", "single-html", "pdf"})
        modes.discard("all")
    allowed = {"html-bundle", "single-html", "pdf"}
    unknown = modes - allowed
    if unknown:
        raise ValueError(f"unknown modes: {', '.join(sorted(unknown))}")
    return modes or {"html-bundle"}


def local_reference(value: str) -> bool:
    if value.startswith(("#", "data:", "mailto:", "tel:", "javascript:")):
        return False
    return urlparse(value).scheme not in REMOTE_SCHEMES


def validate_html(path: Path, root: Path, offline: bool, single: bool) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    if "<html" not in text.lower() or "</html>" not in text.lower():
        errors.append(f"{path.name}: not a complete HTML document")
    if PLACEHOLDER_RE.search(text):
        errors.append(f"{path.name}: contains unresolved placeholder text")

    parser = AssetParser()
    parser.feed(text)
    for kind, value in parser.refs:
        parsed = urlparse(value)
        if parsed.scheme in REMOTE_SCHEMES:
            if offline or single:
                errors.append(f"{path.name}: remote dependency in {kind}: {value}")
            continue
        if not local_reference(value):
            continue
        clean = unquote(value.split("#", 1)[0].split("?", 1)[0])
        if not clean:
            continue
        candidate = (path.parent / clean).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{path.name}: asset escapes output directory: {value}")
            continue
        if not candidate.exists():
            errors.append(f"{path.name}: missing asset for {kind}: {value}")
    return errors


def validate_diagram_pairs(root: Path) -> list[str]:
    errors: list[str] = []
    for source in root.rglob("*.excalidraw"):
        if not source.with_suffix(".png").exists():
            errors.append(f"missing PNG render for diagram: {source.relative_to(root)}")
    return errors


def validate_output(root: Path, modes: set[str], offline: bool) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"output directory does not exist: {root}"]

    for required in ("explanation-brief.yaml", "qa-report.md"):
        path = root / required
        if not path.is_file():
            errors.append(f"missing required file: {required}")
        elif PLACEHOLDER_RE.search(path.read_text(encoding="utf-8", errors="replace")):
            errors.append(f"{required}: contains unresolved placeholder text")

    if "html-bundle" in modes:
        index = root / "index.html"
        if not index.is_file():
            errors.append("missing bundle entry: index.html")
        else:
            errors.extend(validate_html(index, root, offline, single=False))

    if "single-html" in modes:
        singles = sorted(root.glob("*.single.html"))
        if not singles:
            errors.append("missing single-file HTML: *.single.html")
        for single in singles:
            errors.extend(validate_html(single, root, offline=True, single=True))

    if "pdf" in modes:
        pdfs = sorted(root.glob("*.pdf"))
        if not pdfs:
            errors.append("missing PDF: *.pdf")
        for pdf in pdfs:
            if pdf.stat().st_size < 1024:
                errors.append(f"{pdf.name}: PDF is suspiciously small")
            elif pdf.read_bytes()[:5] != b"%PDF-":
                errors.append(f"{pdf.name}: invalid PDF header")

    errors.extend(validate_diagram_pairs(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--modes", default="html-bundle")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    try:
        modes = parse_modes(args.modes)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 2

    errors = validate_output(args.output_dir.resolve(), modes, args.offline)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {args.output_dir} ({', '.join(sorted(modes))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

