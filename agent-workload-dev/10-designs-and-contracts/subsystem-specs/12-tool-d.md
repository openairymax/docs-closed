# Tool Daemon 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-18 | **团队**: A（核心引擎）
> **代码路径**: `agentrt/daemons/tool_d/`

---

## 1. 职责边界

Tool Daemon 是 AgentRT 的工具执行守护进程，负责外部工具的注册、发现、安全执行和结果管理。它在沙箱环境中执行工具代码，通过 Cupolas SafetyGuard 进行权限检查和安全控制，是 Agent 与外部世界交互的关键执行层。

### 核心职责

| 模块 | 职责 | 源文件 |
|------|------|--------|
| **工具注册与发现** | 动态注册/注销外部工具，管理工具元数据（ID、名称、可执行文件、参数定义、权限规则） | `src/registry.c` |
| **工具执行（沙箱）** | 在沙箱环境中执行工具代码，超时控制，标准输出/错误捕获，进程退出码，执行耗时统计，支持同步和异步模式 | `src/executor.c` |
| **参数校验** | 基于 JSON Schema 的参数类型和格式校验，必填参数检查 | `src/validator.c` |
| **权限审批** | 工具执行前的参数净化、权限检查、SafetyGuard 链式检查、审计日志记录 | `src/tool_approval.c`, `include/tool_approval.h` |
| **SafetyGuard 桥接** | 桥接 Cupolas 安全穹顶的 6 种守卫类型（PERMISSION / RATE_LIMIT / CONTENT_FILTER / INPUT / RESOURCE / AUDIT）到工具审批流程 | `src/safety_guard_bridge.c`, `include/safety_guard_bridge.h` |
| **结果缓存** | 基于工具 ID + 参数哈希的缓存键，LRU 缓存，可配置容量和 TTL，仅缓存标记为可缓存的工具结果 | `src/cache.c` |
| **配置管理** | 工具定义、缓存容量、执行器线程池、沙箱类型（process / container）的配置加载 | `src/config.c` |
| **服务核心** | 编排 registry、executor、validator、cache、approval，处理请求生命周期 | `src/service.c` |
| **服务适配器** | 将工具服务适配到 AgentRT 统一服务管理框架（svc_common） | `src/tool_svc_adapter.c` |
| **守护进程入口** | JSON-RPC 2.0 服务端，Unix Socket / TCP 双模式，事件驱动框架，注册 `register`、`list_tools`、`get_tool`、`execute_tool` 四个 RPC 方法 | `src/main.c` |
| **工具辅助函数** | ID 校验、名称净化、版本解析 | `src/utils/tool_helpers.c` |

### 非职责（明确排除）

- AI/LLM 推理逻辑（属于 CoreLoopThree / llm_d）
- 安全守卫规则定义（属于 Cupolas，tool_d 仅通过桥接层调用）
- 网络协议处理/认证（属于 gateway_d）
- 内存管理/线程调度（属于 CoreKern）
- 持久化存储（属于 HeapStore）
- 工具二进制文件的开发和维护（属于工具提供方）

---

## 2. 公共接口

### 2.1 头文件清单

| 头文件 | 用途 | 公开 API 数量 |
|--------|------|:---:|
| `include/tool_service.h` | 工具服务对外接口（生命周期、注册/注销、查询、执行、流式执行） | 10 |
| `include/tool_svc_adapter.h` | 工具服务适配器接口（统一服务管理框架对齐） | 8 |
| `include/tool_approval.h` | 工具审批接口（参数净化、权限检查、SafetyGuard 链式检查、审计日志） | 5 |
| `include/safety_guard_bridge.h` | SafetyGuard 桥接层接口（6 种守卫类型检查、审计日志） | 7 |
| `src/registry.h` | 工具注册表内部接口（添加/删除/查找/列表） | 5 |
| `src/executor.h` | 工具执行器接口（同步/异步执行、审批上下文设置） | 5 |
| `src/validator.h` | 工具参数验证器接口（JSON Schema 校验） | 3 |
| `src/cache.h` | 工具结果缓存接口（get/put/clear/key 生成/JSON 序列化） | 6 |
| `src/config.h` | 工具配置结构（工具定义、缓存、执行器、沙箱类型） | 2 |
| `src/utils/tool_helpers.h` | 工具辅助函数（ID 校验、名称净化、版本解析） | 3 |
| `src/utils/tool_errors.h` | 工具服务错误码定义 | 8 |

### 2.2 关键 API 签名

```c
// ── 服务生命周期 ──
tool_service_t *tool_service_create(const char *config_path);
void tool_service_destroy(tool_service_t *svc);

// ── 工具管理 ──
int tool_service_register(tool_service_t *svc, const tool_metadata_t *meta);
int tool_service_unregister(tool_service_t *svc, const char *tool_id);
tool_metadata_t *tool_service_get(tool_service_t *svc, const char *tool_id);
void tool_metadata_free(tool_metadata_t *meta);
char *tool_service_list(tool_service_t *svc);  // 返回 JSON 数组

// ── 工具执行 ──
int tool_service_execute(tool_service_t *svc, const tool_execute_request_t *req,
                         tool_result_t **out_result);
int tool_service_execute_stream(tool_service_t *svc, const tool_execute_request_t *req,
                                tool_stream_callback_t callback, void *callback_data,
                                tool_result_t **out_result);
void tool_result_free(tool_result_t *res);

// ── 审批 ──
tool_approval_ctx_t *tool_approval_create(const tool_approval_config_t *cfg);
void tool_approval_destroy(tool_approval_ctx_t *ctx);
int tool_approval_check(tool_approval_ctx_t *ctx, const tool_metadata_t *meta,
                        const char *params_json, tool_approval_detail_t *detail);
int tool_approval_sanitize_params(tool_approval_ctx_t *ctx, const char *tool_name,
                                  const char *params_json, char *sanitized_params,
                                  size_t sanitized_size);
void tool_approval_get_stats(tool_approval_ctx_t *ctx, uint64_t *out_total_checks,
                             uint64_t *out_denied_count, uint64_t *out_sanitized_count);

// ── SafetyGuard 桥接 ──
safety_guard_bridge_t *safety_guard_bridge_create(const safety_guard_bridge_config_t *config);
void safety_guard_bridge_destroy(safety_guard_bridge_t *bridge);
int safety_guard_bridge_check(safety_guard_bridge_t *bridge,
                              const tool_metadata_t *meta,
                              const char *params_json,
                              safety_guard_bridge_result_t *result);
int safety_guard_bridge_check_permission(safety_guard_bridge_t *bridge,
                                         const char *agent_id,
                                         const char *tool_name,
                                         const char *action);
int safety_guard_bridge_check_rate_limit(safety_guard_bridge_t *bridge,
                                         const char *tool_name);
int safety_guard_bridge_filter_content(safety_guard_bridge_t *bridge,
                                       const char *params_json,
                                       char *sanitized_params,
                                       size_t sanitized_size);
int safety_guard_bridge_audit_log(safety_guard_bridge_t *bridge,
                                  const char *event_type, const char *tool_name,
                                  int decision, const char *reason, const char *agent_id);
void safety_guard_bridge_get_stats(safety_guard_bridge_t *bridge,
                                   uint64_t *out_total_checks,
                                   uint64_t *out_denied_count,
                                   uint64_t *out_rate_limited);

// ── 执行器 ──
tool_executor_t *tool_executor_create(const tool_executor_config_t *cfg);
tool_executor_t *tool_executor_create_ex(const tool_executor_config_t *ecfg);
void tool_executor_destroy(tool_executor_t *exec);
int tool_executor_run(tool_executor_t *exec, const tool_metadata_t *meta,
                      const char *params_json, tool_result_t **out_result);
int tool_executor_run_async(tool_executor_t *exec, const tool_metadata_t *meta,
                            const char *params_json, tool_execute_callback_t callback,
                            void *user_data, tool_result_t **out_result);
void tool_executor_set_approval_ctx(tool_executor_t *exec, tool_approval_ctx_t *approval_ctx);

// ── 验证器 ──
tool_validator_t *tool_validator_create(void);
void tool_validator_destroy(tool_validator_t *val);
int tool_validator_validate(tool_validator_t *val, const tool_metadata_t *meta,
                            const char *params_json);

// ── 注册表 ──
tool_registry_t *tool_registry_create(const tool_config_t *cfg);
void tool_registry_destroy(tool_registry_t *reg);
int tool_registry_add(tool_registry_t *reg, const tool_metadata_t *meta);
tool_metadata_t *tool_registry_get(tool_registry_t *reg, const char *tool_id);
char *tool_registry_list_json(tool_registry_t *reg);

// ── 缓存 ──
tool_cache_t *tool_cache_create(size_t capacity, int ttl_sec);
void tool_cache_destroy(tool_cache_t *cache);
int tool_cache_get(tool_cache_t *cache, const char *key, char **out_value);
void tool_cache_put(tool_cache_t *cache, const char *key, const char *value);
void cache_clear(tool_cache_t *cache);
char *tool_cache_key(const char *tool_id, const char *params_json);
char *tool_result_to_json(const tool_result_t *res);
tool_result_t *tool_result_from_json(const char *json);

// ── 服务适配器 ──
airy_err_t tool_service_adapter_create(airy_service_t *out_service,
                                            const airy_svc_config_t *config);
airy_err_t tool_service_adapter_wrap(airy_service_t *out_service,
                                          tool_service_t tool_svc,
                                          const airy_svc_config_t *config);
tool_service_t tool_service_adapter_get_original(airy_service_t service);
airy_err_t tool_service_adapter_init(airy_service_t service);
airy_err_t tool_service_adapter_start(airy_service_t service);
airy_err_t tool_service_adapter_stop(airy_service_t service, bool force);
void tool_service_adapter_destroy(airy_service_t service);
airy_err_t tool_service_adapter_healthcheck(airy_service_t service);
```

### 2.3 JSON-RPC 2.0 方法

| 方法 | 说明 |
|------|------|
| `register` | 注册新工具（id / name / executable / description / params / timeout_sec / cacheable / permission_rule） |
| `list_tools` | 列出所有已注册工具（返回 JSON 数组） |
| `get_tool` | 查询单个工具详细信息（参数：tool_id） |
| `execute_tool` | 执行工具调用（参数：tool_id + params JSON） |

### 2.4 SafetyGuard 守卫类型

| 守卫类型 | 说明 | 桥接接口 |
|----------|------|----------|
| `SAFETY_GUARD_PERMISSION` | RBAC 权限检查 | `safety_guard_bridge_check_permission()` |
| `SAFETY_GUARD_RATE_LIMIT` | 工具调用频率限制 | `safety_guard_bridge_check_rate_limit()` |
| `SAFETY_GUARD_CONTENT_FILTER` | 输入内容过滤 | `safety_guard_bridge_filter_content()` |
| `SAFETY_GUARD_INPUT` | 参数净化 | `safety_guard_bridge_check()` 内部 |
| `SAFETY_GUARD_RESOURCE` | 资源配额检查 | `safety_guard_bridge_check()` 内部 |
| `SAFETY_GUARD_AUDIT` | 审计日志记录 | `safety_guard_bridge_audit_log()` |

### 2.5 审批决策结果

| 决策 | 枚举值 | 说明 |
|------|:---:|------|
| `TOOL_APPROVAL_ALLOWED` | 0 | 批准执行 |
| `TOOL_APPROVAL_DENIED` | 1 | 拒绝执行 |
| `TOOL_APPROVAL_SANITIZED` | 2 | 已净化参数，批准执行 |
| `TOOL_APPROVAL_PENDING_AUDIT` | 3 | 需人工审核 |

### 2.6 错误码

| 错误码 | 值 | 含义 |
|--------|:---:|------|
| `TOOL_ERR_NOT_FOUND` | 3101 | 工具未找到 |
| `TOOL_ERR_INVALID_PARAMS` | 3102 | 无效参数 |
| `TOOL_ERR_PERMISSION_DENIED` | 3103 | 权限拒绝 |
| `TOOL_ERR_EXEC_FAILED` | 3104 | 执行失败 |
| `TOOL_ERR_TIMEOUT` | 3105 | 执行超时 |
| `TOOL_ERR_NOT_IMPLEMENTED` | 3106 | 未实现 |
| `TOOL_ERR_IO` | 3107 | I/O 错误 |
| `TOOL_ERR_FORK` | 3108 | Fork 失败 |

---

## 3. 依赖关系

### 3.1 内部依赖（编译时）

```
tool_d
  ├── airy_common (commons 公共库)
  │    ├── platform/          — platform.h
  │    ├── utils/memory/      — memory_compat.h, AIRY_MALLOC/FREE/STRDUP
  │    ├── utils/error/       — error.h
  │    ├── utils/logging/     — logging.h, logging_compat.h
  │    ├── utils/sync/        — sync_compat.h, airy_mutex_t
  │    ├── utils/atomic/      — atomic_compat.h
  │    ├── utils/cache/       — 缓存基础设施
  │    ├── utils/network/     — airy_socket_t, airy_socket_*
  │    └── utils/ipc/         — ipc_service_bus
  ├── svc_common (daemon 通用服务层)
  │    ├── svc_logger         — SVC_LOG_* 宏
  │    ├── method_dispatcher  — JSON-RPC 方法分发
  │    ├── jsonrpc_helpers    — JSONRPC_SEND_* 宏
  │    ├── daemon_event_driver— 事件驱动框架
  │    ├── daemon_bootstrap_sd — 服务发现注册
  │    ├── daemon_bootstrap_ipc — IPC 总线注册
  │    ├── param_validator    — 参数校验
  │    └── thread_pool        — 线程池
  └── cupolas
       ├── daemon_security    — 输入清洗、权限检查、审计日志
       └── safety_guard       — safety_guard_check_chain() API
```

### 3.2 运行时依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| cJSON (libcjson) | 系统 | JSON 解析与构造 |
| libyaml | 系统 | YAML 配置文件解析 |
| POSIX 线程 (libpthread) | 系统 | 线程互斥锁 |
| 工具可执行文件 | 文件系统 | 在沙箱中执行的工具二进制文件 |

### 3.3 被依赖方

| 消费者 | 使用接口 | 说明 |
|--------|---------|------|
| CoreLoopThree | `tool_service_execute` / `tool_service_register` | Agent 认知循环中的工具调用 |
| gateway_d | JSON-RPC 2.0 `register` / `execute_tool` / `list_tools` / `get_tool` | 外部请求转发 |
| Cupolas | SafetyGuard 桥接层 | 安全守卫检查 |
| 所有 Agent | `tool_service.h` 公共接口 | 工具注册与执行 |

---

## 4. 配置参数

### 4.1 守护进程配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `daemon.socket_path` | string | `/var/run/agentrt/tool.sock` | Unix Socket 路径 |
| `daemon.tcp_port` | uint16 | 8081 | TCP 监听端口（启用 TCP 时） |
| `daemon.max_clients` | int | 64 | 最大客户端连接数 |

### 4.2 工具服务配置 (tool_config_t)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `tools[]` | tool_def_t[] | — | 内置工具定义数组（以 `name == NULL` 结尾） |
| `cache_capacity` | size_t | — | 结果缓存容量 |
| `cache_ttl_sec` | int | — | 缓存条目 TTL（秒） |
| `executor_workers` | int | — | 执行器线程池大小 |
| `workbench_type` | string | — | 沙箱类型：`"process"` 或 `"container"` |
| `container_image` | string | — | 默认容器镜像（workbench_type=container 时） |

### 4.3 工具定义 (tool_def_t)

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 工具名称 |
| `executable` | string | 可执行文件路径或命令 |
| `params[]` | string[] | 参数模式定义（可选） |
| `timeout_sec` | int | 执行超时（秒） |
| `cacheable` | int | 结果是否可缓存（0/1） |
| `permission_rule` | string | 权限规则标识（与 Cupolas 配合） |

### 4.4 工具元数据 (tool_metadata_t)

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 工具唯一标识 |
| `name` | string | 工具名称 |
| `description` | string | 描述 |
| `executable` | string | 可执行文件路径或命令 |
| `params[].name` | string | 参数名 |
| `params[].schema` | string | JSON Schema 片段 |
| `param_count` | size_t | 参数数量 |
| `timeout_sec` | int | 执行超时（秒） |
| `cacheable` | int | 结果是否可缓存（0/1） |
| `permission_rule` | string | 权限规则标识 |

### 4.5 审批配置 (tool_approval_config_t)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `agent_id` | string | — | 请求 Agent ID |
| `enable_safety_guard_chain` | bool | false | 是否启用 SafetyGuard 链式检查 |
| `enable_audit_logging` | bool | false | 是否记录审计日志 |
| `permission_rules` | string | NULL | 权限规则 JSON（NULL 使用默认） |

### 4.6 SafetyGuard 桥接配置 (safety_guard_bridge_config_t)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `enable_permission_guard` | bool | true | 启用权限守卫 |
| `enable_rate_limit_guard` | bool | true | 启用速率限制守卫 |
| `enable_content_filter` | bool | true | 启用内容过滤守卫 |
| `enable_input_sanitization` | bool | true | 启用输入净化守卫 |
| `enable_resource_quota` | bool | true | 启用资源配额守卫 |
| `enable_audit_guard` | bool | true | 启用审计守卫 |
| `rate_limit_per_minute` | uint32_t | 0 | 每分钟最大调用次数（0=无限制） |
| `max_params_size` | uint32_t | 0 | 最大参数大小（字节，0=无限制） |
| `denied_patterns` | string | NULL | 禁止的参数模式（逗号分隔） |
| `agent_id` | string | — | Agent ID |

---

## 5. 跨团队接口合约

### 5.1 合约文件

- `contracts/contract_A_B.h` — 团队A(tool_d) 与 团队B 的接口合约
- 审批流程集成点位于 `executor.c` 的 `tool_executor_run()` 中

### 5.2 测试接口

| 函数 | 用途 | 消费者 |
|------|------|--------|
| `tool_service_create()` | 创建工具服务实例 | 测试/集成 |
| `tool_service_register()` | 注册工具 | 测试/集成 |
| `tool_service_execute()` | 执行工具 | 测试/集成 |
| `tool_service_list()` | 列出工具 | 测试/验证 |
| `tool_service_get()` | 获取工具元数据 | 测试/验证 |
| `tool_validator_validate()` | 参数校验 | 测试/验证 |
| `tool_approval_check()` | 审批检查 | 测试/安全测试 |
| `tool_approval_get_stats()` | 审批统计 | 测试/监控 |
| `safety_guard_bridge_check()` | 守卫链检查 | 测试/安全测试 |
| `safety_guard_bridge_get_stats()` | 桥接层统计 | 测试/监控 |
| `tool_cache_get()` / `tool_cache_put()` | 缓存操作 | 测试/验证 |

---

## 6. 文件所有权

```
@owner: team-A
```

所有 `agentrt/daemons/tool_d/` 下的文件归属于团队A。团队C 仅可修改 `tests/` 目录下的测试文件。

---

## 7. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-06-18 | 初始版本，基于代码现状 |