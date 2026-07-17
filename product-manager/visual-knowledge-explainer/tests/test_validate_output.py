from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_output.py"
SPEC = importlib.util.spec_from_file_location("validate_output", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ValidateOutputTests(unittest.TestCase):
    def make_base(self, root: Path) -> None:
        (root / "explanation-brief.yaml").write_text("brief_version: 1\n", encoding="utf-8")
        (root / "qa-report.md").write_text("# QA Report\n\nPASS\n", encoding="utf-8")

    def test_valid_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.make_base(root)
            (root / "assets").mkdir()
            (root / "assets" / "diagram.png").write_bytes(b"png")
            (root / "index.html").write_text(
                '<!doctype html><html><body><img src="assets/diagram.png"></body></html>',
                encoding="utf-8",
            )
            self.assertEqual([], MODULE.validate_output(root, {"html-bundle"}, offline=True))

    def test_missing_asset_and_remote_single_file_fail(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.make_base(root)
            (root / "index.html").write_text(
                '<!doctype html><html><body><img src="missing.png"></body></html>',
                encoding="utf-8",
            )
            (root / "topic.single.html").write_text(
                '<!doctype html><html><head><script src="https://example.com/a.js"></script></head><body></body></html>',
                encoding="utf-8",
            )
            errors = MODULE.validate_output(root, {"html-bundle", "single-html"}, offline=True)
            self.assertTrue(any("missing asset" in error for error in errors))
            self.assertTrue(any("remote dependency" in error for error in errors))

    def test_excalidraw_requires_png_pair(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.make_base(root)
            (root / "index.html").write_text(
                "<!doctype html><html><body></body></html>", encoding="utf-8"
            )
            (root / "main.excalidraw").write_text("{}", encoding="utf-8")
            errors = MODULE.validate_output(root, {"html-bundle"}, offline=False)
            self.assertTrue(any("missing PNG render" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

