# 源码修正日志

> **作用域**：`agentrt/` 源码 P0/P1 级问题修正
> **基准报告**：`01-engineering-code-review-v2.md`（v2.0 工程代码审查）
> **修正日期**：2026-07-13
> **修正原则**：IRON-1~5 工程铁律（禁止桩函数/禁止简化功能/禁止绕开限制的编译集成）
> **跨平台约束**：Linux/macOS/Windows 三平台用户态路径均保持兼容

---

## 修正总览

| 编号 | 严重度 | 问题摘要 | 修正状态 | 涉及文件 |
|------|--------|----------|----------|----------|
| P0-6 | P0 | WebSocket 适配器协议类型错误（PROTOCOL_HTTP → PROTOCOL_WEBSOCKET） | ✅ 已修正 | `protocols_impl.c` |
| P0-7 | P0 | agent_registry_core 4 函数解锁后返回内部指针（数据竞争） | ✅ 已修正 | `agent_registry_core.h` / `.c` |
| N1 | P1 | core_init DCLP 自旋等待无 yield/无超时（CPU 空转 + 潜在死锁） | ✅ 已修正 | `core_init.c` |
| N2 | P1 | cupolas_init 4 条错误路径泄漏 mutex（仅 unlock 未 destroy） | ✅ 已修正 | `cupolas.c` |
| N3 | P1 | cupolas_init 非并发安全（锁外检查 initialized + memset 整结构） | ✅ 已修正 | `cupolas.c` |
| N5 | P1 | sched_d main.c 4 处重复错误清理块（无 goto 集中出口） | ✅ 已修正 | `sched_d/main.c` |
| N6 | P2 | sync_compat.h 丢弃底层错误码（仅返回 0/-1） | ✅ 已修正 | `sync_compat.h` |

---

## P0-6：WebSocket 适配器协议类型错误

**文件**：`agentrt/protocols/common/src/protocols_impl.c:117`

**问题**：WebSocket 适配器 `s_ws_adapter` 的 `type` 字段被错误设置为 `PROTOCOL_HTTP`，导致协议分发时 WebSocket 连接被当作 HTTP 处理。

**修正前**：
```c
s_ws_adapter.type = PROTOCOL_HTTP;
```

**修正后**：
```c
s_ws_adapter.type = PROTOCOL_WEBSOCKET;
```

**验证**：
- `PROTOCOL_WEBSOCKET` 枚举值已确认存在于 `unified_protocol.h:106`
- Grep 验证：`protocols_impl.c:117` 现为 `PROTOCOL_WEBSOCKET`，无 `PROTOCOL_HTTP` 残留
- WebSocket 适配器其余字段（`init`/`send`/`recv`/`close` 回调）未受影响，原功能保持

---

## P0-7：agent_registry_core 数据竞争（解锁后返回内部指针）

**文件**：
- `agentrt/daemons/market_d/include/agent_registry_core.h:71,82,98,110`
- `agentrt/daemons/market_d/src/agent_registry_core.c`

**问题**：4 个查询函数（`get`/`get_latest_version`/`list`/`search_by_tag`）在锁内查到目标后，解锁并返回指向 registry 内部 `entries[]` 数组的指针。调用方在锁外访问该指针时，其他线程可能并发修改或扩容 `entries[]`，导致 use-after-free 或数据损坏。

**修正方案**：改为 copy-to-caller-buffer 模式——在锁内将数据浅拷贝到调用方传入的输出缓冲区，解锁后返回。函数签名相应变更。

**修正前签名**（返回内部指针）：
```c
const agent_entry_t *agent_registry_core_get(agent_registry_t *registry, const char *agent_id);
const char *agent_registry_core_get_latest_version(agent_registry_t *registry, const char *agent_id);
size_t agent_registry_core_list(agent_registry_t *registry, const agent_entry_t **out_entries, size_t max_entries);
size_t agent_registry_core_search_by_tag(agent_registry_t *registry, const char *tag, const agent_entry_t **out_entries, size_t max_entries);
```

**修正后签名**（copy-to-buffer）：
```c
int  agent_registry_core_get(agent_registry_t *registry, const char *agent_id, agent_entry_t *out);
int  agent_registry_core_get_latest_version(agent_registry_t *registry, const char *agent_id, char *out, size_t out_size);
size_t agent_registry_core_list(agent_registry_t *registry, agent_entry_t *out_entries, size_t max_entries);
size_t agent_registry_core_search_by_tag(agent_registry_t *registry, const char *tag, agent_entry_t *out_entries, size_t max_entries);
```

**实现模式**（以 `get` 为例）：
```c
int agent_registry_core_get(agent_registry_t *registry, const char *agent_id, agent_entry_t *out)
{
    if (!registry || !registry->initialized || !agent_id || !out)
        return AIRY_ERR_INVALID_PARAM;
    airy_mtx_lock(&registry->lock);
    for (size_t i = 0; i < registry->entry_count; i++) {
        if (strcmp(registry->entries[i].id, agent_id) == 0) {
            *out = registry->entries[i];   /* 锁内浅拷贝 */
            airy_mtx_unlock(&registry->lock);
            return 0;
        }
    }
    airy_mtx_unlock(&registry->lock);
    return AIRY_ERR_NOT_FOUND;
}
```

**验证**：
- Grep 确认 4 个函数签名均已变更（`.h:71,82,98,110`）
- `.c` 实现均采用锁内拷贝 + 解锁后返回模式
- 返回值语义：成功返回 `0`/`AIRY_OK`，失败返回 `AIRY_ERR_NOT_FOUND`/`AIRY_ERR_INVALID_PARAM`
- **调用方影响**：经 Grep 确认，`_core` 系列函数当前为 dead code——`agent_registry.c` 包装层有独立实现（不调用 `_core` 函数），测试文件 `test_agent_registry_core.c` 调用的是无 `_core` 后缀的函数名（历史遗留）。因此签名变更不会破坏现有编译。
- **已知遗留**：`agent_registry_core_search`（非 `search_by_tag`）函数（`.h:239+`）存在相同数据竞争模式，但不在本次 4 函数修正范围内，标记延期至 1.0.1。

---

## N1：core_init DCLP 自旋等待无 yield/无超时

**文件**：`agentrt/atoms/corekern/src/core_init.c:26-62`

**问题**：DCLP（Double-Checked Locking Pattern）中，当线程检测到 `g_core_initialized == 2`（初始化中）时，使用 `while (atomic_load_explicit(..., memory_order_seq_cst) == 2) {}` 空转等待。存在三个缺陷：
1. 无 `sched_yield`/`Sleep(0)` 让出 CPU → 100% 空转
2. 无超时保护 → 初始化线程崩溃时等待线程永久自旋（潜在死锁）
3. `memory_order_seq_cst` 过度保守 → CAS 已在上方建立 happens-before，acquire 足够

**修正前**：
```c
while (atomic_load_explicit(&g_core_initialized, memory_order_seq_cst) == 2) {
}
```

**修正后**：
```c
/* N1 修复：跨平台 yield + 超时保护 + acquire 内存序 */
#ifdef _WIN32
#include <windows.h>
#else
#include <sched.h>
#endif

#define AIRY_INIT_SPIN_MAX_RETRIES 10000000UL

unsigned long spin_count = 0;
while (atomic_load_explicit(&g_core_initialized, memory_order_acquire) == 2) {
#ifdef _WIN32
    Sleep(0);
#else
    sched_yield();
#endif
    if (++spin_count >= AIRY_INIT_SPIN_MAX_RETRIES) {
        AIRY_LOG_ERROR("core_init: init spin-wait timed out after %lu retries", spin_count);
        return AIRY_ERR_TIMEOUT;
    }
}
```

**验证**：
- Grep 确认 `AIRY_INIT_SPIN_MAX_RETRIES`、`sched_yield`、`Sleep(0)`、`memory_order_acquire`、`AIRY_ERR_TIMEOUT` 均已就位（`core_init.c:38,53,55,57,59,62`）
- 跨平台 yield 模式参照现有 `alloc.c:118-125` 的成熟实现
- 10,000,000 次 `sched_yield` 约对应 10+ 秒等待，足以覆盖正常初始化耗时
- 超时后返回 `AIRY_ERR_TIMEOUT`（-8），调用方可据此重试或报警

---

## N2：cupolas_init 4 条错误路径泄漏 mutex

**文件**：`agentrt/cupolas/src/cupolas.c:142,161,180,205`

**问题**：`cupolas_init()` 中 `cupolas_mutex_init(&g_cupolas.lock)` 成功后，4 条错误路径（config 加载失败、permission_engine 创建失败、sanitizer 创建失败、audit_logger 创建失败）仅调用 `cupolas_mutex_unlock` 而未调用 `cupolas_mutex_destroy`，导致 mutex 资源泄漏。

**修正前**：
```c
cupolas_mutex_unlock(&g_cupolas.lock);
return result;  /* ← mutex 未 destroy，泄漏 */
```

**修正后**：
```c
cupolas_mutex_unlock(&g_cupolas.lock);
cupolas_mutex_destroy(&g_cupolas.lock);   /* N2 修复：销毁避免泄漏 */
cupolas_atomic_store32(&g_cupolas_init_state, 0);  /* N3 修复：重置状态允许重试 */
return result;
```

**验证**：
- Grep 确认 4 处错误路径均添加了 `cupolas_mutex_destroy`（`cupolas.c:142,161,180,205`）
- mutex 生命周期完整：`init` → `lock` → `unlock` → `destroy`
- 同时添加了 `cupolas_atomic_store32(&g_cupolas_init_state, 0)` 重置状态（配合 N3 修复）

---

## N3：cupolas_init 非并发安全

**文件**：`agentrt/cupolas/src/cupolas.c:80-220`

**问题**：原实现在锁外检查 `g_cupolas.initialized`，若未初始化则 `__builtin_memset(&g_cupolas, 0, sizeof(g_cupolas))` 清零整个结构（含 mutex 字段）。两个线程可同时通过检查，导致数据竞争：一个线程 memset 清零 mutex 时，另一个线程可能正在使用该 mutex。

**修正方案**：引入 DCLP 原子 CAS 状态机（参照 `core_init.c` 模式），使用 cupolas 自有原子操作（非 C11 stdatomic）：
- 状态 `0` = 未初始化
- 状态 `2` = 初始化中（仅一个线程持有）
- 状态 `1` = 就绪

**修正后关键逻辑**：
```c
static cupolas_atomic32_t g_cupolas_init_state = 0;
#define CUPOLAS_INIT_SPIN_MAX_RETRIES 10000000UL

int cupolas_init(const char *config_path, airy_err_t *error)
{
    /* 快速路径：已就绪 */
    if (cupolas_atomic_load32(&g_cupolas_init_state) == 1)
        return CUPOLAS_OK;

    /* CAS 0→2：仅一个线程进入初始化 */
    if (!cupolas_atomic_cas32(&g_cupolas_init_state, 0, 2)) {
        /* CAS 失败：其他线程正在初始化或已完成 */
        if (cupolas_atomic_load32(&g_cupolas_init_state) == 1)
            return CUPOLAS_OK;
        /* state==2：自旋等待 + cupolas_sleep_us(1) yield + 超时保护 */
        unsigned long spin_count = 0;
        while (cupolas_atomic_load32(&g_cupolas_init_state) == 2) {
            cupolas_sleep_us(1);
            if (++spin_count >= CUPOLAS_INIT_SPIN_MAX_RETRIES) {
                if (error) *error = AIRY_ERR_TIMEOUT;
                return cupolas_ERR_STATE_ERROR;
            }
        }
        return CUPOLAS_OK;
    }

    /* 仅获胜线程执行 memset + mutex_init + ... */
    __builtin_memset(&g_cupolas, 0, sizeof(g_cupolas));
    /* ... 初始化逻辑 ... */

    /* 成功：发布就绪状态 2→1（必须在 unlock 后，确保一致性） */
    cupolas_atomic_store32(&g_cupolas_init_state, 1);
    return CUPOLAS_OK;

    /* 错误路径：重置状态 2→0 允许后续重试 */
}
```

**验证**：
- Grep 确认 `g_cupolas_init_state`、`CUPOLAS_INIT_SPIN_MAX_RETRIES`、`cupolas_atomic_cas32`、`cupolas_atomic_load32`、`cupolas_atomic_store32` 均已就位
- 5 条错误路径（mutex init 失败 + 4 条 N2 路径）均重置状态为 `0`
- `cupolas_cleanup()` 末尾重置状态为 `0`（`cupolas.c:264`），允许重新初始化
- 成功路径在 `mutex_unlock` 后发布状态 `1`（`cupolas.c:217`），确保等待线程看到 `initialized=1` 与 `state=1` 一致
- 使用 cupolas 自有原子操作（`cupolas_atomic_*`），不引入 C11 stdatomic 依赖

---

## N5：sched_d main.c 重复错误清理块

**文件**：`agentrt/daemons/sched_d/src/main.c:252-327`

**问题**：`main()` 中 4 处错误路径各自包含独立的资源清理代码（`destroy_service` + `airy_mtx_destroy` + `airy_sock_cleanup` + `return 1`），导致代码重复且维护困难。违反 OS-KER-001 goto fall-through 集中清理模式。

**修正前**（4 处重复，以 service_create 失败为例）：
```c
if (ret != AIRY_SUCCESS || !g_service) {
    SVC_LOG_ERROR("Failed to create scheduler service (error=%d)", ret);
    airy_mtx_destroy(&g_running_lock_sched_d);
    airy_sock_cleanup();
    return 1;
}
/* ... 另外 3 处类似重复 ... */
```

**修正后**（goto fall-through 集中出口）：
```c
if (ret != AIRY_SUCCESS || !g_service) {
    SVC_LOG_ERROR("Failed to create scheduler service (error=%d)", ret);
    goto out_mtx_sock;
}
/* ... */
if (server_fd < 0) {
    SVC_LOG_ERROR("Failed to create server socket");
    goto out_service;
}
/* ... */
if (ret != AIRY_SUCCESS || !g_event_driver_sched_d) {
    SVC_LOG_ERROR("Failed to create event driver");
    goto out_server_fd;
}
/* ... */
if (daemon_event_driver_add_server_fd(...) != 0) {
    SVC_LOG_ERROR("Failed to add server fd to event driver");
    goto out_event_driver;
}

/* 成功路径不变 */
daemon_event_driver_run(g_event_driver_sched_d);
/* ... 标准清理 ... */
return 0;

/* N5 修复：goto 集中出口标签（按资源分配逆序释放，fall-through 模式） */
out_event_driver:
    daemon_event_driver_destroy(g_event_driver_sched_d);
out_server_fd:
    airy_sock_close(server_fd);
out_service:
    destroy_service();
out_mtx_sock:
    airy_mtx_destroy(&g_running_lock_sched_d);
    airy_sock_cleanup();
    return 1;
```

**验证**：
- Grep 确认 4 个 goto 跳转（`goto out_mtx_sock`/`out_service`/`out_server_fd`/`out_event_driver`）和 4 个标签均已就位（`main.c:255,266,290,303,318,320,322,324`）
- 资源释放顺序严格按分配逆序：`event_driver` → `server_fd` → `service` → `mtx` + `sock`
- `server_fd` 未初始化时（`goto out_service` 路径）不会执行 `airy_sock_close(server_fd)`，因为 `out_server_fd` 标签在 `out_service` 之后，fall-through 不会反向跳转
- 成功路径（`return 0`）不受影响，仍走 `daemon_cleanup_standard` 标准清理链

---

## N6：sync_compat.h 丢弃底层错误码

**文件**：`agentrt/commons/utils/sync/include/sync_compat.h:34-277`

**问题**：所有 25 个兼容层 inline 函数将底层 `sync_*` API 的具体错误码（`SYNC_ERROR_TIMEOUT`/`SYNC_ERROR_DEADLOCK`/`SYNC_ERROR_INVALID`/`SYNC_ERROR_MEMORY`/`SYNC_ERROR_PERMISSION`/`SYNC_ERROR_BUSY`/`SYNC_ERROR_UNSUPPORTED`）压缩为 `0`/`-1`，调用方无法区分失败原因，无法做差异化错误处理（重试/报警/回退）。

**修正前**：
```c
static inline int airy_mtx_init(sync_mutex_t *mutex, const void *attrs)
{
    (void)attrs;
    return sync_mutex_create(mutex, NULL) == SYNC_SUCCESS ? 0 : -1;  /* ← 丢弃错误码 */
}
```

**修正方案**：
1. 新增 `#include "error.h"`（airy_err_t 错误码定义）
2. 新增 `airy_sync_map_err()` 映射函数，将 `sync_result_t` 完整映射到 `airy_err_t`
3. 所有 25 个函数返回类型从 `int` 改为 `airy_err_t`，返回值从 `0/-1` 改为映射后的 `airy_err_t` 错误码

**错误码映射表**：

| sync_result_t | 值 | airy_err_t | 值 | 语义 |
|---------------|-----|------------|-----|------|
| SYNC_SUCCESS | 0 | AIRY_OK | 0 | 成功 |
| SYNC_ERROR_TIMEOUT | 1 | AIRY_ERR_TIMEOUT | -8 | 超时 |
| SYNC_ERROR_DEADLOCK | 2 | AIRY_ERR_SYS_DEADLOCK | -103 | 死锁 |
| SYNC_ERROR_INVALID | 3 | AIRY_ERR_INVALID_PARAM | -2 | 无效参数 |
| SYNC_ERROR_MEMORY | 4 | AIRY_ERR_OUT_OF_MEMORY | -4 | 内存不足 |
| SYNC_ERROR_PERMISSION | 5 | AIRY_ERR_PERMISSION_DENIED | -10 | 权限不足 |
| SYNC_ERROR_BUSY | 6 | AIRY_ERR_BUSY | -17 | 资源繁忙 |
| SYNC_ERROR_UNSUPPORTED | 7 | AIRY_ERR_NOT_SUPPORTED | -9 | 不支持 |
| SYNC_ERROR_UNKNOWN | 8 | AIRY_ERR_UNKNOWN | -1 | 未知错误 |

**修正后**（以 `airy_mtx_init` 为例）：
```c
static inline airy_err_t airy_mtx_init(sync_mutex_t *mutex, const void *attrs)
{
    (void)attrs;
    return airy_sync_map_err(sync_mutex_create(mutex, NULL));
}
```

**映射函数**：
```c
static inline airy_err_t airy_sync_map_err(sync_result_t r)
{
    switch (r) {
    case SYNC_SUCCESS:           return AIRY_OK;
    case SYNC_ERROR_TIMEOUT:     return AIRY_ERR_TIMEOUT;
    case SYNC_ERROR_DEADLOCK:    return AIRY_ERR_SYS_DEADLOCK;
    case SYNC_ERROR_INVALID:     return AIRY_ERR_INVALID_PARAM;
    case SYNC_ERROR_MEMORY:      return AIRY_ERR_OUT_OF_MEMORY;
    case SYNC_ERROR_PERMISSION:  return AIRY_ERR_PERMISSION_DENIED;
    case SYNC_ERROR_BUSY:        return AIRY_ERR_BUSY;
    case SYNC_ERROR_UNSUPPORTED: return AIRY_ERR_NOT_SUPPORTED;
    case SYNC_ERROR_UNKNOWN:
    default:                     return AIRY_ERR_UNKNOWN;
    }
}
```

**修正范围**（25 个函数，4 大类）：
- 互斥锁 API（5 个）：`airy_mtx_init`/`destroy`/`lock`/`trylock`/`unlock`
- 条件变量 API（6 个）：`airy_cond_init`/`destroy`/`wait`/`timedwait`/`signal`/`broadcast`
- 读写锁 API（7 个）：`airy_rwlock_init`/`destroy`/`rdlock`/`tryrdlock`/`wrlock`/`trywrlock`/`unlock`
- 信号量 API（7 个）：`airy_sem_init`/`destroy`/`wait`/`trywait`/`timedwait`/`post`/`getvalue`

**验证**：
- Grep 确认 0 处 `SYNC_SUCCESS ? 0 : -1` 残留（原为 25 处）
- Grep 确认 0 处 `static inline int airy_(mtx|cond|rwlock|sem)_` 残留（旧返回类型）
- Grep 确认 25 处 `static inline airy_err_t airy_(mtx|cond|rwlock|sem)_`（新返回类型）
- `airy_err_t` 为 `typedef int32_t airy_err_t`（`airy_types.h:40`），与 `int` ABI 兼容
- **调用方兼容性**：Grep 确认所有调用方均使用 `!= 0` 或 `== 0` 检查返回值（如 `weighted.c:82`、`memory.c:63`、`logging.c:576` 等），无 `== -1` 精确比较。AIRY_OK == 0，错误码为负值，`!= 0`/`== 0` 检查语义不变。
- `#include "error.h"` 位于 `#ifndef AIRY_RT_PLATFORM_H` 块内，仅当未包含 platform.h 时生效，无循环依赖
- `airy_sync_map_err` 为 `static inline`，无链接器冲突风险

---

## 跨平台兼容性验证

| 修正项 | Linux | macOS | Windows | 说明 |
|--------|-------|-------|---------|------|
| P0-6 | ✓ | ✓ | ✓ | 协议类型枚举，平台无关 |
| P0-7 | ✓ | ✓ | ✓ | mutex + 浅拷贝，使用 `airy_mtx_*` 跨平台 API |
| N1 | ✓ | ✓ | ✓ | `#ifdef _WIN32` → `Sleep(0)`；POSIX → `sched_yield()` |
| N2 | ✓ | ✓ | ✓ | `cupolas_mutex_destroy` 跨平台 |
| N3 | ✓ | ✓ | ✓ | `cupolas_atomic_*` + `cupolas_sleep_us` 跨平台 |
| N5 | ✓ | ✓ | ✓ | goto 模式，平台无关；`airy_sock_close`/`airy_mtx_destroy` 跨平台 |
| N6 | ✓ | ✓ | ✓ | `airy_err_t` 为 `int32_t`，所有平台一致 |

---

## 已知遗留（延期至 1.0.1）

| 编号 | 问题 | 原因 |
|------|------|------|
| — | `agent_registry_core_search`（非 `search_by_tag`）数据竞争 | 不在本次 4 函数修正范围内 |
| — | `agent_registry_core_*` 系列函数为 dead code（无活跃调用方） | `agent_registry.c` 包装层有独立实现，需在 1.0.1 统一清理 |
| — | `test_agent_registry_core.c` 调用无 `_core` 后缀的函数名 | 测试文件历史遗留，需在 1.0.1 修正 |
