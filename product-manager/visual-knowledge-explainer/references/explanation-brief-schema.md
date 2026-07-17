# Explanation Brief 结构

Brief 使用 YAML，作为正文、图、单文件 HTML 和 PDF 的唯一事实底稿。

```yaml
brief_version: 1
topic:
  title: ""
  slug: ""
  goal: ""
  scope: []
audience:
  primary: [business, product, engineering]
  assumed_knowledge: "mixed"
delivery:
  generation_mode: direct       # direct | plan-only
  output_modes: [html-bundle]   # html-bundle | single-html | pdf | all
  outline_policy: generate      # generate | preserve | augment | replace
  pdf_orientation: auto         # auto | portrait | landscape
sources:
  - id: S1
    type: pdf                    # pdf | image | document | repository | web | user
    locator: ""
    role: ""
claims:
  - id: C1
    text: ""
    confidence: confirmed       # confirmed | inferred | external | unknown
    source_ids: [S1]
    evidence: "页码、文件:行号、章节或链接"
    caveat: ""
outline:
  - id: business
    title: ""
    audience: business
    purpose: ""
    claim_ids: [C1]
    children: []
visual_tasks:
  - id: V1
    role: exact                 # exact | abstract
    section_id: product
    purpose: ""
    claim_ids: [C1]
    provider: excalidraw-diagram
    deliverables: [editable, png]
unknowns:
  - id: U1
    question: ""
    impact: low                 # low | medium | high
    handling: "在正文中标注"
```

## 约束

- `topic.slug` 只使用小写字母、数字和连字符。
- 每个正文关键结论必须能回到 `claims`。
- `inferred` 必须填写 `evidence` 与 `caveat`。
- `external` 必须关联可访问的来源。
- `unknown` 不得分配给承担结论证明的视觉任务。
- 每个视觉任务只解决一个主要问题。
- 用户大纲的每个保留章节都必须映射到 `outline`。

