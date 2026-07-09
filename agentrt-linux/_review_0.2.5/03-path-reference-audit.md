# 路径引用校对审查报告

> **审查范围**: `OpenAirymax/docs/AirymaxOS/` 目录下全部 Markdown 文件（110 个 `.md` 文件）
> **审查日期**: 2026-07-09
> **审查版本**: 0.2.5
> **审查工具**: Grep / Glob / Read / Python 脚本穷举校验
> **审查性质**: 只读审查，未修改任何文件

---

## 审查方法说明

1. 通过 `os.walk` 遍历 AirymaxOS 全树，收集所有 `.md` 文件路径作为基线。
2. 使用正则 `\[([^\]]*)\]\(([^)]+\.md(?:#[^)]*)?)\)` 提取所有指向 `.md` 的相对路径链接（共 483 处），逐一解析相对路径并验证目标存在性。
3. 使用 GitHub Flavored Markdown slugger 规则（小写化 + 保留 `\w`/空格/连字符 + 空格转连字符）验证文档内 TOC 锚点（`[文本](#锚点)` 形式，共 190 处）。
4. 跨文档锚点（`xxx.md#锚点`、`xxx.md#L行号`）形式引用：穷举搜索，结果为 0 处。
5. 对 `docs/AirymaxAgentOS/`、`docs/AirymaxAgentRT/`、`150-cloud-native`、`agentrt_contract`、`ADR-0XX`、子仓名等关键命名做全树扫描。

---

## 一、内部文档引用断链（相对路径）

共发现 **29 处**断链，归为 7 组。

### 组 A：`../../00-architectural-principles.md` 路径错误（10 处）

实际文件位于 `docs/AirymaxRT/00-architectural-principles.md`，但链接解析到 `docs/00-architectural-principles.md`（不存在）。正确相对路径应为 `../../AirymaxRT/00-architectural-principles.md`。

| 文件 | 行号 | 链接文本 | 错误目标 |
|------|------|----------|----------|
| `00-requirements/01-business-requirements.md` | 552 | Airymax 架构设计原则 | `../../00-architectural-principles.md` |
| `00-requirements/02-functional-requirements.md` | 353 | Airymax 架构设计原则 | `../../00-architectural-principles.md` |
| `00-requirements/03-non-functional-requirements.md` | 822 | Airymax 架构设计原则 | `../../00-architectural-principles.md` |
| `00-requirements/README.md` | 402 | Airymax 架构设计原则 | `../../00-architectural-principles.md` |
| `10-architecture/02-five-dimensional-principles.md` | 9 | 00-architectural-principles.md | `../../00-architectural-principles.md` |
| `10-architecture/02-five-dimensional-principles.md` | 557 | 架构原则 | `../../00-architectural-principles.md` |
| `10-architecture/04-engineering-baseline.md` | 414 | 架构原则 | `../../00-architectural-principles.md` |
| `10-architecture/05-adrs.md` | 1073 | 架构原则 | `../../00-architectural-principles.md` |
| `10-architecture/README.md` | 276 | 架构原则 | `../../00-architectural-principles.md` |
| `40-dataflows/README.md` | 148 | Airymax 架构设计原则 | `../../00-architectural-principles.md` |

**建议修复**：将上述 10 处 `../../00-architectural-principles.md` 统一改为 `../../AirymaxRT/00-architectural-principles.md`。

### 组 B：`../_review_0.1.1/` 目录不存在（2 处）

实际审查报告位于 `docs-closed/agentrt-linux/_review_0.1.1/`，而 AirymaxOS 树下不存在 `_review_0.1.1/` 目录。

| 文件 | 行号 | 链接文本 | 错误目标 |
|------|------|----------|----------|
| `50-engineering-standards/00-engineering-standards-handbook.md` | 9 | comprehensive-review-report.md | `../_review_0.1.1/comprehensive-review-report.md` |
| `50-engineering-standards/00-engineering-standards-handbook.md` | 9 | revision-changelog.md | `../_review_0.1.1/revision-changelog.md` |

**建议修复**：删除这两处链接，或改为指向 `docs-closed/agentrt-linux/_review_0.1.1/`（但跨 `docs/` 与 `docs-closed/` 两个顶层目录的相对路径会非常深，建议改为纯文字引用或删除链接）。

### 组 C：`../project_erp/` 应为 `../50-project-erp/`（6 处）

实际目录为 `50-engineering-standards/50-project-erp/`（带 `50-` 前缀），但链接使用了不带前缀的 `project_erp/`。

| 文件 | 行号 | 链接文本 | 错误目标 |
|------|------|----------|----------|
| `50-engineering-standards/40-integration/README.md` | 473 | 项目管理规范总览 | `../project_erp/README.md` |
| `50-engineering-standards/40-integration/README.md` | 474 | 统一错误码参考 | `../project_erp/error_code_reference.md` |
| `50-engineering-standards/40-integration/README.md` | 475 | SBOM 规范 | `../project_erp/SBOM.md` |
| `50-engineering-standards/40-integration/agentrt_integration.md` | 809 | 项目管理规范总览 | `../project_erp/README.md` |
| `50-engineering-standards/40-integration/agentrt_integration.md` | 810 | 统一错误码参考 | `../project_erp/error_code_reference.md` |
| `50-engineering-standards/40-integration/agentrt_integration.md` | 811 | SBOM 规范 | `../project_erp/SBOM.md` |

**建议修复**：将 `../project_erp/` 改为 `../50-project-erp/`。

### 组 D：`../integration_standards/` 应为 `../40-integration/`（5 处）

实际目录为 `50-engineering-standards/40-integration/`（带 `40-` 前缀且名为 `integration`），但链接使用了 `integration_standards/`（无前缀且名称不同）。

| 文件 | 行号 | 链接文本 | 错误目标 |
|------|------|----------|----------|
| `50-engineering-standards/50-project-erp/README.md` | 373 | 集成标准总览 | `../integration_standards/README.md` |
| `50-engineering-standards/50-project-erp/README.md` | 374 | agentrt 集成规范 | `../integration_standards/agentrt_integration.md` |
| `50-engineering-standards/50-project-erp/SBOM.md` | 468 | 集成标准总览 | `../integration_standards/README.md` |
| `50-engineering-standards/50-project-erp/error_code_reference.md` | 673 | 集成标准总览 | `../integration_standards/README.md` |
| `50-engineering-standards/50-project-erp/error_code_reference.md` | 674 | agentrt 集成规范 | `../integration_standards/agentrt_integration.md` |

**建议修复**：将 `../integration_standards/` 改为 `../40-integration/`。注意组 C 与组 D 互为反向引用——`40-integration/` 引用 `50-project-erp/`（组 C 错），`50-project-erp/` 引用 `40-integration/`（组 D 错），双向断链。

### 组 E：`20-contracts/` 下缺失 3 个被引用文件（3 处）

`logging_contract.md` 引用了 3 个不存在的同级文件。`20-contracts/` 实际仅含 `README.md`、`ipc_protocol_contract.md`、`logging_contract.md`、`syscall_api_contract.md`。

| 文件 | 行号 | 链接文本 | 错误目标 |
|------|------|----------|----------|
| `50-engineering-standards/20-contracts/logging_contract.md` | 524 | agentrt-linux（AirymaxOS）IRON-9 v2 通道规范 | `iron9_channel_contract.md` |
| `50-engineering-standards/20-contracts/logging_contract.md` | 525 | agentrt-linux（AirymaxOS）安全策略规范 | `security_policy.md` |
| `50-engineering-standards/20-contracts/logging_contract.md` | 526 | agentrt-linux（AirymaxOS）OpenTelemetry 集成指南 | `otel_integration.md` |

**建议修复**：这 3 个文件（`iron9_channel_contract.md`、`security_policy.md`、`otel_integration.md`）在 OpenAirymax 全树均不存在。应创建对应文件，或删除/改为纯文字引用。

### 组 F：`AirymaxAgentRT/agentrt_contract/` 双重命名错误（1 处）

`50-engineering-standards/20-contracts/README.md:276` 引用 `../../../AirymaxAgentRT/50-specifications/10-contracts/03-protocol-contract.md`。实际路径为 `docs/AirymaxRT/50-specifications/10-contracts/03-protocol-contract.md`。存在 **两处**命名错误：
- 目录名 `AirymaxAgentRT` 应为 `AirymaxRT`
- 子目录名 `agentrt_contract` 应为 `agentrt_contract`

正确相对路径应为 `../../../AirymaxRT/50-specifications/10-contracts/03-protocol-contract.md`。

### 组 G：`../../AirymaxAgentRT/00-basic-theories/` 目录名错误（2 处）

`50-engineering-standards/30-runtime-interfaces/README.md` 引用 `../../AirymaxAgentRT/00-basic-theories/`。实际目录为 `docs/AirymaxRT/00-basic-theories/`（`AirymaxRT` 而非 `AirymaxAgentRT`）。两个被引用文件本身存在，仅目录名错误。

| 文件 | 行号 | 链接文本 | 错误目标 |
|------|------|----------|----------|
| `50-engineering-standards/30-runtime-interfaces/README.md` | 503 | 体系并行论 | `../../AirymaxAgentRT/00-basic-theories/01-mcis-cn.md` |
| `50-engineering-standards/30-runtime-interfaces/README.md` | 504 | 系统设计原则 | `../../AirymaxAgentRT/00-basic-theories/04-design-principles-cn.md` |

**建议修复**：将 `../../AirymaxAgentRT/` 改为 `../../AirymaxRT/`。

---

## 二、章节锚点引用

### 2.1 跨文档锚点（`xxx.md#锚点`、`xxx.md#L行号`）

穷举搜索结果：**0 处**。文档中不存在跨文档锚点引用，无需校验。

### 2.2 文档内 TOC 锚点（`[文本](#锚点)`）

共扫描 190 处文档内 TOC 锚点，发现 **5 处断锚**。均为同一根因：TOC 锚点中 `agentrt-linux` 被错误替换为 `airymaxos`，导致锚点与标题不匹配。

| 文件 | 行号 | TOC 链接文本 | 错误锚点 | 对应实际标题 |
|------|------|--------------|----------|--------------|
| `90-observability/01-ftrace-framework.md` | 25 | 第 10 章 agentrt-linux Agent 行为追踪扩展 | `#第-10-章-airymaxos-agent-行为追踪扩展` | `## 第 10 章 agentrt-linux Agent 行为追踪扩展` |
| `90-observability/02-ebpf-probes.md` | 26 | 第 11 章 agentrt-linux Token 能效监控与 Agent 行为追踪 | `#第-11-章-airymaxos-token-能效监控与-agent-行为追踪` | `## 第 11 章 agentrt-linux Token 能效监控与 Agent 行为追踪` |
| `110-security/01-lsm-framework.md` | 23 | 第 8 章 agentrt-linux Cupolas 作为 LSM 模块集成 | `#第-8-章-airymaxos-cupolas-作为-lsm-模块集成` | `## 第 8 章 agentrt-linux Cupolas 作为 LSM 模块集成` |
| `110-security/02-landlock-sandbox.md` | 17 | 第 2 章 Landlock 在 agentrt-linux 中的定位 | `#第-2-章-landlock-在-airymaxos-中的定位` | `## 第 2 章 Landlock 在 agentrt-linux 中的定位` |
| `110-security/02-landlock-sandbox.md` | 23 | 第 8 章 agentrt-linux Agent 沙箱实现 | `#第-8-章-airymaxos-agent-沙箱实现` | `## 第 8 章 agentrt-linux Agent 沙箱实现` |

**根因分析**：链接文本与实际标题均使用 `agentrt-linux`，但锚点部分被批量替换工具误改为 `airymaxos`（OS 简称），造成锚点无法匹配标题。这是一个系统性的批量替换副作用。

**建议修复**：将上述 5 处锚点中的 `airymaxos` 改回 `agentrt-linux`（与标题文本一致）。

---

## 三、跨目录引用对称性

对 `00-requirements` → `10-architecture` → `20-modules` → `30-interfaces` → `40-dataflows` 五个核心目录的跨目录引用矩阵如下（行=源，列=目标，单元格=引用次数，对角线自身引用已排除）：

| 源 \ 目标 | 00-requirements | 10-architecture | 20-modules | 30-interfaces | 40-dataflows |
|-----------|-----------------|------------------|------------|---------------|--------------|
| 00-requirements | — | 0 | 0 | 0 | 0 |
| 10-architecture | 1 | — | 4 | 0 | 0 |
| 20-modules | 1 | 6 | — | 10 | 3 |
| 30-interfaces | 6 | 2 | 17 | — | 0 |
| 40-dataflows | 8 | 2 | 6 | 10 | — |

### 发现的非对称引用对（3 对）

**非对称 1：`10-architecture` ⇄ `30-interfaces`**
- `30-interfaces → 10-architecture`：2 次（`30-interfaces/README.md:70,152`）
- `10-architecture → 30-interfaces`：0 次
- 接口层引用了架构层，但架构层未反向引用接口层。`10-architecture/README.md` 的"相关文档"章节链接了 requirements、modules，但遗漏了 interfaces。

**非对称 2：`10-architecture` ⇄ `40-dataflows`**
- `40-dataflows → 10-architecture`：2 次（`04-scheduling-flow.md:889`、`README.md:145`）
- `10-architecture → 40-dataflows`：0 次
- 数据流层引用了架构层（ADR、README），但架构层未反向引用数据流层。

**非对称 3：`30-interfaces` ⇄ `40-dataflows`**
- `40-dataflows → 30-interfaces`：10 次（高频）
- `30-interfaces → 40-dataflows`：0 次
- 数据流层大量引用接口层（syscalls、ipc-protocol），但接口层"相关文档"章节未反向链接数据流层。这是最显著的单向引用。

**说明**：上述非对称不一定是错误（数据流向下游引用上游属合理设计），但根据"不矛盾"原则，建议在 `10-architecture/README.md`、`30-interfaces/README.md` 的相关文档列表中补全对 interfaces/dataflows 的反向链接，提升导航闭环。

### `00-requirements` 单向被引用

`00-requirements` 被 4 个目录引用共 16 次（10-arch×1 + 20-mod×1 + 30-if×6 + 40-df×8），但自身向其他 4 个目录的出向引用为 0。需求层作为最上游"事实源"不出向引用下游设计属合理设计，不视为问题，仅作记录。

---

## 四、目录路径引用一致性

### 4.1 `docs/AirymaxAgentOS/` 应为 `docs/AirymaxOS/`（148 处，16 个文件）

**严重问题**：实际物理目录为 `docs/AirymaxOS/`（短名），但文档中 148 处使用 `docs/AirymaxAgentOS/`（正式英文名）作为路径引用。`AirymaxAgentOS` 是文档中规定的"正式英文名"，`AirymaxOS` 是"简称"（见 `README.md:6`、`10-terminology.md:246-248`），但物理目录使用的是简称。**当 `AirymaxAgentOS` 出现在路径上下文（尤其是可执行 shell 命令）中时，全部失效。**

按文件分布（按频次降序）：

| 文件 | 出现次数 | 危险等级 |
|------|----------|----------|
| `130-roadmap/06-acceptance-criteria.md` | 101 | **高**（验收命令，`find`/`grep` 会直接失败） |
| `50-engineering-standards/08-compliance-checklist.md` | 15 | **高**（合规检查脚本，`find`/`grep`/`for` 循环会失败） |
| `10-terminology.md` | 7 | 中（路径元信息 + 参考文献引用） |
| `50-engineering-standards/00-engineering-standards-handbook.md` | 5 | 中 |
| `50-engineering-standards/README.md` | 3 | 中 |
| `50-engineering-standards/50-project-erp/README.md` | 3 | 中 |
| `180-i18n/03-doc-i18n.md` | 3 | 中 |
| `README.md` | 2 | 中（含目录树根 `docs/AirymaxAgentOS/`） |
| `50-engineering-standards/30-runtime-interfaces/README.md` | 2 | 中 |
| `50-engineering-standards/30-runtime-interfaces/L3_security_governance.md` | 1 | 低 |
| `50-engineering-standards/30-runtime-interfaces/L2_service_protocol.md` | 1 | 低 |
| `50-engineering-standards/30-runtime-interfaces/L1_runtime_interface.md` | 1 | 低 |
| `180-i18n/README.md` | 1 | 低 |
| `120-development-process/02-maintainer-hierarchy.md` | 1 | 低 |
| `10-architecture/02-five-dimensional-principles.md` | 1 | 低 |
| `00-requirements/README.md` | 1 | 低 |
| **合计** | **148** | |

**典型失效示例**（`130-roadmap/06-acceptance-criteria.md:228`）：
```
| OS-ACC-092 | 150-cloudnative/ 8 文档完成 | `find docs/AirymaxAgentOS/150-cloudnative/ -name "*.md" \| wc -l` | ≥8 |
```
该验收命令运行 `find docs/AirymaxAgentOS/150-cloudnative/` 会因路径不存在而返回 0，导致验收永远无法通过。

**建议修复**：全树将路径上下文中的 `docs/AirymaxAgentOS/` 替换为 `docs/AirymaxOS/`（共 148 处）。注意保留散文中作为"正式英文名"的 `AirymaxAgentOS`（如 `README.md:6` 的"正式英文名：AirymaxAgentOS"表述），仅修正路径上下文。

### 4.2 `docs/AirymaxAgentRT/` 应为 `docs/AirymaxRT/`（3 处）

实际物理目录为 `docs/AirymaxRT/`（短名），但有 3 处路径引用使用了 `docs/AirymaxAgentRT/`（正式英文名）。

| 文件 | 行号 | 错误路径引用 |
|------|------|--------------|
| `10-terminology.md` | 816 | `docs/AirymaxAgentRT/50-specifications/10-terminology.md` |
| `10-terminology.md` | 817 | `docs/AirymaxAgentRT/50-specifications/README.md` |
| `50-engineering-standards/20-contracts/README.md` | 30 | `docs/AirymaxAgentRT/50-specifications/10-contracts/` |

**建议修复**：将路径上下文中的 `AirymaxAgentRT` 改为 `AirymaxRT`。其中第 30 行同时存在 `agentrt_contract` 应为 `agentrt_contract` 的错误（见 4.3）。

### 4.3 `agentrt_contract` 应为 `agentrt_contract`（命名不一致）

实际子目录为 `50-specifications/10-contracts/`，但文档中多处使用 `agentrt_contract`。

| 文件 | 行号 | 类型 | 内容 |
|------|------|------|------|
| `50-engineering-standards/20-contracts/README.md` | 30 | 路径引用 | `docs/AirymaxAgentRT/50-specifications/10-contracts/` |
| `50-engineering-standards/20-contracts/README.md` | 276 | 断链（见组 F） | `../../../AirymaxAgentRT/Capital_Specificates/agentrt_contract/protocol_contract.md` |
| `50-engineering-standards/README.md` | 115 | 迁移说明（散文） | `原 50-specifications/10-contracts/` |
| `50-engineering-standards/20-contracts/syscall_api_contract.md` | 8, 412 | 链接文本 | `[agentrt_contract README](README.md)` |
| `50-engineering-standards/20-contracts/ipc_protocol_contract.md` | 8, 397 | 链接文本 | `[agentrt_contract README](README.md)` |

**说明**：`20-contracts/README.md:115` 的"原 50-specifications/10-contracts/"是迁移历史描述，可能记录的是旧名；但当前实际目录名为 `agentrt_contract`，建议核实迁移前的真实目录名后统一表述。`syscall_api_contract.md` 与 `ipc_protocol_contract.md` 的链接文本"agentrt_contract README"指向本地 `README.md`（链接本身有效），但文本使用了与实际子目录名（`20-contracts`）不一致的历史名，建议改为"契约规范 README"或"20-contracts README"。

### 4.4 `50-engineering-standards/` 文档计数过时

`README.md:50` 目录树与 `README.md:104` 表格均标注"50-engineering-standards # 工程标准规范（8 文档）"，但实际该目录顶层已有 **18 个** `.md` 文件（`00`-`09` 共 10 个 + `60/70/80/90/100/110/120` 共 7 个 + `README.md`）。"8 文档"仅对应 `01`-`08` 主题文档，未覆盖 `00-engineering-standards-handbook.md`、`09-license-strategy.md` 及 `60`-`120` 系列扩展文档。

**建议修复**：更新目录树与分层说明表中的计数，或在括号中注明"8 主题文档 + 扩展规范"。

---

## 五、ADR 编号引用

`10-architecture/05-adrs.md` 实际包含 **14 个 ADR**（ADR-001 ~ ADR-014，已逐条核对标题，全部为 `Accepted` 状态）。

### 5.1 ADR 描述错位（`01-system-architecture.md`）

`10-architecture/01-system-architecture.md:212-217` 的 ADR 摘要表只列出 6 条 ADR，且描述与 `05-adrs.md` 权威定义**错位/不符**：

| 行号 | 表中描述 | `05-adrs.md` 权威定义 | 一致性 |
|------|----------|------------------------|--------|
| 212 | ADR-001: 基于 Linux 内核，不从零开发微内核 | ADR-001: 采用 Linux 6.6 内核基线（同步 SP3 增强） | 主题相近，描述偏简 |
| 213 | ADR-002: 微内核化改造策略 | ADR-002: 微内核化改造策略 | ✅ 一致 |
| 214 | ADR-003: 全面采用 agentrt-linux 工程基线 | ADR-003: 8 子仓划分 | ❌ **不符**（描述对应工程基线文档，非 ADR-003） |
| 215 | ADR-004: agentrt 和 agentrt-linux 同源且部分代码共享 | ADR-004: capability 安全模型 | ❌ **不符**（描述实际对应 ADR-010） |
| 216 | ADR-005: 8 子仓按能力域划分 | ADR-005: io_uring IPC 子系统 | ❌ **不符**（描述实际对应 ADR-003） |
| 217 | ADR-006: OS 文档与 RT 文档物理分开 | ADR-006: CoreLoopThree kthread 认知循环 | ❌ **不符**（无对应 ADR） |

**根因**：该表使用的是 ADR 编号重排前的旧描述（疑似 v0.1.1 早期编号方案），未随 ADR-003~010 重新编号同步更新，且仅列 6 条而漏掉 ADR-007~014。

**建议修复**：以 `05-adrs.md` 为权威源，重写 `01-system-architecture.md:212-217` 的 ADR 摘要表，补全至 14 条并对齐描述。

### 5.2 过时的"10 个核心 ADR"计数（3 处）

| 文件 | 行号 | 过时表述 |
|------|------|----------|
| `10-architecture/02-five-dimensional-principles.md` | 389 | `（10 个 ADR）` |
| `10-architecture/02-five-dimensional-principles.md` | 556 | `10 个核心 ADR` |
| `10-architecture/04-engineering-baseline.md` | 413 | `10 个核心 ADR` |

**建议修复**：将"10"改为"14"。

### 5.3 过时的"ADR-001~010"区间（2 处）

| 文件 | 行号 | 过时表述 |
|------|------|----------|
| `10-architecture/README.md` | 230 | `架构决策记录 ADR-001~010（10 个核心决策）` |
| `10-architecture/05-adrs.md` | 1082 | `初始版本（含 ADR-001~010 共 10 个架构决策记录）` |

**说明**：`05-adrs.md:1082` 位于 v0.1.1 版本历史表中，作为 v0.1.1 的历史记录是准确的；但该版本历史表缺少新增 ADR-011~014 的版本条目（应补一条如 `0.2.x | 2026-07-XX | 新增 ADR-011~014（共 14 个架构决策记录）`）。`README.md:230` 的"ADR-001~010（10 个核心决策）"是当前文档定位描述，应更新为"ADR-001~014（14 个核心决策）"。

### 5.4 ADR-011 ~ ADR-014 引用情况

穷举搜索 `ADR-01[1-4]` 在 `05-adrs.md` 之外的引用：**0 处**。即新增的 ADR-011（7 层架构模型范围界定）、ADR-012（微内核化改造技术路线）、ADR-013（版本基线锁定战略）、ADR-014（微内核设计思想来源单一化）**未被任何其他文档引用**。

- ADR-014 在 `05-adrs.md:879` 被 ADR-012 内部引用（"见 ADR-014"），属自引用。
- ADR-008 在 `05-adrs.md:669,696` 被 ADR-009 内部引用（"与 ADR-008 集成"），属自引用。
- ADR-002 在 `40-dataflows/04-scheduling-flow.md:889`、`40-dataflows/README.md:100` 被外部引用 ✅
- ADR-010 在 `50-engineering-standards/40-integration/agentrt_integration.md:816` 被外部引用 ✅
- ADR-004 在 `10-architecture/README.md:239` 被外部引用 ✅

**建议**：ADR-011~014 作为重要战略决策，应在相关设计文档中补引：
- ADR-011（7 层架构模型）应在 `10-architecture/01-system-architecture.md` 引用
- ADR-012（微内核技术路线）应在 `10-architecture/03-microkernel-strategy.md` 引用
- ADR-013（版本基线锁定）应在 `160-compatibility/01-abi-stability.md` 或 `README.md` 版本说明引用
- ADR-014（思想来源单一化）应在 `10-architecture/03-microkernel-strategy.md` 引用

### 5.5 ADR-010 标题与表格不一致（小问题）

| 位置 | 行号 | 表述 |
|------|------|------|
| `05-adrs.md` 表格 | 44 | `ADR-010 \| 与 agentrt 同源且部分代码共享（IRON-9 v2，无适配层天然契合）` |
| `05-adrs.md` 标题 | 705 | `## ADR-010: 与 agentrt 同源且部分代码共享（IRON-9，无适配层天然契合）` |

表格用"IRON-9 v2"，标题用"IRON-9"（缺 v2）。正文（722、735、739 行）均用"IRON-9 v2"。**建议修复**：将 705 行标题改为"IRON-9 v2"。

---

## 六、文件命名一致性（`150-cloud-native` / `150-cloudnative`）

**结论：无问题。** 该历史 bug 已修复。

穷举搜索 `150-cloud-native`（带连字符）：**0 处**。所有 24 处引用均使用正确的 `150-cloudnative`（无连字符），与实际目录名一致。

---

## 七、版本号与计数引用

### 7.1 ADR 计数过时（见 5.2、5.3）

- "10 个核心 ADR" / "10 个 ADR"：3 处（应为 14）
- "ADR-001~010（10 个核心决策）"：1 处（应为 ADR-001~014，14 个）
- `05-adrs.md` 版本历史缺 ADR-011~014 新增条目

### 7.2 工程标准文档计数过时（见 4.4）

- `50-engineering-standards` 标注"8 文档"，实际 18 个顶层 `.md` 文件。

### 7.3 其他计数核对

- "8 子仓"：与实际 8 个子仓（kernel/services/security/memory/cognition/cloudnative/system/tests）一致 ✅
- "12 daemons"：与 `02-services.md` 描述一致 ✅
- "19 模块"（`04-engineering-baseline.md:344`）：指 19 个文档模块层级，与根 README 导航一致 ✅
- "24 原则"（五维正交）：一致 ✅
- "110 项 OS-ACC"（`README.md:112`）：与 `06-acceptance-criteria.md` 的 OS-ACC-001~110 编号范围一致 ✅

---

## 八、子仓命名一致性

### 8.1 子仓名称

8 个子仓（`airymaxos-kernel`、`airymaxos-services`、`airymaxos-security`、`airymaxos-memory`、`airymaxos-cognition`、`airymaxos-cloudnative`、`airymaxos-system`、`airymaxos-tests-linux`）在文档中**命名一致**，未发现拼写变体：
- 无 `airymaxos_cloudnative`（下划线变体）作为子仓名——`airymaxos_*`（下划线）出现处均为 Prometheus 指标名（如 `airymaxos_cognition_latency_seconds`），属指标命名规范，非子仓名错误。
- 无 `airymax-kernel`/`airymax-services` 等缺 `os` 前缀的子仓引用——`airymax-*` 出现处（`90-maintainers-subsystem-model.md`）均为**内核源码树内子系统路径**（如 `kernel/airymax/`、`security/airymax/`），与子仓名（`airymaxos-*`）是刻意区分的两套命名，非错误。
- 无 `agentrt-linux-kernel`/`agentrtos-kernel` 等错误前缀。

### 8.2 `README.md` 子仓表表述不一致（小问题）

`README.md:33-41` 子仓表前 7 行链接文本使用短名（`kernel`/`services`/.../`system`），但第 8 行（`README.md:41`）使用全名 `airymaxos-tests-linux`，与前 7 行风格不一致。属表述统一性小问题，不影响路径正确性。

### 8.3 `airymax-memory` CLI 工具名（待确认）

`190-distribution/03-update-mechanism.md:562` 出现 `airymax-memory migrate --from ... --to ...`。若 `airymax-memory` 是独立 CLI 工具名则无问题；若意在引用子仓，则应为 `airymaxos-memory`。建议核实。

---

## 九、其他结构性观察（非路径引用问题，供参考）

### 9.1 重复编号文件

`180-i18n/` 与 `190-distribution/` 存在**同编号文件重复**，且这些重复文件均未被其他文档引用：

| 目录 | 重复编号 | 文件 |
|------|----------|------|
| `180-i18n/` | 02 | `02-encoding-spec.md` + `02-error-message-i18n.md` |
| `180-i18n/` | 03 | `03-cjk-support.md` + `03-doc-i18n.md` |
| `190-distribution/` | 02 | `02-dnf-repo-design.md` + `02-installer-design.md` |
| `190-distribution/` | 03 | `03-installer-design.md` + `03-update-mechanism.md` |

虽未造成断链（均未被引用），但同编号文件并存影响编号唯一性约定。建议重新编号（如合并或顺延）。

### 9.2 `190-distribution/03-installer-design.md` 与 `02-installer-design.md` 内容疑似重叠

两个 installer-design 文件分属 02、03 编号，需核实是否为重复内容。

---

## 问题统计汇总

| 问题类别 | 问题数 | 备注 |
|----------|--------|------|
| **断链（相对路径）** | **29** | 7 组（A=10, B=2, C=6, D=5, E=3, F=1, G=2） |
| **文档内 TOC 锚点错误** | **5** | 均为 `agentrt-linux`→`airymaxos` 误替换 |
| **跨文档锚点引用** | **0** | 文档中不存在该形式引用 |
| **跨目录引用非对称** | **3 对** | 10-arch⇄30-if、10-arch⇄40-df、30-if⇄40-df |
| **目录路径引用错误** | **151 处** | `docs/AirymaxAgentOS/`=148（16 文件）+ `docs/AirymaxAgentRT/`=3 |
| **ADR 描述错位** | **4 条** | `01-system-architecture.md` ADR-003~006 描述不符 |
| **ADR 计数过时** | **4 处** | "10 个"×3 + "ADR-001~010"×1 |
| **ADR-011~014 未被引用** | **4 条** | 新增 ADR 无任何外部文档引用 |
| **ADR 标题不一致** | **1 处** | ADR-010 标题缺"v2" |
| **`cloud-native` 历史命名 bug** | **0** | 已修复，无残留 |
| **子仓命名变体** | **0** | 命名一致（仅 1 处 CLI 工具名待确认） |
| **`agentrt_contract` 命名不一致** | **多处** | 应为 `agentrt_contract`（路径/链接文本/迁移说明） |
| **工程标准文档计数过时** | **2 处** | "8 文档"应为 18 |
| **重复编号文件** | **6 个文件** | 180-i18n 与 190-distribution 各 2 对 |
| **05-adrs.md 版本历史缺条目** | **1 处** | 缺 ADR-011~014 新增版本记录 |

### 优先级建议

| 优先级 | 问题 | 理由 |
|--------|------|------|
| **P0** | `docs/AirymaxAgentOS/` 路径错误（148 处） | 直接导致 `130-roadmap/06-acceptance-criteria.md`（101 处）与 `08-compliance-checklist.md`（15 处）的验收/合规命令运行失败 |
| **P0** | 29 处断链 | 文档导航失效，特别是 `../../00-architectural-principles.md`（10 处）跨 4 个核心目录 |
| **P1** | ADR 描述错位（`01-system-architecture.md`） | 架构决策摘要与权威定义矛盾，误导读者 |
| **P1** | "10 个核心 ADR"过时计数（4 处） | 与实际 14 个 ADR 不符 |
| **P1** | 5 处 TOC 锚点错误 | 目录跳转失效 |
| **P2** | `agentrt_contract`→`agentrt_contract` 命名 | 跨仓引用一致性 |
| **P2** | ADR-011~014 未被外部引用 | 重要决策缺少传播 |
| **P3** | 跨目录引用非对称（3 对） | 导航闭环优化 |
| **P3** | 重复编号文件（6 个） | 编号唯一性 |
| **P3** | 工程标准文档计数过时 | 表述准确性 |

---

## 附：审查覆盖范围

- 已审查 Markdown 文件数：**110**
- 已校验相对路径链接数：**483**
- 已校验文档内 TOC 锚点数：**190**
- 已校验跨文档锚点数：**0**（不存在）
- 已扫描路径命名模式：`docs/AirymaxAgentOS/`、`docs/AirymaxAgentRT/`、`150-cloud-native`、`agentrt_contract`、`ADR-0XX`、`airymaxos-*`、`airymax-*`

> 本报告为只读审查，未修改任何源文件。所有文件路径均为绝对路径或相对 AirymaxOS 根目录的路径。
