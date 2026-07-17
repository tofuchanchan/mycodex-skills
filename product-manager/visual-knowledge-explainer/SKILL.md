---
name: visual-knowledge-explainer
description: 将 PDF、文档、截图、代码仓库、功能实现、专业术语或用户大纲转成面向业务、产品与研发混合团队的中文可视化说明页面。编排 visual-explainer 完成 HTML 页面，excalidraw-diagram 完成精确流程或架构，ian-xiaohei-illustrations 完成抽象概念插图，并可交付 HTML 目录包、单文件 HTML、PDF 或全部格式。用户提到说明页、知识解释、术语解释、功能实现逻辑、架构说明、流程说明、可视化 HTML、解释型 PDF 时使用。
compatibility: Requires the three child skills when their routed capabilities are used, plus a browser for HTML/PDF inspection. PDF output requires the local PDF rendering workflow.
metadata:
  short-description: 统一生成分层知识说明页、精确图、概念插图和 PDF
---

# Visual Knowledge Explainer

把不同形态的材料转成一套事实一致、三层可读、视觉分工清楚的说明产物。不要把三个子 Skill 简单串联；先建立唯一事实底稿，再分别下发受约束的视觉任务。

## 默认行为

- 默认直接生成完整结果，不先征求大纲确认。
- 用户明确说“先出大纲”“只规划”时，只交付 Brief 和页面大纲，不生成最终资产。
- 只有以下情况才暂停：材料无法读取、关键事实冲突、任务范围存在实质歧义、所需子 Skill 缺失。
- 默认受众是业务、产品、研发混合团队。用户指定其他受众时覆盖默认值。
- 默认输出模式是 `html-bundle`。支持 `single-html`、`pdf`、`all`。
- 默认使用智能视觉路由；不要为了凑数强制调用所有子 Skill。

## 第一步：依赖预检

从 `$CODEX_HOME/skills` 或当前技能目录体系定位以下 Skill。每次真正调用某个子 Skill 前，完整读取它当前安装版本的 `SKILL.md`，并按其路由读取必要参考文件。

| 子 Skill | 何时必需 |
|---|---|
| `visual-explainer` | 生成任何最终 HTML 页面时必需 |
| `excalidraw-diagram` | 页面包含精确流程、架构、调用链、状态或分支时必需 |
| `ian-xiaohei-illustrations` | 页面需要抽象概念、业务价值或认知转折插图时必需 |

需要的依赖不存在时，立即说明缺失项和受影响的输出，不要伪造替代结果。若只是某类可选视觉不需要，则继续执行。

## 第二步：识别输入与结构策略

读取 [intake-routing.md](references/intake-routing.md)，判断输入类型、证据提取方式和大纲策略。

大纲策略只能使用以下值：

- `generate`：没有大纲，自动生成。
- `preserve`：用户大纲完整，保持章节顺序和意图，只修正文案与视觉表达。
- `augment`：用户大纲不完整，保留已有骨架并补充缺失层级。
- `replace`：仅当用户明确要求重做大纲时使用。

不要把整仓代码、整份长 PDF 或未经筛选的搜索结果直接塞给子 Skill。先提取与任务有关的事实、证据和未知项。

## 第三步：建立唯一 Explanation Brief

在生成任何正文或图像前，按 [explanation-brief-schema.md](references/explanation-brief-schema.md) 创建 `explanation-brief.yaml`。它是所有输出的唯一内容底稿。

来源优先级：

1. 用户明确约束和用户大纲。
2. 用户提供的原始材料。
3. 代码仓库中的可定位证据。
4. 权威外部资料。
5. 明确标注的推断。

每个关键主张必须标记：

- `confirmed`：由一手材料或代码直接支持。
- `inferred`：根据证据推断，必须说明推断依据。
- `external`：来自权威外部资料，必须记录链接或出处。
- `unknown`：材料不足，正文中必须如实暴露。

内容默认分为三层：

1. 业务层：是什么、为什么、带来什么价值。
2. 产品层：谁参与、规则是什么、状态和分支如何变化。
3. 工程层：入口在哪里、调用链怎样、数据和状态如何流转、异常如何处理、怎样扩展，并给出文件或方法证据。

不要把同一段内容复制三遍。每一层回答不同问题，并用链接或锚点向下钻取。

## 第四步：规划视觉任务

读取 [visual-routing.md](references/visual-routing.md)，为每个视觉建立任务卡。先判定它是“精确关系”还是“抽象理解”，再选择子 Skill。

### 给 Excalidraw 的任务包

只传递已核实的节点、边、方向、条件、状态、标签和证据。要求同时交付可编辑 `.excalidraw` 和页面使用的 PNG。执行其强制的渲染—查看—修复循环。

### 给小黑插图的任务包

每张图只传递一个抽象概念、认知转折或业务隐喻，附放置章节、核心意思、建议短标签和禁止表达。默认 2–4 张；短内容可以 1 张，确实没有抽象概念时为 0 张。生成后按其 QA 规则检查。

### 给 visual-explainer 的任务包

传递已经润色的章节正文、资产清单、相对路径、页面审美方向、响应式与打印要求。明确要求复用已有 Excalidraw 和小黑资产，不得用 Mermaid、CSS 图形或新图片重复描画同一核心关系。

关键事实必须同时存在于 HTML 正文、表格或精确图中，不能只存在于生成式插图里。

## 第五步：生成规范 HTML

先生成 `html-bundle`，它是其他格式的母版。默认目录：

```text
output/<topic-slug>/
├── index.html
├── <topic-slug>.single.html
├── <topic-slug>.pdf
├── explanation-brief.yaml
├── qa-report.md
└── assets/
    ├── source/
    ├── diagrams/
    │   ├── main-flow.excalidraw
    │   └── main-flow.png
    └── illustrations/
```

只创建用户所选模式需要的格式，但始终保留 Brief 和 QA 报告。源材料只在用户允许复制且交付需要时放入 `assets/source/`。

页面要求：

- 首屏说清主题、价值、阅读路径和证据状态。
- 业务、产品、工程三层有明确导航。
- 复杂信息使用语义表格、卡片或精确图，不用装饰性图表假装解释。
- 资产使用相对路径；中文字体有可靠回退。
- 桌面和移动端都不能横向溢出。
- 为 `@media print` 单独处理导航、分页、背景、表格、图像和链接。

## 第六步：派生交付格式

读取 [output-and-qa.md](references/output-and-qa.md)。格式必须从同一份规范 HTML 派生，禁止分别重写内容。

- `html-bundle`：保留相对资产目录。
- `single-html`：把本地 CSS、脚本、字体和图片内嵌；断网可读。
- `pdf`：从规范 HTML 打印。默认 A4 自动定向；知识/产品说明优先纵向，架构/流程密集页面优先横向。用户指定方向时服从用户。
- `all`：先完成 bundle，再派生 single HTML 和 PDF。

PDF 必须有封面、目录、页码和来源。生成后把每页渲染为图片并逐页检查裁切、断表、乱码、缺图和低清晰度。

## 第七步：质量门禁

在交付前完成以下检查：

1. 事实：关键主张均有状态和来源；未知项没有被改写成确定结论。
2. 覆盖：业务、产品、工程三层与用户大纲均被映射。
3. 视觉：精确图不承担抽象插画工作，小黑图不承担精确流程工作，页面不重复画图。
4. 子 Skill：分别执行三个子 Skill 自带的检查清单。
5. 文件：运行 `scripts/validate_output.py` 检查资产、离线依赖、占位符和格式完整性。
6. 浏览器：检查控制台错误、桌面/移动端溢出、导航和图片加载。
7. PDF：逐页渲染并肉眼复核。

把结论写入 `qa-report.md`，至少包括：通过项、失败项、已知限制、`unknown` 清单、人工复核记录。

## 交付说明

最终回复只报告：

- 生成了哪些格式及其路径。
- 精确图和小黑插图各有几张。
- 事实未知项或关键限制。
- QA 是否通过。

不要在聊天里复述整份页面内容。

