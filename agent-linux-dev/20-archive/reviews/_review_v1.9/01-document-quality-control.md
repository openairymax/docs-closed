Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# Airymax 文档规范与质量控制跨域审查报告 v2.0

> **文档定位**：v2.0 新增维度的跨域审查收敛报告，覆盖 `docs/`（开源）与 `docs-closed/`（闭源）两个仓库的文档规范与技术质量，作为 1.0.1 M1 启动前文档侧阻断项的判定基线之一。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：2.0（2026-07-13）。
> **审查范围**：开源 `docs/AirymaxOS/` + `docs/AirymaxRT/` + `docs/OpenStandards/` + 闭源 `docs-closed/agentrt/` + `docs-closed/agent-linux-dev/`，共 5 个文档子仓库；核心交叉验证文件 ~20 份。
> **审查方法**：参考文件精读 + Grep 机器检查 + 路径有效性实测（`ls -e`） + 上下游关系交叉对照 + 与 v1.0 综合分析（`docs-closed/agentrt/_review_v1.0/00-comprehensive-analysis.md`）结论对照。
> **证据要求**：所有结论附文件路径与行号（格式：`文件路径:L行号`），可通过 Grep/Read 工具复核。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. 开源文档技术准确性检查](#2-开源文档技术准确性检查)
- [3. 闭源文档工程准确性检查](#3-闭源文档工程准确性检查)
- [4. 跨仓库一致性检查](#4-跨仓库一致性检查)
- [5. 文档质量评估矩阵](#5-文档质量评估矩阵)
- [6. 问题清单（按严重程度排序）](#6-问题清单按严重程度排序)
- [7. 修复建议](#7-修复建议)

---

## 1. 执行摘要

### 1.1 审查目标与边界

本报告是 v2.0 新增的"文档规范与质量控制"维度审查，**不重复 v1.0 综合分析已覆盖的源码正确性、IPC 头三重违规、ES-SEL4-7 分类冲突等源码/方案侧问题**，而是聚焦于：

1. 开源文档对**上下游关系**（openEuler / seL4 / Linux 6.6 / agentrt ↔ agent-linux）描述的准确性；
2. 开源文档对**技术声明**（magic 值、SCHED_EXT、[SC] 头文件清单、错误码）的跨文档一致性；
3. **抄袭风险**与原创性声明充分性；
4. **开源 vs 闭源版本对齐**与"版本倒置"问题；
5. 闭源工程文档的事实性、工程指导性、特有准确性问题；
6. **跨仓库概念定义、术语表、引用路径**的一致性。

### 1.2 综合评分

| 评分维度 | 评分 | 说明 |
|---------|------|------|
| 开源文档技术准确性 | **55/D+** | IPC magic / AGTS magic / SCHED_EXT=7 跨文档一致；但 [SC] 头文件清单在 AirymaxRT 与 AirymaxOS/OpenStandards 之间不一致，错误码 6 套方案未收敛 |
| 上下游关系描述 | **65/C+** | AirymaxOS 与 openEuler / seL4 / Linux 6.6 关系总体准确；但 BAN-INTERNAL-002 与开源实际现状存在偏差（5 文件仍含 openEuler） |
| 抄袭风险 | **80/B+** | seL4 / Linux / openEuler 引用均注明来源；MCIS 原创性声明充分；未发现直接复制 |
| 版本一致性 | **45/D** | OpenStandards README 头部 1.0 vs 版本历史 1.1 矛盾；AirymaxRT README 无版本号；闭源 agentrt 工程标准手册 v28.0 与开源 v0.1.1 对齐但内部 29→38 仓变更说明残留 |
| 工程指导性（闭源） | **70/B-** | 闭源总纲 v0.2.5 + 开发路线可指导 1.0.1 M1；但闭源 agentrt 工程标准手册（v28.0）使用已废弃的 `agentos_*` 前缀，与实际源码 `airy_*` 严重背离 |
| 引用有效性 | **35/D-** | 5 个文档仓库均存在引用路径错误：开源 AirymaxRT 引用 `00-basic-theories/`（应为 `00-requirements/`）、`30-coding-standard/`、`08-compliance-checklist.md`、`70-project-erp/`、`DocsClosed/` 等不存在路径；闭源 agent-linux/README.md 引用 `docs/AirymaxAgentOS/`（应为 `docs/AirymaxOS/`） |
| **总评** | **58/D+** | 文档技术内核（magic/AGTS/SCHED_EXT）扎实，但引用路径体系、版本一致性、闭源手册与源码对齐存在系统性缺陷；开源文档已可对外发布但需先修复路径错误 |

### 1.3 核心结论

> **5 个文档仓库当前未达到"文档侧可开发"状态**：技术内核（IPC magic 0x41524531 / AGTS 0x41475453 / SCHED_EXT=7 / 微核心-微内核术语区分）跨文档一致且准确；但**引用路径体系系统性失效**（5 仓库全部存在引用错误）、**版本号体系混乱**（OpenStandards 内部 1.0 vs 1.1 矛盾、AirymaxRT 无版本号、闭源 agentrt 工程标准手册与源码前缀严重背离）、**[SC] 6 头文件清单在 AirymaxRT 与 SSoT 之间不一致**（仍列 `bpf_struct_ops.h` 而非 `syscalls.h`），需在进入 1.0.1 M1 代码开发前完成收敛。

### 1.4 与 v1.0 综合分析的关系

本报告**沿用 v1.0 综合分析（`docs-closed/agentrt/_review_v1.0/00-comprehensive-analysis.md`）**关于 P0-1（错误码 6 套）、P0-5（"操作系统"误称 15+ 处）、P0-8（[SC] 头文件清单不一致）、P0-9（文件路径引用错误）的判定，并经本次实测**全部确认仍然存在**（截至 2026-07-13）；同时新增**版本一致性、上下游关系、抄袭风险、闭源手册与源码前缀背离** 4 类 v1.0 未覆盖的问题。

---

## 2. 开源文档技术准确性检查

### 2.1 上下游关系描述准确性

#### 2.1.1 AirymaxOS 与 openEuler 的关系（准确但与 BAN 规则冲突）

| 维度 | 描述 | 评估 |
|------|------|------|
| 关系定位 | "工程实现标准完全对齐 Linux 6.6 内核基线（参考 `01Reference/kernel-OLK-6.6`，即 openEuler OLK-6.6 内核源代码）。agent-linux 不移植 openEuler 特有特性，与 openEuler 的关系仅限于技术参考，不共享代码" | **准确** |
| 证据 | `docs/AirymaxOS/README.md:163` | — |
| 冲突点 | 同一行明示 "openEuler OLK-6.6 内核源代码"，与闭源 `docs-closed/agent-linux-dev/README.md:78` BAN-INTERNAL-002 "开源文档 `docs/AirymaxAgentOS/` 中严禁出现 'openEuler'、'open Euler'、'openeuler' 等描述" 直接冲突 | **冲突** |

**实测 openEuler 在开源文档中的出现位置**（5 个文件，32 处提及）：

| 文件 | 行号 | 上下文 | 是否违规 |
|------|------|--------|---------|
| `docs/AirymaxOS/README.md` | 30, 163 | "openEuler OLK-6.6 标杆" / "openEuler OLK-6.6 内核源代码" | 违规（BAN-INTERNAL-002） |
| `docs/AirymaxOS/10-architecture/06-directory-structure.md` | 118, 222, 234, 235 | "openEuler 扩展（C-D01）" / "Makefile.oever openEuler 扩展" / "lib/Kconfig.openeuler openEuler Kconfig 扩展" | 违规 |
| `docs/AirymaxOS/50-engineering-standards/README.md` | 230, 231, 242 | "OLK-6.6 `Makefile.oever`（openEuler 发行版构建扩展）" / "Kconfig.openeuler 配置规范" | 违规 |
| `docs/OpenStandards/_research_v1.0/01-open-standards-rebuild-proposal.md` | 22, 84, 86, 96, 99, 141, 481, 483, 485, 490, 491, 495, 496, 523, 533, 544, 545, 588, 595, 1013, 1029, 1091 | 多处对比治理模式 | 研究文档（边缘） |

**结论**：开源 `docs/AirymaxOS/` 中存在 **3 个生产级文档文件、共 9 处** openEuler 提及，与闭源 BAN-INTERNAL-002 形成直接冲突；同时 BAN-INTERNAL-002 自身存在路径错误（声明 `docs/AirymaxAgentOS/` 而实际路径为 `docs/AirymaxOS/`，详见 §4.3）。

#### 2.1.2 AirymaxOS 与 seL4 的关系（准确）

`docs/AirymaxOS/README.md:28-30`：
- "**微内核设计思想** | 最小化特权态代码、服务用户态化、消息传递通信、capability 安全 | seL4（核心参考，ADR-014 唯一来源）"
- 明确"参考来源：seL4 源码（`01Reference/seL4-master`）"

`docs/AirymaxOS/README.md:163` 进一步明示："agent-linux 的微内核设计思想**唯一来源为 seL4**"。

**评估**：**准确**。seL4 借鉴边界清晰，仅限架构层（capability / 消息传递 / 服务用户态化 / 形式化验证），未宣称代码移植，与 IRON-012 约束一致。

#### 2.1.3 AirymaxOS 与 Linux 6.6 内核基线的关系（准确）

`docs/AirymaxOS/README.md:30`：
- "Linux 6.6 内核基线 | 基于 Linux 6.6 内核，sched_ext + eBPF + io_uring + Rust 微内核化改造"
- 明确"openEuler OLK-6.6 标杆"和具体源码路径 `01Reference/kernel-OLK-6.6`

`docs/OpenStandards/06-airy-scheduling-standard.md:35`：明示"SCHED_EXT | Linux 可扩展调度器框架（主线 6.12+，agent-linux 向前移植到 6.6）"——准确描述了 sched_ext 主线版本与 6.6 向前移植关系。

**评估**：**准确**。Linux 6.6 基线约束清晰，与 IRON-10（禁止引用 Linux 7.0 专属特性）一致。

#### 2.1.4 AirymaxRT 与 agent-linux 的关系（准确）

`docs/AirymaxRT/README.md:18`：明示"agentrt 与 agent-linux 共用一套工程标准，物理宿主在 `docs/AirymaxOS/50-engineering-standards/`，通过符号链接 `50-engineering-standards` 引用"。

`docs/AirymaxOS/README.md:165-179`：详细图示 agentrt 与 agent-linux 的同源关系（MicroCoreRT↔Agent 调度、AgentsIPC↔IPC 子系统、Cupolas↔capability+LSM 等 5 项同源映射）。

实测：`docs/AirymaxRT/50-engineering-standards` 符号链接存在且有效。

**评估**：**准确**。共用工程标准机制通过符号链接落地，符合 IRON-9 v2 同源原则。

#### 2.1.5 OpenStandards 与 agentrt/agent-linux 的关系（准确）

`docs/OpenStandards/README.md:27-65`：明示"本体系标准来自 agentrt 与 agent-linux 的共同抽象，遵循 IRON-9 v2 三层模型"，且 [SC]/[SS]/[IND] 三层在开放标准中的体现清晰（仅公开 [SC] 与 [SS]）。

**评估**：**准确**。

### 2.2 技术准确性检查

#### 2.2.1 IPC magic 值（0x41524531 = 'ARE1'）—— 一致

实测 7 处定义/引用，全部一致为 `0x41524531`：

| 文件 | 行号 | 表述 |
|------|------|------|
| `docs/OpenStandards/02-airy-ipc-protocol-standard.md` | 65 | `#define AIRY_IPC_MAGIC 0x41524531u /* 'A''R''E''1' */` |
| `docs/OpenStandards/01-airy-agent-runtime-standard.md` | 515 | `hdr.magic = AIRY_IPC_MAGIC; /* 0x41524531 */` |
| `docs/AirymaxOS/30-interfaces/02-ipc-protocol.md` | 37, 59, 80, 399, 456, 462, 470, 526 | `#define AIRY_IPC_MAGIC 0x41524531u`（多处一致） |
| `docs/AirymaxOS/30-interfaces/01-syscalls.md` | 489, 499 | "IPC magic 0x41524531 'ARE1'" |
| `docs/AirymaxOS/50-engineering-standards/01-coding-standards.md` | 2960, 2968, 2973 | `#define AIRY_IPC_MAGIC 0x41524531 /* 'ARE1' */` |
| `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md` | 584, 1310, 1331 | 一致 |
| `docs/AirymaxRT/30-interfaces/06-ipc/README.md` | 28 | `uint32_t magic; // 0x41524531 ("ARE1")` |

**评估**：**完全一致**。IPC magic 值在所有开源文档中跨仓库一致，与源码 `commons/include/airymax/ipc.h:18` 一致。

#### 2.2.2 任务描述符 magic（0x41475453 = 'AGTS'）—— 一致

实测 14 处定义/引用，全部一致为 `0x41475453`：

| 文件 | 行号 |
|------|------|
| `docs/AirymaxOS/30-interfaces/01-syscalls.md` | 489, 498, 538 |
| `docs/AirymaxOS/30-interfaces/03-sdk-api.md` | 527 |
| `docs/AirymaxOS/30-interfaces/05-syscall-semantic-mapping.md` | 132, 346, 395 |
| `docs/AirymaxOS/10-architecture/04-engineering-baseline.md` | 580 |
| `docs/AirymaxOS/10-architecture/05-adrs.md` | 1087 |
| `docs/AirymaxOS/10-architecture/03-microkernel-strategy.md` | 601 |
| `docs/AirymaxOS/10-architecture/02-five-dimensional-principles.md` | 584 |
| `docs/AirymaxOS/10-architecture/06-directory-structure.md` | 147 |
| `docs/AirymaxOS/60-driver-model/01-device-model.md` | 490, 503, 506 |
| `docs/AirymaxOS/60-driver-model/02-platform-driver.md` | 491, 504, 507 |
| `docs/AirymaxOS/40-dataflows/04-scheduling-flow.md` | 89, 273, 278, 805, 851, 869 |

**评估**：**完全一致**。AGTS magic 值在所有开源文档中跨仓库一致，与源码 `commons/include/airymax/sched.h` 一致。

#### 2.2.3 SCHED_EXT=7 —— 一致但有 SCHED_AGENT=8 边界争议

| 文件 | 行号 | 表述 |
|------|------|------|
| `docs/OpenStandards/06-airy-scheduling-standard.md` | 71-72 | `\| SCHED_EXT \| 7 \| 可扩展 \| ...` / `\| SCHED_AGENT \| 8 \| Agent 调度类 \| Airymax 专属（基于 SCHED_EXT）` |
| `docs/OpenStandards/06-airy-scheduling-standard.md` | 74 | "`SCHED_EXT=7` **永久稳定**（AOS-STD-SCHED-001，L1 稳定级，对齐 Linux 主线）" |
| `docs/AirymaxOS/30-interfaces/01-syscalls.md` | 489, 498 | "SCHED_EXT=7" |
| `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md` | 583 | "SCHED_EXT 调度类编号约束（复用内核 SCHED_EXT=7，禁止 SCHED_AGENT 宏）" |

**评估**：SCHED_EXT=7 跨文档一致，**正确**。但存在**边界争议**：
- `docs/OpenStandards/06-airy-scheduling-standard.md:72` 定义 `SCHED_AGENT=8` 为 Airymax 专属调度类编号；
- 而 `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md:583` 明示"禁止 SCHED_AGENT 宏"；
- 与 v1.0 综合分析 §5.3（"复用内核 SCHED_EXT=7，禁止 SCHED_AGENT 宏"）一致。

**结论**：开放标准定义 SCHED_AGENT=8 作为"对外公开的语义编号"，但内部工程标准禁止在源码中使用 `SCHED_AGENT` 宏——这是合理的双层语义，但**应在开放标准中明示"SCHED_AGENT 是抽象调度类语义标识，源码实现使用 sched_ext struct_ops 注册而非宏"**，否则外部实现者可能误解为应定义 `SCHED_AGENT=8` 宏。

#### 2.2.4 [SC] 6 个头文件清单 —— **AirymaxRT 与 SSoT 不一致**（v1.0 P0-8 仍存在）

**SSoT 权威定义**（`docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:65-77`）：

| 序号 | 文件 |
|------|------|
| 1 | `memory_types.h` |
| 2 | `security_types.h` |
| 3 | `cognition_types.h` |
| 4 | `sched.h` |
| 5 | `ipc.h` |
| 6 | `syscalls.h` |
| 补充 | `bpf_struct_ops.h`（**非 [SC] 核心头文件**，line 85 明示） |

**AirymaxRT 文档侧**（`docs/AirymaxRT/10-architecture/06-iron9-shared-model.md:64-73`）：

| 序号 | 文件 |
|------|------|
| 1 | `bpf_struct_ops.h` ← **错误，应为 `syscalls.h`** |
| 2 | `memory_types.h` |
| 3 | `security_types.h` |
| 4 | `cognition_types.h` |
| 5 | `sched.h` |
| 6 | `ipc.h` |

**对比 OpenStandards**（`docs/OpenStandards/07-airy-syscall-standard.md:635`）：明示"`syscalls.h`（24 槽位编号）+ `ipc.h`（IPC magic + 128B 消息头）+ `sched.h`（任务描述符 magic + SCHED_EXT=7）+ `security_types.h` + `memory_types.h` + `cognition_types.h`"——**6 头文件清单与 SSoT 一致**。

**评估**：v1.0 综合分析 P0-8（[SC] 头文件清单不一致）**仍存在**。AirymaxRT 文档侧第 1 项错误地用 `bpf_struct_ops.h` 替代了 `syscalls.h`，与 SSoT、OpenStandards、AirymaxOS、源码 `commons/include/airymax/syscalls.h`（实际存在并使用 Tab 8 缩进）均不一致。需在 1.0.1 M1 启动前修复。

#### 2.2.5 错误码定义 —— **6 套方案仍并存**（v1.0 P0-1 仍存在）

实测 AirymaxRT 文档中错误码方案至少 4 套并存：

| 方案 | 文件 | 行号 | 表述 |
|------|------|------|------|
| A（POSIX errno 直接赋值） | `docs/AirymaxRT/10-architecture/00-architectural-principles.md` | 923-924 | `AIRY_EOK = 0, AIRY_EINVAL = EINVAL` |
| B（POSIX 对齐负值 -22） | `docs/AirymaxRT/10-architecture/06-iron9-shared-model.md` | 214-215 | `#define AIRY_EOK 0` / `#define AIRY_EINVAL (-22)`（注释含递归错误："/* 成功（替代 AIRY_EOK） */"） |
| C（正值序列 1001） | `docs/AirymaxRT/10-architecture/05-syscall.md` | 641, 644 | `AIRY_EOK = 0, AIRY_EINVAL = 1001` |
| D（双错误码体系） | `docs/AirymaxRT/20-modules/10-contracts/03-protocol-contract.md` | 685 | "C 内核层使用负整数（如 `AIRY_EINVAL=-1`），SDK/外部层使用十六进制字符串（如 `"0x0003"`）" |
| E（同上双体系） | `docs/AirymaxRT/20-modules/10-contracts/05-logging-format.md` | 301 | "C 内核层使用负整数（如 `-2`），SDK/外部层使用十六进制字符串（如 `"0x0003"`）" |

**评估**：v1.0 综合分析 P0-1（错误码 6 套方案并存）**仍存在**。`AIRY_EINVAL` 至少有 4 种取值（`EINVAL` / `-22` / `1001` / `-1` / `-2`），C 内核与 SDK 双错误码体系描述混乱。SSoT 应为 `airy_err_t`（`int32_t`）+ `AIRY_EOK=0` + 13 个 `AIRY_E*` 宏（负值），但 AirymaxRT 文档侧未对齐。

### 2.3 抄袭风险检查

#### 2.3.1 openEuler 文档抄袭风险——**低**

`docs/AirymaxOS/README.md:163` 明示"agent-linux 不移植 openEuler 特有特性，与 openEuler 的关系仅限于技术参考，不共享代码"。

闭源 `docs-closed/agent-linux-dev/README.md:79-81` BAN-INTERNAL-003/004/005 进一步约束："openEuler 内容必须经过消化吸收后才能体现在开源设计文档中" / "开源文档中的技术方案表述必须用 AirymaxOS 自身语言，不能是 openEuler 的直接翻译"。

**评估**：**无抄袭风险**。但 BAN-INTERNAL-002 在开源实际执行层面失效（5 文件仍含 openEuler，详见 §2.1.1），需统一规则与执行。

#### 2.3.2 seL4 文档抄袭风险——**低**

`docs/AirymaxOS/README.md:29-30` 明示 seL4 为"核心参考，ADR-014 唯一来源"。

v1.0 综合分析 §5.6 确认："seL4 借鉴仅限架构层（IRON-012 约束），注明参考来源（`20-modules/01-kernel.md:55-62` 引用 Liedtke 原文）"。

**评估**：**无抄袭风险**。引用 Liedtke 原文且明示借鉴边界。

#### 2.3.3 Linux 内核文档抄袭风险——**低**

`docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:36-40` 明示 Linux 6.6 内核基线源码路径引用（如 `include/uapi/linux/sched.h:114-123`、`arch/x86/Makefile:137-138`、`scripts/checkpatch.pl:836-851`），均为路径引用而非内容复制。

**评估**：**无抄袭风险**。Linux 内核引用具体到源码行号，符合开源引用规范。

#### 2.3.4 MCIS（多体控制论智能系统）原创性声明——**充分**

`docs/AirymaxRT/00-requirements/01-mcis-cn.md` 完整阐述 MCIS 体系并行论。

v1.0 综合分析 §5.6 确认："MCIS 体系并行论 + 五维正交 24 原则为原创理论框架，无抄袭风险"。

`docs/AirymaxOS/README.md:149-162` 列出 10 项前沿理论参考，明确区分"参考来源"（seL4 / LionsOS / sDDF / Linux 6.6 / sched_ext / io_uring / eBPF / MGLRU / Wasm 3.0 / CXL）与"Airymax 原创"（MicroCoreRT / CoreLoopThree / MemoryRovol / Thinkdual / Cupolas）。

**评估**：**原创性声明充分**。

#### 2.3.5 引用外部规范的引文格式——**良好但有改进空间**

`docs/OpenStandards/_research_v1.0/01-open-standards-rebuild-proposal.md:22` 明示"所有外部引用必须附 URL，不得转述为 Airymax 自有观点"。

`docs/OpenStandards/06-airy-scheduling-standard.md:542` 引用 Linux sched_ext 文档附 URL：`https://docs.kernel.org/scheduler/sched-ext.html`。

`docs/OpenStandards/07-airy-syscall-standard.md:662` 同样附 URL。

**评估**：**良好**。但 OpenStandards 7 个主题标准文档（01-07）仅个别附 URL，建议在每条引用外部规范处统一附 URL。

### 2.4 开源文档版本一致性

#### 2.4.1 各文档仓库版本号清单

| 文档仓库 | 头部版本 | 版本历史最新 | 最后更新 | 评估 |
|---------|---------|-------------|---------|------|
| `docs/AirymaxOS/README.md` | 0.1.1（line 8） | — | 2026-07-13（line 9） | OK |
| `docs/AirymaxRT/README.md` | **无版本号**（仅"最新更新 2026-07-11"，line 8） | — | 2026-07-11 | **缺失** |
| `docs/AirymaxRT/README_zh.md` | **无版本号**（同上，line 8） | — | 2026-07-11 | **缺失** |
| `docs/OpenStandards/README.md` | **1.0（开放标准草案）**（line 6, 118） | **1.1**（line 245，2026-07-11，新增 07 系统调用标准） | 2026-07-11 | **内部矛盾**（头部 1.0 vs 历史 1.1） |
| `docs/OpenStandards/01-airy-agent-runtime-standard.md` | 1.0（line 6） | — | 2026-07-09 | 与 README 1.1 不一致（个体标准未跟进） |
| `docs/OpenStandards/06-airy-scheduling-standard.md` | 1.0（版本历史 line 532） | — | 2026-07-09 | 同上 |
| `docs/OpenStandards/07-airy-syscall-standard.md` | 应为 1.1（README 历史 line 245 称 1.1 新增 07） | — | — | **需明示** |

#### 2.4.2 版本倒置检查

| 开源版本 | 闭源对应版本 | 是否倒置 |
|---------|------------|---------|
| AirymaxOS README v0.1.1（2026-07-13） | agent-linux 基本工程标准规范 v0.2.5（2026-07-13） | **正常**（闭源总纲 v0.2.5 是开源手册 v0.1.1 的工程实施细化版，闭源略新于开源属合理） |
| AirymaxRT README 无版本号（2026-07-11） | agentrt 工程标准规范手册 v28.0（2026-07-06，适用 AgentRT v0.1.1） | **倒置**（闭源最后更新 2026-07-06 早于开源 2026-07-11，但闭源版本号 v28.0 与开源 v0.1.1 不可比） |
| OpenStandards README 1.0/1.1（2026-07-11） | 无对应闭源 | N/A |

**评估**：开源 AirymaxRT 缺失版本号导致无法做版本对齐判定；OpenStandards README 内部 1.0 vs 1.1 矛盾是 P1 级问题。

---

## 3. 闭源文档工程准确性检查

### 3.1 内部工程文档的事实性

#### 3.1.1 `docs-closed/agentrt/` 内部工程文档的事实性

| 文档 | 版本 | 事实性评估 |
|------|------|-----------|
| `docs-closed/agentrt/README.md` | 0.1.1（2026-07-10） | 目录结构描述与实际目录一致（已实测 05-tech-reference-and-improvement/、06-contracts/、07-subsystem-specs/、_analysis_0.1.1/、_review_0.1.1/、_design_0.1.1/、_archive_conversations/、_archive_fix_history/ 全部存在） |
| `docs-closed/agentrt/agentrt工程标准规范手册.md` | v28.0（2026-07-06，适用 AgentRT v0.1.1） | **存在系统性事实性失真**（详见 §3.1.3） |

#### 3.1.2 `docs-closed/agent-linux-dev/` 内部工程文档的事实性

| 文档 | 版本 | 事实性评估 |
|------|------|-----------|
| `docs-closed/agent-linux-dev/README.md` | 0.1.1（2026-07-07） | **目录结构描述与实际路径不一致**（详见 §3.3） |
| `docs-closed/agent-linux-dev/agent-linux基本工程标准规范.md` | v0.2.5（2026-07-13） | 事实性较高，与开源手册对齐（[SC] 6 头文件清单正确，line 11） |
| `docs-closed/agent-linux-dev/agent-linux开发路线和进度.md` | v0.2.5（2026-07-13） | 进度描述与 v1.0 综合分析结论一致；但 line 69 仍使用 "29 仓拆分" 旧表述（与同目录闭源总纲 v0.2.5 未明示 38 仓迁移） |

#### 3.1.3 闭源 agentrt 工程标准手册的事实性失真（系统性）

`docs-closed/agentrt/agentrt工程标准规范手册.md` 存在 3 类事实性失真：

**失真 1：[SC] 共享契约层头文件数量错误（4 vs 6）**

`docs-closed/agentrt/agentrt工程标准规范手册.md:21`：
> "[SC] 共享契约层（`include/airymax/` 4 个头文件完全共享：bpf_struct_ops.h / memory_types.h / security_types.h / cognition_types.h）"

**对比事实**：
- 同目录闭源 `agent-linux基本工程标准规范.md:11` 明示"[SC] 共享契约层 6 个头文件落地于 `include/airymax/`"——**正确**；
- 开源 `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:65-77` 明示 6 个头文件——**正确**；
- 源码 `commons/include/airymax/` 实际存在 6 个 [SC] 头文件 + 1 个补充文件 `bpf_struct_ops.h`。

**结论**：闭源 agentrt 工程标准手册的 [SC] 头文件数量声明（4 个）与所有其他文档（6 个）和源码（6 个）均不一致，是 v28.0 历史遗留未更新。

**失真 2：代码前缀使用已废弃的 `agentos_*`**

`docs-closed/agentrt/agentrt工程标准规范手册.md:99-111` 术语强制规范表：

| 标准名称 | 标准英文 | 手册声明代码前缀 | 实际源码前缀（v1.0 §5.2） |
|---------|---------|----------------|------------------------|
| 原子核心 | CoreKern | `agentos_core_*` | `airy_*`（atoms 916+ 处） |
| 三层认知循环 | CoreLoopThree | `agentos_loop_*` | `airy_*` |
| 记忆卷载 | MemoryRovol | `agentos_layer*_*` | `airy_*` |
| 系统调用层 | AirymaxSyscall | `agentos_sys_*` | `airy_sys_*` |
| 任务流引擎 | TaskFlow | `agentos_taskflow_*` | `airy_*` |
| 记忆交换算法 | MemorySwap | `agentos_memory_swap_*` | `airy_*` |
| 统一错误码体系 | ErrorCodeSystem | `AGENTOS_E*` | `AIRY_E*`（atoms 916+ 处） |

**结论**：闭源 agentrt 工程标准手册的所有代码前缀声明与实际源码 100% 不一致。手册描述的是 v25.0 之前的 `agentos_*` 时代状态，而源码已彻底迁移至 `airy_*`（v1.0 §5.2 确认 `agentos_*` 在源码中 0 残留）。手册自身的 v26.0 变动说明（line 9）也提到"agentos_ → agentrt_ 改名彻底"，但实际源码用的是 `airy_*` 而非 `agentrt_*`——**改名方向与实际源码不一致**。

**失真 3：仓库总数 29 → 38 变更说明残留**

`docs-closed/agentrt/agentrt工程标准规范手册.md:9,19`：
- line 9（v26.0 历史）：声明 "29 仓拆分：1 伞仓 + 4 管理仓 + 21 叶子仓 + 3 顶层仓"（数学校验：1+4+21+3=29 ✓）
- line 4-5（v28.0 当前）：声明 "38 仓拆分" / "38 个 git 仓库（伞仓 airymaxhub + 5 管理仓 agentrt/agent-linux/sdk/ecosystem/products + 29 叶子仓 + 3 顶层仓 devtools/docs/docs-closed）"（数学校验：1+5+29+3=38 ✓）
- line 19（v27.0 变动说明）："仓库总数变更：29 仓 → 38 仓（+9）"

**结论**：仓库数从 29 涨至 38 是 v27.0 的合理变更，但**手册保留了 v26.0 历史"29 仓拆分：1+4+21+3"明细**，与 v28.0 当前"38 仓：1+5+29+3"明细并列出现，读者易混淆。

#### 3.1.4 闭源文档与开源文档的矛盾检查

| 矛盾点 | 闭源声明 | 开源声明 | 严重程度 |
|--------|---------|---------|---------|
| [SC] 头文件数量 | 4 个（agentrt 手册） | 6 个（agent-linux 总纲、AirymaxOS、OpenStandards、源码） | **P0** |
| 代码前缀 | `agentos_*`（agentrt 手册） | `airy_*`（OpenStandards、AirymaxOS、源码） | **P0** |
| daemon 数量 | 12 个（agentrt 手册 line 9 称"16 个 daemon"） | 12 个（AirymaxRT `02-l2-service-protocol.md`、v1.0 §5.8） | P2 |
| 仓库总数 | 38 仓（agentrt 手册 v28.0）/ 29 仓（agent-linux 开发路线 line 69） | 8 子仓（AirymaxOS README，仅 agent-linux 范围） | P1（语义不同但表述易混） |

### 3.2 工程指导性

#### 3.2.1 闭源总纲 v0.2.5（agent-linux基本工程标准规范.md）—— **指导性强**

`docs-closed/agent-linux-dev/agent-linux基本工程标准规范.md` 14 章正文 + 5 附录，覆盖：
- 第 1-3 章：总则、代码规范、代码格式（OLK-6.6 Tab 8/snake_case/最小 typedef 等）
- 第 4-8 章：工程思想（ES-OLK-1~13）、开发流程、工具链、维护者制度、规范符合性检查
- 第 9 章：IRON-9 v2 三层共享模型（含 [SC] 6 头文件落地路径）
- 第 10 章：Euler 标准兼容性
- 第 11 章：禁词清单与处罚机制
- 第 12-14 章："Linux 6.6 为基、seL4 为鉴"工程取向、8 子仓目录结构、P2 增强建议落地规划

**评估**：**指导性强**，可作为 1.0.1 M1 内核开发组的执行基线。

#### 3.2.2 闭源开发路线 v0.2.5（agent-linux开发路线和进度.md）—— **指导性强**

`docs-closed/agent-linux-dev/agent-linux开发路线和进度.md` 13 章覆盖：
- 9 里程碑（M0-M8）
- 任务分解 WBS
- 资源分配
- 进度跟踪机制
- 验收标准
- 风险识别与缓解
- 与 agentrt 协同

明示总工时 ~2,750h（line 44），与 v1.0 综合分析 §6.1 工作量估算（方案侧 P0 ~21h + P1 ~23h）形成对照（一个是开发总工时，一个是审查修复工时）。

**评估**：**指导性强**，但 line 69 "29 仓拆分 ~1,800h" 与同目录闭源总纲未明示 38 仓迁移形成不一致（详见 §3.1.4）。

#### 3.2.3 闭源 agentrt 工程标准手册 v28.0 —— **指导性被失真削弱**

`docs-closed/agentrt/agentrt工程标准规范手册.md` 虽然覆盖 38 章 + BAN 规则 357 项 + ACC 138 项，体系庞大，但存在以下指导性削弱点：

1. **代码前缀全部错误**（详见 §3.1.3 失真 2）：开发者按手册使用 `agentos_*` 前缀将与实际源码 `airy_*` 严重背离，CI 门禁直接失败。
2. **[SC] 头文件数量错误**（详见 §3.1.3 失真 1）：开发者按手册只共享 4 个头文件将漏掉 `syscalls.h` 和 `ipc.h`/`sched.h`，破坏 IRON-014。
3. **抽象设计文档**：第 33-34 章微内核架构规范、开放标准规范属于设计层，缺少与具体子仓代码的映射示例。
4. **缺少实施细节**：第 36 章 38 仓 git 拆分工程规范虽有 SPLIT-01~SPLIT-08 8 项规则，但未提供 `git subtree split`/`git submodule add` 的具体命令序列示例。

**评估**：**指导性被失真削弱**，需在 1.0.1 M1 启动前完成代码前缀和 [SC] 头文件清单的事实性更新。

### 3.3 闭源文档特有的准确性问题

#### 3.3.1 闭源 `agent-linux基本工程标准规范.md` 工程准确性——**较高**

- line 11：[SC] 6 个头文件清单**正确**（与开源 SSoT 一致）
- line 14：明示"OLK-6.6 均为 openEuler 官方分支名称或路径引用，非概念引用"——术语清洗准确
- line 31：SCHED_EXT=7 约束**正确**
- line 12：引用 `docs/00-architectural-principles.md`——**路径错误**（实际为 `docs/AirymaxRT/10-architecture/00-architectural-principles.md`）
- line 60：引用 `0.1.1工程标准规范手册.md`——**路径错误**（实际为 `docs-closed/agentrt/agentrt工程标准规范手册.md`）

#### 3.3.2 闭源 `agent-linux开发路线和进度.md` 进度准确性——**较高**

- line 10：明示"Wave 2 v2（2026-07-13）源码级深读审查完成，三层对齐度评分从 61/C+ 跃升至 80/B，达到'可开始进行工程开发'文档层面前置条件"——与 v1.0 综合分析 §7（agentrt 源码 vs 工程标准 45/D+）存在评分差异，原因是闭源开发路线聚焦 agent-linux 文档层，v1.0 综合分析聚焦 agentrt 源码层，两者评分对象不同，**不构成矛盾**。
- line 69："29 仓拆分 ~1,800h"——与同目录闭源总纲 v0.2.5 未明示 38 仓迁移路径**不一致**。

#### 3.3.3 闭源审查报告结论准确性

| 审查报告 | 路径 | 综合评分 | 与 v1.0 综合分析对照 |
|---------|------|---------|--------------------|
| `docs-closed/agentrt/_review_v1.0/00-comprehensive-analysis.md` | v1.0 | 65/C+ | —（本身） |
| `docs-closed/agentrt/_review_v1.0/03-airymaxrt-solution-review.md` | v1.0 | 62/C+ | 与 v1.0 综合分析 §1.2 一致 |
| `docs-closed/agent-linux-dev/_review_v1.0/01-systematic-recheck.md` | v1.0 | 79/B+ | 与 v1.0 综合分析 §1.2 一致 |
| `docs-closed/agent-linux-dev/_review_0.9.0/` 7 份报告 | 0.9.0 | — | 已被 v1.0 综合分析引用 |

**评估**：**结论准确**。但 v1.0 综合分析 P0-1/4/5/8/9 等 5 项方案侧 P0 仍存在（截至 2026-07-13 实测），需在 v2.0 报告中明示。

---

## 4. 跨仓库一致性检查

### 4.1 概念定义一致性

#### 4.1.1 "微核心"（micro-core）vs "微内核"（micro-kernel）—— **跨仓库一致**

| 文档 | 表述 | 评估 |
|------|------|------|
| `docs/OpenStandards/README.md:33-39` | "agentrt = 微核心（micro-core），不得用'微内核'描述 agentrt" / "agent-linux = 微内核（micro-kernel）" | **正确** |
| `docs/OpenStandards/01-airy-agent-runtime-standard.md:31-32` | "微核心（micro-core）用户态极简运行时核心（agentrt 定位）" / "微内核（micro-kernel）操作系统发行版的内核极简化形态（agent-linux 定位）" | **正确** |
| `docs/AirymaxRT/README.md:16` | "AirymaxAgentRT 是用户态 AI Agent 运行时，定位为**微核心**（micro-core）" | **正确** |
| `docs/AirymaxOS/README.md:16,21` | "agent-linux 是基于 Linux 内核的**操作系统发行版**" + "微内核设计思想" | **正确** |
| `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:24-27` | "agentrt（用户态）= 微核心（micro-core）" / "agent-linux（OS 发行版）= 微内核（micro-kernel）" / "禁止用'微内核原语'描述 agentrt" | **正确** |
| `docs-closed/agentrt/agentrt工程标准规范手册.md:103` | "微核心 \| MicroCoreRT \| `agentos_core_*` \| '微内核'、'Microkernel'" | 概念**正确**，代码前缀**错误**（详见 §3.1.3） |
| `docs-closed/agent-linux-dev/agent-linux基本工程标准规范.md:24-27` | 同开源 120-cross-project-code-sharing.md | **正确** |

**评估**：**概念定义跨仓库一致**。但闭源 agentrt 工程标准手册的代码前缀列错误（详见 §3.1.3）。

#### 4.1.2 "agentrt" vs "agent-linux" 定位描述—— **跨仓库一致**

`docs/OpenStandards/README.md:31-39`、`docs/AirymaxOS/README.md:14-23`、`docs/AirymaxRT/README.md:16`、`docs-closed/agentrt/README.md:1-3`、`docs-closed/agent-linux-dev/README.md:1-9` 均一致：
- agentrt = 跨平台用户态运行时（微核心）
- agent-linux = 基于 Linux 内核的发行版（微内核，AirymaxOS）

#### 4.1.3 "AirymaxOS" vs "AirymaxRT" 命名—— **跨仓库一致但有历史别名残留**

`docs/AirymaxOS/README.md:6-8` 明示："正式全称：agent-linux（极境智能体操作系统，英文名：AirymaxOS）/ 仓库别名：agent-linux（仓库名）"。

`docs/AirymaxRT/README.md:4` 明示："AirymaxAgentRT 文档中心"。

**历史别名残留**：
- `docs-closed/agent-linux-dev/README.md:18,66,71,124-126` 引用 `docs/AirymaxAgentOS/`（实际为 `docs/AirymaxOS/`）—— **路径错误 4 处**
- `docs-closed/agentrt/agentrt工程标准规范手册.md:20` 明示"OS 文档位置决策：OS 设计文档全部在 `docs/AirymaxAgentOS/` 模块内"——**路径错误**（应为 `docs/AirymaxOS/`）

**评估**：命名一致但闭源文档存在 5 处 `AirymaxAgentOS/` → `AirymaxOS/` 路径错误。

#### 4.1.4 [SC] / [SS] / [IND] 三层模型—— **跨仓库一致**

所有 5 个文档仓库对 IRON-9 v2 三层模型的使用完全一致：
- [SC] = Shared Contract（共享契约层）= `include/airymax/` 6 个头文件
- [SS] = Semantic Same-source（语义同源层）= API 签名同源、实现独立
- [IND] = Independent（完全独立层）= 各自独立演进

唯一不一致点是闭源 agentrt 工程标准手册 v28.0 仍称 [SC] 为 4 个头文件（详见 §3.1.3 失真 1）。

### 4.2 术语表一致性

#### 4.2.1 统一术语表的存在性

| 术语表 | 路径 | 存在性 |
|--------|------|--------|
| Airymax 统一术语表 | `docs/AirymaxRT/TERMINOLOGY.md` | OK |
| AirymaxOS 术语表 | `docs/AirymaxOS/TERMINOLOGY.md` | **缺失**（OpenStandards/README.md:231 引用此路径但文件不存在） |
| 术语子集 | `docs/AirymaxRT/00-requirements/10-terminology.md` | OK |
| 术语子集 | `docs/AirymaxRT/20-modules/10-contracts/06-glossary-index.md` | OK |
| 术语子集 | `docs/AirymaxRT/50-specifications/10-contracts/06-glossary-index.md` | OK（与 20-modules 版本逐字节相同，229 行重复） |

#### 4.2.2 术语表跨仓库一致性

`docs/AirymaxRT/TERMINOLOGY.md:8` 自称"路径: `Docs/TERMINOLOGY.md`"——**路径错误**（实际为 `docs/AirymaxRT/TERMINOLOGY.md`，注意大小写 `Docs/` vs `docs/`）。

`docs/AirymaxRT/TERMINOLOGY.md:604-607` 引用 `00-basic-theories/01-mcis-cn.md` 等 4 个文件——**路径错误**（实际为 `00-requirements/`，v1.0 P0-9 仍存在）。

**评估**：术语表存在但**路径自指错误**和**引用路径错误**同时存在。

### 4.3 引用路径有效性

#### 4.3.1 实测引用路径错误清单（系统性）

实测 5 个文档仓库的引用路径错误，共发现 **5 类系统性问题**：

**P-DQC-1：开源 AirymaxRT 引用 `00-basic-theories/` 不存在目录**

| 文件 | 行号 | 错误引用 | 实际路径 |
|------|------|---------|---------|
| `docs/AirymaxRT/TERMINOLOGY.md` | 604-607 | `00-basic-theories/01-mcis-cn.md` 等 4 文件 | `00-requirements/01-mcis-cn.md` 等 |

**P-DQC-2：开源 AirymaxRT 引用 `30-coding-standard/` 不存在目录**

| 文件 | 行号 | 错误引用 |
|------|------|---------|
| `docs/AirymaxRT/20-modules/10-contracts/01-agent-contract.md` | 814, 815 | `../30-coding-standard/02-c-cpp-secure-coding.md` / `../30-coding-standard/10-log-standard.md` |
| `docs/AirymaxRT/20-modules/10-contracts/03-protocol-contract.md` | 45, 867 | `../30-coding-standard/10-log-standard.md` |
| `docs/AirymaxRT/20-modules/10-contracts/05-logging-format.md` | 952 | `../30-coding-standard/10-log-standard.md` |
| `docs/AirymaxRT/140-application-development/05-config-change-process.md` | 353 | `specifications/30-coding-standard/15-security-design.md` |

实际编码规范在 `docs/AirymaxOS/50-engineering-standards/10-coding-style/`（开源共享符号链接）。

**P-DQC-3：开源 AirymaxRT/README 引用 `08-compliance-checklist.md` 不存在文件**

| 文件 | 行号 | 错误引用 |
|------|------|---------|
| `docs/AirymaxRT/README.md` | 62 | `50-engineering-standards/08-compliance-checklist.md` |
| `docs/AirymaxRT/README_zh.md` | 87 | 同上 |

实测 `docs/AirymaxOS/50-engineering-standards/08-compliance-checklist.md` **不存在**。

**P-DQC-4：开源 AirymaxRT 引用 `70-project-erp/` 不存在目录**

| 文件 | 行号 | 错误引用 |
|------|------|---------|
| `docs/AirymaxRT/20-modules/10-contracts/03-protocol-contract.md` | 685 | `../70-project-erp/02-error-code-reference.md` |

实测 `docs/AirymaxRT/70-project-erp/` **目录不存在**。

**P-DQC-5：开源 AirymaxRT 引用 `DocsClosed/` 不存在目录**

| 文件 | 行号 | 错误引用 |
|------|------|---------|
| `docs/AirymaxRT/30-interfaces/06-ipc/README.md` | 61 | `../../../DocsClosed/0.1.1详细任务清单.md` |

实际目录为 `docs-closed/`（小写），非 `DocsClosed/`。

**P-DQC-6：闭源 agent-linux/README 引用 `docs/AirymaxAgentOS/` 不存在目录**

| 文件 | 行号 | 错误引用 | 实际路径 |
|------|------|---------|---------|
| `docs-closed/agent-linux-dev/README.md` | 18, 66, 71, 124, 125, 126 | `docs/AirymaxAgentOS/` | `docs/AirymaxOS/` |

实测 `docs/AirymaxAgentOS/` **不存在**。

**P-DQC-7：闭源 agent-linux/README 引用 `docs/00-architectural-principles.md` 不存在文件**

| 文件 | 行号 | 错误引用 | 实际路径 |
|------|------|---------|---------|
| `docs-closed/agent-linux-dev/README.md` | 127 | `docs/00-architectural-principles.md` | `docs/AirymaxRT/10-architecture/00-architectural-principles.md` |
| `docs-closed/agent-linux-dev/agent-linux基本工程标准规范.md` | 12 | 同上 | 同上 |

**P-DQC-8：闭源 agent-linux/README 引用 `docs-closed/0.1.1工程标准规范手册.md` 不存在文件**

| 文件 | 行号 | 错误引用 | 实际路径 |
|------|------|---------|---------|
| `docs-closed/agent-linux-dev/README.md` | 128 | `docs-closed/0.1.1工程标准规范手册.md` | `docs-closed/agentrt/agentrt工程标准规范手册.md` |
| `docs-closed/agent-linux-dev/agent-linux基本工程标准规范.md` | 60 | `0.1.1工程标准规范手册.md` | 同上 |

**P-DQC-9：开源 OpenStandards/README 引用 `docs/AirymaxOS/TERMINOLOGY.md` 不存在文件**

| 文件 | 行号 | 错误引用 | 实际路径 |
|------|------|---------|---------|
| `docs/OpenStandards/README.md` | 231 | `docs/AirymaxOS/TERMINOLOGY.md` | `docs/AirymaxRT/TERMINOLOGY.md` |

#### 4.3.2 引用路径错误的影响评估

| 影响维度 | 评估 |
|---------|------|
| 外部开发者体验 | 严重受损——按引用路径查找文件 100% 失败 |
| CI 链接检查 | 无法通过——无 markdown-link-check 配置 |
| SSoT 路径体系 | 混乱——同一文件在闭源和开源中路径表述不一致 |
| 文档可用性 | 5 个仓库全部受影响 |

---

## 5. 文档质量评估矩阵

| 维度 | docs/AirymaxOS | docs/AirymaxRT | docs/OpenStandards | docs-closed/agentrt | docs-closed/agent-linux |
|------|----------------|----------------|--------------------|---------------------|---------------------------|
| **技术准确性** | B+（magic/AGTS/SCHED_EXT/[SC] 6 头文件清单全部正确） | C-（[SC] 头文件清单错误列 bpf_struct_ops.h；错误码 6 套并存） | B+（magic/SCHED_EXT/[SC] 6 头文件清单全部正确；个体标准未跟进 1.1） | D（[SC] 4 头文件错误；代码前缀 agentos_* 全错） | A-（[SC] 6 头文件正确；SCHED_EXT=7 正确；OLK-6.6 术语清洗准确） |
| **上下游关系** | B（与 openEuler/seL4/Linux 6.6 关系准确，但 5 文件含 openEuler 违反 BAN-INTERNAL-002） | B+（与 agent-linux 同源关系准确） | A（与 agentrt/agent-linux 关系清晰） | B（与 agent-linux 同源关系准确，但引用路径错误） | B+（与 openEuler/seL4/Linux 6.6 关系准确，BAN-INTERNAL 规则完整） |
| **抄袭风险** | A（无抄袭，引用规范） | A（MCIS 原创性声明充分） | A（外部引用附 URL） | A（无抄袭） | A（无抄袭） |
| **版本一致性** | B+（v0.1.1 头部与最后更新对齐） | D（README 无版本号；AIRY_EINVAL 多值） | C-（头部 1.0 vs 历史 1.1 矛盾） | D（v28.0 但内部 29→38 残留；前缀全部失真） | B+（v0.2.5 内部一致） |
| **工程指导性** | N/A（开源设计文档） | N/A（开源设计文档） | N/A（开放标准） | C+（38 章+BAN 357 项+ACC 138 项体系完整，但前缀/[SC] 失真削弱指导性） | A-（14 章+5 附录指导性强；M0-M8 里程碑清晰） |
| **引用有效性** | B（少量 openEuler 路径暴露） | D（5 类路径错误：00-basic-theories/30-coding-standard/08-compliance-checklist/70-project-erp/DocsClosed） | B（仅 1 处 TERMINOLOGY.md 路径错误） | B（README 引用相对正确） | D（3 类路径错误：AirymaxAgentOS/00-architectural-principles/0.1.1工程标准规范手册） |
| **综合** | **B** | **C-** | **B-** | **C-** | **B** |

---

## 6. 问题清单（按严重程度排序）

### 6.1 P0 级问题（5 项，阻断 1.0.1 M1 启动）

| # | 问题 | 来源 | 证据 | 工作量 |
|---|------|------|------|--------|
| **P0-DQC-1** | 闭源 agentrt 工程标准手册 [SC] 头文件数量错误（4 vs 6） | 本报告 §3.1.3 失真 1 | `docs-closed/agentrt/agentrt工程标准规范手册.md:21`（声明 4 个）vs `docs-closed/agent-linux-dev/agent-linux基本工程标准规范.md:11`（声明 6 个）+ 源码 `commons/include/airymax/`（实际 6 个） | ~1h |
| **P0-DQC-2** | 闭源 agentrt 工程标准手册代码前缀全部错误（agentos_* vs airy_*） | 本报告 §3.1.3 失真 2 | `docs-closed/agentrt/agentrt工程标准规范手册.md:99-111`（agentos_core_*/agentos_loop_*/AGENTOS_E* 等 7 项）vs v1.0 §5.2（源码 airy_* 916+ 处） | ~4h（手册术语表全量更新） |
| **P0-DQC-3** | 开源 AirymaxRT [SC] 头文件清单仍错误列 bpf_struct_ops.h（v1.0 P0-8 仍存在） | 本报告 §2.2.4 | `docs/AirymaxRT/10-architecture/06-iron9-shared-model.md:64-73`（第 1 项 bpf_struct_ops.h）vs SSoT `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:65-77`（第 6 项 syscalls.h） | ~1h |
| **P0-DQC-4** | 开源 AirymaxRT 错误码 6 套方案仍并存（v1.0 P0-1 仍存在） | 本报告 §2.2.5 | `docs/AirymaxRT/10-architecture/00-architectural-principles.md:923-924`（EINVAL 直接赋值）/ `06-iron9-shared-model.md:214-215`（-22）/ `05-syscall.md:641,644`（1001）/ `03-protocol-contract.md:685`（-1）/ `05-logging-format.md:301`（-2） | ~8h |
| **P0-DQC-5** | 开源 AirymaxRT "操作系统"误称 18 文件未修复（v1.0 P0-5 仍存在） | 本报告 §2.1 实测 | `docs/AirymaxRT/10-architecture/00-architectural-principles.md:54` / `04-microcorert.md:13,19,271` 等 15+ 处 / `00-requirements/04-design-principles-cn.md:14,99` | ~4h |

### 6.2 P1 级问题（9 项，1.0.1 M1 内完成）

| # | 问题 | 来源 | 证据 | 工作量 |
|---|------|------|------|--------|
| **P1-DQC-1** | 引用路径错误 9 类系统性问题（5 仓库全部受影响） | 本报告 §4.3.1 | 详见 P-DQC-1~9 清单 | ~6h |
| **P1-DQC-2** | OpenStandards README 内部版本矛盾（1.0 vs 1.1） | 本报告 §2.4.1 | `docs/OpenStandards/README.md:6,118`（1.0）vs `:245`（1.1） | ~0.5h |
| **P1-DQC-3** | AirymaxRT README 无版本号 | 本报告 §2.4.1 | `docs/AirymaxRT/README.md:8`（仅"最新更新 2026-07-11"，无版本号字段） | ~0.5h |
| **P1-DQC-4** | 闭源 agentrt 手册 29→38 仓变更说明残留 | 本报告 §3.1.3 失真 3 | `docs-closed/agentrt/agentrt工程标准规范手册.md:9`（v26.0 历史 29 仓明细）vs `:4-5`（v28.0 当前 38 仓明细） | ~1h |
| **P1-DQC-5** | 闭源 agent-linux 开发路线仍用 29 仓表述 | 本报告 §3.3.2 | `docs-closed/agent-linux-dev/agent-linux开发路线和进度.md:69`（"29 仓拆分 ~1,800h"） | ~1h |
| **P1-DQC-6** | 开源 AirymaxOS 含 openEuler 提及（与 BAN-INTERNAL-002 冲突） | 本报告 §2.1.1 | `docs/AirymaxOS/README.md:30,163` / `06-directory-structure.md:118,222,234,235` / `50-engineering-standards/README.md:230,231,242` | ~2h（删除或改写为"主流 Linux 发行版"） |
| **P1-DQC-7** | BAN-INTERNAL-002 路径表述错误 | 本报告 §2.1.1 | `docs-closed/agent-linux-dev/README.md:78`（声明 `docs/AirymaxAgentOS/`，实际为 `docs/AirymaxOS/`） | ~0.5h |
| **P1-DQC-8** | 50-specifications/ 与 20-modules/10-contracts/06-glossary-index.md 重复（v1.0 P1-13 仍存在） | 本报告 §4.2.1 | `docs/AirymaxRT/50-specifications/10-contracts/06-glossary-index.md` 与 `docs/AirymaxRT/20-modules/10-contracts/06-glossary-index.md` 均 229 行（逐字节相同） | ~0.5h（删除 50-specifications 版本） |
| **P1-DQC-9** | AirymaxRT daemon 数量 10 vs 12 文内矛盾（v1.0 P1-6 仍存在） | 本报告 §2.2.4 | `docs/AirymaxRT/10-architecture/01-system-architecture.md:305`（10 个）vs `:575`（12 daemons）+ `02-l2-service-protocol.md:255,286,288`（12 个） | ~0.5h |

### 6.3 P2 级问题（5 项，1.0.1 全阶段改进）

| # | 问题 | 证据 | 工作量 |
|---|------|------|--------|
| **P2-DQC-1** | AirymaxRT/06-iron9-shared-model.md 递归注释 | `docs/AirymaxRT/10-architecture/06-iron9-shared-model.md:214`（"/* 成功（替代 AIRY_EOK） */" 自指） | ~0.1h |
| **P2-DQC-2** | TERMINOLOGY.md 路径自指错误 | `docs/AirymaxRT/TERMINOLOGY.md:8`（"路径: `Docs/TERMINOLOGY.md`" 应为 `docs/AirymaxRT/TERMINOLOGY.md`） | ~0.1h |
| **P2-DQC-3** | OpenStandards 7 个主题标准文档未跟进 1.1 版本号 | `docs/OpenStandards/01-airy-agent-runtime-standard.md:6`（1.0）vs README 历史 1.1 | ~0.5h |
| **P2-DQC-4** | 闭源 agentrt 工程标准手册 daemon 数量表述 16 vs 12 | `docs-closed/agentrt/agentrt工程标准规范手册.md:9`（"16 个 daemon"） | ~0.5h |
| **P2-DQC-5** | AirymaxOS/TERMINOLOGY.md 缺失（被 OpenStandards 引用） | `docs/OpenStandards/README.md:231` 引用 `docs/AirymaxOS/TERMINOLOGY.md`，文件不存在 | ~2h（创建或修改引用至 AirymaxRT/TERMINOLOGY.md） |

### 6.4 问题汇总

| 类别 | P0 | P1 | P2 | 合计 |
|------|----|----|----|----|
| 引用路径 | 0 | 1（P1-DQC-1 含 9 子项） | 0 | 1 |
| 技术准确性 | 3（P0-DQC-1/3/4） | 1（P1-DQC-9） | 1（P2-DQC-1） | 5 |
| 一致性 | 1（P0-DQC-2） | 4（P1-DQC-4/5/7/8） | 2（P2-DQC-2/4） | 7 |
| 版本管理 | 0 | 2（P1-DQC-2/3） | 1（P2-DQC-3） | 3 |
| 上下游关系 | 1（P0-DQC-5） | 2（P1-DQC-6/7） | 0 | 3 |
| 文档完整性 | 0 | 0 | 1（P2-DQC-5） | 1 |
| **合计** | **5** | **9** | **5** | **19**（不含与 v1.0 重叠的 P0-1/4/5/8/9 共 5 项） |

**工作量估算**：
- P0 合计：~18h（不含与 v1.0 重叠的方案侧修复）
- P1 合计：~12h
- P2 合计：~3.2h
- **v2.0 文档质量控制维度总工作量**：~33.2h

---

## 7. 修复建议

### 7.1 立即修复（1.0.1 M1 启动前 ~18h）

| # | 修复项 | 操作 | 工作量 |
|---|--------|------|--------|
| 1 | P0-DQC-1 | 修正 `docs-closed/agentrt/agentrt工程标准规范手册.md:21` 的 [SC] 头文件清单：4 个 → 6 个，将 `bpf_struct_ops.h` 标注为"补充共享文件"，新增 `syscalls.h`/`ipc.h`/`sched.h` 为 [SC] 核心 | ~1h |
| 2 | P0-DQC-2 | 全量更新 `docs-closed/agentrt/agentrt工程标准规范手册.md:99-111` 术语强制规范表：`agentos_*` → `airy_*`、`AGENTOS_E*` → `AIRY_E*`、`agentos_sys_*` → `airy_sys_*` | ~4h |
| 3 | P0-DQC-3 | 修正 `docs/AirymaxRT/10-architecture/06-iron9-shared-model.md:64-73`：第 1 项 `bpf_struct_ops.h` → `syscalls.h`，将 `bpf_struct_ops.h` 移至"补充共享文件"小节 | ~1h |
| 4 | P0-DQC-4 | 在 `docs/AirymaxOS/50-engineering-standards/` 建立错误码 SSoT 文档；统一 AirymaxRT 全部 6 套方案为 `airy_err_t`（`int32_t`）+ `AIRY_EOK=0` + 13 个 `AIRY_E*` 宏（负值） | ~8h（与 v1.0 P0-1 重叠） |
| 5 | P0-DQC-5 | 全量替换 AirymaxRT 文档中"操作系统"为"运行时平台"或"运行时"（除真正指代宿主 OS 的上下文），保留 `04-microcorert.md:183` 中正确描述 | ~4h（与 v1.0 P0-5 重叠） |

### 7.2 1.0.1 M1 阶段修复（~12h）

| # | 修复项 | 操作 | 工作量 |
|---|--------|------|--------|
| 1 | P1-DQC-1 | 全量修复 9 类引用路径错误（详见 §4.3.1）；配置 markdown-link-check CI 门禁 | ~6h |
| 2 | P1-DQC-2 | 修正 `docs/OpenStandards/README.md:6,118`：版本号 1.0 → 1.1 | ~0.5h |
| 3 | P1-DQC-3 | 在 `docs/AirymaxRT/README.md` 和 `README_zh.md` 添加"文档版本"字段（建议 0.1.1） | ~0.5h |
| 4 | P1-DQC-4 | 在 `docs-closed/agentrt/agentrt工程标准规范手册.md:9` 添加历史标注"v27.0 已迁移至 38 仓，详见 line 19" | ~1h |
| 5 | P1-DQC-5 | 修正 `docs-closed/agent-linux-dev/agent-linux开发路线和进度.md:69`：29 仓 → 38 仓 | ~1h |
| 6 | P1-DQC-6 | 删除或改写 `docs/AirymaxOS/` 中 9 处 openEuler 提及：替换为"主流 Linux 发行版"或"Linux 6.6 内核基线上游发行版" | ~2h |
| 7 | P1-DQC-7 | 修正 `docs-closed/agent-linux-dev/README.md:78` BAN-INTERNAL-002：`docs/AirymaxAgentOS/` → `docs/AirymaxOS/` | ~0.5h |
| 8 | P1-DQC-8 | 删除 `docs/AirymaxRT/50-specifications/10-contracts/06-glossary-index.md`（保留 `20-modules/10-contracts/06-glossary-index.md` 版本） | ~0.5h |

### 7.3 1.0.1 全阶段改进（~3.2h）

| # | 修复项 | 操作 | 工作量 |
|---|--------|------|--------|
| 1 | P2-DQC-1 | 修正 `docs/AirymaxRT/10-architecture/06-iron9-shared-model.md:214` 递归注释 | ~0.1h |
| 2 | P2-DQC-2 | 修正 `docs/AirymaxRT/TERMINOLOGY.md:8` 路径自指：`Docs/TERMINOLOGY.md` → `docs/AirymaxRT/TERMINOLOGY.md` | ~0.1h |
| 3 | P2-DQC-3 | OpenStandards 7 个主题标准文档版本号统一更新至 1.1 | ~0.5h |
| 4 | P2-DQC-4 | 修正 `docs-closed/agentrt/agentrt工程标准规范手册.md:9`：16 个 daemon → 12 个 daemon | ~0.5h |
| 5 | P2-DQC-5 | 创建 `docs/AirymaxOS/TERMINOLOGY.md`（或修改 `docs/OpenStandards/README.md:231` 引用至 `docs/AirymaxRT/TERMINOLOGY.md`） | ~2h |

### 7.4 长期改进建议

1. **建立 CI 文档链接检查器**：配置 markdown-link-check + lychee 等工具，在 PR 合并前自动校验所有 markdown 链接有效性，防止 P-DQC-1~9 类路径错误再次发生。
2. **建立术语表 SSoT 单一数据源**：将 `docs/AirymaxRT/TERMINOLOGY.md` 提升为 Airymax 全项目术语 SSoT，所有其他文档（含闭源）通过引用而非复制使用术语定义。
3. **建立版本号管理规范**：明确"文档版本"（如 v0.1.1）与"适用代码版本"（如 AgentRT v0.1.1）的区分；明确开源文档与闭源文档的版本对齐机制。
4. **闭源 agentrt 工程标准手册全面校订**：v28.0 手册存在 [SC] 头文件数量错误、代码前缀全部错误、daemon 数量表述错误 3 类系统性事实性失真，建议在 1.0.1 M1 启动前进行全面校订，确保与实际源码、闭源 agent-linux 总纲、开源文档三方对齐。
5. **建立文档评审 SLA**：每次源码重大变更（如 agentos_→airy_ 改名）后，必须在 1 个工作日内同步更新闭源工程标准手册，避免出现 v28.0 手册描述 v25.0 时代状态的失真。

### 7.5 关键决策点（需要用户裁决）

| # | 决策点 | 选项 | 推荐 |
|---|--------|------|------|
| 1 | openEuler 在开源文档中的处理 | A：完全删除（最严格）/ B：保留为"上游发行版"模糊表述 / C：仅在路径引用中保留（如 `01Reference/kernel-OLK-6.6`） | **B**（保留技术参考价值但避免暴露具体上游） |
| 2 | 闭源 agentrt 工程标准手册代码前缀更新方向 | A：仅更新术语表 / B：全量更新所有代码示例和引用 / C：废弃 v28.0 重写 v29.0 | **B**（全量更新确保事实性） |
| 3 | AirymaxOS/TERMINOLOGY.md 处理 | A：创建文件（复制 AirymaxRT 版本）/ B：修改 OpenStandards 引用至 AirymaxRT 版本 | **B**（避免术语表重复） |
| 4 | 50-specifications/ 目录处理 | A：删除（保留 20-modules 版本）/ B：重新定位为规范规格书目录 | **A**（避免重复） |
| 5 | 闭源 agentrt 手册 29→38 仓历史说明 | A：删除 v26.0 历史 / B：保留历史但明示"已迁移至 38 仓" | **B**（保留变更追溯） |

---

## 附录 A：审查文件清单

### A.1 必读参考文件（3 份）

| 文件 | 路径 | 用途 |
|------|------|------|
| v1.0 综合分析 | `docs-closed/agentrt/_review_v1.0/00-comprehensive-analysis.md` | 了解上一轮发现 |
| OpenStandards README | `docs/OpenStandards/README.md` | 开源开放标准示例 |
| AirymaxOS README | `docs/AirymaxOS/README.md` | 开源 OS 设计文档示例 |

### A.2 实际审查文件（20+ 份）

**开源 docs/**：
- `docs/AirymaxOS/README.md`
- `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md`
- `docs/AirymaxOS/50-engineering-standards/README.md`
- `docs/AirymaxOS/10-architecture/06-directory-structure.md`
- `docs/AirymaxOS/30-interfaces/01-syscalls.md` / `02-ipc-protocol.md` / `05-syscall-semantic-mapping.md`
- `docs/AirymaxRT/README.md` / `README_zh.md` / `TERMINOLOGY.md`
- `docs/AirymaxRT/10-architecture/06-iron9-shared-model.md` / `00-architectural-principles.md` / `04-microcorert.md` / `05-syscall.md`
- `docs/AirymaxRT/00-requirements/04-design-principles-cn.md`
- `docs/AirymaxRT/30-interfaces/06-ipc/README.md`
- `docs/AirymaxRT/20-modules/10-contracts/03-protocol-contract.md` / `05-logging-format.md`
- `docs/OpenStandards/README.md` / `01-airy-agent-runtime-standard.md` / `02-airy-ipc-protocol-standard.md` / `06-airy-scheduling-standard.md` / `07-airy-syscall-standard.md`

**闭源 docs-closed/**：
- `docs-closed/agentrt/README.md`
- `docs-closed/agentrt/agentrt工程标准规范手册.md`
- `docs-closed/agent-linux-dev/README.md`
- `docs-closed/agent-linux-dev/agent-linux基本工程标准规范.md`
- `docs-closed/agent-linux-dev/agent-linux开发路线和进度.md`
- `docs-closed/agentrt/_review_v1.0/00-comprehensive-analysis.md`

### A.3 Grep 机器检查项

| 检查项 | 模式 | 范围 |
|--------|------|------|
| IPC magic 一致性 | `0x41524531\|ARE1\|AIRY_IPC_MAGIC` | docs/ |
| AGTS magic 一致性 | `0x41475453\|AGTS\|AIRY_TASK_MAGIC` | docs/ |
| SCHED_EXT 一致性 | `SCHED_EXT\|SCHED_AGENT\|sched_ext` | docs/ |
| openEuler 泄露 | `openEuler\|open Euler\|openeuler` | docs/ |
| 操作系统误称 | `操作系统` | docs/AirymaxRT/ |
| 错误码变体 | `AIRY_EOK\|AIRY_OK\|ARE_OK\|AIRY_EINVAL` | docs/AirymaxRT/ |
| daemon 数量 | `10 个核心\|12 个核心\|10 个 daemon\|12 个 daemon` | docs/AirymaxRT/ |
| 仓库总数 | `38 仓\|29 仓\|38 个 git\|29 个` | docs-closed/ |
| 路径有效性 | `ls -e` 实测 | docs/ + docs-closed/ |

---

## 附录 B：术语对照

| 术语 | 定义 |
|------|------|
| 文档侧可开发状态 | 文档技术内核准确、引用路径有效、版本号一致、闭源手册与源码对齐，可指导 1.0.1 M1 代码开发 |
| BAN-INTERNAL-002 | 闭源 `docs-closed/agent-linux-dev/README.md:78` 定义的禁词规则，禁止开源文档出现 openEuler 描述 |
| IRON-9 v2 | agentrt 三层模型（[SC] 共享契约层 / [SS] 语义同源层 / [IND] 完全独立层） |
| SSoT | Single Source of Truth（单一真值源） |
| [SC] | Shared Contract（共享契约层），落地于 `include/airymax/` 6 个头文件 |
| OLK-6.6 | openEuler OLK-6.6 内核分支（Linux 6.6 内核基线的上游发行版实现） |
| 微核心（micro-core） | agentrt 定位（用户态运行时） |
| 微内核（micro-kernel） | agent-linux 定位（OS 发行版内核极简化形态） |
| MCIS | 多体控制论智能系统（Airymax 原创理论框架） |
| DQC | Document Quality Control（文档质量控制，本报告维度代号） |

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>

---

**报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-13 | 审查版本：v2.0 | 维度：文档规范与质量控制
