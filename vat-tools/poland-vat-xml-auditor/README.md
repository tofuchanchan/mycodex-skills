# Poland VAT XML Auditor 使用帮助

`poland-vat-xml-auditor` 用于检查波兰 VAT 申报相关 XML，重点处理 `JPK_V7M` 主申报文件和 `VAT-UE` 欧盟交易汇总文件。

## 能检查什么

- XML 文件类型、结构、命名、申报周期、税号是否异常
- 跨境 B2B 销售
- 跨境 B2B 采购
- 欧盟内移仓出口
- 欧盟内移仓进口
- `JPK_V7M` 与 `VAT-UE` 的金额、VAT 号、交易类型是否对应
- 可能影响申报的风险点

## 使用前准备

把同一申报期的两份 XML 放在同一个文件夹里：

```text
PLxxxxxxxxxx_2026-04.xml
PLxxxxxxxxxx_2026-04(UE).xml
```

每次执行前，必须确认客户是否有波兰以外的其他欧盟 VAT 税号。这个信息不能依赖历史聊天、旧配置文件、文件名或公司名。

## 怎么问 Codex

如果客户没有其他欧盟 VAT 税号：

```text
客户没有波兰以外的其他欧盟 VAT 税号。
请调用 $poland-vat-xml-auditor 检查当前文件夹下的 JPK_V7M 和 VAT-UE XML。
```

如果客户有其他欧盟 VAT 税号：

```text
客户有以下波兰以外的欧盟 VAT 税号：
DE: 888888888
CZ: 88888888
ES: N8888888J

请调用 $poland-vat-xml-auditor 检查当前文件夹下的 JPK_V7M 和 VAT-UE XML。
```

公司名不是必填项。VAT 号才是确认移仓的核心证据；公司名只能辅助人工复核，不能单独作为移仓确认依据。

## 安装方式

在 Codex 里安装：

```text
Install this skill:
https://github.com/tofuchanchan/mycodex-skills/tree/main/vat-tools/poland-vat-xml-auditor
```

也可以使用 skill installer：

```powershell
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo tofuchanchan/mycodex-skills --path vat-tools/poland-vat-xml-auditor
```

安装或更新后，重启 Codex。

## 输出文件

执行后会生成按税号、申报周期、日期和序号归档的文件夹，例如：

```text
audit-output/PL8888888888_2026-04_20260610_001/
```

主要输出：

| 文件 | 用途 |
| --- | --- |
| `vat_xml_audit_report.md` | 中文审计报告，建议先看这个 |
| `extracted_transactions.csv` | 提取出的交易明细，包括销售、采购、移仓出口、移仓进口 |
| `reconciliation_issues.csv` | 两份 XML 的不一致问题 |
| `audit_findings.json` | 结构化风险结果，适合系统读取或二次处理 |

## 风险等级

| 等级 | 含义 |
| --- | --- |
| `P0` | XML 无法解析、文件类型无法识别或关键结构错误 |
| `P1` | 金额、VAT 号、交易对应关系等高风险不一致 |
| `P2` | 需要人工确认的风险，例如疑似移仓但缺少自有 VAT 号 |
| `P3` | 一般提示或低风险问题 |

## 注意事项

- 这个工具是审计辅助，不是自动报税工具。
- 移仓识别必须依赖客户提供的自有欧盟 VAT 号。
- 如果没有提供其他欧盟 VAT 号，工具不会把交易强行认定为移仓，只会提示疑似风险。
- `VAT-UE` 和 `JPK_V7M` 的交易金额可能存在取整差异，工具会按容差判断。
- 优先处理 `P0` 和 `P1`，再看 `P2` 和 `P3`。
