---
name: dingtalk-doc-mcp-guidelines
description: Use whenever Codex reads, writes, overwrites, appends, or updates DingTalk/Alidocs online documents through the dingtalk-doc MCP, including dingtalkdoc requests, alidocs.dingtalk.com URLs, document frameworks, PRDs, headings, tables, block updates, JsonML structure, numbering, or formatting. Requires MCP-first operation, JsonML-aware writes, preservation of existing document structure, and post-write verification; never use browser or web UI simulation for DingTalk document writes unless the user explicitly asks for that fallback.
---

# DingTalk Doc MCP Guidelines

## Core Rules

- Use the dingtalk-doc MCP for DingTalk document reading and writing. Do not use browser automation, web UI simulation, copy-paste automation, or Playwright/Chrome fallbacks for document writes unless the user explicitly asks for that fallback after MCP options are exhausted.
- Extract the document id from the Alidocs URL and confirm the target with `get_document_info` before writing.
- Prefer structure-aware operations. Use `list_document_blocks(format="jsonml")` before formatting-sensitive edits, and use JsonML for headings, numbered sections, tables, rich text, or partial block updates.
- Preserve existing user content and block ids. When repairing or updating a block, keep its `uuid` unless a new block is genuinely being inserted.
- Verify after every write with the most structure-relevant readback, usually `list_document_blocks(format="jsonml")` for formatting and `get_document_content` for plain content.

## Default Workflow

1. Identify the target document id from the DingTalk/Alidocs URL.
2. Call `get_document_info` and confirm the document is the expected target.
3. For read-only summaries, use `get_document_content` first, then `list_document_blocks(format="jsonml")` if structure matters.
4. For writes, inspect existing structure with `list_document_blocks(format="jsonml")` before generating payloads.
5. Choose the narrowest write operation available:
   - Use whole-document update only when replacing or creating the full skeleton is intended.
   - Use block update or insertion when editing a specific section.
6. Use JsonML for formatting-sensitive content. Markdown is acceptable only for simple plain text where exact DingTalk structure does not matter.
7. After writing, verify the resulting structure and content. Report any MCP limitation or unverifiable formatting explicitly.

## Numbered Headings

When writing DingTalk document content with the dingtalk-doc MCP, do not use Markdown text such as `# 1. Background` to create numbered headings.

That only writes the number into the title text. It is not DingTalk's structured project-numbering format, will not reliably auto-renumber, and can break the expected heading hierarchy.

Use JsonML heading blocks with a `list` object when the document needs numbered headings.

### Required Numbering Workflow

1. Inspect existing heading blocks with `list_document_blocks(format="jsonml")`.
2. If the document already contains a correct numbered heading, reuse its `list.listId`, `listStyleType`, `listStyle`, `symbolStyle`, and level pattern.
3. If no sample exists, create a new shared `listId` for the document or operation, for example `heading-auto-<short-id>`.
4. Keep heading text clean. Put only the title text in the heading, such as `Background`; never include `1. `, `2. `, or `3.1 ` in the text.
5. Verify the result with `list_document_blocks(format="jsonml")`, not Markdown export.

### Generic Heading Pattern

Use the same `listId` for all headings in one numbering system.

Level 1 heading:

```json
["h1", {
  "uuid": "block-id-or-generated-id",
  "ind": {"hanging": 0, "left": 0},
  "list": {
    "listId": "heading-auto-main",
    "level": 0,
    "isTaskList": false,
    "isOrdered": true,
    "listStyleType": "DEC_DEC_DEC_P",
    "symbolStyle": {"sz": 21, "bold": true},
    "listStyle": {"format": "decimal", "text": "%1", "align": "left"},
    "autoLevel": true
  }
}, ["span", {"data-type": "text"}, ["span", {"bold": true, "data-type": "leaf"}, "Background"]]]
```

Level 2 heading:

```json
["h2", {
  "uuid": "block-id-or-generated-id",
  "ind": {"hanging": 0, "left": 0},
  "list": {
    "listId": "heading-auto-main",
    "level": 1,
    "isTaskList": false,
    "isOrdered": true,
    "listStyleType": "DEC_DEC_DEC_P",
    "symbolStyle": {"sz": 17, "bold": true},
    "listStyle": {"format": "decimal", "text": "%1.%2", "align": "left"},
    "autoLevel": true
  }
}, ["span", {"data-type": "text"}, ["span", {"bold": true, "data-type": "leaf"}, "Overview"]]]
```

Level 3 heading list object:

```json
{
  "listId": "heading-auto-main",
  "level": 2,
  "isTaskList": false,
  "isOrdered": true,
  "listStyleType": "DEC_DEC_DEC_P",
  "symbolStyle": {"sz": 15, "bold": true},
  "listStyle": {"format": "decimal", "text": "%1.%2.%3", "align": "left"},
  "autoLevel": true
}
```

## Repairing Bad Heading Numbering

When a document has fake numbered headings, repair them by updating the heading block's JsonML:

- Convert the block to `h1`, `h2`, or `h3` with a real `list` object.
- Remove the numeric prefix from the heading text.
- Keep the same `uuid` when updating an existing block.
- If a duplicate fake heading exists beside a correct heading, convert the duplicate to an empty paragraph or delete it only when a safe delete operation is available and the deletion target is unambiguous.

## Verification Checklist

After writing or repairing a DingTalk document, confirm:

- The target document id matches the requested URL.
- Expected headings, paragraphs, tables, and blocks exist after the write.
- Numbered heading blocks have `list.isOrdered=true`.
- Heading blocks in the same numbering system share the same `listId`.
- `h1` headings use `level: 0` and `listStyle.text: "%1"`.
- `h2` headings use `level: 1` and `listStyle.text: "%1.%2"`.
- Visible heading text does not contain hand-written numbering.
- No unrelated user content was overwritten.

Markdown export may omit auto-generated numbers. Do not use Markdown output alone to verify structured numbering; use JsonML block structure.
