Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

<!-- SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0 -->
<!-- 保密级别：SPHARX Ltd 内部参考，闭源不公开 -->
<!-- 版本：3.0 | 日期：2026-07-14 -->

# Airymax agentrt v3.0 综合分析报告（含系统性修正路线图）

> **文档定位**：v3.0 全面审查 + 系统性修正任务的阶段 2 综合分析报告。整合 4 份并行 v3.0 审查报告（开源文档 / 闭源文档 / 源码 / 跨文档一致性），对 agentrt 项目进行去重归类、系统性修正路线图制定与 1.0.1 M1 就绪判定。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：3.0（2026-07-14）。
> **审查范围**：仅 `agentrt` 模块（`docs/AirymaxRT/` + `docs-closed/agentrt/` + `agentrt/` 源码）；**不涉及** `agent-linux`。
> **评分模型**：规范声明层（35%）+ 方案设计层（40%）+ 实现落地层（25%）三维度加权。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. v2.0 修正持久性综合判定](#2-v20-修正持久性综合判定)
- [3. v3.0 问题去重与归类](#3-v30-问题去重与归类)
- [4. 系统性修正路线图](#4-系统性修正路线图)
- [5. 1.0.1 M1 就绪判定](#5-101-m1-就绪判定)
- [6. 修正后评分预估](#6-修正后评分预估)
- [7. 附录](#7-附录)

---

## 1. 执行摘要

### 1.1 v3.0 审查范围与方法

本报告整合 4 份并行 v3.0 审查报告，采用"分域审查 + 交叉去重 + 主题归类"三阶段方法：

| Agent | 审查域 | 审查范围 | 报告路径 |
|-------|--------|---------|---------|
| Agent 1 | 开源文档 | `docs/AirymaxRT/`（87 .md + 1 .dox + 1 .drawio） | `01-open-docs-review.md` |
| Agent 2 | 闭源文档 | `docs-closed/agentrt/`（主手册 + README + 07-subsystem-specs/ + 06-contracts/ 等） | `02-closed-docs-review.md` |
| Agent 3 | 源码 | `agentrt/`（833 源文件：atoms 237 + daemons 243 + cupolas 95 + gateway 33 + commons 184 + protocols 41） | `03-source-code-review.md` |
| Agent 4 | 跨文档一致性 | 开源 + 闭源 + [SC] 6 头文件 + SSoT 交叉对照（8 维度 A-H） | `04-cross-doc-consistency-review.md` |

每份报告均通过 Grep 机器检查独立复核，所有结论附 `文件路径:L行号` 证据。本综合报告在 4 份报告基础上执行去重合并与主题归类。

### 1.2 评分变化轨迹

| 版本阶段 | 综合评分 | 级别 | 变化 | 主要原因 |
|---------|---------|------|------|---------|
| v1.0（初始审查） | 65 | C+ | — | 8 项 P0 + 多项 P1/P2 |
| v2.0（修正前） | 63 | C+ | -2 | v2.0 审查新发现 30 项问题 |
| v2.0（修正后预估） | 72 | B- | +9 | 9/10 P0 修正 + 9/13 P1 修正 |
| **v3.0（本次复审）** | **66** | **C+** | **-6** | 新发现 10 P0 + 19 P1 + 18 P2（去重后） |

### 1.3 核心结论

> **agentrt 项目 v3.0 复审后未达到 1.0.1 M1 代码开发就绪条件（≥80/B）**。
>
> v2.0 修正在其已识别范围内整体持久（开源 9/10 + 闭源 7/7 + 源码 7/7 + 跨文档 7/7 = 30/31 持久），但 v3.0 深度审查暴露了 v2.0 修正的**三大盲区**：
>
> 1. **错误码 SSoT 系统性崩溃**：50-engineering-standards/ 内部 5+ 套错误码方案并行，SSoT 声明的权威文件 `include/airymax/error.h` 不存在，`airy_err_t` 定位声明错误，源码实际值（-1/-2/-6）与文档 SSoT 值（-22/-12/-110）严重冲突。
> 2. **v2.0 修正范围盲区**：P0-DQC-2 仅修正 `agentrt工程标准规范手册.md` 1 个文件，遗漏 `07-subsystem-specs/`（302 处）+ `06-contracts/`（38 处）共 340 处 `agentos_*` 残留；P0-4 仅修正 `06-ipc/README.md`，遗漏 `02-l2-service-protocol.md` 和闭源手册 §34.2 两处 IPC 头三重违规。
> 3. **v2.0 修正副作用**：N1/N3 DCLP 修正引入状态机缺陷（假成功 + 状态卡死）；N5 修正不完整（5 个 daemon 同模式未修）；N6 修正被 `#ifndef AIRY_RT_PLATFORM_H` 屏蔽对生产代码无效。
>
> **1.0.1 M1 启动判定**：必须在 M1 启动前完成工作流 A（错误码 SSoT 统一）+ B（IPC 头对齐）+ C（函数前缀 + §11.6 重写）+ E（DCLP 并发安全修复）+ G（文档工程规范盲区修正），预计 ~43h。完成后预估评分 ~76/B，仍低于 80/B 阈值；需进一步推进工作流 F（P0-2 源码工程标准分批处理 ~40h）方可达标。

---

## 2. v2.0 修正持久性综合判定

### 2.1 持久性验证综合矩阵

整合 4 份报告的 v2.0 修正持久性验证结果：

| Agent | 验证项总数 | 完全持久 | 部分持久 | 回退 | 持久率 |
|-------|----------|---------|---------|------|--------|
| Agent 1（开源文档） | 10 | 9 | 1 | 0 | 90% |
| Agent 2（闭源文档） | 7 | 7 | 0 | 0 | 100% |
| Agent 3（源码） | 7 | 7 | 0 | 0 | 100% |
| Agent 4（跨文档） | 7 | 7 | 0 | 0 | 100% |
| **合计** | **31** | **30** | **1** | **0** | **96.8%** |

**核心结论**：v2.0 修正整体持久性良好（30/31 完全持久），无回退项。唯一的"部分持久"项为 Agent 1 验证的 P0-4 IPC 头三重违规——`06-ipc/README.md` 已修正，但 `02-l2-service-protocol.md` 遗漏（详见 §3.2）。

### 2.2 v2.0 修正范围盲区

v3.0 审查发现 v2.0 修正存在两大范围盲区，导致大量残留未被发现：

#### 2.2.1 闭源文档盲区：仅覆盖手册 1 文件

v2.0 P0-DQC-1/P0-DQC-2 修正仅作用于 `agentrt工程标准规范手册.md` 1 个文件，未覆盖 `docs-closed/agentrt/` 下其他文件：

| 盲区范围 | 残留类型 | 残留数量 | 涉及文件数 | 出处 |
|---------|---------|---------|----------|------|
| `07-subsystem-specs/` | `agentos_*` 前缀残留 | **302 处** | 10 文件 | Agent 2 P0-V3-1 |
| `06-contracts/` | `agentos_*` 前缀残留 | **38 处** | 3 文件 | Agent 2 P0-V3-2 |
| `05-tech-reference-and-improvement/` | `agentos_*` 历史归档 | **1738 处** | 5 文件 | Agent 2 P2-V3-3（归档不修） |
| **小计（生产级文档）** | — | **340 处** | **13 文件** | — |

**影响**：开发者按 `07-subsystem-specs/03-coreloopthree.md` 等子系统规格文档编写代码，将使用 `agentos_loop_create`/`agentos_error_t` 等错误前缀，CI 门禁直接失败（源码已全面使用 `airy_*`）。`06-contracts/` 合约头文件前缀错误将直接破坏编译。

#### 2.2.2 开源文档盲区：P0-4 IPC 头修正遗漏

v2.0 P0-4 修正仅覆盖 `30-interfaces/06-ipc/README.md`，遗漏同目录下 `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md` 和闭源手册 §34.2 两处同款三重违规。

### 2.3 v2.0 修正副作用

Agent 3 源码复审发现 4 项 v2.0 修正引入的副作用或修正不完整：

| 副作用编号 | 源修正项 | 副作用描述 | 严重度 | 证据 |
|-----------|---------|-----------|--------|------|
| V3.0-N1 | N1/N3（DCLP） | 自旋等待线程在初始化线程失败后仍返回 SUCCESS | P1 | `agentrt/atoms/corekern/src/core_init.c:66` / `agentrt/cupolas/src/cupolas.c:112` |
| V3.0-N2 | N1/N3（DCLP） | 超时后状态停留在 2，后续调用永久超时 | P1 | `agentrt/atoms/corekern/src/core_init.c:62` / `agentrt/cupolas/src/cupolas.c:109` |
| V3.0-N3 | N5（goto） | 相同 goto-less 模式存在于 5 个其他 daemon（19 处 `return 1`） | P1 | `agentrt/daemons/{market_d,llm_d,tool_d,monit_d,channel_d}/src/main.c` |
| V3.0-N4 | N6（sync_compat） | 修正被 `#ifndef AIRY_RT_PLATFORM_H` 屏蔽，生产代码普遍包含 platform.h，N6 修正对大多数调用方无效 | P1 | `agentrt/commons/utils/sync/include/sync_compat.h:32` / `agentrt/commons/platform/platform.c:194-331` |

**关键风险**：V3.0-N1/N2 是并发安全的真实风险——多线程并发初始化时，若初始化线程失败，等待线程将"假成功"返回，调用方在未初始化的运行时上操作，可能导致 NULL deref、数据损坏或安全穹顶失效。

---

## 3. v3.0 问题去重与归类

### 3.1 错误码 SSoT 系统性崩溃（最严重）

#### v3.0-综合-P0-1：SSoT 50-engineering-standards 内部错误码 5+ 套方案并行

| 属性 | 内容 |
|------|------|
| **严重度** | P0 |
| **问题摘要** | `docs/AirymaxOS/50-engineering-standards/` 内部存在 5+ 套错误码方案并行，数值互相矛盾（`AIRY_EINVAL` 有 -22/-1/-2 三种值），违反 SSoT 原则 |
| **证据位置** | 方案 A: `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md:420-427`（POSIX errno 负值 -22/-12/-110）；方案 B: `docs/AirymaxOS/50-engineering-standards/30-runtime-interfaces/runtime_interfaces.md:1753-1770`（自定义序列 -1/-2/-11）；方案 C: `docs/AirymaxOS/50-engineering-standards/10-coding-style/coding_conventions.md:2959-2981`（已废弃 -2/-4/-6）；方案 D: `docs/AirymaxOS/50-engineering-standards/50-project-erp/project_erp.md:987-1003`（位掩码 0x00010000）；SSoT 声明: `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:81` |
| **影响范围** | 编译行为不可预测；跨模块错误码语义断裂；调试困难 |
| **出处报告** | Agent 4 P0-v3-1 |
| **工作量估算** | ~6h（确定唯一权威方案 + 废弃其余 4 套 + 交叉引用修正） |

#### v3.0-综合-P0-2：源码 airy_types.h 错误码值与文档 SSoT 严重不一致

| 属性 | 内容 |
|------|------|
| **严重度** | P0 |
| **问题摘要** | 源码 `AIRY_EINVAL=-1`、`AIRY_ENOMEM=-2`、`AIRY_ETIMEDOUT=-6`，文档 SSoT 值为 `-22`/`-12`/`-110`，所有返回错误码的函数语义与文档不符 |
| **证据位置** | `agentrt/commons/include/airy_types.h:50-55`；文档 SSoT: `docs/AirymaxRT/10-architecture/00-architectural-principles.md:937`（`AIRY_EINVAL=(-22)`）；`docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md:420-427` |
| **影响范围** | 所有返回错误码的函数语义与文档不符；跨模块调试困难；error.h 注释自承认技术债（`agentrt/commons/utils/error/include/error.h:66-68`） |
| **出处报告** | Agent 4 P0-v3-2 + Agent 3 §3.2 延期项 #6 |
| **工作量估算** | ~8h（全量对齐 30 个码 + 调用方审查）；~2h（仅对齐 3 个核心码） |

#### v3.0-综合-P0-3：SSoT 声明 airy_err_t 在 cognition_types.h，实际在 airy_types.h

| 属性 | 内容 |
|------|------|
| **严重度** | P0 |
| **问题摘要** | SSoT 声明 `airy_err_t` 定义于 `cognition_types.h`，实际源码 38 行中 0 匹配 `airy_err_t`，真实定义在 `airy_types.h:40`。06-iron9 文档同样做出错误声明 |
| **证据位置** | 声明: `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:73` + `docs/AirymaxRT/10-architecture/06-iron9-shared-model.md:70`；实际: `agentrt/commons/include/airy_types.h:40`（`typedef int32_t airy_err_t;`）；验证: `agentrt/commons/include/airymax/cognition_types.h` 完整 38 行 Grep `airy_err_t` = 0 匹配 |
| **影响范围** | 开发者按 SSoT 引用 `#include <airymax/cognition_types.h>` 获取 `airy_err_t` 将编译失败 |
| **出处报告** | Agent 4 P0-v3-3 + P1-v3-6 |
| **工作量估算** | ~1h（修正 SSoT 声明 + 06-iron9 描述，或迁移 airy_err_t 定义到 cognition_types.h） |

#### v3.0-综合-P0-4：SSoT 声明 include/airymax/error.h 为权威源，该文件不存在

| 属性 | 内容 |
|------|------|
| **严重度** | P0 |
| **问题摘要** | SSoT 声明 `include/airymax/error.h` 为错误码权威源，但该文件不存在（Glob 验证 No file found），实际路径为 `agentrt/commons/utils/error/include/error.h`。4+ 处文档引用断链 |
| **证据位置** | 声明: `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:81` + `docs/AirymaxRT/10-architecture/00-architectural-principles.md:919,921` + `docs/AirymaxRT/TERMINOLOGY.md:209` + `docs/AirymaxRT/20-modules/10-contracts/03-protocol-contract.md:692`；实际: `agentrt/commons/utils/error/include/error.h` |
| **影响范围** | SSoT 声明的权威源不存在，4+ 处文档引用断链 |
| **出处报告** | Agent 4 P0-v3-4 |
| **工作量估算** | ~1h（创建 symlink 或修正所有引用路径） |

#### v3.0-综合-P0-5：闭源手册错误码类型名 airy_error_t 与 SSoT airy_err_t 不一致

| 属性 | 内容 |
|------|------|
| **严重度** | P0 |
| **问题摘要** | 闭源手册正文 6 处使用 `airy_error_t`（含 `error`），与开源 SSoT `airy_err_t`（无 `error`）不一致，且与同目录 `07-subsystem-specs/02-corekern.md`（已用 `airy_err_t`）内部矛盾 |
| **证据位置** | `docs-closed/agentrt/agentrt工程标准规范手册.md:251,507,535,764,787,1521`；SSoT: `docs/AirymaxRT/10-architecture/00-architectural-principles.md:925`（`typedef int32_t airy_err_t;`）；内部矛盾: `docs-closed/agentrt/07-subsystem-specs/02-corekern.md:62,74,79,84`（已用 `airy_err_t`） |
| **影响范围** | 开发者按手册编写代码将使用错误类型名，编译失败 |
| **出处报告** | Agent 2 P0-V3-4 |
| **工作量估算** | ~0.5h（6 处 `airy_error_t` → `airy_err_t`） |

#### v3.0-综合-P1-1：源码 error.h 内部语义重叠/同值冲突

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | error.h 内部存在同值冲突（`AIRY_ERR_UNKNOWN=-1` 与 `airy_types.h:50` `AIRY_EINVAL=-1` 同值）和语义重叠（`AIRY_ERR_PROTOCOL=-900` 与 `AIRY_EPROTO=-13`），`#undef AIRY_EPERM` 后重定义覆盖原始值 |
| **证据位置** | `agentrt/commons/utils/error/include/error.h:46`（`AIRY_ERR_UNKNOWN=-1`）/ `:493`（`AIRY_ERR_PROTOCOL=-900`）/ `:88-89`（`#undef AIRY_EPERM` 重定义 -10） |
| **影响范围** | 错误码语义歧义；调用方无法精确判别错误类型 |
| **出处报告** | Agent 4 P1-v3-5 |
| **工作量估算** | ~2h（消除数值重叠 + 调用方审查） |

#### v3.0-综合-P1-2：源码 error.h 仍定义和使用 AIRY_OK

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | 文档声明"不再使用 `AIRY_OK`"（`TERMINOLOGY.md:212`），但源码 error.h 仍定义并活跃使用 `AIRY_OK`（6 处） |
| **证据位置** | `agentrt/commons/utils/error/include/error.h:43`（`#define AIRY_OK 0`）/ `:668,681`（`if (__err != AIRY_OK)`）；文档声明: `docs/AirymaxRT/TERMINOLOGY.md:212` + `docs/AirymaxRT/20-modules/10-contracts/03-protocol-contract.md:692` |
| **影响范围** | 文档与源码不一致；成功码命名不统一 |
| **出处报告** | Agent 4 P1-v3-7 |
| **工作量估算** | ~1h（移除 AIRY_OK 定义 + 替换调用方为 AIRY_EOK） |

#### v3.0-综合-P1-3：闭源手册 §34.5 错误码分段与开源 SSoT 不一致

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | 闭源手册 §34.5 错误码分段为 9 段（通用/系统/内核/服务/LLM/执行/记忆/安全/协议），开源 SSoT 为 11 段（含 i18n/发行版），权威源路径用旧 `agentos/` 路径 |
| **证据位置** | 闭源手册: `docs-closed/agentrt/agentrt工程标准规范手册.md:3386-3405`（9 段，line 3393-3403）；开源 SSoT: `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:81`（11 段）；权威源路径错误: `:3390`（`agentos/commons/utils/error/include/error.h`） |
| **影响范围** | 闭源手册错误码体系不完整；权威源路径断链 |
| **出处报告** | Agent 2 P1-V3-3 |
| **工作量估算** | ~1h（§34.5 全节对齐 + 补 i18n/发行版分段 + 修正权威源路径） |

---

### 3.2 IPC 消息头 SSoT 对齐

#### v3.0-综合-P0-6：02-l2-service-protocol.md IPC 头三重违规未修正

| 属性 | 内容 |
|------|------|
| **严重度** | P0 |
| **问题摘要** | v2.0 P0-4 修正遗漏 `02-l2-service-protocol.md`，该文件仍包含与 [SC] SSoT 直接矛盾的 `are_ipc_message_header_t` 定义（typedef + `uint32_t` + 13 字段 + 无 packed + 注释中的 `_Static_assert`），且使用 `ARE_IPC_MAGIC` 宏名（应为 `AIRY_IPC_MAGIC`） |
| **证据位置** | `docs/AirymaxRT/30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md:55-116`（L60 `ARE_IPC_MAGIC` / L93 `typedef struct are_ipc_message_header` / L94-108 13 字段 `uint32_t` 类型 / L108 无 `__attribute__((packed))` / L109 无真实 `_Static_assert`）；SSoT: `docs/AirymaxRT/30-interfaces/06-ipc/README.md:53-66`（`struct airy_ipc_msg_hdr` + `__u32` + 8 字段 + packed + `_Static_assert`）；Grep 实测 9 处 `are_ipc_message_header` |
| **影响范围** | 同一 magic 值 `0x41524531` 对应两种不同字段布局（13 vs 8 字段），接收方无法判别应按哪个布局解析；违反 IRON-014（[SC] 6 头文件单一数据源） |
| **出处报告** | Agent 1 v3.0-P0-1 + Agent 4 P0-v3-5 + P1-v3-4 |
| **工作量估算** | ~3h（对齐 SSoT + 迁移说明 + 评估 L2 协议独立性） |

#### v3.0-综合-P0-7：闭源手册 §34.2 IPC 头三重违规残留

| 属性 | 内容 |
|------|------|
| **严重度** | P0 |
| **问题摘要** | 闭源手册 §34.2 STD-02 仍使用 `are_ipc_message_header_t`（typedef + `uint32_t` + 13 字段 + 无 packed + 无 `_Static_assert`），且作为"强制规则 STD-02"使用，误导性更强。是 v2.0 开源 P0-4 修正未同步到闭源手册 |
| **证据位置** | `docs-closed/agentrt/agentrt工程标准规范手册.md:3328-3356`（L3330 `are_ipc_message_header_t` / L3334 typedef / L3335-3348 13 字段 / L3349 无 packed / L3353 无 _Static_assert）；另有 L2901 引用 `are_ipc_message_header_t.trace_id` |
| **影响范围** | 开发者按闭源手册 §34.2 实现的 IPC 消息头将与源码 `commons/include/airymax/ipc.h` 不兼容；作为"强制规则"误导性更强 |
| **出处报告** | Agent 2 P0-V3-3 + Agent 4 P0-v3-6 |
| **工作量估算** | ~2h（§34.2 全节重写对齐 SSoT） |

---

### 3.3 函数前缀与改名规范违反 SSoT

#### v3.0-综合-P0-8：07-subsystem-specs/ 10 文件 302 处 agentos_* 前缀残留

| 属性 | 内容 |
|------|------|
| **严重度** | P0 |
| **问题摘要** | v2.0 P0-DQC-2 修正仅作用于 `agentrt工程标准规范手册.md` 1 个文件，`07-subsystem-specs/` 下 10 个子系统规格文件未纳入修正范围，仍使用已废弃的 `agentos_*` 前缀。Grep 实测 302 处/10 文件 |
| **证据位置** | `docs-closed/agentrt/07-subsystem-specs/03-coreloopthree.md`（166 处）/ `05-gateway-d.md`（42 处）/ `09-memory.md`（35 处）/ `06-llm-d.md`（21 处）/ `12-tool-d.md`（20 处）/ `08-market-d.md`（10 处）/ `04-cupolas.md`（3 处）/ `01-checkpoint.md`（2 处）/ `11-orchestrator.md`（2 处）/ `07-manager.md`（1 处）；对比: `02-corekern.md`（0 处，已用 `airy_*`）+ `10-openlab.md`（0 处） |
| **影响范围** | 开发者按子系统规格文档编写代码将使用错误前缀，CI 门禁直接失败；07-subsystem-specs/ 内部不一致（02-corekern.md 已修正 vs 其他 10 文件未修正） |
| **出处报告** | Agent 2 P0-V3-1 |
| **工作量估算** | ~6h（10 文件逐项核对类型名，如 `agentos_error_t` → `airy_err_t` 而非 `airy_error_t`） |

#### v3.0-综合-P0-9：06-contracts/ 3 文件 38 处 agentos_* 前缀残留

| 属性 | 内容 |
|------|------|
| **严重度** | P0 |
| **问题摘要** | `06-contracts/` 下 3 个合约文件未纳入 v2.0 P0-DQC-2 修正范围，仍使用 `agentos_*` 前缀。合约头文件作为模块间接口契约，前缀错误将直接破坏编译 |
| **证据位置** | `docs-closed/agentrt/06-contracts/contract_A_C.h`（17 处，L131 `#define CONTRACT_AC_METRIC_PREFIX "agentos_"`）/ `contract_test.c`（17 处）/ `contract_A_B.h`（4 处） |
| **影响范围** | 合约头文件定义的指标前缀 `agentos_` 与源码实际使用的 `airy_` 不一致，Prometheus 指标采集失败；编译破坏 |
| **出处报告** | Agent 2 P0-V3-2 |
| **工作量估算** | ~1h（3 文件全量替换） |

#### v3.0-综合-P0-10：闭源手册 §11.6 以"强制规则"公然违反 SSoT 函数前缀规则

| 属性 | 内容 |
|------|------|
| **严重度** | P0 |
| **问题摘要** | §11.6 标题为"airy_ → agentrt_ 彻底改名规范"，要求将 SSoT 正确前缀 `airy_*` 改为 SSoT 禁止前缀 `agentrt_*`。BAN-342 要求"airy_ 零残留"，但 SSoT 规定 `airy_*` 是 [SC] + 应用层正确前缀。源码有 1788 处 `airy_`、0 处 `agentrt_`。如果执行 §11.6 将破坏整个 [SC] 共享契约层 |
| **证据位置** | `docs-closed/agentrt/agentrt工程标准规范手册.md:1509`（标题）/ `:1511`（核心决策）/ `:1521`（`airy_error_t` → `agentrt_error_t`）/ `:1531`（"airy_ 零残留: grep airy_ → 0"）/ `:1542`（BAN-342）；SSoT: `docs/AirymaxRT/10-architecture/06-iron9-shared-model.md:268`（`agentrt_*` 不使用）/ `:274`（`airy_*` 是正确前缀） |
| **影响范围** | 工程标准手册以"强制规则"名义公然违反 SSoT；如执行将导致跨端通信断裂；与术语表 lines 98-111（`airy_*`）直接矛盾 |
| **出处报告** | Agent 2 P1-V3-4 + Agent 4 P0-v3-7 |
| **工作量估算** | ~0.5h（添加历史决策声明，保留 §11.6 作为 v26.0 历史记录，标注"未执行，当前前缀规范以 §1.6 术语表为准"） |

#### v3.0-综合-P1-4：闭源手册 line 4175 "agentrt_ 前缀"与术语表矛盾

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | 闭源手册 §37.3 PROD-03（line 4175）描述 `include/`: C 公开 ABI 头文件（agentrt_ 前缀），与术语表 lines 98-111（`airy_*`）和实际源码（`airy_*`，1788 处）矛盾 |
| **证据位置** | `docs-closed/agentrt/agentrt工程标准规范手册.md:4175` |
| **影响范围** | 开发者对 C 公开 ABI 前缀产生混淆 |
| **出处报告** | Agent 2 P1-V3-5 |
| **工作量估算** | ~0.1h（line 4175 `agentrt_ 前缀` → `airy_ 前缀`） |

#### v3.0-综合-P1-5：SSoT §4.4.2 函数前缀规则内部矛盾

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | `coding_conventions.md` §4.4.2 内部自相矛盾：L2606 说 agent-linux [IND] 用 `airy_*`，L2607 说 `airy_*` 不得用于 agent-linux 专属功能——同一节内直接矛盾。L2601 用 `AIRYMAXOS_*` 作为活跃前缀，但 `06-iron9:270` 说 `airymaxos_*` 已废弃 |
| **证据位置** | `docs/AirymaxOS/50-engineering-standards/10-coding-style/coding_conventions.md:2599-2607`（L2606 vs L2607 直接矛盾；L2601 `AIRYMAXOS_*` vs `06-iron9:270` `~~airymaxos_*~~` 已废弃） |
| **影响范围** | 函数前缀规则自身矛盾，开发者无法确定正确前缀 |
| **出处报告** | Agent 4 P1-v3-3 |
| **工作量估算** | ~2h（重写 §4.4.2 消除矛盾 + 与 06-iron9 §3.12 对齐） |

---

### 3.4 路径引用断链

#### v3.0-综合-P1-6：agentrt/daemon/ 路径单数 vs 实际 agentrt/daemons/ 复数（44 处/16 文件）

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | 开源文档中大量使用单数 `agentrt/daemon/` 引用源码路径，与实际源码目录结构 `agentrt/daemons/`（复数）不一致。Grep 实测 44 处/16 文件 |
| **证据位置** | `docs/AirymaxRT/10-architecture/00-architectural-principles.md`（9 处）/ `10-architecture/50-services/02-logging.md`（7 处）/ `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md`（8 处）/ `30-interfaces/05-runtime-interfaces/01-l1-runtime-interface.md`（2 处）/ `30-interfaces/05-runtime-interfaces/03-l3-security-governance.md`（2 处）/ `30-interfaces/60-syscalls/06-telemetry.md`（1 处）/ `20-modules/10-contracts/03-protocol-contract.md`（3 处）/ `20-modules/10-contracts/04-syscall-api-contract.md`（1 处）/ `20-modules/10-contracts/05-logging-format.md`（3 处）/ `00-requirements/04-design-principles.md` + `04-design-principles-cn.md`（2 处）/ `140-application-development/24-create-agent.md`（2 处）/ `140-application-development/25-create-skill.md`（1 处）/ `140-application-development/23-troubleshooting-faq.md`（1 处）/ `140-application-development/26-coreloopthree-dag-integration.md`（1 处）/ `10-architecture/30-kernel/01-ipc.md`（1 处） |
| **影响范围** | 外部开发者按文档路径查找源码文件全部失败；CI 链接检查无法通过 |
| **出处报告** | Agent 1 v3.0-P1-1 |
| **工作量估算** | ~1.5h（三步替换法避免子串误替换） |

#### v3.0-综合-P1-7：L1/L2/L3 文件间 cross-reference 文件名错误（15 处/4 文件）

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | `30-interfaces/05-runtime-interfaces/` 下 L1/L2/L3 三个标准文档相互引用时使用旧命名约定（如 `L1_runtime_interface.md`），与实际文件名（`01-l1-runtime-interface.md`）不匹配 |
| **证据位置** | `01-l1-runtime-interface.md:16,17,791,792`（4 处）/ `02-l2-service-protocol.md:25,26,755,756`（4 处）/ `03-l3-security-governance.md:26,27,775,776`（4 处）/ `README.md:22,23,24`（3 处） |
| **影响范围** | 同目录内 cross-reference 全部 broken；Markdown 渲染器与 CI 链接检查器报错 |
| **出处报告** | Agent 1 v3.0-P1-2 |
| **工作量估算** | ~0.3h |

#### v3.0-综合-P1-8：AgentRT/ 大写断链引用（60 处/24 文件）

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | Linux 文件系统大小写敏感，实际目录为 `agentrt/`（小写），但开源文档中存在 `AgentRT/`（大写）引用。Grep 实测 60 处/24 文件 |
| **证据位置** | `docs/AirymaxRT/TERMINOLOGY.md`（8 处）/ `30-interfaces/01-doxygen-guide.md`（6 处）/ `30-interfaces/60-syscalls/01-agent.md`（3 处）/ `140-application-development/01-getting-started.md`（4 处）/ `140-application-development/10-migration-guide.md`（4 处）/ `10-architecture/40-philosophy/01-design-philosophy.md`（2 处）/ 等 24 文件 |
| **影响范围** | Linux 下路径无法解析；CI 链接检查失败 |
| **出处报告** | Agent 4 P1-v3-1 |
| **工作量估算** | ~2h（逐文件区分大小写敏感场景 vs 品牌名用法） |

#### v3.0-综合-P1-9：闭源手册 docs/AirymaxAgentOS/ 路径错误（7 处）

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | 闭源手册 7 处引用 `docs/AirymaxAgentOS/`，实际目录为 `docs/AirymaxOS/`（无 `Agent`） |
| **证据位置** | `docs-closed/agentrt/agentrt工程标准规范手册.md:20,2232,4327,4341,4398,4421,4442` |
| **影响范围** | 路径无法解析；误导开发者对 OS 文档目录的认知 |
| **出处报告** | Agent 2 P1-V3-1 + Agent 4 P1-v3-2 |
| **工作量估算** | ~0.3h（7 处 `docs/AirymaxAgentOS/` → `docs/AirymaxOS/`） |

#### v3.0-综合-P1-10：闭源手册 agentos/ 目录路径残留（60+ 处）

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | 闭源手册正文广泛使用 `agentos/` 目录路径（带斜杠），与 §11.6.1 L1 描述的 `agentos/` → `agentrt/` 改名矛盾，与实际源码目录（`agentrt/`）不一致。P0-DQC-2 全量替换仅针对 `agentos_`（带下划线），未涉及 `agentos/`（带斜杠） |
| **证据位置** | `docs-closed/agentrt/agentrt工程标准规范手册.md:83,84`（团队三权分立代码范围）/ `:2058-2060` / `:2712` / `:2866`（`/var/log/agentos/agentos.log`）/ `:3019-3025`（许可证表 7 处）/ `:3371`（`agentos.yaml`）/ `:3384` / `:3390`（错误码权威源路径）/ `:3461-3465` |
| **影响范围** | 开发者按手册路径引用源码将找不到文件；错误码权威源路径与开源 SSoT `include/airymax/error.h` 不一致 |
| **出处报告** | Agent 2 P1-V3-2 |
| **工作量估算** | ~3h（60+ 处逐项核对，区分目录路径 vs 历史记录） |

#### v3.0-综合-P1-11：02-logging.md 包含错误的双重路径与错误归属

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | `02-logging.md` 多处包含错误路径：路径重复（`agentrt/daemon/agentrt/commons/...`）与错误归属（`agentrt/daemon/atoms`） |
| **证据位置** | `docs/AirymaxRT/10-architecture/50-services/02-logging.md:113`（`agentrt/daemon/agentrt/commons/include/svc_common.h`）/ `:732`（`agentrt/daemon/atoms`）/ `:754`（同 L113 路径重复） |
| **影响范围** | 路径无法解析；误导开发者对源码目录结构的理解 |
| **出处报告** | Agent 1 v3.0-P1-4 |
| **工作量估算** | ~0.2h |

#### v3.0-综合-P1-12：06-glossary-index.md 引用不存在的 error_code_reference.md

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | `06-glossary-index.md` 两处引用 `error_code_reference.md`，该文件不存在（实际文件为 `project_erp.md`） |
| **证据位置** | `docs/AirymaxRT/20-modules/10-contracts/06-glossary-index.md:185,187` |
| **影响范围** | 链接 broken；开发者无法访问错误码完整映射关系 |
| **出处报告** | Agent 1 v3.0-P1-5 |
| **工作量估算** | ~0.1h |

#### v3.0-综合-P2-1：01-doxygen-guide.md 路径错误（2 处）

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | doxygen-guide 路径错误 + 引用不存在的 `code_comment_template.md` |
| **证据位置** | `docs/AirymaxRT/30-interfaces/01-doxygen-guide.md:326`（`../../00-architectural-principles.md` 应为 `../10-architecture/00-architectural-principles.md`）/ `:327`（`code_comment_template.md` 不存在） |
| **出处报告** | Agent 1 v3.0-P2-1/2 |
| **工作量估算** | ~0.1h |

#### v3.0-综合-P2-2：30-interfaces/README.md 引用不存在的 naming_conventions.md

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | `30-interfaces/README.md:109` 引用 `naming_conventions.md`，该文件不存在于 `10-coding-style/` 目录 |
| **证据位置** | `docs/AirymaxRT/30-interfaces/README.md:109` |
| **出处报告** | Agent 1 v3.0-P2-3 |
| **工作量估算** | ~0.05h |

#### v3.0-综合-P2-3：0.1.1详细任务清单.md 不存在（4 处引用）

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | 4 处引用 `../../../docs-closed/0.1.1详细任务清单.md`，该文件不存在 |
| **证据位置** | `docs/AirymaxRT/30-interfaces/06-ipc/README.md:104` / `30-interfaces/07-rpc-api/README.md:82` / `30-interfaces/08-service-discovery/README.md:68` / `140-application-development/01-sdk/README.md:72` |
| **出处报告** | Agent 1 v3.0-P2-4 + Agent 4 P2-v3-1 |
| **工作量估算** | ~0.3h |

#### v3.0-综合-P2-4：TERMINOLOGY.md 路径头大小写错误

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | `TERMINOLOGY.md:8` 路径头 `Docs/TERMINOLOGY.md` 大小写错误，实际为 `docs/AirymaxRT/TERMINOLOGY.md` |
| **证据位置** | `docs/AirymaxRT/TERMINOLOGY.md:8` |
| **出处报告** | Agent 1 v3.0-P2-5 |
| **工作量估算** | ~0.05h |

#### v3.0-综合-P2-5：Docs/ 大小写错误（2 处）

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | 2 处使用 `Docs/`（大写 D），实际仓库目录为 `docs/`（小写 d） |
| **证据位置** | `docs/AirymaxRT/30-interfaces/05-runtime-interfaces/README.md:29` / `docs/AirymaxRT/140-application-development/02-build-guide.md:80` |
| **出处报告** | Agent 1 v3.0-P2-6 |
| **工作量估算** | ~0.05h |

---

### 3.5 源码并发安全（DCLP 状态机）

#### v3.0-综合-P1-13：DCLP 自旋等待在初始化失败后返回 SUCCESS

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | N1/N3 修正引入的 DCLP 自旋等待存在状态机缺陷。当初始化线程失败并将状态重置为 0 时，自旋等待线程的循环退出（state != 2），但随后直接返回 SUCCESS 而未验证 state == 1。多线程并发初始化时"假成功"风险 |
| **证据位置** | `agentrt/atoms/corekern/src/core_init.c:66`（`return AIRY_SUCCESS;` ← BUG: state 可能是 0）/ `agentrt/cupolas/src/cupolas.c:112`（`return CUPOLAS_OK;` ← BUG） |
| **影响范围** | 多线程并发初始化时，若初始化线程失败，等待线程将"假成功"返回，调用方在未初始化的运行时上操作，可能导致 NULL deref、数据损坏或安全穹顶失效 |
| **出处报告** | Agent 3 V3.0-N1 |
| **工作量估算** | ~1h（2 处修正 + 注释 + 测试场景设计） |

#### v3.0-综合-P1-14：DCLP 自旋超时后状态卡死在 2

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | N1/N3 修正增加的超时保护在触发时仅返回错误，未重置状态。状态停留在 2（initializing），后续所有调用都将进入自旋等待并再次超时，运行时永久不可初始化 |
| **证据位置** | `agentrt/atoms/corekern/src/core_init.c:62`（`return AIRY_ERR_TIMEOUT;` ← BUG: state 仍为 2，未重置）/ `agentrt/cupolas/src/cupolas.c:109`（`return cupolas_ERR_STATE_ERROR;` ← BUG） |
| **影响范围** | 若初始化线程长时间阻塞，state 永久为 2，运行时永久不可用 |
| **出处报告** | Agent 3 V3.0-N2 |
| **工作量估算** | ~0.5h（2 处 CAS 2→0 重置 + 竞争分析） |

#### v3.0-综合-P1-15：agent_registry_core_search 同模式数据竞争（v2.0 延期项 #2）

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | `agent_registry_core_search` 仍返回 `const agent_entry_t **out_entries` 指向内部 entries[]，与 P0-7 修正的 4 个函数同模式数据竞争，但 v2.0 未修正 |
| **证据位置** | `agentrt/daemons/market_d/src/agent_registry_core.c:239-254` |
| **影响范围** | 锁外访问内部数据，多线程场景存在数据竞争 |
| **出处报告** | Agent 3 §3.1 延期项 #2 |
| **工作量估算** | ~0.5h（改为 copy-to-buffer，参照 P0-7 修正模式） |

#### v3.0-综合-P2-6：agent_registry_search 嵌套加锁（依赖递归互斥锁）

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | `agent_registry_search()` 在持有 `g_registry.lock` 的情况下调用 `agent_registry_get()`，后者再次尝试获取同一锁。当前依赖 `PTHREAD_MUTEX_RECURSIVE` 可工作，但若未来改为非递归锁将立即死锁 |
| **证据位置** | `agentrt/daemons/market_d/src/agent_registry.c:204`（lock）/ `:235`（调用 `agent_registry_get` 内部再次 lock） |
| **出处报告** | Agent 3 V3.0-P2-1 |
| **工作量估算** | ~1h（抽取 `agent_registry_get_locked()` 不加锁版本） |

---

### 3.6 源码工程标准违规（P0-2 延期）

#### v3.0-综合-P1-16：P0-2 源码工程标准全量违规（规模增长）

| 属性 | 内容 |
|------|------|
| **严重度** | P1（v2.0 延期 P0，按工作量降级为 M1 阶段处理） |
| **问题摘要** | agentrt 源码全量违反 OLK-6.6 六大支柱，且违规规模较 v1.0 持续增长：4 空格缩进 10847→12535+ / typedef struct 540→597 / fprintf 159→174 / ASCII 装饰分节符 354 处/100 文件 |
| **证据位置** | Grep 实测: 4 空格缩进 12535+ 处/100 文件（截断）/ typedef struct 597 处/100+ 文件 / fprintf 174 处/22 文件 / 装饰分节符 354 处/100 文件；合规标杆: Tab 8 缩进仅 111 处/7 文件（[SC] 6 头文件 + 1 测试） |
| **影响范围** | 源码风格与 [SC] 6 头文件标杆（Tab 8 + struct 无 typedef + kernel-doc）严重背离；v1.0→v3.0 期间新增代码未遵循 OLK-6.6 标准，P0-2 债务持续累积 |
| **出处报告** | Agent 3 §5 + 延期项 #1 |
| **工作量估算** | ~46h（4 阶段分批：Tab 8 ~8h + typedef ~16h + goto ~12h + 装饰符/fprintf ~10h）；0.1.1 内可完成 ~30-35h |

#### v3.0-综合-P2-7：agent_registry_core_* 系列函数为 dead code

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | `agent_registry.c` 包装层 0 处调用 `_core` 函数，`_core` 系列为 dead code |
| **证据位置** | Grep 确认 `agent_registry.c` 0 处调用 `_core` 函数 |
| **出处报告** | Agent 3 延期项 #3 |
| **工作量估算** | ~2h（删除 `_core` 系列函数 + 头文件声明，或标记 `__attribute__((deprecated))`） |

#### v3.0-综合-P2-8：test_agent_registry_core.c 调用无 _core 后缀函数名

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | 测试文件调用 `agent_registry_get`/`list`/`search_by_tag` 等（无 `_core` 后缀），而非 `_core` 版本 |
| **证据位置** | `agentrt/daemons/market_d/tests/test_agent_registry_core.c:82,122,153,181,205,276` |
| **出处报告** | Agent 3 延期项 #4 |
| **工作量估算** | ~0.5h（修正测试调用或删除测试） |

#### v3.0-综合-P2-9：.bak 备份文件 agentrt_ 残留（42→43）

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | `triple_coordinator.c.bak` 中 `agentrt_` 前缀残留数量从 v2.0 的 42 处增至 43 处 |
| **证据位置** | `agentrt/atoms/coreloopthree/src/cognition/critique/triple_coordinator.c.bak`（Grep `agentrt_` = 43 处） |
| **出处报告** | Agent 3 V3.0-P2-3 + 延期项 #5 + Agent 4 P2-v3-3 |
| **工作量估算** | ~0.1h（`rm` 删除，git history 已保留） |

---

### 3.7 源码 v2.0 修正副作用

#### v3.0-综合-P1-17：N5 修正不完整——5 个其他 daemon 存在相同 goto-less 模式

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | v2.0 N5 修正仅修复 `sched_d/src/main.c` 的 4 处重复错误清理块，相同 goto-less 模式存在于 5 个其他 daemon，共 19 处 `return 1` 重复清理代码 |
| **证据位置** | `agentrt/daemons/market_d/src/main.c:341-399`（4 处）/ `agentrt/daemons/llm_d/src/main.c:500-563`（4 处）/ `agentrt/daemons/tool_d/src/main.c:377-435`（4 处）/ `agentrt/daemons/monit_d/src/main.c:430-504`（4 处）/ `agentrt/daemons/channel_d/src/main.c:312-330`（3 处） |
| **影响范围** | 违反 OS-KER-001 goto 集中出口要求，维护时极易遗漏新增资源的清理 |
| **出处报告** | Agent 3 V3.0-N3 |
| **工作量估算** | ~5h（5 个 daemon 各 ~1h） |

#### v3.0-综合-P1-18：N6 修正不完整——sync_compat.h 修正被 platform.h 屏蔽

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | N6 修正将 `sync_compat.h` 的 25 个同步原语返回类型改为 `airy_err_t`，但该修正被 `#ifndef AIRY_RT_PLATFORM_H` 条件编译块包裹。生产代码普遍包含 platform.h（经 airy_rt.h），sync_compat.h 修正被完全跳过，实际使用 platform.c 实现（返回原始 POSIX errno 正值），N6 修正对大多数调用方无效 |
| **证据位置** | `agentrt/commons/utils/sync/include/sync_compat.h:32`（`#ifndef AIRY_RT_PLATFORM_H`）/ `agentrt/commons/platform/platform.c:194-202`（`airy_mtx_init` 返回原始 POSIX errno）/ `:316-331`（`airy_cond_timedwait` 超时返回 -8，其他返回正值，语义不一致）；验证: 生产代码（taskflow_core.c:769 / pregel_engine.c:1069 / ipc_common.c:1637 / engine.c:892）均通过 platform.h 路径调用 |
| **影响范围** | N6 修正目标（错误码透明化）对大多数调用方未达成；生产代码仍无法区分 EINVAL/EBUSY/EDEADLK 等具体失败原因 |
| **出处报告** | Agent 3 V3.0-N4 |
| **工作量估算** | ~3h（platform.c 25 个函数修正 + 调用方审查） |

---

### 3.8 术语一致性

#### v3.0-综合-P1-19：Cupolas 子系统数量不一致（4 vs 7）

| 属性 | 内容 |
|------|------|
| **严重度** | P1 |
| **问题摘要** | `04-mainpage.dox` 将 Cupolas 描述为"四重纵深防护"仅列 4 子系统，但权威定义为 7 子系统。"四重防护"本指 4 阶段防护链，与"七大子系统"是不同维度概念，但 `04-mainpage.dox` 的子系统表仅列 4 项，与权威 7 子系统清单不一致 |
| **证据位置** | 权威（7 子系统）: `docs/AirymaxRT/TERMINOLOGY.md:193` + `01-design-philosophy.md:61` + `00-architectural-principles.md:310,749,893`；不一致（4 子系统）: `docs/AirymaxRT/30-interfaces/04-mainpage.dox:42-49`（仅列 Workbench/Permission/Sanitizer/Audit，缺失 Guards/Security Vault/Network Security）/ `:114`（"四重纵深防护"） |
| **影响范围** | Doxygen 主页生成的文档与权威术语表矛盾；外部开发者对 Cupolas 子系统数量产生混淆 |
| **出处报告** | Agent 1 v3.0-P1-3 |
| **工作量估算** | ~0.5h（补全为 7 子系统 + 区分"四重防护链"与"七大子系统"两个概念） |

#### v3.0-综合-P2-10：mainpage.dox 使用 agentrt_ 废弃前缀

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | Doxygen 文档示例使用 `agentrt_error_t` 和 `agentrt_error_get_message()`，违反 SSoT 函数前缀规则 |
| **证据位置** | `agentrt/cupolas/src/mainpage.dox:110,113` |
| **出处报告** | Agent 4 P2-v3-4 |
| **工作量估算** | ~0.1h |

---

### 3.9 文档工程规范盲区

#### v3.0-综合-P2-11：README.md 版本号不一致

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | `docs-closed/agentrt/README.md` 自身版本号不一致，line 7 与 line 96 给出不同版本 |
| **证据位置** | `docs-closed/agentrt/README.md:7`（"版本: 0.1.1"）/ `:96`（"文档版本: v1.0"） |
| **出处报告** | Agent 2 P1-V3-6 |
| **工作量估算** | ~0.1h |

#### v3.0-综合-P2-12：闭源手册 agentos.yaml 配置文件名残留

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | 闭源手册 line 3371 使用 `agentos.yaml` 配置文件名，与 §11.6.1 L3 运行时路径改名（`/etc/agentos` → `/etc/agentrt`）矛盾 |
| **证据位置** | `docs-closed/agentrt/agentrt工程标准规范手册.md:3371` |
| **出处报告** | Agent 2 P2-V3-1 |
| **工作量估算** | ~0.1h（`agentos.yaml` → `agentrt.yaml`） |

#### v3.0-综合-P2-13：闭源手册 AgentOS 历史名称残留（多处）

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | 闭源手册正文广泛使用 `AgentOS` 历史名称，§11.8 标注"v24.1 已完成 AgentOS→AgentRT 改名"，但正文仍用 `AgentOS`。部分为历史变动说明（保留合理），部分为正文当前描述（应修正） |
| **证据位置** | `docs-closed/agentrt/agentrt工程标准规范手册.md:28,133,179,339,347,365,381,383,694,1068,1261,1263,1415,1466,1472,1493,1495,1500,1736,1738,2524` 等 |
| **出处报告** | Agent 2 P2-V3-2 |
| **工作量估算** | ~1h（逐项核对，区分历史记录 vs 当前描述） |

#### v3.0-综合-P2-14：05-tech-reference-and-improvement/ 历史归档 1738 处 agentos_ 残留

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | `05-tech-reference-and-improvement/` 下 5 个历史归档文档共 1738 处 `agentos_` 残留。修改会破坏历史记录完整性 |
| **证据位置** | `historical-prototypes/AgentOS原型文档.md`（1335 处）/ `analysis-reports/第01版-AgentOS下一步改进建议.md`（155 处）/ `analysis-reports/第01版-AgentOS双思维模型详细落地方案.md`（151 处）/ `analysis-reports/第02版-AgentOS技术改进策略和详细方案.md`（75 处）/ `core-module-designs/CoreLoopThree具体实现方案01.md`（22 处） |
| **出处报告** | Agent 2 P2-V3-3 |
| **工作量估算** | ~0.2h（仅添加归档说明，不修正内容） |

---

### 3.10 其他遗留项

#### v3.0-综合-P2-15：闭源手册 29→38 仓变更说明残留

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | line 9（v26.0 历史 29 仓明细）与 line 4-5（v28.0 当前 38 仓明细）并列出现，读者易混淆。line 19 已明示"29 仓 → 38 仓（+9）"变更，但 line 9 未添加"已迁移"标注 |
| **证据位置** | `docs-closed/agentrt/agentrt工程标准规范手册.md:9`（v26.0 历史 29 仓）/ `:4-5`（v28.0 当前 38 仓）/ `:19`（v27.0 变动说明） |
| **出处报告** | Agent 2 P1-DQC-4 |
| **工作量估算** | ~0.2h（line 9 末尾添加历史标注） |

#### v3.0-综合-P2-16：闭源手册 daemon 数量 16 vs 12

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | line 40 的"16 个 daemon"是 v0.1.0 时代残留，与 line 3377/4173/4364/4383 的"12 个 daemon"形成内部矛盾，与开源 SSoT（12 个）不一致 |
| **证据位置** | `docs-closed/agentrt/agentrt工程标准规范手册.md:40`（"16 个 daemon"）/ `:3377,4173,4364,4383`（"12 个 daemon"）；开源 SSoT: `docs/AirymaxRT/10-architecture/01-system-architecture.md:305`（"12 个核心用户态服务"） |
| **出处报告** | Agent 2 P2-DQC-4 |
| **工作量估算** | ~0.1h（line 40 "16 个 daemon" → "12 个 daemon"） |

#### v3.0-综合-P2-17：docs/AirymaxOS/TERMINOLOGY.md 不存在

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | 已知 P2-DQC-5 遗留问题，v2.0 未修复。该文件被多处引用但不存在 |
| **证据位置** | `Glob docs/AirymaxOS/TERMINOLOGY.md` → No file found |
| **出处报告** | Agent 4 P2-v3-2 |
| **工作量估算** | ~0.1h（评估是否创建或修正引用；注意此为 agent-linux 范围，按约束不处理，仅标注） |

#### v3.0-综合-P2-18：error.h 路线图注释与验证报告不一致

| 属性 | 内容 |
|------|------|
| **严重度** | P2 |
| **问题摘要** | error.h L66 注释称"计划 0.1.2 消除"，但 v2.0 验证报告称"留待 1.0.1 M1 阶段对齐"。目标版本不一致 |
| **证据位置** | `agentrt/commons/utils/error/include/error.h:66`（"计划 0.1.2 消除"）；v2.0 验证报告 §9.1 延期项 #6（"留待 1.0.1 M1 阶段对齐"） |
| **出处报告** | Agent 3 V3.0-P2-2 |
| **工作量估算** | ~0.1h（统一路线图为 1.0.1 M1） |

---

### 3.11 去重归类汇总

| 主题 | P0 | P1 | P2 | 小计 |
|------|----|----|----|----|
| 3.1 错误码 SSoT 系统性崩溃 | 5 | 3 | 0 | 8 |
| 3.2 IPC 消息头 SSoT 对齐 | 2 | 0 | 0 | 2 |
| 3.3 函数前缀与改名规范违反 SSoT | 3 | 2 | 0 | 5 |
| 3.4 路径引用断链 | 0 | 7 | 5 | 12 |
| 3.5 源码并发安全（DCLP 状态机） | 0 | 3 | 1 | 4 |
| 3.6 源码工程标准违规（P0-2 延期） | 0 | 1 | 3 | 4 |
| 3.7 源码 v2.0 修正副作用 | 0 | 2 | 0 | 2 |
| 3.8 术语一致性 | 0 | 1 | 1 | 2 |
| 3.9 文档工程规范盲区 | 0 | 0 | 4 | 4 |
| 3.10 其他遗留项 | 0 | 0 | 4 | 4 |
| **合计** | **10** | **19** | **18** | **47** |

---

## 4. 系统性修正路线图

### 4.1 工作流 A：错误码 SSoT 统一收敛（最优先）

| 属性 | 内容 |
|------|------|
| **涉及问题** | v3.0-综合-P0-1 / P0-2 / P0-3 / P0-4 / P0-5 / P1-1 / P1-2 / P1-3 |
| **优先级** | **必须在 M1 启动前完成** |
| **工作量估算** | ~24h |

**修正步骤（按依赖顺序）**：

1. **确定唯一权威方案**（~2h）：选定方案 A（POSIX errno 负值），在 `120-cross-project-code-sharing.md` 中明确声明为唯一 SSoT，废弃方案 B/C/D
2. **创建/修正权威源路径**（~1h）：创建 `include/airymax/error.h` symlink 指向 `agentrt/commons/utils/error/include/error.h`，或修正所有 4+ 处文档引用路径
3. **修正 airy_err_t 定位声明**（~1h）：修正 `120-cross-project-code-sharing.md:73` 和 `06-iron9-shared-model.md:70`，将 `airy_err_t` 定位改为 `airy_types.h`（或迁移定义到 `cognition_types.h`）
4. **源码错误码值对齐**（~8h）：将 `airy_types.h:50-55` 的 `AIRY_EINVAL`/`AIRY_ENOMEM`/`AIRY_ETIMEDOUT` 改为 POSIX errno 负值（-22/-12/-110），全量审查 30 个码 + 调用方
5. **消除 error.h 内部冲突**（~2h）：消除 `AIRY_ERR_UNKNOWN=-1` 与 `AIRY_EINVAL=-1` 同值冲突；修正 `#undef AIRY_EPERM` 重定义
6. **移除 AIRY_OK**（~1h）：移除 `error.h:43` 的 `AIRY_OK` 定义，替换 `:668,681` 调用方为 `AIRY_EOK`
7. **闭源手册对齐**（~2.5h）：6 处 `airy_error_t` → `airy_err_t`（P0-5）+ §34.5 补 i18n/发行版分段 + 修正权威源路径（P1-3）
8. **验证**：Grep `airy_error_t` in 闭源手册 = 0；Grep `AIRY_OK` in error.h = 0；Grep `AIRY_EINVAL` in airy_types.h = `(-22)`

**涉及文件清单**：
- `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md`
- `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md`
- `docs/AirymaxOS/50-engineering-standards/10-coding-style/coding_conventions.md`
- `docs/AirymaxOS/50-engineering-standards/30-runtime-interfaces/runtime_interfaces.md`
- `docs/AirymaxOS/50-engineering-standards/50-project-erp/project_erp.md`
- `docs/AirymaxRT/10-architecture/00-architectural-principles.md`
- `docs/AirymaxRT/10-architecture/06-iron9-shared-model.md`
- `docs/AirymaxRT/TERMINOLOGY.md`
- `docs/AirymaxRT/20-modules/10-contracts/03-protocol-contract.md`
- `docs-closed/agentrt/agentrt工程标准规范手册.md`
- `agentrt/commons/include/airy_types.h`
- `agentrt/commons/utils/error/include/error.h`

**验证方法**：
```bash
# P0-1: SSoT 方案唯一性
Grep "AIRY_EINVAL.*-1[^0-9]" docs/AirymaxOS/50-engineering-standards/ → 期望 0（方案 B/C 废弃）
# P0-2: 源码值对齐
Grep "AIRY_EINVAL" agentrt/commons/include/airy_types.h → 期望 (-22)
# P0-3: airy_err_t 定位
Grep "airy_err_t" agentrt/commons/include/airymax/cognition_types.h → 期望有匹配（若迁移）或文档声明已修正
# P0-4: 权威源存在
Glob include/airymax/error.h → 期望文件存在
# P0-5: 闭源手册类型名
Grep "airy_error_t" docs-closed/agentrt/agentrt工程标准规范手册.md → 期望 0
# P1-2: AIRY_OK 清除
Grep "AIRY_OK" agentrt/commons/utils/error/include/error.h → 期望 0
```

---

### 4.2 工作流 B：IPC 消息头 SSoT 对齐

| 属性 | 内容 |
|------|------|
| **涉及问题** | v3.0-综合-P0-6 / P0-7 |
| **优先级** | **必须在 M1 启动前完成** |
| **工作量估算** | ~5h |

**修正步骤**：

1. **02-l2-service-protocol.md 对齐 SSoT**（~3h）：
   - 结构体名 `are_ipc_message_header_t` → `struct airy_ipc_msg_hdr`（无 typedef）
   - 类型 `uint32_t/uint16_t/uint64_t` → `__u32/__u16/__u64/__u8`（UAPI）
   - 添加 `__attribute__((packed))`
   - 字段布局对齐 SSoT 8 字段（magic/opcode/flags/trace_id/timestamp_ns/src_task/dst_task/payload_len/reserved[84]）
   - 添加真实 `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128)`
   - 宏 `ARE_IPC_MAGIC` → `AIRY_IPC_MAGIC`
   - 在迁移说明中保留旧字段对应关系表
   - 评估 L2 协议是否需要独立于 [SC] SSoT 的消息头（若需要，使用不同 magic 值；若不需要，直接复用）

2. **闭源手册 §34.2 全节重写**（~2h）：
   - 对齐开源 SSoT `struct airy_ipc_msg_hdr`
   - 移除所有 `are_ipc_message_header_t` 引用（L2901/3330/3334/3349/3353）
   - 修正 `AIRY_ERR_PROTOCOL` 引用为当前错误码命名

**涉及文件清单**：
- `docs/AirymaxRT/30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md`
- `docs-closed/agentrt/agentrt工程标准规范手册.md`

**验证方法**：
```bash
# P0-6: 02-l2 对齐
Grep "are_ipc_message_header" docs/AirymaxRT/30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md → 期望仅迁移说明中保留
Grep "ARE_IPC_MAGIC" docs/AirymaxRT/ → 期望 0
Grep "struct airy_ipc_msg_hdr" docs/AirymaxRT/30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md → 期望有匹配
# P0-7: 闭源手册 §34.2 对齐
Grep "are_ipc_message_header" docs-closed/agentrt/agentrt工程标准规范手册.md → 期望 0（或仅迁移说明）
```

---

### 4.3 工作流 C：函数前缀与 §11.6 重写

| 属性 | 内容 |
|------|------|
| **涉及问题** | v3.0-综合-P0-8 / P0-9 / P0-10 / P1-4 / P1-5 |
| **优先级** | **必须在 M1 启动前完成** |
| **工作量估算** | ~9.6h |

**修正步骤**：

1. **07-subsystem-specs/ 10 文件全量替换**（~6h）：
   - `agentos_` → `airy_`、`AGENTOS_` → `AIRY_`
   - **关键**：逐项核对类型名（`agentos_error_t` → `airy_err_t` 而非 `airy_error_t`、`agentos_arena_t` → `airy_arena_t` 等）
   - 参照已修正的 `02-corekern.md` 作为标杆

2. **06-contracts/ 3 文件全量替换**（~1h）：
   - 含指标前缀 `agentos_requests_total` → `airy_requests_total` 等
   - `#define CONTRACT_AC_METRIC_PREFIX "agentos_"` → `"airy_"`

3. **§11.6 添加历史决策声明**（~0.5h）：
   - 在 §11.6 标题下方添加显著声明："历史决策记录（未执行），实际源码保留 `airy_*`/`AIRY_*` 前缀，当前前缀规范以 §1.6 术语表为准"
   - 保留 §11.6 作为 v26.0 历史决策记录，不删除（BAN-341~BAN-344 仍被其他章节引用）

4. **line 4175 修正**（~0.1h）：`agentrt_ 前缀` → `airy_ 前缀`

5. **SSoT §4.4.2 重写**（~2h）：消除 L2606 vs L2607 矛盾，与 `06-iron9 §3.12` 对齐

**涉及文件清单**：
- `docs-closed/agentrt/07-subsystem-specs/01-checkpoint.md`
- `docs-closed/agentrt/07-subsystem-specs/03-coreloopthree.md`
- `docs-closed/agentrt/07-subsystem-specs/04-cupolas.md`
- `docs-closed/agentrt/07-subsystem-specs/05-gateway-d.md`
- `docs-closed/agentrt/07-subsystem-specs/06-llm-d.md`
- `docs-closed/agentrt/07-subsystem-specs/07-manager.md`
- `docs-closed/agentrt/07-subsystem-specs/08-market-d.md`
- `docs-closed/agentrt/07-subsystem-specs/09-memory.md`
- `docs-closed/agentrt/07-subsystem-specs/11-orchestrator.md`
- `docs-closed/agentrt/07-subsystem-specs/12-tool-d.md`
- `docs-closed/agentrt/06-contracts/contract_A_B.h`
- `docs-closed/agentrt/06-contracts/contract_A_C.h`
- `docs-closed/agentrt/06-contracts/contract_test.c`
- `docs-closed/agentrt/agentrt工程标准规范手册.md`
- `docs/AirymaxOS/50-engineering-standards/10-coding-style/coding_conventions.md`

**验证方法**：
```bash
# P0-8: 07-subsystem-specs/ 残留清零
Grep -c "agentos_" docs-closed/agentrt/07-subsystem-specs/ → 期望 0（10 文件全部清零）
# P0-9: 06-contracts/ 残留清零
Grep -c "agentos_" docs-closed/agentrt/06-contracts/ → 期望 0
# P0-10: §11.6 历史声明存在
Grep "历史决策记录" docs-closed/agentrt/agentrt工程标准规范手册.md → 期望有匹配
# P1-4: line 4175 修正
Grep "agentrt_ 前缀" docs-closed/agentrt/agentrt工程标准规范手册.md → 期望 0
```

---

### 4.4 工作流 D：路径引用与术语统一

| 属性 | 内容 |
|------|------|
| **涉及问题** | v3.0-综合-P1-6 / P1-7 / P1-8 / P1-9 / P1-10 / P1-11 / P1-12 / P1-19 / P2-1 / P2-2 / P2-3 / P2-4 / P2-5 / P2-10 |
| **优先级** | M1 早期 |
| **工作量估算** | ~8.6h |

**修正步骤**：

1. **agentrt/daemon/ → agentrt/daemons/ 全量替换**（~1.5h，P1-6）：44 处/16 文件，三步替换法
2. **L1/L2/L3 cross-reference 文件名修正**（~0.3h，P1-7）：15 处/4 文件
3. **AgentRT/ → agentrt/ 大小写修正**（~2h，P1-8）：60 处/24 文件，区分品牌名用法 vs 路径引用
4. **docs/AirymaxAgentOS/ → docs/AirymaxOS/**（~0.3h，P1-9）：7 处
5. **agentos/ 目录路径 → agentrt/**（~3h，P1-10）：60+ 处，逐项核对区分目录路径 vs 历史记录
6. **02-logging.md 双重路径修正**（~0.2h，P1-11）
7. **error_code_reference.md → project_erp.md**（~0.1h，P1-12）
8. **Cupolas 子系统补全**（~0.5h，P1-19）：`04-mainpage.dox` 补全为 7 子系统
9. **P2 路径修正集合**（~0.65h，P2-1~5 + P2-10）：doxygen-guide / naming_conventions / 0.1.1任务清单 / TERMINOLOGY path / Docs case / mainpage.dox

**涉及文件清单**：
- `docs/AirymaxRT/` 下 24+ 文件（路径修正）
- `docs/AirymaxRT/30-interfaces/04-mainpage.dox`（Cupolas 补全）
- `docs-closed/agentrt/agentrt工程标准规范手册.md`（agentos/ 路径 + AirymaxAgentOS/）
- `agentrt/cupolas/src/mainpage.dox`（agentrt_ 前缀）

**验证方法**：
```bash
# P1-6: daemon/daemons
Grep "agentrt/daemon/" docs/AirymaxRT/ → 期望 0
# P1-8: AgentRT/ 大写
Grep "AgentRT/" docs/AirymaxRT/ → 期望仅品牌名合法用法
# P1-9: AirymaxAgentOS/
Grep "AirymaxAgentOS" docs-closed/agentrt/agentrt工程标准规范手册.md → 期望 0
# P1-10: agentos/ 目录
Grep "agentos/" docs-closed/agentrt/agentrt工程标准规范手册.md → 期望仅历史记录保留
```

---

### 4.5 工作流 E：源码并发安全修复（DCLP）

| 属性 | 内容 |
|------|------|
| **涉及问题** | v3.0-综合-P1-13 / P1-14 / P1-15 / P2-6 |
| **优先级** | **必须在 M1 启动前完成**（P1-13/P1-14 为并发安全真实风险） |
| **工作量估算** | ~3h |

**修正步骤**：

1. **DCLP 自旋等待失败后验证 state == 1**（~1h，P1-13）：
   - `core_init.c:64` 后增加 `if (atomic_load_explicit(&g_core_initialized, memory_order_acquire) != 1) return AIRY_ERR_NOTINIT;`
   - `cupolas.c:112` 前增加 `if (cupolas_atomic_load32(&g_cupolas_init_state) != 1) return cupolas_ERR_STATE_ERROR;`

2. **DCLP 超时后 CAS 2→0 重置状态**（~0.5h，P1-14）：
   - `core_init.c:59-63` 超时分支增加 `atomic_compare_exchange_strong_explicit(&g_core_initialized, &expected_state, 0, ...)`
   - `cupolas.c:104-110` 同理

3. **agent_registry_core_search 改为 copy-to-buffer**（~0.5h，P1-15）：参照 P0-7 修正模式

4. **agent_registry_search 嵌套加锁消除**（~1h，P2-6）：抽取 `agent_registry_get_locked()` 不加锁版本

**涉及文件清单**：
- `agentrt/atoms/corekern/src/core_init.c`
- `agentrt/cupolas/src/cupolas.c`
- `agentrt/daemons/market_d/src/agent_registry_core.c`
- `agentrt/daemons/market_d/src/agent_registry.c`

**验证方法**：
```bash
# P1-13: state 验证存在
Grep "AIRY_ERR_NOTINIT\|state.*!= 1" agentrt/atoms/corekern/src/core_init.c → 期望有匹配
# P1-14: CAS 2→0 重置存在
Grep "compare_exchange.*expected_state.*2.*0" agentrt/atoms/corekern/src/core_init.c → 期望有匹配
```

---

### 4.6 工作流 F：源码工程标准分批处理（P0-2）

| 属性 | 内容 |
|------|------|
| **涉及问题** | v3.0-综合-P1-16 / P1-17 / P1-18 / P2-7 / P2-8 / P2-9 |
| **优先级** | M1 全阶段（渐进式） |
| **工作量估算** | ~56.6h（0.1.1 内可完成 ~40-46h） |

**修正步骤（4 阶段分批）**：

1. **阶段 1：Tab 8 自动化**（~8h，M1 早期）：
   - 配置 `.clang-format`（`IndentWidth: 8` / `TabWidth: 8` / `UseTab: Always` / `ColumnLimit: 80`）
   - 添加 `make format` 目标 + CI 门禁
   - 分模块执行：commons/ → atoms/ → daemons/ → cupolas/ → gateway/ → protocols/
   - 出口标准：4 空格缩进从 12535+ 降至 <500

2. **阶段 2：typedef 重构**（~16h，M1 中期）：
   - 将 597 处 `typedef struct { ... } xxx_t;` 重构为 `struct xxx { ... };`
   - 保留不透明指针 typedef + [SC] 头文件
   - 出口标准：typedef struct 从 597 降至 <200

3. **阶段 3：goto 集中出口**（~12h，M1 中后期）：
   - 优先处理 V3.0-N3 的 5 个 daemon main.c（~5h，P1-17）
   - 扫描其他多资源函数
   - 出口标准：V3.0-N3 的 5 个 daemon 全部修正 + 全仓库 goto 标签 ≥50

4. **阶段 4：装饰分节符 + fprintf 收口**（~10h，M1 后期）：
   - 移除 354 处 ASCII 装饰分节符
   - fprintf 收口到 `log_write` 或标注 BAN-70 EXEMPT
   - 出口标准：装饰分节符 <50；fprintf <60

5. **N6 修正完善**（~3h，P1-18）：将 `airy_sync_map_err` 映射逻辑移植到 `platform.c` 的 25 个同步原语

6. **dead code 清理 + 测试修正 + .bak 删除**（~2.6h，P2-7/8/9）

**涉及文件清单**：
- `agentrt/` 全部 833 源文件（阶段 1-4 渐进）
- `agentrt/daemons/{market_d,llm_d,tool_d,monit_d,channel_d}/src/main.c`（P1-17）
- `agentrt/commons/platform/platform.c`（P1-18）
- `agentrt/daemons/market_d/src/agent_registry_core.c` + `tests/test_agent_registry_core.c`（P2-7/8）
- `agentrt/atoms/coreloopthree/src/cognition/critique/triple_coordinator.c.bak`（P2-9）

**验证方法**：
```bash
# 阶段 1: Tab 8 达标
Grep "^    [a-zA-Z_]" agentrt/ --glob "*.{c,h}" → 期望 <500
# 阶段 2: typedef 削减
Grep "typedef\s+struct" agentrt/ --glob "*.{c,h}" → 期望 <200
# P1-17: 5 daemon goto
Grep "goto out_" agentrt/daemons/{market_d,llm_d,tool_d,monit_d,channel_d}/src/main.c → 期望有匹配
# P2-9: .bak 删除
Glob agentrt/atoms/coreloopthree/src/cognition/critique/*.bak → 期望 No file found
```

---

### 4.7 工作流 G：文档工程规范盲区修正

| 属性 | 内容 |
|------|------|
| **涉及问题** | v3.0-综合-P2-11 / P2-12 / P2-13 / P2-14 |
| **优先级** | M1 早期 |
| **工作量估算** | ~1.4h |

**修正步骤**：

1. **README.md 版本号统一**（~0.1h，P2-11）：line 7 与 line 96 统一
2. **agentos.yaml → agentrt.yaml**（~0.1h，P2-12）：line 3371
3. **AgentOS 历史名称逐项核对**（~1h，P2-13）：区分历史记录 vs 当前描述
4. **05-tech-reference 添加归档说明**（~0.2h，P2-14）：不修正内容，仅添加标注

**涉及文件清单**：
- `docs-closed/agentrt/README.md`
- `docs-closed/agentrt/agentrt工程标准规范手册.md`
- `docs-closed/agentrt/05-tech-reference-and-improvement/README.md`（或目录说明）

**验证方法**：
```bash
# P2-11: 版本号一致
Grep "版本" docs-closed/agentrt/README.md → 期望统一
# P2-12: agentos.yaml 清零
Grep "agentos.yaml" docs-closed/agentrt/agentrt工程标准规范手册.md → 期望 0
```

---

### 4.8 工作流 H：遗留项清理

| 属性 | 内容 |
|------|------|
| **涉及问题** | v3.0-综合-P2-15 / P2-16 / P2-17 / P2-18 |
| **优先级** | M1 早期 |
| **工作量估算** | ~0.5h |

**修正步骤**：

1. **29→38 仓变更标注**（~0.2h，P2-15）：line 9 末尾添加"（注：v27.0 已迁移至 38 仓，详见 line 19）"
2. **daemon 16→12 修正**（~0.1h，P2-16）：line 40 "16 个 daemon" → "12 个 daemon"
3. **TERMINOLOGY.md 标注**（~0.1h，P2-17）：评估是否创建或修正引用（agent-linux 范围，仅标注）
4. **error.h 路线图注释统一**（~0.1h，P2-18）：统一为 1.0.1 M1

**涉及文件清单**：
- `docs-closed/agentrt/agentrt工程标准规范手册.md`
- `agentrt/commons/utils/error/include/error.h`

**验证方法**：
```bash
# P2-16: daemon 数量一致
Grep "16 个 daemon" docs-closed/agentrt/agentrt工程标准规范手册.md → 期望 0
# P2-18: 路线图统一
Grep "0.1.2" agentrt/commons/utils/error/include/error.h → 期望 0（或改为 1.0.1 M1）
```

---

### 4.9 工作流汇总

| 工作流 | 涉及问题数 | 工作量 | 优先级 | 0.1.1 可完成 |
|--------|----------|--------|--------|-------------|
| A：错误码 SSoT 统一收敛 | 8 | ~24h | **M1 启动前** | ✅ |
| B：IPC 消息头 SSoT 对齐 | 2 | ~5h | **M1 启动前** | ✅ |
| C：函数前缀与 §11.6 重写 | 5 | ~9.6h | **M1 启动前** | ✅ |
| D：路径引用与术语统一 | 14 | ~8.6h | M1 早期 | ✅ |
| E：源码并发安全修复（DCLP） | 4 | ~3h | **M1 启动前** | ✅ |
| F：源码工程标准分批处理 | 6 | ~56.6h | M1 全阶段 | 部分（~40-46h） |
| G：文档工程规范盲区修正 | 4 | ~1.4h | M1 早期 | ✅ |
| H：遗留项清理 | 4 | ~0.5h | M1 早期 | ✅ |
| **合计** | **47** | **~108.7h** | — | ~88-94h |

---

## 5. 1.0.1 M1 就绪判定

### 5.1 判定条件矩阵

| # | 判定条件 | 当前状态 | 阻塞工作流 | 说明 |
|---|---------|---------|-----------|------|
| 1 | P0 阻断项清零 | ❌ 未通过（10 项 P0 残留） | A/B/C | 错误码 SSoT 5 项 + IPC 头 2 项 + 函数前缀 3 项 |
| 2 | 综合评分 ≥ 80/B | ❌ 未通过（当前 66/C+） | A/B/C/E/F | 需完成 A+B+C+E+部分 F |
| 3 | SSoT 收敛 | ❌ 未通过 | A | 错误码 5+ 套方案并行 + 权威源不存在 |
| 4 | IPC 消息头对齐 | ❌ 未通过 | B | 2 处三重违规残留 |
| 5 | 并发安全 | ❌ 未通过 | E | DCLP 假成功 + 状态卡死 |
| 6 | 工程标准规范 | ❌ 未通过 | F | P0-2 规模增长（12535+ 处 4 空格） |
| 7 | [SC] 6 头文件清单一致 | ✅ 通过 | — | v2.0 修正持久 |
| 8 | 跨平台一致性 | ⚠️ 边界 | — | 无新发现，维持 v2.0 状态 |

### 5.2 当前状态评估

> **agentrt 项目 v3.0 复审后不满足 1.0.1 M1 代码开发就绪条件**。
>
> 8 项判定条件中仅 1 项通过（[SC] 6 头文件清单一致），6 项未通过，1 项边界。核心阻塞项为错误码 SSoT 系统性崩溃（工作流 A）和 IPC 头 SSoT 对齐（工作流 B），这两项是恢复 SSoT 完整性的关键。

### 5.3 必须在 M1 启动前完成的阻塞项

按优先级排序（**M1 启动前必须完成**）：

| 优先级 | 工作流 | 工作量 | 阻塞原因 |
|--------|--------|--------|---------|
| 1 | **A：错误码 SSoT 统一收敛** | ~24h | SSoT 系统性崩溃，5+ 套方案并行，权威源不存在 |
| 2 | **B：IPC 消息头 SSoT 对齐** | ~5h | 2 处三重违规，破坏 [SC] 共享契约层 |
| 3 | **C：函数前缀与 §11.6 重写** | ~9.6h | 340 处 agentos_* 残留 + §11.6 违反 SSoT |
| 4 | **E：源码并发安全修复** | ~3h | DCLP 假成功 + 状态卡死，并发安全真实风险 |
| 5 | **G：文档工程规范盲区** | ~1.4h | 闭源手册版本/配置文件名不一致 |
| **合计** | A+B+C+E+G | **~43h** | — |

### 5.4 可以在 M1 阶段并行处理的项目

| 工作流 | 工作量 | M1 阶段 | 说明 |
|--------|--------|--------|------|
| D：路径引用与术语统一 | ~8.6h | M1 早期 | 文档可用性问题，不影响架构正确性 |
| F：源码工程标准分批处理 | ~40-46h | M1 全阶段 | P0-2 渐进式重构，按 4 阶段分批 |
| H：遗留项清理 | ~0.5h | M1 早期 | P2 级遗留项 |

---

## 6. 修正后评分预估

### 6.1 三维度评分模型

| 评分维度 | 权重 | 当前 v3.0 | 说明 |
|---------|------|----------|------|
| 规范声明层 | 35% | ~60/C | SSoT 错误码崩溃 + §11.6 违反 SSoT + 路径断链 |
| 方案设计层 | 40% | ~70/B- | 架构设计完整，但 IPC/SSoT 存在系统性问题 |
| 实现落地层 | 25% | ~68/C+ | 源码 DCLP 缺陷 + P0-2 规模增长 |
| **加权综合** | 100% | **~66/C+** | 60×0.35 + 70×0.40 + 68×0.25 = 21 + 28 + 17 = 66 |

### 6.2 评分恢复路径

| 修正阶段 | 规范声明层 | 方案设计层 | 实现落地层 | 加权综合 | 级别 |
|---------|----------|----------|----------|---------|------|
| 当前 v3.0 | 60/C | 70/B- | 68/C+ | **66** | C+ |
| 完成 A+B+C+G（M1 启动前） | 78/B+ | 78/B+ | 68/C+ | **76** | B |
| 完成 A+B+C+D+E+G（+D+E） | 80/B+ | 80/B+ | 74/B- | **78** | B |
| 完成全部 A-H（+F+H） | 85/B+ | 82/B+ | 85/B+ | **84** | B+ |

### 6.3 80/B 阈值可达性分析

| 修正范围 | 预估评分 | 是否达 80/B | 说明 |
|---------|---------|------------|------|
| A+B+C+G（M1 启动前阻塞项） | ~76/B | ❌ 未达 | 实现落地层未改善（68/C+） |
| A+B+C+D+E+G（+路径+并发） | ~78/B | ❌ 未达 | 实现落地层仅部分改善（74/B-） |
| A-H 全部完成（含 P0-2） | ~84/B+ | ✅ 达标 | 三维度均达 B+ |

> **关键判定**：80/B 阈值**仅在完成工作流 F（P0-2 源码工程标准分批处理 ~40-46h）后方可达到**。仅完成 M1 启动前阻塞项（A+B+C+E+G，~43h）可达到 ~76/B，仍低于 80/B 阈值 4 分。
>
> **建议**：将 80/B 阈值调整为 M1 **出口条件**（而非启动条件），M1 启动条件设为 ≥75/B（即完成 A+B+C+E+G 后）。M1 阶段并行推进 F（P0-2），M1 出口时达到 ≥80/B。

---

## 7. 附录

### 7.1 v3.0 问题清单汇总表

| 编号 | 严重度 | 摘要 | 主题 | 出处 |
|------|--------|------|------|------|
| v3.0-综合-P0-1 | P0 | SSoT 5+ 套错误码方案并行 | 3.1 | Agent 4 P0-v3-1 |
| v3.0-综合-P0-2 | P0 | 源码错误码值与文档 SSoT 冲突 | 3.1 | Agent 4 P0-v3-2 + Agent 3 §3.2 |
| v3.0-综合-P0-3 | P0 | airy_err_t 定位声明错误 | 3.1 | Agent 4 P0-v3-3 + P1-v3-6 |
| v3.0-综合-P0-4 | P0 | include/airymax/error.h 不存在 | 3.1 | Agent 4 P0-v3-4 |
| v3.0-综合-P0-5 | P0 | 闭源手册 airy_error_t vs airy_err_t | 3.1 | Agent 2 P0-V3-4 |
| v3.0-综合-P0-6 | P0 | 02-l2-service-protocol.md IPC 头三重违规 | 3.2 | Agent 1 v3.0-P0-1 + Agent 4 P0-v3-5 |
| v3.0-综合-P0-7 | P0 | 闭源手册 §34.2 IPC 头三重违规 | 3.2 | Agent 2 P0-V3-3 + Agent 4 P0-v3-6 |
| v3.0-综合-P0-8 | P0 | 07-subsystem-specs/ 302 处 agentos_* | 3.3 | Agent 2 P0-V3-1 |
| v3.0-综合-P0-9 | P0 | 06-contracts/ 38 处 agentos_* | 3.3 | Agent 2 P0-V3-2 |
| v3.0-综合-P0-10 | P0 | §11.6 违反 SSoT 函数前缀规则 | 3.3 | Agent 2 P1-V3-4 + Agent 4 P0-v3-7 |
| v3.0-综合-P1-1 | P1 | error.h 内部语义重叠/同值冲突 | 3.1 | Agent 4 P1-v3-5 |
| v3.0-综合-P1-2 | P1 | 源码 error.h 仍使用 AIRY_OK | 3.1 | Agent 4 P1-v3-7 |
| v3.0-综合-P1-3 | P1 | 闭源手册 §34.5 错误码分段 9 vs 11 | 3.1 | Agent 2 P1-V3-3 |
| v3.0-综合-P1-4 | P1 | line 4175 agentrt_ 前缀矛盾 | 3.3 | Agent 2 P1-V3-5 |
| v3.0-综合-P1-5 | P1 | SSoT §4.4.2 函数前缀规则内部矛盾 | 3.3 | Agent 4 P1-v3-3 |
| v3.0-综合-P1-6 | P1 | agentrt/daemon/ vs daemons/ 44 处 | 3.4 | Agent 1 v3.0-P1-1 |
| v3.0-综合-P1-7 | P1 | L1/L2/L3 cross-reference 15 处 | 3.4 | Agent 1 v3.0-P1-2 |
| v3.0-综合-P1-8 | P1 | AgentRT/ 大写 60 处 | 3.4 | Agent 4 P1-v3-1 |
| v3.0-综合-P1-9 | P1 | docs/AirymaxAgentOS/ 7 处 | 3.4 | Agent 2 P1-V3-1 + Agent 4 P1-v3-2 |
| v3.0-综合-P1-10 | P1 | agentos/ 目录路径 60+ 处 | 3.4 | Agent 2 P1-V3-2 |
| v3.0-综合-P1-11 | P1 | 02-logging.md 双重路径 | 3.4 | Agent 1 v3.0-P1-4 |
| v3.0-综合-P1-12 | P1 | error_code_reference.md 断链 | 3.4 | Agent 1 v3.0-P1-5 |
| v3.0-综合-P1-13 | P1 | DCLP 失败后返回 SUCCESS | 3.5 | Agent 3 V3.0-N1 |
| v3.0-综合-P1-14 | P1 | DCLP 超时后状态卡死 | 3.5 | Agent 3 V3.0-N2 |
| v3.0-综合-P1-15 | P1 | agent_registry_core_search 数据竞争 | 3.5 | Agent 3 延期项 #2 |
| v3.0-综合-P1-16 | P1 | P0-2 源码工程标准全量违规 | 3.6 | Agent 3 §5 + 延期项 #1 |
| v3.0-综合-P1-17 | P1 | N5 修正不完整 5 daemon goto-less | 3.7 | Agent 3 V3.0-N3 |
| v3.0-综合-P1-18 | P1 | N6 修正被 platform.h 屏蔽 | 3.7 | Agent 3 V3.0-N4 |
| v3.0-综合-P1-19 | P1 | Cupolas 子系统数量 4 vs 7 | 3.8 | Agent 1 v3.0-P1-3 |
| v3.0-综合-P2-1 | P2 | doxygen-guide 路径错误 | 3.4 | Agent 1 v3.0-P2-1/2 |
| v3.0-综合-P2-2 | P2 | naming_conventions.md 断链 | 3.4 | Agent 1 v3.0-P2-3 |
| v3.0-综合-P2-3 | P2 | 0.1.1详细任务清单.md 断链 | 3.4 | Agent 1 v3.0-P2-4 + Agent 4 P2-v3-1 |
| v3.0-综合-P2-4 | P2 | TERMINOLOGY.md 路径头大小写 | 3.4 | Agent 1 v3.0-P2-5 |
| v3.0-综合-P2-5 | P2 | Docs/ 大小写 2 处 | 3.4 | Agent 1 v3.0-P2-6 |
| v3.0-综合-P2-6 | P2 | agent_registry_search 嵌套加锁 | 3.5 | Agent 3 V3.0-P2-1 |
| v3.0-综合-P2-7 | P2 | agent_registry_core_* dead code | 3.6 | Agent 3 延期项 #3 |
| v3.0-综合-P2-8 | P2 | test 调用无 _core 后缀 | 3.6 | Agent 3 延期项 #4 |
| v3.0-综合-P2-9 | P2 | .bak 文件 43 处 agentrt_ | 3.6 | Agent 3 V3.0-P2-3 + Agent 4 P2-v3-3 |
| v3.0-综合-P2-10 | P2 | mainpage.dox agentrt_ 废弃前缀 | 3.8 | Agent 4 P2-v3-4 |
| v3.0-综合-P2-11 | P2 | README.md 版本号不一致 | 3.9 | Agent 2 P1-V3-6 |
| v3.0-综合-P2-12 | P2 | agentos.yaml 配置文件名 | 3.9 | Agent 2 P2-V3-1 |
| v3.0-综合-P2-13 | P2 | AgentOS 历史名称残留 | 3.9 | Agent 2 P2-V3-2 |
| v3.0-综合-P2-14 | P2 | 05-tech-reference 归档 1738 处 | 3.9 | Agent 2 P2-V3-3 |
| v3.0-综合-P2-15 | P2 | 29→38 仓变更说明残留 | 3.10 | Agent 2 P1-DQC-4 |
| v3.0-综合-P2-16 | P2 | daemon 16 vs 12 | 3.10 | Agent 2 P2-DQC-4 |
| v3.0-综合-P2-17 | P2 | docs/AirymaxOS/TERMINOLOGY.md 不存在 | 3.10 | Agent 4 P2-v3-2 |
| v3.0-综合-P2-18 | P2 | error.h 路线图注释不一致 | 3.10 | Agent 3 V3.0-P2-2 |

### 7.2 v2.0 修正持久性综合矩阵

| # | Agent | 验证项 | 状态 | 关键证据 |
|---|-------|--------|------|---------|
| 1 | Agent 1 | P0-1 错误码 SSoT 统一 | ✅ 持久 | 582 处/29 文件统一为 POSIX errno 负值 |
| 2 | Agent 1 | P0-4 IPC 头三重违规 | ⚠️ 部分持久 | `06-ipc/README.md` 已修正，`02-l2-service-protocol.md` 遗漏 |
| 3 | Agent 1 | P0-5 "操作系统"误称 | ✅ 持久 | 37 处全部合法 |
| 4 | Agent 1 | P0-8 [SC] 头文件清单 | ✅ 持久 | syscalls.h 为 #6 |
| 5 | Agent 1 | P0-9 文件路径引用 | ✅ 持久 | 5 类旧路径 0 残留 |
| 6 | Agent 1 | P1-5 Cupola→Cupolas | ✅ 持久 | 0 残留 |
| 7 | Agent 1 | P1-6 Daemon 10→12 | ✅ 持久 | 2 匹配 |
| 8 | Agent 1 | P1-11 MemoryRovol 命名 | ✅ 持久 | L72 标准命名 |
| 9 | Agent 1 | P1-13 删除重复文件 | ✅ 持久 | 目录不存在 |
| 10 | Agent 1 | P1-1/3 函数前缀三层定义 | ✅ 持久 | 5 行匹配 |
| 11 | Agent 2 | 闭源手册 agentos_ 零残留 | ✅ 持久 | 仅手册 1 文件 0 残留 |
| 12 | Agent 2 | 闭源手册 AGENTOS_ 零残留 | ✅ 持久 | 0 残留 |
| 13 | Agent 2 | [SC] 6 头文件清单 | ✅ 持久 | 3 处全部为 6 |
| 14 | Agent 2 | 旧的"4 个"消除 | ✅ 持久 | 0 残留 |
| 15 | Agent 2 | 术语表 airy_sys_* | ✅ 持久 | line 106 |
| 16 | Agent 2 | 术语表 AIRY_E* | ✅ 持久 | line 111 |
| 17 | Agent 2 | 术语表 7+1 项 | ✅ 持久 | 7+1 |
| 18 | Agent 3 | P0-6 WebSocket 类型 | ✅ 持久 | L117 PROTOCOL_WEBSOCKET |
| 19 | Agent 3 | P0-7 agent_registry_core 4 函数 | ✅ 持久 | L71/82/98/110 |
| 20 | Agent 3 | N1 core_init DCLP | ✅ 持久 | 10 行匹配 |
| 21 | Agent 3 | N2 cupolas mutex destroy | ✅ 持久 | 5 处 |
| 22 | Agent 3 | N3 cupolas DCLP CAS | ✅ 持久 | 19 行匹配 |
| 23 | Agent 3 | N5 sched_d goto | ✅ 持久 | 8 行匹配 |
| 24 | Agent 3 | N6 sync_compat airy_err_t | ✅ 持久 | 25 wrapper + 1 mapping |
| 25 | Agent 4 | [SC] 6 头文件三方一致 | ✅ 持久 | 开源 34 处 + 闭源 19 处 |
| 26 | Agent 4 | 错误码命名 AIRY_ETIMEOUT | ✅ 持久 | 23 处 / AIRY_ETIMEDOUT 0 |
| 27 | Agent 4 | 闭源手册 agentos_/AGENTOS_ | ✅ 持久 | 0 残留 |
| 28 | Agent 4 | Cupola 单数修正 | ✅ 持久 | 0 残留 |
| 29 | Agent 4 | 源码 agentos_/airymaxos_ | ✅ 持久 | 0 残留 |
| 30 | Agent 4 | v2.0 修正 5 类旧路径 | ✅ 持久 | 全部 0 残留 |
| 31 | Agent 4 | 50-specifications 目录删除 | ✅ 持久 | 目录不存在 |

### 7.3 工作流优先级矩阵

| 优先级 | 工作流 | 工作量 | 触发条件 | 出口标准 |
|--------|--------|--------|---------|---------|
| **P0-阻断** | A：错误码 SSoT 统一收敛 | ~24h | M1 启动前必须完成 | SSoT 唯一方案 + 权威源存在 + 源码值对齐 |
| **P0-阻断** | B：IPC 消息头 SSoT 对齐 | ~5h | M1 启动前必须完成 | 2 处三重违规清零 |
| **P0-阻断** | C：函数前缀与 §11.6 重写 | ~9.6h | M1 启动前必须完成 | 340 处 agentos_* 清零 + §11.6 历史声明 |
| **P0-阻断** | E：源码并发安全修复 | ~3h | M1 启动前必须完成 | DCLP state 验证 + 超时重置 |
| **P0-阻断** | G：文档工程规范盲区 | ~1.4h | M1 启动前必须完成 | 版本号/配置文件名统一 |
| P1-早期 | D：路径引用与术语统一 | ~8.6h | M1 早期启动 | 路径断链清零 + Cupolas 7 子系统 |
| P1-早期 | H：遗留项清理 | ~0.5h | M1 早期启动 | P2 遗留项清零 |
| P1-全阶段 | F：源码工程标准分批 | ~40-46h | M1 全阶段渐进 | Tab 8 <500 + typedef <200 + goto ≥50 |

### 7.4 必读历史报告索引

| # | 报告 | 路径 | 版本 |
|---|------|------|------|
| 1 | v1.0 综合分析 | `docs-closed/agentrt/00-reviews/_review_v1.0/00-comprehensive-analysis.md` | 1.0（2026-07-13） |
| 2 | v2.0 工程规范与代码审查 | `docs-closed/agentrt/00-reviews/_review_v2.0/01-engineering-code-review-v2.md` | 2.0（2026-07-13） |
| 3 | v2.0 修正验证报告 | `docs-closed/agentrt/00-reviews/_review_v2.0/fix-verification-report.md` | 1.0（2026-07-13） |
| 4 | v3.0 开源文档审查 | `docs-closed/agentrt/00-reviews/_review_v3.0/01-open-docs-review.md` | 3.0（2026-07-14） |
| 5 | v3.0 闭源文档审查 | `docs-closed/agentrt/00-reviews/_review_v3.0/02-closed-docs-review.md` | 3.0（2026-07-14） |
| 6 | v3.0 源码审查 | `docs-closed/agentrt/00-reviews/_review_v3.0/03-source-code-review.md` | 3.0（2026-07-14） |
| 7 | v3.0 跨文档一致性审查 | `docs-closed/agentrt/00-reviews/_review_v3.0/04-cross-doc-consistency-review.md` | 3.0（2026-07-14） |

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>

---

**综合分析报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-14 | 审查版本：v3.0 | 评分模型：规范声明层 35% + 方案设计层 40% + 实现落地层 25%
