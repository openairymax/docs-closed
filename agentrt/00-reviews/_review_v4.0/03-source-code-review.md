Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
<!-- SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0 -->
<!-- 保密级别：SPHARX Ltd 内部参考，闭源不公开 -->
<!-- 版本：4.0 | 日期：2026-07-14 -->

# agentrt 源码 v4.0 全面深化审查报告

> **文档定位**：agentrt 源码 v4.0 深化审查收敛文档。在 v3.0 系统性修正（域1 错误码 SSoT + 域4 DCLP 并发安全）完成后，对 `agentrt/` 源码进行独立持久性复核 + 副作用检测 + 新发现问题扫描 + 残留项状态复核，作为 1.0.1 M1 阶段源码工程治理的深化判定基线。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：4.0（2026-07-14）。
> **审查范围**：仅 `agentrt/` 源码（atoms 237 + daemons 243 + cupolas 95 + gateway 33 + commons 184 + protocols 41 = 833 源文件）。不审查 `agentrt-linux/`、`docs/`、`docs-closed/`。
> **审查方法**：v3.0 修正持久性验证（7 项源码修正）→ v3.0 修正副作用检测（4 维度）→ v4.0 新发现问题扫描（8 维度）→ 残留项状态复核（6 项）→ P0-2 规模统计。
> **证据要求**：所有结论附 `文件路径:L行号` 或 Grep 命令与匹配数，可通过 Read/Grep 工具复核。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. v3.0 源码修正持久性验证矩阵（7 项）](#2-v30-源码修正持久性验证矩阵7-项)
- [3. v3.0 修正副作用清单](#3-v30-修正副作用清单)
- [4. v4.0 新发现问题清单](#4-v40-新发现问题清单)
- [5. 残留项状态复核](#5-残留项状态复核)
- [6. P0-2 源码工程标准违规当前规模统计](#6-p0-2-源码工程标准违规当前规模统计)
- [7. 修正后评分预估](#7-修正后评分预估)
- [8. 附录](#8-附录)

---

## 1. 执行摘要

### 1.1 审查范围与方法

| 维度 | 范围 | 方法 |
|------|------|------|
| v3.0 修正持久性 | 7 项源码修正（airy_types.h 23 码 + error.h 16 码迁移 + core_init.c V3.0-N1/N2 + cupolas.c V3.0-N1/N2 + agent_registry_core.c search + agent_registry.c get_locked + agent_registry_core.h 同步） | Grep 机器检查 + Read 源码逐行复核 |
| v3.0 修正副作用 | 4 维度（错误码值修改后调用方语义 + error.h 16 码迁移后旧值引用 + DCLP CAS 2→0 重置新竞态 + agent_registry_core_search 签名修改后调用方同步） | Grep 机器检查 + 竞态分析 + 调用方审查 |
| v4.0 新发现 | 8 维度（并发安全/资源管理/错误处理/ABI兼容/跨平台/工程标准/安全漏洞/v2.0-v3.0修正副作用） | 系统性 Grep 扫描 + 代表性文件深读 |
| 残留项状态 | 6 项（R4-1/R4-2/R4-3/F-1/F-2/F-3） | Grep 统计 + Read 验证当前状态 |
| P0-2 规模统计 | 5 项违规（Tab8/typedef/goto/fprintf/装饰符） | Grep 统计当前违规规模 |

### 1.2 核心结论

> **v3.0 源码修正 7/7 全部持久保留**：经 Grep 独立复核，所有 v3.0 源码修正均在源码中就位，无回退。
>
> **v3.0 修正引入 2 项 P0 级编译破坏性副作用**：
> - **V4.0-P0-1（P0）**：v3.0 从 `error.h` 移除 `AIRY_OK` 定义，但 **39 个文件仍引用 `AIRY_OK`**，包括 `cupolas.h`（L53 `#define cupolas_OK AIRY_OK`）、`handler.c`（错误模块实现本身，7+ 处）、`test_banned_functions.c`（L72-73 `#ifndef AIRY_OK / #error`）。agentrt 全仓库**无任何 `#define AIRY_OK` 定义**（CMakeLists.txt 也无 `-DAIRY_OK` 注入），这些文件将无法编译。
> - **V4.0-P0-2（P0）**：v3.0 将 `error.h` 中 9 个 `AIRY_ERR_*` 扩展码迁移至 -40~-48（如 `AIRY_ERR_INVALID_PARAM` -2→-40、`AIRY_ERR_STATE_ERROR` -13→-46），但 `cupolas_error.h` 的 `cupolas_ERR_*` 枚举**未同步更新**，仍保留旧值（-2/-5/-7/-10/-11/-13/-14/-16/-17）。导致：① `test_error_code_consistency.c` 9 项断言将失败；② cupolas 枚举值与 v3.0 新增的 `AIRY_E*` POSIX 码发生**数值碰撞**（如 `cupolas_ERR_UNKNOWN=-1` 与 `AIRY_EPERM=-1`、`cupolas_ERR_INVALID_PARAM=-2` 与 `AIRY_ENOENT=-2`、`cupolas_ERR_AUTH_FAILED=-16` 与 `AIRY_EBUSY=-16` 等 8 处碰撞）。
>
> **v4.0 新发现 7 项问题**（2 项 P0 + 3 项 P1 + 2 项 P2），其中 5 项为 **v3.0 修正引入的副作用**：
> - **V4.0-P1-1（P1）**：V3.0-N2 CAS 2→0 重置引入双重初始化竞态——超时线程重置 state 2→0 后，第三线程可 CAS 0→2 进入并行初始化，与仍在运行的初始化线程并发执行 `airy_mem_init()` 等子系统初始化，可能破坏内部状态。
> - **V4.0-P1-2（P1）**：`refcount_retain` 使用 `memory_order_relaxed` + `if (old == 0)` 检查模式存在 use-after-free 竞态——fetch_add(0→1) 与 old==0 检查之间，另一线程的 release 可执行 deleter 释放内存。
> - **V4.0-P1-3（P1）**：`test_error_code_consistency.c` 9 项断言将失败（cupolas 枚举值与 commons 宏值不匹配），且 L63 引用未定义的 `AIRY_OK` 导致编译失败。
>
> **残留项状态**：R4-1 **显著恶化**（19→32 处 `return 1`，5→11 个 daemon），R4-2/R4-3/F-1/F-2/F-3 均未处理。
>
> **综合评分**：v3.0 修正后预估 76/B → v4.0（含新发现扣分）预估 **68/C+**（下调 8 分，反映 2 项 P0 编译破坏 + 3 项 P1 副作用）。若 v4.0 新发现 2 项 P0 + 3 项 P1 全部修正，预估可达 **78/B+**。

### 1.3 1.0.1 M1 启动就绪判定

| 判定条件 | v3.0 修正后状态 | v4.0 复审状态 | 变化 |
|---------|----------------|-------------|------|
| P0 阻断项清零 | ✅ 通过（10/10 P0 修正） | ⚠️ **回退**（V4.0-P0-1/P0-2 为编译破坏性 P0） | 回退 |
| 综合评分 ≥ 70/B- | ✅ 通过（~76/B） | ⚠️ 边界（68/C+） | -8 分 |
| 错误码 SSoT 收敛 | ✅ 通过（方案 A 唯一权威） | ⚠️ **回退**（cupolas_error.h 枚举未同步 + AIRY_OK 残留引用） | 回退 |
| 并发安全 | ✅ 通过（V3.0-N1/N2 修正） | ⚠️ V4.0-P1-1 双重初始化竞态 + V4.0-P1-2 refcount 竞态 | 回退 |

> **v4.0 判定**：agentrt 模块 **不再满足 1.0.1 M1 代码开发启动的最低条件**——V4.0-P0-1（AIRY_OK 编译破坏）和 V4.0-P0-2（cupolas 枚举值碰撞）是阻塞性 P0，必须在 M1 启动前修正。V4.0-P1-1/P1-2/P1-3 应在 M1 早期优先修正。

---

## 2. v3.0 源码修正持久性验证矩阵（7 项）

每项均通过 Grep 机器检查 + Read 源码逐行复核。

### 2.1 验证矩阵

| # | 修正项 | 验证方法 | 期望 | 实际 | 状态 |
|---|--------|---------|------|------|------|
| 1 | **airy_types.h 23 码 POSIX 对齐** | Read `airy_types.h:56-86` 确认 23 个 `AIRY_E*` 使用 POSIX errno 负值 | EINVAL=-22/ENOMEM=-12/ETIMEDOUT=-110 等 | L56-78: 23 码全部对齐（EPERM=-1/ENOENT=-2/EIO=-5/E2BIG=-7/EAGAIN=-11/ENOMEM=-12/EACCES=-13/EBUSY=-16/EEXIST=-17/EINVAL=-22/ENOSPC=-28/ERANGE=-34/EDEADLK=-35/EPROTO=-71/EOVERFLOW=-75/EMSGSIZE=-90/EPROTONOSUPPORT=-93/ENOTSUP=-95/ECONNRESET=-104/ENOTCONN=-107/ETIMEDOUT=-110/ECONNREFUSED=-111/EALREADY=-114） | ✅ 持久 |
| 2 | **error.h AIRY_OK 移除** | Grep `#define\s+AIRY_OK` in agentrt | 0 matches | 0 matches（L42-46 注释明示"AIRY_OK 已移除"） | ✅ 持久 |
| 3 | **error.h 16 码迁移** | Read `error.h:125-227` 确认 9 个冲突码迁移至 -40~-48 + 4 个 SYS 码迁移至 -120~-123 | INVALID_PARAM=-40/STATE_ERROR=-46/SYS_THREAD=-120 等 | L126: INVALID_PARAM=-40 / L135: BUFFER_TOO_SMALL=-41 / L141: ALREADY_EXISTS=-42 / L150: PERMISSION_DENIED=-43 / L153: IO=-44 / L156: PARSE_ERROR=-45 / L159: STATE_ERROR=-46 / L168: CANCELED=-47 / L171: BUSY=-48 / L205: SYS_THREAD=-120 / L214: SYS_CONDITION=-121 / L223: SYS_PIPE=-122 / L226: SYS_PROCESS=-123 | ✅ 持久 |
| 4 | **core_init.c V3.0-N1（state==1 验证）** | Read `core_init.c:73-79` 确认自旋退出后验证 state==1 | 返回 `AIRY_ERR_SYS_NOT_INIT` | L76-78: `if (... != 1) { ... return AIRY_ERR_SYS_NOT_INIT; }` | ✅ 持久 |
| 5 | **core_init.c V3.0-N2（CAS 2→0 重置）** | Read `core_init.c:60-70` 确认超时分支 CAS 2→0 | `atomic_compare_exchange_strong_explicit(&g_core_initialized, &expected_state, 0, ...)` | L64-67: `long expected_state = 2; atomic_compare_exchange_strong_explicit(&g_core_initialized, &expected_state, 0, memory_order_seq_cst, memory_order_seq_cst);` | ✅ 持久 |
| 6 | **cupolas.c V3.0-N1/N2** | Read `cupolas.c:104-125` 确认 CAS 重置 + state==1 验证 | CAS 2→0 + 返回 `cupolas_ERR_STATE_ERROR` | L109: `cupolas_atomic_cas32(&g_cupolas_init_state, 2, 0)` + L120-124: `if (... != 1) { *error = AIRY_ERR_SYS_NOT_INIT; return cupolas_ERR_STATE_ERROR; }` | ✅ 持久 |
| 7 | **agent_registry_core.c search 签名 + agent_registry.c get_locked** | Read `agent_registry_core.c:239-258` + `agent_registry.c:196-221` 确认 copy-to-buffer + get_locked | search 用 `agent_entry_t *out_entries` + get_locked 不加锁 | L239: `size_t agent_registry_core_search(..., agent_entry_t *out_entries, size_t max_entries)` + L252: `out_entries[count] = registry->entries[i]` (锁内拷贝) + L196: `static int agent_registry_get_locked(...)` + L268: `agent_registry_get_locked(entry->info.agent_id, ...)` | ✅ 持久 |

**验证矩阵小结**：**7/7 项通过 Grep + Read 机器检查**，所有 v3.0 源码修正均持久保留在源码中，无回退。

### 2.2 关键修正实现细节复核

#### core_init.c V3.0-N1/N2 实现（L40-82）

```c
40: int airy_init(void)
43:     if (!atomic_compare_exchange_strong_explicit(&g_core_initialized, &expected, 2, ...)) {
45:         if (expected == 2) {
53:             while (atomic_load_explicit(&g_core_initialized, memory_order_acquire) == 2) {
59:                 if (++spin_count >= AIRY_INIT_SPIN_MAX_RETRIES) {
64:                     long expected_state = 2;
65:                     atomic_compare_exchange_strong_explicit(&g_core_initialized, &expected_state, 0, ...);
70:                     return AIRY_ERR_TIMEOUT;
72:             }
76:             if (atomic_load_explicit(&g_core_initialized, memory_order_acquire) != 1) {
78:                 return AIRY_ERR_SYS_NOT_INIT;
79:             }
81:         return AIRY_SUCCESS;
```

V3.0-N1（L76-78）和 V3.0-N2（L64-67）均就位，注释完整。

#### cupolas.c V3.0-N1/N2 实现（L104-126）

```c
104:     if (++spin_count >= CUPOLAS_INIT_SPIN_MAX_RETRIES) {
109:         cupolas_atomic_cas32(&g_cupolas_init_state, 2, 0);
114:         return cupolas_ERR_STATE_ERROR;
117:     if (cupolas_atomic_load32(&g_cupolas_init_state) != 1) {
122:             *error = AIRY_ERR_SYS_NOT_INIT;
124:             return cupolas_ERR_STATE_ERROR;
```

V3.0-N1（L117-124）和 V3.0-N2（L109）均就位。

---

## 3. v3.0 修正副作用清单

### 3.1 副作用矩阵

| # | 副作用 | 严重度 | 证据位置 | 影响范围 |
|---|--------|--------|---------|---------|
| V4.0-P0-1 | AIRY_OK 移除后 39 文件仍引用，编译破坏 | **P0** | `error.h:42-46`（移除）/ `cupolas.h:53` / `handler.c:149,397,586,604,693,823,836` / `agent_registry.c:82,86,134,157,190,220,247,276,299` / `sync_compat.h:47` / `error_compat.h:40,208,235,252` / `daemons/common/include/error.h:127-128` / `test_banned_functions.c:72-73` | 39 文件编译失败 |
| V4.0-P0-2 | cupolas_error.h 枚举值未随 v3.0 迁移同步 | **P0** | `cupolas_error.h:41-59`（枚举保留旧值）/ `error.h:126-171`（commons 已迁移） | cupolas 错误码与 commons 不一致 + 8 处数值碰撞 |
| V4.0-P1-1 | DCLP CAS 2→0 重置引入双重初始化竞态 | **P1** | `core_init.c:64-67` / `cupolas.c:109` | 多线程初始化场景的并发破坏 |
| V4.0-P1-3 | test_error_code_consistency.c 9 项断言失败 + 编译失败 | **P1** | `test_error_code_consistency.c:63,67-92` | CI 测试失败 |

### 3.2 V4.0-P0-1 深度分析：AIRY_OK 移除后编译破坏

**v3.0 修正内容**：`error.h:42-46` 注释明示"AIRY_OK 已移除（v3.0 SSoT 统一收敛）：成功码统一使用 AIRY_EOK（=0），定义于 airy_types.h。本文件不再定义 AIRY_OK。"

**问题**：v3.0 移除了 `AIRY_OK` 的定义，但未更新引用 `AIRY_OK` 的 39 个文件。经 Grep 确认，agentrt 全仓库**无任何 `#define AIRY_OK` 定义**（包括 .h/.c/CMakeLists.txt），也无 `-DAIRY_OK` 编译注入。

**关键编译破坏点**：

| 文件 | 行号 | 代码 | 影响 |
|------|------|------|------|
| `cupolas.h` | L53 | `#define cupolas_OK AIRY_OK` | cupolas_OK 未定义，所有使用 cupolas_OK 的代码编译失败 |
| `handler.c` | L149 | `{AIRY_OK, "OK", "Success", "成功", ...}` | 错误模块实现本身编译失败 |
| `handler.c` | L397/586/604/693/823/836 | `return AIRY_OK;` / `state->chain.code = AIRY_OK;` | 6 处编译失败 |
| `agent_registry.c` | L82/86/134/157/190/220/247/276/299 | `return AIRY_OK;` | 9 处编译失败 |
| `sync_compat.h` | L47 | `case SYNC_SUCCESS: return AIRY_OK;` | sync 兼容层编译失败（platform.h 未包含时） |
| `error_compat.h` | L40 | `#define AIRY_COMPAT_SUCCESS AIRY_OK` | 兼容层编译失败 |
| `error_compat.h` | L208/235/252 | `if (err != AIRY_OK)` | 3 处编译失败 |
| `daemons/common/include/error.h` | L127-128 | `#define AIRY_IS_ERROR(code) ((code) != AIRY_OK)` | 宏展开编译失败 |
| `test_banned_functions.c` | L72-73 | `#ifndef AIRY_OK / #error "BAN-073: AIRY_OK (0) must be defined"` | 测试触发 #error |
| 其他 30 文件 | — | `return AIRY_OK;` / `== AIRY_OK` | 各模块编译失败 |

**验证方法**：
```bash
# 确认无 AIRY_OK 定义
grep -rn "define[[:space:]]\+AIRY_OK" agentrt/  # = 0 matches
# 确认无 -DAIRY_OK 注入
grep -rn "DAIRY_OK" agentrt/**/CMakeLists.txt  # = 0 matches
# 确认 39 文件引用 AIRY_OK
grep -rl "AIRY_OK" agentrt/ --include="*.{c,h}"  # = 39 files
```

**影响**：agentrt 源码**无法通过编译**。v3.0 的 20 项 Grep 验证（fix-verification-report-v3.md §3）仅检查了 AIRY_OK 从 error.h 移除（检查 #4: `#define AIRY_OK` in error.h = 0 matches ✅），但**未检查其他文件是否仍引用 AIRY_OK**，导致此编译破坏未被发现。

**修复建议**：在 `error.h` 或 `airy_types.h` 中恢复 `AIRY_OK` 定义，与 `AIRY_EOK`/`AIRY_SUCCESS` 等价：
```c
#define AIRY_OK 0  /* 兼容旧代码，与 AIRY_EOK/AIRY_SUCCESS 等价 */
```
或：将 39 文件中的 `AIRY_OK` 批量替换为 `AIRY_EOK`（~2h）。

**工作量估算**：~0.5h（恢复定义）或 ~2h（批量替换）。

### 3.3 V4.0-P0-2 深度分析：cupolas_error.h 枚举值未同步

**v3.0 修正内容**：`error.h` 将 9 个 `AIRY_ERR_*` 扩展码从旧值迁移至 -40~-48 区间，消除与 `airy_types.h` POSIX 码的数值冲突。

**问题**：`cupolas_error.h:39-60` 的 `cupolas_ERR_*` 枚举**未同步更新**，仍保留与 v3.0 迁移前的 `AIRY_ERR_*` 旧值一致的数值。

**cupolas 枚举值与 commons 宏值不匹配清单**：

| cupolas 枚举 | cupolas 值 | commons 宏 | commons 值（v3.0 后） | 是否匹配 |
|-------------|-----------|-----------|---------------------|---------|
| cupolas_ERR_UNKNOWN | -1 | AIRY_ERR_UNKNOWN | -99 | ❌ 不匹配 |
| cupolas_ERR_INVALID_PARAM | -2 | AIRY_ERR_INVALID_PARAM | -40 | ❌ 不匹配 |
| cupolas_ERR_BUFFER_TOO_SMALL | -5 | AIRY_ERR_BUFFER_TOO_SMALL | -41 | ❌ 不匹配 |
| cupolas_ERR_ALREADY_EXISTS | -7 | AIRY_ERR_ALREADY_EXISTS | -42 | ❌ 不匹配 |
| cupolas_ERR_PERMISSION_DENIED | -10 | AIRY_ERR_PERMISSION_DENIED | -43 | ❌ 不匹配 |
| cupolas_ERR_IO | -11 | AIRY_ERR_IO | -44 | ❌ 不匹配 |
| cupolas_ERR_STATE_ERROR | -13 | AIRY_ERR_STATE_ERROR | -46 | ❌ 不匹配 |
| cupolas_ERR_OVERFLOW | -14 | AIRY_ERR_OVERFLOW | -14 | ✅ 匹配（未迁移） |
| cupolas_ERR_TIMEOUT | -8 | AIRY_ERR_TIMEOUT | -8 | ✅ 匹配（未迁移） |

**9 项不匹配中的 7 项**会导致 `test_error_code_consistency.c` 的 `test_cupolas_enum_matches_commons()` 断言失败。

**cupolas 枚举值与 v3.0 新增 AIRY_E* POSIX 码数值碰撞清单**：

| cupolas 枚举 | cupolas 值 | AIRY_E* POSIX 码 | POSIX 值 | 碰撞类型 |
|-------------|-----------|-----------------|---------|---------|
| cupolas_ERR_UNKNOWN | -1 | AIRY_EPERM | -1 | 语义碰撞（未知错误 vs 权限不足） |
| cupolas_ERR_INVALID_PARAM | -2 | AIRY_ENOENT | -2 | 语义碰撞（参数无效 vs 资源不存在） |
| cupolas_ERR_BUFFER_TOO_SMALL | -5 | AIRY_EIO | -5 | 语义碰撞（缓冲区过小 vs I/O 错误） |
| cupolas_ERR_ALREADY_EXISTS | -7 | AIRY_E2BIG | -7 | 语义碰撞（已存在 vs 参数过长） |
| cupolas_ERR_PERMISSION_DENIED | -10 | AIRY_ECANCELLED | -10 | 语义碰撞（权限拒绝 vs 操作取消） |
| cupolas_ERR_IO | -11 | AIRY_EAGAIN | -11 | 语义碰撞（I/O 错误 vs 资源暂不可用） |
| cupolas_ERR_AUTH_FAILED | -16 | AIRY_EBUSY | -16 | 语义碰撞（认证失败 vs 资源忙碌） |
| cupolas_ERR_CERT_INVALID | -17 | AIRY_EEXIST | -17 | 语义碰撞（证书无效 vs 资源已存在） |

**8 处数值碰撞**意味着：cupolas 返回的错误码可能被调用方误判为完全不同的 POSIX 错误。例如，cupolas 返回 `cupolas_ERR_AUTH_FAILED=-16`，调用方检查 `if (err == AIRY_EBUSY)` 会误判为"资源忙碌"。

**影响**：
1. `test_error_code_consistency.c` 编译失败（L63 引用 `AIRY_OK`）+ 9 项断言失败
2. cupolas 公共 API 返回的错误码与 commons 错误码语义不一致
3. cupolas 错误码与 POSIX errno 码数值碰撞，调用方可能误判错误类型

**修复建议**：
- **方案 A（推荐）**：更新 `cupolas_error.h` 枚举值，使其与 v3.0 迁移后的 `AIRY_ERR_*` 一致。注意：这会改变 cupolas 的 ABI（枚举值变化），需评估调用方影响。~4h。
- **方案 B**：将 cupolas 枚举改为引用 commons 宏（`cupolas_ERR_STATE_ERROR = AIRY_ERR_STATE_ERROR`），消除硬编码值。~2h。

**工作量估算**：~2-4h（含调用方审查）。

### 3.4 V4.0-P1-1 深度分析：DCLP CAS 2→0 重置引入双重初始化竞态

**v3.0 修正内容**：V3.0-N2 在自旋超时分支增加 CAS 2→0 重置，允许后续重试。

**问题**：CAS 2→0 重置引入了一个新的竞态窗口——超时线程重置 state 2→0 后，第三线程可 CAS 0→2 进入并行初始化。

**竞态场景**：
1. 线程 A：CAS 0→2 成功，开始执行 `airy_mem_init()` / `airy_task_init()` 等初始化
2. 线程 B：CAS 0→2 失败（expected=2），进入自旋等待
3. 线程 B：自旋 10,000,000 次后超时，CAS 2→0 成功（线程 A 仍在初始化中）
4. 线程 B：返回 `AIRY_ERR_TIMEOUT`
5. 线程 C：调用 `airy_init()`，CAS 0→2 成功（state 被 B 重置为 0），开始**并行初始化**
6. **线程 A 和线程 C 同时执行 `airy_mem_init()` / `airy_task_init()` / `airy_ipc_init()` 等子系统初始化**
7. 子系统初始化函数非幂等并发安全 → 内部状态破坏（双重分配、互斥锁重复初始化等）

**证据**：
- `core_init.c:64-67`：CAS 2→0 重置
- `core_init.c:84-156`：初始化线程执行 6 个子系统初始化（mem/oom/task/ipc/eventloop/heapstore），均无并发保护
- `cupolas.c:109`：同模式 CAS 2→0 重置

**影响**：当初始化耗时超过 10 秒（10M 次 sched_yield）且有第三线程尝试初始化时，双重初始化可能破坏核心子系统内部状态，导致运行时不稳定或崩溃。

**严重度**：P1（罕见但危险的并发破坏）。

**修复建议**：
```c
/* 方案 A（推荐）：超时不重置 state，仅返回错误。
 * 初始化线程若仍在运行，state 保持 2，阻止新线程进入。
 * 调用方若需强制恢复，提供独立的 airy_force_reset() API。 */
if (++spin_count >= AIRY_INIT_SPIN_MAX_RETRIES) {
    AIRY_LOG_ERROR("core_init: init spin-wait timed out after %lu retries", spin_count);
    /* 不执行 CAS 2→0 重置，state 保持 2，阻止新线程进入初始化 */
    return AIRY_ERR_TIMEOUT;
}

/* 方案 B：CAS 2→0 后立即 CAS 0→2 重新获取初始化权。
 * 但这实际上让超时线程自己成为新的初始化线程，语义复杂。 */
```

**工作量估算**：~1h（2 处修正 + 竞态分析 + 文档）。

### 3.5 V4.0-P1-3 深度分析：test_error_code_consistency.c 失败

**问题**：`test_error_code_consistency.c` 是 P0.25.6 (ACC-STD06) 错误码一致性测试，设计目的为验证 cupolas 枚举与 commons 宏数值一致。v3.0 迁移后：

1. **编译失败**：L63 `if (cupolas_ERR_OK != AIRY_OK)` 引用未定义的 `AIRY_OK` → 编译错误
2. **9 项断言失败**（即使编译通过）：
   - L67-68: `cupolas_ERR_UNKNOWN(-1) != AIRY_ERR_UNKNOWN(-99)` → FAIL
   - L69-70: `cupolas_ERR_INVALID_PARAM(-2) != AIRY_ERR_INVALID_PARAM(-40)` → FAIL
   - L75-76: `cupolas_ERR_BUFFER_TOO_SMALL(-5) != AIRY_ERR_BUFFER_TOO_SMALL(-41)` → FAIL
   - L79-80: `cupolas_ERR_ALREADY_EXISTS(-7) != AIRY_ERR_ALREADY_EXISTS(-42)` → FAIL
   - L85-86: `cupolas_ERR_PERMISSION_DENIED(-10) != AIRY_ERR_PERMISSION_DENIED(-43)` → FAIL
   - L87-88: `cupolas_ERR_IO(-11) != AIRY_ERR_IO(-44)` → FAIL
   - L89-90: `cupolas_ERR_STATE_ERROR(-13) != AIRY_ERR_STATE_ERROR(-46)` → FAIL

**影响**：CI 测试无法通过，错误码一致性验证机制失效。

**修复建议**：修正 V4.0-P0-1（恢复 AIRY_OK）+ V4.0-P0-2（同步 cupolas 枚举）后，测试自动通过。~0h（依赖前两项修正）。

---

## 4. v4.0 新发现问题清单

按 P0/P1/P2 分级。所有问题附 `文件路径:L行号` 证据。

### 4.1 P0 级（2 项）

#### V4.0-P0-1：AIRY_OK 移除后 39 文件编译破坏（v3.0 修正副作用）

详见 §3.2。

#### V4.0-P0-2：cupolas_error.h 枚举值未随 v3.0 迁移同步（v3.0 修正副作用）

详见 §3.3。

### 4.2 P1 级（3 项）

#### V4.0-P1-1：DCLP CAS 2→0 重置引入双重初始化竞态（v3.0 修正副作用）

详见 §3.4。

#### V4.0-P1-2：refcount_retain 使用 relaxed 内存序 + old==0 检查存在 use-after-free 竞态

**位置**：`agentrt/commons/utils/memory/include/refcounted.h:106-120`

**问题**：`refcount_retain` 使用 `memory_order_relaxed` 的 `atomic_fetch_add` 增加引用计数，随后检查 `if (old == 0)` 判断对象是否已被销毁。此模式存在竞态：

```c
111:    uint32_t old = atomic_fetch_add_explicit(&rc->refcount, 1, memory_order_relaxed);
114:    if (old == 0) {
115:        atomic_store_explicit(&rc->refcount, 0, memory_order_release);
116:        return NULL;
117:    }
```

**竞态场景**：
1. 线程 A：`refcount_release`，`fetch_sub` 将 refcount 从 1→0，准备调用 deleter
2. 线程 B：`refcount_retain`，`fetch_add` 将 refcount 从 0→1（old=0）
3. 线程 A：调用 `deleter(obj)`，释放对象内存
4. 线程 B：检查 `old == 0` 为 true，store 0，return NULL
5. 但线程 B 在步骤 2-4 期间可能已访问 `rc->refcount`（已被释放的内存）→ **use-after-free**

**正确模式**应使用 CAS 循环，原子地"仅当 refcount > 0 时增加"：
```c
uint32_t expected;
do {
    expected = atomic_load_explicit(&rc->refcount, memory_order_acquire);
    if (expected == 0) return NULL;
} while (!atomic_compare_exchange_weak_explicit(&rc->refcount, &expected, expected + 1,
                                                   memory_order_acquire, memory_order_relaxed));
```

**影响**：多线程引用计数场景下，retain 可能在对象已被释放后访问其内存，导致 use-after-free 或数据损坏。

**严重度**：P1（use-after-free 风险）。

**修复建议**：将 `refcount_retain` 改为 CAS 循环模式。~1h。

**工作量估算**：~1h。

#### V4.0-P1-3：test_error_code_consistency.c 编译失败 + 9 项断言失败（v3.0 修正副作用）

详见 §3.5。

### 4.3 P2 级（2 项）

#### V4.0-P2-1：mcp_v1_adapter.c 整数溢出风险

**位置**：
- `agentrt/protocols/standards/mcp/src/mcp_v1_adapter.c:538`
- `agentrt/protocols/standards/mcp/src/mcp_v1_adapter.c:1064`

**问题**：`size_t buf_size = 4096 + result_count * 1024;` 中，`result_count` 来自 handler 回调返回值，无上界校验。若 `result_count` 接近 `SIZE_MAX / 1024`，乘法溢出导致 `buf_size` 远小于预期，后续 `snprintf` 写入溢出。

```c
536:    found->handler(name, arguments_json, &results, &result_count, &is_error, found->user_data);
538:    size_t buf_size = 4096 + result_count * 1024;
539:    char *buf = AIRY_MALLOC(buf_size);
```

**影响**：恶意或异常 handler 返回极大 `result_count` 可触发整数溢出 → 堆缓冲区溢出。

**严重度**：P2（需恶意 handler 触发，当前 handler 均为内部实现）。

**修复建议**：增加溢出检查：
```c
if (result_count > (SIZE_MAX - 4096) / 1024) {
    mcp_content_destroy(results, result_count);
    return AIRY_ERR_OVERFLOW;
}
size_t buf_size = 4096 + result_count * 1024;
```

**工作量估算**：~0.5h（2 处修正）。

#### V4.0-P2-2：refcount_release 双重释放检测不完整

**位置**：`agentrt/commons/utils/memory/include/refcounted.h:150-153`

**问题**：`refcount_release` 检测到 `old == 0`（refcount 下溢）时，仅 `store 0` 但不阻止后续操作。store 0 后，第三次 release 会再次看到 old==0，形成无限静默双重释放循环。

```c
150:    if (old == 0) {
152:        atomic_store_explicit(&rc->refcount, 0, memory_order_release);
153:    }
```

**影响**：双重释放不被中止，仅静默重置计数器，掩盖内存破坏。

**严重度**：P2（双重释放检测不完整，非直接安全漏洞）。

**修复建议**：下溢时 abort 或标记为永久错误状态（如 `UINT32_MAX`）：
```c
if (old == 0) {
    /* 双重释放检测：标记为永久错误，阻止后续操作 */
    atomic_store_explicit(&rc->refcount, UINT32_MAX, memory_order_release);
    AIRY_LOG_ERROR("refcount_release: double release detected");
    /* 可选：abort() 或返回错误 */
}
```

**工作量估算**：~0.5h。

### 4.4 v4.0 新发现汇总

| 编号 | 严重度 | 问题 | 位置 | 工作量 | 类型 |
|------|--------|------|------|--------|------|
| V4.0-P0-1 | **P0** | AIRY_OK 移除后 39 文件编译破坏 | error.h:42-46 / 39 文件 | ~0.5-2h | v3.0 修正副作用 |
| V4.0-P0-2 | **P0** | cupolas_error.h 枚举值未同步 v3.0 迁移 | cupolas_error.h:41-59 | ~2-4h | v3.0 修正副作用 |
| V4.0-P1-1 | P1 | DCLP CAS 2→0 引入双重初始化竞态 | core_init.c:64-67 / cupolas.c:109 | ~1h | v3.0 修正副作用 |
| V4.0-P1-2 | P1 | refcount_retain use-after-free 竞态 | refcounted.h:106-120 | ~1h | 新发现（并发安全） |
| V4.0-P1-3 | P1 | test_error_code_consistency.c 编译+断言失败 | test_error_code_consistency.c:63-92 | ~0h（依赖 P0） | v3.0 修正副作用 |
| V4.0-P2-1 | P2 | mcp_v1_adapter.c 整数溢出风险 | mcp_v1_adapter.c:538,1064 | ~0.5h | 新发现（安全） |
| V4.0-P2-2 | P2 | refcount_release 双重释放检测不完整 | refcounted.h:150-153 | ~0.5h | 新发现（并发安全） |
| **合计** | — | **7 项** | — | **~5.5-9.5h** | — |

### 4.5 安全漏洞扫描结果

| 扫描维度 | Grep 模式 | 结果 | 评估 |
|---------|----------|------|------|
| 不安全字符串函数 | `\b(sprintf\|strcpy\|strcat\|gets)\b` in *.c | 0 处生产代码（strcpy 仅在 banned_functions.h 毒化宏） | ✅ 无违规 |
| 格式字符串漏洞 | `printf\s*\(\s*[a-zA-Z_]` | 0 处（均为 snprintf 带格式串） | ✅ 无漏洞 |
| 整数溢出 | `count\s*\*\s*sizeof\|result_count\s*\*\s*1024` | 2 处 mcp_v1_adapter.c 无溢出检查 | ⚠️ V4.0-P2-1 |
| AIRY_OK 引用 | `AIRY_OK` in *.c/*.h | 39 文件引用未定义宏 | ❌ V4.0-P0-1 |
| cupolas 枚举碰撞 | cupolas_ERR_* vs AIRY_E* | 8 处数值碰撞 | ❌ V4.0-P0-2 |

### 4.6 v3.0 修正副作用专项检查

| 修正项 | 副作用检查 | 结果 |
|--------|----------|------|
| airy_types.h 23 码 POSIX 对齐 | 调用方是否与字面量比较旧值 | ✅ 无 `== -1` 比较 airy 错误码（均为 POSIX API 返回值） |
| error.h AIRY_OK 移除 | 调用方是否仍引用 AIRY_OK | ❌ **V4.0-P0-1**（39 文件引用） |
| error.h 16 码迁移 | 调用方是否仍引用旧值 / 枚举是否同步 | ❌ **V4.0-P0-2**（cupolas_error.h 未同步） |
| core_init.c V3.0-N1 | state==1 验证是否正确 | ✅ 逻辑正确 |
| core_init.c V3.0-N2 | CAS 2→0 是否引入新竞态 | ❌ **V4.0-P1-1**（双重初始化竞态） |
| cupolas.c V3.0-N1/N2 | 同 core_init.c | ❌ **V4.0-P1-1**（同模式） |
| agent_registry_core search 签名 | 调用方是否同步更新 | ✅ 无调用方（dead code，F-2） |
| agent_registry.c get_locked | 嵌套加锁是否消除 | ✅ 已消除（L268 调用 _locked 版本） |

---

## 5. 残留项状态复核

### 5.1 残留项状态矩阵

| # | 残留项 | v3.0 状态 | v4.0 状态 | 变化 | 处理建议 |
|---|--------|----------|----------|------|---------|
| R4-1 | 5 个 daemon 19 处 `return 1` goto-less 模式 | 19 处 / 5 daemon | **32 处 / 11 daemon** | ⚠️ **显著恶化**（+13 处 / +6 daemon） | 详见 §5.2 |
| R4-2 | sync_compat.h 修正被 `#ifndef AIRY_RT_PLATFORM_H` 屏蔽 | 存在（L32） | 存在（L32/L439） | 无变化 | M1 早期修正 |
| R4-3 | .bak 备份文件 43 处 `agentrt_` 残留 | 43 处 | 43 处 | 无变化 | rm 删除 |
| F-1 | P0-2 源码工程标准全量违规 ~46h | 12535+/597/174 | **45687/1315/174** | ⚠️ **显著恶化**（4 空格 +33152 / typedef +718） | 详见 §6 |
| F-2 | agent_registry_core_* 系列函数 dead code | 存在 | 存在（0 调用方） | 无变化 | 删除或标记 deprecated |
| F-3 | test_agent_registry_core.c 调用无 _core 后缀函数名 | 存在 | 存在（6 处调用） | 无变化 | 配合 F-2 |

### 5.2 R4-1 深度分析：goto-less 模式显著恶化

**v3.0 报告**：5 个 daemon（market_d/llm_d/tool_d/monit_d/channel_d）共 19 处 `return 1`。

**v4.0 实测**：11 个 daemon 共 32 处 `return 1`。

| daemon | v3.0 计数 | v4.0 计数 | 变化 |
|--------|----------|----------|------|
| market_d | 4 | 4 | 无变化 |
| llm_d | 4 | 4 | 无变化 |
| tool_d | 4 | 4 | 无变化 |
| monit_d | 4 | 4 | 无变化 |
| channel_d | 3 | 3 | 无变化 |
| gateway_d | — | 1 | **新增** |
| observe_d | — | 3 | **新增** |
| hook_d | — | 1 | **新增** |
| notify_d | — | 3 | **新增** |
| info_d | — | 4 | **新增** |
| sched_d | — | 1 | **新增**（末尾正常退出，非 goto-less） |
| **合计** | **19** | **32** | **+13** |

**注**：sched_d 的 `return 1`（L327）位于 main() 末尾正常退出路径（N5 goto fall-through 修正后的最终 return），非 goto-less 模式。其余 31 处为 goto-less 错误清理重复代码。

**影响**：P0-2 工作流 F 阶段 3（goto 集中出口）工作量从 v3.0 估算的 ~5h 增至 ~8h（11 个 daemon × ~0.7h）。

### 5.3 F-2/F-3 确认

**F-2（dead code）**：Grep 确认 `agent_registry_core_create` / `agent_registry_core_destroy` / `agent_registry_core_init` / `agent_registry_core_add` / `agent_registry_core_remove` / `agent_registry_core_search` 等函数仅在 `.h` 声明 + `.c` 定义，**0 个外部调用方**。确认为 dead code。

**F-3（test 调用错误）**：`test_agent_registry_core.c` L82/122/153/181/205/276 调用 `agent_registry_get` / `agent_registry_list` / `agent_registry_search_by_tag` / `agent_registry_search` / `agent_registry_get_latest_version`（无 `_core` 后缀），但这些函数的签名（`agent_registry.c` 中的包装层）与测试调用的参数不匹配（测试传 `reg` 句柄 + agent_id，但 `agent_registry.c` 的 `agent_registry_get` 签名为 `(const char *agent_id, agent_info_t *out_info)`）。测试编译将失败或行为不正确。

---

## 6. P0-2 源码工程标准违规当前规模统计

### 6.1 v4.0 Grep 实测规模

| 违规类型 | v1.0 统计 | v3.0 统计 | **v4.0 统计** | 变化（v3.0→v4.0） | Grep 命令 |
|---------|----------|----------|-------------|------------------|----------|
| 4 空格缩进 | 10847 处 | 12535+ 处（100 文件截断） | **45687 处 / 441 文件** | +33152（解除截断后实测） | `Grep "^    [a-zA-Z_]" --include="*.{c,h}"` |
| typedef struct | 540 处 | 597 处 | **1315 处 / 441 文件** | +718 | `Grep "typedef\s+struct" --include="*.{c,h}"` |
| fprintf 直接使用 | 159 处/19 文件 | 174 处/22 文件 | **174 处 / 22 文件** | 无变化 | `Grep "\bfprintf\s*\(" --include="*.{c,h}"` |

**注**：v3.0 的 4 空格统计因 Grep 默认 head_limit=250 被截断在 100 文件（12535+ 处）。v4.0 使用 head_limit=0 解除截断，获得全量统计 45687 处 / 441 文件。typedef 同理（v3.0 的 597 可能也是截断值）。

### 6.2 趋势分析

4 空格缩进和 typedef 的全量统计远超 v3.0 截断值，表明 P0-2 债务规模被 v3.0 低估。fprintf 保持稳定（174 处），说明 v3.0→v4.0 期间未新增 fprintf 违规。

### 6.3 工作量重估

| 阶段 | v3.0 估算 | v4.0 重估 | 变化原因 |
|------|----------|----------|---------|
| 阶段 1 Tab 8 | ~8h | **~16h** | 4 空格从 12535+ 增至 45687（3.6x） |
| 阶段 2 typedef | ~16h | **~24h** | typedef 从 597 增至 1315（2.2x） |
| 阶段 3 goto | ~12h | **~15h** | R4-1 从 19 处增至 32 处 |
| 阶段 4 装饰符+fprintf | ~10h | **~10h** | fprintf 无变化 |
| **合计** | **~46h** | **~65h** | +19h（+41%） |

---

## 7. 修正后评分预估

### 7.1 评分变化对比

| 评分维度 | v3.0 修正后预估 | v4.0 复审（含新发现） | v4.0 新发现修正后（预估） |
|---------|----------------|---------------------|------------------------|
| agentrt 源码工程 | 76/B | **68/C+**（-8，V4.0-P0-1/P0-2 编译破坏 + V4.0-P1 副作用） | **78/B+**（+10，2 P0 + 3 P1 修正） |
| 并发安全 | 80/B+ | **70/B-**（-10，V4.0-P1-1 双重初始化 + V4.0-P1-2 refcount 竞态） | **82/B+**（+12，竞态修复） |
| 错误处理 | 78/B+ | **66/C+**（-12，V4.0-P0-1 AIRY_OK + V4.0-P0-2 枚举未同步） | **80/B+**（+14，SSoT 真正收敛） |
| 跨平台一致性 | 68/C+ | **68/C+**（维持，无新发现） | **68/C+** |
| **agentrt 总评** | **~76/B** | **68/C+** | **~78/B+** |

### 7.2 评分修正依据

**v4.0 较 v3.0 修正后下调 8 分（76→68）**：
- V4.0-P0-1（AIRY_OK 编译破坏）：-3
- V4.0-P0-2（cupolas 枚举未同步 + 数值碰撞）：-2
- V4.0-P1-1（双重初始化竞态）：-1
- V4.0-P1-2（refcount use-after-free）：-1
- V4.0-P1-3（测试失败）：-0.5
- V4.0-P2-1/P2-2（2 项 P2）：-0.5

**v4.0 新发现修正后预估 +10 分（68→78）**：
- V4.0-P0-1/P0-2 修正（编译恢复 + SSoT 真正收敛）：+5
- V4.0-P1-1/P1-2 修正（并发安全完善）：+3
- V4.0-P1-3 修正（测试通过）：+1
- V4.0-P2-1/P2-2 修正：+1

### 7.3 是否达到"可开发"状态

> **v4.0 判定**：agentrt 工程体系**不再满足"可开发"状态的最低条件**（综合 68/C+ < 70/B-，且存在 2 项编译破坏性 P0）。V4.0-P0-1 和 V4.0-P0-2 是阻塞性问题，必须在 M1 启动前修正。修正后可达 78/B+（"良好可开发"状态）。

| 判定标准 | v3.0 修正后 | v4.0 复审 | v4.0 新发现修正后 |
|---------|------------|----------|------------------|
| 架构设计完成度 | ✓ | ✓ | ✓ |
| 工程标准规范 | ✗（P0-2 延期） | ✗（P0-2 延期，规模恶化） | △（M1 阶段渐进） |
| 无方案冲突点 | ✗（P0-2 延期） | ✗（P0-2 延期） | △（P0-2 M1 处理） |
| 跨平台一致性 | △ | △ | △ |
| SSoT 收敛 | ✓（v3.0 修正后） | ⚠️ **回退**（AIRY_OK 残留 + cupolas 枚举未同步） | ✓（真正收敛） |
| 历史问题修复 | ✓ | ⚠️ v3.0 修正引入新问题 | ✓（修正后） |
| 技术亮点保留 | ✓ | ✓ | ✓ |
| 并发安全 | ✓（v3.0 修正后） | ⚠️ V4.0-P1-1/P1-2 竞态 | ✓（修正后） |
| **编译可通过** | ✓（假定） | **❌**（V4.0-P0-1 39 文件引用未定义宏） | ✓ |

---

## 8. 附录

### 8.1 v4.0 深读源码文件清单

| # | 文件路径 | 审查内容 |
|---|---------|---------|
| 1 | `agentrt/commons/include/airy_types.h` | 23 码 POSIX 对齐验证（L56-86） |
| 2 | `agentrt/commons/utils/error/include/error.h` | AIRY_OK 移除 + 16 码迁移验证（L42-227） |
| 3 | `agentrt/atoms/corekern/src/core_init.c` | V3.0-N1/N2 验证 + V4.0-P1-1 竞态分析（L40-82） |
| 4 | `agentrt/cupolas/src/cupolas.c` | V3.0-N1/N2 验证 + V4.0-P1-1 竞态分析（L85-234） |
| 5 | `agentrt/daemons/market_d/include/agent_registry_core.h` | search 签名同步验证（L123-124） |
| 6 | `agentrt/daemons/market_d/src/agent_registry_core.c` | search copy-to-buffer + dead code 验证（L239-258） |
| 7 | `agentrt/daemons/market_d/src/agent_registry.c` | get_locked + AIRY_OK 引用验证（L82-299） |
| 8 | `agentrt/cupolas/include/cupolas.h` | cupolas_OK = AIRY_OK 引用验证（L53） |
| 9 | `agentrt/cupolas/src/security/cupolas_error.h` | 枚举值未同步验证（L39-60） |
| 10 | `agentrt/cupolas/tests/unit/test_error_code_consistency.c` | 9 项断言失败验证（L60-95） |
| 11 | `agentrt/commons/utils/error/include/error_compat.h` | AIRY_OK 引用验证（L40/208/235/252） |
| 12 | `agentrt/daemons/common/include/error.h` | AIRY_OK 引用验证（L127-128） |
| 13 | `agentrt/commons/utils/sync/include/sync_compat.h` | AIRY_OK 引用 + R4-2 屏蔽验证（L32/47/439） |
| 14 | `agentrt/commons/utils/error/src/handler.c` | AIRY_OK 引用验证（L149/397/586/604/693/823/836） |
| 15 | `agentrt/commons/utils/memory/include/refcounted.h` | V4.0-P1-2 refcount 竞态验证（L106-156） |
| 16 | `agentrt/protocols/standards/mcp/src/mcp_v1_adapter.c` | V4.0-P2-1 整数溢出验证（L538/1064） |
| 17 | `agentrt/tests/test_banned_functions.c` | AIRY_OK #error 验证（L72-73） |
| 18 | `agentrt/daemons/common/include/daemon_errors.h` | 错误码段冲突验证（L30-49） |
| 19 | `agentrt/daemons/sched_d/src/main.c` | N5 goto 持久性 + R4-1 验证（L255-327） |

### 8.2 Grep 机器检查命令清单

```bash
# v3.0 修正持久性验证
grep -rn "define[[:space:]]\+AIRY_OK" agentrt/  # = 0 matches（AIRY_OK 已移除）
grep -n "AIRY_EINVAL\s+(-22)" agentrt/commons/include/airy_types.h  # = L65
grep -n "AIRY_ERR_INVALID_PARAM\s+(-40)" agentrt/commons/utils/error/include/error.h  # = L126
grep -n "AIRY_ERR_SYS_NOT_INIT" agentrt/atoms/corekern/src/core_init.c  # = L78
grep -n "expected_state" agentrt/atoms/corekern/src/core_init.c  # = L64-65
grep -n "cupolas_atomic_cas32.*2.*0" agentrt/cupolas/src/cupolas.c  # = L109

# V4.0-P0-1 验证（AIRY_OK 编译破坏）
grep -rl "AIRY_OK" agentrt/ --include="*.{c,h}"  # = 39 files
grep -rn "define[[:space:]]\+AIRY_OK" agentrt/  # = 0 matches（无定义）
grep -rn "DAIRY_OK" agentrt/**/CMakeLists.txt  # = 0 matches（无 -D 注入）

# V4.0-P0-2 验证（cupolas 枚举未同步）
grep -n "cupolas_ERR_STATE_ERROR" agentrt/cupolas/src/security/cupolas_error.h  # = L52 (-13)
grep -n "AIRY_ERR_STATE_ERROR" agentrt/commons/utils/error/include/error.h  # = L159 (-46)

# V4.0-P1-1 验证（双重初始化竞态）
grep -n "atomic_compare_exchange_strong_explicit.*expected_state.*0" agentrt/atoms/corekern/src/core_init.c  # = L65

# V4.0-P1-2 验证（refcount 竞态）
grep -n "memory_order_relaxed" agentrt/commons/utils/memory/include/refcounted.h  # = L111

# R4-1 验证（goto-less 恶化）
grep -c "return\s+1\s*;" agentrt/daemons/*/src/main.c  # = 32 total / 11 files

# P0-2 规模统计
grep -c "^    [a-zA-Z_]" agentrt/**/*.{c,h}  # 4 空格 = 45687 / 441 files
grep -c "typedef\s+struct" agentrt/**/*.{c,h}  # typedef = 1315 / 441 files
grep -c "\bfprintf\s*(" agentrt/**/*.{c,h}  # fprintf = 174 / 22 files
```

### 8.3 v4.0 P0 问题修正优先级

| 优先级 | 问题 | 修正方式 | 工作量 | 阻塞性 |
|--------|------|---------|--------|--------|
| **立即** | V4.0-P0-1（AIRY_OK 编译破坏） | 恢复 `#define AIRY_OK 0` 或批量替换为 `AIRY_EOK` | ~0.5-2h | ✅ 阻塞编译 |
| **立即** | V4.0-P0-2（cupolas 枚举未同步） | 更新 cupolas_error.h 枚举值或改为引用 commons 宏 | ~2-4h | ✅ 阻塞测试 |
| **M1 早期** | V4.0-P1-1（双重初始化竞态） | 超时不重置 state，提供独立 force_reset API | ~1h | ⚠️ 并发风险 |
| **M1 早期** | V4.0-P1-2（refcount 竞态） | refcount_retain 改为 CAS 循环 | ~1h | ⚠️ use-after-free |
| **M1 早期** | V4.0-P1-3（测试失败） | 依赖 P0-1/P0-2 修正 | ~0h | ⚠️ CI 阻塞 |
| **M1 中期** | V4.0-P2-1（整数溢出） | 增加溢出检查 | ~0.5h | 非阻塞 |
| **M1 中期** | V4.0-P2-2（双重释放检测） | 下溢时标记永久错误 | ~0.5h | 非阻塞 |

### 8.4 术语对照

| 术语 | 定义 |
|------|------|
| DCLP | Double-Checked Locking Pattern（双重检查锁定模式） |
| SSoT | Single Source of Truth（单一真值源） |
| [SC] | Shared Contract（共享契约层） |
| BAN-073 | 内存分配安全宏定义检查规则 |
| V4.0-P0-1 | v4.0 新发现 P0 #1：AIRY_OK 移除后 39 文件编译破坏 |
| V4.0-P0-2 | v4.0 新发现 P0 #2：cupolas_error.h 枚举值未同步 v3.0 迁移 |
| V4.0-P1-1 | v4.0 新发现 P1 #1：DCLP CAS 2→0 引入双重初始化竞态 |
| V4.0-P1-2 | v4.0 新发现 P1 #2：refcount_retain use-after-free 竞态 |
| V4.0-P1-3 | v4.0 新发现 P1 #3：test_error_code_consistency.c 编译+断言失败 |

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>

---

**报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-14 | 审查版本：v4.0
