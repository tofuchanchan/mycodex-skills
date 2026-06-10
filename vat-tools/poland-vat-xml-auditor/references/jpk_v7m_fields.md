# JPK_V7M Field Reference

Use this reference when explaining findings from the JPK_V7M main XML.

Official basis for the currently supported file variant:

- JPK_V7M (3)
- Namespace: `http://crd.gov.pl/wzor/2025/12/19/14090/`
- Schema: `https://crd.gov.pl/wzor/2025/12/19/14090/schemat.xsd`

If the file declares a different namespace or form variant, verify against that file's official schema before treating this reference as complete.

## File Role

JPK_V7M is the main Polish VAT declaration and ledger XML. It contains both:

- Output VAT side: `SprzedazWiersz`
- Input VAT side: `ZakupWiersz`
- Declaration totals: `Deklaracja/PozycjeSzczegolowe`
- Control totals: `SprzedazCtrl`, `ZakupCtrl`

## Key Output Fields

| Field | Meaning |
|---|---|
| `K_21` | Intra-Community supply of goods, WDT. Used for cross-border B2B sales and transfer exports from Poland to another EU country. |
| `K_23` | Taxable base for intra-Community acquisition of goods, WNT. Used on the output side for cross-border B2B purchases and transfer imports into Poland. |
| `K_24` | Output VAT due for WNT. Usually `K_23 x Polish VAT rate`, often 23%. |

## Key Input Fields

| Field | Meaning |
|---|---|
| `K_40` | Net value for fixed-asset acquisitions. |
| `K_41` | Deductible input VAT for fixed-asset acquisitions. |
| `K_42` | Net value for other goods/services acquisitions. |
| `K_43` | Deductible input VAT for other goods/services acquisitions. |

## WNT Pattern

For ordinary EU B2B purchase and transfer import into Poland, JPK usually needs both:

1. Output side:
   - `SprzedazWiersz/K_23`
   - `SprzedazWiersz/K_24`
2. Input side:
   - `ZakupWiersz/K_42`
   - `ZakupWiersz/K_43`
   - or `K_40/K_41` for fixed assets

This is self-assessment plus deduction. A zero final VAT impact does not mean the transaction can be omitted.

## Declaration Totals

Common totals to reconcile against detail rows:

| Declaration field | Detail source |
|---|---|
| `P_21` | Sum of `K_21` |
| `P_23` | Sum of `K_23` |
| `P_24` | Sum of `K_24` |
| `P_42` | Sum of `K_42` |
| `P_43` | Sum of `K_43` |

Allow small rounding differences when declaration values are whole PLN and detail values have decimals.
