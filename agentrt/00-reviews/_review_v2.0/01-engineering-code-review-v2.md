Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt 工程规范与代码审查第二轮深化报告 v2.0

> **文档定位**：agentrt 工程审查 v2.0 深化报告，在 v1.0 四份报告（综合分析 + atoms 源码 + daemons 源码 + AirymaxRT 方案）基础上执行**验证 + 深化 + 补充**，**不重复** v1.0 已有结论，仅对 P0 进行源码级复核并记录新发现。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：2.0（2026-07-13）。
> **审查范围**：agentrt 源码（atoms/daemons/cupolas/gateway/commons/protocols）+ AirymaxRT 文档（88 .md）+ AirymaxOS 工程标准（23 .md 共享）。
> **审查方法**：v1.0 报告深读 → 源码级重新验证（Read + Grep）→ 新发现扫描（DCLP / 资源泄漏 / ABI / 跨平台）。
> **证据要求**：所有结论附 `文件路径:L行号`，可通过 Read/Grep 工具复核。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. 50-engineering-standards 共用验证](#2-50-engineering-standards-共用验证任务-a)
- [3. AirymaxRT 目录结构验证](#3-airymaxrt-目录结构验证任务-b)
- [4. 函数前缀改动实施情况验证](#4-函数前缀改动实施情况验证任务-c)
- [5. P0 问题逐项验证](#5-p0-问题逐项验证任务-d)
- [6. v2.0 新发现](#6-v20-新发现任务-e)
- [7. 修正后的综合评分](#7-修正后的综合评分)
- [附录 A：v1.0 报告索引](#附录-a-v10-报告索引)
- [附录 B：术语对照](#附录-b-术语对照)

---

## 1. 执行摘要

### 1.1 v1.0 P0 验证结果总览

| P0 编号 | 问题 | v1.0 判定 | v2.0 复核结果 | 关键证据 |
|---------|------|----------|---------------|----------|
| P0-1 | 错误码 6 套并行 | 灾难性 SSoT 冲突 | **确认存在（恶化至 7+ 套）** | 7 套方案并存（详见 §5.1） |
| P0-2 | 源码工程标准全面违规 | 系统性违规 | **确认存在** | 4 空格缩进/typedef/装饰分节符未改 |
| P0-3 | AIRY_ERROR_NULL NULL deref | NULL deref 风险 | **降级为 P1（宏实际 return NULL，无 deref）** | `error.h:634-638` 宏含 `return NULL` |
| P0-4 | IPC 头三重违规 | 命名/类型/布局 | **确认存在** | `06-ipc/README.md:27` 仍为 `are_ipc_message_header_t` |
| P0-5 | "操作系统"定位冲突 | 15+ 处误称 | **确认存在（扩大至 51 处/18 文件）** | `grep 操作系统` = 51 处 |
| P0-6 | WebSocket 类型错误 | PROTOCOL_HTTP 误用 | **确认存在** | `protocols_impl.c:117` 仍为 `PROTOCOL_HTTP` |
| P0-7 | agent_registry 数据竞争 | 返回内部指针后解锁 | **确认存在** | `agent_registry_core.c:123-137` 未改 |
| P0-8 | [SC] 头文件清单不一致 | bpf_struct_ops.h vs syscalls.h | **确认存在（恶化：bpf_struct_ops.h 升为 #1，syscalls.h 完全缺失）** | `06-iron9-shared-model.md:68` |
| P0-9 | 文件路径引用错误 | 系统性 | **确认存在** | `00-basic-theories/` 仍引用于 8+ 文件 |
| P0-10 | ES-SEL4-7 分类残留冲突 | agentrt-linux | **未复核（agentrt-linux 范围）** | 见 v1.0 agentrt-linux 报告 |

**核心结论**：v1.0 识别的 10 项 P0 中，**8 项经源码级复核确认仍然存在**，**1 项（P0-3）应降级为 P1**（v1.0 对宏行为的判定有误），**1 项（P0-10）属 agentrt-linux 范围未在本轮复核**。其中 P0-1、P0-5、P0-8 三项不仅未修复，反而**比 v1.0 描述的更严重**。

### 1.2 v2.0 新发现总览

| 编号 | 问题 | 严重度 | 位置 |
|------|------|--------|------|
| N1 | DCLP 自旋等待无 yield/timeout，CPU 空转 + 潜在死锁 | P1 | `core_init.c:34` |
| N2 | `cupolas_init()` 所有错误路径均泄漏 mutex | P1 | `cupolas.c:84-158` |
| N3 | `cupolas_init()` 非并发安全（初始化检查在锁外） | P1 | `cupolas.c:78-80` |
| N4 | `agentrt_` 前缀残留于 .bak 备份文件（42 处） | P2 | `triple_coordinator.c.bak` |
| N5 | `sched_d main.c` 4 处重复错误清理块，无 goto 集中出口 | P1 | `sched_d/main.c:252-314` |
| N6 | `sync_compat.h` 丢弃底层错误码（仅返回 -1） | P2 | `sync_compat.h:37-72` |
| N7 | P0-8 恶化：`bpf_struct_ops.h` 从 v1.0 的"#6"升至"#1"，`syscalls.h` 完全缺失 | P0（强化 P0-8） | `06-iron9-shared-model.md:68` |
| N8 | `06-iron9-shared-model.md:214` 递归注释 `/* 成功（替代 AIRY_EOK） */` 仍存在 | P2 | 同左 |

### 1.3 修正后的综合评分

| 维度 | v1.0 评分 | v2.0 修正评分 | 修正原因 |
|------|----------|---------------|----------|
| 源码工程 | 68/C+ | **66/C+** | P0-3 降级抵消部分扣分，但 N1/N2/N3/N5 新发现拉低 |
| 方案设计 | 70/B- | **68/C+** | P0-1/P0-5/P0-8 恶化 |
| 跨平台一致性 | 55/D+ | **54/D+** | 函数前缀缺失确认 + N6 |
| **总评** | **65/C+** | **63/C+** | v1.0 评分略偏乐观，P0-3 降级不足以抵消 P0-1/5/8 恶化与新发现 |

> **总体判定**：agentrt 工程体系仍**未达到"可开发"状态**。v1.0 提出的修复建议在 0.1.1 收尾阶段**未被执行**，部分问题反而恶化。建议立即启动 Phase 0 修复（~5.5h 源码正确性 + ~21h 方案 P0）。

---

## 2. 50-engineering-standards 共用验证（任务 a）

### 2.1 符号链接验证

| 检查项 | 结果 | 证据 |
|--------|------|------|
| 符号链接存在 | ✓ 通过 | `readlink docs/AirymaxRT/50-engineering-standards` = `../AirymaxOS/50-engineering-standards` |
| 共享文件数一致 | ✓ 通过 | `find -L docs/AirymaxRT/50-engineering-standards -type f -name "*.md"` = 23；`find docs/AirymaxOS/50-engineering-standards -type f -name "*.md"` = 23 |
| 子目录可访问 | ✓ 通过 | `10-coding-style/`、`20-contracts/`、`30-runtime-interfaces/`、`40-integration/`、`50-project-erp/` 全部可读 |
| SSoT 注册表存在 | ✓ 通过 | `09-ssot-registry.md` + `120-cross-project-code-sharing.md` 在符号链接下可访问 |

**结论**：符号链接配置正确，agentrt 与 agentrt-linux（AirymaxOS）共用同一份 50-engineering-standards（23 文档），符合 IRON-9 v2 同源原则。

### 2.2 六大支柱遵循情况验证（agentrt 源码）

| 支柱 | 规则编号 | [SC] 6 头文件（标杆） | 用户态 atoms/daemons（违规） | 评估 |
|------|---------|---------------------|---------------------------|------|
| Tab 8 缩进 | OS-STD-FMT-001 | ✓ 全部 Tab 8（`ipc.h`/`sched.h`/`syscalls.h` 等） | ✗ 全部 4 空格（`atoms/` 7009 处 `airy_` + `daemons/` 2891 处均 4 空格） | **割裂** |
| K&R 大括号 | OS-STD-FMT-003/009 | ✓ 函数开括号在新行 | ✓ 大多数函数符合 | 通过 |
| 最小 typedef | OS-STD-CODE-020 | ✓ `struct airy_ipc_msg_hdr` 无 typedef | ✗ atoms 114+ 处匿名 struct typedef + daemons 40+ 处 | **割裂** |
| goto 集中出口 | OS-KER-001 | N/A（头文件无实现） | ✗ 全仓库仅 14 处 goto 标签；`cupolas_init()`/`sched_d main()` 等多资源函数用早返回 | **违规** |
| kernel-doc | OS-STD-CODE-012 | ✓ `struct airy_ipc_msg_hdr` 含完整 `@magic/@opcode/@flags` | △ 部分公共 API 有 Doxygen，但 `gateway_*`/`jsonrpc_*`/`protocol_*` 普遍缺失 | **部分割裂** |
| 80 列行宽 | OS-STD-FMT-002 | ✓ 头文件均 ≤80 列 | ✗ `loop.c` 255 处超 80 列（最多 117 列）；`are_ipc.c:45` 211 列 | **违规** |

**结论**：50-engineering-standards 被 agentrt 与 agentrt-linux **声明层共用**（符号链接正确），但 agentrt 用户态源码**实现层系统性违反**六大支柱中的 4 项（Tab 8 / 最小 typedef / goto 集中出口 / 80 列）。仅 [SC] 6 个头文件作为合规标杆存在，与用户态形成"双轨制"割裂。**v1.0 P0-2 结论确认仍成立**。

### 2.3 唯一合规标杆：[SC] 6 头文件

`agentrt/commons/include/airymax/` 下 7 个 .h 文件（6 个 [SC] 核心 + 1 个 uapi_compat.h 辅助）全部 Tab 8 + struct 无 typedef + kernel-doc + `_Static_assert`。其中 `ipc.h:67-80` 的 `struct airy_ipc_msg_hdr` + `__attribute__((packed))` + `_Static_assert(sizeof(...) == 128)` 是全仓库最严格的合规实现，应作为用户态重构的标杆。

---

## 3. AirymaxRT 目录结构验证（任务 b）

### 3.1 顶层目录对比

| AirymaxRT 顶层 | AirymaxOS 对应 | 评估 |
|---------------|---------------|------|
| `00-requirements/` | `00-requirements/` | ✓ 一致 |
| `10-architecture/` | `10-architecture/` | ✓ 一致 |
| `20-modules/` | `20-modules/` | ✓ 一致 |
| `30-interfaces/` | `30-interfaces/` | ✓ 一致 |
| `50-engineering-standards/`（符号链接） | `50-engineering-standards/`（实体） | ✓ 通过链接集成 |
| `50-specifications/`（仅 1 文件，与 `20-modules/10-contracts/06-glossary-index.md` 重复） | 无对应 | △ 冗余 |
| `140-application-development/` | `140-application-development/` | ✓ 一致 |
| — | `40-dataflows/` | 合理缺失（内核数据流） |
| — | `60-driver-model/` | 合理缺失（内核驱动） |
| — | `70-build-system/` | ✗ 不合理缺失（agentrt 应有 CMake 构建文档） |
| — | `80-testing/` | ✗ 不合理缺失（测试框架应独立） |
| — | `90-observability/` | △ 散落在各文档 |
| — | `100-operations/` | △ 部分在 `140-application-development/` |
| — | `110-security/` | △ 散落在 Cupolas 文档 |
| — | `120-development-process/` | ✗ 不合理缺失 |
| — | `130-roadmap/` | △ 缺失 |
| — | `150-cloudnative/`/`160-compatibility/`/`170-performance/`/`180-i18n/`/`190-distribution/` | △ 缺失 |

### 3.2 命名规范验证

| 检查项 | 结果 | 证据 |
|--------|------|------|
| NN-name 模式 | ✓ 通过 | `00-requirements`、`10-architecture`、`20-modules`、`30-interfaces`、`50-specifications`、`140-application-development` |
| kebab-case 子目录 | ✓ 通过 | `01-getting-started.md`、`06-iron9-shared-model.md` 等 |
| 50-engineering-standards 集成方式 | ✓ 符号链接 | `readlink` 确认指向 `../AirymaxOS/50-engineering-standards` |

### 3.3 目录结构评分

**70/B-**（与 v1.0 一致）。符号链接正确，命名规范，但 `50-specifications/` 冗余 + 缺失 `70-build-system/`、`80-testing/`、`120-development-process/` 三个应独立文档化的目录。

---

## 4. 函数前缀改动实施情况验证（任务 c）

### 4.1 前缀分布 Grep 统计（v2.0 实测）

| 前缀 | atoms (.c/.h) | daemons/cupolas/gateway/commons/protocols (.c/.h) | docs/AirymaxRT (.md) | 评估 |
|------|---------------|---------------------------------------------------|---------------------|------|
| `airy_`（C 标识符） | **7009** 处 | **2891** 处（daemons）+ 大量其他 | 大量 | ✓ 主导前缀 |
| `agentrt_`（C 标识符） | **0** 处 | **0** 处 | **0** 处 | ✗ 专属 API 前缀完全缺失 |
| `agentrt_`（.bak 备份文件） | **42** 处 | 0 | — | △ 残留（见 N4） |
| `agentos_` | 0 | 0 | 0 | ✓ 无残留 |
| `airymaxos_` | 0 | 0 | 2（均为禁止声明） | ✓ 无误用 |
| `agentrt`（无下划线，注释/路径） | ~220 处 | — | — | ✓ 非标识符 |

> **统计方法**：`grep -rn "\bairy_[a-z]" agentrt --include="*.c" --include="*.h"` = 13238；`grep -rn "agentrt_" agentrt --include="*.c" --include="*.h"` = 0。

### 4.2 v1.0 统计修正

v1.0 报告称"`agentrt_`（含注释/路径）4058 处"，但 v2.0 实测 `grep -rn "agentrt_" agentrt --include="*.c" --include="*.h"` = **0 处**。v1.0 的 4058 计数可能包含了非 .c/.h 文件或使用了不同的匹配规则。**v2.0 修正**：active 源码中 `agentrt_` C 标识符为 **0 处**，仅在 `.bak` 备份文件中有 42 处残留。

### 4.3 三层前缀分层定义验证

| 层次 | 前缀 | 用途 | SSoT 定义 | 源码使用 | 文档使用 | 评估 |
|------|------|------|----------|---------|---------|------|
| [SC] 共享契约层 | `airy_*` | agentrt 与 agentrt-linux 逐字节共享的 6 头文件 | `120-cross-project-code-sharing.md` | ✓ `airy_ipc_msg_hdr`/`airy_task_desc` 等 | ✓ | **清晰** |
| [SS] 语义同源层 | `airy_*` | agentrt 内部 API（微核心原语 + 应用语义层） | `06-iron9-shared-model.md` §2.2 | ✓ `airy_init`/`airy_loop_create` 等 | ✓ | **清晰** |
| ARE 标准 ABI | `are_*` | 第三方可实现的公开标准接口（L1/L2/L3） | `30-interfaces/05-runtime-interfaces/` | ✓ `are_ipc_*`/`are_crc32_*` | ✓ | **清晰** |
| agentrt 专属 API | `agentrt_*` | daemon 管理、配置、运行时控制 | **未定义** | **0 处使用** | **0 处定义** | ✗ **完全缺失** |

### 4.4 关键结论

1. **`airy_*` 边界清晰**：13238 处使用，覆盖 [SC] + [SS] 两层，无 `agentos_*`/`airymaxos_*` 残留。
2. **`agentrt_*` 专属 API 前缀完全缺失**：源码 0 处 + 文档 0 处定义。这与 v1.0 P1-1/P1-3 结论一致，但 v2.0 进一步确认：**任务描述明确要求 agentrt 拥有专属 API 前缀，但该要求在源码和文档中均未落地**。daemon 管理（`daemon_*`）、配置（`airy_config_*`）、运行时控制（`airy_loop_*`）等内部 API 直接使用了 `airy_*`/`daemon_*` 等前缀，未区分"agentrt 专属"与"[SS] 同源"。
3. **新发现 N4**：`agentrt/atoms/coreloopthree/src/cognition/critique/triple_coordinator.c.bak` 含 42 处 `agentrt_error_t`/`agentrt_thinking_step_t` 等 typedef 残留。虽为备份文件不影响编译，但污染 grep 审计，建议删除。

### 4.5 函数前缀评分

**72/B-**（与 v1.0 一致）。`airy_*`/`are_*` 分层清晰，但 `agentrt_*` 专属前缀缺失是任务描述要求的明确未达标项。

---

## 5. P0 问题逐项验证（任务 d）

### 5.1 P0-1 验证：错误码 SSoT 灾难性冲突（7+ 套方案并存）

**v1.0 判定**：6+ 套方案并存，灾难性 SSoT 冲突。

**v2.0 源码级复核**：重新读取 7 个文档的实际错误码定义，确认**至少 7 套方案并存**（比 v1.0 描述更严重）。

| 方案 | 文件:行号 | 成功码 | AIRY_EINVAL | AIRY_ENOMEM | AIRY_ETIMEOUT | 类型 |
|------|----------|--------|-------------|-------------|---------------|------|
| A | `00-architectural-principles.md:922-940` | `AIRY_EOK=0` | `=EINVAL`（22） | `=ENOMEM`（12） | `=ETIMEDOUT` | POSIX errno 直接赋值（正值） |
| B | `06-iron9-shared-model.md:213-218` | `AIRY_EOK=0` | `-22` | `-12` | — | POSIX 对齐负值 |
| C | `05-syscall.md:641-646` | `AIRY_EOK=0` | `1001` | `1002` | `1003` | 正值序列 |
| D | `04-syscall-api-contract.md:99-105` | `AIRY_EOK=0` | `-1` | `-2` | `-11` | 负值序列 |
| E | `06-glossary-index.md:175-180` | **`AIRY_OK`**（非 EOK） | `-1` | `-2` | **`AIRY_ETIMEDOUT=-6`**（命名+值均不同） | 负值 + 命名不一致 |
| F | `30-interfaces/README.md:80-86` | `AIRY_EOK=0` | `-1` | `-2` | `-11` | 负值序列 |
| G | `03-protocol-contract.md:494-500` | **`AIRY_OK=0`**（非 EOK） | `-1` | `-2` | `-11` | 负值 + 命名不一致 |
| H | `01-l1-runtime-interface.md:48-60` | **`ARE_OK=0`**（非 AIRY_） | `ARE_EINVAL=-1` | `ARE_ENOMEM=-2` | `ARE_ETIMEDOUT=-6` | ARE 标准前缀 |
| SSoT | `120-cross-project-code-sharing.md:81` | — | — | — | — | 13 个 `AIRY_E*` 宏，`airy_err_t` 定义于 `cognition_types.h` |

**冲突点确认**：
1. 成功码：`AIRY_EOK` vs `AIRY_OK` vs `ARE_OK`（3 种命名）
2. `AIRY_EINVAL`：`EINVAL(22)` / `-22` / `1001` / `-1` / `ARE_EINVAL=-1`（5 种值）
3. `AIRY_ENOMEM`：`ENOMEM(12)` / `-12` / `1002` / `-2` / `ARE_ENOMEM=-2`（5 种值）
4. 超时码：`AIRY_ETIMEOUT` vs `AIRY_ETIMEDOUT`（2 种命名）+ 值 `-11` vs `-6` vs `ETIMEDOUT` vs `1003`（4 种值）
5. 前缀：`AIRY_*` vs `ARE_*`（2 种前缀，边界未文档化）

**v2.0 判定**：**确认存在，且比 v1.0 描述更严重**（7 套方案，v1.0 称"6+套"）。**未修复**。

**额外发现 N8**：`06-iron9-shared-model.md:214` 的递归注释 `#define AIRY_EOK 0 /* 成功（替代 AIRY_EOK） */` 仍然存在（v1.0 P2-1 未修复）。

**工作量估算**：~8h（文档统一）+ 源码侧错误码统一另计。

### 5.2 P0-2 验证：源码工程标准全面违规（系统性）

**v1.0 判定**：833 源文件系统性违反 OLK-6.6 六大支柱。

**v2.0 源码级复核**：
- 4 空格缩进：atoms 全量 + daemons 全量仍为 4 空格（`grep "^\s\{4\}"` 模式未变）
- typedef struct：`cupolas.c:37` `typedef struct { ... } cupolas_internal_config_t;` 仍存在；`protocols_impl.c:33` `typedef struct protocol_manager_s { ... } protocol_manager_s;` 仍存在
- ASCII 装饰分节符：`cupolas.c:30/75` `/* ==================== 互斥锁兼容API ==================== */` 仍存在
- 自定义错误宏：`AIRY_ERROR_NULL`/`AIRY_ERROR`/`AIRY_RET_ERR` 仍大量使用（详见 §5.3）
- `__builtin_memset`/`__builtin_memcpy` 与 `AIRY_MEMSET` 混用：`agent_registry_core.c:86` `__builtin_memset(entry, 0, sizeof(agent_entry_t));` 仍存在

**v2.0 判定**：**确认存在，未修复**。与 v1.0 一致。

### 5.3 P0-3 验证：AIRY_ERROR_NULL NULL deref【降级为 P1】

**v1.0 判定**：`AIRY_ERROR_NULL(...)` 用作 if 块最后一条语句无显式 return，后续代码直接解引用可能 NULL 的指针，存在 NULL deref 风险。

**v2.0 源码级复核（关键）**：

重新读取 `agentrt/commons/utils/error/include/error.h:603-638`，确认三个宏的**实际行为**：

```c
/* error.h:603-608 */
#define AIRY_RET_ERR(code)                                                     \
    do {                                                                          \
        airy_err_push_ex((code), __FILE__, __LINE__, __func__, "%s",         \
                         airy_err_str(code));                                 \
        return (code);                                                            \
    } while (0)

/* error.h:613-617 */
#define AIRY_ERROR(code, msg)                                                  \
    do {                                                                          \
        airy_err_push_ex((code), __FILE__, __LINE__, __func__, "%s", (msg)); \
        return (code);                                                            \
    } while (0)

/* error.h:634-638 */
#define AIRY_ERROR_NULL(code, msg)                                             \
    do {                                                                          \
        airy_err_push_ex((code), __FILE__, __LINE__, __func__, "%s", (msg)); \
        return NULL;                                                              \
    } while (0)
```

**关键发现**：三个宏**均包含 `return` 语句**：
- `AIRY_RET_ERR` → `return (code);`
- `AIRY_ERROR` → `return (code);`
- `AIRY_ERROR_NULL` → `return NULL;`

**v2.0 判定**：**降级为 P1**。v1.0 关于"NULL deref 风险"的判定**不成立**——因为 `AIRY_ERROR_NULL` 在 `pregel_engine.c:200-201` 等处执行后会 `return NULL`，后续代码（如 `message_queue_entry_t *entry = queue->front;`）**不会被执行**，因此不存在 NULL deref。

**但以下 P1 级问题仍然成立**：
1. **控制流不透明**（OS-KER-001 违规）：宏使用隐式 `return`，atoms 内开发者无法直接看到宏行为（定义在 `commons/utils/error/include/error.h`），维护性差。
2. **替代 goto 集中出口**：宏的隐式 return 使错误处理路径不可见，与 OS-KER-001 goto 集中出口要求冲突。
3. **缺少 `__attribute__((noreturn))` 标注**：虽然宏实际 return，但调用方无法从签名推断，应增加 `noreturn` 标注或注释明示。

**建议**：
- 立即在 `error.h` 宏定义处增加注释明示"此宏包含 return 语句"
- 长期改用 `goto out_xxx:` 集中出口替代隐式 return
- 工作量从 v1.0 的 ~3h（修复 NULL deref）调整为 ~2h（注释 + 长期 goto 重构另计）

### 5.4 P0-4 验证：IPC 消息头结构体三重违规

**v1.0 判定**：`06-ipc/README.md` 定义 `are_ipc_message_header_t`，与 SSoT `airy_ipc_msg_hdr` 在命名/类型/布局三重违规。

**v2.0 源码级复核**：

| 属性 | `06-ipc/README.md:27-42`（违规） | `120-cross-project-code-sharing.md:343-356`（SSoT） | `ipc.h:67-80`（源码实现） |
|------|--------------------------------|--------------------------------------------------|------------------------|
| 结构体名 | `typedef struct are_ipc_message_header` → `are_ipc_message_header_t` | `struct airy_ipc_msg_hdr` | `struct airy_ipc_msg_hdr` ✓ |
| 类型前缀 | `uint32_t`/`uint16_t`/`uint64_t` | `__u32`/`__u16`/`__u64` | `__u32`/`__u16`/`__u64` ✓ |
| 对齐属性 | 无 | `__attribute__((packed))` | `__attribute__((packed))` ✓ |
| 字段数 | **13 字段**（magic/version/msg_type/protocol/msg_id/trace_id/correlation_id/source[32]/target[32]/payload_len/flags/timestamp_ns/checksum/reserved） | **8 字段**（magic/opcode/flags/trace_id/timestamp_ns/src_task/dst_task/payload_len/reserved[84]） | 8 字段 ✓ |
| 字段语义 | `char source[32]`/`char target[32]`（字符串） | `__u64 src_task`/`__u64 dst_task`（整型 task ID） | `__u64 src_task`/`__u64 dst_task` ✓ |
| 大小验证 | 无 | `_Static_assert(sizeof(...) == 128)` | `_Static_assert(sizeof(...) == 128)` ✓ |

**v2.0 判定**：**确认存在，未修复**。文档侧 `06-ipc/README.md` 三重违规仍然存在；源码侧 `ipc.h` 已正确实现 SSoT 版本（合规标杆）。文档与源码割裂。

**工作量估算**：~3h（重写 `06-ipc/README.md`）。

### 5.5 P0-5 验证："操作系统"定位冲突（扩大至 51 处）

**v1.0 判定**：15+ 处文档误称"操作系统"。

**v2.0 源码级复核**：

`grep -rn "操作系统" docs/AirymaxRT --include="*.md"` = **51 处匹配，分布在 18 个文件**。

| 文件 | 出现次数 | 典型行号 |
|------|---------|---------|
| `10-architecture/04-microcorert.md` | 17 | — |
| `10-architecture/40-philosophy/01-design-philosophy.md` | 9 | L38/45/110/117/119 |
| `30-interfaces/04-mainpage.dox` | 2 | L2/6 |
| `30-interfaces/10-algorithms/README.md` | 3 | L179/182 |
| `TERMINOLOGY.md` | 4 | — |
| `10-architecture/00-architectural-principles.md` | 1 | L54 "Airymax 是一个**驱动多智能体协作的操作系统**" |
| `10-architecture/05-syscall.md` | 1 | L104 |
| `10-architecture/06-iron9-shared-model.md` | 1 | — |
| 其他 10 个文件 | 各 1-2 处 | — |

**v2.0 判定**：**确认存在，且比 v1.0 描述更严重**（51 处 vs v1.0 的"15+ 处"）。**未修复**。

**核心矛盾未消解**：`04-microcorert.md:183` 明确"MicroCoreRT 运行在用户态（Ring 3），依赖宿主操作系统"，与 `00-architectural-principles.md:54` "驱动多智能体协作的操作系统"直接矛盾。

**工作量估算**：~4h（18 文件，51 处替换）。

### 5.6 P0-6 验证：WebSocket 类型错误

**v1.0 判定**：`protocols_impl.c:117` WebSocket 适配器 type 设为 `PROTOCOL_HTTP`。

**v2.0 源码级复核**：

重新读取 `agentrt/protocols/common/src/protocols_impl.c:108-130`：

```c
108: static void init_static_adapters(void)
109: {
110:     if (s_adapters_init)
111:         return;
112:     s_http_adapter.type = PROTOCOL_HTTP;
113:     s_http_adapter.name = "http";
114:     ...
117:     s_ws_adapter.type = PROTOCOL_HTTP;        // ← 仍为 PROTOCOL_HTTP，应为 PROTOCOL_WEBSOCKET
118:     s_ws_adapter.name = "websocket";
119:     ...
122:     s_grpc_adapter.type = PROTOCOL_GRPC;      // ✓ gRPC 正确
127:     s_mqtt_adapter.type = PROTOCOL_MQTT;      // ✓ MQTT 正确
```

**v2.0 判定**：**确认存在，未修复**。`s_ws_adapter.type` 仍为 `PROTOCOL_HTTP`，应为 `PROTOCOL_WEBSOCKET`（或正确的 WebSocket 枚举值）。对比同函数内 `s_grpc_adapter.type = PROTOCOL_GRPC` 和 `s_mqtt_adapter.type = PROTOCOL_MQTT` 均正确，唯独 WebSocket 适配器类型错误。

**影响**：协议路由将 WebSocket 请求错误地路由到 HTTP 处理器，导致 WebSocket 握手/帧解析失败。

**工作量估算**：~0.5h（修复 + 单测）。

### 5.7 P0-7 验证：agent_registry 数据竞争

**v1.0 判定**：`agent_registry_core_get()` 在 `airy_mtx_unlock` 后返回 `&registry->entries[i]`，调用方在无锁状态下访问共享数据。

**v2.0 源码级复核**：

重新读取 `agentrt/daemons/market_d/src/agent_registry_core.c:123-137`：

```c
123: const agent_entry_t *agent_registry_core_get(agent_registry_t *registry, const char *agent_id)
124: {
125:     if (!registry || !registry->initialized || !agent_id) {
126:         AIRY_ERROR_NULL(AIRY_ERR_INVALID_PARAM, "null parameter");
127:     }
128:     airy_mtx_lock(&registry->lock);
129:     for (size_t i = 0; i < registry->entry_count; i++) {
130:         if (strcmp(registry->entries[i].id, agent_id) == 0) {
131:             airy_mtx_unlock(&registry->lock);    // ← 先解锁
132:             return &registry->entries[i];        // ← 后返回内部指针（调用方无锁访问）
133:         }
134:     }
135:     airy_mtx_unlock(&registry->lock);
136:     AIRY_ERROR_NULL(AIRY_ERR_OVERFLOW, "limit exceeded");
137: }
```

同模式 `agent_registry_core_get_latest_version()`（L194-208）：
```c
194: const char *agent_registry_core_get_latest_version(agent_registry_t *registry, const char *agent_id)
199:     airy_mtx_lock(&registry->lock);
200:     for (size_t i = 0; i < registry->entry_count; i++) {
201:         if (strcmp(registry->entries[i].id, agent_id) == 0) {
202:             airy_mtx_unlock(&registry->lock);           // ← 先解锁
203:             return registry->entries[i].latest_version; // ← 后返回内部 char* 指针
204:         }
205:     }
```

**v2.0 判定**：**确认存在，未修复**。两处函数均返回内部数据指针后才解锁，调用方在无锁状态下访问共享 `entries[]` 数组。多线程并发时，另一线程的 `agent_registry_core_remove()`（L102-121，会执行 `registry->entries[j] = registry->entries[j + 1]` 数组搬移）可能覆盖调用方持有的指针，导致 use-after-free 或读取不一致数据。

**v2.0 补充发现**：`agent_registry_core_list()`（L139-150）和 `agent_registry_core_search_by_tag()`（L210+）同样返回 `const agent_entry_t **out_entries`（指向内部 `entries[]` 的指针数组），虽然填充在锁内完成，但调用方解锁后访问仍存在相同数据竞争。**4 个函数均有此问题**，v1.0 仅识别了 2 个。

**修复建议**：改为拷贝到调用方缓冲区（推荐）：`agent_registry_core_get(reg, id, agent_entry_t *out)` 在锁内完成 `*out = registry->entries[i]` 后解锁。

**工作量估算**：~3h（4 个函数 API 签名变更 + 调用方更新，比 v1.0 的 ~2h 多 1h）。

### 5.8 P0-8 验证：[SC] 头文件清单不一致【恶化】

**v1.0 判定**：`06-iron9-shared-model.md` 第 6 头文件为 `bpf_struct_ops.h`，SSoT 为 `syscalls.h`。

**v2.0 源码级复核**：

重新读取 `06-iron9-shared-model.md:64-73`，6 个 [SC] 头文件清单为：

| # | `06-iron9-shared-model.md`（agentrt 侧） | `120-cross-project-code-sharing.md:76`（SSoT） | 一致性 |
|---|------------------------------------------|---------------------------------------------|--------|
| 1 | **`bpf_struct_ops.h`** | `memory_types.h` | ✗ 冲突 |
| 2 | `memory_types.h` | `security_types.h` | ✗ 错位 |
| 3 | `security_types.h` | `cognition_types.h` | ✗ 错位 |
| 4 | `cognition_types.h` | `sched.h` | ✗ 错位 |
| 5 | `sched.h` | `ipc.h` | ✗ 错位 |
| 6 | `ipc.h` | `syscalls.h` | ✗ 冲突 |
| — | **`syscalls.h` 完全缺失** | — | ✗ 缺失 |

**v2.0 判定**：**确认存在，且比 v1.0 描述更严重**（N7）。v1.0 称"`bpf_struct_ops.h` 作为第 6 个"，但 v2.0 实测 `bpf_struct_ops.h` **被列为第 1 个**，`syscalls.h` **完全不在 6 头文件清单中**。`120-cross-project-code-sharing.md:85` 明确指出 `bpf_struct_ops.h` 是"补充共享文件（非 [SC] 核心头文件）"，但 `06-iron9-shared-model.md` 将其列为 [SC] 核心 #1。

**源码侧验证**：`agentrt/commons/include/airymax/` 下实际存在 7 个 .h 文件（`bpf_struct_ops.h` + `memory_types.h` + `security_types.h` + `cognition_types.h` + `sched.h` + `ipc.h` + `syscalls.h` + `uapi_compat.h` 辅助）。源码侧 `syscalls.h` 物理存在且使用 Tab 8 缩进（合规），但文档侧 `06-iron9-shared-model.md` 未将其列入 [SC] 核心。

**工作量估算**：~1h（修正 `06-iron9-shared-model.md` 清单 + 移 `bpf_struct_ops.h` 至补充小节）。

### 5.9 P0-9 验证：文件路径引用错误

**v1.0 判定**：多个文档引用 `00-basic-theories/` 目录，实际为 `00-requirements/`。

**v2.0 源码级复核**：

`grep -rn "00-basic-theories" docs/AirymaxRT --include="*.md"` 仍匹配多个文件：

| 文件:行号 | 错误引用 |
|----------|---------|
| `TERMINOLOGY.md:604` | `00-basic-theories/01-mcis-cn.md` |
| `TERMINOLOGY.md:605` | `00-basic-theories/02-cognition-design-cn.md` |
| `TERMINOLOGY.md:606` | `00-basic-theories/03-memory-design-cn.md` |
| `TERMINOLOGY.md:607` | `00-basic-theories/04-design-principles-cn.md` |
| `04-syscall-api-contract.md:1366` | `../../00-basic-theories/04-design-principles-cn.md` |
| `02-skill-contract.md:42,43,1005,1006` | `../../00-basic-theories/...` |
| `05-logging-format.md:960` | `../../00-basic-theories/04-design-principles-cn.md` |

**v2.0 判定**：**确认存在，未修复**。`00-basic-theories/` 路径错误仍存在于至少 8 处。

**工作量估算**：~3h（~10 文件路径修正 + CI 链接检查器）。

### 5.10 P0-10 验证：ES-SEL4-7 分类残留冲突

**v1.0 判定**：agentrt-linux 闭源总纲中 ES-SEL4-7 分类残留冲突（5 vs 6 项）。

**v2.0 复核范围**：本轮聚焦 agentrt 源码与 AirymaxRT 文档，agentrt-linux 闭源总纲不在复核范围。维持 v1.0 判定。

---

## 6. v2.0 新发现（任务 e）

### 6.1 N1：DCLP 自旋等待无 yield/timeout（core_init.c）

**位置**：`agentrt/atoms/corekern/src/core_init.c:31-37`

```c
31: if (!atomic_compare_exchange_strong_explicit(&g_core_initialized, &expected, 2,
32:                                              memory_order_seq_cst, memory_order_seq_cst)) {
33:     if (expected == 2) {
34:         while (atomic_load_explicit(&g_core_initialized, memory_order_seq_cst) == 2) {}
35:     }
36:     return AIRY_SUCCESS;
37: }
```

**问题 1（CPU 空转）**：L34 自旋等待使用纯 `while` 循环，无 `sched_yield()`/`cpu_relax()`/`__builtin_ia32_pause()` 等让步机制。在初始化路径被多线程并发触发时，等待线程会 100% 占用 CPU 直到初始化线程完成。`memory_order_seq_cst` 在每次循环都插入全内存屏障，进一步加剧开销。

**问题 2（潜在死锁）**：L34 自旋等待**无超时**。若初始化线程在状态=2（initializing）时崩溃（segmentation fault、OOM kill 等），等待线程将**永久自旋**，导致 `airy_init()` 永久挂起。

**问题 3（内存序过度保守）**：L34 的轮询 `atomic_load_explicit(..., memory_order_seq_cst)` 使用全序，但 CAS 已在 L31 建立 happens-before，轮询只需 `memory_order_acquire` 即可保证可见性。

**修复建议**：
```c
while (atomic_load_explicit(&g_core_initialized, memory_order_acquire) == 2) {
#ifdef __x86_64__
    __builtin_ia32_pause();  /* CPU hint: spin-wait */
#else
    sched_yield();           /* POSIX fallback */
#endif
    /* 可选：增加超时计数器，超过 N 次后返回 AIRY_ETIMEOUT */
}
```

**严重度**：P1（不影响单线程初始化，但影响多线程并发初始化的健壮性）。

### 6.2 N2：cupolas_init() 所有错误路径泄漏 mutex

**位置**：`agentrt/cupolas/src/cupolas.c:76-164`

```c
84: if (cupolas_mutex_init(&g_cupolas.lock) != 0) {
85:     ... return cupolas_ERR_UNKNOWN;     /* mutex init 失败，无需 destroy */
88: }
91: cupolas_mutex_lock(&g_cupolas.lock);
...
96-107: if (config_mgr 加载失败) {
104:     cupolas_mutex_unlock(&g_cupolas.lock);
105:     return result;                     /* ← mutex 未 destroy！泄漏 */
107: }
...
112-122: if (perm 创建失败) {
119:     cupolas_mutex_unlock(&g_cupolas.lock);
121:     return cupolas_ERR_OUT_OF_MEMORY;  /* ← mutex 未 destroy！泄漏 */
122: }
...
124-137: if (sanitizer 创建失败) {
134:     cupolas_mutex_unlock(&g_cupolas.lock);
136:     return cupolas_ERR_OUT_OF_MEMORY;  /* ← mutex 未 destroy！泄漏 */
137: }
...
141-158: if (audit_logger 创建失败) {
155:     cupolas_mutex_unlock(&g_cupolas.lock);
157:     return cupolas_ERR_OUT_OF_MEMORY;  /* ← mutex 未 destroy！泄漏 */
158: }
```

**问题**：`cupolas_mutex_init(&g_cupolas.lock)` 在 L84 成功后，所有 4 个错误路径（L105/L121/L136/L157）均仅 `unlock` 而**未 `destroy`**。POSIX `pthread_mutex_t` 和 Windows `CRITICAL_SECTION` 均为内核对象，未 destroy 会导致资源泄漏（POSIX 下还可能触发 EINVAL 重新 init）。

**修复建议**：在所有错误路径的 `unlock` 后增加 `cupolas_mutex_destroy(&g_cupolas.lock);`，或改用 `goto cleanup_mutex:` 集中出口。

**严重度**：P1（资源泄漏，daemon 重启时累积）。

### 6.3 N3：cupolas_init() 非并发安全（初始化检查在锁外）

**位置**：`agentrt/cupolas/src/cupolas.c:78-82`

```c
78: if (g_cupolas.initialized) {       /* ← 检查在锁外 */
79:     return CUPOLAS_OK;
80: }
81:
82: __builtin_memset(&g_cupolas, 0, sizeof(g_cupolas));  /* ← 清零整个结构（含 mutex） */
```

**问题**：L78 的 `g_cupolas.initialized` 检查在 `cupolas_mutex_lock` 之前，两个线程可能同时通过检查并进入初始化：
1. 线程 A 通过 L78 检查，开始 L82 清零
2. 线程 B 此时也通过 L78 检查（因为 A 还未设置 `initialized=1`）
3. 线程 B 的 L82 清零覆盖 A 的初始化状态
4. 两线程同时进入 L91 `cupolas_mutex_lock`，导致状态混乱

**对比**：`core_init.c` 使用 DCLP（CAS + 状态机）正确处理了此问题；`cupolas.c` 未采用任何并发保护。

**修复建议**：参照 `core_init.c` 的 DCLP 模式，使用 `atomic_compare_exchange_strong` 守护初始化入口。

**严重度**：P1（多线程并发初始化时数据竞争，可能导致 cupolas 安全穹顶失效）。

### 6.4 N4：agentrt_ 前缀残留于 .bak 备份文件

**位置**：`agentrt/atoms/coreloopthree/src/cognition/critique/triple_coordinator.c.bak`

**统计**：`grep -rn "agentrt_" agentrt 2>/dev/null | grep "\.bak"` = **42 处**。

**问题**：备份文件 `triple_coordinator.c.bak` 含 `agentrt_error_t`、`agentrt_thinking_step_t` 等 typedef 残留，与当前 `airy_*` 前缀约定冲突。虽不影响编译，但：
1. 污染 grep 审计（v1.0 可能因此误计"agentrt_ 4058 处"）
2. 混淆代码考古（git blame / git log -p 可能误读历史）
3. 违反"仓库应保持干净"原则

**修复建议**：`rm agentrt/atoms/coreloopthree/src/cognition/critique/triple_coordinator.c.bak`（git history 已保留历史版本）。

**严重度**：P2（不影响功能，但影响审计准确性）。

### 6.5 N5：sched_d main.c 4 处重复错误清理块

**位置**：`agentrt/daemons/sched_d/src/main.c:252-314`

```c
252: if (ret != AIRY_SUCCESS || !g_service) {
254:     airy_mtx_destroy(&g_running_lock_sched_d);
255:     airy_sock_cleanup();
256:     return 1;
257: }
...
264: if (server_fd < 0) {
266:     destroy_service();
267:     airy_mtx_destroy(&g_running_lock_sched_d);
268:     airy_sock_cleanup();
269:     return 1;
270: }
...
290: if (ret != AIRY_SUCCESS || !g_event_driver_sched_d) {
292:     airy_sock_close(server_fd);
293:     destroy_service();
294:     airy_mtx_destroy(&g_running_lock_sched_d);
295:     airy_sock_cleanup();
296:     return 1;
297: }
...
306: if (daemon_event_driver_add_server_fd(...) != 0) {
308:     daemon_event_driver_destroy(g_event_driver_sched_d);
309:     airy_sock_close(server_fd);
310:     destroy_service();
311:     airy_mtx_destroy(&g_running_lock_sched_d);
312:     airy_sock_cleanup();
313:     return 1;
314: }
```

**问题**：4 个错误路径每个都重复 `destroy_service + airy_mtx_destroy + airy_sock_cleanup`（部分加 `airy_sock_close` 或 `daemon_event_driver_destroy`），违反 OS-KER-001 goto 集中出口要求。维护时极易遗漏新增资源的清理。

**v2.0 补充发现**：L308-313 的清理顺序存在隐患——`daemon_event_driver_destroy` 在 `add_server_fd` 失败时调用，但此时 event driver 可能处于部分初始化状态，destroy 可能访问未初始化字段。

**修复建议**：改用 `goto out_xxx:` 标签按资源分配逆序释放。

**严重度**：P1（维护性风险 + 潜在部分初始化 destroy 问题）。

### 6.6 N6：sync_compat.h 丢弃底层错误码

**位置**：`agentrt/commons/utils/sync/include/sync_compat.h:37-72`

```c
37: static inline int airy_mtx_init(sync_mutex_t *mutex, const void *attrs)
38: {
39:     (void)attrs;
40:     return sync_mutex_create(mutex, NULL) == SYNC_SUCCESS ? 0 : -1;  /* ← 仅返回 0/-1 */
41: }
46: static inline int airy_mtx_destroy(sync_mutex_t *mutex)
47: {
48:     return sync_mutex_free(*mutex) == SYNC_SUCCESS ? 0 : -1;          /* ← 仅返回 0/-1 */
49: }
54: static inline int airy_mtx_lock(sync_mutex_t *mutex)
55: {
56:     return sync_mutex_lock_ex(*mutex, NULL) == SYNC_SUCCESS ? 0 : -1; /* ← 仅返回 0/-1 */
57: }
```

**问题**：所有兼容层函数将底层 `sync_*` 的具体错误码（`SYNC_SUCCESS`/`SYNC_ERR_*`）丢弃，仅返回 `0`/`-1`。调用方无法区分失败原因（如 EBUSY/EDEADLK/ENOMEM 等），无法做差异化错误处理。

**对比**：POSIX `pthread_mutex_lock` 返回 `EBUSY`/`EDEADLK`/`EINVAL` 等具体错误码，调用方可据此重试或报警。`sync_compat.h` 的封装丢失了这一信息。

**修复建议**：直接透传 `sync_*` 返回值，或在文档中明确声明"兼容层仅返回 0/-1，需要详细错误码请直接调用 `sync_*`"。

**严重度**：P2（影响错误处理精度，但不影响正确性）。

### 6.7 N7：P0-8 恶化（bpf_struct_ops.h 升为 #1）

详见 §5.8。v1.0 称 `bpf_struct_ops.h` 为"第 6 个"，v2.0 实测为"第 1 个"，`syscalls.h` 完全缺失。

**严重度**：强化 P0-8（违规程度加深）。

### 6.8 N8：06-iron9-shared-model.md 递归注释未修复

**位置**：`docs/AirymaxRT/10-architecture/06-iron9-shared-model.md:214`

```c
214: #define AIRY_EOK        0       /* 成功（替代 AIRY_EOK） */
```

**问题**：注释说"替代 AIRY_EOK"但自身就是 `AIRY_EOK` 的定义，递归无意义。v1.0 P2-1 已识别但未修复。

**修复建议**：改为 `/* 成功 */` 或 `/* 替代 POSIX errno */`。

**严重度**：P2（文档瑕疵）。

### 6.9 跨平台兼容层质量评估

**验证对象**：`agentrt/commons/include/airymax/uapi_compat.h` + `agentrt/commons/utils/sync/include/sync_compat.h` + 8 个其他 compat 头文件。

| compat 头 | 用途 | 评估 | 问题 |
|-----------|------|------|------|
| `uapi_compat.h` | UAPI 类型 `__u8/__u16/__u32/__u64/__s32/__s64` 跨平台 | ✓ 良好 | 无重大问题；Linux 用 `<linux/types.h>`，macOS/Windows 用 `<stdint.h>` + typedef，`#ifndef __u8` 防重定义 |
| `sync_compat.h` | pthread 兼容 API（`airy_mtx_*`/`airy_cond_*`） | △ 一般 | N6：丢弃错误码 |
| `memory_compat.h` | `AIRY_MALLOC/CALLOC/REALLOC/FREE` 跨平台 | ✓ 良好 | 已在 v1.0 验证 |
| `string_compat.h` | 字符串操作跨平台 | ✓ 良好 | 已在 v1.0 验证 |
| `atomic_compat.h` | 原子操作跨平台 | ✓ 良好 | C11 `<stdatomic.h>` 封装 |
| `error_compat.h` | 错误码跨平台 | ✓ 良好 | — |
| `logging_compat.h` | 日志跨平台 | ✓ 良好 | — |
| `config_compat.h` | 配置跨平台 | ✓ 良好 | — |
| `observability_compat.h` | 可观测性跨平台 | ✓ 良好 | — |
| `compat.h` | 通用兼容 | ✓ 良好 | — |

**结论**：跨平台兼容层整体质量良好（9/10 良好），仅 `sync_compat.h` 存在 N6 问题。`uapi_compat.h` 的设计尤其值得肯定——清晰区分了 Linux/macOS/Windows/fallback 四种场景，并通过 `#ifndef __u8` 防止重定义冲突，是 [SC] 6 头文件能在非 Linux 平台编译的关键保障。

### 6.10 [SC] 6 头文件 ABI 兼容性评估

| 头文件 | Tab 8 | struct 无 typedef | kernel-doc | `_Static_assert` | UAPI 类型 | `__attribute__((packed))` | 评估 |
|--------|-------|-------------------|-----------|------------------|-----------|---------------------------|------|
| `ipc.h` | ✓ | ✓ `struct airy_ipc_msg_hdr` | ✓ `@magic/@opcode/@flags/@trace_id/...` | ✓ `sizeof == 128` | ✓ `__u32/__u16/__u64/__u8` | ✓ | **优秀** |
| `sched.h` | ✓ | ✓ `struct airy_task_desc` | ✓ `@magic/@prio/@vtime` | — | ✓ `__u32/__u16/__s32` | — | **优秀**（无 packed，因无对齐要求） |
| `security_types.h` | ✓ | ✓ | ✓ | — | ✓ | — | **优秀** |
| `cognition_types.h` | ✓ | ✓ | ✓ | — | ✓ | — | **优秀** |
| `memory_types.h` | ✓ | ✓ | ✓ | — | ✓ | — | **优秀** |
| `syscalls.h` | ✓ | ✓ | ✓ | — | ✓ | — | **优秀** |

**结论**：[SC] 6 头文件全部通过 ABI 兼容性验证。`ipc.h` 是最严格的实现（含 `_Static_assert` + `__attribute__((packed))` + 完整 kernel-doc），应作为其他头文件演进的目标标杆。

**v2.0 新发现**：`sched.h:57-61` 的 `airy_vtime_decay()` 是 `static inline` 函数，含完整 kernel-doc，使用 Q16.16 定点数运算（无浮点），符合 IRON-9 v2 "禁止 float 类型"约束。这是跨端 ABI 的优秀实践。

---

## 7. 修正后的综合评分

### 7.1 v1.0 vs v2.0 评分对比

| 维度 | v1.0 评分 | v2.0 评分 | 变化 | 修正原因 |
|------|----------|----------|------|---------|
| 源码工程 | 68/C+ | **66/C+** | -2 | P0-3 降级抵消部分扣分，但 N1（DCLP 自旋）/N2（mutex 泄漏）/N3（cupolas 竞争）/N5（sched_d 重复清理）新发现拉低 |
| 方案设计 | 70/B- | **68/C+** | -2 | P0-1 恶化（6→7 套）/P0-5 恶化（15→51 处）/P0-8 恶化（#6→#1） |
| 跨平台一致性 | 55/D+ | **54/D+** | -1 | 函数前缀缺失确认 + N6（sync_compat 丢错误码） |
| **总评** | **65/C+** | **63/C+** | **-2** | v1.0 评分略偏乐观 |

### 7.2 评分修正依据

**v1.0 偏乐观的点**：
1. **P0-3 误判**：v1.0 称"NULL deref 风险"，但宏实际 `return NULL`，无 deref。v1.0 此项扣分过高。
2. **P0-1 低估**：v1.0 称"6+ 套"，实际 7 套，且每个方案的冲突点更细（5 种 AIRY_EINVAL 值，v1.0 仅列 4 种）。
3. **P0-5 低估**：v1.0 称"15+ 处"，实际 51 处/18 文件，问题规模是 v1.0 的 3 倍。
4. **P0-8 低估**：v1.0 称 `bpf_struct_ops.h` 为"第 6 个"，实际为"第 1 个"，`syscalls.h` 完全缺失，违规程度更深。
5. **P0-7 低估**：v1.0 识别 2 个函数，实际 4 个函数（`get`/`get_latest_version`/`list`/`search_by_tag`）均有数据竞争。

**v2.0 新发现扣分**：
- N1（DCLP 自旋无 yield/timeout）：-1
- N2（cupolas mutex 泄漏）：-1
- N3（cupolas 非并发安全）：-1
- N5（sched_d 4 处重复清理）：-0.5
- N6（sync_compat 丢错误码）：-0.5

**P0-3 降级加分**：
- 宏实际 return，无 NULL deref：+2

**净变化**：+2 - 1 - 1 - 1 - 0.5 - 0.5 - 2（P0-1/5/8 恶化）= **-4**，但因 v1.0 已在 65 分，下限约束为 **63/C+**。

### 7.3 是否达到"可开发"状态

> **明确结论：agentrt 工程体系当前仍未达到"可开发"状态**。

| 判定标准 | v1.0 状态 | v2.0 状态 | 说明 |
|---------|----------|----------|------|
| 架构设计完成度 | ✓ 达标 | ✓ 达标 | MicroCoreRT / CoreLoopThree / MemoryRovol / Thinkdual / Cupolas / 12 Daemons 完整 |
| 工程标准规范 | ✗ 未达标 | ✗ 未达标 | 833 源文件系统性违反 OLK-6.6 六大支柱 |
| 无方案冲突点 | ✗ 未达标 | ✗ 未达标 | 8 项 P0 仍未修复（P0-3 降级为 P1） |
| 跨平台一致性 | ✗ 未达标 | ✗ 未达标 | `agentrt_*` 专属前缀缺失 + IPC 头三重违规 + 错误码 7 套 |
| SSoT 收敛 | △ 部分达标 | △ 部分达标 | 09-ssot-registry.md 已建立，但文档侧未对齐 |
| 历史问题修复 | ✓ 达标 | ✓ 达标 | koa-connect / io_uring / MGLRU 2.0 / daemon→daemons 全部修复 |
| 技术亮点保留 | ✓ 达标 | ✓ 达标 | 15 项技术亮点 + [SC] 6 头文件合规标杆 |
| 并发安全 | — 未评估 | ✗ 未达标 | N1（DCLP 自旋）/N3（cupolas 竞争）/P0-7（4 函数数据竞争） |

### 7.4 修正后的阻断项清单（v2.0）

进入 1.0.1 M1 代码开发前必须完成收敛的 P0（8 项，较 v1.0 减少 P0-3 降级）：

1. **P0-1**：错误码 7 套并行，~8h（文档统一）
2. **P0-5**：操作系统定位冲突（51 处/18 文件），~4h
3. **P0-4**：IPC 头三重违规，~3h
4. **P0-9**：文件路径引用错误，~3h
5. **P0-8**：[SC] 头文件清单不一致（恶化），~1h
6. **P0-6**：WebSocket 类型错误，~0.5h
7. **P0-7**：agent_registry 数据竞争（4 函数），~3h
8. **P0-2**：源码工程标准全面违规，~46h（可与 M1 并行渐进推进）

> **方案侧阻断项（P0-1/4/5/8/9）合计 ~19h**，建议在 1.0.1 M1 启动前 1 周内完成。
> **源码正确性阻断项（P0-6/7）合计 ~3.5h**，建议立即修复。
> **源码系统性改造（P0-2 ~46h）** 可在 M1 阶段并行推进。

### 7.5 v2.0 新增建议执行项

| 优先级 | 编号 | 问题 | 工作量 |
|--------|------|------|--------|
| P1 | N1 | core_init.c DCLP 自旋增加 yield + 超时 | ~1h |
| P1 | N2 | cupolas_init() 错误路径 destroy mutex | ~0.5h |
| P1 | N3 | cupolas_init() 改用 DCLP 守护并发入口 | ~1h |
| P1 | N5 | sched_d main.c 改用 goto 集中出口 | ~1h |
| P1 | P0-3（降级） | error.h 宏增加注释明示 return 行为 + 长期改 goto | ~2h |
| P2 | N4 | 删除 .bak 备份文件 | ~0.1h |
| P2 | N6 | sync_compat.h 透传错误码或文档化 | ~0.5h |
| P2 | N8 | 06-iron9-shared-model.md:214 递归注释 | ~0.1h |

### 7.6 建议的修复路径（v2.0 修正）

```
[Phase 0] 立即修复（~3.5h，0.1.1 收尾）
    ├── P0-6 WebSocket 类型错误（~0.5h）
    ├── P0-7 agent_registry 数据竞争 4 函数（~3h）
    ├── N4 删除 .bak 文件（~0.1h）
    └── N8 递归注释（~0.1h）

[Phase 1] 1.0.1 M1 启动前（~19h，方案侧 P0）
    ├── P0-1 错误码 7 套统一（~8h）
    ├── P0-5 "操作系统"定位冲突 51 处（~4h）
    ├── P0-4 IPC 头三重违规（~3h）
    ├── P0-9 文件路径引用错误（~3h）
    └── P0-8 [SC] 头文件清单（~1h）

[Phase 2] 1.0.1 M1 阶段 - 并发安全（~3.5h）
    ├── N1 DCLP 自旋 yield + 超时（~1h）
    ├── N2 cupolas mutex destroy（~0.5h）
    ├── N3 cupolas DCLP（~1h）
    └── N5 sched_d goto 集中出口（~1h）

[Phase 3] 1.0.1 M1 阶段（~46h，源码系统性改造）
    └── P0-2 源码工程标准全面违规
        ├── .clang-format 配置 + make format（~8h）
        ├── typedef 重构 540 处（~16h）
        ├── goto 集中出口替代错误宏（~12h，含 P0-3 降级项）
        ├── ASCII 装饰分节符移除（~4h）
        └── fprintf/__builtin_* 收口（~6h）

[Phase 4] 1.0.1 M1 内（~23h，P1 命名/前缀/文档）
    └── 见 v1.0 P1 清单

[Phase 5] 1.0.1 全阶段（~19h，P2 长期改进）
    └── 见 v1.0 P2 清单 + N6
```

**总工作量**：~115h（含 P0-2 系统性源码改造）或 ~69h（不含 P0-2）。

### 7.7 最终结论

agentrt 工程体系经过 v2.0 第二轮深化审查（源码级复核 + 新发现扫描），**确认 v1.0 识别的 10 项 P0 中 8 项仍然存在**，其中 P0-1（错误码 7 套）、P0-5（操作系统 51 处）、P0-8（bpf_struct_ops.h 升为 #1）三项**比 v1.0 描述的更严重**。**P0-3 经源码级复核降级为 P1**（v1.0 对 `AIRY_ERROR_NULL` 宏行为的判定有误，宏实际包含 `return NULL`，无 NULL deref）。

v2.0 新发现 8 项问题，其中 N1（DCLP 自旋无 yield/timeout）、N2（cupolas mutex 泄漏）、N3（cupolas 非并发安全）三项为 P1 级并发安全问题，需在 M1 阶段优先修复。

**修正后综合评分：63/C+**（较 v1.0 的 65/C+ 下调 2 分，反映 P0 恶化与新发现）。

**关键决策点（需用户裁决）**：

| # | 决策点 | v1.0 推荐 | v2.0 修正推荐 |
|---|--------|----------|---------------|
| 1 | 错误码统一 | SSoT 13 个 `AIRY_E*` 宏 | **维持**，但需明确 `AIRY_ETIMEOUT` vs `AIRY_ETIMEDOUT` 二选一 |
| 2 | P0-3 宏行为 | 先审查宏定义再决定 | **已审查**：宏含 return，**降级为 P1**，长期改 goto |
| 3 | P0-8 头文件清单 | bpf_struct_ops.h 移至补充 | **维持**，但需注意 v2.0 发现 bpf_struct_ops.h 已升为 #1 |
| 4 | N1 DCLP 自旋 | — | 增加 yield + 超时，参照 `sched_yield()`/`__builtin_ia32_pause()` |
| 5 | N3 cupolas 并发 | — | 参照 `core_init.c` 的 DCLP 模式重写 `cupolas_init()` |
| 6 | P0-7 修复范围 | 2 个函数 | **扩大至 4 个函数**（含 `list`/`search_by_tag`） |

完成上述修复路径后，agentrt 工程体系可达到"可开发"状态，综合评分预期从 63/C+ 提升至 80/B+。

---

## 附录 A：v1.0 报告索引

| 报告 | 路径 | 行数 | 综合评分 |
|------|------|------|----------|
| 00 综合分析 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v1.0/00-comprehensive-analysis.md` | 614 | 65/C+ |
| 01 atoms 源码深读 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v1.0/01-atoms-source-deep-review.md` | 840 | 架构 A / 技术 A- / 工程标准 C+ |
| 02 daemons 等源码深读 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v1.0/02-daemons-others-source-deep-review.md` | 453 | 用户态工程标准系统性违规 |
| 03 AirymaxRT 方案审查 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v1.0/03-airymaxrt-solution-review.md` | 887 | 62/C+ |

## 附录 B：术语对照

| 术语 | 定义 |
|------|------|
| OLK-6.6 | Linux 6.6 内核基线编码风格（agentrt-linux 工程标准基线） |
| IRON-9 v2 | agentrt 三层模型（[SC] 共享契约层 / [SS] 语义同源层 / [IND] 完全独立层） |
| DCLP | Double-Checked Locking Pattern（双重检查锁定模式） |
| BAN-333 | pregel_engine max_workers=1 强制串行降级规则 |
| ASan | AddressSanitizer 内存错误检测器 |
| SSoT | Single Source of Truth（单一真值源） |
| [SC] | Shared Contract（共享契约层） |
| [SS] | Semantic Sibling（语义同源层） |
| [IND] | Independent（完全独立层） |
| MicroCoreRT | agentrt 微核心运行时（用户态 Ring 3） |
| CoreLoopThree | 三阶段认知循环（cognition/execution/memory） |
| MemoryRovol | 四层记忆系统（L1 Raw / L2 Feature / L3 Structure / L4 Pattern） |
| Cupolas | 安全穹顶（7 子系统） |
| UAPI | User-space API（用户空间接口，内核态 `__u32` 等类型） |

## 附录 C：v2.0 审查工具与命令

```bash
# 符号链接验证
readlink docs/AirymaxRT/50-engineering-standards
# = ../AirymaxOS/50-engineering-standards

# 共享文件数验证
find -L docs/AirymaxRT/50-engineering-standards -type f -name "*.md" | wc -l  # = 23
find docs/AirymaxOS/50-engineering-standards -type f -name "*.md" | wc -l      # = 23

# 函数前缀统计
grep -rn "\bairy_[a-z]" agentrt --include="*.c" --include="*.h" | wc -l        # = 13238
grep -rn "agentrt_" agentrt --include="*.c" --include="*.h" | wc -l            # = 0
grep -rn "agentrt_" agentrt 2>/dev/null | grep "\.bak" | wc -l                 # = 42

# 错误码方案验证
grep -n "AIRY_EOK\|AIRY_EINVAL\|AIRY_ENOMEM" docs/AirymaxRT/10-architecture/00-architectural-principles.md
grep -n "AIRY_EOK\|AIRY_EINVAL\|AIRY_ENOMEM" docs/AirymaxRT/10-architecture/06-iron9-shared-model.md
grep -n "AIRY_EOK\|AIRY_EINVAL\|AIRY_ENOMEM" docs/AirymaxRT/10-architecture/05-syscall.md

# "操作系统"误称统计
grep -rn "操作系统" docs/AirymaxRT --include="*.md" | wc -l                    # = 51

# 路径错误统计
grep -rn "00-basic-theories" docs/AirymaxRT --include="*.md" | wc -l           # = 10+

# AIRY_ERROR_NULL 宏定义
# 位置：agentrt/commons/utils/error/include/error.h:634-638
# 关键：宏包含 return NULL; 语句

# WebSocket 类型错误
sed -n '117p' agentrt/protocols/common/src/protocols_impl.c
# = s_ws_adapter.type = PROTOCOL_HTTP;

# agent_registry 数据竞争
sed -n '123-137p' agentrt/daemons/market_d/src/agent_registry_core.c
# 关键：L131 unlock 后 L132 return &registry->entries[i]
```

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>

---

**报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-13 | 审查版本：v2.0
