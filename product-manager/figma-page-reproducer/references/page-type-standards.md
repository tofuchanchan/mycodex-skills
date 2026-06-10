# Page Type Standards

Detect the page type before applying a design standard. Reproducing the page means preserving what exists; QA and reconstruction still need the correct rulebook. Mixing them up is how a商户端 page gets dressed like a后台 table prison, which is exactly the kind of离谱事故 this reference is here to prevent.

## Classification Priority

Use evidence in this order:

1. **Explicit user instruction**: if the user says 后台/admin/internal or 商户端/user/customer, follow that unless the URL clearly contradicts it.
2. **URL/domain/app identity**:
   - `uat-user.evatmaster.com`, `user.evatmaster.com`, `*-user.*`, `/user/login`, `/workPlace`, `/buy`, `/payCenter`, `/VAT/orderIndex`, `/VAT/declareIndex` are OST商户端/user evidence.
   - domains or paths containing `admin`, `backend`, `ops`, `manage`, `operation`, or internal-only system names are OST后台/admin evidence.
3. **App shell and navigation**:
   - 商户端 usually has 欧税通云服务平台, 购物车, 邀请有礼, 优惠专区, 帮助, 购买指南, 购买服务, 续费服务, 合规空间, VAT+, EPR服务, 账户中心.
   - 后台 usually has internal operations modules, approval queues, task centers, merchant/user management, system settings, audit/report workflows, and compact management navigation.
4. **Content and task model**:
   - Dense tables alone do not prove 后台. VAT税号、VAT申报、订单列表 in `uat-user.evatmaster.com` are still 商户端.
   - Purchase cards, service pricing, guided申报 steps, help/tutorial/customer service affordances are 商户端 evidence.

## OST Admin / Backend

Likely admin pages usually have:

- internal employee audience: operations, finance,客服, delivery, reviewer, or administrator
- dense data tables, filters, batch actions, approval flows, task queues, audit/report workflows, permission management, or manual processing
- compact forms and repeated table/list operations
- internal management terms such as order management, merchant management, user code, supplier, registration, workflow, audit, report, or system config

When likely admin:

- use `ost-admin-system-guidelines` as the design/reconstruction/QA standard
- keep dense, work-focused layout and existing admin information hierarchy
- verify colors, typography, sidebar/header structure, form controls, table density, buttons, cards, dividers, status colors, and operational affordances against the admin standard
- record in QA that `ost-admin-system-guidelines` was selected

## OST User / Merchant-Facing

Likely商户端/user pages usually have:

- merchant/customer audience: sellers,商户, account users, service buyers, VAT/EPR service users
- domains such as `uat-user.evatmaster.com`
- onboarding, login, workbench, purchase, renewal, service selection, order center, account center, help, shopping cart, coupons, or customer service language
- product/service cards, pricing, purchase buttons, guided forms, VAT申报 steps, tax number details, file preview/download, tutorial entry, or user-facing empty/error states

When likely商户端/user:

- use `ost-user-system-guidelines` as the design/reconstruction/QA standard
- preserve the captured商户端 visual system: white sidebar/header, blue primary actions, white cards on light grey canvas, service cards, readable user-facing copy, and guided流程 structure
- verify merchant-side navigation, service purchase cards, VAT列表/详情/申报 page patterns, status wording, help/customer-service affordances, and 404/login patterns against the user standard
- record in QA that `ost-user-system-guidelines` was selected

## Unclear Page Type

If the page could be admin or user and the standard will affect component density, copy tone, or page reconstruction, ask:

```text
This page could be OST admin/backend or OST user/merchant-facing. Should I use `ost-admin-system-guidelines` or `ost-user-system-guidelines` for the Figma reconstruction QA?
```

Do not choose admin just because the page has tables. That is lazy pattern matching wearing a fake mustache.

## QA Record

Final QA should include:

```text
Page type: OST user / merchant-facing
Design standard: ost-user-system-guidelines
Checked: app shell, user navigation, cards/tables, forms, flow steps, button hierarchy, typography, colors, status wording, divider artifacts
```
