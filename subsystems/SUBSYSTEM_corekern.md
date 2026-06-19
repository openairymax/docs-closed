# CoreKern 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-17 | **团队**: A（核心引擎）
> **代码路径**: `agentos/atoms/corekern/`

---

## 1. 职责边界

CoreKern 是 AgentRT 的微内核，提供 Agent 运行时最底层的基础设施服务。它不包含任何 AI/LLM 逻辑，仅负责操作系统级别的资源管理。

### 核心职责

| 模块 | 职责 | 源文件 |
|------|------|--------|
| **内存管理** | 分配/释放/追踪/泄漏检测，Arena 线性分配器，线程缓存(tcache)，内存池(pool)，引用计数(refcount)，内存守卫(guard) | `src/mem/alloc.c`, `arena.c`, `pool.c`, `tcache.c`, `refcount.c`, `guard.c` |
| **OOM 处理** | 五级内存压力框架(NORMAL→WARNING→DEGRADED→CRITICAL→FATAL)，降级回调，分配检查，统计报告 | `src/mem/oom_handler.c` |
| **任务调度** | 任务创建/调度/优先级管理，协程式 yield，依赖解析 | `src/task/scheduler.c`, `scheduler_core.c`, `scheduler_platform.c` |
| **线程管理** | 线程创建/销毁/join，线程本地存储 | `src/task/thread.c` |
| **IPC 通信** | 进程间通道创建/消息发送接收/同步调用，Buffer 管理 | `src/ipc/binder.c`, `buffer.c` |
| **时间服务** | 单调时钟/实时时钟，sleep，定时器，事件同步 | `src/time/clock.c`, `timer.c`, `event.c` |
| **可观测性** | 日志/指标/追踪基础设施 | `src/observability/observability.c` |
| **错误处理** | 统一错误码定义，错误栈追踪 | `src/error.c` |
| **核心初始化** | 子系统启动/关闭编排 | `src/core_init.c` |

### 非职责（明确排除）

- AI/LLM 推理逻辑（属于 CoreLoopThree）
- 安全守卫/内容过滤（属于 Cupolas）
- 网络协议处理（属于 gateway_d）
- 工具调用执行（属于 tool_d）
- 持久化存储（属于 HeapStore）
- 配置管理（属于 commons + 各 daemon）

---

## 2. 公共接口

### 2.1 头文件清单

| 头文件 | 用途 | 公开 API 数量 |
|--------|------|:---:|
| `agentos.h` | 统一入口，包含所有子模块头文件 | — |
| `export.h` | AGENTOS_API 导出宏定义 | — |
| `mem.h` | 内存管理 API | 15+ |
| `oom_handler.h` | OOM 处理框架 API | 20+ |
| `task.h` | 任务调度 API | 12+ |
| `ipc.h` | 进程间通信 API | 10+ |
| `agentos_time.h` | 时间服务 API | 8+ |
| `error.h` | 错误码定义 + 日志宏 | 5+ |
| `arena.h` | Arena 线性分配器 | 6 |
| `tcache.h` | 线程本地缓存 | 5 |
| `refcount.h` | 原子引用计数 | 4 |
| `observability.h` | 可观测性 API | 5+ |
| `platform_core.h` | 平台抽象层 | 3+ |
| `stdatomic.h` | C11 原子操作兼容层 | — |

### 2.2 关键 API 签名

```c
// 核心初始化
agentos_error_t agentos_core_init(void);
void agentos_core_shutdown(void);

// 内存管理
void *agentos_mem_alloc(size_t size);
void *agentos_mem_calloc(size_t count, size_t size);
void agentos_mem_free(void *ptr);
void *agentos_mem_realloc(void *ptr, size_t size);
void agentos_mem_check_leaks(void);
void agentos_mem_cleanup(void);

// OOM 处理
agentos_error_t agentos_oom_init(size_t total_system_memory);
void agentos_oom_destroy(void);
agentos_mem_pressure_level_t agentos_oom_get_pressure(void);
void agentos_oom_set_pressure(agentos_mem_pressure_level_t level);
int agentos_oom_check_allocation(size_t requested_size);
agentos_error_t agentos_register_degradation(degradation_handler_t *handler);
void agentos_unregister_degradation(degradation_handler_t *handler);
void agentos_oom_degrade(watermark_level_t old_level, watermark_level_t new_level);

// 任务调度
agentos_error_t agentos_task_create(agentos_task_t *task, ...);
agentos_error_t agentos_task_yield(void);
agentos_error_t agentos_task_sleep(uint32_t ms);

// IPC
agentos_error_t agentos_ipc_channel_create(agentos_ipc_channel_t *ch, ...);
agentos_error_t agentos_ipc_send(agentos_ipc_channel_t *ch, const void *data, size_t size);
agentos_error_t agentos_ipc_recv(agentos_ipc_channel_t *ch, void *buf, size_t *size);

// 时间服务
uint64_t agentos_clock_monotonic_ms(void);
uint64_t agentos_clock_realtime_ms(void);
void agentos_sleep_ms(uint32_t ms);
```

### 2.3 错误码（部分）

| 错误码 | 值 | 含义 |
|--------|:---:|------|
| `AGENTOS_SUCCESS` | 0 | 成功 |
| `AGENTOS_EINVAL` | -1 | 无效参数 |
| `AGENTOS_ENOMEM` | -2 | 内存不足 |
| `AGENTOS_ENOTINIT` | -3 | 未初始化 |
| `AGENTOS_EEXIST` | -4 | 已存在 |
| `AGENTOS_EBUSY` | -5 | 资源忙 |
| `AGENTOS_ENOENT` | -6 | 不存在 |
| `AGENTOS_EALREADY` | -7 | 已完成/已操作 |

---

## 3. 依赖关系

### 3.1 内部依赖（编译时）

```
corekern
  ├── agentos_atoms (atoms 公共接口)
  └── agentos_common (commons 公共库)
       ├── utils/memory/    — memory_compat.h, memory_common.h, memory_prealloc.h
       ├── utils/error/     — error_compat.h, error_types.h
       ├── utils/types/     — agentos_types.h, basic_types.h
       ├── utils/string/    — string_compat.h, safe_string.h
       ├── utils/compliance/— banned_functions.h
       ├── utils/logging/   — logging_compat.h
       ├── utils/sync/      — 互斥锁/信号量
       └── platform/        — platform.h, agentos_sleep_ms
```

### 3.2 运行时依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| POSIX 线程 (libpthread) | 系统 | 线程创建/互斥锁 |
| 系统时钟 (clock_gettime) | 系统 | 单调/实时时钟 |
| nanosleep / Sleep | 系统 | 跨平台 sleep |

### 3.3 被依赖方

| 消费者 | 使用接口 | 说明 |
|--------|---------|------|
| CoreLoopThree | 任务调度、内存分配 | 认知循环执行 |
| Cupolas | 内存分配、IPC | 安全守卫 |
| 所有 daemon | 内存管理、错误处理 | 通用基础设施 |
| gateway_d | IPC 通道 | 协议网关通信 |
| llm_d | 内存管理、OOM 回调 | LLM 推理 |
| tool_d | 线程管理、IPC | 工具执行 |

---

## 4. 配置参数

### 4.1 OOM 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `warning_threshold` | double | 0.70 | WARNING 级别内存使用率阈值 |
| `degraded_threshold` | double | 0.80 | DEGRADED 级别阈值 |
| `critical_threshold` | double | 0.90 | CRITICAL 级别阈值 |
| `fatal_threshold` | double | 0.95 | FATAL 级别阈值 |
| `check_interval_ms` | uint32_t | 1000 | 内存检查间隔(ms) |
| `recovery_cooldown_ms` | uint32_t | 5000 | 恢复冷却时间(ms) |
| `enable_auto_recovery` | bool | true | 是否启用自动恢复 |
| `enable_allocation_check` | bool | true | 是否启用分配检查 |
| `emergency_pool_size` | size_t | 1MB | 紧急内存池大小 |
| `max_heap_size` | size_t | 0(自动) | 最大堆大小 |

### 4.2 Arena 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `block_size` | size_t | 64KB | 默认 Arena 块大小 |
| `ARENA_MIN_BLOCK_SIZE` | size_t | 4KB | 最小块大小 |
| `ARENA_ALIGN_SIZE` | size_t | 16 | 默认对齐 |

### 4.3 tcache 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `slot_size` | size_t | 256 | 缓存槽大小 |
| `max_slots` | uint32_t | 256 | 最大槽位数 |
| `batch_size` | uint32_t | 32 | 批量获取/归还大小 |

### 4.4 内存池配置

| 参数 | 说明 |
|------|------|
| `block_size` | 每个池块大小（≥ sizeof(void*)） |
| `block_count` | 池中块数量 |
| `POOL_MAGIC` | 0x504F4F4C，用于校验池完整性 |

---

## 5. 跨团队接口合约

### 5.1 合约文件

- `contracts/contract_A_C.h` — 团队A(CoreKern) 与 团队C(测试/质量) 的接口合约

### 5.2 测试接口

| 函数 | 用途 | 消费者 |
|------|------|--------|
| `agentos_oom_get_handler()` | 获取 OOM handler 内部状态 | 测试 |
| `agentos_oom_set_pressure()` | 手动设置压力级别 | 测试 |
| `agentos_oom_get_pressure()` | 获取当前压力级别 | 测试/监控 |
| `agentos_oom_report_stats()` | 输出统计报告 | 测试/监控 |

---

## 6. 文件所有权

```
@owner: team-A
```

所有 `agentos/atoms/corekern/` 下的文件归属于团队A。团队C 仅可修改 `tests/` 目录下的测试文件。

---

## 7. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-06-17 | 初始版本，基于 v0.1.1 代码现状 |