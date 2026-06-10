# Classification Rules

Use this reference when explaining why a row was classified as B2B sale, B2B purchase, transfer export, or transfer import.

## Evidence Priority

1. Configured own EU VAT ID match: strongest evidence for transfer.
2. Country + VAT ID + amount reconciliation between JPK and VAT-UE.
3. Company name alias: supporting evidence only.
4. Internal or missing document number such as `BRAK` or `WEW`: supporting evidence only.

Never confirm transfer classification from company name alone.

## Own VAT Configuration

Ask the user to provide all non-PL EU VAT registrations before confirming transfer rows.

Required data for confirmed transfer identification:

- Country code
- VAT ID

Optional data:

- Company name aliases

Company aliases help identify possible transfer rows for manual review, but they do not replace VAT IDs.

Do not infer that the taxpayer has no non-PL EU VAT registrations from silence. The gate is resolved only when the current user request provides non-PL own VAT IDs or explicitly confirms that none exist. If the gate is unresolved, stop and ask the user before running the audit.

Do not use prior conversation context, previous reports, or config files to satisfy this gate. A config file can provide VAT ID details after the user confirms there are other EU VAT registrations, but it cannot replace the per-run question.

After the user explicitly confirms no non-PL own VAT IDs, default ambiguous rows to ordinary B2B categories and flag possible transfers as P2 for review.

Example config:

```json
{
  "taxpayer_nip": "8888888888",
  "period": "2026-04",
  "own_company_aliases": [
    "FAKE VAT DEMO GMBH",
    "DEMO EU TRADING GMBH"
  ],
  "own_vat_ids": {
    "DE": ["888888888"],
    "CZ": ["88888888"],
    "ES": ["N8888888J"],
    "FR": ["88888888888"],
    "IT": ["88888888888"]
  },
  "vat_rate": "0.23",
  "rounding_tolerance_pln": "1"
}
```

## Cross-Border B2B Sale

Classify as ordinary cross-border B2B sale when:

- JPK row is `SprzedazWiersz`.
- Country is an EU country other than `PL`.
- Row has `K_21`.
- VAT ID does not match configured own VAT IDs.

VAT-UE counterpart should be `Grupa1`.

## Cross-Border B2B Purchase

Classify as ordinary cross-border B2B purchase when:

- JPK output side has `SprzedazWiersz/K_23` and `K_24`.
- JPK input side has matching `ZakupWiersz/K_42` and `K_43`, or fixed-asset `K_40` and `K_41`.
- VAT ID does not match configured own VAT IDs.

VAT-UE counterpart should be `Grupa2`.

## Transfer Export

Classify as confirmed transfer export only when:

- JPK row has `K_21`.
- Country is a non-PL EU country.
- Counterparty VAT ID matches configured own VAT IDs for that country.

VAT-UE counterpart should be `Grupa1`.

## Transfer Import

Classify as confirmed transfer import only when:

- JPK output side has `K_23/K_24`.
- JPK input side has matching `K_42/K_43` or `K_40/K_41`.
- Counterparty VAT ID matches configured own VAT IDs for that country.

VAT-UE counterpart should be `Grupa2`.

## Common Risks

- JPK has K_21 but VAT-UE Grupa1 has no counterpart.
- JPK has K_23 but VAT-UE Grupa2 has no counterpart.
- VAT-UE has counterpart but JPK country/VAT ID differs.
- JPK WNT output side exists without input deduction, or input deduction exists without output side.
- `Grupa2` uses `P_Da/P_Db/P_Dc/P_Dd`.
- Company name suggests own company but own VAT ID was not configured.
- Negative cross-border amount lacks clear correction/credit-note explanation.
