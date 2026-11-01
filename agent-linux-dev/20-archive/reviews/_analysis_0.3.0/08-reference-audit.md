Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 文档引用校对报告（C-2.8）

> **报告定位**: agent-linux（AirymaxOS）方案文档目录 `docs/AirymaxOS/` 的路径引用与交叉引用全面校对报告
> **报告日期**: 2026-07-09
> **报告版本**: v0.3.0
> **校对范围**: `/home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/` 全部 137 个 `.md` 文件
> **机密级别**: 闭源不公开

---

## 1. 校对概述

### 1.1 背景

agent-linux（AirymaxOS）项目文档体系历经多次演进：项目正式英文全称为 `AirymaxAgentOS`（简称为 `AirymaxOS`），仓库别名为 `agent-linux`；文档目录已统一迁移至 `docs/AirymaxOS/`。在 0.1.1 版本迭代过程中，180-i18n 与 190-distribution 模块经历过文件命名冲突修复、50-engineering-standards 子目录从 `50-specifications/` 迁移、90-maintainers-subsystem-model.md 合并入 07 等多次结构调整。这些变更可能遗留旧路径引用、旧文件名引用、跨模块无效链接以及 README 索引与实际文件不一致等问题。

本报告（任务编号 C-2.8）对上述问题进行穷尽式校对，为后续修复提供逐项可执行的修复清单。

### 1.2 校对目标

1. 识别 `docs/AirymaxAgentOS/` 旧路径迁移遗漏
2. 识别指向不存在文件的无效 Markdown 链接
3. 识别交叉引用不一致（旧文件名、错误文件名、stale 状态标签）
4. 校验各模块 README 索引与实际文件清单的一致性
5. 输出逐项修复方案与 Grep 验证命令

### 1.3 校对范围

| 维度 | 数值 |
|------|------|
| 校对目录 | `docs/AirymaxOS/` |
| 顶层模块目录数 | 20（00-requirements ~ 190-distribution） |
| `.md` 文件总数 | 137（含顶层 `README.md` + `TERMINOLOGY.md`） |
| 顶层文件 | 2（README.md、TERMINOLOGY.md） |
| 模块内文件 | 135 |
| 待校对 Markdown 链接总数 | 702 |
| 跨模块（EXTERNAL）链接 | 17 |
| 模块内部（INTERNAL）链接 | 685 |

### 1.4 核心结论速览

| # | 问题类别 | 数量 | 严重程度 |
|---|----------|------|----------|
| 1 | 旧路径迁移遗漏（`docs/AirymaxAgentOS/`） | 0 | — |
| 2 | `AirymaxAgentOS` 字符串引用 | 6（均为合规全称引用） | 信息项 |
| 3 | 无效 Markdown 链接（BROKEN） | 2 | P0 |
| 4 | 错误文件名引用（prose/backtick） | 3 | P1 |
| 5 | Stale "待创建" 标签（文件已存在） | 8 | P1 |
| 6 | Stale 问题报告（问题已修复） | 1 | P2 |
| 7 | 主 README 索引不一致 | 6 类 | P1 |
| 8 | 140-190 模块版本范围自相矛盾 | 6 模块 | P1 |
| 9 | 180-i18n 文档数计数错误 | 1 | P2 |
| 10 | 90-observability 前向引用未标注规划 | 2 文件 | P2 |

> **关键发现**：原担心的 "AirymaxAgentOS → AirymaxOS 旧路径迁移遗漏" **不存在**——全部路径引用均已使用 `docs/AirymaxOS/`，残留的 6 处 `AirymaxAgentOS` 字符串是命名规范约定的正式英文全称（非路径），属合规引用。校对过程中真正的问题集中在 **2 处相对路径深度错误**、**3 处错误文件名引用**、**8 处 stale 状态标签**，以及 **140-190 模块的版本范围声明自相矛盾**。

---

## 2. 校对方法详述

### 2.1 工具链

| 工具 | 用途 |
|------|------|
| `Glob` / `find` | 建立 `docs/AirymaxOS/` 完整文件清单 |
| `Grep`（ripgrep） | 搜索 `AirymaxAgentOS`、`docs/AirymaxAgentOS`、Markdown 链接模式、`待创建`、`占位` 等关键字 |
| `Python 3.12` 脚本 | 批量解析全部 `.md` 文件中的 `[text](target)` 链接，逐条 resolve 相对路径并校验目标存在性 |

### 2.2 校对流程

1. **文件清册建立**：`find docs/AirymaxOS -name "*.md"` 列出全部 137 个文件，建立真实文件清单（SSoT）。
2. **旧路径搜索**：`grep -rn "AirymaxAgentOS"` 与 `grep -rn "docs/AirymaxAgentOS"` 穷举旧路径残留。
3. **Markdown 链接解析**：Python 脚本以正则 `\]\([^)]+\.md[^)]*\)` 抽取所有指向 `.md` 的链接，对每条链接基于源文件目录 `resolve()` 相对路径，校验目标是否存在；区分 INTERNAL（落在 `docs/AirymaxOS/` 内）与 EXTERNAL（跨模块，如 `../../AirymaxRT/`、`../../../docs-closed/`）。
4. **非链接引用搜索**：`grep -rnE '`[^`]*\.md[^`]*`'` 搜索反引号包裹的 prose 路径引用（这些不会被 Markdown 渲染器校验，但仍是事实性引用）。
5. **交叉引用关键字搜索**：`grep -rnE '参见|详见|相关文档|参考文档'` 搜索中文交叉引用关键字。
6. **README 索引一致性校验**：逐模块读取 README 的"文档索引"章节，与 `find` 实际文件清单比对，识别数量声明与状态声明的矛盾。
7. **版本范围声明校验**：交叉比对主 README、各模块 README 头部"优先级"声明、§3.1"0.1.1 版本范围"声明、`130-roadmap/` 路线图与验收标准中的版本范围声明。

### 2.3 校对覆盖度

| 校对维度 | 覆盖率 |
|----------|--------|
| Markdown 链接目标存在性 | 100%（702 条全部校验） |
| 旧路径残留搜索 | 100%（全目录递归） |
| README 索引 vs 实际文件 | 100%（20 模块逐个比对） |
| 版本范围声明一致性 | 100%（主 README + 全部模块 README + 路线图 + 验收标准） |

---

## 3. 旧路径引用清单（AirymaxAgentOS → AirymaxOS 迁移遗漏）

### 3.1 旧路径残留搜索结果

| 搜索模式 | 命中数 | 结论 |
|----------|--------|------|
| `docs/AirymaxAgentOS`（旧路径） | 0 | **无残留** |
| `AirymaxAgentOS/`（带斜杠的路径片段） | 0 | **无残留** |
| `AirymaxAgentOS`（裸字符串） | 6 | 全部为合规全称引用（见 §3.2） |

### 3.2 `AirymaxAgentOS` 字符串逐项清单

下列 6 处 `AirymaxAgentOS` 字符串**均非路径引用**，而是命名规范约定的"正式英文全称"使用，属合规引用，无需修改。

| # | 文件 | 行号 | 上下文 | 性质 |
|---|------|------|--------|------|
| 1 | `README.md` | 6 | `正式全称: agent-linux（极境智能体操作系统，正式英文名：AirymaxAgentOS，简称 AirymaxOS）` | 合规全称 |
| 2 | `README.md` | 13 | `agent-linux（正式英文名：AirymaxAgentOS，简称 AirymaxOS，中文：极境智能体操作系统）` | 合规全称 |
| 3 | `00-requirements/README.md` | 6 | `正式全称: AirymaxAgentOS（极境智能体操作系统，简称 AirymaxOS）` | 合规全称 |
| 4 | `50-engineering-standards/00-engineering-standards-handbook.md` | 312 | 命名对照表行 `agent-linux \| AirymaxAgentOS 极境智能体操作系统 \| agent-linux / AirymaxOS` | 合规全称 |
| 5 | `50-engineering-standards/00-engineering-standards-handbook.md` | 316 | `正式英文名：全称使用 "AirymaxAgentOS"（无空格），简称使用 "AirymaxOS"` | 命名规范定义 |
| 6 | `50-engineering-standards/00-engineering-standards-handbook.md` | 452 | 路线图条目 `第 2 周 \| 命名体系修正（AirymaxAgentOS 全称）` | 合规引用 |

### 3.3 命名规范确认

`50-engineering-standards/00-engineering-standards-handbook.md:316` 明确约定：

> **正式英文名**：全称使用 "AirymaxAgentOS"（无空格），简称使用 "AirymaxOS"

即 `AirymaxAgentOS`（全称）与 `AirymaxOS`（简称）是**并存的命名规范**，而非"旧名 → 新名"的迁移关系。任务前置假设中"项目从 AirymaxAgentOS 改名为 AirymaxOS"应修正为"项目全称为 AirymaxAgentOS、简称为 AirymaxOS，二者并行使用"。所有路径引用（`docs/AirymaxOS/`）已统一使用简称，无迁移遗漏。

---

## 4. 无效链接清单（BROKEN Markdown Links）

### 4.1 校验统计

| 指标 | 数值 |
|------|------|
| 校验链接总数 | 702 |
| OK（目标存在） | 700 |
| BROKEN（目标不存在） | 2 |
| 链接有效率 | 99.72% |
| 跨模块（EXTERNAL）链接 | 17（全部 OK） |

### 4.2 无效链接逐项清单

仅 2 条 BROKEN 链接，均位于同一文件、同一章节，根因相同（相对路径深度计算错误）。

| # | 引用位置 | 行号 | 链接文本 | 链接目标（原文） | 期望解析目标 | 实际解析路径 | 状态 |
|---|----------|------|----------|------------------|--------------|-------------|------|
| L-1 | `50-engineering-standards/30-runtime-interfaces/README.md` | 503 | 体系并行论 | `../../AirymaxRT/00-basic-theories/01-mcis-cn.md` | `docs/AirymaxRT/00-basic-theories/01-mcis-cn.md` | `docs/AirymaxOS/AirymaxRT/00-basic-theories/01-mcis-cn.md` | BROKEN |
| L-2 | `50-engineering-standards/30-runtime-interfaces/README.md` | 504 | 系统设计原则 | `../../AirymaxRT/00-basic-theories/04-design-principles-cn.md` | `docs/AirymaxRT/00-basic-theories/04-design-principles-cn.md` | `docs/AirymaxOS/AirymaxRT/00-basic-theories/04-design-principles-cn.md` | BROKEN |

### 4.3 根因分析

源文件位于 `docs/AirymaxOS/50-engineering-standards/30-runtime-interfaces/README.md`，相对于 `docs/` 根目录的深度为 **3 级**：

```
docs/                                          ← 目标基线
└── AirymaxOS/                                  ← ../
    └── 50-engineering-standards/               ← ../../
        └── 30-runtime-interfaces/             ← ../../..  (当前文件所在目录)
            └── README.md
```

要回退到 `docs/` 根目录需要 **3 个 `../`**（即 `../../../`），但链接仅写了 **2 个 `../`**（即 `../../`），导致解析时少回退一级，落入 `docs/AirymaxOS/AirymaxRT/`（不存在），而非 `docs/AirymaxRT/`（存在）。

### 4.4 目标文件存在性确认

```
docs/AirymaxRT/00-basic-theories/01-mcis-cn.md                       ✅ 存在
docs/AirymaxRT/00-basic-theories/04-design-principles-cn.md          ✅ 存在
```

目标文件本身存在，仅相对路径写错。修复方式见 §7.1。

### 4.5 跨模块（EXTERNAL）链接抽检

17 条跨模块链接全部 OK，下表为抽检样本（完整清单见校验脚本输出）：

| 引用位置 | 目标 | 状态 |
|----------|------|------|
| `00-requirements/README.md:402` | `../../AirymaxRT/00-architectural-principles.md` | OK |
| `10-architecture/03-microkernel-strategy.md:12` | `../../../docs-closed/agent-linux-dev/_research_0.2.5/01-sel4-deep-analysis.md` | OK |
| `20-modules/01-kernel.md:1068` | `../../../docs-closed/agent-linux-dev/_research_0.2.5/01-sel4-deep-analysis.md` | OK |
| `50-engineering-standards/20-contracts/README.md:276` | `../../../AirymaxRT/50-specifications/10-contracts/03-protocol-contract.md` | OK |

> 注意：`50-engineering-standards/20-contracts/README.md` 同样位于 3 级深度，其跨模块链接正确使用了 3 个 `../`（`../../../AirymaxRT/`）。这进一步证实 §4.3 的根因分析——同一项目内存在深度计算不一致：3 级深度的文件有的用 2 个 `../`、有的用 3 个 `../`。

---

## 5. 交叉引用不一致清单

### 5.1 错误文件名引用（prose / backtick）

下列引用以反引号包裹的 prose 形式出现（非 Markdown 链接），不会被渲染器校验，但属事实性路径引用错误。目标文件实际命名为 `00-architectural-principles.md`（小写、带 `00-` 前缀），而引用使用了 `ARCHITECTURAL_PRINCIPLES.md`（大写、无前缀）。

| # | 文件 | 行号 | 错误引用 | 正确文件名 | 备注 |
|---|------|------|----------|-----------|------|
| F-1 | `50-engineering-standards/README.md` | 8 | `` `docs/AirymaxRT/ARCHITECTURAL_PRINCIPLES.md` `` | `docs/AirymaxRT/00-architectural-principles.md` | 同源映射字段 |
| F-2 | `50-engineering-standards/README.md` | 28 | `` `ARCHITECTURAL_PRINCIPLES.md` `` | `00-architectural-principles.md` | 工程标准三大支柱表 |
| F-3 | `50-engineering-standards/README.md` | 441 | `` `docs/AirymaxRT/ARCHITECTURAL_PRINCIPLES.md` `` | `docs/AirymaxRT/00-architectural-principles.md` | §10.1 同源文档列表 |

> **一致性对比**：项目内其余 19 处引用（`00-requirements/`、`10-architecture/`、`40-dataflows/`、`130-roadmap/` 等）均使用正确的 `00-architectural-principles.md`，仅 `50-engineering-standards/README.md` 的 3 处使用了错误文件名，属孤立错误。

### 5.2 Stale "待创建" 标签（文件已存在）

下列引用将**已存在**的文件标注为"（待创建）"，属 stale 状态标签。这些文件实际已在 0.1.1 版本创建完成。

| # | 文件 | 行号 | 引用 | 被引文件实际状态 |
|---|------|------|------|-----------------|
| S-1 | `140-application-development/01-agent-lifecycle.md` | 455 | `[Token 预算契约](04-token-budget.md)（待创建）` | ✅ 存在（1021 行） |
| S-2 | `140-application-development/01-agent-lifecycle.md` | 456 | `[MemoryRovol API](05-memory-rovol-api.md)（待创建）` | ✅ 存在 |
| S-3 | `140-application-development/01-agent-lifecycle.md` | 457 | `[Agent 部署与运行](06-agent-deployment.md)（待创建）` | ✅ 存在（1409 行） |
| S-4 | `140-application-development/07-syscall-registry.md` | 923 | `[04-token-budget.md](04-token-budget.md) — Token 预算契约（待创建）` | ✅ 存在 |
| S-5 | `140-application-development/07-syscall-registry.md` | 924 | `[05-memory-rovol-api.md](05-memory-rovol-api.md) — 记忆卷载 API（待创建）` | ✅ 存在 |
| S-6 | `140-application-development/07-syscall-registry.md` | 925 | `[06-agent-deployment.md](06-agent-deployment.md) — Agent 部署与运行（待创建）` | ✅ 存在 |
| S-7 | `140-application-development/04-token-budget.md` | 1021 | `[05-memory-rovol-api.md](05-memory-rovol-api.md) — 记忆卷载 API（待创建）` | ✅ 存在 |
| S-8 | `140-application-development/04-token-budget.md` | 1022 | `[06-agent-deployment.md](06-agent-deployment.md) — Agent 部署与运行（待创建）` | ✅ 存在 |

> **影响评估**：链接本身有效（目标存在），但"（待创建）"标签会误导读者与维护者，使其误以为这些文件尚未编写，可能引发重复撰写或跳过阅读。其中 S-4/5/6 与 §5.3 的 stale 问题报告直接相关。

### 5.3 Stale 问题报告（问题已修复）

| # | 文件 | 章节 | 问题描述 | 实际状态 |
|---|------|------|----------|----------|
| P-1 | `140-application-development/07-syscall-registry.md` | §11.2（行 697-706） | "P1-SYS-02: 生命周期文档交叉引用错误（已识别）"——声称 `01-agent-lifecycle.md` 第 9 章存在文件名错配（`03-token-budget.md`→`04-token-budget.md` 等） | **已修复**：当前 `01-agent-lifecycle.md:453-457` 的引用文件名均已正确（`03-agent-orchestration.md`、`04-token-budget.md`、`05-memory-rovol-api.md`、`06-agent-deployment.md`），与 README 实际文件名一致。该问题报告应更新为"已修复"或删除。 |

### 5.4 前向引用未标注规划状态

下列文件在 prose 中引用了尚未创建的 1.0.1 规划文档，但未标注"（规划中/待创建）"，可能误导读者认为这些文档已存在。

| # | 文件 | 行号 | 引用内容 | 目标状态 |
|---|------|------|----------|----------|
| F-4 | `90-observability/01-ftrace-framework.md` | 481 | "同模块文档：`03-perf-analysis.md`、`05-debugfs-tracefs.md`、`06-user-events.md`、`08-agent-tracing.md`" | 4 个文件均不存在（1.0.1 规划） |
| F-5 | `90-observability/02-ebpf-probes.md` | 608 | "同模块文档：`03-perf-analysis.md`、`06-user-events.md`、`07-token-efficiency.md`、`08-agent-tracing.md`" | 4 个文件均不存在（1.0.1 规划） |

> **对比参考**：`80-testing/01-kunit-framework.md:396` 与 `02-kselftest.md:458-459` 同样引用了不存在的 `03-kernel-selftests.md`、`08-agent-contract-testing.md`，但**正确标注了"（待创建）"**，是良好的实践范例。90-observability 应参照此惯例补标。

> **README 索引一致性**：`90-observability/README.md` 的文件树（行 105-115）列出了 `03-perf-analysis.md` 至 `09-memory-monitoring.md` 共 7 个规划文件，作为模块索引这是可接受的（roadmap 形式），但 prose 引用应同步标注规划状态。

---

## 6. README 索引与实际文件不一致清单

### 6.1 实际文件清册（SSoT）

下表为 `find` 命令实测的各模块 `.md` 文件数（recursive，含 README）。

| 模块 | 实际文件数 | 模块 | 实际文件数 |
|------|-----------|------|-----------|
| `00-requirements/` | 4 | `110-security/` | 4 |
| `10-architecture/` | 6 | `120-development-process/` | 3 |
| `20-modules/` | 9 | `130-roadmap/` | 7 |
| `30-interfaces/` | 5 | `140-application-development/` | 8 |
| `40-dataflows/` | 5 | `150-cloudnative/` | 6 |
| `50-engineering-standards/` | 38 | `160-compatibility/` | 6 |
| `60-driver-model/` | 3 | `170-performance/` | 7 |
| `70-build-system/` | 3 | `180-i18n/` | 6 |
| `80-testing/` | 3 | `190-distribution/` | 6 |
| `90-observability/` | 3 | 顶层 `README.md` + `TERMINOLOGY.md` | 2 |
| `100-operations/` | 3 | **总计** | **137** |

### 6.2 主 README.md 索引不一致

| # | 位置 | 声明内容 | 实际情况 | 不一致类型 |
|---|------|----------|----------|-----------|
| R-1 | `README.md:53` vs `:98` | 第 53 行"40-dataflows/ # 数据流程设计层（5 文档）" vs 第 98 行"文档数 \| 4" | 实际 5 文档 | **计数口径不一致**：第 98 行未将 README 计入，而同表其余行（00/10/20/30）均将 README 计入 |
| R-2 | `README.md:82` 与 `:104` | "50-engineering-standards \| 8 文档" / "✅ 8 文档" | 实际 38 文档 | **严重过时**：8 为初始 0.1.1 规划数，现已扩展至 38（含 5 子目录迁移与 6 扩展专题） |
| R-3 | `README.md:110` | "110-security \| 安全加固（LSM 框架 + Landlock 沙箱）\| ✅ 01+02" | 实际含 03-capability-model.md（4 文档） | **未反映新增**：03-capability-model.md 已在 0.1.1 完成（见 110-security/README.md:116 标 ✅） |
| R-4 | `README.md:65-70` | 140-190 模块均标注"README 占位 1.0.1" | 6 模块实际均已含完整文档集（140=8, 150=6, 160=6, 170=7, 180=6, 190=6） | **状态声明过时**：实际已在 0.1.1 完成全部文档 |
| R-5 | `README.md:118-123` | 140-190 模块"0.1.1 状态 \| README 占位" | 同 R-4 | 同 R-4 |
| R-6 | `README.md:85-86` | "P1 模块 140-170（4 模块）README 占位" / "P2 模块 180-190（2 模块）README 占位" | 6 模块均已完成完整文档 | 同 R-4 |

### 6.3 140-190 模块 README 版本范围自相矛盾

下表为各模块 README 内部的版本范围声明矛盾——头部"优先级"字段声称"0.1.1 仅创建 README 占位"，而正文 §3.1"0.1.1 版本范围"却声明"全部文档已在 0.1.1 完成"。

| # | 模块 | 头部声明（行 8） | 正文声明（§3.1） | 实际文件 |
|---|------|-----------------|-----------------|----------|
| M-1 | `140-application-development/README.md` | "0.1.1 README + 01，1.0.1 完成全部 7 文档" | "140 模块 7/7 文档全部完成（100%）" | 8 文档（含 README） |
| M-2 | `150-cloudnative/README.md` | "0.1.1 仅创建 README 占位，1.0.1 完成 5 文档" | "150 模块 5/5 文档全部完成（100%）" | 6 文档 |
| M-3 | `160-compatibility/README.md` | "0.1.1 仅创建 README 占位，1.0.1 完成 5 文档" | "160 模块 5/5 文档全部完成（100%）" | 6 文档 |
| M-4 | `170-performance/README.md` | "0.1.1 仅创建 README 占位，1.0.1 完成 6 文档" | "170 模块 6/6 文档全部完成（100%）" | 7 文档 |
| M-5 | `180-i18n/README.md` | "0.1.1 仅创建 README 占位，1.0.1 完成 4 文档" | §3.1 列出 5 篇文档（01-05） | 6 文档 |
| M-6 | `190-distribution/README.md` | "0.1.1 仅创建 README 占位，1.0.1 完成 5 文档" | "190 模块 5/5 文档全部完成（100%）" | 6 文档 |

> **根因推断**：140-190 模块的文档实际已在 0.1.1 阶段全部撰写完成（正文 §3.1 反映现状），但 README 头部的"优先级"字段与脚注仍停留在最初的"0.1.1 占位、1.0.1 完成"规划表述，未随文档实际完成而更新。这导致同一文件内"占位"与"100% 完成"并存的自相矛盾。

### 6.4 180-i18n 文档数计数错误

| # | 文件 | 行号 | 声明 | 实际 |
|---|------|------|------|------|
| C-1 | `180-i18n/README.md` | 8 | "1.0.1 完成 4 文档" | 非 README 文档实际为 5（01-locale-design、02-encoding-spec、03-error-message-i18n、04-cjk-support、05-doc-i18n） |

> **对比**：`130-roadmap/03-resource-estimation.md:118` 声明"180-i18n/ \| 6 \| 40"（含 README 共 6，正确）。`180-i18n/README.md:101` §3.1 列出 5 篇非 README 文档。仅头部第 8 行的"4 文档"为笔误（应为 5）。

### 6.5 50-engineering-standards README 与主 README 计数不一致

| 来源 | 声明 | 备注 |
|------|------|------|
| `50-engineering-standards/README.md:93` | "共 38 个文档（含本 README）" | 与实际一致（38） |
| `50-engineering-standards/README.md:148` | "核心章节（00-09）：8 主题 + 1 合规 + 1 许可证 = 10 文档" | 与实际一致 |
| `50-engineering-standards/README.md:433` | "0.1.1 版本总产出 ~64 文档（... 40-dataflows 4 ...）" | 40-dataflows 计为 4（未含 README），与主 README 第 53 行"5 文档"口径不一致 |
| 主 `README.md:82` | "50-engineering-standards 8 文档" | 与子 README 的 38 严重不符（过时） |
| `130-roadmap/03-resource-estimation.md:105` | "50-engineering-standards/ \| 8 \| 240" | 同样过时（实际 38） |
| `130-roadmap/06-acceptance-criteria.md:88` | "OS-ACC-001 ★ \| 50-engineering-standards/ 8 文档完成 \| ≥8" | 验收阈值 ≥8，实际 38 已远超（验收通过），但"8 文档完成"的描述性文字过时 |

### 6.6 130-roadmap 验收阈值与 140-190 完成度声明矛盾

下表为 `130-roadmap/06-acceptance-criteria.md` 的 1.0.1 验收阈值与 140-190 模块 README"100% 完成"声明的矛盾。这些阈值为 1.0.1 规划目标，0.1.1 不要求达成属正常；但模块 README 声称"0.1.1 100% 完成"则与阈值隐含的"1.0.1 才完成"语义冲突。

| 验收项 | 模块 | 阈值 | 0.1.1 实际 | 模块 README 声明 |
|--------|------|------|-----------|-----------------|
| OS-ACC-091 | 140-application-development | ≥9 | 8 | "7/7 100% 完成" |
| OS-ACC-092 | 150-cloudnative | ≥8 | 6 | "5/5 100% 完成" |
| OS-ACC-101 | 160-compatibility | ≥8 | 6 | "5/5 100% 完成" |
| OS-ACC-102 | 170-performance | ≥8 | 7 | "6/6 100% 完成" |

> **说明**：验收阈值采用"含 README 与子目录"的计数口径，模块 README 的"X/X"采用"非 README 主文档"口径，二者口径不同导致表面矛盾。但根本问题仍是 §6.3 的版本范围声明错位——0.1.1 完成的文档不应在 README 中表述为"1.0.1 完成"。

---

## 7. 修复方案

### 7.1 无效链接修复（P0）

| # | 文件 | 行号 | 原文 | 修复为 | 操作 |
|---|------|------|------|--------|------|
| FIX-01 | `50-engineering-standards/30-runtime-interfaces/README.md` | 503 | `[体系并行论](../../AirymaxRT/00-basic-theories/01-mcis-cn.md)` | `[体系并行论](../../../AirymaxRT/00-basic-theories/01-mcis-cn.md)` | 增加 1 级 `../` |
| FIX-02 | `50-engineering-standards/30-runtime-interfaces/README.md` | 504 | `[系统设计原则](../../AirymaxRT/00-basic-theories/04-design-principles-cn.md)` | `[系统设计原则](../../../AirymaxRT/00-basic-theories/04-design-principles-cn.md)` | 增加 1 级 `../` |

### 7.2 错误文件名修复（P1）

| # | 文件 | 行号 | 原文 | 修复为 |
|---|------|------|------|--------|
| FIX-03 | `50-engineering-standards/README.md` | 8 | `` agentrt `docs/AirymaxRT/ARCHITECTURAL_PRINCIPLES.md` `` | `` agentrt `docs/AirymaxRT/00-architectural-principles.md` `` |
| FIX-04 | `50-engineering-standards/README.md` | 28 | `` `ARCHITECTURAL_PRINCIPLES.md`（S/K/C/E/A 五维） `` | `` `00-architectural-principles.md`（S/K/C/E/A 五维） `` |
| FIX-05 | `50-engineering-standards/README.md` | 441 | `` `docs/AirymaxRT/ARCHITECTURAL_PRINCIPLES.md` `` | `` `docs/AirymaxRT/00-architectural-principles.md` `` |

### 7.3 Stale "待创建" 标签修复（P1）

| # | 文件 | 行号 | 原文 | 修复为 |
|---|------|------|------|--------|
| FIX-06 | `140-application-development/01-agent-lifecycle.md` | 455 | `[Token 预算契约](04-token-budget.md)（待创建）` | `[Token 预算契约](04-token-budget.md)` |
| FIX-07 | `140-application-development/01-agent-lifecycle.md` | 456 | `[MemoryRovol API](05-memory-rovol-api.md)（待创建）` | `[MemoryRovol API](05-memory-rovol-api.md)` |
| FIX-08 | `140-application-development/01-agent-lifecycle.md` | 457 | `[Agent 部署与运行](06-agent-deployment.md)（待创建）` | `[Agent 部署与运行](06-agent-deployment.md)` |
| FIX-09 | `140-application-development/07-syscall-registry.md` | 923 | `[04-token-budget.md](04-token-budget.md) — Token 预算契约（待创建）` | `[04-token-budget.md](04-token-budget.md) — Token 预算契约` |
| FIX-10 | `140-application-development/07-syscall-registry.md` | 924 | `[05-memory-rovol-api.md](05-memory-rovol-api.md) — 记忆卷载 API（待创建）` | `[05-memory-rovol-api.md](05-memory-rovol-api.md) — 记忆卷载 API` |
| FIX-11 | `140-application-development/07-syscall-registry.md` | 925 | `[06-agent-deployment.md](06-agent-deployment.md) — Agent 部署与运行（待创建）` | `[06-agent-deployment.md](06-agent-deployment.md) — Agent 部署与运行` |
| FIX-12 | `140-application-development/04-token-budget.md` | 1021 | `[05-memory-rovol-api.md](05-memory-rovol-api.md) — 记忆卷载 API（待创建）` | `[05-memory-rovol-api.md](05-memory-rovol-api.md) — 记忆卷载 API` |
| FIX-13 | `140-application-development/04-token-budget.md` | 1022 | `[06-agent-deployment.md](06-agent-deployment.md) — Agent 部署与运行（待创建）` | `[06-agent-deployment.md](06-agent-deployment.md) — Agent 部署与运行` |

### 7.4 Stale 问题报告修复（P2）

| # | 文件 | 章节 | 操作 |
|---|------|------|------|
| FIX-14 | `140-application-development/07-syscall-registry.md` | §11.2（行 697-706） | 将标题"P1-SYS-02: 生命周期文档交叉引用错误（已识别）"改为"（已修复，2026-07-09）"，并在描述中追加"经 C-2.8 校对确认，01-agent-lifecycle.md 第 9 章引用已与 README 实际文件名一致，问题关闭" |

### 7.5 主 README 索引修复（P1）

| # | 文件 | 行号 | 原文 | 修复为 |
|---|------|------|------|--------|
| FIX-15 | `README.md` | 98 | `\| [40-dataflows](40-dataflows/README.md) \| 数据流程（调度流 + IPC 流 + 记忆卷载流 + 认知循环流） \| 4 \|` | 将"4"改为"5"（与第 53 行及同表口径一致） |
| FIX-16 | `README.md` | 82 | `\| **工程标准**  \| 50-engineering-standards \| 8 文档 ✅  \| 持续完善 \|` | 改为"38 文档 ✅" |
| FIX-17 | `README.md` | 104 | `\| [50-engineering-standards](...) \| ... \| ✅ 8 文档 \|` | 改为"✅ 38 文档（含 5 子目录）" |
| FIX-18 | `README.md` | 110 | `\| [110-security](...) \| 安全加固（LSM 框架 + Landlock 沙箱）\| ✅ 01+02 \|` | 改为"✅ 01+02+03（含 capability 模型）" |
| FIX-19 | `README.md` | 65-70 | 140-190 模块均标注"README 占位 1.0.1" | 改为"0.1.1 完成 / 1.0.1 实施"（与各模块 README §3.1 一致） |
| FIX-20 | `README.md` | 118-123 | 140-190 模块"0.1.1 状态 \| README 占位" | 改为"0.1.1 文档完成 / 1.0.1 实施" |

### 7.6 140-190 模块 README 版本范围声明修复（P1）

对下表 6 个模块 README，统一将头部"优先级"字段与脚注的版本范围表述从"0.1.1 占位 / 1.0.1 完成"修正为"0.1.1 文档完成 / 1.0.1 实施"，与正文 §3.1 一致。

| # | 文件 | 行号 | 原文（摘要） | 修复为（摘要） |
|---|------|------|-------------|---------------|
| FIX-21 | `140-application-development/README.md` | 8 | "P1（0.1.1 README + 01，1.0.1 完成全部 7 文档）" | "P1（0.1.1 完成 7 文档，1.0.1 实施验证）" |
| FIX-22 | `150-cloudnative/README.md` | 8 | "P1（0.1.1 仅创建 README 占位，1.0.1 完成 5 文档）" | "P1（0.1.1 完成 5 文档，1.0.1 实施验证）" |
| FIX-23 | `160-compatibility/README.md` | 8 | "P1（0.1.1 仅创建 README 占位，1.0.1 完成 5 文档）" | "P1（0.1.1 完成 5 文档，1.0.1 实施验证）" |
| FIX-24 | `170-performance/README.md` | 8 | "P1（0.1.1 仅创建 README 占位，1.0.1 完成 6 文档）" | "P1（0.1.1 完成 6 文档，1.0.1 实施验证）" |
| FIX-25 | `180-i18n/README.md` | 8 | "P2（0.1.1 仅创建 README 占位，1.0.1 完成 4 文档）" | "P2（0.1.1 完成 5 文档，1.0.1 实施验证）"（同时修正 4→5） |
| FIX-26 | `190-distribution/README.md` | 8 | "P2（0.1.1 仅创建 README 占位，1.0.1 完成 5 文档）" | "P2（0.1.1 完成 5 文档，1.0.1 实施验证）" |

> 同步修复：上述 6 文件的脚注（如 `190-distribution/README.md:102` "190 模块 5/5 文档全部完成（100%）"已正确，无需改；但 `180-i18n/README.md:192` "0.1.1 P2 占位，1.0.1 完成 4 文档"需同步改为"0.1.1 完成 5 文档，1.0.1 实施验证"）。

### 7.7 前向引用标注修复（P2）

| # | 文件 | 行号 | 操作 |
|---|------|------|------|
| FIX-27 | `90-observability/01-ftrace-framework.md` | 481 | 在引用的 `03-perf-analysis.md`、`05-debugfs-tracefs.md`、`06-user-events.md`、`08-agent-tracing.md` 后追加"（1.0.1 规划）"标注 |
| FIX-28 | `90-observability/02-ebpf-probes.md` | 608 | 在引用的 `03-perf-analysis.md`、`06-user-events.md`、`07-token-efficiency.md`、`08-agent-tracing.md` 后追加"（1.0.1 规划）"标注 |

### 7.8 路线图与资源估算同步修复（P2）

| # | 文件 | 行号 | 原文 | 修复为 |
|---|------|------|------|--------|
| FIX-29 | `130-roadmap/03-resource-estimation.md` | 105 | `\| 50-engineering-standards/ \| 8 \| 240 \| P0 \| ...` | 改为"38"（同步更新总计 122→152） |
| FIX-30 | `130-roadmap/README.md` | 30 | "工程标准 8 + 架构 6 + 模块 9 + 接口 5 + 数据流 4 + P0 模块 21 + 路线图 7，共 ~64 文档" | 同步更新工程标准数与总数 |
| FIX-31 | `130-roadmap/README.md` | 148-149 | "P1 模块（140-170）仅 README.md 占位 / 合计 ~64 文档" | 改为反映 140-190 已完成的现状 |

> **修复约束**：130-roadmap 的验收阈值（OS-ACC-001 的 ≥8 等）**不需修改**——阈值是 1.0.1 的最低门槛，0.1.1 已超额完成属正常。仅需更新描述性的"X 文档完成"文字与资源估算的工时表。

---

## 8. 验证方法

### 8.1 无效链接验证

```bash
# 验证 FIX-01/02：30-runtime-interfaces/README.md 的 2 条链接已修复
cd /home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS
python3 - <<'PY'
import re, pathlib
ROOT = pathlib.Path(".")
f = ROOT / "50-engineering-standards/30-runtime-interfaces/README.md"
text = f.read_text(encoding="utf-8")
for ln, line in enumerate(text.splitlines(), 1):
    for m in re.finditer(r'\]\(([^)]+\.md[^)]*)\)', line):
        tgt = m.group(1).split("#")[0].split(" ")[0]
        if tgt.startswith(("http", "mailto")): continue
        ok = (f.parent / tgt).resolve().exists()
        print(f"L{ln}: {tgt} -> {'OK' if ok else 'BROKEN'}")
PY
# 预期：0 条 BROKEN（修复前为 2 条）
```

### 8.2 错误文件名验证

```bash
# 验证 FIX-03/04/05：ARCHITECTURAL_PRINCIPLES.md 已全部改为 00-architectural-principles.md
grep -rn "ARCHITECTURAL_PRINCIPLES" docs/AirymaxOS/
# 预期：0 处残留
grep -rn "00-architectural-principles" docs/AirymaxOS/50-engineering-standards/README.md
# 预期：≥3 处（行 8/28/441）
```

### 8.3 Stale "待创建" 验证

```bash
# 验证 FIX-06~13：140-application-development/ 下不再有指向已存在文件的"（待创建）"
grep -rn "待创建" docs/AirymaxOS/140-application-development/
# 预期：0 处残留（修复前为 8 处）
```

### 8.4 全量链接回归验证

```bash
# 修复后全量回归：所有 .md 链接均应 OK
cd /home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS
python3 - <<'PY'
import re, pathlib
ROOT = pathlib.Path(".")
broken = 0; total = 0
for f in ROOT.rglob("*.md"):
    text = f.read_text(encoding="utf-8")
    for ln, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r'\]\(([^)]+\.md[^)]*)\)', line):
            tgt = m.group(1).split("#")[0].split(" ")[0]
            if tgt.startswith(("http", "mailto")): continue
            total += 1
            if not (f.parent / tgt).resolve().exists():
                broken += 1
                print(f"BROKEN: {f.relative_to(ROOT)}:{ln} {tgt}")
print(f"TOTAL={total} BROKEN={broken}")
PY
# 预期：TOTAL≈702 BROKEN=0
```

### 8.5 README 索引一致性验证

```bash
# 验证主 README 的模块文档数与实际一致
for d in docs/AirymaxOS/*/; do
  actual=$(find "$d" -name "*.md" | wc -l)
  echo "$d : $actual"
done
# 人工比对 README.md 第 92-123 行表格中的"文档数"列

# 验证 140-190 模块 README 头部不再含"仅创建 README 占位"
grep -n "仅创建 README 占位" docs/AirymaxOS/{140,150,160,170,180,190}-*/README.md
# 预期：0 处残留
```

### 8.6 旧路径残留验证

```bash
# 验证无 docs/AirymaxAgentOS 旧路径残留
grep -rn "docs/AirymaxAgentOS" docs/AirymaxOS/
# 预期：0 处

# 验证 AirymaxAgentOS 仅作为命名规范全称出现（合规）
grep -rn "AirymaxAgentOS" docs/AirymaxOS/ | wc -l
# 预期：6（均为命名规范全称引用，非路径）
```

---

## 9. 相关文档

### 9.1 本报告引用的校对对象

- `docs/AirymaxOS/README.md`——主索引（含模块导航与文档数声明）
- `docs/AirymaxOS/50-engineering-standards/README.md`——工程标准主索引（含 `ARCHITECTURAL_PRINCIPLES.md` 错误引用与 38 文档清单）
- `docs/AirymaxOS/50-engineering-standards/30-runtime-interfaces/README.md`——运行时接口索引（含 2 条 BROKEN 链接）
- `docs/AirymaxOS/140-application-development/README.md`——Agent 应用开发索引（版本范围自相矛盾）
- `docs/AirymaxOS/140-application-development/01-agent-lifecycle.md`——含 stale "待创建" 标签
- `docs/AirymaxOS/140-application-development/07-syscall-registry.md`——含 stale 问题报告与 stale 标签
- `docs/AirymaxOS/{150,160,170,180,190}-*/README.md`——版本范围自相矛盾的 5 个模块
- `docs/AirymaxOS/90-observability/{01,02}.md`——前向引用未标注规划
- `docs/AirymaxOS/130-roadmap/README.md`、`03-resource-estimation.md`、`06-acceptance-criteria.md`——路线图与验收阈值
- `docs/AirymaxOS/50-engineering-standards/00-engineering-standards-handbook.md`——命名规范定义（AirymaxAgentOS 全称 / AirymaxOS 简称）

### 9.2 同批分析报告

- `docs-closed/agent-linux-dev/_analysis_0.3.0/01-lessons-learned.md`——经验总结
- `docs-closed/agent-linux-dev/_analysis_0.3.0/02-version-planning-decision.md`——版本规划决策报告
- `docs-closed/agent-linux-dev/_analysis_0.3.0/04-microkernel-source-sel4-only.md`——微内核 seL4 来源分析

### 9.3 外部依赖文档（校验为 OK）

- `docs/AirymaxRT/00-architectural-principles.md`——五维正交 24 原则（被 19 处正确引用）
- `docs/AirymaxRT/00-basic-theories/01-mcis-cn.md`——体系并行论（FIX-01 目标）
- `docs/AirymaxRT/00-basic-theories/04-design-principles-cn.md`——系统设计原则（FIX-02 目标）
- `docs/AirymaxRT/50-specifications/10-contracts/03-protocol-contract.md`——IPC 协议契约
- `docs-closed/agent-linux-dev/_research_0.2.5/01-sel4-deep-analysis.md`——seL4 深度分析
- `docs-closed/agent-linux-dev/_research_0.2.5/02-linux-7.1-forward-looking.md`——Linux 7.1 前瞻研究
- `docs-closed/agent-linux-dev/agent-linux基本工程标准规范.md`——工程标准规范（闭源）

---

## 10. 附录：校对统计汇总

### 10.1 链接校验汇总表

| 模块 | OK 链接数 | BROKEN 链接数 |
|------|----------|--------------|
| `00-requirements/` | 26 | 0 |
| `10-architecture/` | 54 | 0 |
| `20-modules/` | 84 | 0 |
| `30-interfaces/` | 63 | 0 |
| `40-dataflows/` | 52 | 0 |
| `50-engineering-standards/` | 242 | 2 |
| `60-driver-model/` | 0 | 0 |
| `70-build-system/` | 0 | 0 |
| `80-testing/` | 0 | 0 |
| `90-observability/` | 0 | 0 |
| `100-operations/` | 0 | 0 |
| `110-security/` | 19 | 0 |
| `120-development-process/` | 1 | 0 |
| `130-roadmap/` | 0 | 0 |
| `140-application-development/` | 124 | 0 |
| `150-cloudnative/` | 44 | 0 |
| `160-compatibility/` | 0 | 0 |
| `170-performance/` | 0 | 0 |
| `180-i18n/` | 0 | 0 |
| `190-distribution/` | 0 | 0 |
| 顶层 `README.md` | 28 | 0 |
| **合计** | **700** | **2** |

> 说明：部分模块 OK=0 是因为其文档内仅以 prose / 反引号形式引用同模块文件（未使用 Markdown 链接语法），这些引用不计入 702 条链接校验范围，但已纳入 §5 的交叉引用不一致分析。

### 10.2 修复优先级矩阵

| 优先级 | 修复项 | 数量 | 影响 |
|--------|--------|------|------|
| P0 | 无效链接修复（FIX-01/02） | 2 | 链接点击 404 |
| P1 | 错误文件名修复（FIX-03~05） | 3 | 事实性引用错误 |
| P1 | Stale "待创建" 修复（FIX-06~13） | 8 | 误导维护者 |
| P1 | 主 README 索引修复（FIX-15~20） | 6 | 索引与现状脱节 |
| P1 | 140-190 版本范围修复（FIX-21~26） | 6 | 同文件内自相矛盾 |
| P2 | Stale 问题报告（FIX-14） | 1 | 误导后续维护 |
| P2 | 前向引用标注（FIX-27/28） | 2 | 读者误以为已存在 |
| P2 | 路线图同步（FIX-29~31） | 3 | 资源估算过时 |
| **合计** | | **31** | |

### 10.3 校对结论

本次 C-2.8 文档引用校对覆盖 `docs/AirymaxOS/` 全部 137 个 `.md` 文件、702 条 Markdown 链接，识别出 31 项可执行修复项。校对确认：

1. **旧路径迁移无遗漏**：`docs/AirymaxAgentOS/` 旧路径残留为 0；6 处 `AirymaxAgentOS` 字符串均为命名规范约定的正式英文全称，合规。
2. **链接健康度 99.72%**：仅 2 条 BROKEN，集中于 `50-engineering-standards/30-runtime-interfaces/README.md`，根因为相对路径深度计算错误（3 级深度文件误用 2 级 `../`）。
3. **主要风险在版本范围声明**：140-190 共 6 个模块 README 头部"0.1.1 占位"与正文"0.1.1 100% 完成"自相矛盾，主 README 同步过时，是本次校对发现的最系统性问题。
4. **修复方案可执行**：31 项修复均有明确的文件、行号、原文、修复后内容，配合 §8 的 Grep 验证命令可逐项验证闭环。

---

## 11. 修复执行确认（2026-07-09 闭环）

本节记录 31 项修复的实际执行结果与回归验证结论。

### 11.1 修复执行状态

| 优先级 | 修复项 | 数量 | 执行状态 |
|--------|--------|------|----------|
| P0 | 无效链接修复（FIX-01/02） | 2 | ✅ 全部执行 |
| P1 | 错误文件名修复（FIX-03~05） | 3 | ✅ 全部执行 |
| P1 | Stale "待创建" 修复（FIX-06~13） | 8 | ✅ 全部执行 |
| P1 | 主 README 索引修复（FIX-15~20） | 6 | ✅ 全部执行 |
| P1 | 140-190 版本范围修复（FIX-21~26） | 6 | ✅ 全部执行 |
| P2 | Stale 问题报告（FIX-14） | 1 | ✅ 全部执行 |
| P2 | 前向引用标注（FIX-27/28） | 2 | ✅ 全部执行 |
| P2 | 路线图同步（FIX-29~31） | 3 | ✅ 全部执行 |
| — | 180-i18n 脚注同步（FIX-25 补充） | 1 | ✅ 全部执行 |
| **合计** | | **32** | **✅ 100% 闭环** |

### 11.2 回归验证结论

修复后执行 §8.4 全量链接回归验证与 §8.2/§8.3/§8.5 残留搜索，结果如下：

| 验证项 | 修复前 | 修复后 | 状态 |
|--------|--------|--------|------|
| Markdown 链接健康度 | 700/702 OK（99.72%） | 710/710 OK（100%） | ✅ |
| `ARCHITECTURAL_PRINCIPLES` 残留 | 3 处 | 0 处 | ✅ |
| `待创建` 标签（140 模块） | 8 处 | 0 处 | ✅ |
| `README 占位`（主 README） | 12 处 | 0 处 | ✅ |
| 140-190 模块头部版本矛盾 | 6 模块 | 0 模块 | ✅ |
| 主 README 文档数声明 | 过时（8/4/占位） | 同步（38/5/✅完成） | ✅ |
| 路线图资源估算 | 122 文档 | 152 文档 | ✅ |

> **结论**：C-2.8 文档引用校对的 31 项修复（含 1 项脚注同步）已全部执行并通过回归验证，`docs/AirymaxOS/` 文档树链接健康度从 99.72% 提升至 100%，版本范围声明与索引计数全部与实际文件清册（SSoT）一致。

---

> **报告结束** | C-2.8 文档引用校对 | v0.3.0 | 2026-07-09 | 闭源不公开 | 修复闭环 2026-07-09
