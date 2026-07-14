# Checkpoint 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-18 | **团队**: A
> **代码路径**: `agentrt/heapstore/`

## 1. 职责边界

### 核心职责

| 职责 | 说明 |
|------|------|
| 数据分区管理 | 提供 AgentRT 全系统统一的数据分区存储，包含内核、日志、注册表、服务、追踪、IPC、内存七类路径 |
| 日志持久化 | 结构化日志的写入、轮转、清理、快慢路径双通道写入（`heapstore_log_write_fast` / `heapstore_log_write_slow`） |
| 追踪数据存储 | Span/Trace 的写入、批量写入、按 trace_id / 时间范围查询、导出为 JSON |
| 注册表管理 | Agent、Skill、Session 三类注册表的 CRUD 操作，支持批量插入（事务原子性）、迭代器遍历、VACUUM |
| IPC 数据存储 | IPC 通道和缓冲区的记录、查询、活动更新、统计，以及 `heapstore_ipc_send` / `heapstore_ipc_receive` 消息收发 |
| 内存数据存储 | 内存池和分配记录的记录、查询、更新、释放统计 |
| Token 计数 | Prompt/Completion/System/User/CacheHit 五类 Token 的使用统计与预算控制 |
| 批量写入 | 统一批量写入上下文，支持 Log/Trace/Session/Agent/Skill/MemoryPool/MemoryAlloc/IPCChannel/IPCBuffer/Span 十种数据类型 |
| 熔断器 | 基于失败计数的熔断器机制，保护下游存储免受级联故障 |
| 健康检查 | 各子系统（registry/trace/log/ipc/memory）独立健康状态检查 |
| 性能指标 | 收集并暴露总操作次数、失败次数、快慢路径次数、熔断触发次数、平均操作时间、峰值并发数 |
| 数据清理 | 基于保留天数的日志和追踪数据自动/手动清理 |

### 非职责（明确排除）

- 不负责 Agent 生命周期管理（由 Manager 负责）
- 不负责任务调度与编排（由 OpenLab 负责）
- 不负责配置校验与分发（由 Manager 负责）
- 不负责网络通信协议（由 protocols 层负责）
- 不负责业务语义验证（仅提供存储层的 CRUD 和统计）

## 2. 公共接口

### 头文件清单

| 头文件 | 说明 |
|--------|------|
| `include/heapstore.h` | 核心接口：初始化、路径管理、统计、熔断器、批量写入 |
| `include/heapstore_types.h` | 共享类型定义：Agent/Skill/Session 记录、内存池/分配、IPC 通道/缓冲区、Span/Trace、日志条目 |
| `include/heapstore_registry.h` | 注册表接口：Agent/Skill/Session 的 CRUD、查询、批量插入、迭代器、VACUUM |
| `include/heapstore_trace.h` | 追踪接口：Span 写入/查询/导出、导出器配置、清理 |
| `include/heapstore_log.h` | 日志接口：写入（printf 风格）、级别管理、轮转、清理、文件信息 |
| `include/heapstore_ipc.h` | IPC 接口：通道/缓冲区记录、查询、统计、消息收发 |
| `include/heapstore_memory.h` | 内存接口：内存池/分配记录、更新、统计 |
| `include/heapstore_token.h` | Token 接口：Token 记录、统计、预算设置与检查 |
| `include/heapstore_batch.h` | 批量写入接口：批量上下文、添加/提交/回滚/销毁 |
| `include/heapstore_integration.h` | 集成接口：与 syscall/telemetry/memory/corekern/logging 层的集成 API |

### 关键 API 签名

```c
// === 生命周期 ===
heapstore_error_t heapstore_init(const heapstore_config_t *config);
void heapstore_shutdown(void);
bool heapstore_is_initialized(void);

// === 路径管理 ===
const char *heapstore_get_root(void);
const char *heapstore_get_path(heapstore_path_type_t type);
heapstore_error_t heapstore_get_full_path(heapstore_path_type_t type, char *buffer, size_t buffer_size);

// === 日志写入（快/慢路径） ===
heapstore_error_t heapstore_log_write_fast(const char *service, int level, const char *message);
heapstore_error_t heapstore_log_write_slow(const char *service, int level, const char *message,
                                           const char *trace_id, uint32_t timeout_ms);

// === 追踪 ===
heapstore_error_t heapstore_trace_write_span(const heapstore_span_t *span);
heapstore_error_t heapstore_trace_query_by_trace(const char *trace_id, heapstore_span_t **spans, size_t *count);
heapstore_error_t heapstore_trace_export_to_json(char **out_json, bool include_events);

// === 注册表 CRUD ===
heapstore_error_t heapstore_registry_add_agent(const heapstore_agent_record_t *record);
heapstore_error_t heapstore_registry_get_agent(const char *id, heapstore_agent_record_t *record);
heapstore_error_t heapstore_registry_delete_agent(const char *id);
heapstore_error_t heapstore_registry_query_agents(const char *filter_type, const char *filter_status,
                                                  heapstore_registry_iter_t **iter);
heapstore_error_t heapstore_registry_batch_insert_agents(const heapstore_agent_record_t *records, size_t count);

// === 批量写入 ===
heapstore_batch_context_t *heapstore_batch_begin(size_t batch_size);
heapstore_error_t heapstore_batch_add_log(heapstore_batch_context_t *ctx, ...);
heapstore_error_t heapstore_batch_commit(heapstore_batch_context_t *ctx);
void heapstore_batch_context_destroy(heapstore_batch_context_t *ctx);

// === 运维 ===
heapstore_error_t heapstore_cleanup(bool dry_run, uint64_t *freed_bytes);
heapstore_error_t heapstore_flush(void);
heapstore_error_t heapstore_health_check(bool *registry_ok, bool *trace_ok, bool *log_ok,
                                         bool *ipc_ok, bool *memory_ok);
heapstore_error_t heapstore_get_metrics(heapstore_metrics_t *metrics);
heapstore_error_t heapstore_get_circuit_state(heapstore_circuit_info_t *info);
```

### 错误码

| 错误码 | 值 | 说明 |
|--------|-----|------|
| `heapstore_SUCCESS` | 0 | 操作成功 |
| `heapstore_ERR_INVALID_PARAM` | -1 | 无效参数 |
| `heapstore_ERR_NOT_INITIALIZED` | -2 | 未初始化 |
| `heapstore_ERR_ALREADY_INITIALIZED` | -3 | 已初始化 |
| `heapstore_ERR_DIR_CREATE_FAILED` | -4 | 目录创建失败 |
| `heapstore_ERR_DIR_NOT_FOUND` | -5 | 目录不存在 |
| `heapstore_ERR_PERMISSION_DENIED` | -6 | 权限不足 |
| `heapstore_ERR_OUT_OF_MEMORY` | -7 | 内存不足 |
| `heapstore_ERR_DB_INIT_FAILED` | -8 | 数据库初始化失败 |
| `heapstore_ERR_DB_QUERY_FAILED` | -9 | 数据库查询失败 |
| `heapstore_ERR_FILE_OPEN_FAILED` | -10 | 文件打开失败 |
| `heapstore_ERR_CONFIG_INVALID` | -11 | 配置无效 |
| `heapstore_ERR_NOT_FOUND` | -12 | 记录不存在 |
| `heapstore_ERR_FILE_OPERATION_FAILED` | -13 | 文件操作失败 |
| `heapstore_ERR_FILE_NOT_FOUND` | -14 | 文件不存在 |
| `heapstore_ERR_CIRCUIT_OPEN` | -15 | 熔断器开启 |
| `heapstore_ERR_TIMEOUT` | -16 | 操作超时 |
| `heapstore_ERR_NO_SPACE` | -17 | 磁盘空间不足 |
| `heapstore_ERR_NOT_SUPPORTED` | -18 | 不支持的操作 |
| `heapstore_ERR_INTERNAL` | -99 | 内部错误 |

## 3. 依赖关系

### 内部依赖

| 依赖模块 | 用途 |
|----------|------|
| `commons/platform/include/platform.h` | 平台抽象层（`airy_mutex_t` 等同步原语） |
| `airy_rt.h` | AgentRT 核心类型定义（`airy_err_t`、`AIRY_API`） |

### 运行时依赖

| 依赖 | 用途 |
|------|------|
| SQLite3 | 注册表数据库引擎 |
| 文件系统 | 日志、追踪文件持久化 |
| POSIX 线程 | 多线程并发控制 |

### 被依赖方

| 消费模块 | 使用接口 |
|----------|----------|
| syscall 层 | `heapstore_syscall_session_save/load/delete/list`、`heapstore_syscall_trace_save/export` |
| memory (built-in) 层 | `heapstore_memory_raw_save/load/delete` |
| corekern IPC 层 | `heapstore_ipc_channel_save/load` |
| commons logging 层 | `heapstore_logging_write` |
| Manager | `heapstore_get_stats`、`heapstore_get_metrics`、`heapstore_health_check`（监控集成） |

## 4. 配置参数

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `root_path` | `const char *` | (必填) | 数据分区根路径 |
| `max_log_size_mb` | `size_t` | — | 最大日志文件大小(MB) |
| `log_retention_days` | `int` | — | 日志保留天数 |
| `trace_retention_days` | `int` | — | 追踪数据保留天数 |
| `enable_auto_cleanup` | `bool` | — | 启用自动清理 |
| `enable_log_rotation` | `bool` | — | 启用日志轮转 |
| `enable_trace_export` | `bool` | — | 启用追踪导出 |
| `db_vacuum_interval_days` | `int` | — | 数据库 VACUUM 间隔(天) |
| `circuit_breaker_threshold` | `uint32_t` | — | 熔断器阈值（失败次数） |
| `circuit_breaker_timeout_sec` | `uint32_t` | — | 熔断器超时（秒） |

## 5. 跨团队接口合约

### 合约文件

| 合约 | 文件 | 说明 |
|------|------|------|
| 集成接口合约 | `include/heapstore_integration.h` | 定义 heapstore 与 AgentRT 核心模块（syscall/telemetry/memory/ipc/logging）的集成契约 |
| 类型合约 | `include/heapstore_types.h` | 所有子模块间的共享结构体类型定义，打破循环依赖 |

### 测试接口

| 测试文件 | 覆盖范围 |
|----------|----------|
| `tests/test_heapstore_core.c` | 核心初始化、路径管理、统计、熔断器 |
| `tests/test_heapstore_registry.c` | 注册表 CRUD、批量插入、迭代器 |
| `tests/test_heapstore_log.c` | 日志写入、轮转、清理 |
| `tests/test_heapstore_trace.c` | Span 写入、查询、导出 |
| `tests/test_heapstore_ipc.c` | IPC 通道/缓冲区记录 |
| `tests/test_heapstore_memory.c` | 内存池/分配记录 |
| `tests/test_heapstore_integration.c` | 与核心模块的集成测试 |
| `tests/test_heapstore_batch.c` | 批量写入 |
| `tests/test_batch_performance.c` | 批量写入性能 |
| `tests/test_edge_cases.c` | 边界条件 |
| `tests/test_security_path_traversal.c` | 路径遍历安全测试 |
| `tests/test_fuzzing_concurrency.c` | 并发模糊测试 |
| `tests/benchmark_heapstore.c` | 性能基准测试 |

## 6. 文件所有权

```
@owner: team-A
```

## 7. 变更记录

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v1.0.0 | 2026-06-18 | 初始版本，基于 heapstore 代码分析创建 | team-A |