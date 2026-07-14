# LLM Daemon 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-18 | **团队**: A（核心引擎）
> **代码路径**: `agentrt/daemon/llm_d/`

---

## 1. 职责边界

LLM Daemon 是 AgentRT 的大语言模型服务守护进程，屏蔽不同 LLM 提供商的 API 差异，提供统一的模型调用接口。它是 Agent 与外部 LLM 交互的关键桥梁。

### 核心职责

| 模块 | 职责 | 源文件 |
|------|------|--------|
| **Provider 管理** | 多提供商注册/查找/生命周期管理，适配 OpenAI、Anthropic、DeepSeek、Google、本地模型 | `src/providers/registry.c`, `provider.c`, `openai.c`, `anthropic.c`, `deepseek.c`, `google.c`, `local.c` |
| **LLM 路由** | 五种策略路由（round_robin / least_latency / quality_first / cost_aware / fallback），能力匹配，端点管理，降级切换 | `src/router/llm_router.c`, `cost_aware_router.c`, `round_robin_router.c`, `least_latency_router.c`, `quality_first_router.c` |
| **Token 计数** | 基于 tiktoken 编码的精确 Token 计数，支持多种模型编码 | `src/token_counter.c` |
| **成本追踪** | 按模型记录的输入/输出 Token 消耗与费用统计，支持可配置定价规则 | `src/cost_tracker.c` |
| **响应缓存** | LRU 缓存，基于请求内容的哈希键，可配置容量和 TTL | `src/cache.c` |
| **响应序列化** | JSON 格式的请求/响应序列化与反序列化 | `src/response.c` |
| **服务核心** | 编排 provider、router、cache、cost_tracker、token_counter，处理请求生命周期 | `src/service.c` |
| **服务适配器** | 将 LLM 服务适配到 AgentRT 统一服务管理框架（svc_common） | `src/llm_svc_adapter.c` |
| **守护进程入口** | JSON-RPC 2.0 服务端，Unix Socket / TCP 双模式，事件驱动框架，注册 `complete` 和 `complete_stream` 两个 RPC 方法 | `src/main.c` |

### 非职责（明确排除）

- 安全守卫/内容过滤（属于 Cupolas / daemon_security）
- 网络协议网关/认证（属于 gateway_d）
- 工具调用执行（属于 tool_d）
- Agent 认知循环（属于 CoreLoopThree）
- 持久化存储（属于 HeapStore）
- 内存管理/线程调度（属于 CoreKern）

---

## 2. 公共接口

### 2.1 头文件清单

| 头文件 | 用途 | 公开 API 数量 |
|--------|------|:---:|
| `include/llm_service.h` | LLM 服务对外接口（生命周期、complete、complete_stream、stats） | 7 |
| `include/llm_svc_adapter.h` | LLM 服务适配器接口（统一服务管理框架对齐） | 8 |
| `src/router/llm_router.h` | LLM 路由器公共接口（策略枚举、端点注册、路由查询、统计） | 7 |
| `src/cost_tracker.h` | 成本追踪接口（规则配置、添加记录、导出报告） | 4 |
| `src/token_counter.h` | Token 计数接口（创建编码器、计数） | 3 |
| `src/cache.h` | LRU 缓存接口（get/put/clear/size/capacity） | 6 |
| `src/response.h` | 响应序列化接口（JSON 双向转换） | 2 |
| `src/providers/provider.h` | Provider 适配器接口定义（ops 表、HTTP 工具、SSE 流式） | 12+ |
| `src/providers/registry.h` | Provider 注册表接口（创建/销毁/查找） | 4 |

### 2.2 关键 API 签名

```c
// ── 服务生命周期 ──
llm_service_t *llm_service_create(const char *config_path);
void llm_service_destroy(llm_service_t *svc);

// ── 请求接口 ──
int llm_service_complete(llm_service_t *svc, const llm_request_config_t *config,
                         llm_response_t **out_response);
int llm_service_complete_stream(llm_service_t *svc, const llm_request_config_t *config,
                                llm_stream_callback_t callback, void *callback_data,
                                llm_response_t **out_response);
void llm_response_free(llm_response_t *resp);

// ── 统计接口 ──
int llm_service_stats(llm_service_t *svc, char **out_json);

// ── 路由器 ──
int llm_router_init(const char *config_path);
void llm_router_destroy(void);
int llm_router_register_endpoint(const llm_endpoint_t *endpoint);
int llm_router_unregister_endpoint(const char *provider_name, const char *model_name);
int llm_router_route(const llm_route_request_t *request, llm_route_result_t *result);
int llm_router_get_stats(llm_router_stats_t *stats);
int llm_router_set_default_strategy(llm_route_strategy_t strategy);

// ── 成本追踪 ──
cost_tracker_t *cost_tracker_create(const pricing_rule_t *rules, int rule_count);
void cost_tracker_destroy(cost_tracker_t *ct);
void cost_tracker_add(cost_tracker_t *ct, const char *model, uint32_t prompt_tokens,
                      uint32_t completion_tokens);
cJSON *cost_tracker_export(cost_tracker_t *ct);

// ── Token 计数 ──
token_counter_t *token_counter_create(const char *encoding_name);
void token_counter_destroy(token_counter_t *tc);
size_t token_counter_count(token_counter_t *tc, const char *text);

// ── 缓存 ──
cache_t *cache_create(size_t capacity, int ttl_sec);
void cache_destroy(cache_t *cache);
int cache_get(cache_t *cache, const char *key, char **out_value);
void cache_put(cache_t *cache, const char *key, const char *value);
void cache_clear(cache_t *cache);

// ── Provider 注册表 ──
provider_registry_t *provider_registry_create(const service_config_t *cfg);
provider_registry_t *provider_registry_create_from_config(const service_config_t *cfg,
                                                          const char *config_path);
void provider_registry_destroy(provider_registry_t *reg);
const provider_t *provider_registry_find(provider_registry_t *reg, const char *model);

// ── 服务适配器 ──
airy_err_t llm_service_adapter_create(airy_service_t *out_service,
                                           const airy_svc_config_t *config);
airy_err_t llm_service_adapter_wrap(airy_service_t *out_service,
                                         llm_service_t llm_svc,
                                         const airy_svc_config_t *config);
llm_service_t llm_service_adapter_get_original(airy_service_t service);
airy_err_t llm_service_adapter_init(airy_service_t service);
airy_err_t llm_service_adapter_start(airy_service_t service);
airy_err_t llm_service_adapter_stop(airy_service_t service, bool force);
void llm_service_adapter_destroy(airy_service_t service);
airy_err_t llm_service_adapter_healthcheck(airy_service_t service);
```

### 2.3 路由策略枚举

| 策略 | 枚举值 | 说明 |
|------|:---:|------|
| `LLM_ROUTE_COMPLEXITY` | 0 | 基于任务复杂度自动选择模型 |
| `LLM_ROUTE_COST` | 1 | 成本优化路由（最低成本优先） |
| `LLM_ROUTE_LATENCY` | 2 | 延迟优化路由（最低延迟优先） |
| `LLM_ROUTE_FALLBACK` | 3 | 降级路由（主提供商失败时切换） |
| `LLM_ROUTE_ROUND_ROBIN` | 4 | 轮询路由（均匀分发） |

### 2.4 模型能力标志

| 标志 | 位 | 含义 |
|------|:---:|------|
| `LLM_CAP_CHAT` | 0x0001 | 对话 |
| `LLM_CAP_COMPLETION` | 0x0002 | 文本补全 |
| `LLM_CAP_EMBEDDING` | 0x0004 | 嵌入向量 |
| `LLM_CAP_FUNCTION_CALL` | 0x0008 | 函数调用 |
| `LLM_CAP_VISION` | 0x0010 | 视觉 |
| `LLM_CAP_STREAMING` | 0x0020 | 流式输出 |
| `LLM_CAP_JSON_MODE` | 0x0040 | JSON 模式 |
| `LLM_CAP_EXTENDED_THINK` | 0x0080 | 扩展思考（CoT） |
| `LLM_CAP_CODE_EXEC` | 0x0100 | 代码执行 |

### 2.5 JSON-RPC 2.0 方法

| 方法 | 说明 |
|------|------|
| `complete` | 非流式 LLM 补全 |
| `complete_stream` | 流式 LLM 补全（SSE） |

### 2.6 错误码

| 错误码 | 值 | 含义 |
|--------|:---:|------|
| `AIRY_SUCCESS` | 0 | 成功 |
| `AIRY_ERR_INVALID_PARAM` | — | 无效参数 |
| `AIRY_ERR_OUT_OF_MEMORY` | — | 内存不足 |
| `AIRY_ERR_OVERFLOW` | — | 消息数超限 |
| `AIRY_ERR_UNKNOWN` | — | 未知错误 |
| `JSONRPC_INTERNAL_ERROR` | — | JSON-RPC 内部错误 |
| `JSONRPC_INVALID_PARAMS` | — | JSON-RPC 无效参数 |
| `JSONRPC_PARSE_ERROR` | — | JSON-RPC 解析错误 |
| `JSONRPC_INVALID_REQUEST` | — | JSON-RPC 无效请求 |

---

## 3. 依赖关系

### 3.1 内部依赖（编译时）

```
llm_d
  ├── airy_common (commons 公共库)
  │    ├── platform/          — platform.h, airy_sleep_ms
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
       └── daemon_security    — 输入清洗和权限检查
```

### 3.2 运行时依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| libcurl (libcurl) | 系统 | HTTPS 调用外部 LLM API |
| cJSON (libcjson) | 系统 | JSON 解析与构造 |
| libyaml | 系统 | YAML 配置文件解析 |
| POSIX 线程 (libpthread) | 系统 | 线程互斥锁 |
| tiktoken (可选) | 系统 | 精确 Token 计数（`HAVE_TIKTOKEN` 宏控制） |
| 外部 LLM API | 网络 | OpenAI / Anthropic / DeepSeek / Google |

### 3.3 被依赖方

| 消费者 | 使用接口 | 说明 |
|--------|---------|------|
| CoreLoopThree | `llm_service_complete` / `llm_service_complete_stream` | Agent 认知循环中的 LLM 推理 |
| gateway_d | JSON-RPC 2.0 `complete` / `complete_stream` | 外部请求转发 |
| Cupolas | daemon_security 集成 | 输入清洗 |
| 所有 Agent | `llm_service.h` 公共接口 | 文本生成/对话 |

---

## 4. 配置参数

### 4.1 守护进程配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `daemon.socket_path` | string | `/var/run/agentrt/llm.sock` | Unix Socket 路径 |
| `daemon.tcp_port` | uint16 | 8080 | TCP 监听端口（启用 TCP 时） |
| `daemon.max_threads` | int | 8 | 最大线程数 |
| `daemon.max_clients` | int | 64 | 最大客户端连接数 |

### 4.2 服务配置 (service_config_t)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `cache_capacity` | size_t | — | LRU 缓存容量 |
| `cache_ttl_sec` | uint32_t | — | 缓存条目 TTL（秒） |
| `max_retries` | int | 3 | API 调用最大重试次数 |
| `timeout_ms` | uint32_t | — | 请求超时（毫秒） |
| `token_encoding` | string | — | Token 编码名称（如 "cl100k_base"） |
| `providers[].name` | string | — | 提供商名称 |
| `providers[].enabled` | string | — | 是否启用 |

### 4.3 Provider 配置 (provider_config_t)

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 提供商名称 |
| `api_key` | string | API Key（从环境变量获取） |
| `api_base` | string | API 基础 URL |
| `organization` | string | 组织 ID（OpenAI 等） |
| `timeout_sec` | double | 请求超时（秒） |
| `max_retries` | int | 最大重试次数 |
| `models` | string[] | 支持的模型列表 |

### 4.4 路由器端点配置 (llm_endpoint_t)

| 参数 | 类型 | 说明 |
|------|------|------|
| `provider_name` | char[64] | 提供商名称 |
| `model_name` | char[64] | 模型名称 |
| `endpoint` | char[256] | API 端点 URL |
| `api_key_env` | char[64] | API Key 环境变量名 |
| `capabilities` | uint32_t | 能力位掩码 (llm_capability_t) |
| `context_window` | uint32_t | 上下文窗口大小 |
| `cost_per_1k_input` | double | 输入每 1K token 成本 (USD) |
| `cost_per_1k_output` | double | 输出每 1K token 成本 (USD) |
| `avg_latency_ms` | uint32_t | 平均延迟 (ms) |
| `rate_limit_rpm` | uint32_t | 速率限制 (请求/分钟) |
| `enabled` | bool | 是否启用 |
| `priority` | int | 优先级 |

---

## 5. 跨团队接口合约

### 5.1 合约文件

- `contracts/contract_A_B.h` 第3节 — 协议路由表（团队A llm_d 与 团队B 的接口合约）

### 5.2 测试接口

| 函数 | 用途 | 消费者 |
|------|------|--------|
| `llm_service_create()` | 创建 LLM 服务实例 | 测试/集成 |
| `llm_service_complete()` | 非流式调用 | 测试/集成 |
| `llm_service_complete_stream()` | 流式调用 | 测试/集成 |
| `llm_service_stats()` | 获取统计信息 | 测试/监控 |
| `llm_router_get_stats()` | 获取路由器统计 | 测试/基准测试 |
| `cost_tracker_export()` | 导出成本报告 | 测试/监控 |
| `token_counter_count()` | Token 计数 | 测试/验证 |
| `cache_size()` / `cache_capacity()` | 缓存统计 | 测试/监控 |

---

## 6. 文件所有权

```
@owner: team-A
```

所有 `agentrt/daemon/llm_d/` 下的文件归属于团队A。团队C 仅可修改 `tests/` 目录下的测试文件。

---

## 7. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-06-18 | 初始版本，基于代码现状 |