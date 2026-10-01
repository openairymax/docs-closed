Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt 源码 v3.0 全面复审报告

> **文档定位**：agentrt 源码 v3.0 复审收敛文档。在 v2.0 系统性修正（7 项源码修正：P0-6/P0-7/N1/N2/N3/N5/N6）完成后，对 `agentrt/` 源码进行独立持久性复核 + 延期项验证 + 新发现问题扫描 + P0-2 分批方案评估，作为 1.0.1 M1 阶段源码工程治理的判定基线。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：3.0（2026-07-14）。
> **审查范围**：仅 `agentrt/` 源码（atoms 237 + daemons 243 + cupolas 95 + gateway 33 + commons 184 + protocols 41 = 833 源文件）。不审查 `agent-linux/`、`docs/`、`docs-closed/`。
> **审查方法**：v1.0/v2.0 历史报告深读 → Grep 机器检查独立复核 7 项源码修正持久性 → 6 项延期项逐项验证 → v3.0 新发现问题系统性扫描（并发/资源/错误/ABI/跨平台/工程标准/副作用/安全）→ P0-2 分批方案评估。
> **证据要求**：所有结论附 `文件路径:L行号` 或 Grep 命令与匹配数，可通过 Read/Grep 工具复核。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. v2.0 源码修正持久性验证矩阵（7 项）](#2-v20-源码修正持久性验证矩阵7-项)
- [3. v2.0 延期项验证与评估](#3-v20-延期项验证与评估)
- [4. v3.0 新发现问题清单](#4-v30-新发现问题清单)
- [5. P0-2 源码工程标准违规分批处理方案](#5-p0-2-源码工程标准违规分批处理方案)
- [6. 修正后综合评分变化](#6-修正后综合评分变化)
- [7. 附录：审查文件清单](#7-附录审查文件清单)

---

## 1. 执行摘要

### 1.1 审查范围与方法

| 维度 | 范围 | 方法 |
|------|------|------|
| v2.0 修正持久性 | 7 项源码修正（P0-6/P0-7/N1/N2/N3/N5/N6） | Grep 机器检查 + Read 源码逐行复核 |
| v2.0 延期项 | 6 项源码相关延期项（含 P0-2 分批） | Grep 统计 + Read 验证当前状态 |
| v3.0 新发现 | 并发/资源/错误/ABI/跨平台/工程标准/副作用/安全 8 维度 | 系统性 Grep 扫描 + 代表性文件深读 |
| P0-2 分批方案 | 4 阶段（Tab8/typedef/goto/fprintf+装饰符） | Grep 统计当前违规规模 + 工作量估算 |

### 1.2 核心结论

> **v2.0 源码修正 7/7 全部持久保留**：P0-6/P0-7/N1/N2/N3/N5/N6 经 Grep 独立复核，所有修正模式均在源码中就位，无回退。
>
> **v2.0 延期项 6/6 仍然存在**：P0-2 系统性违规规模较 v1.0 略有增长（4 空格 10847→12535+ / typedef 540→597 / fprintf 159→174），其余 5 项延期项均未处理。
>
> **v3.0 新发现 7 项问题**（4 项 P1 + 3 项 P2），其中 4 项为 **v2.0 修正引入的副作用或修正不完整**：
> - **V3.0-N1（P1）**：N1/N3 修正引入 DCLP 状态机缺陷——自旋等待线程在初始化线程失败后仍返回 SUCCESS（core_init.c:66 / cupolas.c:112）
> - **V3.0-N2（P1）**：N1/N3 修正引入 DCLP 状态卡死——超时后状态停留在 2，后续调用永久超时（core_init.c:62 / cupolas.c:109）
> - **V3.0-N3（P1）**：N5 修正不完整——相同 goto-less 模式存在于 5 个其他 daemon（market_d/llm_d/tool_d/monit_d/channel_d），共 19 处 `return 1` 重复清理
> - **V3.0-N4（P1）**：N6 修正不完整——sync_compat.h 修正仅在 platform.h 未包含时生效；生产代码普遍包含 platform.h（经 airy_rt.h），实际使用 platform.c 实现仍返回原始 POSIX errno，N6 修正对大多数调用方无效
>
> **综合评分**：v2.0 修正后源码工程 72/B- → v3.0（含新发现扣分）预估 **70/B-**（下调 2 分，反映 4 项修正副作用/不完整）。若 v3.0 新发现 4 项 P1 全部修正，预估可达 **76/B**。

### 1.3 1.0.1 M1 启动就绪判定

| 判定条件 | v2.0 验证报告状态 | v3.0 复审状态 | 变化 |
|---------|------------------|-------------|------|
| P0 阻断项清零 | ✅ 通过（9/10 修正，P0-2 延期） | ✅ 维持通过（P0-2 仍延期，无新 P0） | 无变化 |
| 综合评分 ≥ 70/B- | ✅ 通过（72/B-） | △ 边界（70/B-） | -2 分（v2.0 修正副作用） |
| 错误码 SSoT 收敛 | ✅ 通过（文档侧） | ⚠️ 源码侧 airy_types.h 仍用 -1/-2/-6（延期项 #6 未处理） | 部分回退 |
| [SC] 6 头文件清单一致 | ✅ 通过 | ✅ 维持通过（[SC] 6 头文件未修改，ABI 兼容） | 无变化 |
| IPC 消息头 SSoT 对齐 | ✅ 通过 | ✅ 维持通过 | 无变化 |
| 并发安全 | △ v2.0 修正后判定达标 | ⚠️ V3.0-N1/N2 揭示 DCLP 状态机缺陷 | 回退 |

> **v3.0 判定**：agentrt 模块仍满足 1.0.1 M1 代码开发启动的最低条件（无新 P0），但 **V3.0-N1/N2（DCLP 状态机缺陷）应在 M1 早期优先修正**，否则多线程初始化场景存在"假成功"风险。V3.0-N3/N4 可在 M1 阶段并行处理。

---

## 2. v2.0 源码修正持久性验证矩阵（7 项）

每项均通过 Grep 机器检查独立复核，记录匹配数与关键行号。

### 2.1 验证矩阵

| # | 修正项 | 验证方法 | 期望 | 实际 | 状态 |
|---|--------|---------|------|------|------|
| 1 | **P0-6 WebSocket 类型** | `Grep "s_ws_adapter\.type\s*=\s*PROTOCOL_(HTTP\|WEBSOCKET)" agentrt/protocols/` | 1 行 PROTOCOL_WEBSOCKET，0 行 PROTOCOL_HTTP | `protocols_impl.c:117: s_ws_adapter.type = PROTOCOL_WEBSOCKET;` | ✅ 持久 |
| 2 | **P0-7 agent_registry_core 4 函数签名** | `Grep "agent_registry_core_(get\|get_latest_version\|list\|search_by_tag)\s*\(" agent_registry_core.h` | 4 行，均含 `out`/`out_entries` 参数 | 4 行匹配（L71/82/98/110），均含 out 参数 | ✅ 持久 |
| 3 | **N1 core_init DCLP yield+timeout** | `Grep "AIRY_INIT_SPIN_MAX_RETRIES\|sched_yield\|Sleep(0)\|memory_order_acquire" core_init.c` | 存在 | 10 行匹配（L26/36/38/47/49/50/53/55/57/59） | ✅ 持久 |
| 4 | **N2 cupolas mutex destroy** | `Grep "cupolas_mutex_destroy" cupolas.c` | ≥4 处错误路径 | 4 处错误路径（L142/161/180/205）+ 1 处 cleanup（L261）= 5 处 | ✅ 持久 |
| 5 | **N3 cupolas DCLP CAS 状态机** | `Grep "g_cupolas_init_state\|CUPOLAS_INIT_SPIN_MAX_RETRIES\|cupolas_atomic_cas32" cupolas.c` | 存在 | 19 行匹配（L80/83/90/95/97/102/104/123/142/144/161/163/180/182/205/207/217/264） | ✅ 持久 |
| 6 | **N5 sched_d goto 集中出口** | `Grep "goto out_(mtx_sock\|service\|server_fd\|event_driver)\|^out_(mtx_sock\|service\|server_fd\|event_driver):" sched_d/main.c` | 4 goto + 4 label | 4 goto（L255/266/290/303）+ 4 label（L318/320/322/324）= 8 行 | ✅ 持久 |
| 7 | **N6 sync_compat airy_err_t** | `Grep "static inline airy_err_t airy_(mtx\|cond\|rwlock\|sem)_\|airy_sync_map_err" sync_compat.h` + `Grep "SYNC_SUCCESS\s*\?\s*0\s*:\s*-1" sync_compat.h` | 25 wrapper + 1 mapping，0 旧模式 | 25 wrapper + 1 mapping（51 行含调用），0 旧 `? 0 : -1` 残留 | ✅ 持久 |

**验证矩阵小结**：**7/7 项通过 Grep 机器检查**，所有 v2.0 源码修正均持久保留在源码中，无回退。

### 2.2 关键修正实现细节复核

#### P0-7 实现模式复核

Read `agent_registry_core.c:123-140`（`agent_registry_core_get`）确认采用锁内浅拷贝模式：

```c
123: int agent_registry_core_get(agent_registry_t *registry, const char *agent_id, agent_entry_t *out)
124: {
127:     airy_mtx_lock(&registry->lock);
129:     for (size_t i = 0; i < registry->entry_count; i++) {
130:         if (strcmp(registry->entries[i].id, agent_id) == 0) {
133:             *out = registry->entries[i];   /* 锁内浅拷贝 */
134:             airy_mtx_unlock(&registry->lock);
135:             return 0;
138:     airy_mtx_unlock(&registry->lock);
139:     return AIRY_ERR_NOT_FOUND;
```

4 个函数（get/get_latest_version/list/search_by_tag）均采用相同模式。注释明示"P0-7 修复：在锁内完成浅拷贝后再解锁"。

#### N1 实现模式复核

Read `core_init.c:26-67` 确认 DCLP 自旋等待改为 yield + 超时 + acquire：

```c
53: while (atomic_load_explicit(&g_core_initialized, memory_order_acquire) == 2) {
55:     Sleep(0);          /* Windows */
57:     sched_yield();     /* POSIX */
59:     if (++spin_count >= AIRY_INIT_SPIN_MAX_RETRIES) {
62:         return AIRY_ERR_TIMEOUT;
```

#### N3 实现模式复核

Read `cupolas.c:80-220` 确认 DCLP CAS 状态机（0/2/1 三态）+ 5 条错误路径状态重置 + cleanup 重置：

```c
80: static cupolas_atomic32_t g_cupolas_init_state = 0;
95: if (!cupolas_atomic_cas32(&g_cupolas_init_state, 0, 2)) { ... }
217: cupolas_atomic_store32(&g_cupolas_init_state, 1);   /* 成功发布 */
264: cupolas_atomic_store32(&g_cupolas_init_state, 0);   /* cleanup 重置 */
```

---

## 3. v2.0 延期项验证与评估

### 3.1 延期项验证矩阵

| # | 延期项 | v2.0 工作量 | v3.0 验证结果 | 0.1.1 可处理 | 修正建议 |
|---|--------|-----------|-------------|-------------|---------|
| 1 | P0-2 源码工程标准全量违规 | ~46h | **确认存在，规模增长**（4 空格 10847→12535+ / typedef 540→597 / fprintf 159→174 / 装饰符 100 文件） | 部分可（阶段 1 Tab8 + 阶段 4 装饰符/fprintf ~18h） | 详见 §5 |
| 2 | agent_registry_core_search 同模式数据竞争 | ~0.5h | **确认存在**（`agent_registry_core.c:239-254`，仍返回 `const agent_entry_t **out_entries` 指向内部 entries[]） | ✅ 可 | 改为 copy-to-buffer，参照 P0-7 修正模式 |
| 3 | agent_registry_core_* 系列函数为 dead code | ~2h | **确认存在**（Grep 确认 `agent_registry.c` 包装层 0 处调用 `_core` 函数） | ✅ 可 | 删除 `_core` 系列函数 + 头文件声明，或标记 `__attribute__((deprecated))` |
| 4 | test_agent_registry_core.c 调用无 _core 后缀函数名 | ~0.5h | **确认存在**（`test_agent_registry_core.c:82/122/153/181/205/276` 调用 `agent_registry_get`/`list`/`search_by_tag`/`search`/`get_latest_version`，非 `_core` 版本） | ✅ 可 | 修正测试调用为 `_core` 版本，或删除测试（若 `_core` 系列删除） |
| 5 | N4 .bak 备份文件 42 处 agentrt_* 残留 | ~0.1h | **确认存在，数量增至 43**（`triple_coordinator.c.bak`，v2.0 报告 42 处，v3.0 实测 43 处） | ✅ 可 | `rm` 删除（git history 已保留） |
| 6 | airy_types.h 错误码值与文档 SSoT 不一致 | ~4h | **确认存在**（`airy_types.h:50-55`：`AIRY_EINVAL=(-1)`/`AIRY_ENOMEM=(-2)`/`AIRY_ETIMEDOUT=(-6)`；文档 SSoT 要求 POSIX errno 负值 `-22/-12/-110`） | ⚠️ 需评估 | 详见 §3.2 |

### 3.2 延期项 #6 深度分析：错误码 SSoT 源码-文档不一致

**当前源码状态**（`agentrt/commons/include/airy_types.h:50-55`）：

```c
#define AIRY_EINVAL (-1)           /**< 参数无效 */
#define AIRY_ENOMEM (-2)           /**< 内存不足 */
#define AIRY_ETIMEDOUT (-6)        /**< 操作超时 */
```

**文档 SSoT 要求**（v2.0 修正后 `00-architectural-principles.md:937`）：

```
AIRY_EINVAL = (-22)    /* POSIX EINVAL 负值 */
AIRY_ENOMEM = (-12)    /* POSIX ENOMEM 负值 */
AIRY_ETIMEOUT = (-110) /* POSIX ETIMEDOUT 负值 */
```

**冲突分析**：

| 错误码 | 源码 airy_types.h | 文档 SSoT | error.h AIRY_ERR_* | sync_compat.h 映射 |
|--------|------------------|----------|--------------------|-------------------|
| EINVAL | -1 | -22 | AIRY_ERR_INVALID_PARAM = -2 | SYNC_ERROR_INVALID → -2 |
| ENOMEM | -2 | -12 | AIRY_ERR_OUT_OF_MEMORY = -4 | SYNC_ERROR_MEMORY → -4 |
| ETIMEDOUT | -6 | -110 | AIRY_ERR_TIMEOUT = -8 | SYNC_ERROR_TIMEOUT → -8 |

**三套错误码体系并存**：
1. `airy_types.h` POSIX 风格宏（AIRY_EINVAL=-1 等，非 POSIX errno 负值）
2. `error.h` 扩展错误码（AIRY_ERR_INVALID_PARAM=-2 等，自定义序列）
3. 文档 SSoT（POSIX errno 负值 -22/-12/-110）

**error.h 注释明示技术债**（`error.h:66-68`）：

> "已知技术债（计划 0.1.2 消除）：types.h POSIX 码（-1 到 -29）与本文件 AIRY_ERR_* 扩展码（-1 到 -19）在数值区间存在重叠（如 EINVAL=-1 与 ERR_UNKNOWN=-1）。调用方应始终使用语义宏，严禁与字面量直接比较。"

**v3.0 发现**：error.h 注释称"计划 0.1.2 消除"，但 v2.0 验证报告称"留待 1.0.1 M1 阶段对齐"。**路线图不一致**（0.1.2 vs 1.0.1 M1），需用户裁决实际目标版本。

**修正建议**：
- **方案 A（推荐）**：源码对齐文档 SSoT，将 `airy_types.h` 的 POSIX 风格宏改为 POSIX errno 负值（-22/-12/-110），同时调整 `error.h` 的 AIRY_ERR_* 扩展码消除数值重叠。工作量 ~8h（含调用方审查）。
- **方案 B**：文档对齐源码，将 SSoT 改为源码当前值（-1/-2/-6）。不推荐（违背 POSIX errno 对齐原则）。
- **0.1.1 内可处理**：部分可。若仅对齐 `airy_types.h` 的 3 个核心码（EINVAL/ENOMEM/ETIMEDOUT），~2h；全量对齐 30 个码，~8h。

### 3.3 延期项处理优先级建议

| 优先级 | 延期项 | 0.1.1 工作量 | 理由 |
|--------|--------|-------------|------|
| **立即**（M1 早期） | #2 agent_registry_core_search 数据竞争 | ~0.5h | 同 P0-7 模式，安全性问题 |
| **立即**（M1 早期） | #5 N4 .bak 文件删除 | ~0.1h | 零风险，消除审计污染 |
| **M1 早期** | #3 dead code 清理 | ~2h | 减少 P0-2 重构范围 |
| **M1 早期** | #4 test 调用修正 | ~0.5h | 配合 #3 |
| **M1 中期** | #6 错误码 SSoT 对齐 | ~2-8h | 需用户裁决方案 A/B 与目标版本 |
| **M1 全阶段** | #1 P0-2 分批处理 | ~18-46h | 详见 §5 |

---

## 4. v3.0 新发现问题清单

按 P0/P1/P2 分级。所有问题附 `文件路径:L行号` 证据。

### 4.1 P0 级（无新发现）

v3.0 未发现新的 P0 级问题。v2.0 修正的 7 项 P0/P1 均持久保留，未引入 P0 级副作用。

### 4.2 P1 级（4 项）

#### V3.0-N1：DCLP 自旋等待在初始化失败后返回 SUCCESS（v2.0 N1/N3 修正副作用）

**位置**：
- `agentrt/atoms/corekern/src/core_init.c:43-67`
- `agentrt/cupolas/src/cupolas.c:95-113`

**问题**：N1（core_init.c）和 N3（cupolas.c）修正引入的 DCLP 自旋等待存在状态机缺陷。当初始化线程失败并将状态重置为 0 时，自旋等待线程的循环退出（state != 2），但随后**直接返回 SUCCESS 而未验证 state == 1**。

**core_init.c 缺陷代码**（L43-67）：

```c
43: if (!atomic_compare_exchange_strong_explicit(&g_core_initialized, &expected, 2, ...)) {
45:     if (expected == 2) {
53:         while (atomic_load_explicit(&g_core_initialized, memory_order_acquire) == 2) {
59:             if (++spin_count >= AIRY_INIT_SPIN_MAX_RETRIES) {
62:                 return AIRY_ERR_TIMEOUT;
64:         }
66:     }
66:     return AIRY_SUCCESS;   /* ← BUG: state 可能是 0（初始化失败），但返回 SUCCESS */
67: }
```

**失败场景**：
1. 线程 A CAS 成功（state 0→2），开始初始化
2. 线程 B CAS 失败（expected=2），进入自旋等待
3. 线程 A 初始化失败（如 `airy_mem_init` 失败），跳转 `fail:` 标签，`atomic_store_explicit(&g_core_initialized, 0, ...)`（L155）
4. 线程 B 自旋循环退出（state=0 != 2）
5. 线程 B 执行 `return AIRY_SUCCESS`（L66）——**调用方认为初始化成功，实际未初始化**
6. 后续调用 `airy_loop_create()` 等依赖初始化的 API 将访问未初始化的子系统

**cupolas.c 同模式缺陷**（L95-113）：

```c
95: if (!cupolas_atomic_cas32(&g_cupolas_init_state, 0, 2)) {
102:     while (cupolas_atomic_load32(&g_cupolas_init_state) == 2) { ... }
112:     return CUPOLAS_OK;   /* ← BUG: state 可能是 0（初始化失败），但返回 CUPOLAS_OK */
```

**影响**：多线程并发初始化时，若初始化线程失败，等待线程将"假成功"返回，调用方在未初始化的运行时上操作，可能导致 NULL deref、数据损坏或安全穹顶失效。

**严重度**：P1（多线程并发初始化场景的"假成功"风险）。

**修复建议**：

```c
/* core_init.c L64 后 */
}
/* 自旋退出后必须验证 state == 1 */
if (atomic_load_explicit(&g_core_initialized, memory_order_acquire) != 1) {
    AIRY_LOG_ERROR("core_init: initialization failed by other thread (state=0)");
    return AIRY_ERR_NOTINIT;   /* 或 AIRY_ERR_UNKNOWN */
}
return AIRY_SUCCESS;
```

cupolas.c 同理，在 L112 前增加 `if (cupolas_atomic_load32(&g_cupolas_init_state) != 1) return cupolas_ERR_STATE_ERROR;`。

**工作量估算**：~1h（2 处修正 + 注释 + 测试场景设计）。

#### V3.0-N2：DCLP 自旋超时后状态卡死在 2（v2.0 N1/N3 修正副作用）

**位置**：
- `agentrt/atoms/corekern/src/core_init.c:59-63`
- `agentrt/cupolas/src/cupolas.c:104-110`

**问题**：N1/N3 修正增加的超时保护在触发时仅返回错误，**未重置状态**。状态停留在 2（initializing），后续所有 `airy_init()` / `cupolas_init()` 调用都将进入自旋等待并再次超时，运行时永久不可初始化。

**core_init.c 缺陷代码**（L59-63）：

```c
59:     if (++spin_count >= AIRY_INIT_SPIN_MAX_RETRIES) {
60:         AIRY_LOG_ERROR("core_init: init spin-wait timed out after %lu retries", spin_count);
62:         return AIRY_ERR_TIMEOUT;   /* ← BUG: state 仍为 2，未重置 */
63:     }
```

**cupolas.c 同模式缺陷**（L104-110）：

```c
104:     if (++spin_count >= CUPOLAS_INIT_SPIN_MAX_RETRIES) {
109:         return cupolas_ERR_STATE_ERROR;   /* ← BUG: state 仍为 2，未重置 */
110:     }
```

**影响**：若初始化线程长时间阻塞（如死锁、被信号暂停但未崩溃），等待线程超时后返回错误，但状态卡在 2。即使初始化线程后续恢复并完成初始化（state→1）或失败（state→0），超时期间的状态卡死已导致调用方收到错误。更严重的是，若初始化线程在超时后仍未完成，state 永久为 2，运行时永久不可用。

**严重度**：P1（运行时永久不可初始化风险）。

**修复建议**：

```c
/* core_init.c L59-63 修正 */
if (++spin_count >= AIRY_INIT_SPIN_MAX_RETRIES) {
    AIRY_LOG_ERROR("core_init: init spin-wait timed out after %lu retries", spin_count);
    /* V3.0-N2 修复：超时后尝试重置状态 2→0，允许后续重试。
     * 注意：仅当当前 state 仍为 2 时才重置，避免覆盖初始化线程的完成/失败发布。 */
    long expected_state = 2;
    atomic_compare_exchange_strong_explicit(&g_core_initialized, &expected_state, 0,
                                            memory_order_seq_cst, memory_order_seq_cst);
    return AIRY_ERR_TIMEOUT;
}
```

cupolas.c 同理，在 L109 前增加 CAS 2→0 重置。

**工作量估算**：~0.5h（2 处修正 + CAS 竞争分析）。

#### V3.0-N3：N5 修正不完整——5 个其他 daemon 存在相同 goto-less 模式

**位置**：
- `agentrt/daemons/market_d/src/main.c:341-399`（4 处 `return 1`）
- `agentrt/daemons/llm_d/src/main.c:500-563`（4 处 `return 1`）
- `agentrt/daemons/tool_d/src/main.c:377-435`（4 处 `return 1`）
- `agentrt/daemons/monit_d/src/main.c:430-504`（4 处 `return 1`）
- `agentrt/daemons/channel_d/src/main.c:312-330`（3 处 `return 1`）

**问题**：v2.0 N5 修正仅修复了 `sched_d/src/main.c` 的 4 处重复错误清理块（改为 goto fall-through），但相同的 goto-less 模式存在于至少 5 个其他 daemon，共 **19 处 `return 1`** 重复清理代码。

**market_d/src/main.c 示例**（L341-399）：

```c
341: if (ret != AIRY_SUCCESS || !g_service) {
343:     airy_mtx_destroy(&g_running_lock_market_d);
344:     airy_sock_cleanup();
345:     return 1;          /* ← 重复清理块 #1 */
349: if (register_rpc_methods() != 0) {
351:     destroy_service();
352:     airy_mtx_destroy(&g_running_lock_market_d);
353:     airy_sock_cleanup();
354:     return 1;          /* ← 重复清理块 #2 */
362: if (server_fd < 0) {
364:     method_dispatcher_destroy(g_dispatcher_market_d);
365:     destroy_service();
366:     airy_mtx_destroy(&g_running_lock_market_d);
367:     airy_sock_cleanup();
368:     return 1;          /* ← 重复清理块 #3 */
389: if (!pool) {
391:     daemon_bootstrap_ipc_stop(g_bipc_market_d);
392:     daemon_bootstrap_sd_stop(g_bsd_market_d);
393:     airy_sock_close(server_fd);
394:     method_dispatcher_destroy(g_dispatcher_market_d);
395:     destroy_service();
396:     airy_mtx_destroy(&g_running_lock_market_d);
397:     airy_sock_cleanup();
398:     return 1;          /* ← 重复清理块 #4 */
```

**影响**：与 v2.0 N5 相同——违反 OS-KER-001 goto 集中出口要求，维护时极易遗漏新增资源的清理。market_d 的 L391-397 清理 7 项资源，新增资源时遗漏风险高。

**严重度**：P1（维护性风险，与 v2.0 N5 同级）。

**修复建议**：参照 sched_d 的 goto fall-through 模式，逐个 daemon 改造。每个 daemon ~1h，5 个 daemon 合计 ~5h。

**工作量估算**：~5h（5 个 daemon 各 ~1h）。

#### V3.0-N4：N6 修正不完整——sync_compat.h 修正被 platform.h 屏蔽

**位置**：
- `agentrt/commons/utils/sync/include/sync_compat.h:32`（`#ifndef AIRY_RT_PLATFORM_H` 条件编译）
- `agentrt/commons/platform/include/platform.h:220-280`（platform.h 自有 `airy_mtx_*` 声明）
- `agentrt/commons/platform/platform.c:194-331`（platform.c 自有 `airy_mtx_*` 实现）

**问题**：N6 修正将 `sync_compat.h` 的 25 个同步原语函数返回类型从 `int`（0/-1）改为 `airy_err_t`（完整错误码映射）。但该修正被 `#ifndef AIRY_RT_PLATFORM_H` 条件编译块（L32）包裹——**当 `platform.h` 已包含时（生产代码的常见情况），`sync_compat.h` 的修正定义被完全跳过**，实际使用的是 `platform.c` 的实现。

**platform.c 的 `airy_mtx_init` 实现**（L194-202）：

```c
194: int airy_mtx_init(airy_mtx_t *mutex)
195: {
196:     pthread_mutexattr_t attr;
197:     pthread_mutexattr_init(&attr);
198:     pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE);
199:     int ret = pthread_mutex_init(mutex, &attr);
200:     pthread_mutexattr_destroy(&attr);
201:     return ret;   /* ← 返回原始 POSIX errno（正值：EINVAL=22/EBUSY=16/...），未映射到 airy_err_t */
202: }
```

**platform.c 的 `airy_cond_timedwait` 实现**（L316-331）：

```c
316: int airy_cond_timedwait(airy_cond_t *cond, airy_mtx_t *mutex, uint32_t timeout_ms)
327:     int ret = pthread_cond_timedwait(cond, mutex, &ts);
328:     if (ret == ETIMEDOUT) {
329:         return AIRY_ERR_TIMEOUT;   /* ← 超时返回 -8（airy_err_t） */
331:     return ret;                    /* ← 其他返回原始 POSIX errno（正值），语义不一致 */
```

**三套返回值语义并存**：

| 调用路径 | 返回值语义 | 示例 |
|---------|----------|------|
| sync_compat.h（platform.h 未包含） | airy_err_t（0/负值，N6 修正后） | AIRY_ERR_TIMEOUT=-8 |
| platform.c（platform.h 已包含，常见） | 原始 POSIX errno（0/正值） | ETIMEDOUT=110 |
| platform.c airy_cond_timedwait（混合） | 超时=airy_err_t，其他=POSIX errno | -8 或 22 |

**验证**：Grep 确认生产代码（如 `taskflow_core.c:769`、`pregel_engine.c:1069`、`ipc_common.c:1637`、`engine.c:892`）均通过 `airy_rt.h` → `platform.h` 路径调用，使用 platform.c 实现，**N6 修正对这些调用方完全无效**。

**调用方安全性分析**：Grep 确认所有调用方使用 `!= 0` / `== 0` 检查返回值（如 `taskflow_core.c:770` `if (ret != 0)`、`engine.c:893` `if (err != 0)`），无 `== -1` 精确比较。因此 N6 修正不完整**未破坏现有调用方**，但 N6 修正的目标（错误码透明化）对大多数调用方未达成。

**影响**：N6 修正的实际效果局限于不包含 platform.h 的少数场景（如某些测试文件）。生产代码仍无法区分 EINVAL/EBUSY/EDEADLK 等具体失败原因。

**严重度**：P1（N6 修正目标未达成，错误处理精度问题）。

**修复建议**：
- **方案 A（推荐）**：将 N6 修正的 `airy_sync_map_err` 映射逻辑移植到 `platform.c` 的 25 个同步原语实现中，使 platform.c 也返回 airy_err_t。
- **方案 B**：统一 `sync_compat.h` 与 `platform.h` 的接口，消除 `#ifndef AIRY_RT_PLATFORM_H` 条件编译分裂。
- 注意：方案 A 需审查所有调用方是否依赖 POSIX errno 正值语义（Grep 确认当前无此类依赖）。

**工作量估算**：~3h（platform.c 25 个函数修正 + 调用方审查）。

### 4.3 P2 级（3 项）

#### V3.0-P2-1：agent_registry_search 嵌套加锁（依赖递归互斥锁）

**位置**：`agentrt/daemons/market_d/src/agent_registry.c:204-243`

**问题**：`agent_registry_search()` 在持有 `g_registry.lock`（L204）的情况下，于 L235 调用 `agent_registry_get()`，而后者在 L167 再次尝试获取同一 `g_registry.lock`。这构成嵌套加锁。

```c
204: airy_mtx_lock(&g_registry.lock);
...
235:     agent_registry_get(entry->info.agent_id, (*results)[result_idx]);  /* ← 内部再次 lock g_registry.lock */
```

**当前可工作的原因**：`platform.c:198` 将互斥锁类型设为 `PTHREAD_MUTEX_RECURSIVE`，允许同一线程多次获取。

**风险**：
1. 性能开销：每次 `agent_registry_get` 调用额外一次 lock/unlock + safe_strdup 深拷贝
2. 脆弱性：依赖递归互斥锁属性，若未来改为非递归锁将立即死锁
3. 可读性差：嵌套加锁通过函数调用隐式发生，代码审查难以发现

**严重度**：P2（性能 + 脆弱性，非功能 bug）。

**修复建议**：将 `agent_registry_get` 的深拷贝逻辑抽取为 `agent_registry_get_locked()`（不加锁版本），`agent_registry_search` 在持锁状态下调用 `agent_registry_get_locked`，避免嵌套加锁。~1h。

#### V3.0-P2-2：error.h 路线图注释与验证报告不一致

**位置**：`agentrt/commons/utils/error/include/error.h:66`

**问题**：error.h L66 注释称"已知技术债（计划 **0.1.2** 消除）"，但 v2.0 验证报告 §9.1 延期项 #6 称"留待 **1.0.1 M1** 阶段对齐"。目标版本不一致。

**严重度**：P2（文档一致性）。

**修复建议**：统一路线图。建议 1.0.1 M1 阶段对齐（与 v2.0 验证报告一致），修正 error.h 注释。~0.1h。

#### V3.0-P2-3：.bak 文件 agentrt_ 残留数量增长（42→43）

**位置**：`agentrt/atoms/coreloopthree/src/cognition/critique/triple_coordinator.c.bak`

**问题**：v2.0 报告称 42 处 `agentrt_` 残留，v3.0 实测 **43 处**（Grep count 模式确认）。数量增长 1 处，可能是 v2.0 计数遗漏或后续编辑新增。

**严重度**：P2（审计准确性，不影响功能）。

**修复建议**：直接 `rm` 删除 .bak 文件（延期项 #5），消除审计污染。~0.1h。

### 4.4 v3.0 新发现汇总

| 编号 | 严重度 | 问题 | 位置 | 工作量 | 类型 |
|------|--------|------|------|--------|------|
| V3.0-N1 | P1 | DCLP 自旋等待失败后返回 SUCCESS | core_init.c:66 / cupolas.c:112 | ~1h | v2.0 修正副作用 |
| V3.0-N2 | P1 | DCLP 自旋超时后状态卡死在 2 | core_init.c:62 / cupolas.c:109 | ~0.5h | v2.0 修正副作用 |
| V3.0-N3 | P1 | N5 修正不完整，5 个 daemon 同模式 | market_d/llm_d/tool_d/monit_d/channel_d main.c | ~5h | v2.0 修正不完整 |
| V3.0-N4 | P1 | N6 修正被 platform.h 屏蔽 | sync_compat.h:32 / platform.c:194-331 | ~3h | v2.0 修正不完整 |
| V3.0-P2-1 | P2 | agent_registry_search 嵌套加锁 | agent_registry.c:235 | ~1h | 新发现 |
| V3.0-P2-2 | P2 | error.h 路线图注释不一致 | error.h:66 | ~0.1h | 新发现 |
| V3.0-P2-3 | P2 | .bak 文件残留 42→43 | triple_coordinator.c.bak | ~0.1h | 已知延期项恶化 |
| **合计** | — | **7 项** | — | **~10.8h** | — |

### 4.5 安全漏洞扫描结果（无新发现）

| 扫描维度 | Grep 模式 | 结果 | 评估 |
|---------|----------|------|------|
| 不安全字符串函数 | `\b(sprintf\|strcpy\|strcat\|gets)\b` in *.c | 4 行匹配（均在 `test_banned_functions.c` 注释/测试） | ✅ 无生产代码违规 |
| 格式字符串漏洞 | `fprintf\s*\(\s*(stderr\|stdout)\s*,\s*[a-zA-Z_]` | 0 匹配 | ✅ 无格式字符串漏洞 |
| printf 非字面量格式 | `printf\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)` | 1 行匹配（`test_safe_string_utils.c:66` 函数名 `test_safe_sprintf`） | ✅ 无漏洞 |
| [SC] 6 头文件 ABI | Read 6 个 [SC] 头文件确认 struct 无 typedef + Tab 8 + kernel-doc | 全部合规（文件日期 Jul 12，v2.0 修正 Jul 13 未修改） | ✅ ABI 兼容性维持 |

### 4.6 v2.0 修正副作用专项检查

| 修正项 | 副作用检查 | 结果 |
|--------|----------|------|
| P0-6 | WebSocket 适配器其他字段（init/send/recv/close）是否受影响 | ✅ 未受影响，仅 type 字段修改 |
| P0-7 | 调用方是否破坏（_core 系列为 dead code，无活跃调用方） | ✅ 无破坏 |
| N1 | DCLP 状态机正确性 | ⚠️ **V3.0-N1/N2 副作用**（假成功 + 状态卡死） |
| N2 | 4 处 mutex destroy 是否完整 | ✅ 完整（L142/161/180/205 + cleanup L261） |
| N3 | DCLP CAS 状态机正确性 | ⚠️ **V3.0-N1/N2 副作用**（同 N1） |
| N5 | goto fall-through 资源释放顺序正确性 | ✅ 正确（分配逆序，未初始化变量不访问） |
| N6 | 调用方是否破坏（`== -1` 精确比较） | ✅ 无破坏（所有调用方用 `!= 0`）；但 **V3.0-N4 修正不完整** |

---

## 5. P0-2 源码工程标准违规分批处理方案

### 5.1 当前违规规模统计（v3.0 Grep 实测）

| 违规类型 | v1.0 统计 | v3.0 统计 | 变化 | Grep 命令 |
|---------|----------|----------|------|----------|
| 4 空格缩进 | 10847 处 | **12535+ 处**（100 文件截断） | +1688 | `Grep "^    [a-zA-Z_]" --include="*.{c,h}"` |
| Tab 8 缩进（合规标杆） | — | 111 处/7 文件（[SC] 6 头文件 + 1 测试） | — | `Grep "^\t" --include="*.{c,h}"` |
| typedef struct | 540 处 | **597 处**/100+ 文件 | +57 | `Grep "typedef\s+struct" --include="*.{c,h}"` |
| ASCII 装饰分节符 | 100 文件 | **354 处**/100 文件 | — | `Grep "/\* =+ [^=]+ =+ \*/\|// =+[^=]+=+" --include="*.{c,h}"` |
| fprintf 直接使用 | 159 处/19 文件 | **174 处**/22 文件 | +15/+3 | `Grep "\bfprintf\s*\(" --include="*.{c,h}"` |

**趋势分析**：4 项违规指标均较 v1.0 增长（4 空格 +1688 / typedef +57 / fprintf +15），表明 v1.0→v2.0→v3.0 期间新增代码未遵循 OLK-6.6 标准，P0-2 债务持续累积。

### 5.2 4 阶段分批处理方案

#### 阶段 1：Tab 8 自动化（~8h，M1 早期可完成）

**目标**：将 4 空格缩进批量转换为 Tab 8，对齐 [SC] 6 头文件标杆。

**执行步骤**：
1. 配置 `.clang-format`（`IndentWidth: 8` / `TabWidth: 8` / `UseTab: Always` / `ColumnLimit: 80`）
2. 添加 `make format` 目标 + CI 门禁（`git diff --check` + clang-format --dry-run）
3. 分模块执行 `clang-format -i`：
   - M1 周 1：commons/（184 文件）+ atoms/corekern/（~30 文件）
   - M1 周 2：atoms/coreloopthree/ + atoms/taskflow/ + atoms/syscall/
   - M1 周 3：daemons/（243 文件）+ cupolas/（95 文件）
   - M1 周 4：gateway/（33 文件）+ protocols/（41 文件）
4. 每个 PR 限制 ≤50 文件，便于 review

**风险**：clang-format 可能改变代码语义（如宏定义续行、字符串字面量缩进）。需逐 PR review + 全量测试。

**M1 出口标准**：4 空格缩进从 12535+ 降至 <500（仅保留宏续行等合法场景）。

#### 阶段 2：typedef 重构（~16h，M1 中期）

**目标**：将 597 处 `typedef struct { ... } xxx_t;` 重构为 `struct xxx { ... };`（仅保留不透明指针 typedef）。

**执行步骤**：
1. 识别可安全重构的 typedef（非不透明指针、非 [SC] 头文件）
2. 分模块重构：
   - 头文件优先（.h），随后更新 .c 调用方
   - 每个 PR 限制 ≤20 处 typedef 重构
3. 对不透明指针 typedef（如 `airy_sandbox_t`/`airy_mempool_t`）保留，仅文档化

**风险**：API breakage（若 typedef 在公共头文件中使用）。需审查每个 typedef 的可见性。

**M1 出口标准**：typedef struct 从 597 降至 <200（保留不透明指针 + [SC] 兼容）。

#### 阶段 3：goto 集中出口（~12h，M1 中后期）

**目标**：将多资源函数的早返回改为 `goto out_xxx:` fall-through 集中出口，对齐 OS-KER-001。

**执行步骤**：
1. 优先处理 V3.0-N3 的 5 个 daemon main.c（~5h，已识别）
2. 扫描其他多资源函数（`cupolas_init` 已在 N2/N3 修正中处理；`permission_engine_create` 等）
3. 每个 PR 限制 ≤5 个函数重构

**风险**：goto 跳转可能跳过变量初始化（C 语言要求 goto 不能跳过 VLAT 变量声明）。需逐函数审查。

**M1 出口标准**：V3.0-N3 的 5 个 daemon 全部修正；全仓库 goto 标签从 v1.0 的 14 处增至 ≥50 处。

#### 阶段 4：装饰分节符 + fprintf 收口（~10h，M1 后期）

**目标**：移除 354 处 ASCII 装饰分节符，将 174 处 fprintf 收口到 `log_write` 或标注 BAN-70 EXEMPT。

**执行步骤**：
1. 装饰分节符：自动化脚本替换 `/* === xxx === */` → `/* xxx */`，`// === xxx ===` → `/* xxx */`
2. fprintf 收口：
   - test 文件：标注 BAN-70 EXEMPT（允许）
   - 非 test 文件：改用 `log_write(LOG_LEVEL_X, ...)` 或 `AIRY_LOG_X(...)`
   - logging.c 内部：已标注 EXEMPT，保留

**风险**：fprintf 改为 log_write 可能改变输出格式/目标。需逐处审查。

**M1 出口标准**：装饰分节符从 354 降至 <50；fprintf 从 174 降至 <60（仅 test + logging.c EXEMPT）。

### 5.3 0.1.1 内可完成的部分

| 阶段 | 工作量 | 0.1.1 可完成 | 说明 |
|------|--------|-------------|------|
| 阶段 1 Tab 8 | ~8h | ✅ 可 | 自动化为主，CI 门禁后渐进 |
| 阶段 2 typedef | ~16h | ⚠️ 部分（~50%） | 需逐模块审查，M1 可完成 commons + atoms |
| 阶段 3 goto | ~12h | ✅ 可（V3.0-N3 5h + 其他 7h） | V3.0-N3 优先 |
| 阶段 4 装饰符+fprintf | ~10h | ✅ 可 | 机械替换为主 |
| **合计** | **~46h** | **~30-35h 可在 0.1.1 完成** | 阶段 2 部分延期至 1.0.2 |

### 5.4 M1 出口条件

| # | 出口标准 | 量化指标 | 验证方法 |
|---|---------|---------|---------|
| 1 | .clang-format 配置 + CI 门禁 | 配置文件存在 + CI 检查脚本存在 | 文件检查 |
| 2 | Tab 8 缩进达标 | 4 空格缩进 <500 处（从 12535+ 降 96%） | `Grep "^    [a-zA-Z_]"` |
| 3 | typedef 削减 | typedef struct <200 处（从 597 降 66%） | `Grep "typedef\s+struct"` |
| 4 | goto 集中出口 | V3.0-N3 的 5 daemon 全部修正 + 全仓库 goto 标签 ≥50 | `Grep "goto out_"` |
| 5 | 装饰分节符削除 | <50 处（从 354 降 86%） | `Grep "/\* =+ [^=]+ =+ \*/"` |
| 6 | fprintf 收口 | <60 处（从 174 降 66%，仅 test + EXEMPT） | `Grep "\bfprintf\s*\("` |
| 7 | [SC] 6 头文件保持合规 | Tab 8 + struct 无 typedef + kernel-doc + _Static_assert | Read 6 头文件 |
| 8 | V3.0 新发现 P1 修正 | V3.0-N1/N2/N3/N4 全部修正 | Grep 验证 |

---

## 6. 修正后综合评分变化

### 6.1 评分变化对比

| 评分维度 | v2.0 修正前 | v2.0 修正后 | v3.0 复审（含新发现） | v3.0 新发现修正后（预估） |
|---------|------------|------------|---------------------|------------------------|
| agentrt 源码工程 | 66/C+ | 72/B- | **70/B-**（-2，V3.0-N1/N2/N3/N4 副作用） | **76/B**（+6，4 项 P1 修正） |
| 并发安全 | — | 78/B+（N1/N2/N3 修正） | **68/C+**（-10，V3.0-N1/N2 DCLP 缺陷） | **80/B+**（+12，DCLP 状态机完善） |
| 错误处理 | — | 75/B-（N6 修正） | **70/B-**（-5，V3.0-N4 N6 不完整） | **78/B+**（+8，platform.c 对齐） |
| 跨平台一致性 | 54/D+ | 68/C+ | **68/C+**（维持，无新发现） | **68/C+** |
| **agentrt 总评** | **63/C+** | **72/B-** | **70/B-** | **76/B** |

### 6.2 评分修正依据

**v3.0 较 v2.0 修正后下调 2 分（72→70）**：
- V3.0-N1（DCLP 假成功）：-1
- V3.0-N2（DCLP 状态卡死）：-0.5
- V3.0-N3（N5 不完整 5 daemon）：-0.5
- V3.0-N4（N6 不完整被屏蔽）：-0.5
- V3.0-P2-1/2/3（3 项 P2）：-0.5
- 抵消：v2.0 修正 7/7 持久保留 +0（已计入 v2.0 修正后评分）

**v3.0 新发现修正后预估 +6 分（70→76）**：
- V3.0-N1/N2 修正（DCLP 状态机完善）：+2
- V3.0-N3 修正（5 daemon goto）：+1.5
- V3.0-N4 修正（platform.c 对齐）：+1.5
- V3.0-P2-1/2/3 修正：+1

### 6.3 是否达到"可开发"状态

> **v3.0 判定**：agentrt 工程体系**仍维持"可开发"状态的最低条件**（综合 70/B-，无新 P0），但 **V3.0-N1/N2（DCLP 状态机缺陷）是并发安全的真实风险**，应在 M1 早期优先修正。修正后可达 76/B（"良好可开发"状态）。

| 判定标准 | v2.0 修正后 | v3.0 复审 | v3.0 新发现修正后 |
|---------|------------|----------|------------------|
| 架构设计完成度 | ✓ | ✓ | ✓ |
| 工程标准规范 | ✗（P0-2 延期） | ✗（P0-2 延期，规模增长） | △（M1 阶段渐进） |
| 无方案冲突点 | ✗（P0-2 延期） | ✗（P0-2 延期） | △（P0-2 M1 处理） |
| 跨平台一致性 | △ | △ | △ |
| SSoT 收敛 | △（源码错误码延期） | △（延期项 #6 未处理） | ✓（源码对齐） |
| 历史问题修复 | ✓ | ✓ | ✓ |
| 技术亮点保留 | ✓ | ✓ | ✓ |
| 并发安全 | ✓（v2.0 修正后） | ⚠️（V3.0-N1/N2 缺陷） | ✓（修正后） |

---

## 7. 附录：审查文件清单

### 7.1 历史报告（必读）

| 报告 | 路径 | 版本 |
|------|------|------|
| v1.0 综合分析 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v1.0/00-comprehensive-analysis.md` | 1.0（2026-07-13） |
| v2.0 工程规范审查 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v2.0/01-engineering-code-review-v2.md` | 2.0（2026-07-13） |
| v2.0 源码修正日志 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v2.0/fix-log-source-code.md` | 1.0（2026-07-13） |
| v2.0 修正验证报告 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v2.0/fix-verification-report.md` | 1.0（2026-07-13） |

### 7.2 v3.0 深读源码文件清单

| # | 文件路径 | 审查内容 |
|---|---------|---------|
| 1 | `agentrt/protocols/common/src/protocols_impl.c` | P0-6 WebSocket 类型验证（L117） |
| 2 | `agentrt/daemons/market_d/include/agent_registry_core.h` | P0-7 4 函数签名验证（L60-119） |
| 3 | `agentrt/daemons/market_d/src/agent_registry_core.c` | P0-7 实现模式 + agent_registry_core_search 数据竞争（L100-254） |
| 4 | `agentrt/daemons/market_d/src/agent_registry.c` | 包装层 + 嵌套加锁（L100-267） |
| 5 | `agentrt/daemons/market_d/tests/test_agent_registry_core.c` | 测试调用无 _core 后缀（L82/122/153/181/205/276） |
| 6 | `agentrt/atoms/corekern/src/core_init.c` | N1 DCLP 验证 + V3.0-N1/N2 副作用（L1-194） |
| 7 | `agentrt/cupolas/src/cupolas.c` | N2/N3 验证 + V3.0-N1/N2 副作用（L70-265） |
| 8 | `agentrt/daemons/sched_d/src/main.c` | N5 goto 验证（L245-328） |
| 9 | `agentrt/daemons/market_d/src/main.c` | V3.0-N3 goto-less 模式（L335-404） |
| 10 | `agentrt/daemons/llm_d/src/main.c` | V3.0-N3 goto-less 模式（L495-569） |
| 11 | `agentrt/commons/utils/sync/include/sync_compat.h` | N6 验证 + V3.0-N4 屏蔽分析（L1-309） |
| 12 | `agentrt/commons/platform/include/platform.h` | V3.0-N4 platform.h 声明（L220-280） |
| 13 | `agentrt/commons/platform/platform.c` | V3.0-N4 platform.c 实现（L194-331） |
| 14 | `agentrt/commons/include/airy_types.h` | 延期项 #6 错误码值（L35-79） |
| 15 | `agentrt/commons/utils/error/include/error.h` | 延期项 #6 + V3.0-P2-2 路线图注释（L1-80） |
| 16 | `agentrt/commons/include/airymax/ipc.h` | [SC] ABI 兼容性验证（全文） |
| 17 | `agentrt/atoms/coreloopthree/src/cognition/critique/triple_coordinator.c.bak` | 延期项 #5 .bak 残留（43 处） |
| 18 | `agentrt/atoms/taskflow/src/taskflow_core.c` | N6 调用方语义验证（L765-779） |
| 19 | `agentrt/atoms/taskflow/src/pregel_engine.c` | N6 调用方语义验证（L1065-1075） |
| 20 | `agentrt/commons/utils/ipc/src/ipc_common.c` | N6 调用方语义验证（L1633-1646） |
| 21 | `agentrt/atoms/coreloopthree/src/execution/engine.c` | N6 调用方语义验证（L888-900） |
| 22 | `agentrt/daemons/tool_d/src/main.c` | V3.0-N3 goto-less 模式（L377-435） |
| 23 | `agentrt/daemons/monit_d/src/main.c` | V3.0-N3 goto-less 模式（L430-504） |

### 7.3 Grep 机器检查命令清单

```bash
# v2.0 修正持久性验证（7 项）
grep -n "s_ws_adapter\.type\s*=\s*PROTOCOL_WEBSOCKET" agentrt/protocols/common/src/protocols_impl.c
# = L117

grep -n "agent_registry_core_\(get\|get_latest_version\|list\|search_by_tag\)\s*(" agentrt/daemons/market_d/include/agent_registry_core.h
# = L71/82/98/110（均含 out 参数）

grep -n "AIRY_INIT_SPIN_MAX_RETRIES\|sched_yield\|Sleep(0)\|memory_order_acquire" agentrt/atoms/corekern/src/core_init.c
# = 10 行匹配

grep -n "cupolas_mutex_destroy\|g_cupolas_init_state\|CUPOLAS_INIT_SPIN_MAX_RETRIES\|cupolas_atomic_cas32" agentrt/cupolas/src/cupolas.c
# = 19 行匹配

grep -n "goto out_\(mtx_sock\|service\|server_fd\|event_driver\)\|^out_\(mtx_sock\|service\|server_fd\|event_driver\):" agentrt/daemons/sched_d/src/main.c
# = 8 行匹配（4 goto + 4 label）

grep -c "static inline airy_err_t airy_\(mtx\|cond\|rwlock\|sem\)_" agentrt/commons/utils/sync/include/sync_compat.h
# = 25 wrapper + 1 airy_sync_map_err

# P0-2 违规规模统计
grep -c "^    [a-zA-Z_]" agentrt/**/*.c agentrt/**/*.h  # 4 空格缩进 = 12535+
grep -c "typedef\s+struct" agentrt/**/*.c agentrt/**/*.h  # typedef struct = 597
grep -c "/\* =+ [^=]+ =+ \*/\|// =+[^=]+=+" agentrt/**/*.c agentrt/**/*.h  # 装饰符 = 354
grep -c "\bfprintf\s*(" agentrt/**/*.c agentrt/**/*.h  # fprintf = 174

# V3.0-N3 验证（5 daemon goto-less 模式）
grep -n "return\s*1\s*;" agentrt/daemons/{market_d,llm_d,tool_d,monit_d,channel_d}/src/main.c
# = 19 处 return 1

# V3.0-N4 验证（N6 被 platform.h 屏蔽）
grep -n "#ifndef AIRY_RT_PLATFORM_H" agentrt/commons/utils/sync/include/sync_compat.h  # = L32
grep -n "int airy_mtx_init" agentrt/commons/platform/platform.c  # = L194（返回原始 POSIX errno）
```

### 7.4 术语对照

| 术语 | 定义 |
|------|------|
| DCLP | Double-Checked Locking Pattern（双重检查锁定模式） |
| OLK-6.6 | Linux 6.6 内核基线编码风格（agent-linux 工程标准基线） |
| [SC] | Shared Contract（共享契约层） |
| SSoT | Single Source of Truth（单一真值源） |
| BAN-70 | fprintf 禁用规则（允许 EXEMPT 标注豁免） |
| BAN-333 | pregel_engine max_workers=1 强制串行降级规则 |
| OS-KER-001 | goto fall-through 集中清理模式工程铁律 |
| V3.0-N1 | v3.0 新发现 #1：DCLP 自旋等待失败后返回 SUCCESS |
| V3.0-N2 | v3.0 新发现 #2：DCLP 自旋超时后状态卡死在 2 |
| V3.0-N3 | v3.0 新发现 #3：N5 修正不完整，5 daemon 同模式 |
| V3.0-N4 | v3.0 新发现 #4：N6 修正被 platform.h 屏蔽 |

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>

---

**报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-14 | 审查版本：v3.0
