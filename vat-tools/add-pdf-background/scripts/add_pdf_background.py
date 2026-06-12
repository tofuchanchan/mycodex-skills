from __future__ import annotations

import argparse
from pathlib import Path

import fitz


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def list_pdf_dir(pdf_dir: Path) -> list[Path]:
    if not pdf_dir.exists():
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")
    if not pdf_dir.is_dir():
        raise NotADirectoryError(f"PDF directory is not a directory: {pdf_dir}")

    return sorted(path for path in pdf_dir.glob("*.pdf") if path.is_file())


def count_annots(pdf_path: Path) -> int:
    total = 0
    with fitz.open(pdf_path) as doc:
        for page in doc:
            total += len(list(page.annots() or []))
    return total


def count_widgets(pdf_path: Path) -> int:
    total = 0
    with fitz.open(pdf_path) as doc:
        for page in doc:
            total += len(list(page.widgets() or []))
    return total


def page_count(pdf_path: Path) -> int:
    with fitz.open(pdf_path) as doc:
        return doc.page_count


def add_background(
    pdf_path: Path,
    image_path: Path,
    output_path: Path,
    keep_proportion: bool,
) -> None:
    with fitz.open(pdf_path) as doc:
        for page in doc:
            page.insert_image(
                page.rect,
                filename=str(image_path),
                overlay=False,
                keep_proportion=keep_proportion,
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(output_path, garbage=4, deflate=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add a required JPG/PNG image as a non-destructive PDF background."
    )
    parser.add_argument(
        "pdfs",
        nargs="*",
        help="PDF templates. Use this or --pdf-dir.",
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Required background image path. Supported: JPG, JPEG, PNG.",
    )
    parser.add_argument(
        "--pdf-dir",
        help="Process all immediate PDF files in this directory.",
    )
    parser.add_argument(
        "--output-dir",
        help=(
            "Directory for generated PDFs. Defaults to output/pdf under --pdf-dir, "
            "or output/pdf under the current working directory."
        ),
    )
    parser.add_argument(
        "--keep-proportion",
        action="store_true",
        help="Keep the image aspect ratio instead of stretching it to the full page.",
    )
    return parser.parse_args()


def resolve_pdf_paths(args: argparse.Namespace) -> tuple[list[Path], Path]:
    if args.pdf_dir and args.pdfs:
        raise ValueError("Use either --pdf-dir or explicit PDF files, not both.")

    if args.pdf_dir:
        base_dir = Path(args.pdf_dir)
        return list_pdf_dir(base_dir), base_dir

    if args.pdfs:
        return [Path(path) for path in args.pdfs], Path.cwd()

    return list_pdf_dir(Path.cwd()), Path.cwd()


def validate_unique_outputs(pdf_paths: list[Path], output_dir: Path) -> None:
    seen: dict[Path, Path] = {}
    for pdf_path in pdf_paths:
        output_path = (output_dir / pdf_path.name).resolve()
        existing_input = seen.get(output_path)
        if existing_input is not None and existing_input.resolve() != pdf_path.resolve():
            raise ValueError(
                "Multiple input PDFs would write to the same output filename: "
                f"{existing_input} and {pdf_path}"
            )
        seen[output_path] = pdf_path


def main() -> None:
    args = parse_args()
    image_path = Path(args.image)
    pdf_paths, default_output_base = resolve_pdf_paths(args)
    output_dir = Path(args.output_dir) if args.output_dir else default_output_base / "output" / "pdf"

    if not image_path.exists():
        raise FileNotFoundError(f"Background image not found: {image_path}")
    if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError(f"Unsupported image type: {image_path.suffix}")
    if not pdf_paths:
        raise FileNotFoundError("No PDF files found.")

    validate_unique_outputs(pdf_paths, output_dir)

    for pdf_path in pdf_paths:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        if not pdf_path.is_file():
            raise ValueError(f"PDF path is not a file: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"Not a PDF file: {pdf_path}")

        output_path = output_dir / pdf_path.name
        if output_path.resolve() == pdf_path.resolve():
            raise ValueError(
                "Output path is the same as input path. "
                "Use a different --output-dir to avoid overwriting the template."
            )

        before_pages = page_count(pdf_path)
        before_annots = count_annots(pdf_path)
        before_widgets = count_widgets(pdf_path)
        add_background(pdf_path, image_path, output_path, args.keep_proportion)
        after_pages = page_count(output_path)
        after_annots = count_annots(output_path)
        after_widgets = count_widgets(output_path)

        if before_pages != after_pages:
            raise RuntimeError(
                f"Page count changed for {pdf_path.name}: {before_pages} -> {after_pages}"
            )
        if before_annots != after_annots:
            raise RuntimeError(
                f"Annotation count changed for {pdf_path.name}: {before_annots} -> {after_annots}"
            )
        if before_widgets != after_widgets:
            raise RuntimeError(
                f"Widget count changed for {pdf_path.name}: {before_widgets} -> {after_widgets}"
            )

        print(
            f"{pdf_path.name} -> {output_path} "
            f"(pages: {before_pages} -> {after_pages}, "
            f"annots: {before_annots} -> {after_annots}, "
            f"widgets: {before_widgets} -> {after_widgets})"
        )


if __name__ == "__main__":
    main()
