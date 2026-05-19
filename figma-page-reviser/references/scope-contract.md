# Scope Contract

Create a short contract before any edit. The user must confirm it.

## Required Fields

- `Target`: Figma file/key, page/frame/node name, and node ID when available.
- `Modification mode`: ask the user to choose `copy frame first` or `directly modify original`.
- `Page type`: record `OST admin/backend`, `OST user/merchant-facing`, or `unclear`.
- `Design standard`: record `ost-admin-system-guidelines`, `ost-user-system-guidelines`, or the exact question that needs user confirmation.
- `Requested changes`: list only what the user explicitly asked for.
- `Allowed area`: node IDs, layer names, or coordinate ranges that may be changed.
- `Frozen area`: areas that must not be changed, especially navigation, sidebar, headers, unrelated cards, unrelated tables, and global styles.
- `Possible impact`: nearby areas that may need adjustment but are not yet approved.
- `Open questions`: ambiguous targets, missing content, unclear page type, or unclear acceptance criteria.

## Contract Template

```text
Modification contract

Target:
- File/frame:
- Node:

Modification mode:
- Please confirm: copy frame first, or directly modify original?

Page type and design standard:
- Page type:
- Standard:

Requested changes:
- R1:
- R2:

Allowed area:
- A1:

Frozen area:
- F1:

Possible impact, not approved yet:
- P1:

Open questions:
- Q1:
```

## Rules

- If the user asks to "just do it" but has not chosen copy vs direct edit, ask again.
- If page type is unclear, ask the user to choose `ost-admin-system-guidelines` or `ost-user-system-guidelines` before editing.
- If URL/domain/app shell clearly indicates OST user/merchant-facing, do not let dense tables alone switch the contract to admin.
- If URL/domain/app shell clearly indicates OST admin/backend, do not use the merchant/user standard just because the requested edit is more spacious or customer-like.
- If the requested change spans multiple unclear regions, split the contract by region.
- If the user names a visible area but not a node, inspect metadata and screenshot before choosing a target.
- If the selected Figma node is too broad, propose a narrower node or coordinate range.
