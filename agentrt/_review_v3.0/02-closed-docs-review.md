Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# Airymax agentrt 闭源文档 v3.0 全面复审报告

> **文档定位**：v3.0 对 `docs-closed/agentrt/` 闭源文档的全面复审，覆盖 v2.0 修正持久性独立复核、v2.0 延期项验证、v3.0 新发现问题、§11.6 历史改名章节专项审查，作为 1.0.1 M1 启动前闭源文档侧的最终判定基线之一。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：3.0（2026-07-14）。
> **审查范围**：仅 `docs-closed/agentrt/`（不含 `docs-closed/agentrt-linux/`、`docs/`、源码）。
> **审查方法**：v2.0 三份历史报告精读 + Grep 机器检查 + 与开源 SSoT 交叉对照 + 全文系统性扫描。
> **证据要求**：所有结论附 `文件路径:L行号`，可通过 Read/Grep 工具复核。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. v2.0 修正持久性验证矩阵](#2-v20-修正持久性验证矩阵)
- [3. v2.0 延期项验证与评估](#3-v20-延期项验证与评估)
- [4. v3.0 新发现问题清单](#4-v30-新发现问题清单)
- [5. §11.6 历史改名章节专项审查](#5-116-历史改名章节专项审查)
- [6. 修正后综合评分变化](#6-修正后综合评分变化)
- [7. 修正建议](#7-修正建议)
- [附录 A：审查文件清单](#附录-a审查文件清单)
- [附录 B：Grep 机器验证矩阵](#附录-bgrep-机器验证矩阵)

---

## 1. 执行摘要

### 1.1 审查目标与边界

本报告是 agentrt 闭源文档 v3.0 全面复审，**聚焦于**：

1. **v2.0 修正持久性独立复核**：验证 P0-DQC-1（[SC] 头文件 4→6）和 P0-DQC-2（代码前缀 agentos_*→airy_*）两项闭源手册 P0 修正是否仍持久，旧的错误表述是否 0 残留。
2. **v2.0 延期项验证与评估**：对 v2.0 验证报告 §9.1 列出的 3 项闭源文档相关延期项（P1-DQC-4 仓变更残留、P2-DQC-4 daemon 16 vs 12、§11.6 agentrt_* 改名目标）进行当前状态验证与 0.1.1 范围内可处理性评估。
3. **v3.0 新发现问题发现**：对 `docs-closed/agentrt/` 下所有文件进行系统性扫描，重点检查手册全文一致性、与开源 SSoT 对齐性、07-subsystem-specs/ 与 06-contracts/ 等其他文件的前缀一致性。
4. **§11.6 历史改名章节专项审查**：评估 P0-DQC-2 全量替换副作用导致的 §11.6 章节语义变化。

**审查边界**：仅 `docs-closed/agentrt/`（不审查 `docs-closed/agentrt-linux/`、`docs/`、源码）。

### 1.2 综合评分

| 评分维度 | v2.0 修正后 | v3.0 复审后 | 变化 | 主要原因 |
|---------|------------|------------|------|---------|
| 技术准确性 | B+ | **C** | -2 | IPC 消息头 `are_ipc_message_header_t` 三重违规残留；错误码类型名 `airy_error_t` 与 SSoT `airy_err_t` 不一致；错误码分段 9 vs 11 |
| 工程指导性 | B+ | **C-** | -3 | 07-subsystem-specs/ 10 文件 302 处 + 06-contracts/ 3 文件 38 处 `agentos_*` 残留，严重误导开发者 |
| 一致性（与开源 SSoT） | B+ | **C** | -2 | IPC 头/错误码类型名/分段/目录路径/`docs/AirymaxAgentOS/` 路径多处不一致 |
| 修正持久性 | A | **A** | 0 | P0-DQC-1/P0-DQC-2 修正仍持久（仅手册正文） |
| **闭源文档总评** | **78/B+** | **66/C+** | **-12** | v2.0 修正范围盲区（07-subsystem-specs/、06-contracts/）暴露 340 处 `agentos_*` 残留 |

### 1.3 核心结论

> **v2.0 P0-DQC-1/P0-DQC-2 修正仅作用于 `agentrt工程标准规范手册.md` 1 个文件，修正持久性良好（0 残留）**；但 v3.0 系统性扫描发现 **v2.0 修正范围存在重大盲区**：
>
> 1. **`07-subsystem-specs/` 10 个文件共 302 处 `agentos_*` 前缀残留**（仅 02-corekern.md 和 10-openlab.md 已用 `airy_*`/无前缀），与已修正的手册正文术语表（`airy_*`）和开源 SSoT（`airy_*`）严重背离。开发者按这些子系统规格文档编写代码将使用错误前缀，CI 门禁直接失败。
> 2. **`06-contracts/` 3 个文件共 38 处 `agentos_*` 前缀残留**（contract_A_B.h / contract_A_C.h / contract_test.c），合约头文件作为模块间接口契约，前缀错误将直接破坏编译。
> 3. **闭源手册 §34.2 IPC 消息头仍使用 `are_ipc_message_header_t`**（typedef + uint32_t/uint16_t/uint64_t + 13 字段 + 无 packed + 无 _Static_assert），与开源 SSoT `struct airy_ipc_msg_hdr`（无 typedef + __u32/__u16/__u64/__u8 + 8 字段 + packed + _Static_assert）三重违规残留，是 v2.0 开源 P0-4 修正未同步到闭源手册。
> 4. **闭源手册错误码类型名 `airy_error_t`（6 处）与开源 SSoT `airy_err_t` 不一致**，且与同目录 07-subsystem-specs/02-corekern.md（用 `airy_err_t`）内部矛盾。
>
> **1.0.1 M1 启动判定**：闭源文档侧 **未达到"可开发"状态**。07-subsystem-specs/ 和 06-contracts/ 的 340 处 `agentos_*` 残留是阻断项，必须在 M1 启动前完成同步修正。

### 1.4 与 v2.0 验证报告的关系

v2.0 验证报告（`fix-verification-report.md`）§8.1 给出"文档质量（闭源）78/B+"评分，**该评分仅基于 `agentrt工程标准规范手册.md` 1 个文件的 P0-DQC-1/P0-DQC-2 修正**，未覆盖 `docs-closed/agentrt/` 下其他文件（07-subsystem-specs/、06-contracts/ 等）。v3.0 复审扩大审查范围至全目录，发现 v2.0 修正范围的盲区，导致评分下调。

---

## 2. v2.0 修正持久性验证矩阵

### 2.1 验证方法

对 v2.0 修正日志（`fix-log-p0-closed-docs.md`）声明的 7 项验证项，使用 Grep 机器检查独立复核当前状态（截至 2026-07-14）。

### 2.2 验证矩阵

| # | 验证项 | Grep 模式 | 期望结果 | 实际结果 | 状态 | 证据 |
|---|--------|----------|---------|---------|------|------|
| 1 | 闭源手册 `agentos_` 零残留 | `agentos_` | 0 | **0** | ✅ 持久 | `agentrt工程标准规范手册.md` Grep count=0 |
| 2 | 闭源手册 `AGENTOS_` 零残留 | `AGENTOS_` | 0 | **0** | ✅ 持久 | `agentrt工程标准规范手册.md` Grep count=0 |
| 3 | [SC] 6 头文件清单 | `6 个头文件完全共享` | 3（line 21/3675/4343） | **3** | ✅ 持久 | line 21/3675/4343 |
| 4 | 旧的"4 个"消除 | `4 个头文件完全共享` | 0 | **0** | ✅ 持久 | Grep: No matches found |
| 5 | 术语表 `airy_sys_*` 正确 | `airy_sys_\*` | line 106 | **line 106** | ✅ 持久 | `agentrt工程标准规范手册.md:106` |
| 6 | 术语表 `AIRY_E*` 正确 | `AIRY_E\*` | line 111 | **line 111** | ✅ 持久 | `agentrt工程标准规范手册.md:111` |
| 7 | 术语表 7 项 `airy_*`/`airy_sys_*` + 1 项 `AIRY_E*` | 逐行核对 lines 98-111 | 7+1 | **7+1** | ✅ 持久 | lines 98/99/100/103/105/106/109 为 `airy_*`/`airy_sys_*`，line 111 为 `AIRY_E*` |

### 2.3 验证结论

> **v2.0 P0-DQC-1 和 P0-DQC-2 修正持久性验证全部通过**：7/7 项 Grep 机器检查通过。`agentrt工程标准规范手册.md` 中 `agentos_`/`AGENTOS_` 0 残留，[SC] 头文件清单 3 处全部为"6 个头文件完全共享"，术语表 lines 98-111 为 7 项 `airy_*`/`airy_sys_*` + 1 项 `AIRY_E*`。
>
> **重要限定**：本验证仅覆盖 `agentrt工程标准规范手册.md` 1 个文件（v2.0 修正范围）。v3.0 发现 `docs-closed/agentrt/` 下其他文件（07-subsystem-specs/、06-contracts/）未纳入 v2.0 修正范围，存在大量 `agentos_*` 残留（详见 §4）。

---

## 3. v2.0 延期项验证与评估

### 3.1 P1-DQC-4：闭源手册 29→38 仓变更说明残留

**当前状态**：⚠️ **仍残留**

**证据**：

| 位置 | 内容 | 版本归属 |
|------|------|---------|
| `agentrt工程标准规范手册.md:4` | "适用版本: AgentRT v0.1.1（三大支柱：奠基 + **38 仓拆分** + 生产就绪）" | v28.0 当前 |
| `agentrt工程标准规范手册.md:5` | "适用范围: Airymax 全项目 **38 个 git 仓库**（伞仓 airymaxhub + 5 管理仓 agentrt/agentrt-linux/sdk/ecosystem/products + 29 叶子仓 + 3 顶层仓 devtools/docs/docs-closed）" | v28.0 当前 |
| `agentrt工程标准规范手册.md:9` | "v4.0 用户确立 0.1.1 目标扩展为**'奠基 + **29 仓拆分** + 生产就绪'三大支柱**...29 仓 git 拆分：1 伞仓 + 4 管理仓 + 21 叶子仓 + 3 顶层仓" | v26.0 历史 |
| `agentrt工程标准规范手册.md:19` | "仓库总数变更: 29 仓 → **38 仓**（+9）。1 伞仓 + 5 管理仓 + 29 叶子仓 + 3 顶层仓。" | v27.0 变动说明 |

**问题**：line 9（v26.0 历史 29 仓明细：1+4+21+3=29）与 line 4-5（v28.0 当前 38 仓明细：1+5+29+3=38）并列出现，读者易混淆。line 19 已明示"29 仓 → 38 仓（+9）"变更，但 line 9 的 v26.0 历史 29 仓明细未添加"已迁移至 38 仓"标注。

**0.1.1 可处理性评估**：✅ **可在 0.1.1 范围内处理**

**修正建议**：在 line 9 的 v26.0 变动说明末尾添加历史标注："（注：v27.0 已迁移至 38 仓，详见 line 19；本条为 v26.0 历史记录）"。保留历史追溯，避免读者混淆。工作量 ~0.2h。

### 3.2 P2-DQC-4：闭源手册 daemon 数量 16 vs 12

**当前状态**：⚠️ **仍残留**

**证据**：

| 位置 | 内容 | 上下文 |
|------|------|--------|
| `agentrt工程标准规范手册.md:40` | "v0.1.1 的核心任务不是'新建模块'，而是将已有 **16 个 daemon** 和 atoms 子系统完成端到端连接" | §1.1 核心哲学（v0.1.0 时代残留） |
| `agentrt工程标准规范手册.md:3377` | "**12 个 daemons** 命名空间" | §34.4 JSON-RPC 方法命名空间 |
| `agentrt工程标准规范手册.md:4173` | "`bin/`: **12 个 daemon** 进程二进制（gateway_d、llm_d、tool_d、sched_d、market_d、monit_d、channel_d、info_d、notify_d、observe_d、hook_d、plugin_d）" | §37.3 PROD-03 包内必含 |
| `agentrt工程标准规范手册.md:4364` | "用户态系统服务（VFS + 网络 + 驱动 + **12 daemons** + systemd）" | §38.3 AirymaxOS 8 子仓 |
| `agentrt工程标准规范手册.md:4383` | "**12 daemons** 用户态进程" | §38.4 同源天然适配 |

**对比开源 SSoT**：`docs/AirymaxRT/10-architecture/01-system-architecture.md:305`（"12 个核心用户态服务"）、`:575`（"Team A (12 daemons)"）—— 开源一致为 12 个。

**问题**：line 40 的"16 个 daemon"是 v0.1.0 时代残留，与 line 3377/4173/4364/4383 的"12 个 daemon"形成内部矛盾，与开源 SSoT（12 个）不一致。

**0.1.1 可处理性评估**：✅ **可在 0.1.1 范围内处理**

**修正建议**：将 line 40 的"16 个 daemon"修正为"12 个 daemon"。工作量 ~0.1h。

### 3.3 §11.6 agentrt_* 作为改名目标（v2.0 验证报告 §9.1 第 9 项）

**当前状态**：⚠️ **仍残留**（详见 §5 专项审查）

**证据**：

| 位置 | 内容 | 问题 |
|------|------|------|
| `agentrt工程标准规范手册.md:1509` | "### 11.6 **airy_ → agentrt_** 彻底改名规范（v26.0 重写）" | 改名目标为 `agentrt_` |
| `agentrt工程标准规范手册.md:1511` | "`airy_` → **`agentrt_`** 彻底改名" | 改名目标为 `agentrt_` |
| `agentrt工程标准规范手册.md:1521` | "L5 C 公开 ABI: `airy_error_t`、`airy_syscalls_init()` 等 → `agentrt_error_t`、`agentrt_syscalls_init()`" | 改名目标为 `agentrt_*` |
| `agentrt工程标准规范手册.md:1522` | "L6 C 宏: `AIRY_API`、`AIRY_VERSION` → `AGENTRT_API`、`AGENTRT_VERSION`" | 改名目标为 `AGENTRT_*` |

**实际源码**（依据 v1.0 §5.2 + v2.0 §3.1.3 失真 2）：源码使用 `airy_*`/`AIRY_*`（atoms 916+ 处），**未使用 `agentrt_*`/`AGENTRT_*`**。

**0.1.1 可处理性评估**：✅ **可在 0.1.1 范围内处理**（但需决策修正方向）

**修正建议**：详见 §5 专项审查。

---

## 4. v3.0 新发现问题清单

### 4.1 P0 级问题（4 项，阻断 1.0.1 M1 启动）

#### P0-V3-1：07-subsystem-specs/ 10 文件 302 处 `agentos_*` 前缀残留（未同步 P0-DQC-2）

**问题描述**：v2.0 P0-DQC-2 修正仅作用于 `agentrt工程标准规范手册.md` 1 个文件，`07-subsystem-specs/` 下 10 个子系统规格文件未纳入修正范围，仍使用已废弃的 `agentos_*` 前缀和 `AGENTOS_*` 宏前缀，与已修正的手册正文术语表（`airy_*`）和开源 SSoT（`airy_*`）严重背离。

**证据**（Grep `agentos_` count，按文件）：

| 文件 | `agentos_` 残留数 | 典型行号 |
|------|------------------|---------|
| `07-subsystem-specs/03-coreloopthree.md` | **166** | line 73-83: `AGENTOS_API agentos_error_t agentos_loop_create(const agentos_loop_config_t *manager, agentos_core_loop_t **out_loop)` 等 |
| `07-subsystem-specs/05-gateway-d.md` | **42** | — |
| `07-subsystem-specs/09-memory.md` | **35** | line 4: `agentos/commons/utils/memory/`；line 43: `agentos_memory.h`；line 93-97: `agentos_arena_t *arena_create(...)` |
| `07-subsystem-specs/06-llm-d.md` | **21** | line 107-117: `agentos_error_t llm_service_adapter_create(agentos_service_t *out_service, const agentos_svc_config_t *config)` 等 |
| `07-subsystem-specs/12-tool-d.md` | **20** | — |
| `07-subsystem-specs/08-market-d.md` | **10** | — |
| `07-subsystem-specs/04-cupolas.md` | **3** | — |
| `07-subsystem-specs/01-checkpoint.md` | **2** | — |
| `07-subsystem-specs/11-orchestrator.md` | **2** | line 4: `agentos/daemon/common/`；line 198: `agentos_common` |
| `07-subsystem-specs/07-manager.md` | **1** | line 53: `agentos_root` |
| **合计** | **302** | — |

**对比已修正文件**：
- `07-subsystem-specs/02-corekern.md`：`agentos_` 残留 0 处，已使用 `airy_err_t`/`airy_core_init`/`airy_mem_alloc` 等 `airy_*` 前缀（line 62-84），与开源 SSoT 一致。
- `07-subsystem-specs/10-openlab.md`：`agentos_` 残留 0 处（纯描述性文档，无代码前缀）。

**影响**：开发者按 03-coreloopthree.md/05-gateway-d.md/09-memory.md 等子系统规格文档编写代码，将使用 `agentos_loop_create`/`agentos_error_t`/`agentos_arena_t` 等错误前缀，CI 门禁直接失败（源码已全面使用 `airy_*`）。这是 07-subsystem-specs/ 内部不一致（02-corekern.md 已修正 vs 其他 10 文件未修正）+ 与手册正文/开源 SSoT 不一致的双重失真。

**工作量**：~6h（10 文件全量替换 `agentos_` → `airy_`、`AGENTOS_` → `AIRY_`，并逐项核对类型名）。

#### P0-V3-2：06-contracts/ 3 文件 38 处 `agentos_*` 前缀残留（未同步 P0-DQC-2）

**问题描述**：`06-contracts/` 下 3 个合约文件（contract_A_B.h / contract_A_C.h / contract_test.c）未纳入 v2.0 P0-DQC-2 修正范围，仍使用 `agentos_*` 前缀。合约头文件作为模块间接口契约，前缀错误将直接破坏编译。

**证据**（Grep `agentos_` count）：

| 文件 | `agentos_` 残留数 | 典型行号 |
|------|------------------|---------|
| `06-contracts/contract_A_C.h` | **17** | line 124: `命名规范：agentos_<daemon>_<metric>_<unit>`；line 131: `#define CONTRACT_AC_METRIC_PREFIX "agentos_"`；line 148-154: `agentos_requests_total`/`agentos_request_duration_seconds`/`agentos_errors_total` 等 |
| `06-contracts/contract_test.c` | **17** | — |
| `06-contracts/contract_A_B.h` | **4** | — |
| **合计** | **38** | — |

**影响**：合约头文件定义的指标前缀 `agentos_` 与源码实际使用的 `airy_` 不一致， Prometheus 指标采集将失败。

**工作量**：~1h（3 文件全量替换）。

#### P0-V3-3：闭源手册 IPC 消息头 `are_ipc_message_header_t` 三重违规残留

**问题描述**：闭源手册 §34.2 STD-02（line 3328-3356）仍使用 `are_ipc_message_header_t`（typedef 命名 + `uint32_t/uint16_t/uint64_t` 类型 + 13 字段 + 无 `__attribute__((packed))` + 无 `_Static_assert`），与开源 SSoT `struct airy_ipc_msg_hdr`（无 typedef + `__u32/__u16/__u64/__u8` UAPI 类型 + 8 字段 + `__attribute__((packed))` + `_Static_assert(sizeof(...) == 128)`）三重违规残留。

这是 v2.0 开源 P0-4（IPC 消息头三重违规）修正未同步到闭源手册的对应问题。v2.0 修正了开源 `docs/AirymaxRT/30-interfaces/06-ipc/README.md`（line 26-67），但闭源手册 §34.2 未同步修正。

**证据**：

| 维度 | 闭源手册（§34.2） | 开源 SSoT（06-ipc/README.md） | 一致性 |
|------|------------------|------------------------------|--------|
| 命名 | `are_ipc_message_header_t`（typedef，line 3330/3349） | `struct airy_ipc_msg_hdr`（无 typedef，line 53） | ✗ 不一致 |
| 类型 | `uint32_t/uint16_t/uint64_t`（line 3335-3348） | `__u32/__u16/__u64/__u8`（UAPI，line 54-62） | ✗ 不一致 |
| 字段数 | 13 字段（magic/version/msg_type/protocol/msg_id/trace_id/correlation_id/source/target/payload_len/flags/timestamp_ns/checksum/reserved，line 3335-3348） | 8 字段（magic/opcode/flags/trace_id/timestamp_ns/src_task/dst_task/payload_len/reserved[84]，line 54-62） | ✗ 不一致 |
| 布局 | 无 `__attribute__((packed))`（line 3349） | `__attribute__((packed))`（line 63） | ✗ 不一致 |
| 大小验证 | 无 `_Static_assert`（仅有 `sizeof(...) == 128` 文字说明，line 3353） | `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128, ...)`（line 65-66） | ✗ 不一致 |
| 残留位置 | line 2901/3330/3334/3349/3353（共 4 处 `are_ipc_message_header_t`） | 开源已修正为 `airy_ipc_msg_hdr` | — |

**影响**：开发者按闭源手册 §34.2 实现的 IPC 消息头将与源码 `commons/include/airymax/ipc.h` 不兼容（字段数/类型/布局均不一致），破坏 [SC] 共享契约层。

**工作量**：~2h（§34.2 全节重写，对齐开源 SSoT `struct airy_ipc_msg_hdr`）。

#### P0-V3-4：闭源手册错误码类型名 `airy_error_t` 与开源 SSoT `airy_err_t` 不一致

**问题描述**：闭源手册正文使用 `airy_error_t` 作为错误码类型名（6 处），与开源 SSoT `airy_err_t`（无 `error`）不一致，且与同目录 `07-subsystem-specs/02-corekern.md`（已用 `airy_err_t`）内部矛盾。

**证据**：

| 位置 | 闭源手册内容 | 开源 SSoT 内容 | 一致性 |
|------|------------|--------------|--------|
| `agentrt工程标准规范手册.md:251` | "所有错误码必须在 `airy_types.h` 的 **`airy_error_t`** 中注册" | `airy_err_t`（`00-architectural-principles.md:925`） | ✗ |
| `agentrt工程标准规范手册.md:507` | "**`airy_error_t`** process_task(task_t *task)" | `airy_err_t`（`01-system-architecture.md` 多处） | ✗ |
| `agentrt工程标准规范手册.md:535` | "**`airy_error_t`** safe_handler(void)" | 同上 | ✗ |
| `agentrt工程标准规范手册.md:764` | "返回值优先使用 **`airy_error_t`**（int32_t）" | `airy_err_t`（`int32_t`） | ✗ |
| `agentrt工程标准规范手册.md:787` | "**`airy_error_t`** err" | `airy_err_t err`（`00-architectural-principles.md:963`） | ✗ |
| `agentrt工程标准规范手册.md:1521` | "L5 C 公开 ABI: **`airy_error_t`** → `agentrt_error_t`" | `airy_err_t`（无改名） | ✗ |
| `07-subsystem-specs/02-corekern.md:62/74/79/84` | **`airy_err_t`**（与开源一致） | `airy_err_t` | ✅ |

**开源 SSoT 权威定义**：
- `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:73`："`airy_err_t` = `int32_t`（定义于 `cognition_types.h` [SC] 第 3 号头文件）"
- `docs/AirymaxRT/10-architecture/00-architectural-principles.md:925`："`typedef int32_t airy_err_t;`"

**影响**：闭源手册正文使用 `airy_error_t`，开发者按手册编写代码将使用错误类型名，与 [SC] 头文件 `cognition_types.h` 定义的 `airy_err_t` 不一致，编译失败。同时闭源手册正文与同目录 02-corekern.md 内部矛盾。

**工作量**：~0.5h（6 处 `airy_error_t` → `airy_err_t`）。

### 4.2 P1 级问题（6 项，1.0.1 M1 内完成）

#### P1-V3-1：闭源手册 `docs/AirymaxAgentOS/` 路径错误 7 处

**问题描述**：闭源手册 7 处引用 `docs/AirymaxAgentOS/`，实际路径为 `docs/AirymaxOS/`（v2.0 报告 §4.1.3 已指出但未修正）。

**证据**：

| 位置 | 内容 |
|------|------|
| `agentrt工程标准规范手册.md:20` | "OS 设计文档全部在 `docs/AirymaxAgentOS/` 模块内" |
| `agentrt工程标准规范手册.md:2232` | "BAN-358 禁止 OS 设计文档放置在 docs-closed/（必须放置在 `docs/AirymaxAgentOS/`）" |
| `agentrt工程标准规范手册.md:4327` | "OS 详细设计文档全部在 `docs/AirymaxAgentOS/` 模块内" |
| `agentrt工程标准规范手册.md:4341` | "文档位置: docs-closed/ \| `docs/AirymaxAgentOS/`" |
| `agentrt工程标准规范手册.md:4398` | "文档: docs.openeuler.org \| `docs/AirymaxAgentOS/`" |
| `agentrt工程标准规范手册.md:4421` | "OS 设计文档: `docs/AirymaxAgentOS/`（docs 顶层仓下子目录，12 个文档）" |
| `agentrt工程标准规范手册.md:4442` | "BAN-358 禁止 OS 设计文档放置在 docs-closed/（必须放置在 `docs/AirymaxAgentOS/`）" |

**工作量**：~0.3h（7 处 `docs/AirymaxAgentOS/` → `docs/AirymaxOS/`）。

#### P1-V3-2：闭源手册 `agentos/` 目录路径残留 60+ 处

**问题描述**：闭源手册正文广泛使用 `agentos/` 目录路径（带斜杠，非代码前缀），与 §11.6.1 L1 描述的 `agentos/` → `agentrt/` 改名矛盾，与实际源码目录（`agentrt/`）不一致。P0-DQC-2 全量替换仅针对 `agentos_`（带下划线），未涉及 `agentos/`（带斜杠）。

**证据**（典型位置，Grep `agentos/` 共 60+ 处）：

| 位置 | 内容 | 应为 |
|------|------|------|
| `:83` | `agentos/atoms/`、`agentos/cupolas/`、`agentos/daemons/` | `agentrt/atoms/` 等 |
| `:84` | `agentos/gateway/`、`agentos/heapstore/`、`agentos/protocols/` | `agentrt/gateway/` 等 |
| `:2058-2060` | 团队三权分立代码范围 `agentos/atoms/` 等 | `agentrt/atoms/` 等 |
| `:2712` | `agentos/commons/utils/print/include/airy_print.h` | `agentrt/commons/...` |
| `:2866` | `/var/log/agentos/agentos.log` | `/var/log/agentrt/agentrt.log` |
| `:3019-3025` | 许可证表 `AgentRT/agentos/atoms/` 等 7 处 | `AgentRT/agentrt/atoms/` 等 |
| `:3371` | `agentos.yaml` 配置文件名 | `agentrt.yaml` |
| `:3384` | `AgentRT/agentos/daemons/` | `AgentRT/agentrt/daemons/` |
| `:3390` | `agentos/commons/utils/error/include/error.h`（错误码权威源路径） | `include/airymax/error.h`（[SC] 共享头文件） |
| `:3461-3465` | `agentos/daemons/observability_d/` 等 | `agentrt/daemons/...` |

**影响**：开发者按手册路径引用源码将找不到文件；错误码权威源路径 `agentos/commons/utils/error/include/error.h` 与开源 SSoT `include/airymax/error.h` 不一致。

**工作量**：~3h（60+ 处逐项核对，区分目录路径 vs 历史记录）。

#### P1-V3-3：闭源手册 §34.5 错误码分段与开源 SSoT 不一致

**问题描述**：闭源手册 §34.5 STD-05（line 3386-3405）的错误码分段（9 段）与开源 SSoT（11 段，含 i18n/发行版）不一致，权威源路径用旧 `agentos/` 路径。

**证据**：

| 维度 | 闭源手册（§34.5） | 开源 SSoT | 一致性 |
|------|------------------|----------|--------|
| 分段数 | 9 段（通用/系统/内核/服务/LLM/执行/记忆/安全/协议，line 3393-3403） | 11 段（通用/系统/内核/服务/LLM/执行/记忆/安全/协议/**i18n/发行版**，`120-cross-project-code-sharing.md:81`） | ✗ 缺 i18n/发行版 |
| 分段范围 | 通用 -1~-99 / 系统 -100~-199 / ... / 协议 -800~-899 | POSIX errno 负值（如 `AIRY_EINVAL=(-22)`、`AIRY_ENOMEM=(-12)`、`AIRY_ETIMEOUT=-110`） | ✗ 分段规范不同 |
| 权威源路径 | `agentos/commons/utils/error/include/error.h`（line 3390） | `include/airymax/error.h`（[SC] 补充共享头文件，`120-cross-project-code-sharing.md:81`） | ✗ 路径不一致 |
| 类型名 | `airy_error_t`（line 251 BAN-196） | `airy_err_t`（`cognition_types.h`） | ✗（见 P0-V3-4） |

**工作量**：~1h（§34.5 全节对齐开源 SSoT，补 i18n/发行版分段，修正权威源路径）。

#### P1-V3-4：闭源手册 §11.6 改名目标 `agentrt_*` 与实际源码 `airy_*` 矛盾

**问题描述**：§11.6 章节描述 `airy_` → `agentrt_` 改名，但实际源码使用 `airy_*`（v1.0 §5.2 确认 916+ 处），改名目标与实际源码矛盾。详见 §5 专项审查。

**证据**：`agentrt工程标准规范手册.md:1509/1511/1521/1522` 等。

**工作量**：~1h（详见 §5 修正建议）。

#### P1-V3-5：闭源手册 line 4175 "agentrt_ 前缀" 与术语表矛盾

**问题描述**：闭源手册 §37.3 PROD-03（line 4175）描述"`include/`: C 公开 ABI 头文件（**agentrt_ 前缀**）"，与术语表 lines 98-111（`airy_*`）和实际源码（`airy_*`）矛盾。

**证据**：

| 位置 | 内容 | 矛盾点 |
|------|------|--------|
| `:4175` | "`include/`: C 公开 ABI 头文件（**agentrt_ 前缀**）" | 声明 `agentrt_` 前缀 |
| `:98-111` | 术语表 7 项 `airy_*`/`airy_sys_*` + 1 项 `AIRY_E*` | 声明 `airy_*` 前缀 |
| 实际源码 | `airy_*`（v1.0 §5.2，916+ 处） | 使用 `airy_*` 前缀 |

**工作量**：~0.1h（line 4175 `agentrt_ 前缀` → `airy_ 前缀`）。

#### P1-V3-6：README.md 版本号不一致

**问题描述**：`docs-closed/agentrt/README.md` 自身版本号不一致，line 7 与 line 96 给出不同版本。

**证据**：

| 位置 | 内容 |
|------|------|
| `README.md:7` | "**版本**: 0.1.1" |
| `README.md:96` | "**文档版本**: v1.0" |

**工作量**：~0.1h（统一版本号）。

### 4.3 P2 级问题（3 项，1.0.1 全阶段改进）

#### P2-V3-1：闭源手册 `agentos.yaml` 配置文件名残留

**问题描述**：闭源手册 line 3371 使用 `agentos.yaml` 配置文件名，与 §11.6.1 L3 运行时路径改名（`/etc/agentos` → `/etc/agentrt`）矛盾。

**证据**：`agentrt工程标准规范手册.md:3371`："**配置选择**：`agentos.yaml` 的 `service_discovery.backend: shm|dns-sd|consul|etcd|k8s`"

**工作量**：~0.1h（`agentos.yaml` → `agentrt.yaml`）。

#### P2-V3-2：闭源手册 `AgentOS` 历史名称残留（多处）

**问题描述**：闭源手册正文广泛使用 `AgentOS` 历史名称，§11.8（line 1736-1738）标注"v24.1 已完成 AgentOS→AgentRT 改名"，但正文仍用 `AgentOS`。

**证据**（典型位置）：line 28/133/179/339/347/365/381/383/694/1068/1261/1263/1415/1466/1472/1493/1495/1500/1736/1738/2524 等。

**评估**：部分为历史变动说明（line 28/1736/1738 等），保留合理；部分为正文当前描述（line 133/694/1068 等），应修正为 `AgentRT`。需逐项区分。

**工作量**：~1h（逐项核对，区分历史记录 vs 当前描述）。

#### P2-V3-3：05-tech-reference-and-improvement/ 历史归档文档 1738 处 `agentos_` 残留

**问题描述**：`05-tech-reference-and-improvement/` 下 5 个历史归档文档共 1738 处 `agentos_` 残留。

**证据**（Grep `agentos_` count）：

| 文件 | `agentos_` 残留数 |
|------|------------------|
| `historical-prototypes/AgentOS原型文档.md` | **1335** |
| `analysis-reports/第01版-AgentOS下一步改进建议.md` | **155** |
| `analysis-reports/第01版-AgentOS双思维模型详细落地方案.md` | **151** |
| `analysis-reports/第02版-AgentOS技术改进策略和详细方案.md` | **75** |
| `core-module-designs/CoreLoopThree具体实现方案01.md` | **22** |
| **合计** | **1738** |

**评估**：这些文件位于 `historical-prototypes/`、`analysis-reports/`、`core-module-designs/` 子目录，从文件名（"第01版"、"第02版"、"AgentOS原型文档"）判断为历史归档文档，记录 AgentOS 时代的技术方案。修改它们会破坏历史记录的完整性。

**建议**：**不修正**，保留历史归档原貌。在 README.md 或目录说明中添加标注："本目录下文档为历史归档，使用 AgentOS 时代命名，不反映当前 `airy_*` 前缀规范"。

**工作量**：~0.2h（仅添加归档说明）。

### 4.4 问题汇总

| 类别 | P0 | P1 | P2 | 合计 |
|------|----|----|----|----|
| 前缀残留（07-subsystem-specs/、06-contracts/） | 2（P0-V3-1/2） | 0 | 1（P2-V3-3 归档） | 3 |
| 技术准确性（IPC 头/错误码） | 2（P0-V3-3/4） | 1（P1-V3-3） | 0 | 3 |
| 路径/目录一致性 | 0 | 2（P1-V3-1/2） | 1（P2-V3-1） | 3 |
| 改名章节/前缀声明 | 0 | 2（P1-V3-4/5） | 1（P2-V3-2） | 3 |
| 版本管理 | 0 | 1（P1-V3-6） | 0 | 1 |
| **合计** | **4** | **6** | **3** | **13** |

**工作量估算**：
- P0 合计：~9.5h（P0-V3-1 ~6h + P0-V3-2 ~1h + P0-V3-3 ~2h + P0-V3-4 ~0.5h）
- P1 合计：~5.5h
- P2 合计：~1.3h
- **v3.0 闭源文档复审总工作量**：~16.3h

---

## 5. §11.6 历史改名章节专项审查

### 5.1 §11.6 章节当前内容

**位置**：`agentrt工程标准规范手册.md:1509-1595`

**章节结构**：

| 小节 | 行号 | 内容 |
|------|------|------|
| §11.6 标题 | 1509 | `### 11.6 airy_ → agentrt_ 彻底改名规范（v26.0 重写）` |
| §11.6 核心决策 | 1511 | "`airy_` → **`agentrt_`** 彻底改名，**不留兼容别名头**" |
| §11.6.1 七层面改名矩阵 | 1513-1525 | L1-L9 改名映射表 |
| §11.6.2 改名验证标准 | 1527-1535 | ACC-SP01 + ACC-SP02 验证项 |
| §11.6.3 改名操作规范 | 1537-1544 | BAN-341~BAN-344 |
| §11.6.4 改名操作步骤 | 1546-1595 | SP01 详细 bash 命令序列 |

### 5.2 §11.6.1 七层面改名矩阵（line 1515-1525）

| 层面 | 旧名 | 新名（§11.6 声明） | 实际源码 | 一致性 |
|------|------|------------------|---------|--------|
| L1 源码目录 | `agentos/` | `agentrt/` | `agentrt/`（v1.0 引用） | ✅ 一致（目录改名已执行） |
| L2 CMake target | `airy_common` 等 | `agentrt_common` 等 | `airy_*`（源码） | ✗ 不一致 |
| L3 运行时路径 | `/etc/agentos`、`AIRY_CONFIG_DIR` | `/etc/agentrt`、`AGENTRT_CONFIG_DIR` | 未确认 | — |
| L4 安装路径 | `include/agentos/` | `include/agentrt/` | `include/airymax/`（[SC]） | ✗ 不一致 |
| L5 C 公开 ABI | `airy_error_t`、`airy_syscalls_init()` | `agentrt_error_t`、`agentrt_syscalls_init()` | `airy_err_t`、`airy_sys_*`（源码） | ✗ 不一致 |
| L6 C 宏 | `AIRY_API`、`AIRY_VERSION` | `AGENTRT_API`、`AGENTRT_VERSION` | `AIRY_*`（源码） | ✗ 不一致 |
| L7 SDK 包名 | `agentos`(PyPI) | `agentrt`(PyPI) | 未确认 | — |
| L8 daemon 模块 | `agentos/daemon/` | `agentrt/daemons/` | `agentrt/daemons/`（v1.0 引用） | ✅ 一致（目录改名已执行） |
| L9 进程二进制名 | `gateway_d` 等 12 个 | 保持不变 | 保持不变 | ✅ 一致 |

### 5.3 问题分析

#### 5.3.1 `agentrt_*` 作为改名目标与实际源码 `airy_*` 矛盾

§11.6 核心决策（line 1511）声明 `airy_` → `agentrt_` 彻底改名，§11.6.1 L2/L5/L6 描述的改名目标为 `agentrt_*`/`AGENTRT_*`。但实际源码使用 `airy_*`/`AIRY_*`（v1.0 §5.2 确认 atoms 916+ 处 `airy_*`），**改名未执行**（或执行后回退）。

**证据链**：
1. v2.0 报告 §3.1.3 失真 2 已指出："手册自身的 v26.0 变动说明（line 9）也提到'agentos_ → agentrt_ 改名彻底'，但实际源码用的是 `airy_*` 而非 `agentrt_*`——**改名方向与实际源码不一致**。"
2. v2.0 P0-DQC-2 修正将手册术语表从 `agentos_*` 改为 `airy_*`（而非 `agentrt_*`），进一步确认实际源码用 `airy_*`。
3. v2.0 修正日志 §4.1 明确说明："§11.6 章节中 `agentrt_*` 作为改名目标的表述本身即为 v2.0 报告指出的失真之一（实际源码用 `airy_*` 而非 `agentrt_*`），但修正 `agentrt_*` 引用超出 P0-DQC-2 范围，需作为后续 P1 级问题单独处理。"

#### 5.3.2 P0-DQC-2 全量替换副作用

v2.0 P0-DQC-2 全量替换 `agentos_` → `airy_` 后，§11.6 标题从"agentos_ → agentrt_ 改名规范"变为"airy_ → agentrt_ 改名规范"。这导致 §11.6 描述的改名方向变为"`airy_` → `agentrt_`"，但实际源码用 `airy_*`，§11.6 描述的改名目标 `agentrt_*` 从未实现。

#### 5.3.3 `agentos/` 目录路径引用（带斜杠）

§11.6.1 L1/L4/L8 描述 `agentos/` → `agentrt/` 目录改名。这部分**已执行**（实际源码目录为 `agentrt/`）。但闭源手册正文其他章节仍广泛使用 `agentos/` 目录路径（60+ 处，见 P1-V3-2），说明目录改名在文档中未同步。

#### 5.3.4 §11.6 与术语表矛盾

§11.6 声明改名目标为 `agentrt_*`，但术语表 lines 98-111（v2.0 P0-DQC-2 已修正）声明代码前缀为 `airy_*`。两者直接矛盾。

### 5.4 修正建议

**推荐方案 A：保留 §11.6 作为历史决策记录，添加显著声明**

在 §11.6 章节头部（line 1509 标题下方）添加显著声明：

```
> ⚠️ **历史决策记录（未执行）**：本节描述的 `airy_` → `agentrt_` 彻底改名是 v26.0 决策，
> 但实际未执行。实际源码保留 `airy_*`/`AIRY_*` 前缀（详见 §1.6 术语强制规范表）。
> 本节仅作为 v26.0 历史决策记录保留，不作为当前工程规范。
> 当前有效的前缀规范以 §1.6 术语表（`airy_*`/`airy_sys_*`/`AIRY_E*`）为准。
```

**理由**：
1. §11.6 记录了 v26.0 的真实决策历史，删除会丢失历史追溯。
2. 添加声明后，读者明确知道该章节为历史记录，不作为当前规范。
3. 与 §11.8（AgentOS→AgentRT 历史改名，v24.1 已完成）的处理方式一致（§11.8 已标注"仅保留历史记录"）。

**备选方案 B：将 §11.6 中 `agentrt_*` 改名目标全部改为 `airy_*`**

不可行。因为 §11.6 描述的是"改名"，若改名目标改为 `airy_*`，则 §11.6 变成"`airy_` → `airy_` 改名"，语义无意义。

**备选方案 C：删除 §11.6**

不推荐。删除会丢失 v26.0 决策历史，且 §11.6.3 BAN-341~BAN-344 仍被其他章节引用（如 line 2216 BAN 规则总表）。

**`agentos/` 目录路径引用处理**：

§11.6.1 L1/L4/L8 中的 `agentos/` → `agentrt/` 是历史改名记录，应保留原样（作为历史决策的一部分）。但闭源手册正文其他章节的 `agentos/` 目录路径残留（P1-V3-2，60+ 处）应修正为 `agentrt/`。

**工作量**：~0.5h（添加历史声明 + 核对 §11.6 内部一致性）。

---

## 6. 修正后综合评分变化

### 6.1 评分变化对比

| 评分维度 | v2.0 修正前 | v2.0 修正后 | v3.0 复审后 | v3.0 修正后（预估） |
|---------|------------|------------|------------|-------------------|
| 技术准确性 | D | B+ | **C** | **B+**（修正 P0-V3-3/4 + P1-V3-3 后） |
| 工程指导性 | C+ | B+ | **C-** | **B+**（修正 P0-V3-1/2 后） |
| 一致性（与开源 SSoT） | D | B+ | **C** | **B+**（修正 P1-V3-1/2/3 后） |
| 修正持久性 | — | A | **A** | **A** |
| **闭源文档总评** | **58/D+** | **78/B+** | **66/C+** | **80/B+**（预估） |

### 6.2 v3.0 评分下调原因

v3.0 复审后评分从 v2.0 修正后的 78/B+ 下调至 66/C+（-12 分），原因：

1. **v2.0 修正范围盲区暴露**（-6 分）：v2.0 P0-DQC-2 仅修正 `agentrt工程标准规范手册.md` 1 个文件，未覆盖 07-subsystem-specs/（302 处）和 06-contracts/（38 处）共 340 处 `agentos_*` 残留。这些残留严重削弱工程指导性（开发者按子系统规格文档编写代码将使用错误前缀）。
2. **IPC 消息头三重违规残留**（-3 分）：闭源手册 §34.2 仍使用 `are_ipc_message_header_t`，与开源 SSoT `struct airy_ipc_msg_hdr` 三重违规，是 v2.0 开源 P0-4 修正未同步。
3. **错误码类型名/分段不一致**（-3 分）：闭源手册用 `airy_error_t`（6 处），开源 SSoT 用 `airy_err_t`；闭源手册 9 分段，开源 SSoT 11 分段。

### 6.3 v3.0 修正后预估评分

若 v3.0 发现的 4 项 P0 + 6 项 P1 全部修正，闭源文档总评可回升至 **80/B+**（比 v2.0 修正后 78/B+ 高 2 分，因修正后覆盖范围更广、一致性更高）。

### 6.4 与 v2.0 评分的关系

| 评分阶段 | 评分 | 评分范围 | 说明 |
|---------|------|---------|------|
| v2.0 修正前 | 58/D+ | 仅 `agentrt工程标准规范手册.md` | v2.0 报告 §3.1.3 |
| v2.0 修正后 | 78/B+ | 仅 `agentrt工程标准规范手册.md` | v2.0 验证报告 §8.1（**仅基于 1 文件**） |
| v3.0 复审后 | 66/C+ | `docs-closed/agentrt/` 全目录 | v3.0 扩大审查范围，暴露盲区 |
| v3.0 修正后（预估） | 80/B+ | `docs-closed/agentrt/` 全目录 | 修正 4 P0 + 6 P1 后 |

> **关键说明**：v2.0 评分 78/B+ 与 v3.0 评分 66/C+ 的差异**不是修正倒退**，而是**审查范围扩大**。v2.0 仅审查 `agentrt工程标准规范手册.md` 1 文件，v3.0 扩大至 `docs-closed/agentrt/` 全目录（含 07-subsystem-specs/、06-contracts/ 等），发现 v2.0 修正范围的盲区。

---

## 7. 修正建议

### 7.1 立即修复（1.0.1 M1 启动前 ~9.5h）

| # | 问题 | 操作 | 工作量 |
|---|------|------|--------|
| 1 | P0-V3-1 | 07-subsystem-specs/ 10 文件全量替换 `agentos_` → `airy_`、`AGENTOS_` → `AIRY_`，逐项核对类型名（`agentos_error_t` → `airy_err_t`、`agentos_arena_t` → `airy_arena_t` 等） | ~6h |
| 2 | P0-V3-2 | 06-contracts/ 3 文件全量替换 `agentos_` → `airy_`（含指标前缀 `agentos_requests_total` → `airy_requests_total` 等） | ~1h |
| 3 | P0-V3-3 | 闭源手册 §34.2 全节重写，对齐开源 SSoT `struct airy_ipc_msg_hdr`（无 typedef + `__u32/__u16/__u64/__u8` + 8 字段 + `__attribute__((packed))` + `_Static_assert`） | ~2h |
| 4 | P0-V3-4 | 闭源手册 6 处 `airy_error_t` → `airy_err_t`（line 251/507/535/764/787/1521） | ~0.5h |

### 7.2 1.0.1 M1 阶段修复（~5.5h）

| # | 问题 | 操作 | 工作量 |
|---|------|------|--------|
| 1 | P1-V3-1 | 7 处 `docs/AirymaxAgentOS/` → `docs/AirymaxOS/` | ~0.3h |
| 2 | P1-V3-2 | 60+ 处 `agentos/` 目录路径 → `agentrt/`（逐项核对，区分目录路径 vs 历史记录） | ~3h |
| 3 | P1-V3-3 | §34.5 错误码分段对齐开源 SSoT（补 i18n/发行版分段，修正权威源路径为 `include/airymax/error.h`） | ~1h |
| 4 | P1-V3-4 | §11.6 添加历史决策声明（详见 §5.4 推荐方案 A） | ~0.5h |
| 5 | P1-V3-5 | line 4175 `agentrt_ 前缀` → `airy_ 前缀` | ~0.1h |
| 6 | P1-V3-6 | README.md 版本号统一（line 7 与 line 96） | ~0.1h |
| 7 | P1-DQC-4 | line 9 v26.0 历史 29 仓明细添加"已迁移至 38 仓"标注 | ~0.2h |
| 8 | P2-DQC-4 | line 40 "16 个 daemon" → "12 个 daemon" | ~0.1h |
| 9 | P2-V3-1 | line 3371 `agentos.yaml` → `agentrt.yaml` | ~0.1h |

### 7.3 1.0.1 全阶段改进（~1.2h）

| # | 问题 | 操作 | 工作量 |
|---|------|------|--------|
| 1 | P2-V3-2 | 闭源手册 `AgentOS` 历史名称残留逐项核对，区分历史记录 vs 当前描述 | ~1h |
| 2 | P2-V3-3 | 05-tech-reference-and-improvement/ 添加归档说明（不修正内容） | ~0.2h |

### 7.4 关键决策点

| # | 决策点 | 选项 | 推荐 |
|---|--------|------|------|
| 1 | 07-subsystem-specs/ agentos_* 修正方式 | A：全量 sed 替换 / B：逐文件人工核对 | **B**（需核对类型名，如 `agentos_error_t` → `airy_err_t` 而非 `airy_error_t`） |
| 2 | §11.6 处理方式 | A：添加历史声明保留 / B：删除 / C：改为 `airy_` → `airy_` | **A**（保留历史追溯，详见 §5.4） |
| 3 | 05-tech-reference-and-improvement/ 归档处理 | A：全量修正 / B：不修正添加归档说明 | **B**（保留历史原貌） |
| 4 | 错误码分段对齐方向 | A：闭源手册对齐开源 SSoT 11 分段 / B：开源 SSoT 对齐闭源 9 分段 | **A**（开源 SSoT 为权威源） |

---

## 附录 A：审查文件清单

### A.1 必读历史报告（3 份）

| 文件 | 路径 | 用途 |
|------|------|------|
| v2.0 文档质量控制 | `docs-closed/_review_v2.0/01-document-quality-control.md` | v2.0 P0-DQC-1/P0-DQC-2 发现 |
| v2.0 闭源 P0 修正日志 | `docs-closed/agentrt/_review_v2.0/fix-log-p0-closed-docs.md` | P0-DQC-1/P0-DQC-2 修正操作 |
| v2.0 修正验证报告 | `docs-closed/agentrt/_review_v2.0/fix-verification-report.md` | 修正验证 + 延期项清单 |

### A.2 实际审查文件（docs-closed/agentrt/ 全目录）

#### A.2.1 主手册（1 份）

| 文件 | 路径 | 审查重点 |
|------|------|---------|
| 工程标准规范手册 | `docs-closed/agentrt/agentrt工程标准规范手册.md`（v28.0，254486 B） | 全文一致性、与开源 SSoT 对齐 |

#### A.2.2 README（1 份）

| 文件 | 路径 | 审查重点 |
|------|------|---------|
| 闭源文档索引 | `docs-closed/agentrt/README.md` | 版本号一致性 |

#### A.2.3 07-subsystem-specs/（12 份）

| 文件 | `agentos_` 残留数 | 审查结论 |
|------|------------------|---------|
| `01-checkpoint.md` | 2 | P0-V3-1 |
| `02-corekern.md` | **0**（已用 `airy_*`） | ✅ 与开源 SSoT 一致 |
| `03-coreloopthree.md` | **166** | P0-V3-1（最严重） |
| `04-cupolas.md` | 3 | P0-V3-1 |
| `05-gateway-d.md` | 42 | P0-V3-1 |
| `06-llm-d.md` | 21 | P0-V3-1 |
| `07-manager.md` | 1 | P0-V3-1 |
| `08-market-d.md` | 10 | P0-V3-1 |
| `09-memory.md` | 35 | P0-V3-1 |
| `10-openlab.md` | **0**（纯描述性） | ✅ 无前缀问题 |
| `11-orchestrator.md` | 2 | P0-V3-1 |
| `12-tool-d.md` | 20 | P0-V3-1 |
| **合计** | **302** | — |

#### A.2.4 06-contracts/（5 份）

| 文件 | `agentos_` 残留数 | 审查结论 |
|------|------------------|---------|
| `contract_A_B.h` | 4 | P0-V3-2 |
| `contract_A_C.h` | 17 | P0-V3-2 |
| `contract_B_C.h` | 0 | ✅ |
| `contract_test.c` | 17 | P0-V3-2 |
| `CMakeLists.txt` / `README.md` | 0 | ✅ |
| **合计** | **38** | — |

#### A.2.5 05-tech-reference-and-improvement/（5 份，历史归档）

| 文件 | `agentos_` 残留数 | 审查结论 |
|------|------------------|---------|
| `historical-prototypes/AgentOS原型文档.md` | 1335 | P2-V3-3（历史归档，不修正） |
| `analysis-reports/第01版-AgentOS下一步改进建议.md` | 155 | P2-V3-3 |
| `analysis-reports/第01版-AgentOS双思维模型详细落地方案.md` | 151 | P2-V3-3 |
| `analysis-reports/第02版-AgentOS技术改进策略和详细方案.md` | 75 | P2-V3-3 |
| `core-module-designs/CoreLoopThree具体实现方案01.md` | 22 | P2-V3-3 |
| **合计** | **1738** | — |

#### A.2.6 开源 SSoT 对照文件（3 份）

| 文件 | 路径 | 用途 |
|------|------|------|
| 跨项目代码共享 SSoT | `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md` | [SC] 6 头文件 + 错误码 SSoT |
| IPC 消息头 SSoT | `docs/AirymaxRT/30-interfaces/06-ipc/README.md` | `struct airy_ipc_msg_hdr` 权威定义 |
| 错误码 SSoT | `docs/AirymaxRT/10-architecture/00-architectural-principles.md` | `airy_err_t` + `AIRY_E*` 权威定义 |

### A.3 审查范围说明

本次审查覆盖 `docs-closed/agentrt/` 下所有文件（含主手册、README、07-subsystem-specs/、06-contracts/、05-tech-reference-and-improvement/、_analysis_0.1.1/、_archive_*/ 等子目录）。其中：

- **主手册 + README + 07-subsystem-specs/ + 06-contracts/**：生产级文档，需与开源 SSoT 严格对齐，为 v3.0 审查重点。
- **05-tech-reference-and-improvement/**：历史归档文档（analysis-reports/historical-prototypes/core-module-designs/），保留历史原貌，仅添加归档说明。
- **_archive_*/（_archive_conversations/、_archive_fix_history/）**：历史对话与修复档案，不在本次审查范围（已归档）。
- **_review_v1.0/、_review_v2.0/、_review_v2.1/、_review_v3.0/**：审查报告目录，不在本次审查范围（自身为审查产物）。
- **_analysis_0.1.1/、_design_0.1.1/、_review_0.1.1/**：0.1.1 阶段分析与设计文档，本次未深入审查（聚焦生产级文档）。

---

## 附录 B：Grep 机器验证矩阵

### B.1 v2.0 修正持久性验证（7 项，全部通过）

| # | 验证项 | Grep 命令 | 期望 | 实际 | 状态 |
|---|--------|----------|------|------|------|
| 1 | 闭源手册 `agentos_` 零残留 | `grep -c "agentos_" agentrt工程标准规范手册.md` | 0 | 0 | ✅ |
| 2 | 闭源手册 `AGENTOS_` 零残留 | `grep -c "AGENTOS_" agentrt工程标准规范手册.md` | 0 | 0 | ✅ |
| 3 | [SC] 6 头文件清单 | `grep -n "6 个头文件完全共享"` | 3（line 21/3675/4343） | 3 | ✅ |
| 4 | 旧的"4 个"消除 | `grep -c "4 个头文件完全共享"` | 0 | 0 | ✅ |
| 5 | 术语表 `airy_sys_*` | `grep -n "airy_sys_\*"` | line 106 | line 106 | ✅ |
| 6 | 术语表 `AIRY_E*` | `grep -n "AIRY_E\*"` | line 111 | line 111 | ✅ |
| 7 | 术语表 7+1 项 | 逐行核对 lines 98-111 | 7 `airy_*`/`airy_sys_*` + 1 `AIRY_E*` | 7+1 | ✅ |

### B.2 v3.0 新发现验证（13 项）

| # | 验证项 | Grep 命令 | 实际 | 问题编号 |
|---|--------|----------|------|---------|
| 1 | 07-subsystem-specs/ `agentos_` 残留 | `grep -rc "agentos_" 07-subsystem-specs/` | 302（10 文件） | P0-V3-1 |
| 2 | 06-contracts/ `agentos_` 残留 | `grep -rc "agentos_" 06-contracts/` | 38（3 文件） | P0-V3-2 |
| 3 | 闭源手册 `are_ipc_message_header_t` 残留 | `grep -n "are_ipc_message_header_t"` | 4（line 2901/3330/3349/3353） | P0-V3-3 |
| 4 | 闭源手册 `airy_error_t` 残留 | `grep -n "airy_error_t"` | 6（line 251/507/535/764/787/1521） | P0-V3-4 |
| 5 | 闭源手册 `docs/AirymaxAgentOS/` 路径错误 | `grep -n "docs/AirymaxAgentOS/"` | 7（line 20/2232/4327/4341/4398/4421/4442） | P1-V3-1 |
| 6 | 闭源手册 `agentos/` 目录残留 | `grep -n "agentos/"` | 60+ | P1-V3-2 |
| 7 | 闭源手册错误码分段 9 vs 11 | `grep -n "通用.*-1~-99\|i18n\|发行版"` | 9 分段（无 i18n/发行版） | P1-V3-3 |
| 8 | §11.6 `agentrt_` 改名目标 | `grep -n "airy_ → agentrt_\|agentrt_error_t\|AGENTRT_API"` | 多处（line 1509/1511/1521/1522） | P1-V3-4 |
| 9 | line 4175 `agentrt_ 前缀` | `grep -n "agentrt_ 前缀"` | 1（line 4175） | P1-V3-5 |
| 10 | README 版本号不一致 | `grep -n "版本"` README.md | 2（line 7: 0.1.1 / line 96: v1.0） | P1-V3-6 |
| 11 | `agentos.yaml` 配置文件名 | `grep -n "agentos.yaml"` | 1（line 3371） | P2-V3-1 |
| 12 | `AgentOS` 历史名称残留 | `grep -n "AgentOS"` | 多处 | P2-V3-2 |
| 13 | 05-tech-reference/ 历史归档 `agentos_` | `grep -rc "agentos_" 05-tech-reference-and-improvement/` | 1738（5 文件） | P2-V3-3 |

### B.3 v2.0 延期项验证（3 项）

| # | 验证项 | Grep 命令 | 实际 | 状态 |
|---|--------|----------|------|------|
| 1 | P1-DQC-4 29→38 仓残留 | `grep -n "29 仓\|38 仓"` | line 9（v26.0 历史 29 仓）vs line 4-5（v28.0 当前 38 仓） | ⚠️ 仍残留 |
| 2 | P2-DQC-4 daemon 16 vs 12 | `grep -n "16 个 daemon\|12 个 daemon"` | line 40（16 个）vs line 3377/4173/4364/4383（12 个） | ⚠️ 仍残留 |
| 3 | §11.6 agentrt_* 改名目标 | `grep -n "airy_ → agentrt_"` | line 1509/1511 | ⚠️ 仍残留 |

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>

---

**报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-14 | 审查版本：v3.0 | 维度：闭源文档全面复审
