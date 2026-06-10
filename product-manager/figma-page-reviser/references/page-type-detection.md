# Page Type Detection

Detect the page type before applying a design standard. The goal is not to win a guessing game; the goal is to avoid turning商户端 into后台, or后台 into客服小清新页面. 两边混起来就是产品事故套餐。

## Classification Priority

Use evidence in this order:

1. **Explicit user instruction**: if the user says 后台/admin/internal or 商户端/user/customer, follow that unless the node/page evidence clearly contradicts it.
2. **Source URL/domain or frame naming**:
   - `uat-user.evatmaster.com`, `user.evatmaster.com`, `*-user.*`, `/user/login`, `/workPlace`, `/buy`, `/payCenter`, `/VAT/orderIndex`, `/VAT/declareIndex` indicate OST商户端/user.
   - domains/paths/names containing `admin`, `backend`, `ops`, `manage`, `operation`, or internal-only system names indicate OST后台/admin.
3. **Visible app shell**:
   - 商户端 indicators: 欧税通云服务平台, 购物车, 邀请有礼, 优惠专区, 帮助, 购买指南, 购买服务, 续费服务, 合规空间, VAT+, EPR服务, 账户中心, 客服, 公众号.
   - 后台 indicators: internal modules, approval/task queues, merchant/user management, system settings, audit/report navigation, dense internal operation panels.
4. **Task model and copy**:
   - 商户端: purchase, renewal, service card, account, VAT/EPR申报 submission, upload report, tax number validation, invoice upload, payment, customer guidance, tutorial/help.
   - 后台: batch processing, manual review, internal workflow, permission management, RPA, file distribution, audit, operations status tracking.

Dense tables do not override URL/app-shell evidence. VAT税号列表 and VAT申报列表 inside `uat-user.evatmaster.com` are 商户端 pages with tables, not后台 pages. 看到表格就喊后台，跟看到锅就喊厨师一样离谱。

## OST Admin / Backend

Likely admin when the page contains:

- internal employee audience: operations, finance/operation staff,客服, delivery teams, reviewers, or administrators
- dense data tables, filters, tabs, drawer/detail panels, bulk actions, status tracking, manual processing workflows, approval flows, task queues, or permission management
- internal management language such as admin, backend, operations, staff, reviewer, RPA, audit, approval, declaration records, task queue, report, or system config

When likely admin:

- use `ost-admin-system-guidelines`
- preserve dense, work-focused layout and internal information hierarchy
- judge revisions against admin colors, typography, table density, forms, buttons, cards, dividers, and app-shell consistency
- record that `ost-admin-system-guidelines` was selected

## OST User / Merchant-Facing

Likely商户端/user when the page contains:

- merchant/customer audience: sellers,商户, account users, service buyers, VAT/EPR service users
- source URL or frame hints from `uat-user.evatmaster.com`
- login, workbench, purchase, renewal, service selection, order center, account center, help, shopping cart, coupons, customer service, VAT申报, tax number details, file preview/download, tutorial entry, or user-facing empty/error states
- more explanatory copy, guided flows, readable forms, service cards, prices, and customer guidance

When likely商户端/user:

- use `ost-user-system-guidelines`
- preserve商户端 visual language: white sidebar/header, blue primary actions, light grey page background, white cards, service/product cards, readable form hierarchy, guided申报 steps, and user-facing status/copy
- judge revisions against user-side page patterns such as login, workbench, order list/detail, buy page, VAT list/detail/申报,申报详情, and 404
- record that `ost-user-system-guidelines` was selected

## Unclear

Ask the user:

```text
This page could be OST admin/backend or OST user/merchant-facing. Which standard should I use for review and revisions: `ost-admin-system-guidelines` or `ost-user-system-guidelines`?
```

Do not guess when the visual/design standard affects component choices, density, copy tone, or whether a suggested fix is acceptable.
