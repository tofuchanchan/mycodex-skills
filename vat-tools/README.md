# VAT Tools

Codex skills for VAT XML parsing, audit, reconciliation, and tax-risk diagnostics.

## Skills

| Skill | Description | Install URL |
| --- | --- | --- |
| `poland-vat-xml-auditor` | Audit Polish JPK_V7M and VAT-UE XML files, extract B2B and transfer transactions, reconcile files, and flag VAT reporting risks. | https://github.com/tofuchanchan/mycodex-skills/tree/main/vat-tools/poland-vat-xml-auditor |

## Poland VAT XML Auditor 使用帮助

`poland-vat-xml-auditor` 用来检查波兰 VAT 申报相关 XML，主要支持：

- `JPK_V7M` 主申报 XML
- `VAT-UE` 欧盟交易汇总 XML
- 跨境 B2B 销售识别
- 跨境 B2B 采购识别
- 欧盟内移仓出口识别
- 欧盟内移仓进口识别
- 两份 XML 的金额、VAT 号、交易类型对应关系检查
- XML 字段、命名、申报周期、税号等风险提示

### 使用前准备

把同一申报期的两份 XML 放在同一个文件夹里：

```text
PLxxxxxxxxxx_2026-04.xml
PLxxxxxxxxxx_2026-04(UE).xml
```

每次执行前，都必须确认客户是否有波兰以外的欧盟 VAT 税号。这个信息不能靠历史聊天、旧配置、文件名或者公司名瞎猜，不然移仓识别很容易翻车，锅还得人背。

如果客户没有其他欧盟 VAT 税号，直接告诉 Codex：

```text
客户没有波兰以外的其他欧盟 VAT 税号。
请调用 $poland-vat-xml-auditor 检查当前文件夹下的 JPK_V7M 和 VAT-UE XML。
```

如果客户有其他欧盟 VAT 税号，按国家列出来：

```text
客户有以下波兰以外的欧盟 VAT 税号：
DE: 312959814
CZ: 684687494
ES: 2765840J

请调用 $poland-vat-xml-auditor 检查当前文件夹下的 JPK_V7M 和 VAT-UE XML。
```

公司名不是必填项。VAT 号才是确认移仓的核心证据；公司名最多只是辅助参考，别拿公司名硬装 VAT 号，税务稽查看了都想报警。

### 安装方式

在 Codex 里让它安装这个 skill：

```text
Install this skill:
https://github.com/tofuchanchan/mycodex-skills/tree/main/vat-tools/poland-vat-xml-auditor
```

也可以用 skill installer：

```powershell
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo tofuchanchan/mycodex-skills --path vat-tools/poland-vat-xml-auditor
```

安装或更新后，重启 Codex，让 skill 生效。

### 输出文件

执行后会生成一个按税号、申报周期、日期和序号归档的文件夹，例如：

```text
audit-output/PL5263243352_2026-04_20260610_001/
```

主要文件：

| 文件 | 用途 |
| --- | --- |
| `vat_xml_audit_report.md` | 中文审计报告，适合先看这个 |
| `extracted_transactions.csv` | 提取出的交易明细，包括销售、采购、移仓出口、移仓进口 |
| `reconciliation_issues.csv` | 两份 XML 的不一致问题 |
| `audit_findings.json` | 结构化风险结果，适合后续系统读取 |

### 风险等级

| 等级 | 含义 |
| --- | --- |
| `P0` | XML 结构或关键字段严重问题，可能无法继续判断 |
| `P1` | 金额、VAT 号、交易对应关系等高风险不一致 |
| `P2` | 需要人工确认的风险，例如疑似移仓但缺少自有 VAT 号 |
| `P3` | 一般提示或低风险问题 |

### 注意事项

- 这个工具是审计辅助，不是自动报税机器人，别把它当税局亲儿子。
- 移仓识别必须依赖客户提供的自有欧盟 VAT 号。
- 如果没有提供其他欧盟 VAT 号，工具不会把交易强行认定为移仓，只会提示疑似风险。
- `VAT-UE` 和 `JPK_V7M` 的交易金额可能存在取整差异，工具会按容差判断。
- 看到 `P0` 或 `P1`，先处理这些；别上来就抠 `P3`，那叫战略性迷路。
