# Page Type Detection

Detect the page type before applying a design standard.

## Internal Admin / Operations / Backend

Likely internal when the page contains:

- Admin, backend, operations, staff, reviewer, RPA, file distribution, audit, approval, declaration records, task queue, or permission-management language.
- Dense data tables, filters, tabs, drawer/detail panels, bulk actions, status tracking, or manual processing workflows.
- User audience is internal employees, finance/operation staff, customer service, delivery teams, or administrators.

When likely internal, use `ost-system-guidelines` if available. Preserve existing page density and system style.

## Merchant-Facing / Customer-Facing

Likely merchant-facing when the page contains:

- Store, authorization, VAT/EPR declaration submission, upload report, tax number validation, invoice upload, payment, renewal, service purchase, or customer guidance language.
- User audience is merchants, sellers, customers, or external users.
- More explanatory copy, guided flows, warnings, and form validation are visible.

When likely merchant-facing, do not apply `ost-system-guidelines` by default. Match the current page's visual system and ask before introducing a new standard.

## Unclear

Ask the user:

```text
This page could be internal admin or merchant-facing. Which standard should I use for review and revisions?
```

Do not guess when the visual/design standard affects component choices, density, or copy tone.
