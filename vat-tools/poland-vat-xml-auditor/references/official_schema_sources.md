# Official Schema Sources

Use the schema declared by the XML namespace as the primary source for field meaning and structure. The skill currently targets the following official schemas.

## JPK_V7M

- Form: `JPK_V7M (3)`
- Namespace: `http://crd.gov.pl/wzor/2025/12/19/14090/`
- Official schema: `https://crd.gov.pl/wzor/2025/12/19/14090/schemat.xsd`
- Used for:
  - `SprzedazWiersz`
  - `ZakupWiersz`
  - `K_21`
  - `K_23/K_24`
  - `K_40/K_41`
  - `K_42/K_43`
  - declaration and control totals

## VAT-UE

- Form: `VAT-UE (5)`
- Namespace: `http://crd.gov.pl/wzor/2021/01/12/10293/`
- Official schema: `https://crd.gov.pl/wzor/2021/01/12/10293/schemat.xsd`
- Used for:
  - `Grupa1`: `P_Da/P_Db/P_Dc/P_Dd`
  - `Grupa2`: `P_Na/P_Nb/P_Nc/P_Nd`
  - `Grupa3`: `P_Ua/P_Ub/P_Uc`
  - `Grupa4`: `P_Ca/P_Cb/...`

## Version Rule

If a user's XML declares a different namespace, form variant, or schema version, do not blindly apply these field references as if nothing changed. Parse what can be parsed, but flag a review item that the official schema reference should be updated for that file version.
