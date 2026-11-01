# Memory 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-17 | **团队**: A（核心引擎）
> **代码路径**: `agentrt/commons/utils/memory/`

---

## 1. 职责边界

Memory 是 AgentRT 的统一内存管理框架，提供安全的内存分配/释放、内存调试和统计追踪等基础设施。它是 AgentRT 中所有内存操作的基础，旨在消除项目中分散的内存管理代码，提供一致的内存管理策略。

> **归属说明（2026-09-11）**：Arena 线性分配器（`airy_arena_*`）、per-thread cache（`airy_tcache_*`）与引用计数（`refcounted_t`）的权威实现已统一到 corekern（`atoms/corekern/include/arena.h`、`include/tcache.h`、`include/refcount.h`），commons 侧的平行实现已删除。
>
> **归属说明（2026-10-06）**：内存池与 Slab（`airy_mempool_*` / `airy_slab_*`）的权威实现统一归 corekern（`atoms/corekern/include/mempool.h`、`include/slab.h`）；commons 侧 `memory_pool_*` 平行实现与 cupolas 内部 mempool/slab 副本已删除，避免同名符号重复定义。

### 核心职责

| 模块 | 职责 | 源文件 |
|------|------|--------|
| **核心分配层** | 安全的内存分配/释放/重分配，支持对齐分配、零初始化、失败策略、标签追踪 | `src/memory.c` (`airy_memory.h`) |
| **兼容层** | 与标准 C 库兼容的 `AIRY_MALLOC`/`AIRY_FREE` 等宏，安全缓冲区操作，溢出检查 | `memory_compat.h` |
| **内存调试** | 泄漏检测、边界检查、释放后使用检查、双重释放检查、堆栈跟踪、检查点比较 | `src/memory_debug.c` (`memory_debug.h`) |
| **统计追踪** | 全局内存统计、按类别跟踪（ALLOC_SHORT_LIVED/LONG_LIVED/CRITICAL）、水位监控、OOM 响应 | `src/memory_common.c` (`memory_common.h`) |
| **统计上报** | 后台线程定期（60s）上报 6 项关键内存指标（总分配、总释放、当前使用率、峰值、分配次数、碎片率） | `src/memory_stats_reporter.c` (`memory_stats_reporter.h`) |
| **预分配池** | 启动时预分配应急缓冲区（信号/OOM/审计/关闭），保证关键路径分配永不失败 | `src/memory_prealloc.c` (`memory_prealloc.h`) |

### 非职责（明确排除）

- 不负责 AI/LLM 推理逻辑（属于 CoreLoopThree）
- 不负责业务级内存语义（属于 coreloopthree 的记忆引擎）
- 不负责持久化存储格式（属于 HeapStore）
- 不负责 OOM 处理框架的执行调度（属于 corekern 的 `oom_handler`）
- 不负责禁止函数编译期注入（属于 `commons/utils/compliance/banned_functions.h`，通过 CMake `-include` 注入）

---

## 2. 公共接口

### 2.1 头文件清单

| 头文件 | 用途 | 公开 API 数量 |
|--------|------|:---:|
| `airy_memory.h` | 核心层 API：分配/释放/统计/调试 | 16+ |
| `memory_common.h` | 安全分配接口 + 全局策略 | 10+ |
| `memory_compat.h` | 向后兼容层：安全宏 + OOM 水位监控 + 分配追踪 | 20+ |
| `memory_debug.h` | 内存调试：泄漏检测/边界检查/堆栈跟踪/检查点 | 17+ |
| `memory_prealloc.h` | 预分配应急池：init/shutdown/acquire/release | 6 |
| `memory_stats_reporter.h` | 统计上报：init/shutdown/get/record_alloc/record_oom | 7 |

### 2.2 关键 API 签名

```c
// 核心生命周期
bool memory_init(const memory_options_t *options);
void memory_cleanup(void);

// 核心分配
void *memory_alloc(size_t size, const char *tag);
void *memory_calloc(size_t size, const char *tag);
void *memory_aligned_alloc(size_t alignment, size_t size, const char *tag);
void *memory_realloc(void *ptr, size_t new_size, const char *tag);
void memory_free(void *ptr);

// 统计与调试
bool memory_get_stats(memory_stats_t *stats);
void memory_reset_stats(void);
size_t memory_get_current_usage(void);
size_t memory_get_peak_usage(void);
size_t memory_check_leaks(bool dump_to_stderr);
void memory_dump_debug_info(const char *file);
bool memory_validate(void *ptr);
bool memory_debug_enable(bool enable);
void memory_set_fail_callback(void (*callback)(size_t, const char*, void*), void *user_data);

// Arena 分配器（权威实现已归 corekern：atoms/corekern/include/arena.h，airy_arena_*）
airy_arena_t *airy_arena_create(size_t block_size);
void airy_arena_destroy(airy_arena_t *arena);
void *airy_arena_alloc(airy_arena_t *arena, size_t size);
void *airy_arena_alloc_aligned(airy_arena_t *arena, size_t size, size_t alignment);
void airy_arena_reset(airy_arena_t *arena);
airy_arena_mark_t airy_arena_mark(airy_arena_t *arena);
void airy_arena_reset_to(airy_arena_t *arena, airy_arena_mark_t mark);
size_t airy_arena_used(airy_arena_t *arena);
size_t airy_arena_capacity(airy_arena_t *arena);

// 线程缓存（权威实现已归 corekern：atoms/corekern/include/tcache.h，airy_tcache_*）
// 引用计数（权威实现已归 corekern：atoms/corekern/include/refcount.h，refcount_*）

// 预分配
int airy_prealloc_init(void);
void airy_prealloc_shutdown(void);
void *airy_prealloc_acquire(int category);
void airy_prealloc_release(int category);

// 统计上报
int airy_mem_stats_reporter_init(void);
void airy_mem_stats_reporter_shutdown(void);
int airy_mem_stats_get(airy_mem_stats_t *stats);
void airy_mem_stats_record_alloc(size_t bytes);
void airy_mem_stats_record_dealloc(size_t bytes);
void airy_mem_stats_record_oom(void);
```

### 2.3 兼容层关键宏

| 宏 | 说明 |
|------|------|
| `AIRY_MALLOC(size)` | 安全内存分配（替代 `malloc`，自动记录统计） |
| `AIRY_CALLOC(num, size)` | 安全清零分配（替代 `calloc`，含溢出检查） |
| `AIRY_REALLOC(ptr, new_size)` | 安全重分配（替代 `realloc`） |
| `AIRY_FREE(ptr)` | 安全释放（替代 `free`，自动记录统计） |
| `AIRY_STRDUP(str)` | 安全字符串复制（替代 `strdup`） |
| `AIRY_STRNCPY_TERM(dst, src, size)` | 安全字符串复制（保证 null 终止） |
| `AIRY_MEMCPY_SAFE(dst, src, size, dst_capacity)` | 带边界检查的 `memcpy` |
| `AIRY_MEMSET(ptr, value, size)` | 带零大小保护的 `memset` |
| `SAFE_MALLOC(ptr, size)` | 安全分配（失败返回 NULL） |
| `SAFE_MALLOC_ARRAY(ptr, count, element_size)` | 安全数组分配（带溢出检查） |
| `MEMORY_FREE_SAFE(ptr_ptr)` | 安全释放并置 NULL |

### 2.4 错误码（来自 corekern `error.h`）

| 错误码 | 含义 |
|--------|------|
| `AIRY_SUCCESS` (0) | 成功 |
| `AIRY_EINVAL` | 无效参数 |
| `AIRY_ERR_OUT_OF_MEMORY` | 内存不足 |
| `AIRY_ERR_BUSY` | 资源忙（如回调槽位已满） |
| `AIRY_E_OVERFLOW` | 整数溢出（如 count * size 溢出） |

---

## 3. 依赖关系

### 3.1 内部依赖（编译时）

```
commons/utils/memory/
  ├── error.h (来自 corekern)           — airy_err_t 错误码
  ├── stdbool.h / stddef.h / stdint.h   — 标准 C 类型
  ├── stdatomic.h                       — C11 原子操作
  └── commons/utils/compliance/         — banned_functions.h（通过 CMake -include 注入）
```

### 3.2 运行时依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| POSIX 线程 (libpthread) | 系统 | 线程安全互斥锁（全局统计与调试表加锁） |
| 系统时钟 | 系统 | 分配时间戳（`airy_time_ms()`） |

### 3.3 被依赖方

| 消费者 | 使用接口 | 说明 |
|--------|---------|------|
| corekern | `AIRY_MALLOC`/`AIRY_FREE`、`memory_compat.h` | 所有内存操作的基础设施 |
| CoreLoopThree | 内存分配 | 认知循环中的临时分配 |
| Cupolas | 内存分配 | 安全守卫运行 |
| 所有 daemon | `AIRY_MALLOC`/`AIRY_FREE` | 通用内存分配 |
| llm_d | OOM 水位回调 | LLM 推理内存管理 |
| tool_d | 内存分配 | 工具执行 |

---

## 4. 配置参数

### 4.1 核心配置 (`memory_options_t`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `alignment` | size_t | 0（默认） | 内存对齐要求 |
| `zero_memory` | bool | false | 是否将分配的内存清零 |
| `tag` | const char* | NULL | 内存分配标签（调试用） |
| `fail_strategy` | enum | RETURN_NULL | 失败策略：RETURN_NULL / ABORT / CALLBACK / RETRY |
| `fail_callback` | 函数指针 | NULL | 分配失败回调 |
| `fail_callback_user_data` | void* | NULL | 失败回调用户数据 |

### 4.2 Arena / tcache 配置（权威实现已归 corekern）

Arena 与 tcache 不再有全局配置常量；参数在创建时传入（corekern `atoms/corekern/include/arena.h`、`include/tcache.h`）：

| 参数 | 传入方式 | 说明 |
|------|------|------|
| arena 块大小 | `airy_arena_create(block_size)` | 初始块大小，块耗尽自动链式扩展 |
| arena 对齐 | 默认 `sizeof(void*)`；自定义用 `airy_arena_alloc_aligned(…, alignment)` | alignment 须为 2 的幂 |
| tcache 参数 | `airy_tcache_create(const airy_tcache_config_t *config, …)` | 批量/缓存上限等经 config 结构传入 |

### 4.3 预分配池 (`memory_prealloc.h`)

| 参数 | 值 | 说明 |
|------|:---:|------|
| `AIRY_PREALLOC_SIGNAL_BUF_SIZE` | 4096 | 信号处理器缓冲区 |
| `AIRY_PREALLOC_OOM_BUF_SIZE` | 8192 | OOM 错误报告缓冲区 |
| `AIRY_PREALLOC_AUDIT_BUF_SIZE` | 16384 | 审计日志应急缓冲区 |
| `AIRY_PREALLOC_SHUTDOWN_BUF_SIZE` | 8192 | 应急关闭缓冲区 |

### 4.4 内存调试配置 (`memory_debug_options_t`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `enable_leak_check` | bool | false | 启用泄漏检查 |
| `enable_boundary_check` | bool | false | 启用边界检查 |
| `enable_use_after_free_check` | bool | false | 启用释放后使用检查 |
| `enable_double_free_check` | bool | false | 启用双重释放检查 |
| `enable_invalid_free_check` | bool | false | 启用无效释放检查 |
| `track_allocations` | bool | false | 跟踪分配信息 |
| `fill_pattern_on_alloc` | bool | false | 分配时填充模式 |
| `fill_pattern_on_free` | bool | false | 释放时填充模式 |
| `redzone_size` | size_t | 0 | 红区大小（边界检查） |
| `verbosity_level` | int | 0 | 详细级别（0-3） |

### 4.7 统计上报配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `report_interval` | unsigned int | 60 | 上报间隔（秒） |

---

## 5. 跨团队接口合约

### 5.1 合约文件

- `contracts/contract_A_C_memory.h` — 团队A（Memory）与团队C（测试/质量）的接口合约

### 5.2 测试接口

| 函数 | 用途 | 消费者 |
|------|------|--------|
| `memory_get_stats()` | 获取全局内存统计 | 测试/监控 |
| `memory_reset_stats()` | 重置全局内存统计 | 测试 |
| `memory_check_leaks(dump_to_stderr)` | 检查内存泄漏 | 测试 |
| `memory_validate(ptr)` | 验证内存块完整性 | 测试 |
| `memory_debug_check_leaks(report, dump)` | 详细泄漏检测 | 测试 |
| `memory_debug_validate_all(error_count, dump)` | 全量内存块验证 | 测试 |
| `memory_debug_checkpoint(name)` | 创建内存状态检查点 | 测试 |
| `memory_debug_compare_checkpoints(cp1, cp2, report)` | 比较检查点差异 | 测试 |
| `airy_arena_used(arena)` / `airy_arena_capacity(arena)` | 获取 Arena 用量/容量（corekern） | 测试/监控 |
| `airy_tcache_get_stats(tc, stats)` | 获取 tcache 统计（corekern） | 测试/监控 |
| `airy_mem_stats_get(stats)` | 获取运行时统计快照 | 测试/监控 |
| `airy_mem_stats_record_oom()` | 记录 OOM 事件 | 测试 |

---

## 6. 文件所有权

```
@owner: team-A
```

所有 `agentrt/commons/utils/memory/` 下的文件归属于团队A。团队C 仅可修改 `test/` 目录下的测试文件。

---

## 7. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-06-17 | 初始版本，基于 v0.1.0 代码现状 |