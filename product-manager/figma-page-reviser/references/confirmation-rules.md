# Confirmation Rules

Use this when proposing inferred completion work that the user did not explicitly request.

## Suggestion Categories

`Must confirm`

- Adds, removes, or renames fields.
- Changes business logic, workflow, validation, permissions, prices, tax/accounting concepts, status names, or button meaning.
- Changes navigation, page hierarchy, global layout, or repeated components outside the edit area.
- Applies a design standard that differs from the recorded page type standard.
- Switches between `ost-admin-system-guidelines` and `ost-user-system-guidelines`, or applies either standard while page type is still unclear.

`Should confirm`

- Adds empty, loading, error, disabled, success, permission, or long-text states.
- Adds helper text, warnings, examples, or tooltips.
- Changes responsive behavior or scroll behavior.
- Adjusts a nearby section to make the requested change fit.

`Visual repair`

- Fixes overflow, local alignment, local spacing, icon color, crop, clipping, or layer order inside the already-approved area.
- Keeps the same meaning and same component style.

## Approval Format

List suggestions as IDs:

```text
Suggested completions

S1 [Must confirm]: Add an empty state for the revised table.
S2 [Should confirm]: Add a validation message below the new field.
S3 [Visual repair]: Align the revised buttons to the existing 8px spacing rhythm.

Please approve by ID, for example: "Approve S1 and S3; skip S2."
```

## Execution Rules

- Execute only approved IDs.
- Do not treat a requested visual polish as permission to switch admin/user standards. Standard switching requires explicit approval.
- If an approved suggestion reveals a new dependency, stop and ask again.
- If the user approves a vague group such as "all reasonable ones", restate the exact IDs and ask for confirmation.
- Visual repairs may be bundled only when they are entirely inside the approved area and do not alter meaning.
