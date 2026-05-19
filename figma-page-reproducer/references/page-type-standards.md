# Page Type Standards

Detect the page type before applying a design standard. Reproducing the page means preserving what exists; restyling it means choosing the correct rulebook. Mixing them up is how a merchant-facing page wakes up dressed like a back-office table prison.

## Internal Admin / Operations / Backend

Likely internal admin pages usually have:

- dense data tables, filters, batch actions, pagination, approval flows, or operational status tags
- app-shell navigation with sidebar and top header
- management terms such as order management, compliance, declaration, tax, user code, supplier, registration, workflow, audit, or report
- compact forms and repeated table/list operations

When likely internal:

- use `ost-system-guidelines` if available
- keep dense, work-focused layout and existing admin information hierarchy
- verify colors, typography, sidebar/header structure, form controls, table density, buttons, cards, dividers, and status colors against the OST admin standard
- record in QA that `ost-system-guidelines` was selected

## Merchant-Facing / Customer-Facing

Likely merchant-facing pages usually have:

- onboarding, purchase, marketing, service selection, help, account, or guided task language
- explanatory copy, cards, product/service descriptions, pricing, or more spacious layouts
- less dense operations tooling and more customer guidance

When likely merchant-facing:

- do not apply `ost-system-guidelines` by default
- preserve the current page's visual system and density
- ask before converting it to the OST admin standard

## Unclear Page Type

If the page could be internal admin or merchant-facing, ask:

```text
This page could be internal admin or merchant-facing. Should I use `ost-system-guidelines` for the Figma reconstruction QA, or preserve the current page style?
```

## QA Record

Final QA should include:

```text
Page type: internal admin
Design standard: ost-system-guidelines
Checked: layout density, app shell, forms, table styling, button hierarchy, typography, colors, divider artifacts
```
