Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
<!-- SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0 -->
<!-- 保密级别：SPHARX Ltd 内部参考，闭源不公开 -->
<!-- 版本：4.0 | 日期：2026-07-14 -->

# Airymax agentrt v4.0 审查报告 —— 跨文档一致性与 SSoT 深化复审

> **版权声明**: Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved. "From data intelligence emerges."
> **保密级别**: SPHARX Ltd 内部参考，闭源不公开
> **版本**: 4.0
> **日期**: 2026-07-14
> **审查范围**: `docs/AirymaxRT/` + `docs-closed/agentrt/` + `docs/AirymaxOS/50-engineering-standards/`（SSoT）+ `agentrt/` 源码（833 文件）+ [SC] 6 头文件
> **审查性质**: 仅审查，不修改任何文件
> **基线**: v3.0 修正后预估 ~76/B（`docs-closed/agentrt/_review_v3.0/fix-verification-report-v3.md`）
> **审查 Agent**: Agent 4（跨文档一致性与 SSoT）

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [v3.0 修正持久性跨域验证矩阵](#2-v30-修正持久性跨域验证矩阵)
3. [v3.0 修正副作用跨域清单](#3-v30-修正副作用跨域清单)
4. [v4.0 新发现问题清单](#4-v40-新发现问题清单)
5. [八维度 A-H 一致性验证矩阵](#5-八维度-a-h-一致性验证矩阵)
6. [残留项状态复核](#6-残留项状态复核)
7. [修正后评分预估](#7-修正后评分预估)

---

## 1. 执行摘要

本报告为 Airymax agentrt 项目 v4.0 第四轮深化审查的跨文档一致性专项报告。在前三轮（v1.0/v2.0/v3.0）已完成的基础上，独立审查跨三大文档域 + 源码 + [SC] 共享契约层的交叉一致性，重点发现 v1.0/v2.0/v3.0 未发现的新问题，以及 v3.0 修正可能引入的副作用。

### 核心结论

**v3.0 修正持久性**（10 项已验证）：

| # | 修正项 | 验证结果 | 证据 |
|---|--------|---------|------|
| 1 | 错误码 SSoT 收敛为方案 A | ✅ 持久 | `airy_types.h:65` `AIRY_EINVAL (-22)`，POSIX errno 负值 |
| 2 | `airy_err_t` 定位于 `airy_types.h:41` | ✅ 持久 | SSoT `120-cross-project-code-sharing.md:82` 正确声明 |
| 3 | error.h 16 个冲突码迁移 | ✅ 持久 | `error.h:126`(-40), `:205`(-120), `:214`(-121), `:223`(-122), `:226`(-123) |
| 4 | AIRY_OK 从 error.h 移除 | ✅ 持久（源码） | `error.h:43-46` 注释确认移除 |
| 5 | IPC 头 SSoT 对齐 02-l2 | ✅ 持久 | `02-l2-service-protocol.md:111-124` `struct airy_ipc_msg_hdr` + packed + _Static_assert |
| 6 | IPC 头 SSoT 对齐闭源手册 §34.2 | ✅ 持久 | `agentrt工程标准规范手册.md:3369-3382` 结构体对齐 |
| 7 | 函数前缀清零 07-subsystem-specs/ | ✅ 持久 | 0 处 `agentos_` 残留 |
| 8 | 函数前缀清零 06-contracts/ | ✅ 持久 | 0 处 `agentos_` 残留 |
| 9 | `daemon/` → `daemons/` 路径修正 | ✅ 持久 | docs/AirymaxRT 中 0 处 `agentrt/daemon/` |
| 10 | `AgentRT/` → `agentrt/` 大小写修正（docs/AirymaxRT） | ⚠️ 部分持久 | 从 60 处降至 5 处（4 文件） |

**v4.0 新发现问题**（20 项）：

| 级别 | 数量 | 关键问题 |
|------|------|---------|
| **P0** | **5 项** | `AIRY_ETIMEOUT`（40 处文档引用）为未定义宏；03-protocol-contract.md §7.1 表 8+ 错误码值错误；闭源手册 §4.9 错误码分段方案与 error.h 完全不同；§11.6.3 BAN-342 仍活跃（v3.0 副作用）；闭源手册 LOG-09 仍声称 error.h 定义 AIRY_OK（v3.0 副作用） |
| **P1** | **10 项** | `AIRY_ECANCELLED`(-10) vs `AIRY_ECANCELED`(-47) 拼写+值分裂；coding_conventions §4.4.2 内部矛盾（v3.0 遗漏）；06-iron9 cognition_types.h 描述失实；闭源手册 32 处 AgentRT/ 未清理；02-l2 字段文档引用错误枚举名；airy_ipc_header_t 第三种 IPC 头未入 SSoT 等 |
| **P2** | **5 项** | 字段数不一致（9 vs 8）；docs/AirymaxRT 5 处 AgentRT/ 残留；.bak 43 处残留；闭源手册代码示例用 AIRY_OK；§11.6 引用错误 SSoT 路径 |

### 综合评分

| 版本 | 评分 | 级别 | 变化 |
|------|------|------|------|
| v3.0（复审） | 66 | C+ | — |
| v3.0（修正后预估） | ~76 | B | +10 |
| **v4.0（本次深化复审）** | **~71** | **B-** | **-5** |

评分下调原因：v3.0 修正在已识别范围内有效（10/10 项持久），但 v4.0 深化跨域审查发现：(1) `AIRY_ETIMEOUT` 为未定义宏却被 40 处文档引用（v3.0 误判 `AIRY_ETIMEOUT` 为正确命名）；(2) 03-protocol-contract.md §7.1 错误码表 8+ 个值全部错误（R1-2 比预期更严重）；(3) 闭源手册 §4.9 错误码分段方案与源码完全不同（系统性分裂）；(4) v3.0 修正引入 6 项跨域副作用。

---

## 2. v3.0 修正持久性跨域验证矩阵

### 2.1 域1：错误码 SSoT 统一收敛

| # | v3.0 修正项 | 验证方法 | 实际结果 | 持久性 |
|---|------------|---------|---------|--------|
| 1 | `airy_err_t` 定位于 `airy_types.h:41` | Read `airy_types.h:41` | `typedef int32_t airy_err_t;` | ✅ |
| 2 | SSoT 声明指向 `airy_types.h:41` | Grep `airy_types.h:41` in docs | 9 occurrences / 6 files | ✅ |
| 3 | `AIRY_EINVAL=(-22)` POSIX 负值 | Read `airy_types.h:65` | `#define AIRY_EINVAL (-22)` | ✅ |
| 4 | `AIRY_ENOMEM=(-12)` | Read `airy_types.h:61` | `#define AIRY_ENOMEM (-12)` | ✅ |
| 5 | `AIRY_ETIMEDOUT=(-110)` | Read `airy_types.h:76` | `#define AIRY_ETIMEDOUT (-110)` | ✅ |
| 6 | error.h `AIRY_OK` 移除 | Grep `#define AIRY_OK` in error.h | 0 matches | ✅ |
| 7 | error.h `AIRY_ERR_UNKNOWN` → -99 | Read `error.h:48` | `#define AIRY_ERR_UNKNOWN (-99)` | ✅ |
| 8 | error.h 9 个冲突码迁移至 -40~-48 | Read `error.h:126,135,141,150,153,156,159,168,171` | 全部迁移确认 | ✅ |
| 9 | error.h 4 个 `AIRY_ERR_SYS_*` 迁移至 -120~-123 | Read `error.h:205,214,223,226` | 全部迁移确认 | ✅ |
| 10 | `AIRY_EPERM` 不再重定义 | Read `error.h:98` | 注释确认"不再重定义" | ✅ |
| 11 | SSoT 方案 B/C/D 标注废弃 | Read `120-cross-project-code-sharing.md:86` | "已废弃方案"声明 | ✅ |
| 12 | `cognition_types.h` 不含 `airy_err_t` | Grep `airy_err_t` in cognition_types.h | 0 matches | ✅ |

### 2.2 域2：IPC 头 + 路径术语

| # | v3.0 修正项 | 验证方法 | 实际结果 | 持久性 |
|---|------------|---------|---------|--------|
| 13 | 02-l2 IPC 头对齐 `struct airy_ipc_msg_hdr` | Read `02-l2-service-protocol.md:111-124` | 结构体 + packed + _Static_assert | ✅ |
| 14 | 02-l2 `ARE_IPC_MAGIC` → `AIRY_IPC_MAGIC` | Read `02-l2-service-protocol.md:65` | `#define AIRY_IPC_MAGIC 0x41524531u` | ✅ |
| 15 | 闭源手册 §34.2 IPC 头对齐 | Read `手册:3369-3382` | `struct airy_ipc_msg_hdr` + packed + _Static_assert | ✅ |
| 16 | `agentrt/daemon/` → `agentrt/daemons/` | Grep `agentrt/daemon/` in docs/AirymaxRT | 0 matches | ✅ |
| 17 | `AgentRT/` → `agentrt/` in docs/AirymaxRT | Grep `AgentRT/` in docs/AirymaxRT | 5 occurrences (4 files) | ⚠️ 部分 |
| 18 | Cupolas 4→7 子系统 | （域2声明，由域3执行） | 未独立验证 | — |

### 2.3 域3：闭源文档

| # | v3.0 修正项 | 验证方法 | 实际结果 | 持久性 |
|---|------------|---------|---------|--------|
| 19 | 07-subsystem-specs/ 302 处 `agentos_` 清零 | Grep `agentos_` in 07-subsystem-specs/ | 0 matches | ✅ |
| 20 | 06-contracts/ 38 处 `agentos_` 清零 | Grep `agentos_` in 06-contracts/ | 0 matches | ✅ |
| 21 | §11.6 历史决策声明 | Grep `历史决策` in 手册 | 2 occurrences (L1511, L1518) | ✅ |
| 22 | `agentos.yaml` → `agentrt.yaml` | Grep `agentos.yaml` in 手册 | 0 matches | ✅ |
| 23 | `airy_error_t` → `airy_err_t` | Grep `airy_error_t` in docs/AirymaxRT | 0 matches | ✅ |

### 2.4 持久性总结

> **v3.0 修正 23 项验证中：21 项完全持久 ✅，1 项部分持久 ⚠️，1 项未独立验证。** v3.0 修正在其已识别范围内基本有效，但存在跨域副作用（见第 3 节）和未覆盖范围（见第 4 节）。

---

## 3. v3.0 修正副作用跨域清单

v3.0 某域的修正可能在其他域引入新的不一致。以下为检测到的 6 项副作用：

### 副作用-1：闭源手册 LOG-09 仍声称 error.h 定义 AIRY_OK（P0）

- **触发域**：域1（源码 error.h 移除 `AIRY_OK`）
- **影响域**：域3（闭源手册未同步更新）
- **证据**：
  - 源码 `error.h:43-46`：注释确认 `AIRY_OK` 已移除
  - 闭源手册 `agentrt工程标准规范手册.md:2803`：仍声称 `"commons/utils/error/include/error.h（权威源，定义 AIRY_OK/AIRY_ERR_* 错误码）"`
  - 闭源手册 `agentrt工程标准规范手册.md:847`：代码示例 `@return AIRY_OK (0) 成功`
- **影响**：开发者按闭源手册使用 `AIRY_OK` 将编译失败（宏已不存在）

### 副作用-2：§11.6.3 BAN-342 仍活跃，与 §11.6 历史声明矛盾（P0）

- **触发域**：域3（§11.6 添加历史决策声明）
- **影响域**：域3自身（§11.6.3 规则未同步废止）
- **证据**：
  - `手册:1518`：声明 `airy_ → agentrt_ 改名部分已废止`
  - `手册:1553`：BAN-342 仍为活跃规则 `"禁止改名后留有 airy_ 前缀残留——任何残留即编译失败 | [SPLIT-SCAN] grep airy_ 期望 0"`
  - `手册:2227`：BAN-342 在汇总表中仍列为活跃规则
  - `手册:4559`：汇总仍描述 `§11.6：airy_→agentrt_ 彻底改名规范`
- **影响**：如果执行 BAN-342 的 `[SPLIT-SCAN] grep airy_ 期望 0`，将要求删除源码中全部 1788 处 `airy_` 前缀，破坏整个 [SC] 共享契约层

### 副作用-3：02-l2 IPC 头字段文档引用错误枚举名（P1）

- **触发域**：域2（02-l2 IPC 头结构体对齐 SSoT）
- **影响域**：域2自身（字段注释未同步对齐）
- **证据**：
  - `02-l2-service-protocol.md:98`：`@opcode: Operation code; see enum are_msg_type_t.`（应为 `enum airy_ipc_op`）
  - `02-l2-service-protocol.md:99`：`@flags: Message flags (ARE_FLAG_*).`（应为 `AIRY_IPC_F_*`）
  - `02-l2-service-protocol.md:113`：opcode 注释 `见 are_msg_type_t`（应为 `enum airy_ipc_op`）
  - `02-l2-service-protocol.md:114`：flags 注释 `ARE_FLAG_*`（应为 `AIRY_IPC_F_*`）
  - [SC] `ipc.h:25,33`：定义 `enum airy_ipc_op` + `AIRY_IPC_F_*`
- **影响**：结构体布局对齐但字段语义引用不一致，开发者可能混淆 `are_msg_type_t` 与 `enum airy_ipc_op`

### 副作用-4：闭源手册 32 处 `AgentRT/` 未清理（P1）

- **触发域**：域2（仅清理 docs/AirymaxRT 中的 `AgentRT/`）
- **影响域**：域3（闭源手册未同步清理）
- **证据**：
  - Grep `AgentRT/` in `docs-closed/agentrt/agentrt工程标准规范手册.md` → 32 occurrences
  - 关键违规：`手册:1472` `OpenAirymax/AgentRT/`、`:3030-3036` `AgentRT/agentos/atoms/` 等
  - 其中 L3030-3036 许可证表使用 `AgentRT/agentos/` 路径——双重错误（`AgentRT/` 大写 + `agentos/` 旧名）
- **影响**：Linux 大小写敏感，`AgentRT/` 路径断链；`agentos/` 内层目录名也未更新

### 副作用-5：coding_conventions.md §4.4.2 内部矛盾未修复（P1）

- **触发域**：v3.0 域1 修正了 9 个 OS 工程标准文档的 SSoT 声明，但未修正此内部矛盾
- **影响域**：SSoT 自身（coding_conventions.md §4.4.2）
- **证据**：
  - `coding_conventions.md:2606`：`agentrt-linux 专属符号（[IND] 层）使用 airy_* 前缀`
  - `coding_conventions.md:2607`：`airy_* 前缀不得用于 agentrt-linux 专属功能；airy_* 前缀不得用于 agentrt 用户态`
  - L2606 与 L2607 直接矛盾（同一节内）；L2607 与 `06-iron9:274` 矛盾（`airy_*` 是 [SC] + 应用层正确前缀）
- **影响**：SSoT 函数前缀规则自相矛盾，06-iron9 §3.12 L280 声明以此文件为 SSoT 权威，形成循环引用

### 副作用-6：cognition_types.h 内容描述未修正（P1）

- **触发域**：域1 修正了 `airy_err_t` 定位声明（从 cognition_types.h → airy_types.h）
- **影响域**：SSoT + 06-iron9（cognition_types.h 内容列表未同步修正）
- **证据**：
  - SSoT `120-cross-project-code-sharing.md:73`：声称 cognition_types.h 含 `CoreLoopThree 阶段枚举 + Thinkdual 模式枚举 + LLM 推理阶段枚举 + 上下文结构 + Token 能效指标 + GPU/NPU 描述符`
  - `06-iron9-shared-model.md:70`：同样声称含 `LLM 推理阶段枚举 + Token 能效指标结构 + GPU/NPU 能力描述符`
  - `06-iron9-shared-model.md:249`：`/* LLM 推理阶段枚举：PREFILL / DECODE / SPECULATIVE */`
  - 实际 `cognition_types.h`（38 行）：仅含 `airy_q16_t` + `enum airy_cog_phase` + `enum airy_think_mode`，**零匹配** LLM/Token/GPU/NPU
- **影响**：开发者按文档引用 `#include <airymax/cognition_types.h>` 获取 LLM 推理阶段枚举将编译失败

---

## 4. v4.0 新发现问题清单

### 4.1 P0 级问题（5 项）

#### P0-v4-1：`AIRY_ETIMEOUT`（40 处文档引用）为未定义宏

- **严重度**: P0
- **问题摘要**: 40 处文档引用 `AIRY_ETIMEOUT`（无 D），但该宏在源码中**未定义**。源码权威源 `airy_types.h:76` 定义的是 `AIRY_ETIMEDOUT`（有 D，POSIX 风格）。v3.0 报告误判 `AIRY_ETIMEOUT` 为"正确命名"（仅检查 docs/AirymaxRT 中 `AIRY_ETIMEDOUT` 为 0 即下结论，未检查源码和 docs/AirymaxOS）。
- **证据位置**:
  - 源码 `airy_types.h:76`: `#define AIRY_ETIMEDOUT (-110)` — 有 D
  - 源码 `loop.h:350`: `AIRY_ETIMEOUT`（无 D）— 仅注释，非定义
  - Grep `#define\s+AIRY_ETIMEOUT` in agentrt → 0 matches（未定义）
  - 文档 `AIRY_ETIMEOUT`: 40 occurrences / 21 files（docs/AirymaxRT + docs/AirymaxOS + docs/OpenStandards）
  - 文档 `AIRY_ETIMEDOUT`: 18 occurrences / 8 files
  - 源码 `AIRY_ETIMEOUT`: 1 occurrence / 1 file（仅 loop.h 注释）
  - 源码 `AIRY_ETIMEDOUT`: 20 occurrences / 14 files
  - SSoT `120-cross-project-code-sharing.md:84`: 使用 `AIRY_ETIMEDOUT`（有 D，正确）
- **影响范围**: 40 处文档引用使用未定义宏，开发者按文档使用 `AIRY_ETIMEOUT` 将编译失败
- **工作量估算**: ~4h（40 处文档 `AIRY_ETIMEOUT` → `AIRY_ETIMEDOUT` + 1 处源码注释修正）
- **关联**: v3.0 报告 §7.1 误判此项为"已通过"

#### P0-v4-2：03-protocol-contract.md §7.1 错误码表 8+ 个值全部错误

- **严重度**: P0
- **问题摘要**: R1-2 残留项比 v3.0 报告描述更严重——不仅 4 个码值错误，而是 8+ 个码值错误或未定义，且与闭源手册 §4.9 的错误分段方案关联，形成系统性分裂。
- **证据位置**: `docs/AirymaxRT/20-modules/10-contracts/03-protocol-contract.md:696-716`
- **错误码值对比**:

| 错误码 | 文档表值 | 源码实际值 | 源码位置 | 冲突类型 |
|--------|---------|----------|---------|---------|
| `AIRY_EBADF` | -9 | -112（别名 `AIRY_ERR_SYS_FILE`） | `error.h:87,229` | 值错误 + -9 与 `AIRY_ENOTINIT` 冲突 |
| `AIRY_ENOSYS` | -38 | **未定义** | — | 宏不存在 |
| `AIRY_EFAULT` | -14 | **未定义** | — | 宏不存在 |
| `AIRY_ECANCELED` | -125 | -47（别名 `AIRY_ERR_CANCELED`） | `error.h:80-81,168` | 值错误 |
| `AIRY_EINTR` | -4 | -19（别名 `AIRY_ERR_INTERRUPTED`） | `error.h:83-84,177` | 值错误（-4 是 POSIX 值，但别名给 -19） |
| `AIRY_ECONFLICT` | -4096 | **未定义** | — | 宏不存在 |
| `AIRY_ENOTINIT` | -4097 | -9 | `airy_types.h:80` | 值严重错误 |
| `AIRY_ERESOURCE` | -4098 | -102（别名 `AIRY_ERR_SYS_RESOURCE`） | `error.h:89-90,199` | 值严重错误 |

- **影响范围**: 整个 03-protocol-contract.md §7.1 错误码表不可信，开发者按此表使用错误码将得到错误值
- **工作量估算**: ~3h（重写 §7.1 表 + 修正 8 个值 + 补充缺失宏定义决策）

#### P0-v4-3：闭源手册 §4.9 错误码分段方案与 error.h 完全不同

- **严重度**: P0
- **问题摘要**: 闭源手册 §4.9 定义了一套完全不同的错误码分段方案（-1001~-1099 Task / -2001~-2099 Memory / -3001~-3099 Session / -4001~-4099 Telemetry 等），与 error.h 实际分段（-1~-99 通用 / -100~-199 系统 / -200~-299 内核 / -300~-399 服务 / -400~-499 LLM 等）完全不同。03-protocol-contract.md §7.1 中的 -4096/-4097/-4098 值即来源于此错误分段。
- **证据位置**:
  - 闭源手册 `agentrt工程标准规范手册.md:797-811`：§4.9 错误码分段表
  - 源码 `error.h:106-118`：实际分段规划注释（-1~-99 / -100~-999 / -1000~-1999 / -2000~-2999 等）
  - 源码 `error.h:120-319`：实际定义值（-40 / -3 / -4 / -41 / -6 / -42 / -8 / -9 / -43 / -44 / -45 / -46 / -14 / -15 / -47 / -48 / -18 / -19 / -30 / -31）
- **影响范围**: 闭源手册 §4.9 + BAN-231（"新增错误码必须在其所属分段范围内注册"）基于错误分段，所有按此分段的错误码分配都是错误的
- **工作量估算**: ~4h（重写 §4.9 分段表 + 修正 BAN-231 引用）

#### P0-v4-4：§11.6.3 BAN-342 仍为活跃规则，要求 `grep airy_ → 0`（v3.0 副作用-2）

- **严重度**: P0
- **问题摘要**: v3.0 在 §11.6 标题处添加了历史决策声明（L1511/L1518 称 `airy_ → agentrt_` 改名"已废止"），但 §11.6.3 中的 BAN-342 规则**未同步废止**，仍为活跃状态，要求 `grep airy_ 期望 0`。源码有 1788 处 `airy_` 前缀（正确前缀），BAN-342 若执行将破坏整个 [SC] 共享契约层。
- **证据位置**:
  - `手册:1518`：`airy_ → agentrt_ 改名部分已废止`
  - `手册:1553`：`BAN-342 | 禁止改名后留有 airy_ 前缀残留——任何残留即编译失败 | [SPLIT-SCAN] grep airy_ 期望 0`
  - `手册:2227`：BAN-342 在 §20.4 汇总表中仍为活跃规则
  - `手册:4559`：§4559 汇总仍描述 `§11.6：airy_→agentrt_ 彻底改名规范（v4.0 重写）`
  - 源码 `airy_` 前缀: 1788 occurrences / 100 files
- **影响范围**: BAN-342 作为活跃规则与 SSoT 函数前缀规则直接矛盾，CI 若执行 `[SPLIT-SCAN]` 将导致全部编译失败
- **工作量估算**: ~2h（废止 BAN-341/BAN-342 中关于 `airy_` 的部分 + 更新 §20.4 汇总表 + 更新 §4559 描述）

#### P0-v4-5：闭源手册 LOG-09 仍声称 error.h 定义 AIRY_OK（v3.0 副作用-1）

- **严重度**: P0
- **问题摘要**: v3.0 从源码 error.h 移除了 `AIRY_OK` 定义，但闭源手册 LOG-09 规则（L2803）仍声称 error.h 定义 `AIRY_OK`，且代码示例（L847）仍使用 `AIRY_OK`。
- **证据位置**:
  - 源码 `error.h:43-46`：注释确认 `AIRY_OK` 已移除
  - 闭源手册 `手册:2803`：`commons/utils/error/include/error.h（权威源，定义 AIRY_OK/AIRY_ERR_* 错误码）`
  - 闭源手册 `手册:847`：`@return AIRY_OK (0) 成功`
  - TERMINOLOGY.md:212：`不再使用 AIRY_OK`
- **影响范围**: 开发者按闭源手册 LOG-09 使用 `AIRY_OK` 将编译失败
- **工作量估算**: ~1h（修正 L2803 + L847 + 全手册 Grep `AIRY_OK` 清理）

### 4.2 P1 级问题（10 项）

#### P1-v4-1：`AIRY_ECANCELLED`(-10) vs `AIRY_ECANCELED`(-47) 拼写+值分裂

- **严重度**: P1
- **问题摘要**: 权威源 `airy_types.h:81` 定义 `AIRY_ECANCELLED`（双 L，英式拼写）= -10；error.h:80-81 定义 `AIRY_ECANCELED`（单 L，美式拼写，POSIX 风格）= `AIRY_ERR_CANCELED` = -47。两个宏拼写不同、值不同，但语义相同（操作取消）。POSIX 标准使用 `ECANCELED`（单 L），应统一为 `AIRY_ECANCELED`。
- **证据位置**:
  - `airy_types.h:81`: `#define AIRY_ECANCELLED (-10)` — 双 L，SSoT 权威
  - `error.h:80-81`: `#ifndef AIRY_ECANCELED / #define AIRY_ECANCELED AIRY_ERR_CANCELED` — 单 L，别名
  - `error.h:168`: `#define AIRY_ERR_CANCELED (-47)`
  - `error.h:150`: 注释 `迁移避免与 AIRY_ECANCELLED(-10) 冲突` — 引用双 L 形式
- **影响范围**: 两个不同拼写/值的宏共存，开发者可能混用导致语义错误
- **工作量估算**: ~2h（统一为 `AIRY_ECANCELED` 单 L + 修正 airy_types.h + error.h + 文档）

#### P1-v4-2：coding_conventions.md §4.4.2 函数前缀规则内部矛盾（v3.0 遗漏，v3.0 副作用-5）

- **严重度**: P1
- **问题摘要**: v3.0 报告 P1-v3-3 指出的问题未修复。L2606 说 agentrt-linux [IND] 用 `airy_*`，L2607 说 `airy_*` 不得用于 agentrt-linux 专属功能——同一节内直接矛盾。L2607 还说 `airy_*` 不得用于 agentrt 用户态，与 SSoT `06-iron9:274` 矛盾。
- **证据位置**:
  - `coding_conventions.md:2606`: `agentrt-linux 专属符号（[IND] 层）使用 airy_* 前缀`
  - `coding_conventions.md:2607`: `禁止混用——airy_* 前缀不得用于 agentrt-linux 专属功能；airy_* 前缀不得用于 agentrt 用户态`
- **影响范围**: SSoT 函数前缀规则自相矛盾，06-iron9 §3.12 L280 声明以此文件为权威
- **工作量估算**: ~2h（重写 §4.4.2 消除矛盾）

#### P1-v4-3：06-iron9 + SSoT cognition_types.h 内容描述失实（v3.0 副作用-6）

- **严重度**: P1
- **问题摘要**: v3.0 修正了 `airy_err_t` 定位声明（→ airy_types.h:41），但未修正 cognition_types.h 的内容描述。SSoT L73 和 06-iron9 L70 均声称 cognition_types.h 含 `LLM 推理阶段枚举 + Token 能效指标结构 + GPU/NPU 能力描述符`，实际文件（38 行）仅含 `airy_q16_t` + CoreLoopThree 枚举 + Thinkdual 枚举。
- **证据位置**:
  - SSoT `120-cross-project-code-sharing.md:73`: 声明含 `LLM 推理阶段枚举 + 上下文结构 + Token 能效指标 + GPU/NPU 描述符`
  - `06-iron9-shared-model.md:70`: 同样声明
  - `06-iron9-shared-model.md:249`: `/* LLM 推理阶段枚举：PREFILL / DECODE / SPECULATIVE */`
  - 实际 `cognition_types.h`（38 行）：仅 `airy_q16_t` + `enum airy_cog_phase` + `enum airy_think_mode`
- **影响范围**: 开发者按文档引用 `#include <airymax/cognition_types.h>` 获取 LLM/Token/GPU/NPU 类型将编译失败
- **工作量估算**: ~2h（修正 SSoT L73 + 06-iron9 L70/L246-250 描述）

#### P1-v4-4：闭源手册 32 处 `AgentRT/` 大写路径未清理（v3.0 副作用-4）

- **严重度**: P1
- **问题摘要**: v3.0 域2 清理了 docs/AirymaxRT 中的 `AgentRT/`（60→5），但未清理闭源手册中的 32 处 `AgentRT/`。其中 L3030-3036 许可证表使用 `AgentRT/agentos/` 路径——双重错误（大写 + 旧内层目录名）。
- **证据位置**:
  - Grep `AgentRT/` in `agentrt工程标准规范手册.md` → 32 occurrences
  - `手册:1472`: `OpenAirymax/AgentRT/`（应为 `agentrt/`）
  - `手册:3030-3036`: `AgentRT/agentos/atoms/` 等（应为 `agentrt/agentrt/atoms/` 等）
  - `手册:1697`: `--prefix=AgentRT/agentrt/atoms/`（应为 `agentrt/`）
- **影响范围**: Linux 大小写敏感，32 处路径断链
- **工作量估算**: ~3h（32 处路径修正）

#### P1-v4-5：02-l2 IPC 头字段文档引用错误枚举名（v3.0 副作用-3）

- **严重度**: P1
- **问题摘要**: 02-l2 IPC 头结构体已对齐 SSoT，但字段注释仍引用 L2 特有的 `are_msg_type_t` 和 `ARE_FLAG_*`，而非 [SC] SSoT 的 `enum airy_ipc_op` 和 `AIRY_IPC_F_*`。
- **证据位置**:
  - `02-l2-service-protocol.md:98`: `@opcode: Operation code; see enum are_msg_type_t.`
  - `02-l2-service-protocol.md:99`: `@flags: Message flags (ARE_FLAG_*).`
  - `02-l2-service-protocol.md:113`: `opcode` 注释 `见 are_msg_type_t`
  - `02-l2-service-protocol.md:114`: `flags` 注释 `ARE_FLAG_*`
  - [SC] `ipc.h:25`: `enum airy_ipc_op`（SSoT 枚举）
  - [SC] `ipc.h:33`: `AIRY_IPC_F_NOWAIT` 等（SSoT 标志位）
- **影响范围**: 结构体布局对齐但字段语义引用不一致
- **工作量估算**: ~1h（修正 4 处字段注释引用）

#### P1-v4-6：airy_types.h `airy_ipc_header_t` 第三种 IPC 头类型未入 SSoT

- **严重度**: P1
- **问题摘要**: `airy_types.h:147-169` 定义了 `airy_ipc_header_t`（12 字段，`uint32_t/uint64_t/char`，无 packed，无 _Static_assert，~200+ 字节），这是第三种 IPC 头类型，SSoT 未提及。SSoT 仅提及 [SC] `struct airy_ipc_msg_hdr`（128B，9 字段）和 [IND] `are_ipc_message_header_t`（128B，14 字段，已废弃）。`airy_ipc_header_t` 使用相同 magic 值但布局完全不同。
- **证据位置**:
  - `airy_types.h:147-159`: `airy_ipc_header_t` 定义（12 字段，`uint32_t magic` + `uint32_t version` + ... + `char source[64]` + `char target[64]` + ...）
  - `airy_types.h:165-169`: `airy_ipc_message_t` 包装结构
  - SSoT `120-cross-project-code-sharing.md:440`: 仅提及 `airy_ipc_msg_hdr`（9 字段）和 `are_ipc_message_header_t`（14 字段），未提及 `airy_ipc_header_t`
- **影响范围**: 三种 IPC 头类型共存，SSoT 未覆盖第三种，开发者可能混淆
- **工作量估算**: ~3h（SSoT 补充 `airy_ipc_header_t` 定位说明 + 明确三层 IPC 头关系）

#### P1-v4-7：`AIRY_EINTR` 文档值(-4)与别名值(-19)不一致（R1-1）

- **严重度**: P1
- **问题摘要**: R1-1 残留项。03-protocol-contract.md:711 表值 `AIRY_EINTR = -4`（POSIX EINTR=4 负值），但 error.h:83-84 别名 `AIRY_EINTR = AIRY_ERR_INTERRUPTED = -19`。-4 是 POSIX 正确值但未被使用，-19 是实际别名值但非 POSIX。`AIRY_EINTR` 未入 airy_types.h SSoT 权威源。
- **证据位置**:
  - `03-protocol-contract.md:711`: `AIRY_EINTR | -4`
  - `error.h:83-84`: `#define AIRY_EINTR AIRY_ERR_INTERRUPTED`
  - `error.h:176-177`: `#define AIRY_ERR_INTERRUPTED (-19)`
  - Grep `AIRY_EINTR` in `airy_types.h` → 0 matches（未入 SSoT）
- **影响范围**: 文档值与源码值不一致，`AIRY_EINTR` 未入 SSoT 权威源
- **工作量估算**: ~1h（将 `AIRY_EINTR` 加入 airy_types.h 为 POSIX -4 + 修正 error.h 别名 + 修正文档表值）

#### P1-v4-8：`AIRY_EFAULT` 在源码中未定义（R1-1）

- **严重度**: P1
- **问题摘要**: R1-1 残留项。03-protocol-contract.md:707 表值 `AIRY_EFAULT = -14`，但 `AIRY_EFAULT` 在源码中**完全未定义**（airy_types.h 和 error.h 均无定义）。Grep `AIRY_EFAULT` in agentrt 源码 → 0 matches。-14 实际是 `AIRY_ERR_OVERFLOW`（error.h:162）。
- **证据位置**:
  - `03-protocol-contract.md:707`: `AIRY_EFAULT | -14`
  - Grep `AIRY_EFAULT` in `agentrt` → No matches found
  - `error.h:162`: `#define AIRY_ERR_OVERFLOW (-14)` — -14 实际归属
- **影响范围**: 文档引用未定义宏，开发者使用 `AIRY_EFAULT` 将编译失败
- **工作量估算**: ~1h（在 airy_types.h 添加 `AIRY_EFAULT=(-14)` POSIX 定义 + 修正 error.h 冲突）

#### P1-v4-9：R4-2 sync_compat.h 修正被 `#ifndef AIRY_RT_PLATFORM_H` 屏蔽

- **严重度**: P1
- **问题摘要**: v3.0 延期项 R4-2。`sync_compat.h:32` 和 `:439` 的修正代码被 `#ifndef AIRY_RT_PLATFORM_H` 条件编译屏蔽。当 `platform.h` 被先包含时（正常情况），`AIRY_RT_PLATFORM_H` 已定义，sync_compat.h 的修正代码被跳过，修正对生产代码无效。
- **证据位置**:
  - `platform.h:27-28`: `#ifndef AIRY_RT_PLATFORM_H / #define AIRY_RT_PLATFORM_H`
  - `sync_compat.h:32`: `#ifndef AIRY_RT_PLATFORM_H` — 修正代码开始
  - `sync_compat.h:432`: `#endif /* AIRY_RT_PLATFORM_H */` — 修正代码结束
  - `sync_compat.h:439`: `#ifndef AIRY_RT_PLATFORM_H` — 第二段修正
  - `sync_compat.h:503`: `#endif /* AIRY_RT_PLATFORM_H */`
- **影响范围**: v3.0 sync_compat 修正对生产代码无效
- **工作量估算**: ~3h（重构条件编译策略）

#### P1-v4-10：docs/AirymaxRT 5 处 `AgentRT/` 残留

- **严重度**: P1
- **问题摘要**: v3.0 将 docs/AirymaxRT 中 `AgentRT/` 从 60 处降至 5 处（4 文件），但 5 处残留未清理。
- **证据位置**:
  - `docs/AirymaxRT/30-interfaces/40-docker/README.md:1`
  - `docs/AirymaxRT/30-interfaces/50-examples/01-quickstart.md:2`
  - `docs/AirymaxRT/20-modules/10-contracts/01-agent-contract-schema.json:1`
  - `docs/AirymaxRT/20-modules/10-contracts/02-skill-contract-schema.json:1`
- **影响范围**: 5 处路径断链
- **工作量估算**: ~0.5h

### 4.3 P2 级问题（5 项）

#### P2-v4-1：IPC 头字段数不一致（SSoT 9 字段 vs 闭源手册 8 字段）

- **严重度**: P2
- **问题摘要**: SSoT `120-cross-project-code-sharing.md:440` 称 `struct airy_ipc_msg_hdr` 为"9 字段"（含 reserved），闭源手册 `手册:3341` 称"8 字段"（不含 reserved）。实际源码有 9 个命名字段（magic/opcode/flags/trace_id/timestamp_ns/src_task/dst_task/payload_len/reserved[84]）。
- **证据位置**:
  - SSoT `120-cross-project-code-sharing.md:440`: "9 字段"
  - 闭源手册 `agentrt工程标准规范手册.md:3341`: "8 字段"
  - 02-l2 `02-l2-service-protocol.md:56`: "8 字段"
- **影响范围**: 字段数描述不一致（是否含 reserved）
- **工作量估算**: ~0.5h

#### P2-v4-2：.bak 备份文件 43 处 `agentrt_` 残留（R4-3）

- **严重度**: P2
- **问题摘要**: v3.0 延期项 R4-3。`triple_coordinator.c.bak` 中 43 处 `agentrt_` 前缀残留，污染审计。
- **证据位置**: `agentrt/atoms/coreloopthree/src/cognition/critique/triple_coordinator.c.bak` → 43 occurrences
- **影响范围**: 审计污染
- **工作量估算**: ~0.1h（rm 删除）

#### P2-v4-3：闭源手册代码示例仍使用 AIRY_OK（v3.0 副作用-1 扩展）

- **严重度**: P2
- **问题摘要**: 闭源手册 L847 代码示例 `@return AIRY_OK (0) 成功` 使用已移除的 `AIRY_OK` 宏。
- **证据位置**: `手册:847`
- **影响范围**: 示例代码不可编译
- **工作量估算**: ~0.1h（`AIRY_OK` → `AIRY_EOK`）

#### P2-v4-4：§11.6 附加说明引用错误 SSoT 路径

- **严重度**: P2
- **问题摘要**: 闭源手册 L1520 附加说明引用 `docs/AirymaxRT/10-architecture/00-architectural-principles.md` 作为 SSoT，但实际 SSoT 为 `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md`。源码注释（8 个 [SC] 头文件 + airy_types.h）均引用 `docs/AirymaxOS/` 路径。
- **证据位置**:
  - `手册:1520`: `参见 SSoT docs/AirymaxRT/10-architecture/00-architectural-principles.md`
  - 源码 `ipc.h:6`: `SSoT: docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md`
  - 源码 `airy_types.h:39`: `详见 docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md`
- **影响范围**: SSoT 路径引用不一致
- **工作量估算**: ~0.1h

#### P2-v4-5：R2-1 `are_ipc_message_t` 便利包装类型保留

- **严重度**: P2
- **问题摘要**: v3.0 残留项 R2-1。`02-l2-service-protocol.md:131` 仍有 `are_ipc_message_t`（非 `are_ipc_message_header_t`）便利包装类型。v3.0 决定保留供第三方实现。
- **证据位置**: `02-l2-service-protocol.md:126-129`
- **影响范围**: L2 特有便利类型，保留供第三方实现
- **工作量估算**: 0h（保留决策）

---

## 5. 八维度 A-H 一致性验证矩阵

### A. 错误码 SSoT 一致性

| 检查项 | 权威源 | 文档 SSoT | 闭源手册 | 源码 | 一致性 |
|--------|--------|----------|---------|------|--------|
| `airy_err_t` 定位 | `airy_types.h:41` | `120-cross-project:82` ✅ | `手册:251,1520` ✅ | `airy_types.h:41` ✅ | ✅ |
| `AIRY_EINVAL` 值 | `airy_types.h:65` = -22 | `120-cross-project:84` ✅ | — | `airy_types.h:65` ✅ | ✅ |
| `AIRY_OK` 移除 | `error.h:43-46` 移除 | `TERMINOLOGY:212` ✅ | `手册:847,2803` ❌ | error.h ✅ | ❌ 闭源手册未同步 |
| `AIRY_ETIMEOUT` 命名 | **未定义** | 40 处使用 ❌ | — | 0 处定义 ❌ | ❌ 未定义宏 |
| `AIRY_ECANCELLED` 拼写 | `airy_types.h:81` 双L | `120-cross-project` 未提及 | — | error.h 单L别名 ❌ | ❌ 拼写分裂 |
| `AIRY_EINTR` 入 SSoT | **未入** airy_types.h | `03-protocol:711` = -4 | — | error.h 别名 = -19 ❌ | ❌ R1-1 |
| `AIRY_EFAULT` 定义 | **未定义** | `03-protocol:707` = -14 | — | 0 处定义 ❌ | ❌ R1-1 |
| 03-protocol §7.1 表值 | airy_types.h + error.h | 8+ 错误码值错误 ❌ | — | — | ❌ P0-v4-2 |
| 闭源手册 §4.9 分段 | error.h:106-118 | — | 完全不同方案 ❌ | — | ❌ P0-v4-3 |

**A 维度结论**: ❌ 不一致。`airy_err_t` 定位和核心 POSIX 码值已收敛（v3.0 有效），但存在 6 项严重不一致：`AIRY_ETIMEOUT` 未定义、`AIRY_ECANCELLED` 拼写分裂、`AIRY_EINTR`/`AIRY_EFAULT` 未入 SSoT、03-protocol §7.1 表值错误、闭源手册 §4.9 分段方案不同、闭源手册 AIRY_OK 未同步移除。

### B. IPC 消息头 SSoT 一致性

| 检查项 | [SC] ipc.h | SSoT 文档 | 02-l2 | 闭源手册 §34.2 | airy_types.h | 一致性 |
|--------|-----------|----------|-------|-------------|-------------|--------|
| 结构体名 | `struct airy_ipc_msg_hdr` | ✅ | ✅ | ✅ | `airy_ipc_header_t` ❌ | ⚠️ |
| 字段数 | 9 | 9 | 8(注释) | 8(注释) | 12 | ⚠️ 字段数描述不一致 |
| 类型 | `__u32/__u16/__u64/__u8` | ✅ | ✅ | ✅ | `uint32_t/uint64_t/char` ❌ | ⚠️ |
| packed | ✅ | ✅ | ✅ | ✅ | ❌ | ⚠️ |
| _Static_assert | ✅ | ✅ | ✅ | ✅ | ❌ | ⚠️ |
| 字段注释枚举引用 | `enum airy_ipc_op` | — | `are_msg_type_t` ❌ | ✅ | — | ❌ P1-v4-5 |
| magic 值 | `0x41524531u` | ✅ | ✅ | ✅ | ✅ | ✅ |

**B 维度结论**: ⚠️ 部分一致。[SC] SSoT 结构体在 ipc.h、SSoT 文档、02-l2、闭源手册间已对齐（v3.0 有效），但存在 3 项问题：02-l2 字段注释引用错误枚举名、airy_types.h 第三种 IPC 头未入 SSoT、字段数描述不一致（9 vs 8）。

### C. 函数前缀规则一致性

| 检查项 | SSoT (06-iron9 §3.12) | coding_conventions §4.4.2 | 闭源手册 §11.6 | 源码 | 一致性 |
|--------|----------------------|--------------------------|-------------|------|--------|
| `airy_*` [SC]+应用层 | ✅ 正确 | L2606 矛盾 ❌ | §11.6 已废止 ✅ | 1788 处 ✅ | ⚠️ |
| `are_*` 标准 ABI | ✅ 正确 | — | — | 230 处 ✅ | ✅ |
| `agentrt_*` 不使用 | ✅ 正确 | — | §11.6 已废止 ✅ | 0 处(.c/.h) ✅ | ✅ |
| `agentos_*` 废弃 | ✅ 正确 | — | §11.6.3 BAN-342 仍活跃 ❌ | 0 处 ✅ | ❌ P0-v4-4 |
| `airymaxos_*` 废弃 | ✅ 正确 | L2601 使用大写 `AIRYMAXOS_*` ⚠️ | — | 0 处 ✅ | ⚠️ |

**C 维度结论**: ⚠️ 部分一致。源码前缀落地正确（v3.0 清零有效），但 SSoT coding_conventions §4.4.2 内部矛盾未修复（P1-v4-2），闭源手册 BAN-342 仍活跃（P0-v4-4）。

### D. 路径引用一致性

| 检查项 | 权威源路径 | docs/AirymaxRT | 闭源手册 | 源码注释 | 一致性 |
|--------|----------|---------------|---------|---------|--------|
| `agentrt/daemons/` | `agentrt/daemons/` | 0 处 `daemon/` ✅ | — | — | ✅ |
| `AgentRT/` 大写 | `agentrt/` 小写 | 5 处残留 ❌ | 32 处 ❌ | — | ❌ P1-v4-4/v4-10 |
| `docs/AirymaxOS/` | SSoT 所在 | 5 处交叉引用 ✅ | L1520 引用 `docs/AirymaxRT/` ❌ | 8 处 ✅ | ⚠️ |
| `docs/AirymaxAgentOS/` | `docs-closed/agentrt-linux/` | — | 7 处 ❌ (R3-2) | — | ❌ |
| `AgentRT/agentos/` 双重错误 | `agentrt/agentrt/` | — | L3030-3036 ❌ | — | ❌ |

**D 维度结论**: ❌ 不一致。`daemon/` → `daemons/` 已修复，但 `AgentRT/` 大写在闭源手册 32 处 + docs/AirymaxRT 5 处未清理，`docs/AirymaxAgentOS/` 7 处未修复（R3-2），闭源手册 L3030-3036 双重路径错误。

### E. 术语一致性

| 检查项 | TERMINOLOGY.md | docs 正文 | 闭源手册 | 源码 | 一致性 |
|--------|---------------|----------|---------|------|--------|
| Cupola 单/复数 | — | 0 处单数 ✅ | — | — | ✅ |
| `AIRY_ETIMEOUT` vs `AIRY_ETIMEDOUT` | L209 用 `ETIMEDOUT` ✅ | 40 处 `ETIMEOUT` ❌ | — | 20 处 `ETIMEDOUT` ✅ | ❌ P0-v4-1 |
| `AIRY_ECANCELLED` vs `AIRY_ECANCELED` | — | — | — | 双拼写共存 ❌ | ❌ P1-v4-1 |
| `AIRY_OK` 废弃 | L212 声明废弃 ✅ | — | L847, L2803 仍用 ❌ | error.h 已移除 ✅ | ❌ P0-v4-5 |
| 12 daemon / 38 仓 / 0.1.1 | — | — | L40 16→12 修正 ✅, L9 29→38 修正 ✅ | — | ✅ |

**E 维度结论**: ⚠️ 部分一致。Cupola 和版本号已统一，但 `AIRY_ETIMEOUT`/`AIRY_ETIMEDOUT` 命名分裂（P0）、`AIRY_ECANCELLED`/`AIRY_ECANCELED` 拼写分裂（P1）、`AIRY_OK` 废弃声明未全面落地（P0）。

### F. [SC] 6 头文件清单一致性

| 检查项 | SSoT 声明 | 实际目录 | 06-iron9 | 闭源手册 | 一致性 |
|--------|---------|---------|---------|---------|--------|
| 6 头文件清单 | `120-cross-project:67-76` | `agentrt/commons/include/airymax/` 6 文件 ✅ | ✅ 34 处引用 | ✅ 19 处引用 | ✅ |
| cognition_types.h 内容描述 | L73 声明含 LLM/Token/GPU/NPU | 实际仅 q16+枚举 ❌ | L70 同样失实 ❌ | — | ❌ P1-v4-3 |
| bpf_struct_ops.h 标注 | "非 [SC] 核心" ✅ | 存在 ✅ | — | — | ✅ |
| uapi_compat.h 标注 | "辅助文件" ✅ | 存在 ✅ | — | — | ✅ |

**F 维度结论**: ⚠️ 部分一致。6 头文件清单三方一致（v2.0/v3.0 修正有效），但 cognition_types.h 内容描述在 SSoT 和 06-iron9 中均失实（P1-v4-3）。

### G. 错误码值交叉验证

| 错误码 | airy_types.h | error.h | 03-protocol §7.1 | 闭源手册 §4.9 | 一致性 |
|--------|-------------|---------|-----------------|-------------|--------|
| `AIRY_EOK`/`AIRY_SUCCESS` | 0 / 0 | (移除 AIRY_OK) | 0 ✅ | §4.9 `AIRY_SUCCESS` ✅ | ✅ |
| `AIRY_EINVAL` | -22 ✅ | — | -22 ✅ | — | ✅ |
| `AIRY_ENOMEM` | -12 ✅ | — | — | — | ✅ |
| `AIRY_ETIMEDOUT` | -110 ✅ | — | -110 ✅ | — | ✅ |
| `AIRY_EBADF` | 未定义 | -112(别名) | -9 ❌ | — | ❌ |
| `AIRY_ENOSYS` | 未定义 | 未定义 | -38 ❌ | — | ❌ |
| `AIRY_EFAULT` | 未定义 | 未定义 | -14 ❌ | — | ❌ |
| `AIRY_ECANCELED` | — | -47(别名) | -125 ❌ | — | ❌ |
| `AIRY_EINTR` | 未定义 | -19(别名) | -4 ❌ | — | ❌ |
| `AIRY_ECONFLICT` | 未定义 | 未定义 | -4096 ❌ | — | ❌ |
| `AIRY_ENOTINIT` | -9 ✅ | — | -4097 ❌ | — | ❌ |
| `AIRY_ERESOURCE` | 未定义 | -102(别名) | -4098 ❌ | — | ❌ |
| 分段方案 | — | -1~-99/-100~-199/... | — | -1001~-1099/... ❌ | ❌ |

**G 维度结论**: ❌ 严重不一致。核心 POSIX 码值（EINVAL/ENOMEM/ETIMEDOUT）在源码和文档间一致（v3.0 有效），但 03-protocol §7.1 表中 8+ 个码值全部错误，闭源手册 §4.9 分段方案与 error.h 完全不同。

### H. v3.0 修正副作用跨域检测

| 副作用 | 触发域 | 影响域 | 严重度 | 状态 |
|--------|--------|--------|--------|------|
| 副作用-1: 闭源手册 AIRY_OK 未同步 | 域1 | 域3 | P0 | ❌ 检测到 |
| 副作用-2: BAN-342 仍活跃 | 域3 | 域3 | P0 | ❌ 检测到 |
| 副作用-3: 02-l2 字段注释错误 | 域2 | 域2 | P1 | ❌ 检测到 |
| 副作用-4: 闭源手册 AgentRT/ 未清理 | 域2 | 域3 | P1 | ❌ 检测到 |
| 副作用-5: coding_conventions 矛盾未修 | 域1 | SSoT | P1 | ❌ 检测到 |
| 副作用-6: cognition_types.h 描述未修 | 域1 | SSoT+06-iron9 | P1 | ❌ 检测到 |

**H 维度结论**: ❌ 检测到 6 项跨域副作用。v3.0 各域修正在其域内有效，但跨域同步不完整，特别是在闭源手册（域3）中残留较多 v3.0 域1/域2 修正的未同步项。

---

## 6. 残留项状态复核

| 残留项 | v3.0 状态 | v4.0 验证 | 变化 |
|--------|---------|---------|------|
| **R1-1**: `AIRY_EINTR`/`AIRY_EFAULT` 未入 SSoT | P2 延期 | ❌ **仍存在，升级为 P1**。`AIRY_EINTR` 别名值(-19)与文档值(-4)不一致；`AIRY_EFAULT` 完全未定义 | 升级 P2→P1 |
| **R1-2**: 03-protocol §7.1 表值不一致 | P2 延期 | ❌ **仍存在，升级为 P0**。不仅 4 个码值错误，而是 8+ 个码值错误或未定义，且与闭源手册 §4.9 错误分段方案关联 | 升级 P2→P0 |
| **R1-3**: ~15 文件引用 `include/airymax/error.h` | P2 延期 | ✅ **已解决**。Grep `include/airymax/error.h` 全项目 → 0 matches。SSoT L85 改为声明 `airymax/error.h` 为"规划中路径，尚未创建" | 已解决 |
| **R2-1**: `are_ipc_message_t` 便利包装保留 | P2 保留 | ✅ **确认保留**。`02-l2:126-129` 仍保留，v3.0 决定有效 | 保留 |
| **R3-2**: 7 处 `docs/AirymaxAgentOS/` 路径 | P1 延期 | ❌ **仍存在**。闭源手册 L20/2243/4379/4393/4450/4473/4494 共 7 处 | 未修复 |
| **R4-2**: sync_compat.h 被屏蔽 | P1 延期 | ❌ **仍存在**。`#ifndef AIRY_RT_PLATFORM_H` 屏蔽修正 | 未修复 |
| **R4-3**: .bak 文件 43 处 agentrt_ | P2 延期 | ❌ **仍存在**。`triple_coordinator.c.bak` 43 处 | 未修复 |

---

## 7. 修正后评分预估

### 7.1 评分变化轨迹

| 版本阶段 | 综合评分 | 级别 | 变化 | 主要原因 |
|---------|---------|------|------|---------|
| v1.0（初始审查） | 65 | C+ | — | 8 项 P0 + 多项 P1/P2 |
| v2.0（修正后） | 72 | B- | +7 | 9/10 P0 修正 |
| v3.0（复审） | 66 | C+ | -6 | 新发现 10 P0 + 19 P1 + 18 P2 |
| v3.0（修正后预估） | ~76 | B | +10 | 10 P0 全部清零 + 主要 P1 修正 |
| **v4.0（本次深化复审）** | **~71** | **B-** | **-5** | **v3.0 修正 21/23 持久，但发现 5 P0 + 10 P1 + 6 副作用** |

### 7.2 评分下调分析

v4.0 评分从 v3.0 修正后预估的 ~76/B 下调至 ~71/B-，下调 5 分，原因如下：

| 下调因素 | 扣分 | 说明 |
|---------|------|------|
| `AIRY_ETIMEOUT` 未定义宏 40 处引用（P0-v4-1） | -1.5 | v3.0 误判此项为"已通过"，实际为系统性命名分裂 |
| 03-protocol §7.1 表 8+ 码值错误 + 闭源手册 §4.9 分段方案不同（P0-v4-2/v4-3） | -1.5 | R1-2 比预期更严重，且与闭源手册 §4.9 关联形成系统性分裂 |
| BAN-342 仍活跃 + LOG-09 AIRY_OK 未同步（P0-v4-4/v4-5） | -1.0 | v3.0 副作用——域1 修正未同步到域3 |
| cognition_types.h 描述失实 + coding_conventions 矛盾 + 闭源手册 32 处 AgentRT/（P1-v4-2/v4-3/v4-4） | -1.0 | v3.0 遗漏 + 副作用 |

### 7.3 维度评分

| 维度 | v3.0 修正后 | v4.0 复审 | 变化 | 主要问题 |
|------|-----------|----------|------|---------|
| 规范声明层（35%） | 78 | 73 | -5 | AIRY_ETIMEOUT 命名分裂 + BAN-342 矛盾 + cognition_types.h 描述失实 |
| 方案设计层（40%） | 77 | 72 | -5 | 03-protocol §7.1 表值错误 + §4.9 分段方案不同 + 02-l2 字段注释错误 |
| 实现落地层（25%） | 72 | 70 | -2 | AIRY_EINTR/EFAULT 未入 SSoT + R4-2 sync_compat 屏蔽 |
| **加权综合** | **~76** | **~71** | **-5** | — |

### 7.4 评分恢复路径

要将评分从 ~71/B- 提升至 ≥80/B（M1 代码开发就绪阈值），需按以下优先级修复：

| 优先级 | 修复项 | 预估工时 | 预期加分 |
|--------|--------|---------|---------|
| 1 | P0-v4-1: 40 处 `AIRY_ETIMEOUT` → `AIRY_ETIMEDOUT` | ~4h | +1.5 |
| 2 | P0-v4-2/v4-3: 重写 03-protocol §7.1 表 + 闭源手册 §4.9 分段 | ~7h | +1.5 |
| 3 | P0-v4-4/v4-5: 废止 BAN-342 + 清理闭源手册 AIRY_OK | ~3h | +1.0 |
| 4 | P1-v4-1: 统一 `AIRY_ECANCELED` 拼写 | ~2h | +0.5 |
| 5 | P1-v4-2: 修复 coding_conventions §4.4.2 矛盾 | ~2h | +0.5 |
| 6 | P1-v4-3: 修正 cognition_types.h 描述 | ~2h | +0.5 |
| 7 | P1-v4-4: 清理闭源手册 32 处 AgentRT/ | ~3h | +0.5 |
| 8 | P1-v4-7/v4-8: AIRY_EINTR/EFAULT 入 SSoT | ~2h | +0.5 |
| 9 | P1-v4-5/v4-6/v4-9/v4-10 + P2 全部 | ~6h | +1.0 |
| 10 | 残留项 R3-2/R4-2/R4-3 | ~6h | +0.5 |
| **合计** | — | **~37h** | **+9.0** |

完成全部修复后预估评分：71 + 9.0 = **~80/B**，可达 M1 就绪阈值。

### 7.5 结论

agentrt 项目在 v3.0 修正后，错误码 SSoT 核心值收敛（POSIX errno 负值）、IPC 头 SSoT 对齐、函数前缀清零等方面取得有效进展（21/23 项持久）。但 v4.0 深化跨域审查发现：

1. **v3.0 误判 `AIRY_ETIMEOUT` 为正确命名**（实际源码使用 `AIRY_ETIMEDOUT`），导致 40 处文档引用未定义宏
2. **R1-2 残留比预期更严重**（8+ 码值错误 + 闭源手册 §4.9 分段方案系统性分裂）
3. **v3.0 引入 6 项跨域副作用**（闭源手册 AIRY_OK 未同步、BAN-342 仍活跃、02-l2 字段注释错误等）
4. **v3.0 遗漏 coding_conventions §4.4.2 内部矛盾**（P1-v3-3 未修复）

**agentrt 项目当前状态不满足 1.0.1 M1 代码开发就绪条件（≥80/B），但距阈值约 9 分（~37h 工作量），可通过系统性修复 P0-v4-1~5 达到条件性通过。**

建议优先修复 P0-v4-1（`AIRY_ETIMEOUT` 命名统一）和 P0-v4-2/v4-3（错误码表值 + 分段方案统一），这两项是恢复错误码 SSoT 完整性的关键阻塞项。

---

## 附录：Grep/Read 命令执行记录汇总

| # | 检查项 | 方法 | 范围 | 结果 |
|---|--------|------|------|------|
| 1 | `AIRY_ETIMEDOUT` in airy_types.h | Grep | 源码 | 1 match (L76) |
| 2 | `AIRY_ETIMEOUT` in docs | Grep count | docs/ | 40 occurrences / 21 files |
| 3 | `AIRY_ETIMEDOUT` in docs | Grep count | docs/ | 18 occurrences / 8 files |
| 4 | `AIRY_ETIMEOUT` in agentrt .c/.h | Grep count | agentrt/ | 1 occurrence / 1 file |
| 5 | `AIRY_ETIMEDOUT` in agentrt .c/.h | Grep count | agentrt/ | 20 occurrences / 14 files |
| 6 | `#define AIRY_ETIMEOUT` in agentrt | Grep | agentrt/ | 0 matches (未定义) |
| 7 | `AIRY_EINTR`/`AIRY_EFAULT` in airy_types.h | Grep | 源码 | 0 matches (未入 SSoT) |
| 8 | `AIRY_EINTR`/`AIRY_EFAULT` in SSoT | Grep | SSoT 文档 | 0 matches |
| 9 | `ECANCEL` in airy_types.h | Grep | 源码 | 2 matches (L53, L81 双L) |
| 10 | `ECANCEL` in error.h | Grep | 源码 | 4 matches (L73, L80-81 单L, L150) |
| 11 | `AgentRT/` in docs/AirymaxRT | Grep count | docs/AirymaxRT | 5 occurrences / 4 files |
| 12 | `AgentRT/` in docs-closed/agentrt | Grep count | docs-closed/agentrt | 255 occurrences / 16 files |
| 13 | `AgentRT/` in 闭源手册 | Grep content | 手册 | 32 occurrences |
| 14 | `agentrt/daemon/` in docs/AirymaxRT | Grep count | docs/AirymaxRT | 0 matches ✅ |
| 15 | `AirymaxAgentOS` in 闭源手册 | Grep content | 手册 | 7 occurrences (R3-2) |
| 16 | `agentos_` in 07-subsystem-specs/ | Grep | 闭源文档 | 0 matches ✅ |
| 17 | `agentos_` in 06-contracts/ | Grep | 闭源文档 | 0 matches ✅ |
| 18 | `BAN-341`/`BAN-342` in 闭源手册 | Grep content | 手册 | 12 matches (仍活跃) |
| 19 | `struct airy_ipc_msg_hdr` in 02-l2 | Grep content | 开源文档 | 14 occurrences ✅ |
| 20 | `struct airy_ipc_msg_hdr` in 闭源手册 | Grep content | 手册 | 7 occurrences ✅ |
| 21 | `are_ipc_message_header` in 闭源手册 | Grep content | 手册 | 7 occurrences (含迁移说明) |
| 22 | `AIRY_OK` in error.h | Grep | 源码 | 0 matches ✅ (已移除) |
| 23 | `AIRY_OK` in 闭源手册 | Grep content | 手册 | L847, L2803 (未同步) |
| 24 | `agentrt_` in *.bak | Grep count | agentrt/ | 43 occurrences / 1 file (R4-3) |
| 25 | `docs/AirymaxOS/` in agentrt .c/.h | Grep content | 源码 | 8 occurrences (正确 SSoT 路径) |
| 26 | `airymax/error.h` 全项目 | Grep | 全项目 | SSoT L85 提及（规划中路径） |
| 27 | `include/airymax/error.h` 全项目 | Grep | 全项目 | 0 matches (R1-3 已解决) |
| 28 | cognition_types.h 实际内容 | Read | 源码 | 38 行，仅 q16 + 枚举 |
| 29 | `docs/AirymaxRT/50-engineering-standards` | readlink -f | 文件系统 | → `docs/AirymaxOS/50-engineering-standards` (符号链接) |
| 30 | `airy_types.h` 位置 | Glob | agentrt/ | `agentrt/commons/include/airy_types.h` (非 airymax/ 子目录) |

---

<!-- 审查报告结束 -->
<!-- © 2025-2026 SPHARX Ltd. All Rights Reserved. -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0 -->
