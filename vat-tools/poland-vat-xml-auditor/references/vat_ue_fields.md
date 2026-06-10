# VAT-UE Field Reference

Use this reference when explaining findings from the VAT-UE XML.

Official basis for the currently supported file variant:

- VAT-UE (5)
- Namespace: `http://crd.gov.pl/wzor/2021/01/12/10293/`
- Schema: `https://crd.gov.pl/wzor/2021/01/12/10293/schemat.xsd`

If the file declares a different namespace or form variant, verify against that file's official schema before treating this reference as complete.

## File Role

VAT-UE is a summary information XML for intra-Community transactions. It is a reconciliation/listing file, not a VAT calculation ledger.

Do not duplicate the JPK WNT output/input pattern inside VAT-UE. Each transaction is reported in the relevant group from the Polish taxpayer's perspective.

## Groups

| Group | Meaning | Official fields |
|---|---|---|
| `Grupa1` | Intra-Community supplies of goods | `P_Da/P_Db/P_Dc/P_Dd` |
| `Grupa2` | Intra-Community acquisitions of goods | `P_Na/P_Nb/P_Nc/P_Nd` |
| `Grupa3` | Intra-Community services | `P_Ua/P_Ub/P_Uc` |
| `Grupa4` | Call-off stock movements | `P_Ca/P_Cb/...` |

## Grupa1

Use for:

- Cross-border B2B sales from Poland to another EU country.
- Transfer exports from Poland to the taxpayer's own VAT registration in another EU country.

Fields:

| Field | Meaning |
|---|---|
| `P_Da` | Buyer country code |
| `P_Db` | Buyer VAT ID |
| `P_Dc` | Total transaction value in PLN |
| `P_Dd` | Triangular transaction flag: `1` no, `2` yes |

## Grupa2

Use for:

- Cross-border B2B purchases from another EU country into Poland.
- Transfer imports from the taxpayer's own VAT registration in another EU country into Poland.

Fields:

| Field | Meaning |
|---|---|
| `P_Na` | Supplier country code |
| `P_Nb` | Supplier VAT ID |
| `P_Nc` | Total transaction value in PLN |
| `P_Nd` | Triangular transaction flag: `1` no, `2` yes |

If `Grupa2` contains `P_Da/P_Db/P_Dc/P_Dd`, flag it as a schema risk. Those are `Grupa1` fields.

## No Single-File Double-Siding

Within one Polish VAT-UE file:

- A supply goes to `Grupa1`.
- An acquisition goes to `Grupa2`.
- The same transaction should not be duplicated in both groups from the same taxpayer perspective.

The "double side" logic belongs to JPK WNT self-assessment and deduction, not to VAT-UE.
