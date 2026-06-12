---
name: add-pdf-background
description: Add a required JPG/PNG image as the bottom-layer background of one or more PDF templates while preserving existing PDF content, annotations, and AcroForm text fields. Use when the user asks to set an image as a PDF background, keep PDF filenames unchanged, process all PDFs in a specified folder, batch apply a background to PDF templates, or mentions PDF background images, variable boxes, form fields, text boxes, PDF加背景图, JPG作为PDF背景, 不影响文本框, 保留变量框, or 批量处理PDF.
---

# Add PDF Background

## Purpose

Use this skill to place a user-provided raster image behind existing PDF page content without flattening the PDF. This is for PDF templates where visible text, vector lines, annotations, or fillable fields must stay editable and remain above the background.

## Required Inputs

Always require the user to provide a background image path. Do not auto-detect or guess the image.

Require at least one PDF target:

- Explicit PDF files.
- A folder whose immediate `.pdf` files should all receive the same background.
- The current working directory, only when the user's wording clearly refers to "this directory".

## Default Workflow

1. Inspect the target location with `rg --files` when needed.
2. Confirm the background image path is explicit and points to `.jpg`, `.jpeg`, or `.png`.
3. Run the bundled script with either explicit PDF files:

```powershell
python C:\Users\fuweicheng\.codex\skills\add-pdf-background\scripts\add_pdf_background.py --image background.jpg template-a.pdf template-b.pdf
```

Or process all PDFs directly inside a folder:

```powershell
python C:\Users\fuweicheng\.codex\skills\add-pdf-background\scripts\add_pdf_background.py --image background.jpg --pdf-dir C:\path\to\pdf-folder
```

4. Keep generated files in `output/pdf/` unless the user specifies another directory.
5. Keep output PDF filenames identical to the input filenames. Do not overwrite source templates unless the user explicitly asks for that separate destructive workflow.
6. Verify the script output:
   - Page count is unchanged.
   - Annotation count is unchanged.
   - Widget/form-field count is unchanged.
   - Output path is different from input path.
7. For layout-sensitive work, render at least one output PDF page to PNG and inspect it visually.

## Script Behavior

The bundled `scripts/add_pdf_background.py`:

- Requires `--image`; it never guesses the background image.
- Accepts explicit PDF file arguments or `--pdf-dir` for all immediate PDFs in a folder.
- Inserts the image with `overlay=False`, so the image is placed behind existing PDF content.
- Defaults generated files to `output/pdf` under the target folder when `--pdf-dir` is used, or under the current working directory otherwise.
- Preserves original PDF filenames in the output directory.
- Refuses to write output over the input PDF path.
- Checks page count, annotation count, and AcroForm widget count before and after processing.

## Notes

- Prefer PyMuPDF (`fitz`) for this workflow.
- Do not convert the PDF page to an image and redraw text on top. That flattens the template and can destroy editable fields.
- If the background image is the same aspect ratio as the PDF page, use the default full-page stretch. For mismatched assets, ask whether the user wants stretching or proportional placement.
