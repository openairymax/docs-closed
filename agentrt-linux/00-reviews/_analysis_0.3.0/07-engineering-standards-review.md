Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux（AirymaxOS）工程标准规范逐章审查报告

> **报告编号**: C-2（工程标准规范审查）
> **报告日期**: 2026-07-09
> **报告版本**: v0.3.0（系统性分析与决策阶段）
> **审查范围**: `docs/AirymaxOS/50-engineering-standards/` 全部 38 份 Markdown 文件（17 顶层 + 5 子目录共 21 子文件）+ 闭源总纲 `docs-closed/agent-linux/agent-linux基本工程标准规范.md`（1444 行）+ OLK-6.6 参考基线 `01Reference/kernel-OLK-6.6/Documentation/process/coding-style.rst`
> **机密级别**: 闭源不公开（SPHARX Ltd 内部参考）
> **核心结论**: 工程标准体系在内容覆盖度上已达 0.1.1 奠基要求（38 文档覆盖编码/格式/风格/思想/流程/工具链/治理/合规 8 大维度），但存在 3 类系统性缺陷——(1) 规则编号体系 14 种前缀并存且 3 段/4 段混用（C-2.6 已识别 15 个重复对，10 项 P0-CRITICAL）；(2) IRON 铁律在公开 00-handbook（10 条）与闭源总纲（14 条）之间存在 003/005/006 三条语义冲突；(3) OLK-6.6 coding-style.rst 19 章中 §19 I/O 未覆盖。本报告整合 C-2.6 合并决策（D-01~D-09）与 C-2.5 可落地工程标准（STD-KABI-01 等 6 项），形成系统性审查结论。

---

## 目录

- [第 1 章 审查概述](#第-1-章-审查概述)
- [第 2 章 逐章核对结果](#第-2-章-逐章核对结果)
- [第 3 章 与 openEuler/OLK-6.6 对齐分析](#第-3-章-与-openeulerolk-66-对齐分析)
- [第 4 章 整合 C-2.6 合并决策](#第-4-章-整合-c-26-合并决策)
- [第 5 章 整合 C-2.5 可落地工程标准](#第-5-章-整合-c-25-可落地工程标准)
- [第 6 章 系统性审查结论](#第-6-章-系统性审查结论)
- [第 7 章 修复优先级矩阵与执行计划](#第-7-章-修复优先级矩阵与执行计划)
- [第 8 章 相关文档](#第-8-章-相关文档)

---

## 第 1 章 审查概述

### 1.1 审查目标

本报告执行用户指令第 2 项任务——"仔细审查修正后的工程标准规范文档，进行逐章逐节的内容核对，确保其完全同步并符合 openEuler 社区的代码编写规范与要求"。具体目标：

1. **逐章核对**：对 `50-engineering-standards/` 全部 38 份文档进行章节级内容核对，验证规则定义的完整性与一致性。
2. **openEuler 对齐**：以 OLK-6.6 `Documentation/process/coding-style.rst`（19 章）为基线，验证 agent-linux 工程标准与 openEuler 编码规范的对齐度。
3. **整合既有分析**：整合 C-2.6 合并审查报告（942 行，9 项决策）与 C-2.5 代码分析报告（831 行，6 项可落地标准）的结论，避免重复劳动。
4. **形成执行清单**：输出可执行的修复优先级矩阵，为 1.0.1 M0 工程标准奠基阶段提供输入。

### 1.2 审查方法

| 步骤 | 工具 | 目的 |
|------|------|------|
| 1. 文件清查 | `Glob` + `LS` | 列出 50-engineering-standards/ 全部 38 份 .md 文件与 5 子目录 |
| 2. 章节采样 | `Read`（每文件头部 + `Grep ^## ` 章节标题） | 提取每份文档的章节结构与权威声明 |
| 3. 规则枚举 | `Grep OS-[A-Z]+` | 抓取所有规则编号及其上下文 |
| 4. 基线比对 | OLK-6.6 `coding-style.rst` 19 章 | 逐章映射 agent-linux 规则到 OLK-6.6 章节 |
| 5. 交叉引用 | C-2.6 报告 §3 重复对 + C-2.5 报告 §6 可落地标准 | 整合既有分析结论 |

### 1.3 审查范围

**公开文档（38 份）**：

| 类别 | 文件数 | 文件清单 |
|------|--------|---------|
| 顶层主题文档 | 17 | README + 00-handbook + 01~09 + 60/70/80/100/110/120 |
| 10-coding-style/ 子目录 | 6 | README + C_coding_style + C_supplement + C_Cpp_secure + Rust_coding + Rust_secure |
| 20-contracts/ 子目录 | 4 | README + logging + syscall_api + ipc_protocol |
| 30-runtime-interfaces/ 子目录 | 4 | README + L1 + L2 + L3 |
| 40-integration/ 子目录 | 2 | README + agentrt_integration |
| 50-project-erp/ 子目录 | 5 | README + resource_management + manuals_module + SBOM + error_code |
| **合计** | **38** | — |

**闭源参考（1 份）**：`docs-closed/agent-linux/agent-linux基本工程标准规范.md`（80KB / 1444 行）。

**OLK-6.6 基线（1 份）**：`01Reference/kernel-OLK-6.6/Documentation/process/coding-style.rst`（44KB / 19 章）。

### 1.4 审查依据

| 依据 | 来源 | 用途 |
|------|------|------|
| OLK-6.6 coding-style.rst | `01Reference/kernel-OLK-6.6/Documentation/process/coding-style.rst` | 编码风格权威基线（19 章） |
| OLK-6.6 .clang-format | `01Reference/kernel-OLK-6.6/.clang-format`（689 行） | 格式规则源 |
| OLK-6.6 checkpatch.pl | `01Reference/kernel-OLK-6.6/scripts/checkpatch.pl` | 规则映射源 |
| OLK-6.6 kernel-doc | `01Reference/kernel-OLK-6.6/scripts/kernel-doc` | 注释规范源 |
| OLK-6.6 KABI | `01Reference/kernel-OLK-6.6/include/linux/kabi.h` + `lib/Kconfig.kabi` | 二进制兼容演进基线 |
| C-2.6 合并报告 | `00-reviews/_analysis_0.3.0/06-engineering-standards-consolidation.md`（942 行） | 编号体系合并决策 |
| C-2.5 代码分析报告 | `00-reviews/_analysis_0.3.0/05-code-analysis-sel4-olk66.md`（831 行） | 可落地工程标准 |
| C-1 经验总结 | `00-reviews/_analysis_0.3.0/01-lessons-learned.md` | 历史经验教训 |

---

## 第 2 章 逐章核对结果

### 2.1 README.md（主索引）

**章节结构**：主索引与总纲，含三大支柱表、文档清单、五维原则映射。

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| 文档清单完整性 | ✅ 通过 | 17 顶层 + 5 子目录全部列出 |
| 文档计数准确性 | ✅ 已修复 | C-2.8 已将"8 文档"修正为"38 文档"（FIX-16/17） |
| 三大支柱映射 | ✅ 通过 | Linux 6.6 基线 + 五维原则 + seL4 思想三支柱清晰 |
| 交叉引用文件名 | ✅ 已修复 | C-2.8 已将 `ARCHITECTURAL_PRINCIPLES.md` 修正为 `00-architectural-principles.md`（FIX-03/04/05） |
| 同源映射字段 | ✅ 通过 | 引用 agentrt 同源文档路径正确 |

**未发现问题**。README.md 经 C-2.8 修复后状态良好。

### 2.2 00-engineering-standards-handbook.md（SSoT 索引）

**章节结构**：10 章——体系总览 / IRON 铁律 / SSoT 注册表 / IRON-9 v2 三层共享 / 7 层验证 / 禁词清单 / 微核心术语 / 乔布斯美学 / OLK-6.6 基线 / 开发就绪检查。

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| SSoT 权威声明 | ✅ 通过 | §0 明确声明"本手册为 SSoT 索引" |
| IRON 铁律数量 | ❌ **P0 缺陷** | §2.1 仅列 10 条（OS-IRON-001~010），闭源总纲附录 A 有 14 条（001~014）。缺 IRON-011~014（双源边界/seL4 借鉴/8 子仓/[SC] 单一数据源） |
| IRON-003 语义冲突 | ❌ **P0 缺陷** | 公开="补丁中点可编译"，闭源="策略与机制分离"。**3 种完全不同定义** |
| IRON-005 语义冲突 | ❌ **P0 缺陷** | 公开="DCO Signed-off-by 强制"，闭源="审查优先文化" |
| IRON-006 语义冲突 | ❌ **P0 缺陷** | 公开="信任链分层不可越级"，闭源="不破坏用户空间原则" |
| 编号格式约定 | ⚠️ P1 缺陷 | §3.1 描述"3 位数字序号 OS-<前缀>-<子域>-<NNN>"，但实际 3 段（OS-KER-005）与 4 段（OS-STD-CODE-001）混用 |
| SSoT 注册表完整性 | ⚠️ P1 缺陷 | §3 列出 OS-STD-CODE 4 条 + OS-STD-FMT 2 条，但 01-coding-standards 实际有 OS-STD-001~020（20 条），注册表不完整 |
| 7 层验证体系 | ✅ 通过 | §5 清晰定义 Layer 0-7 |
| 禁词清单 | ✅ 通过 | §6 描述性表述合规（不直接列出禁词） |
| 微核心 vs 微内核术语 | ✅ 通过 | §7 明确区分"微核心"（agentrt）与"微内核"（agent-linux） |
| OLK-6.6 基线声明 | ✅ 通过 | §9 引用 `01Reference/kernel-OLK-6.6/` 源码 |

**发现问题**：4 项 P0（IRON 铁律数量 + 3 条语义冲突）+ 2 项 P1（编号格式 + 注册表不完整）。对应 C-2.6 决策 D-01。

### 2.3 01-coding-standards.md（代码规范）

**章节结构**：0 文档说明 + 1 命名 + 2 函数 + 3 注释 + 4 头文件 + 5 错误处理 + 6 类型规范 + 7 内存管理 + 8 锁与并发 + 9 五维映射。

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| 权威声明 | ✅ 通过 | §0 声明"语义层代码规则唯一权威来源（SSoT）" |
| 编号格式一致性 | ❌ **P0 缺陷** | 首条用 4 段（OS-STD-CODE-001），第二条起退化为 3 段（OS-STD-002~020）。同文件内部不一致 |
| OS-KER-002 双义 | ❌ **P0 缺陷** | §6.2 定义"u8/u16/u32 类型"，§6.3 同一编号定义"bool 仅返回值"。同文件内部编号冲突 |
| OLK-6.6 §4 命名对齐 | ✅ 通过 | OS-STD-CODE-001 全局描述性命名 ↔ OLK-6.6 §4 Naming |
| OLK-6.6 §5 typedef 对齐 | ✅ 通过 | OS-STD-020 typedef 5 种例外 ↔ OLK-6.6 §5 Typedefs（5 规则 a-e） |
| OLK-6.6 §6 Functions 对齐 | ✅ 通过 | OS-STD-006~009 函数规范 ↔ OLK-6.6 §6 Functions |
| OLK-6.6 §7 goto 对齐 | ✅ 通过 | OS-STD-CODE-002 goto 集中出口 ↔ OLK-6.6 §7 Centralized exiting |
| OLK-6.6 §8 Commenting 对齐 | ✅ 通过 | OS-STD-010~014 注释规范 ↔ OLK-6.6 §8 Commenting |
| OLK-6.6 §9 Macros 对齐 | ✅ 通过 | OS-STD-003/018/019 宏与枚举 ↔ OLK-6.6 §9 Macros |
| OLK-6.6 §10 inline 对齐 | ✅ 通过 | OS-STD-019 inline disease ↔ OLK-6.6 §10 The inline disease |
| OLK-6.6 §11 返回值对齐 | ✅ 通过 | OS-STD-004 返回值约定 ↔ OLK-6.6 §11 Function return values |
| strscpy 规则 | ⚠️ P1 缺陷 | OS-STD-CODE-003 定义正确，但同一规则在 6 处以 4 种不同编号出现（C-2.6 R-10） |
| bool 边界规则 | ⚠️ P1 缺陷 | OS-KER-002（01 双义）/ OS-KER-008（00-handbook）/ OS-STD-011（闭源）——4 种编号（C-2.6 R-14） |

**发现问题**：2 项 P0（编号格式 + OS-KER-002 双义）+ 2 项 P1（strscpy 多编号 + bool 多编号）。对应 C-2.6 决策 D-05。

### 2.4 02-code-format.md（代码格式）

**章节结构**：0 章节定位 + 1 缩进 + 2 行宽 + 3 大括号 + 4 空格 + 5 switch-case + 6 空行 + 7 多语句 + 8 指针声明 + 9 clang-format 配置 + 10 五维映射。

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| 权威声明 | ✅ 通过 | §0 声明"代码格式规则唯一权威来源（SSoT）"，并明确 `10-coding-style/C*` 须引用本卷 |
| OLK-6.6 §1 缩进对齐 | ✅ 通过 | OS-KER-005 Tab 8 字符 ↔ OLK-6.6 §1 Indentation |
| OLK-6.6 §2 行宽对齐 | ✅ 通过 | OS-KER-004 80 列 ↔ OLK-6.6 §2 Breaking long lines |
| OLK-6.6 §3 大括号对齐 | ✅ 通过 | OS-STD-047 + OS-KER-008 K&R ↔ OLK-6.6 §3 Placing Braces |
| OLK-6.6 §3 空格对齐 | ✅ 通过 | OS-KER-010~014 空格规则 ↔ OLK-6.6 §3 Spaces |
| OLK-6.6 §7 goto 对齐 | ✅ 通过 | 引用 01 的 OS-STD-CODE-002 |
| clang-format 配置 | ⚠️ P0 缺陷 | §9 clang-format 配置项表与 `80-clang-format-enforcement.md` §1 重叠 >70%（C-2.6 R-2） |
| 与 10-coding-style/C* 重叠 | ❌ **P0 缺陷** | 与 `C_coding_style_standard.md` §2.1-§2.4 重叠 >80%，且编号完全冲突（OS-KER-005 vs OS-KER-011）（C-2.6 R-3） |
| OS-KER-005 双义 | ⚠️ P1 缺陷 | §1.1 定义"Tab 8 字符"，§2 也定义"字符串禁止断行"——同编号两种含义 |
| 配置即代码原则 | ✅ 通过 | OS-STD-201 "每条格式规则必须有对应工具配置项" |

**发现问题**：2 项 P0（与 80 重叠 + 与 C* 重叠）+ 1 项 P1（OS-KER-005 双义）。对应 C-2.6 决策 D-02（合并 80）、D-03（删除 C*）、D-04（迁移 OS-FMT）。

### 2.5 03-code-style.md（代码风格）

**章节结构**：0 章节定位 + 1 模块化 + 2 策略机制分离 + 3 函数分解 + 4 数据结构 + 5 抽象层次 + 6 防御性 + 7 性能 + 8 专属风格 + 9 工具链 + 10 五维映射。

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| 模块化设计 | ✅ 通过 | §1 反过度抽象（OS-KER-022）↔ OLK-6.6 §15 Idiomatic C |
| 策略机制分离 | ✅ 通过 | §2 OS-KER-020 ↔ OLK-6.6 工程思想 |
| 函数分解 | ✅ 通过 | §3 ↔ OLK-6.6 §6 Functions |
| 数据结构 | ✅ 通过 | §4 引用计数（OS-KER-031）↔ OLK-6.6 §15 |
| 抽象层次 | ✅ 通过 | §5 反过度抽象 |
| 防御性编程 | ✅ 通过 | §6 IS_ENABLED（OS-KER-030）↔ OLK-6.6 §14 Conditional Compilation |
| 性能优化 | ✅ 通过 | §7 cache 影响优先 |
| I/O 风格 | ❌ **P1 缺失** | OLK-6.6 §19 I/O（ioremap/readl/writel）未覆盖。建议新增 §10 或新建 90-driver-engineering.md |
| 编号冲突 | ⚠️ P1 缺陷 | OS-KER-022（反过度抽象）与 04 §2（补丁顺序）共用编号；OS-KER-030（IS_ENABLED）与 04 §5（bug 修复附回归测试）共用编号 |

**发现问题**：1 项 P1 缺失（I/O 未覆盖）+ 1 项 P1（编号冲突）。I/O 缺失对应 C-2.5 建议；编号冲突对应 C-2.6 决策 D-04。

### 2.6 04-engineering-philosophy.md（工程思想）

**章节结构**：10 章——概述 / 双层稳定性 / 策略机制分离 / 渐进式开发 / regression 不可接受 / 审查优先 / 可追溯性 / 文档即代码 / 不破坏用户空间 / 管理哲学。

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| 双层稳定性 | ✅ 通过 | §2 OLK-6.6 ABI 永久稳定 + 内核 API 可变 |
| 策略机制分离 | ✅ 通过 | §3 ↔ OLK-6.6 工程思想 |
| 渐进式开发 | ✅ 通过 | §4 ↔ OLK-6.6 Merge Window + RC |
| regression 不可接受 | ✅ 通过 | §5 ↔ OLK-6.6 regression 零容忍 |
| 审查优先文化 | ✅ 通过 | §6 ↔ OLK-6.6 审查文化 |
| IRON 编号冲突 | ❌ **P0 缺陷** | §2-§7 重新定义了 IRON-003/005/006 三条铁律，与 00-handbook 和闭源总纲语义完全不同（C-2.6 R-5/R-6） |
| 五维原则映射 | ✅ 通过 | 附录 B 完整映射表 |

**发现问题**：1 项 P0（IRON 三条语义冲突）。对应 C-2.6 决策 D-01。

### 2.7 05-development-process.md（开发流程）

**章节结构**：补丁生命周期 / 维护者层级 / 补丁格式 / Merge Window + RC。

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| 补丁生命周期 | ✅ 通过 | ↔ OLK-6.6 `Documentation/process/submitting-patches.rst` |
| 维护者层级 | ✅ 通过 | ↔ OLK-6.6 MAINTAINERS 制度 |
| 编号段冲突 | ❌ **P0 缺陷** | §12 使用 OS-STD-101~234，与 06 §11 的 OS-STD-101~158 共用编号段，30+ 条语义冲突（C-2.6 R-7） |
| 补丁格式规范 | ✅ 通过 | ↔ OLK-6.6 `submitting-patches.rst` |

**发现问题**：1 项 P0（与 06 编号段冲突）。对应 C-2.6 决策 D-06（隔离为 OS-STD-PROD）。

### 2.8 06-toolchain-and-automation.md（工具链）

**章节结构**：7 层验证 / checkpatch / CI 矩阵 / 覆盖率门槛。

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| 7 层验证体系 | ✅ 通过 | Layer 0-7 清晰定义 |
| checkpatch 集成 | ✅ 通过 | ↔ OLK-6.6 `scripts/checkpatch.pl` |
| CI 矩阵 | ✅ 通过 | ↔ OLK-6.6 CI 实践 |
| 编号段冲突 | ❌ **P0 缺陷** | §11 使用 OS-STD-101~158，与 05 冲突（同上） |
| sparse + W 分级 | ⚠️ P1 缺失 | 未明确 sparse（`make C=1`）+ W=1/2/3/e 分级警告集成要求（C-2.5 STD-CODE-07） |
| 编号格式混用 | ⚠️ P1 缺陷 | 首条 4 段（OS-STD-CODE-004），余 3 段（OS-STD-002） |

**发现问题**：1 项 P0（编号段冲突）+ 2 项 P1（sparse 缺失 + 编号格式混用）。对应 C-2.6 决策 D-06（隔离为 OS-STD-TOOL）+ C-2.5 STD-CODE-07。

### 2.9 07-maintainers-and-governance.md（治理）

**章节结构**：MAINTAINERS / DCO / 信任链 / SSoT 注册表 / 6 级成熟度模型。

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| MAINTAINERS 制度 | ✅ 通过 | ↔ OLK-6.6 `MAINTAINERS`（24218 行） |
| DCO 强制 | ✅ 通过 | ↔ OLK-6.6 Signed-off-by |
| 信任链分层 | ✅ 通过 | ↔ OLK-6.6 维护者层级 |
| SSoT 注册表 | ✅ 通过 | §10 规则编号注册表 |
| 6 级成熟度模型 | ✅ 通过 | ↔ OLK-6.6 组织成熟度 |
| OS-STD-GOV 编号 | ✅ 通过 | 使用 4 段编号 OS-STD-GOV-001~007，格式正确 |
| 8 子仓 MAINTAINERS 缺失 | ⚠️ P2 缺失 | 8 子仓无 MAINTAINERS 文件（C-2.5 STD-IRON-18 / R-03） |

**发现问题**：1 项 P2（8 子仓 MAINTAINERS 缺失）。对应 C-2.5 STD-IRON-18。

### 2.10 08-compliance-checklist.md（合规检查）

**章节结构**：检查机制定位 / 文档标准化 / 代码标准化 / IRON-9 v2 检查 / 自动化集成 / 编号体系 / 实施路线。

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| 17 项检查规则 | ✅ 通过 | STD-DOC-01~08 + STD-CODE-01~05 + STD-IRON-01~04 + STD-CI-01 |
| 16 个检查脚本 | ✅ 通过 | 规范清晰 |
| CI/CD 集成 | ✅ 通过 | §5 自动化检查集成 |
| 编号前缀独立 | ❌ **P1 缺陷** | 自创 STD-DOC/CODE/IRON/CI 四个独立前缀，与全项目 OS-* 体系并行（C-2.6 R-9） |
| seL4 借鉴检查 | ⚠️ P2 缺失 | 未含 STD-DOC-18/19 + STD-IRON-18 + STD-CODE-08 四项 seL4 借鉴检查规则（C-2.6 报告 §6.3 缺失项） |

**发现问题**：1 项 P1（前缀独立）+ 1 项 P2（seL4 借鉴检查缺失）。对应 C-2.6 决策 D-07 + R-04。

### 2.11 09-license-strategy.md（许可证策略，已废弃）

**核对结论**：§0 已明确废弃声明（2026-07-09），内容已合并至 110-spdx-license-compliance.md。**严重度 P2-MINOR**，仅需在 README 与 00-handbook 标注"已废弃"链接。对应 C-2.6 决策 D-08。

### 2.12 60-checkpatch-rule-map.md（checkpatch 规则映射）

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| checkpatch 规则映射 | ✅ 通过 | OS-STD-CODE-001~999 映射到 checkpatch 规则 |
| 编号格式 | ✅ 通过 | 使用 4 段编号 OS-STD-CODE-NNN |
| 与 01 编号对齐 | ⚠️ P1 缺陷 | 60 使用 OS-STD-CODE-010（strscpy），01 使用 OS-STD-CODE-003——同一规则两个编号（C-2.6 R-10） |

**发现问题**：1 项 P1（strscpy 编号不一致）。对应 C-2.6 决策 D-05。

### 2.13 70-kernel-doc-standard.md（kernel-doc 规范）

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| kernel-doc 注释规范 | ✅ 通过 | ↔ OLK-6.6 `scripts/kernel-doc` |
| 编号格式 | ✅ 通过 | 使用 4 段编号 OS-STD-DOC-001~NNN |
| syscall.xml 契约 | ⚠️ P2 缺失 | 未引入 seL4 syscall.xml 式机器可读接口契约（C-2.5 STD-DOC-18 / R-01） |

**发现问题**：1 项 P2（syscall.xml 契约缺失）。对应 C-2.5 STD-DOC-18。

### 2.14 80-clang-format-enforcement.md（clang-format 配置）

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| .clang-format 配置 | ✅ 通过 | ↔ OLK-6.6 `.clang-format`（689 行） |
| CI 门禁流程 | ✅ 通过 | §5 CI 门禁脚本流程 |
| 与 02 重叠 | ❌ **P0 缺陷** | §1 配置项详解与 02 §9 重叠 >70%（C-2.6 R-2） |
| 编号冲突 | ⚠️ P1 缺陷 | 80 用 OS-KER-011（缩进配置），02 用 OS-KER-005（Tab 8 字符）——同一规则两个编号 |

**发现问题**：1 项 P0（与 02 重叠）+ 1 项 P1（编号冲突）。对应 C-2.6 决策 D-02。

### 2.15 100-deprecated-api-registry.md（弃用 API 清单）

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| 弃用 API 清单 | ✅ 通过 | strcpy/strncpy/strlcpy → strscpy；BUG()/BUG_ON() → WARN_ON_ONCE()；%p → %pK 等 |
| 与 OLK-6.6 对齐 | ✅ 通过 | ↔ OLK-6.6 弃用 API 实践 |

**未发现问题**。内容质量良好。

### 2.16 110-spdx-license-compliance.md（SPDX 合规）

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| SPDX 5 类文件分类 | ✅ 通过 | ↔ OLK-6.6 SPDX 实践 |
| 编号格式 | ✅ 通过 | 使用 4 段编号 OS-STD-SPDX-001~003 |

**未发现问题**。

### 2.17 120-cross-project-code-sharing.md（跨项目代码共享）

**核对结论**：

| 核对项 | 状态 | 说明 |
|--------|------|------|
| IRON-9 v2 三层模型 | ✅ 通过 | [SC] 共享契约层 + [SS] 语义同源层 + [IND] 完全独立层 |
| [SC] 6 头文件清单 | ✅ 通过 | bpf_struct_ops / memory_types / security_types / cognition_types / sched / ipc |
| 编号引用 | ✅ 通过 | 引用 OS-IRON-008~014 |

**未发现问题**。内容质量良好。

### 2.18 10-coding-style/ 子目录（6 文件）

**核对结论**：

| 文件 | 核对结论 | 问题 |
|------|---------|------|
| README.md | ✅ 通过 | 子目录索引清晰 |
| C_coding_style_standard.md | ❌ **P0 缺陷** | 与 02 重叠 >80%，编号完全冲突（OS-KER-011 vs OS-KER-005）。C-2.6 R-3，决策 D-03 删除 |
| C_coding_style_standard_supplement.md | ❌ **P0 缺陷** | 与 C_coding_style_standard 编号冲突（OS-KER-013/014/015 完全不同含义）。C-2.6 R-4，决策 D-03 删除 |
| C_Cpp_secure_coding_standard.md | ⚠️ P1 缺陷 | strscpy 用 OS-BAN-006（与 00-handbook OS-BAN-003 冲突）；%p 用 OS-BAN-007（冲突） |
| Rust_coding_style_standard.md | ✅ 通过 | Rust 风格规范清晰 |
| Rust_secure_coding_standard.md | ✅ 通过 | Rust 安全规范清晰 |

**发现问题**：2 项 P0（C* 两份文件需删除）+ 1 项 P1（安全编码编号冲突）。对应 C-2.6 决策 D-03。

### 2.19 20-contracts/ 子目录（4 文件）

**核对结论**：

| 文件 | 核对结论 |
|------|---------|
| README.md | ✅ 通过 |
| logging_contract.md | ✅ 通过 |
| syscall_api_contract.md | ✅ 通过 |
| ipc_protocol_contract.md | ✅ 通过 |

**未发现问题**。契约层文档质量良好。

### 2.20 30-runtime-interfaces/ 子目录（4 文件）

**核对结论**：

| 文件 | 核对结论 |
|------|---------|
| README.md | ✅ 已修复 | C-2.8 已修复 2 条 BROKEN 链接（FIX-01/02） |
| L1_runtime_interface.md | ✅ 通过 |
| L2_service_protocol.md | ✅ 通过 |
| L3_security_governance.md | ✅ 通过 |

**未发现问题**。

### 2.21 40-integration/ 子目录（2 文件）

**核对结论**：

| 文件 | 核对结论 |
|------|---------|
| README.md | ✅ 通过 |
| agentrt_integration.md | ✅ 通过 |

**未发现问题**。建议新增 syscall-contract.xml（C-2.5 STD-DOC-18）和 bitfield-contract.bf（C-2.5 STD-CODE-08）。

### 2.22 50-project-erp/ 子目录（5 文件）

**核对结论**：

| 文件 | 核对结论 |
|------|---------|
| README.md | ✅ 通过 |
| resource_management_table.md | ✅ 通过 |
| manuals_module_requirements.md | ✅ 通过 |
| SBOM.md | ✅ 通过 |
| error_code_reference.md | ✅ 通过 |

**未发现问题**。

---

## 第 3 章 与 openEuler/OLK-6.6 对齐分析

### 3.1 OLK-6.6 coding-style.rst 19 章映射

| OLK-6.6 章节 | 主题 | agent-linux 对应规则 | 对齐状态 |
|-------------|------|----------------------|---------|
| §1 | Indentation（Tab 8 字符） | OS-KER-005 / OS-KER-011 / OS-FMT-001 | ✅ 对齐（3 编号冲突需统一，C-2.6 D-04） |
| §2 | Breaking long lines and strings | OS-KER-005（字符串）/ OS-KER-006（后继行） | ✅ 对齐 |
| §3 | Placing Braces and Spaces | OS-STD-047 / OS-KER-008~014 | ✅ 对齐 |
| §4 | Naming | OS-STD-CODE-001 / OS-STD-005 | ✅ 对齐 |
| §5 | Typedef | OS-STD-020 / OS-KER-002 | ✅ 对齐（5 种例外完全一致） |
| §6 | Functions | OS-STD-006~009 | ✅ 对齐 |
| §7 | Centralized exiting of functions | OS-STD-CODE-002 / OS-KER-001 / OS-KER-009 | ✅ 对齐（3 编号需统一） |
| §8 | Commenting | OS-STD-010~014 | ✅ 对齐 |
| §9 | Macros, Enums and RTL | OS-STD-003 / OS-STD-018~019 / OS-BAN-004 | ✅ 对齐 |
| §10 | The inline disease | OS-STD-019 | ✅ 对齐 |
| §11 | Function return values and names | OS-STD-004 | ✅ 对齐 |
| §12 | Kernel messages | OS-KER-005（字符串禁止断行） | ✅ 对齐 |
| §13 | Printing kernel messages | 分散 | ✅ 对齐 |
| §14 | Conditional Compilation | OS-KER-003 / OS-KER-030 | ✅ 对齐（IS_ENABLED 完全一致） |
| §15 | Idiomatic C | 分散 | ✅ 对齐 |
| §16 | Rationale | 背景 | ✅ 对齐 |
| §17 | References | 背景 | ✅ 对齐 |
| §18 | Breaking long lines and strings | 同 §2 | ✅ 对齐 |
| §19 | I/O | **未覆盖** | ❌ **缺失** |

### 3.2 对齐度量化

| 维度 | OLK-6.6 章节数 | agent-linux 覆盖数 | 对齐率 |
|------|--------------|-------------------|--------|
| 编码风格对齐 | 19 | 18 | **94.7%**（仅 §19 I/O 缺失） |
| 工程思想覆盖 | 13 | 12 | **92.3%**（ES-OLK-8 MAINTAINERS 未落地，R-03） |
| seL4 借鉴 | 10 | 8 | **80.0%**（ES-SEL4-6/8 未引入，R-01/R-02） |
| 编码风格条目对齐（D1） | 16 | 16 | **100%** |

### 3.3 OLK-6.6 §19 I/O 缺失分析

OLK-6.6 §19 涉及 I/O 操作规范（`ioremap` / `readl` / `writel` / `iounmap` / `ioport_map` / `pci_iomap` 等），agent-linux 当前未覆盖。

**影响评估**：agent-linux 的 8 子仓中 `airymaxos-kernel` 涉及设备驱动（尤其是 GPU/NPU 加速器接入），I/O 操作规范缺失可能导致不安全的 I/O 访问模式。

**建议**：在 `03-code-style.md` 新增 §10 I/O 风格规范，或新建 `90-driver-engineering.md`（OS-DRV-001~NNN）。内容应覆盖：
- `ioremap` / `iounmap` 生命周期管理
- `readl` / `writel` 内存屏障语义
- `ioport_map` / `ioport_unmap` 端口 I/O
- `devm_ioremap` 资源管理变体（推荐）
- DMA 映射一致性

**优先级**：P1（1.0.1 M1 落地，与驱动模型 60-driver-model 协同）。

### 3.4 单语句大括号规则冲突解决

OLK-6.6 §3 立场：**单语句可不加大括号，但多语句必须加**。

- `02-code-format.md` OS-KER-009：与 OLK-6.6 **一致**（单语句不需要，多语句必须加）
- 闭源总纲 OS-FMT-004：与 OLK-6.6 **不一致**（即使单条语句也使用大括号）

**决策**：采纳 OLK-6.6 立场，删除闭源 OS-FMT-004，统一为 02 的 OS-KER-009（迁移后为 OS-FMT-004）。

---

## 第 4 章 整合 C-2.6 合并决策

### 4.1 决策汇总

C-2.6 报告（942 行）识别了 15 个重复问题对（10 项 P0-CRITICAL + 3 项 P1-MAJOR + 1 项 P2-MINOR）和 14 种编号前缀并存问题，给出 9 项合并决策：

| 决策 | 涉及文件 | 决策类型 | 优先级 | 状态 |
|------|---------|---------|--------|------|
| D-01 | 00-handbook + 04-philosophy + 闭源总纲 | IRON 铁律对齐（闭源 14 条为准） | P0 | 待执行 |
| D-02 | 02 + 80 | 合并（80 仅保留 CI 部分） | P0 | 待执行 |
| D-03 | 10-coding-style/C* | 删除 2 份文件 | P0 | 待执行 |
| D-04 | 02 + 闭源 §3 | 编号迁移 OS-FMT | P0 | 待执行 |
| D-05 | 01 + 闭源 §2 | 编号迁移 OS-STD-CODE | P0 | 待执行 |
| D-06 | 05 + 06 | 编号段隔离 PROD/TOOL | P0 | 待执行 |
| D-07 | 08 | 前缀统一 OS-STD-CHECK | P1 | 待执行 |
| D-08 | 09 | 物理移除标记 | P2 | 待执行 |
| D-09 | 60 + 70 + 110 | 子域前缀校验 | P2 | 待执行 |

### 4.2 执行状态

**截至本报告日期（2026-07-09），9 项决策均处于"待执行"状态**。C-2.6 报告建议的 4 阶段执行计划时间线为：

| 阶段 | 时间 | 决策 | 状态 |
|------|------|------|------|
| 阶段 1：编号体系对齐 | 2026-07-10 ~ 2026-07-23 | D-01、D-04、D-05、D-06 | 未启动 |
| 阶段 2：重复文件合并 | 2026-07-24 ~ 2026-07-30 | D-02、D-03 | 未启动 |
| 阶段 3：检查规则前缀统一 | 2026-07-31 ~ 2026-08-13 | D-07 + 缺失项补齐 | 未启动 |
| 阶段 4：废弃文件清理 | 2026-08-14 ~ 2026-08-20 | D-08、D-09 + 缺失项补齐 | 未启动 |

**注意**：上述时间线是 1.0.1 开发阶段的工作，不属于 0.1.1 文档体系范围。0.1.1 的工程标准文档已完成奠基（38 文档），编号体系合并是 1.0.1 M0 工程标准奠基阶段的首批任务。

### 4.3 编号体系目标状态

合并完成后的目标编号体系（C-2.6 附录 B）：

| 前缀 | 含义 | 数量 | 文档分布 |
|------|------|------|---------|
| OS-IRON-001~014 | 工程铁律 | 14 | 闭源附录 A + 公开 00-handbook §2.1 |
| OS-BAN-001~011 | 禁止规则 | 7 | 闭源 §2.2.4 + 公开 01 §OS-BAN |
| OS-STD-CODE-001~020 | 编码标准 | 20 | 01-coding-standards |
| OS-STD-FMT-001~014 | 格式标准 | 14 | 02-code-format |
| OS-STD-STY-001~NNN | 风格标准 | 待定 | 03-code-style |
| OS-STD-PROD-101~234 | 流程标准 | 50+ | 05-development-process |
| OS-STD-TOOL-001~158 | 工具标准 | 50+ | 06-toolchain-and-automation |
| OS-STD-GOV-001~007 | 治理标准 | 7 | 07-maintainers-and-governance |
| OS-STD-CHECK-* | 检查标准 | 17 | 08-compliance-checklist |
| OS-STD-CODE-001~999 | checkpatch 映射 | 30+ | 60-checkpatch-rule-map |
| OS-STD-DOC-001~NNN | kernel-doc | 待定 | 70-kernel-doc-standard |
| OS-STD-SPDX-001~003 | SPDX 合规 | 3 | 110-spdx-license-compliance |
| OS-KER-001~003 + 101~111 | 内核工程（仅内核态专属） | 14 | 01 + 03 |
| OS-ACC-001~NNN | 验收标准 | 待扩展 | 00-handbook §3.6 |
| OS-ABI-001 | 接口稳定性 | 1 | 00-handbook §3.5 |
| OS-DRV-001~NNN | 驱动工程 | 待新建 | 90-driver-engineering（新建） |
| OS-BUILD-001~NNN | 构建工程 | 待新建 | 75-build-engineering（新建） |
| OS-TEST-001~NNN | 测试工程 | 待新建 | 85-test-engineering（新建） |
| OS-OBS-001~NNN | 可观测性 | 待新建 | 95-observability-rules（新建） |
| OS-SEC-001~020 | 安全工程 | 20 | 65-security-engineering（合并自 10-coding-style/*_secure） |

---

## 第 5 章 整合 C-2.5 可落地工程标准

### 5.1 6 项可落地工程标准

C-2.5 代码分析报告（831 行，基于 seL4 + OLK-6.6 源码逐行研读）提出 6 项可落地工程标准：

| 优先级 | 编号 | 内容 | 上游依据 | 建议落地时机 | 预估工时 | 状态 |
|--------|------|------|---------|-------------|---------|------|
| P1 | STD-KABI-01 | KABI 二进制兼容演进机制 | ES-OLK-14（`include/linux/kabi.h` + `lib/Kconfig.kabi`） | 1.0.1 M1 | ~20h | 待落地 |
| P1 | STD-CODE-07 | sparse + W=1/2/3/e 分级警告集成 | ES-OLK-9（`Makefile:111-119` + `scripts/Makefile.extrawarn`） | 1.0.1 M1 | ~8h | 待落地 |
| P2 | STD-DOC-18 | syscall.xml 式接口契约定义 | ES-SEL4-6（`libsel4/include/api/syscall.xml` + `tools/syscall_header_gen.py`） | 1.0.1 M1 | ~16h | 待落地 |
| P2 | STD-CODE-08 | [SC] 头文件位域定义 bitfield codegen | ES-SEL4-8（`include/object/structures_64.bf` + `tools/bitfield_gen.py`） | 1.0.1 M1 | ~12h | 待落地 |
| P2 | STD-IRON-18 | 8 子仓 MAINTAINERS 文件 | ES-OLK-8（`MAINTAINERS` 24218 行） | 1.0.1 M5 | ~8h | 待落地 |
| P2 | STD-TEST-09 | CI 多工具矩阵 | ES-SEL4-11（8 个 CI badges）+ ES-OLK-9 | 1.0.1 M3 | ~16h | 待落地 |
| — | 合计 | 6 项工程标准 | — | 1.0.1 M1-M5 | ~80h | — |

### 5.2 落地建议

1. **STD-KABI-01（P1）**：在 `50-engineering-standards/` 新增 `09-kabi-evolution.md`，定义 agent-linux 的 KABI 宏机制（借鉴 OLK-6.6 `KABI_EXTEND`/`KABI_DEPRECATE`/`KABI_BROKEN_INSERT_ENUM`/`KABI_USE` 但不复制其实现）。新增字段必须追加到结构体末尾，废弃字段保留 hole。

2. **STD-CODE-07（P1）**：在 `01-coding-standards.md` 增补规则——CI 必须运行 `make C=1`（sparse 检查重编译文件）+ `make W=1`（相关警告）+ `make W=e`（警告即错误）三档。W=2/W=3 可选。

3. **STD-DOC-18（P2）**：在 `50-engineering-standards/40-integration/` 新增 `syscall-contract.xml`，由 `scripts/syscall_gen.py` 自动生成 `include/uapi/airymax/syscall.h` + `kernel/entry/airymax_syscall_table.c`。XML 格式借鉴 seL4 但不复制其内容。

4. **STD-CODE-08（P2）**：在 `50-engineering-standards/40-integration/` 新增 `bitfield-contract.bf` 规范，定义 `.bf` DSL 格式，由 `scripts/bitfield_gen.py` 自动生成 C 结构体与访问函数。

5. **STD-IRON-18（P2）**：为 8 子仓每个仓根目录新增 `MAINTAINERS` 文件，格式精简（`M:`/`S:`/`F:`/`W:` 四字段）。

6. **STD-TEST-09（P2）**：在 `80-testing` 定义 CI 多工具矩阵——(1) 编译检查（多编译器/多架构）；(2) 静态分析（sparse/smatch/cppcheck/coccinelle）；(3) 单元测试（KUnit）；(4) 集成测试（kselftest）；(5) 文档生成（`make htmldocs`）；(6) 契约一致性检查（syscall.xml / bitfield.bf）；(7) checkpatch 规范检查；(8) 形式化验证（tests-linux 子仓）。

### 5.3 与 C-2.6 缺失标准的关系

C-2.6 报告 §6.3 识别了 8 项缺失标准，其中 5 项与 C-2.5 的 6 项可落地标准直接对应：

| C-2.6 缺失项 | C-2.5 对应 | 优先级 | 落地方式 |
|-------------|-----------|--------|---------|
| OS-DRV-001~NNN 驱动工程规则 | —（C-2.5 未涉及，但 §3.3 I/O 缺失分析指向此处） | P1 | 新建 90-driver-engineering.md |
| OS-BUILD-001~NNN 构建工程规则 | — | P1 | 新建 75-build-engineering.md |
| OS-TEST-001~NNN 测试工程规则 | STD-TEST-09（CI 多工具矩阵） | P1 | 新建 85-test-engineering.md |
| OS-OBS-001~NNN 可观测性规则 | — | P2 | 新建 95-observability-rules.md |
| OS-SEC-001~NNN 安全工程规则 | — | P1 | 合并 10-coding-style/*_secure 至 65-security-engineering.md |
| 公开 IRON-011~014 | — | P0 | 00-handbook §2.1 补齐 4 条 |
| 8 子仓差异化标准矩阵 | STD-IRON-18（MAINTAINERS） | P1 | 00-handbook 新增 §2.2 |
| 微核心 vs 微内核术语规范 | — | P2 | 00-handbook §7 升级为 OS-STD-TERM-001 |

---

## 第 6 章 系统性审查结论

### 6.1 审查结果汇总

| 维度 | 审查结果 |
|------|---------|
| 文档覆盖度 | ✅ **达标**——38 文档覆盖 8 大维度（编码/格式/风格/思想/流程/工具链/治理/合规） |
| OLK-6.6 对齐度 | ✅ **94.7%**（18/19 章对齐，仅 §19 I/O 缺失） |
| seL4 借鉴度 | ✅ **80.0%**（8/10 借鉴，syscall.xml + bitfield codegen 待落地） |
| 编码风格条目对齐 | ✅ **100%**（16/16 全对齐） |
| 编号体系一致性 | ❌ **不达标**——14 种前缀并存，3 段/4 段混用，15 个重复对（10 项 P0） |
| IRON 铁律一致性 | ❌ **不达标**——公开 10 条 vs 闭源 14 条，003/005/006 三条语义冲突 |
| SSoT 注册表完整性 | ⚠️ **部分达标**——注册表仅列 6 条（4 CODE + 2 FMT），实际 20+ 条 |

### 6.2 问题分类汇总

| 严重度 | 问题数 | 问题分类 |
|--------|--------|---------|
| P0-CRITICAL | 12 | IRON 铁律数量 + 3 条语义冲突（D-01）+ 02/80 重叠（D-02）+ 10-coding-style/C* 重叠（D-03）+ 编号格式混用（D-04/D-05）+ 05/06 编号段冲突（D-06）+ 同编号双义（OS-KER-002/005/011~015）+ 同规则多编号（strscpy/goto/BUG/bool） |
| P1-MAJOR | 8 | 08 前缀独立（D-07）+ I/O 缺失 + sparse+W 缺失 + syscall.xml 缺失 + bitfield codegen 缺失 + 8 子仓 MAINTAINERS 缺失 + 安全编码编号冲突 + CI 多工具矩阵缺失 |
| P2-MINOR | 5 | 09 废弃清理（D-08）+ 60/70/110 子域校验（D-09）+ seL4 借鉴检查规则缺失 + 微核心术语升级 + 可观测性规则缺失 |
| **合计** | **25** | — |

### 6.3 综合成熟度评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 内容覆盖度 | 95/100 | 38 文档覆盖全面，仅 I/O 缺失 |
| OLK-6.6 对齐度 | 94/100 | 94.7% 章节对齐 |
| seL4 借鉴度 | 80/100 | 80% 借鉴，2 项待落地 |
| 编号体系一致性 | 60/100 | 14 前缀并存，15 重复对（严重扣分） |
| IRON 铁律一致性 | 70/100 | 3 条语义冲突（严重扣分） |
| 工具链自动化 | 90/100 | 7 层验证 + checkpatch + CI 完整 |
| **综合成熟度** | **82/100（B+，有条件 Go）** | 内容质量高但编号体系混乱，需 1.0.1 M0 阶段完成 C-2.6 合并决策后升级至 A |

### 6.4 与 v0.2.1 综合成熟度的关系

v0.2.1 再检查报告给出综合成熟度 100/100（A+，无条件 Go），本报告给出 82/100（B+）。**二者不矛盾**，因为：

1. v0.2.1 评估的是**方案设计层面**的成熟度（架构/模块/接口/数据流），不含工程标准编号体系。
2. 本报告评估的是**工程标准规范层面**的成熟度，聚焦编号一致性与 IRON 铁律对齐。
3. 工程标准编号体系合并是 1.0.1 M0 阶段的工作（C-2.6 建议 4 阶段 6 周），不影响 0.1.1 文档体系"无条件 Go"状态。

**结论**：0.1.1 文档体系保持"无条件 Go"，工程标准编号体系合并在 1.0.1 M0 完成后，综合成熟度将升级至 A。

---

## 第 7 章 修复优先级矩阵与执行计划

### 7.1 修复优先级矩阵

| 优先级 | 修复项 | 数量 | 影响 | 对应决策 | 执行阶段 |
|--------|--------|------|------|---------|---------|
| P0 | IRON 铁律对齐（补齐 4 条 + 修正 3 条语义） | 1 项 | IRON 不可妥协级冲突 | D-01 | 阶段 1 |
| P0 | 02 + 80 合并（80 仅保留 CI 部分） | 1 项 | 格式规则 SSoT 混乱 | D-02 | 阶段 2 |
| P0 | 删除 10-coding-style/C* 两份文件 | 1 项 | 编号完全冲突 | D-03 | 阶段 2 |
| P0 | 格式规则迁移 OS-FMT | 1 项 | 14 条格式规则编号统一 | D-04 | 阶段 1 |
| P0 | 编码规则迁移 OS-STD-CODE | 1 项 | 20 条编码规则编号统一 | D-05 | 阶段 1 |
| P0 | 05/06 编号段隔离 PROD/TOOL | 1 项 | 30+ 条编号段冲突消除 | D-06 | 阶段 1 |
| P1 | 08 前缀统一 OS-STD-CHECK | 1 项 | 17 条检查规则融入 OS-* 体系 | D-07 | 阶段 3 |
| P1 | I/O 风格规范新增 | 1 项 | OLK-6.6 §19 覆盖 | — | 阶段 3 |
| P1 | sparse + W 分级集成（STD-CODE-07） | 1 项 | CI 基础设施 | C-2.5 | 阶段 3 |
| P1 | KABI 机制新增（STD-KABI-01） | 1 项 | 二进制兼容演进 | C-2.5 | 阶段 3 |
| P1 | 安全工程规则合并（OS-SEC） | 1 项 | 安全编码统一 | C-2.6 | 阶段 3 |
| P1 | 驱动/构建/测试工程规则新建 | 3 项 | 子域规则补齐 | C-2.6 | 阶段 3 |
| P1 | 8 子仓 MAINTAINERS（STD-IRON-18） | 1 项 | 治理落地 | C-2.5 | 阶段 3 |
| P2 | 09 废弃清理 | 1 项 | 引用清理 | D-08 | 阶段 4 |
| P2 | 60/70/110 子域校验 | 1 项 | 编号一致性校验 | D-09 | 阶段 4 |
| P2 | syscall.xml 契约（STD-DOC-18） | 1 项 | 机器可读接口契约 | C-2.5 | 阶段 4 |
| P2 | bitfield codegen（STD-CODE-08） | 1 项 | 位域自动生成 | C-2.5 | 阶段 4 |
| P2 | CI 多工具矩阵（STD-TEST-09） | 1 项 | CI 覆盖度 | C-2.5 | 阶段 4 |
| P2 | seL4 借鉴检查规则（R-04） | 1 项 | 检查规则补齐 | C-2.6 | 阶段 4 |
| P2 | 可观测性规则新建 | 1 项 | 子域规则补齐 | C-2.6 | 阶段 4 |
| P2 | 微核心术语升级 | 1 项 | 术语规范 | C-2.6 | 阶段 4 |
| **合计** | **20 项修复** | — | — | — | — |

### 7.2 执行计划

| 阶段 | 时间 | 修复项 | 工时估计 | 责任 |
|------|------|--------|---------|------|
| 阶段 1：编号体系对齐 | 1.0.1 M0 第 1-2 周 | D-01、D-04、D-05、D-06（6 项 P0） | ~80h | 架构委员会 + 工程标准组 |
| 阶段 2：重复文件合并 | 1.0.1 M0 第 3 周 | D-02、D-03（2 项 P0） | ~40h | 工程标准组 |
| 阶段 3：缺失标准补齐 | 1.0.1 M0 第 4-5 周 | D-07 + I/O + sparse + KABI + OS-SEC + OS-DRV/BUILD/TEST + MAINTAINERS（8 项 P1） | ~120h | 工程标准组 + 安全组 |
| 阶段 4：P2 项补齐 | 1.0.1 M0 第 6 周 | D-08、D-09 + syscall.xml + bitfield + CI 矩阵 + seL4 检查 + OS-OBS + 术语（7 项 P2） | ~80h | 工程标准组 |
| **合计** | **6 周** | **20 项** | **~320h** | — |

### 7.3 验证机制

每阶段完成后，运行以下验证脚本（C-2.6 §8.6 建议落地为 `scripts/check-rule-numbering.sh`）：

```bash
#!/bin/bash
# check-rule-numbering.sh
# 验证所有规则编号在所有文档中语义一致

# 1. 提取所有 OS-* 编号及其上下文
grep -rnE '\*\*OS-[A-Z]+(-[A-Z]+)*-[0-9]+\*\*' \
    docs/AirymaxOS/50-engineering-standards/ \
    docs-closed/agent-linux/agent-linux基本工程标准规范.md \
    > /tmp/all-rules.txt

# 2. 检查同编号双义
awk -F: '{print $3}' /tmp/all-rules.txt | sort | uniq -d
# 期望输出：空（无重复编号）

# 3. 检查 IRON 铁律 14 条完整性
IRON_COUNT=$(grep -cE 'OS-IRON-0[01][0-9]' \
    docs-closed/agent-linux/agent-linux基本工程标准规范.md)
if [ "$IRON_COUNT" -lt 14 ]; then
    echo "ERROR: IRON 铁律不足 14 条（当前 $IRON_COUNT）"
    exit 1
fi
```

### 7.4 验证清单

| 验证项 | 验证方法 | 期望结果 |
|--------|---------|---------|
| IRON 铁律 14 条完整 | `grep -cE 'OS-IRON-0[01][0-9]'` | ≥14 |
| IRON-003/005/006 语义统一 | 人工核对 00-handbook + 04-philosophy + 闭源总纲 | 三处定义一致 |
| 编号格式统一 | `grep -rnE 'OS-STD-[0-9]'`（3 段残留） | 0 处（全部 4 段） |
| 10-coding-style/C* 删除 | `ls 10-coding-style/` | 仅 README + 3 份安全编码 |
| 02/80 重叠消除 | `diff <(grep clang-format 02) <(grep clang-format 80)` | 80 仅含 CI 部分 |
| 05/06 编号段隔离 | `grep 'OS-STD-PROD' 05` + `grep 'OS-STD-TOOL' 06` | 各有独立前缀 |
| I/O 风格规范覆盖 | `grep -r 'ioremap\|readl\|writel' 50-engineering-standards/` | ≥1 处定义 |
| KABI 机制定义 | `ls 50-engineering-standards/09-kabi-evolution.md` | 文件存在 |
| 8 子仓 MAINTAINERS | `ls airymaxos-*/MAINTAINERS` | 8 个文件 |

---

## 第 8 章 相关文档

### 8.1 直接相关

| 文档 | 路径 | 关系 |
|------|------|------|
| 工程标准 README | `docs/AirymaxOS/50-engineering-standards/README.md` | 主索引 |
| SSoT 手册 | `docs/AirymaxOS/50-engineering-standards/00-engineering-standards-handbook.md` | SSoT 索引（需 D-01 重写） |
| 闭源工程标准总纲 | `docs-closed/agent-linux/agent-linux基本工程标准规范.md` | 闭源 SSoT（附录 A 为权威） |
| OLK-6.6 编码风格 | `01Reference/kernel-OLK-6.6/Documentation/process/coding-style.rst` | 参考基线（19 章） |
| C-2.6 合并报告 | `docs-closed/agent-linux/_analysis_0.3.0/06-engineering-standards-consolidation.md` | 编号体系合并决策（942 行） |
| C-2.5 代码分析报告 | `docs-closed/agent-linux/_analysis_0.3.0/05-code-analysis-sel4-olk66.md` | 可落地工程标准（831 行） |
| C-1 经验总结 | `docs-closed/agent-linux/_analysis_0.3.0/01-lessons-learned.md` | 历史经验教训 |

### 8.2 编号体系参考

| 文档 | 路径 | 用途 |
|------|------|------|
| OLK-6.6 .clang-format | `01Reference/kernel-OLK-6.6/.clang-format`（689 行） | 格式规则源 |
| OLK-6.6 checkpatch.pl | `01Reference/kernel-OLK-6.6/scripts/checkpatch.pl` | 规则映射源 |
| OLK-6.6 kernel-doc | `01Reference/kernel-OLK-6.6/scripts/kernel-doc` | 注释规范源 |
| OLK-6.6 kabi.h | `01Reference/kernel-OLK-6.6/include/linux/kabi.h` | KABI 宏定义源 |
| OLK-6.6 Kconfig.kabi | `01Reference/kernel-OLK-6.6/lib/Kconfig.kabi` | KABI Kconfig 源 |
| seL4 syscall.xml | `01Reference/seL4-master/libsel4/include/api/syscall.xml` | 接口契约源 |
| seL4 bitfield_gen.py | `01Reference/seL4-master/tools/bitfield_gen.py` | 位域生成源 |

### 8.3 同批分析报告

| 报告编号 | 路径 | 主题 |
|---------|------|------|
| C-1 | `00-reviews/_analysis_0.3.0/01-lessons-learned.md` | 经验总结 |
| C-2.1 | `00-reviews/_analysis_0.3.0/02-version-planning-decision.md` | 版本规划决策 |
| C-2.2 | `00-reviews/_analysis_0.3.0/04-microkernel-source-sel4-only.md` | 微内核来源收紧 |
| C-2.3 | `00-reviews/_analysis_0.3.0/03-architecture-model-analysis.md` | 架构模型论证 |
| C-2.4 | `00-reviews/_analysis_0.3.0/03b-tech-decision-linux-based.md` | 基于 Linux 改造决策 |
| C-2.5 | `00-reviews/_analysis_0.3.0/05-code-analysis-sel4-olk66.md` | seL4 + OLK-6.6 代码分析 |
| C-2.6 | `00-reviews/_analysis_0.3.0/06-engineering-standards-consolidation.md` | 工程标准合并 |
| **C-2（本报告）** | `00-reviews/_analysis_0.3.0/07-engineering-standards-review.md` | **工程标准逐章审查** |
| C-2.8 | `00-reviews/_analysis_0.3.0/08-reference-audit.md` | 文档引用校对 |

---

> **报告结束** | C-2 工程标准规范逐章审查 | v0.3.0 | 2026-07-09 | 闭源不公开
> **综合成熟度**: 82/100（B+，有条件 Go）—— 内容质量高但编号体系混乱，需 1.0.1 M0 完成 C-2.6 合并决策后升级至 A
> **下次审查触发条件**: C-2.6 阶段 1 完成（编号体系对齐）后启动验证审查
