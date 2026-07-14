<!-- SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0 -->
<!-- SPDX-Copyright: Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved. -->
<!-- 保密级别：机密（Confidential）—— 仅限 SPHARX Ltd. 内部工程审查使用 -->
<!-- 版本：3.0 | 日期：2026-07-14 | 审查 Agent：Agent 4（跨文档一致性与 SSoT） -->

# Airymax 项目 v3.0 审查报告 —— Agent 4：agentrt 跨文档一致性与 SSoT 复审

> **版权声明**: Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved. "From data intelligence emerges."  
> **保密级别**: 机密（Confidential）—— 仅限 SPHARX Ltd. 内部工程审查使用，禁止外传  
> **版本**: 3.0  
> **日期**: 2026-07-14  
> **SPDX-License-Identifier**: AGPL-3.0-or-later OR Apache-2.0  
> **审查范围**: `docs/AirymaxRT/` + `docs-closed/agentrt/` + `agentrt/` [SC] 6 头文件 + `docs/AirymaxOS/50-engineering-standards/`（仅引用）  
> **审查性质**: 仅审查，不修改任何文件  
> **基线**: v2.0 修正后预估 72/B-（`docs-closed/agentrt/_review_v2.0/fix-verification-report.md`）

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [A. 错误码 SSoT 跨文档/源码一致性](#2-a-错误码-ssot-跨文档源码一致性)
3. [B. [SC] 6 头文件清单三方一致性](#3-b-sc-6-头文件清单三方一致性)
4. [C. IPC magic / AGTS magic / SCHED_EXT 跨文档一致性](#4-c-ipc-magic--agts-magic--sched_ext-跨文档一致性)
5. [D. 函数前缀三层分层落地](#5-d-函数前缀三层分层落地)
6. [E. 文件路径引用完整性](#6-e-文件路径引用完整性)
7. [F. 术语一致性](#7-f-术语一致性)
8. [G. IRON-9 v2 三层模型落地](#8-g-iron-9-v2-三层模型落地)
9. [H. v2.0 修正副作用扫描](#9-h-v20-修正副作用扫描)
10. [v3.0 新发现问题清单](#10-v30-新发现问题清单)
11. [修正后综合评分变化](#11-修正后综合评分变化)

---

## 1. 执行摘要

本报告为 Airymax 项目 v3.0 审查的 Agent 4 专项报告，聚焦 agentrt 跨文档一致性与 SSoT（单一真值源）复审。审查覆盖 8 个维度（A-H），所有结论均附 `文件路径:L行号` 证据，所有 Grep 命令均已实际执行并记录匹配数。

### 核心结论

**v2.0 修正有效部分**（6 项已验证通过）：

| # | 修正项 | 验证结果 | 证据 |
|---|--------|---------|------|
| 1 | [SC] 6 头文件清单三方一致 | ✅ 通过 | 闭源手册 19 处引用、06-iron9 文档 34 处引用，均与 SSoT 一致 |
| 2 | 错误码命名统一（AIRY_ETIMEOUT） | ✅ 通过 | AirymaxRT 中 AIRY_ETIMEOUT 23 处、AIRY_ETIMEDOUT 0 处 |
| 3 | 闭源手册 agentos_/AGENTOS_ 残留 | ✅ 通过 | 闭源手册 0 处残留 |
| 4 | Cupola 单数修正 | ✅ 通过 | AirymaxRT 中 `[^s]Cupola[^s]` 0 处匹配 |
| 5 | 源码 agentos_/airymaxos_ 残留 | ✅ 通过 | agentrt .c/.h 中 0 处残留 |
| 6 | v2.0 修正的 5 类旧路径 | ✅ 通过 | 全部 0 残留 |

**v3.0 新发现问题**（18 项）：

| 级别 | 数量 | 关键问题 |
|------|------|---------|
| **P0** | **7 项** | SSoT 错误码 5+ 套方案并行、源码与文档值冲突、airy_err_t 定位错误、SSoT 权威文件不存在、IPC 头违规遗漏 2 处、闭源手册 §11.6 公然违反 SSoT 前缀规则 |
| **P1** | **7 项** | AgentRT/ 大写断链 60 处、AirymaxAgentOS/ 断链 7 处、函数前缀规则内部矛盾、ARE_IPC_MAGIC 命名不一致、源码错误码语义冲突、cognition_types.h 虚假声明、AIRY_OK 仍在源码中使用 |
| **P2** | **4 项** | 任务清单断链、TERMINOLOGY.md 缺失、.bak 残留 43 处、mainpage.dox 废弃前缀 |

### 综合评分

| 版本 | 评分 | 级别 | 变化 |
|------|------|------|------|
| v2.0（修正前） | 63 | C+ | — |
| v2.0（修正后预估） | 72 | B- | +9（修正有效） |
| **v3.0（本次复审）** | **66** | **C+** | **-6（新发现 7 项 P0）** |

评分下调原因：v2.0 修正虽在已识别范围内有效，但 v3.0 深度审查发现 SSoT 错误码体系存在系统性崩溃（5+ 套方案并行、权威源文件不存在、源码与文档值严重不一致），以及闭源手册 §11.6 作为"强制规则"公然违反 SSoT 函数前缀规则，属于工程标准层面的根本性矛盾。

---

## 2. A. 错误码 SSoT 跨文档/源码一致性

### 2.1 SSoT 权威声明

SSoT 权威文件 `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md` 做出以下声明：

- **L73**: `cognition_types.h` 含"统一错误码类型（`airy_err_t` = `int32_t`）"
- **L81**: "所有 `AIRY_E*` 错误码值唯一定义于 `include/airymax/error.h`（[SC] 补充共享头文件）"

### 2.2 实际验证

#### 2.2.1 airy_err_t 定位验证

| 声明位置 | 声明内容 | 实际验证 | 结果 |
|---------|---------|---------|------|
| `120-cross-project-code-sharing.md:73` | `airy_err_t` 在 `cognition_types.h` | `cognition_types.h` 完整 38 行，**0 匹配** `airy_err_t` | ❌ 声明失效 |
| `120-cross-project-code-sharing.md:81` | 权威源在 `include/airymax/error.h` | `Glob include/airymax/error.h` → **No file found** | ❌ 文件不存在 |
| 实际权威源 | — | `agentrt/commons/include/airy_types.h:40` → `typedef int32_t airy_err_t;` | ✅ 实际在此 |
| `error.h:38`（辅助确认） | — | `agentrt/commons/utils/error/include/error.h:38` 注释："airy_err_t 已在 airy_types.h 中定义（BAN-196 权威源）" | ✅ 确认 |

**Grep 命令执行记录**：
```
Grep pattern="airy_err_t" path="agentrt/commons/include/airymax/cognition_types.h" → No matches found (0)
Glob pattern="agentrt/commons/include/airymax/error.h" → No file found
Grep pattern="airy_err_t|AIRY_EINVAL|..." path="agentrt/commons/include/airy_types.h" → 6 lines matched
```

#### 2.2.2 错误码值跨文档/源码对比

| 错误码 | 文档 SSoT 值（方案 A） | 源码实际值 | 源码位置 | 结果 |
|--------|----------------------|----------|---------|------|
| `AIRY_EOK` | 0 | 0 | `airy_types.h` + `error.h:43` | ✅ 一致 |
| `AIRY_EINVAL` | -22 | **-1** | `airy_types.h:50` | ❌ 冲突 |
| `AIRY_ENOMEM` | -12 | **-2** | `airy_types.h:51` | ❌ 冲突 |
| `AIRY_ETIMEOUT` | -110 | **-6**（名为 `AIRY_ETIMEDOUT`） | `airy_types.h:55` | ❌ 命名+值冲突 |
| `AIRY_EPROTO` | — | -13 | `airy_types.h:62` | — |

**文档 SSoT 值来源**（方案 A）：
- `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md:420-427`：POSIX errno 负值（`AIRY_EINVAL=(-EINVAL)=-22`、`AIRY_ENOMEM=(-ENOMEM)=-12`、`AIRY_ETIMEDOUT=(-ETIMEDOUT)=-110`）
- `docs/AirymaxRT/10-architecture/00-architectural-principles.md:924-943`：同方案 A
- `docs/AirymaxRT/TERMINOLOGY.md:209`：同方案 A

#### 2.2.3 SSoT 50-engineering-standards 内部错误码方案并行（5+ 套）

| 方案 | 文件 | 行号 | AIRY_EINVAL | AIRY_ENOMEM | AIRY_ETIMEOUT | 风格 |
|------|------|------|------------|------------|-------------|------|
| **A** | `10-coding-style/C_Cpp_coding_style.md` | 420-427 | -22 | -12 | -110 | POSIX errno 负值 |
| **B** | `30-runtime-interfaces/runtime_interfaces.md` | 1753-1770 | **-1** | **-2** | **-11** | 自定义序列 |
| **C** | `10-coding-style/coding_conventions.md` | 2959-2981 | **-2** | **-4** | **-6** | 已废弃（自承认） |
| **D** | `50-project-erp/project_erp.md` | 987-1003 | — | — | — | 位掩码（`AIRY_ERROR_INVALID_PARAM=0x00010000`） |
| **声明** | `120-cross-project-code-sharing.md` | 81 | — | — | — | 指向不存在的 `include/airymax/error.h` |

**方案 C 自承认废弃**（`coding_conventions.md:2955`）：
> "以下旧定义仅作历史参考，**禁止在新代码中使用本节的数值**。正确数值以 `agentrt/commons/utils/error/include/error.h` 及上述参考文档为准。"

但方案 C 的废弃数值与源码 `airy_types.h` 的实际值高度重合（`AIRY_EINVAL=-2` vs 源码 `-1`、`AIRY_ENOMEM=-4` vs 源码 `-2`），说明源码可能受废弃方案影响。

#### 2.2.4 源码 error.h 内部冲突

| 宏 | 值 | 位置 | 冲突对象 |
|----|---|------|---------|
| `AIRY_OK` | 0 | `error.h:43` | 文档称"不再使用 AIRY_OK"（`TERMINOLOGY.md:212`） |
| `AIRY_ERR_UNKNOWN` | -1 | `error.h:46` | 与 `airy_types.h:50` `AIRY_EINVAL=-1` 同值 |
| `AIRY_ERR_PROTOCOL` | -900 | `error.h:493` | 与 `airy_types.h:62` `AIRY_EPROTO=-13` 语义重叠 |
| `AIRY_EPERM` | -10（重定义） | `error.h:88-89` | `#undef` 后覆盖 `airy_types.h` 的值 |

### 2.5 A 部分结论

SSoT 错误码体系处于**系统性崩溃**状态：
1. SSoT 声明的权威文件 `include/airymax/error.h` **不存在**
2. SSoT 声明 `airy_err_t` 在 `cognition_types.h`，实际在 `airy_types.h`
3. 50-engineering-standards 内部存在 **5+ 套并行方案**，数值互相矛盾
4. 源码实际值（`-1/-2/-6`）与文档 SSoT 值（`-22/-12/-110`）严重不一致
5. 源码 `error.h` 内部存在同值冲突和语义重叠

---

## 3. B. [SC] 6 头文件清单三方一致性

### 3.1 SSoT 权威清单

`docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md` §2.1（L67-76）定义 6 个 [SC] 核心头文件：

| # | 头文件 | 物理路径 |
|---|--------|---------|
| 1 | `memory_types.h` | `include/airymax/memory_types.h` |
| 2 | `security_types.h` | `include/airymax/security_types.h` |
| 3 | `cognition_types.h` | `include/airymax/cognition_types.h` |
| 4 | `sched.h` | `include/airymax/sched.h` |
| 5 | `ipc.h` | `include/airymax/ipc.h` |
| 6 | `syscalls.h` | `include/airymax/syscalls.h` |

### 3.2 三方一致性验证

| 文档 | 6 头文件引用数 | 一致性 | Grep 命令 |
|------|--------------|--------|---------|
| SSoT（`120-cross-project-code-sharing.md`） | 基准 | ✅ | — |
| 开源文档（`06-iron9-shared-model.md`） | 34 处 | ✅ 一致 | `Grep "memory_types\.h\|security_types\.h\|cognition_types\.h\|sched\.h\|ipc\.h\|syscalls\.h"` → 34 |
| 闭源手册（`agentrt工程标准规范手册.md`） | 19 处 | ✅ 一致 | `Grep "memory_types\.h\|..."` → 19 |
| 源码（`agentrt/commons/include/airymax/`） | 6 文件全部存在 | ✅ 一致 | `Glob` 逐文件确认 |

### 3.3 补充共享文件标注验证

| 文件 | 标注 | 验证 |
|------|------|------|
| `bpf_struct_ops.h` | "Supplementary shared file (NOT one of the 6 [SC] core headers)" | ✅ 正确标注 |
| `uapi_compat.h` | "NOT one of the 6 [SC] core shared contract layer headers" | ✅ 正确标注 |

### 3.4 B 部分结论

**[SC] 6 头文件清单三方一致，v2.0 修正有效。** ✅

但 `cognition_types.h` 的**内容描述**与实际不符（见 A 部分 P0-v3-3 和 P1-v3-6）：SSoT L73 和 `06-iron9-shared-model.md:70` 均称 `cognition_types.h` 含"统一错误码类型（`airy_err_t = int32_t`）"，但实际源码 38 行中**零匹配** `airy_err_t`。该文件仅含 `airy_q16_t` + CoreLoopThree 阶段枚举 + Thinkdual 模式枚举，不含错误码类型、LLM 推理阶段枚举、Token 能效指标结构、GPU/NPU 能力描述符。

---

## 4. C. IPC magic / AGTS magic / SCHED_EXT 跨文档一致性

### 4.1 IPC magic（0x41524531 'ARE1'）

| 来源 | 位置 | 值 | 结果 |
|------|------|---|------|
| 源码 `ipc.h` | L18-19 | `AIRY_IPC_MAGIC 0x41524531u` | ✅ |
| SSoT `120-cross-project-code-sharing.md` | §3.1 | `0x41524531` | ✅ |
| 开源 `06-iron9-shared-model.md` | L115 | `AIRY_IPC_MAGIC 0x41524531u` | ✅ |
| 开源 `06-ipc/README.md` | L34 | `AIRY_IPC_MAGIC 0x41524531u` | ✅ |
| 开源 `02-l2-service-protocol.md` | L60 | `ARE_IPC_MAGIC 0x41524531u` | ❌ **宏命名不一致**（ARE_ vs AIRY_） |

**Grep 执行记录**：
```
Grep pattern="AIRY_IPC_MAGIC|airy_ipc_msg_hdr|0x41524531" path="agentrt/commons/include/airymax/ipc.h" → 7 lines
```

### 4.2 AGTS magic（0x41475453 'AGTS'）

| 来源 | 位置 | 值 | 结果 |
|------|------|---|------|
| 源码 `sched.h` | L24-25 | `AIRY_TASK_MAGIC 0x41475453u` | ✅ |
| SSoT `120-cross-project-code-sharing.md` | §3.3 | `0x41475453` | ✅ |
| 开源 `06-iron9-shared-model.md` | L155 | `AIRY_TASK_MAGIC 0x41475453u` | ✅ |

**Grep 执行记录**：
```
Grep pattern="AIRY_TASK_MAGIC|SCHED_EXT|SCHED_AGENT|0x41475453" path="agentrt/commons/include/airymax/sched.h" → 7 lines
```

### 4.3 SCHED_EXT=7

| 来源 | 位置 | 声明 | 结果 |
|------|------|------|------|
| 源码 `sched.h` | L19-21 | `SCHED_EXT=7`，禁止定义 `SCHED_AGENT` 宏 | ✅ |
| SSoT `120-cross-project-code-sharing.md` | §3.4 | 复用 `SCHED_EXT=7`，禁止 `SCHED_AGENT` 宏 | ✅ |
| 开源 `06-iron9-shared-model.md` | L169-175 | 同上 | ✅ |

### 4.4 IPC 消息头结构体一致性

| 来源 | 结构体名 | 字段数 | 类型 | packed | _Static_assert | 结果 |
|------|---------|--------|------|--------|----------------|------|
| 源码 `ipc.h:67-80` | `airy_ipc_msg_hdr` | 8 | `__u32/__u16/__u64/__u8` | ✅ | ✅ | ✅ SSoT |
| SSoT `120-cross-project-code-sharing.md:343-356` | `airy_ipc_msg_hdr` | 8 | UAPI | ✅ | ✅ | ✅ |
| 开源 `06-iron9-shared-model.md:128-138` | `airy_ipc_msg_hdr` | 8 | UAPI | ✅ | ✅ | ✅ |
| 开源 `06-ipc/README.md:53-66` | `airy_ipc_msg_hdr` | 8 | UAPI | ✅ | ✅ | ✅（含迁移说明） |
| **开源 `02-l2-service-protocol.md:93-109`** | `are_ipc_message_header_t` | **13** | **`uint32_t`** | **❌** | **❌** | ❌ **三重违规** |
| **闭源手册 §34.2 L3334-3349** | `are_ipc_message_header_t` | **13** | **`uint32_t`** | **❌** | **❌** | ❌ **三重违规** |

**违规详情**（`02-l2-service-protocol.md:55-116`）：
- L60: `ARE_IPC_MAGIC`（应为 `AIRY_IPC_MAGIC`）
- L93: `typedef struct are_ipc_message_header`（应为 `struct airy_ipc_msg_hdr`，无 typedef）
- L94-108: 13 字段（应为 8 字段）、`uint32_t/uint16_t/uint64_t` 类型（应为 `__u32/__u16/__u64`）
- L108: 无 `__attribute__((packed))`
- L109: 无 `_Static_assert(sizeof(...) == 128)`（仅注释提及）

**违规详情**（闭源手册 §34.2 STD-02，L3328-3356）：
- L3330: `are_ipc_message_header_t`（作为"强制规则 STD-02"使用违规命名）
- L3334: `typedef struct are_ipc_message_header`（typedef + 违规命名）
- L3335-3348: 13 字段 + `uint32_t/uint16_t/uint64_t` 类型
- L3349: 无 `__attribute__((packed))`、无 `_Static_assert`
- L3354: 引用 `AIRY_ERR_PROTOCOL`（使用废弃的 `AIRY_ERR_*` 前缀）
- L2901: 另一处引用 `are_ipc_message_header_t.trace_id`

**Grep 执行记录**：
```
Grep pattern="are_ipc_message_header" path="docs/AirymaxRT" → 9 occurrences (8 in 02-l2-service-protocol.md + 1 in 06-ipc/README.md)
Grep pattern="are_ipc_message_header|ARE_IPC_MAGIC" path="docs-closed/agentrt/agentrt工程标准规范手册.md" → 5 occurrences
```

### 4.5 C 部分结论

magic 值（IPC/AGTS/SCHED_EXT）在源码和主流文档中**一致** ✅。但 IPC 消息头结构体在 **2 处文件**完整保留三重违规（命名/类型/布局），v2.0 修正遗漏了这两处。

---

## 5. D. 函数前缀三层分层落地

### 5.1 SSoT 函数前缀三层定义

`06-iron9-shared-model.md:260-279` §3.12 定义：

| # | 前缀 | 所属层级 | 用途 | 状态 |
|---|------|---------|------|------|
| 1 | `airy_*` | [SC] + 应用层 | 共享头文件结构体/宏/枚举 + 应用层函数 | ✅ 正确 |
| 2 | `are_*` | 标准 ABI 层 | 对外发布稳定 ABI 接口 | ✅ 正确 |
| 3 | ~~`agentrt_*`~~ | — | **不使用** | ✅ 正确 |
| 4 | ~~`agentos_*`~~ | — | **已废弃** | ✅ 正确 |
| 5 | ~~`airymaxos_*`~~ | — | **已废弃** | ✅ 正确 |

### 5.2 源码验证

| 前缀 | 源码 .c/.h 匹配数 | 状态 | Grep 命令 |
|------|-----------------|------|---------|
| `airy_` | **1788** 处（100 文件） | ✅ 活跃使用 | `Grep "\bairy_" glob="*.{c,h}" path="agentrt"` |
| `are_` | **230** 处（8 文件） | ✅ 活跃使用 | `Grep "\bare_\w" glob="*.{c,h}" path="agentrt"` |
| `agentrt_` | **0** 处（.c/.h） | ✅ 不使用 | `Grep "agentrt_" glob="*.{c,h}" path="agentrt"` → 仅 mainpage.dox 2 处 |
| `agentos_`/`airymaxos_` | **0** 处 | ✅ 已清除 | `Grep "agentos_\|airymaxos_" glob="*.{c,h}" path="agentrt"` |

**源码前缀落地与 SSoT 一致。** ✅

### 5.3 闭源手册 §11.6 严重违反 SSoT

**这是 v3.0 最严重的发现之一。** 闭源手册 `agentrt工程标准规范手册.md` §11.6（L1509-1544）以"强制规则"名义公然违反 SSoT 函数前缀规则：

| §11.6 声明 | SSoT 声明 | 矛盾性质 |
|-----------|---------|---------|
| L1509: "airy_ → agentrt_ 彻底改名规范" | `06-iron9:268`: `agentrt_*` **不使用** | **直接违反** |
| L1511: "核心决策 §v4.0: airy_ → agentrt_ 彻底改名" | `06-iron9:274`: `airy_*` 是 [SC] + 应用层**正确前缀** | **直接违反** |
| L1518: `airy_common` → `agentrt_common` | 源码实际使用 `airy_common` | **与源码矛盾** |
| L1521: `airy_error_t` → `agentrt_error_t` | 源码 `airy_types.h:40` 使用 `airy_err_t` | **与源码矛盾** |
| L1522: `AIRY_API` → `AGENTRT_API` | 源码使用 `AIRY_*` 宏 | **与源码矛盾** |
| L1531: "L1-L6 airy_ 零残留: grep airy_ → 0" | 源码有 1788 处 `airy_` | **要求删除全部正确前缀** |
| L1532: "L6 AIRY_ 宏零残留: grep AIRY_ → 0" | 源码大量使用 `AIRY_*` 宏 | **要求删除全部正确宏** |
| L1542: "BAN-342: 禁止改名后留有 airy_ 前缀残留" | SSoT 称 `airy_*` 是正确前缀 | **强制规则违反 SSoT** |

**关键矛盾分析**：
- §11.6 标题为"airy_ → agentrt_ 彻底改名"，要求将**正确的** `airy_` 前缀改为**SSoT 禁止的** `agentrt_` 前缀
- §11.6 的 BAN-342 规则要求"airy_ 零残留"，但 SSoT 明确规定 `airy_*` 是 [SC] + 应用层的正确前缀
- §11.6 的验证标准（L1531-1532）要求 grep `airy_` 和 `AIRY_` 返回 0，但源码有 1788 处 `airy_` 和大量 `AIRY_` 宏
- 如果执行 §11.6 的改名，将破坏整个代码库的 [SC] 共享契约层

**历史分析**：§11.6 标题中的 `airy_ → agentrt_` 改名方向与项目历史决策矛盾。项目实际执行的是 `agentos_ → airy_` 改名（已完成），而非 `airy_ → agentrt_` 改名。§11.6 可能是将 `agentos_ → agentrt_` 的旧决策误写为 `airy_ → agentrt_`。

### 5.4 SSoT §4.4.2 函数前缀规则内部矛盾

`docs/AirymaxOS/50-engineering-standards/10-coding-style/coding_conventions.md` §4.4.2（L2595-2607）存在内部矛盾：

| 行号 | 内容 | 矛盾 |
|------|------|------|
| L2599 | `airy_*` 用于 [SC]/[SS]，agentrt + agentrt-linux 共享 | — |
| L2601 | `AIRYMAXOS_*` 用于 agentrt-linux [IND] 专属宏 | 与 `06-iron9:270` `~~airymaxos_*~~` 已废弃矛盾（大写宏 vs 小写函数前缀） |
| L2606 | agentrt-linux [IND] 专属符号使用 `airy_*` 前缀 | — |
| L2607 | "`airy_*` 前缀不得用于 agentrt-linux 专属功能" | **与 L2606 直接矛盾** |
| L2607 | "`airy_*` 前缀不得用于 agentrt 用户态" | **与 L2599 共享（含 agentrt）矛盾，与 `06-iron9:274` 矛盾** |

**L2606 vs L2607 直接矛盾**：L2606 说 agentrt-linux [IND] 用 `airy_*`，L2607 说 `airy_*` 不得用于 agentrt-linux 专属功能——同一节内自相矛盾。

### 5.5 D 部分结论

源码前缀落地与 SSoT 一致 ✅，但存在两个严重问题：
1. 闭源手册 §11.6 以"强制规则"名义公然违反 SSoT，要求删除全部 `airy_` 前缀（P0-v3-7）
2. SSoT §4.4.2 自身内部矛盾（L2606 vs L2607）（P1-v3-3）

---

## 6. E. 文件路径引用完整性

### 6.1 AgentRT/ 大写断链

Linux 文件系统大小写敏感，实际目录为 `agentrt/`（小写），但文档中存在 `AgentRT/`（大写）引用。

**Grep 执行记录**：
```
Grep pattern="AgentRT/" path="docs/AirymaxRT" → 60 occurrences across 24 files
```

**受影响文件**（部分列举）：
- `docs/AirymaxRT/TERMINOLOGY.md`: 8 处
- `docs/AirymaxRT/30-interfaces/01-doxygen-guide.md`: 6 处
- `docs/AirymaxRT/30-interfaces/60-syscalls/01-agent.md`: 3 处
- `docs/AirymaxRT/140-application-development/01-getting-started.md`: 4 处
- `docs/AirymaxRT/140-application-development/10-migration-guide.md`: 4 处
- `docs/AirymaxRT/10-architecture/40-philosophy/01-design-philosophy.md`: 2 处
- ...共 24 个文件

### 6.2 docs/AirymaxAgentOS/ 断链

闭源手册 7 处引用 `docs/AirymaxAgentOS/`，实际目录为 `docs-closed/agentrt-linux/`。

**Grep 执行记录**：
```
Grep pattern="AirymaxAgentOS" path="docs-closed/agentrt/agentrt工程标准规范手册.md" → 7 occurrences
```

| 行号 | 引用内容 |
|------|---------|
| L20 | "OS 设计文档全部在 `docs/AirymaxAgentOS/` 模块内" |
| L2232 | "BAN-358 禁止 OS 设计文档放置在 docs-closed/（必须放置在 docs/AirymaxAgentOS/）" |
| L4327 | "OS 详细设计文档全部在 `docs/AirymaxAgentOS/` 模块内" |
| L4341 | "文档位置: docs-closed/ vs docs/AirymaxAgentOS/" |
| L4398 | "docs.openeuler.org vs docs/AirymaxAgentOS/" |
| L4421 | "OS 设计文档: `docs/AirymaxAgentOS/`（docs 顶层仓下子目录，12 个文档）" |
| L4442 | "BAN-358 禁止 OS 设计文档放置在 docs-closed/（必须放置在 docs/AirymaxAgentOS/）" |

### 6.3 docs-closed/0.1.1详细任务清单.md 断链

`docs/AirymaxRT/30-interfaces/06-ipc/README.md:104` 引用 `../../../docs-closed/0.1.1详细任务清单.md`，该文件不存在。

**Glob 验证**：
```
Glob pattern="docs-closed/0.1.1详细任务清单.md" → No file found
```

### 6.4 docs/AirymaxOS/TERMINOLOGY.md 缺失

**Glob 验证**：
```
Glob pattern="docs/AirymaxOS/TERMINOLOGY.md" → No file found
```

此为已知 P2-DQC-5 遗留问题，v2.0 未修复。

### 6.5 E 部分结论

文件路径引用存在 4 类断链问题，其中 AgentRT/ 大写断链（60 处/24 文件）和 AirymaxAgentOS/ 断链（7 处）影响范围较大。

---

## 7. F. 术语一致性

### 7.1 错误码命名统一

| 检查项 | Grep 结果 | 状态 |
|--------|---------|------|
| `AIRY_ETIMEOUT`（正确命名） | AirymaxRT 中 **23 处**（14 文件） | ✅ 统一使用 |
| `AIRY_ETIMEDOUT`（旧命名） | AirymaxRT 中 **0 处** | ✅ 已清除 |

**Grep 执行记录**：
```
Grep pattern="AIRY_ETIMEOUT" path="docs/AirymaxRT" → 23 occurrences across 14 files
Grep pattern="AIRY_ETIMEDOUT" path="docs/AirymaxRT" → No matches found (0)
```

### 7.2 AIRY_OK 使用情况

| 来源 | 使用情况 | 状态 |
|------|---------|------|
| 文档 `TERMINOLOGY.md:212` | "成功码统一为 `AIRY_EOK = 0`，不再使用 `AIRY_OK`" | 声明废弃 |
| 文档 `03-protocol-contract.md:692` | "成功码统一为 `AIRY_EOK = 0`（不再使用 `AIRY_OK`）" | 声明废弃 |
| **源码 `error.h:43`** | `#define AIRY_OK 0` | ❌ **仍在定义** |
| **源码 `error.h:668,681`** | `if (__err != AIRY_OK)` | ❌ **仍在使用** |

**Grep 执行记录**：
```
Grep pattern="AIRY_OK" path="agentrt/commons/utils/error/include/error.h" → 6 occurrences
```

文档声称废弃 `AIRY_OK`，但源码 `error.h` 仍定义并活跃使用 `AIRY_OK`（6 处）。

### 7.3 Cupola 单数/复数

**Grep 执行记录**：
```
Grep pattern="[^s]Cupola[^s]" path="docs/AirymaxRT" → No matches found (0)
```

✅ Cupola 单数残留已清除（v2.0 修正有效）。

### 7.4 操作系统术语

**Grep 执行记录**：
```
Grep pattern="操作系统" path="docs/AirymaxRT" → 34 occurrences (全部合法，指 agentrt-linux/AirymaxOS 定位)
```

✅ 全部合法使用。

### 7.5 F 部分结论

术语一致性在**命名层面**基本通过（AIRY_ETIMEOUT 统一、Cupola 清除），但 `AIRY_OK` 在源码中仍活跃使用，与文档声明矛盾。

---

## 8. G. IRON-9 v2 三层模型落地

### 8.1 三层模型定义一致性

| 层级 | SSoT 定义 | 06-iron9 文档 | 一致性 |
|------|---------|-------------|--------|
| [SC] 共享契约层 | `120-cross-project-code-sharing.md` §2.1 | `06-iron9-shared-model.md` §2.1 | ✅ |
| [SS] 语义同源层 | `120-cross-project-code-sharing.md` §2.2 | `06-iron9-shared-model.md` §2.2 | ✅ |
| [IND] 完全独立层 | `120-cross-project-code-sharing.md` §2.3 | `06-iron9-shared-model.md` §2.3 | ✅ |

### 8.2 [SC] 头文件内容描述准确性

| 头文件 | SSoT 描述 | 实际源码内容 | 准确性 |
|--------|---------|------------|--------|
| `cognition_types.h` | 含"统一错误码类型（`airy_err_t = int32_t`）"+ LLM 推理阶段枚举 + Token 能效指标 + GPU/NPU 描述符 | 仅 `airy_q16_t` + CoreLoopThree 枚举 + Thinkdual 枚举（38 行） | ❌ **描述严重失实** |

**关键证据**：
- `120-cross-project-code-sharing.md:73`: 声明 `cognition_types.h` 含 `airy_err_t`
- `06-iron9-shared-model.md:70`: 同样声明 `cognition_types.h` 含 `airy_err_t`
- `cognition_types.h` 实际内容（完整 38 行）：`airy_q16_t` + `enum airy_cog_phase` + `enum airy_think_mode`，**零匹配** `airy_err_t`

### 8.3 函数前缀与层级对齐

参见 D 部分。源码前缀与 SSoT 一致 ✅，但闭源手册 §11.6 违反 SSoT ❌。

### 8.4 G 部分结论

IRON-9 v2 三层模型定义在文档间一致 ✅，但 `cognition_types.h` 内容描述严重失实（SSoT 和 06-iron9 均声称含 `airy_err_t`，实际不含）。

---

## 9. H. v2.0 修正副作用扫描

### 9.1 v2.0 修正有效性验证

| # | v2.0 修正项 | v3.0 验证结果 | Grep 命令 | 匹配数 |
|---|------------|-------------|---------|--------|
| 1 | [SC] 6 头文件清单统一 | ✅ 通过 | `Grep "memory_types\.h\|..."` in 闭源手册 | 19 |
| 2 | 错误码命名 AIRY_ETIMEOUT 统一 | ✅ 通过 | `Grep "AIRY_ETIMEDOUT"` in AirymaxRT | 0 |
| 3 | 闭源手册 agentos_/AGENTOS_ 清除 | ✅ 通过 | `Grep "agentos_\|AGENTOS_"` in 闭源手册 | 0 |
| 4 | Cupola 单数清除 | ✅ 通过 | `Grep "[^s]Cupola[^s]"` in AirymaxRT | 0 |
| 5 | 源码 agentos_/airymaxos_ 清除 | ✅ 通过 | `Grep "agentos_\|airymaxos_"` glob="*.{c,h}" in agentrt | 0 |
| 6 | 50-specifications 目录删除 | ✅ 通过 | 目录不存在 | — |
| 7 | v2.0 修正的 5 类旧路径 | ✅ 通过 | 逐类 Grep 验证 | 全部 0 |

### 9.2 v2.0 修正遗漏（副作用）

| # | 遗漏项 | 位置 | 说明 |
|---|--------|------|------|
| 1 | IPC 头三重违规 | `02-l2-service-protocol.md:55-116` | v2.0 修正了 `06-ipc/README.md`，但遗漏此文件 |
| 2 | IPC 头三重违规 | 闭源手册 §34.2 STD-02 L3328-3356 | v2.0 修正未覆盖闭源手册 §34.2 |
| 3 | .bak 文件残留 | `triple_coordinator.c.bak`（43 处 `agentrt_`） | v2.0 N4 延期项未修复 |

### 9.3 v2.0 延期项状态

| 延期项 | v2.0 状态 | v3.0 验证 |
|--------|---------|---------|
| P0-2 源码工程标准全面重构（~46h） | 延期至 1.0.1 M1 | **未修复**——源码 `airy_types.h` 错误码值仍与文档 SSoT 冲突 |
| N4 .bak 文件清理 | 延期 | **未修复**——43 处 `agentrt_` 残留 |
| P2-DQC-5 TERMINOLOGY.md | 延期 | **未修复**——`docs/AirymaxOS/TERMINOLOGY.md` 不存在 |

### 9.4 H 部分结论

v2.0 修正在其已识别范围内**有效**（7/7 项通过验证），但存在 2 处 IPC 头违规遗漏和 3 项延期项未修复。

---

## 10. v3.0 新发现问题清单

### 10.1 P0 级问题（7 项）

#### P0-v3-1：SSoT 50-engineering-standards 内部错误码 5+ 套方案并行

- **位置**：
  - 方案 A: `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md:420-427`
  - 方案 B: `docs/AirymaxOS/50-engineering-standards/30-runtime-interfaces/runtime_interfaces.md:1753-1770`
  - 方案 C: `docs/AirymaxOS/50-engineering-standards/10-coding-style/coding_conventions.md:2959-2981`
  - 方案 D: `docs/AirymaxOS/50-engineering-standards/50-project-erp/project_erp.md:987-1003`
  - SSoT 声明: `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:81`
- **问题**：5+ 套错误码方案在同一 SSoT 目录下并行，数值互相矛盾（AIRY_EINVAL 有 -22/-1/-2 三种值），违反 SSoT 原则
- **影响**：编译行为不可预测、跨模块错误码语义断裂

#### P0-v3-2：源码 airy_types.h 错误码值与文档 SSoT 严重不一致

- **位置**：`agentrt/commons/include/airy_types.h:50-55`
- **问题**：源码 `AIRY_EINVAL=-1`、`AIRY_ENOMEM=-2`、`AIRY_ETIMEDOUT=-6`，文档 SSoT 值为 `-22`/`-12`/`-110`
- **影响**：所有返回错误码的函数语义与文档不符，调试困难
- **关联**：v2.0 P0-2 延期项，未修复

#### P0-v3-3：SSoT 声明 airy_err_t 在 cognition_types.h，实际在 airy_types.h

- **声明位置**：`docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:73`
- **实际位置**：`agentrt/commons/include/airy_types.h:40`
- **验证**：`cognition_types.h` 完整 38 行，Grep `airy_err_t` → 0 匹配
- **影响**：SSoT 自身矛盾（§2.1 表格 vs §3.8 代码块），开发者无法确定权威源

#### P0-v3-4：SSoT 声明 include/airymax/error.h 为权威源，该文件不存在

- **声明位置**：
  - `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:81`
  - `docs/AirymaxRT/10-architecture/00-architectural-principles.md:919,921`
  - `docs/AirymaxRT/TERMINOLOGY.md:209`
  - `docs/AirymaxRT/20-modules/10-contracts/03-protocol-contract.md:692`
- **验证**：`Glob include/airymax/error.h` → No file found
- **实际路径**：`agentrt/commons/utils/error/include/error.h`
- **影响**：SSoT 声明的权威源不存在，4+ 处文档引用断链

#### P0-v3-5：IPC 头三重违规在 02-l2-service-protocol.md 完整保留

- **位置**：`docs/AirymaxRT/30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md:55-116`
- **违规**：命名（`are_ipc_message_header_t`）+ 类型（`uint32_t`）+ 布局（13 字段、无 packed、无 _Static_assert）
- **关联**：v2.0 修正遗漏（修正了 `06-ipc/README.md`，遗漏此文件）

#### P0-v3-6：IPC 头三重违规在闭源手册 §34.2 STD-02 完整保留

- **位置**：`docs-closed/agentrt/agentrt工程标准规范手册.md:3328-3356`
- **违规**：同 P0-v3-5，且作为"强制规则 STD-02"使用，误导性更强
- **关联**：v2.0 修正遗漏

#### P0-v3-7：闭源手册 §11.6 以"强制规则"公然违反 SSoT 函数前缀规则

- **位置**：`docs-closed/agentrt/agentrt工程标准规范手册.md:1509-1544`
- **问题**：§11.6 标题为"airy_ → agentrt_ 彻底改名规范"，要求将 SSoT 正确前缀 `airy_*` 改为 SSoT 禁止前缀 `agentrt_*`
- **矛盾详情**：
  - L1509: 标题"airy_ → agentrt_ 彻底改名" vs `06-iron9:268`: `agentrt_*` 不使用
  - L1521: `airy_error_t` → `agentrt_error_t` vs 源码使用 `airy_err_t`（1788 处 `airy_`，0 处 `agentrt_`）
  - L1531: "airy_ 零残留: grep airy_ → 0" vs 源码 1788 处 `airy_`
  - L1542: "BAN-342 禁止 airy_ 前缀残留" vs SSoT 规定 `airy_*` 是正确前缀
- **影响**：如果执行 §11.6，将破坏整个 [SC] 共享契约层，导致跨端通信断裂

### 10.2 P1 级问题（7 项）

#### P1-v3-1：AgentRT/（大写）60 处断链引用

- **位置**：`docs/AirymaxRT/` 中 24 个文件，共 60 处
- **问题**：Linux 文件系统大小写敏感，实际目录为 `agentrt/`（小写），`AgentRT/` 引用断链
- **Grep**：`Grep "AgentRT/" path="docs/AirymaxRT"` → 60 occurrences across 24 files

#### P1-v3-2：docs/AirymaxAgentOS/ 7 处断链

- **位置**：`docs-closed/agentrt/agentrt工程标准规范手册.md` L20/2232/4327/4341/4398/4421/4442
- **问题**：实际目录为 `docs-closed/agentrt-linux/`，引用 `docs/AirymaxAgentOS/` 断链
- **Grep**：`Grep "AirymaxAgentOS" path="docs-closed/agentrt/agentrt工程标准规范手册.md"` → 7

#### P1-v3-3：SSoT §4.4.2 函数前缀规则内部矛盾

- **位置**：`docs/AirymaxOS/50-engineering-standards/10-coding-style/coding_conventions.md:2599-2607`
- **矛盾**：
  - L2606 说 agentrt-linux [IND] 用 `airy_*`
  - L2607 说 `airy_*` 不得用于 agentrt-linux 专属功能（与 L2606 直接矛盾）
  - L2607 说 `airy_*` 不得用于 agentrt 用户态（与 L2599 共享矛盾，与 `06-iron9:274` 矛盾）
  - L2601 用 `AIRYMAXOS_*` 作为活跃前缀，但 `06-iron9:270` 说 `airymaxos_*` 已废弃

#### P1-v3-4：ARE_IPC_MAGIC 宏命名不一致

- **位置**：`docs/AirymaxRT/30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md:60`
- **问题**：使用 `ARE_IPC_MAGIC`（ARE_ 前缀），其他所有文档和源码使用 `AIRY_IPC_MAGIC`（AIRY_ 前缀）
- **Grep**：`Grep "ARE_IPC_MAGIC"` → 仅此文件使用

#### P1-v3-5：源码错误码语义重叠/同值冲突

- **位置**：`agentrt/commons/utils/error/include/error.h`
- **冲突**：
  - L493 `AIRY_ERR_PROTOCOL=-900` vs `airy_types.h:62` `AIRY_EPROTO=-13`（语义重叠）
  - L46 `AIRY_ERR_UNKNOWN=-1` vs `airy_types.h:50` `AIRY_EINVAL=-1`（同值冲突）
  - L88-89 `#undef AIRY_EPERM` 后重定义为 -10，覆盖 `airy_types.h` 的值

#### P1-v3-6：06-iron9-shared-model.md 仍称 cognition_types.h 含 airy_err_t

- **位置**：`docs/AirymaxRT/10-architecture/06-iron9-shared-model.md:70`
- **问题**：声称 `cognition_types.h` 含"统一错误码类型（`airy_err_t = int32_t`）"，实际源码不含
- **影响**：开发者按此引用 `#include <airymax/cognition_types.h>` 获取 `airy_err_t` 将编译失败

#### P1-v3-7：源码 error.h 仍定义和使用 AIRY_OK

- **位置**：`agentrt/commons/utils/error/include/error.h:43,668,681`
- **问题**：文档（`TERMINOLOGY.md:212`、`03-protocol-contract.md:692`）声明"不再使用 `AIRY_OK`"，但源码仍定义并活跃使用
- **Grep**：`Grep "AIRY_OK" path="agentrt/commons/utils/error/include/error.h"` → 6

### 10.3 P2 级问题（4 项）

#### P2-v3-1：docs-closed/0.1.1详细任务清单.md 不存在

- **位置**：`docs/AirymaxRT/30-interfaces/06-ipc/README.md:104`
- **问题**：引用 `../../../docs-closed/0.1.1详细任务清单.md`，该文件不存在
- **Glob**：`Glob "docs-closed/0.1.1详细任务清单.md"` → No file found

#### P2-v3-2：docs/AirymaxOS/TERMINOLOGY.md 不存在

- **问题**：已知 P2-DQC-5 遗留问题，v2.0 未修复
- **Glob**：`Glob "docs/AirymaxOS/TERMINOLOGY.md"` → No file found

#### P2-v3-3：.bak 备份文件 43 处 agentrt_ 残留

- **位置**：`agentrt/atoms/coreloopthree/src/cognition/critique/triple_coordinator.c.bak`
- **问题**：.bak 文件中 43 处 `agentrt_` 前缀残留（v2.0 N4 延期项未修复）
- **Grep**：`Grep "agentrt_" glob="*.bak" path="agentrt"` → 43 occurrences in 1 file

#### P2-v3-4：mainpage.dox 使用 agentrt_ 废弃前缀

- **位置**：`agentrt/cupolas/src/mainpage.dox:110,113`
- **问题**：Doxygen 文档示例使用 `agentrt_error_t` 和 `agentrt_error_get_message()`，违反 SSoT 函数前缀规则
- **Grep**：`Grep "agentrt_" path="agentrt/cupolas/src/mainpage.dox"` → 2

---

## 11. 修正后综合评分变化

### 11.1 评分变化轨迹

| 版本 | 评分 | 级别 | 变化 | 主要原因 |
|------|------|------|------|---------|
| v1.0 | 65 | C+ | — | 初始审查 |
| v2.0（修正前） | 63 | C+ | -2 | 新发现 30 项问题 |
| v2.0（修正后预估） | 72 | B- | +9 | 修正 9/10 项 P0，1 项延期 |
| **v3.0（本次复审）** | **66** | **C+** | **-6** | 新发现 7 项 P0 + 7 项 P1 |

### 11.2 评分下调分析

v3.0 评分从 v2.0 修正后预估的 72/B- 下调至 66/C+，下调 6 分，原因如下：

| 下调因素 | 扣分 | 说明 |
|---------|------|------|
| SSoT 错误码系统性崩溃（P0-v3-1/2/3/4） | -3 | 5+ 套方案并行 + 源码与文档值冲突 + 权威源文件不存在 + airy_err_t 定位错误 |
| IPC 头违规遗漏 2 处（P0-v3-5/6） | -1.5 | v2.0 修正范围不完整，遗漏 02-l2 和闭源手册 §34.2 |
| 闭源手册 §11.6 违反 SSoT（P0-v3-7） | -1 | 工程标准手册以"强制规则"名义公然违反 SSoT 前缀规则 |
| 函数前缀规则内部矛盾 + 路径断链（P1-v3-1/2/3） | -0.5 | 多处工程标准矛盾 |

### 11.3 评分恢复路径

要将评分从 66/C+ 提升至 ≥80/B（M1 代码开发就绪阈值），需按以下优先级修复：

| 优先级 | 修复项 | 预估工时 | 预期加分 |
|--------|--------|---------|---------|
| 1 | 统一错误码 SSoT（消除 5+ 套方案，修正源码值，创建 include/airymax/error.h 或修正引用路径） | ~24h | +3 |
| 2 | 修复 IPC 头违规 2 处（02-l2 + 闭源手册 §34.2） | ~4h | +1.5 |
| 3 | 重写闭源手册 §11.6（改为 agentos_ → airy_ 改名规范，非 airy_ → agentrt_） | ~8h | +1 |
| 4 | 修复 cognition_types.h 描述失实（SSoT + 06-iron9） | ~2h | +0.5 |
| 5 | 修复路径断链（AgentRT/ 60 处 + AirymaxAgentOS/ 7 处） | ~6h | +0.5 |
| 6 | 修复函数前缀规则内部矛盾（coding_conventions §4.4.2） | ~4h | +0.5 |
| 7 | 清除源码 AIRY_OK 使用 + 修复 P1/P2 遗留项 | ~8h | +0.5 |
| **合计** | — | **~56h** | **+7.5** |

完成全部修复后预估评分：66 + 7.5 = **73.5/B-**，仍低于 80/B 阈值，需进一步配合源码工程标准全面重构（v2.0 P0-2 延期项，~46h）方可达标。

### 11.4 结论

agentrt 项目在 v2.0 修正后，[SC] 6 头文件清单一致性、错误码命名统一、agentos_ 清除等方面取得有效进展。但 v3.0 深度审查发现 SSoT 错误码体系存在系统性崩溃（5+ 套方案并行、权威源文件不存在、源码与文档值严重不一致），以及闭源手册 §11.6 作为"强制规则"公然违反 SSoT 函数前缀规则，属于工程标准层面的根本性矛盾。

**agentrt 项目当前状态不满足 1.0.1 M1 代码开发就绪条件（≥80/B）。**

建议优先修复 SSoT 错误码统一（P0-v3-1/2/3/4）和闭源手册 §11.6 重写（P0-v3-7），这两项是恢复 SSoT 完整性的关键阻塞项。

---

## 附录：Grep 命令执行记录汇总

| # | Grep 命令 | 范围 | 匹配数 |
|---|---------|------|--------|
| 1 | `airy_err_t` in `cognition_types.h` | 源码 | 0 |
| 2 | `airy_err_t\|AIRY_EINVAL\|...` in `airy_types.h` | 源码 | 6 lines |
| 3 | `Glob include/airymax/error.h` | 源码 | No file found |
| 4 | `AgentRT/` in `docs/AirymaxRT` | 开源文档 | 60 (24 files) |
| 5 | `AirymaxAgentOS` in 闭源手册 | 闭源文档 | 7 |
| 6 | `are_ipc_message_header` in `docs/AirymaxRT` | 开源文档 | 9 (2 files) |
| 7 | `agentrt_` glob="*.{c,h}" in `agentrt` | 源码 | 0（仅 mainpage.dox 2 处） |
| 8 | `agentrt_` glob="*.bak" in `agentrt` | 源码备份 | 43 (1 file) |
| 9 | `AIRY_ETIMEOUT` in `docs/AirymaxRT` | 开源文档 | 23 (14 files) |
| 10 | `AIRY_ETIMEDOUT` in `docs/AirymaxRT` | 开源文档 | 0 |
| 11 | `agentos_\|airymaxos_` glob="*.{c,h}" in `agentrt` | 源码 | 0 |
| 12 | `agentos_\|AGENTOS_` in 闭源手册 | 闭源文档 | 0 |
| 13 | `[^s]Cupola[^s]` in `docs/AirymaxRT` | 开源文档 | 0 |
| 14 | `AIRY_IPC_MAGIC\|airy_ipc_msg_hdr\|0x41524531` in `ipc.h` | 源码 | 7 lines |
| 15 | `AIRY_TASK_MAGIC\|SCHED_EXT\|0x41475453` in `sched.h` | 源码 | 7 lines |
| 16 | `are_ipc_message_header\|ARE_IPC_MAGIC` in 闭源手册 | 闭源文档 | 5 |
| 17 | `airy_` glob="*.{c,h}" in `agentrt` | 源码 | 1788 (100 files) |
| 18 | `\bare_\w` glob="*.{c,h}" in `agentrt` | 源码 | 230 (8 files) |
| 19 | `AIRY_OK` in `error.h` | 源码 | 6 |
| 20 | `memory_types\.h\|security_types\.h\|...` in 闭源手册 | 闭源文档 | 19 |
| 21 | `memory_types\.h\|security_types\.h\|...` in `06-iron9-shared-model.md` | 开源文档 | 34 |
| 22 | `Glob docs-closed/0.1.1详细任务清单.md` | 闭源文档 | No file found |
| 23 | `Glob docs/AirymaxOS/TERMINOLOGY.md` | 开源文档 | No file found |
| 24 | `AIRY_OK` in `docs/AirymaxRT` | 开源文档 | 2（均为合法迁移说明） |

---

<!-- 审查报告结束 -->
<!-- © 2025-2026 SPHARX Ltd. All Rights Reserved. -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0 -->
