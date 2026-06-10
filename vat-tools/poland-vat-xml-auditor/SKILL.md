---
name: poland-vat-xml-auditor
description: Use this skill whenever the user asks to inspect, validate, reconcile, classify, or audit Polish VAT XML files, especially JPK_V7M and VAT-UE files. This skill is for checking XML format and naming issues, extracting cross-border B2B sales, cross-border B2B purchases, B2B transfer exports, B2B transfer imports, reconciling JPK_V7M against VAT-UE, and producing Polish VAT risk findings. Always use this skill for folders containing Polish VAT XML files or prompts mentioning K_21, K_23, K_24, K_42, K_43, Grupa1, Grupa2, WDT, WNT, VAT-UE, or JPK_V7M.
---

# Poland VAT XML Auditor

Audit Polish VAT XML packages containing a JPK_V7M file and a VAT-UE file. The goal is to produce a practical Chinese audit report that identifies file issues, extracts cross-border B2B and transfer transactions, reconciles the two XML files, and flags tax/reporting risks.

## Inputs

Accept one of:
- A folder containing XML files.
- Explicit paths to one JPK_V7M XML and one VAT-UE XML.
- Optional configuration JSON with taxpayer context:
  - `taxpayer_nip`
  - `period`
  - `own_vat_ids`
  - `own_company_aliases` optional; aliases help review but do not confirm transfer
  - `vat_rate`, default `0.23`
  - `rounding_tolerance_pln`, default `1`

## Required Own VAT Gate

At the start of every skill invocation, ask the user whether the taxpayer has existing EU VAT registrations outside Poland, unless the current user message already answers this exact question.

Do not rely on:
- previous conversation context
- previous audit outputs
- existing config files
- remembered customer facts
- filenames or company names

This gate is per-run. A config file can provide VAT ID details, but it cannot prove the user answered the question for the current execution.

If yes, require country code + VAT ID. Company name or alias is optional and can be omitted.

Preferred format:

```text
DE: 888888888
CZ: 88888888
ES: N8888888J
```

Optional alias format:

```text
DE: 888888888, FAKE VAT DEMO GMBH
```

If the user provides only company names and no VAT IDs, treat the own-VAT gate as unresolved. Company names alone cannot confirm transfer.

Do not infer "no other EU VAT registrations" from silence. The gate is resolved only when the user either:
- provides at least one non-PL own EU VAT ID, or
- explicitly says there are no non-PL own EU VAT registrations.

If the user has not answered this gate, ask the question and stop. Do not run the audit script yet.

When no non-PL own VAT IDs are provided:
- Do not classify transactions as confirmed transfer exports or confirmed transfer imports based only on company name.
- Classify non-PL `K_21` rows as cross-border B2B sales unless explicit user-provided evidence proves transfer.
- Classify `K_23/K_24` plus `K_42/K_43` rows as cross-border B2B purchases unless explicit user-provided evidence proves transfer.
- If counterparty name resembles the taxpayer name but no matching own VAT ID was configured, create a P2 finding for possible missing own-VAT configuration.

Always state the own-VAT assumption in the report. VAT ID is the primary transfer evidence; company name is only supporting evidence.

## Official Schema Sources

Use the official schema version indicated by the XML file whenever possible. For the current supported schemas:

- JPK_V7M (3), namespace `http://crd.gov.pl/wzor/2025/12/19/14090/`, schema: `https://crd.gov.pl/wzor/2025/12/19/14090/schemat.xsd`
- VAT-UE (5), namespace `http://crd.gov.pl/wzor/2021/01/12/10293/`, schema: `https://crd.gov.pl/wzor/2021/01/12/10293/schemat.xsd`

If an XML file uses a different namespace or form variant, flag a P2 finding that the skill's field reference may need updating against that file's official schema.

## Workflow

1. Locate XML files.
2. Parse XML with namespace-aware parsing.
3. Identify file types from XML content, not filenames:
   - JPK_V7M: root `JPK`, form code containing `JPK_V7M`.
   - VAT-UE: root `Deklaracja`, form code containing `VAT-UE`.
4. Validate basic structure, period, taxpayer NIP, and filename consistency.
5. Extract JPK_V7M rows:
   - `SprzedazWiersz`
   - `ZakupWiersz`
   - declaration summary fields
   - control totals
6. Extract VAT-UE groups:
   - `Grupa1`: intra-Community supplies
   - `Grupa2`: intra-Community acquisitions
   - `Grupa3`: intra-Community services
   - `Grupa4`: call-off stock movements
7. Classify transactions into:
   - cross-border B2B sales
   - cross-border B2B purchases
   - B2B transfer exports
   - B2B transfer imports
   - possible transfers needing human confirmation
8. Reconcile JPK_V7M and VAT-UE.
9. Produce a Chinese report with findings sorted by severity.

## Preferred Script

Use `scripts/audit_poland_vat_xml.py` for deterministic parsing and reconciliation. Run it before writing the final explanation when local files are available.

Example:

```powershell
python poland-vat-xml-auditor\scripts\audit_poland_vat_xml.py `
  --input . `
  --own-vat-status provided `
  --config own_vat_config.json `
  --output-dir audit-output
```

The script creates an archive subfolder under `--output-dir` using:

```text
PL{tax_number}_{reporting_period}_{YYYYMMDD}_{incrementing_id}
```

Example:

```text
audit-output/PL8888888888_2026-04_20260610_001/
```

If no config file exists and the user explicitly confirms there are no non-PL own EU VAT registrations, run:

```powershell
python poland-vat-xml-auditor\scripts\audit_poland_vat_xml.py --input . --own-vat-status none --output-dir audit-output
```

Then explain clearly that the run used the user's explicit "no non-PL own EU VAT registrations" answer.

The script intentionally refuses to run without an explicit per-run `--own-vat-status` value. A config containing VAT IDs is not enough by itself. If it exits with the unresolved-gate error, ask the user the gate question instead of bypassing it.

## Classification Rules

### Cross-Border B2B Sales

Classify as cross-border B2B sale when:
- Source is `SprzedazWiersz`.
- `KodKrajuNadaniaTIN` is an EU country other than `PL`.
- Row has `K_21`.
- Counterparty is not recognized as the taxpayer's own VAT ID.
- The row is not confirmed transfer based on configured own VAT IDs.

Match to VAT-UE `Grupa1`.

### Cross-Border B2B Purchases

Classify as cross-border B2B purchase when:
- JPK has output VAT side in `SprzedazWiersz` with `K_23/K_24`.
- JPK has input VAT side in `ZakupWiersz` with `K_42/K_43`, or `K_40/K_41` for fixed assets.
- Supplier country is an EU country other than `PL`.
- Supplier is not recognized as the taxpayer's own VAT ID.

Match to VAT-UE `Grupa2`.

### B2B Transfer Export

Classify as confirmed transfer export only when:
- Source is `SprzedazWiersz`.
- Row has `K_21`.
- Country is a non-PL EU country.
- Counterparty VAT ID matches configured `own_vat_ids` for that country.

Supporting signals such as own company name, `DowodSprzedazy=BRAK`, `WEW`, or internal document numbers can raise confidence, but they cannot confirm transfer without a configured own VAT ID.

Match to VAT-UE `Grupa1`.

### B2B Transfer Import

Classify as confirmed transfer import only when:
- JPK has `SprzedazWiersz` with `K_23/K_24`.
- JPK has matching `ZakupWiersz` with `K_42/K_43` or `K_40/K_41`.
- Counterparty VAT ID matches configured `own_vat_ids` for that country.

Match to VAT-UE `Grupa2`.

### Possible Transfer

Classify as possible transfer, not confirmed transfer, when:
- Company name resembles the taxpayer's name, or document number is internal/missing, but no configured own VAT ID matches.
- The user has not supplied own non-PL VAT IDs.

Report these as P2 findings requiring human confirmation.

## VAT-UE Field Rules

Use official VAT-UE group meanings:

| Group | Meaning | Official fields |
|---|---|---|
| `Grupa1` | intra-Community supplies | `P_Da/P_Db/P_Dc/P_Dd` |
| `Grupa2` | intra-Community acquisitions | `P_Na/P_Nb/P_Nc/P_Nd` |
| `Grupa3` | intra-Community services | `P_Ua/P_Ub/P_Uc` |
| `Grupa4` | call-off stock | `P_Ca/P_Cb/...` |

If `Grupa2` uses `P_Da/P_Db/P_Dc/P_Dd`, flag it as a schema risk even if values can be read for diagnostic purposes.

## Reconciliation Rules

Compare:
- JPK `K_21` by country + VAT ID against VAT-UE `Grupa1`.
- JPK `K_23` by country + VAT ID against VAT-UE `Grupa2`.
- JPK `K_23/K_24` against `ZakupWiersz` `K_42/K_43` or `K_40/K_41`.
- Declaration fields `P_21`, `P_23`, `P_24`, `P_42`, `P_43` against row totals.
- Control totals against row totals.

Use configurable rounding tolerance for VAT-UE amounts because VAT-UE commonly reports whole PLN values.

## Findings

Use severity:
- `P0`: XML cannot be parsed, file type cannot be identified, or schema-critical structure is broken.
- `P1`: Missing transaction, mismatched VAT ID, mismatched amount, missing VAT-UE counterpart, or JPK output/input mismatch.
- `P2`: Suspicious classification, missing own VAT configuration, unusual document number, negative amount, or possible transfer.
- `P3`: Naming issue, cosmetic issue, low-risk warning.

## Output

Always produce:
1. Executive summary.
2. File identification.
3. Own-VAT assumption.
4. Extracted transaction tables.
5. JPK vs VAT-UE reconciliation.
6. JPK internal reconciliation.
7. Risk findings sorted by severity.
8. Recommended fixes.

The report summary must explicitly show the Polish tax number, reporting period, and taxpayer name. CSV outputs must use Chinese reader-facing status descriptions, especially the transaction confidence column.

Prefer Chinese output unless the user asks otherwise.

When a script was run, cite the generated files and summarize the highest-risk findings. Do not dump the entire JSON unless the user asks for raw output.
