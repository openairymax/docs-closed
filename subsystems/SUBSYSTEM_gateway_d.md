# Gateway Daemon 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-17 | **团队**: A（核心引擎）
> **代码路径**: `agentos/daemon/gateway_d/`

---

## 1. 职责边界

Gateway Daemon（gateway_d）是 AgentRT 的 API 网关守护进程，作为整个系统的流量入口，负责将外部客户端的 HTTP/WebSocket/Stdio 请求转换为内部 JSON-RPC 2.0 调用，并路由到对应的服务守护进程。它是外部世界与 AgentRT 内部服务之间的唯一入口点，承担协议转换、请求路由、连接管理、限流熔断和 TLS 终止等核心职责。

### 核心职责

| 模块 | 职责 | 源文件 |
|------|------|--------|
| **网关服务核心** | 管理 HTTP/WebSocket/Stdio 三种网关实例的生命周期（create/init/start/stop/destroy），配置加载，状态查询，健康检查 | `src/service.c` (`gateway_service.h`) |
| **服务适配器** | 将网关服务包装为统一的 AgentOS 服务管理框架接口，支持服务注册表、服务发现、统一生命周期管理 | `src/gateway_svc_adapter.c` (`gateway_svc_adapter.h`) |
| **协议路由** | 根据请求的 Content-Type + Path + Body 自动检测协议类型（MCP/A2A/OpenAI/JSON-RPC），分发到对应协议处理器 | `src/protocol/gateway_protocol_router.c` (`gateway_protocol_router.h`) |
| **MCP 服务端** | Model Context Protocol 服务端实现，允许 MCP 客户端通过网关与 AgentRT 后端服务交互 | `src/protocol/gateway_mcp_server.c` |
| **A2A 处理器** | Agent-to-Agent 协议处理，支持 Agent 间通信 | `src/protocol/gateway_a2a_handler.c` |
| **OpenAI 兼容层** | OpenAI API 兼容处理，支持 Chat/Completions 等端点，将 OpenAI 格式请求转换为内部协议 | `src/protocol/gateway_openai_compat.c` |
| **请求转发** | 外部 HTTP 请求 → gateway → gateway_d → 协议路由 → 目标 daemon 的完整转发链路，支持 A2A/MCP/OpenAI/JSON-RPC 四种协议路径 | `src/gateway_forward.c` (`gateway_forward.h`) |
| **守护进程入口** | 进程启动、配置解析、信号处理、优雅关闭 | `src/main.c` |

### 通信架构

```
外部客户端 (HTTP/WS/MCP/A2A/OpenAI)
       │
       ▼
  gateway_d (守护进程)
       │
       ├─→ gateway_svc_adapter  ← 请求解析与协议转换
       ├─→ gateway_service      ← 核心服务逻辑（路由、限流、鉴权）
       ├─→ gw_proto_router      ← 多协议路由分发
       ├─→ gw_forward           ← 协议转发到目标 daemon
       │
       ▼
  IPC Service Bus (JSON-RPC 2.0)
       │
       ├─→ sched_d (A2A)
       ├─→ tool_d (MCP)
       ├─→ llm_d (OpenAI)
       └─→ sched_d (JSON-RPC)
```

### 协议路由表

| 协议类型 | 检测条件 | 目标 daemon | IPC 通道 |
|----------|---------|------------|----------|
| A2A | Agent-to-Agent 协议特征 | `sched_d` | `a2a` |
| MCP | Model Context Protocol 特征 | `tool_d` | `mcp` |
| OpenAI API | OpenAI API 格式请求 | `llm_d` | `llm` |
| JSON-RPC | 通用 JSON-RPC 2.0 | `sched_d` | `sched` |

### 非职责（明确排除）

- 不负责 LLM 推理（属于 llm_d）
- 不负责工具执行（属于 tool_d）
- 不负责 Agent 市场管理（属于 market_d）
- 不负责底层协议转换实现（属于 `agentos/gateway/` 协议转换层）
- 不负责输入净化/网络安全过滤（属于 Cupolas）
- 不负责系统调用实现（属于 `agentos/atoms/syscall/`）

---

## 2. 公共接口

### 2.1 头文件清单

| 头文件 | 用途 | 公开 API 数量 |
|--------|------|:---:|
| `gateway_service.h` | 网关服务核心接口：生命周期/状态查询/配置管理 | 11 |
| `gateway_svc_adapter.h` | 服务适配器：统一服务框架集成/注册/配置重载 | 16 |
| `gateway_forward.h` | 协议转发器：转发创建/协议检测/请求转发/统计 | 12 |
| `gateway_protocol_router.h` | 协议路由器：路由创建/协议检测/注册/路由分发/统计 | 10 |

### 2.2 关键 API 签名

```c
// === 网关服务生命周期 (gateway_service.h) ===

// 创建/销毁
agentos_error_t gateway_service_create(gateway_service_t *service,
                                       const gateway_service_config_t *config);
void gateway_service_destroy(gateway_service_t service);

// 生命周期
agentos_error_t gateway_service_init(gateway_service_t service);
agentos_error_t gateway_service_start(gateway_service_t service);
agentos_error_t gateway_service_stop(gateway_service_t service, bool force);

// 状态查询
agentos_svc_state_t gateway_service_get_state(gateway_service_t service);
bool gateway_service_is_running(gateway_service_t service);
agentos_error_t gateway_service_get_stats(gateway_service_t service,
                                          agentos_svc_stats_t *stats);
agentos_error_t gateway_service_healthcheck(gateway_service_t service);

// 配置管理
agentos_error_t gateway_service_load_config(gateway_service_config_t *config,
                                            const char *config_path);
void gateway_service_get_default_config(gateway_service_config_t *config);

// === 服务适配器 (gateway_svc_adapter.h) ===

// 创建/包装
agentos_error_t gateway_service_adapter_create(agentos_service_t *out_service,
                                               const agentos_svc_config_t *config);
agentos_error_t gateway_service_adapter_wrap(agentos_service_t *out_service,
                                             gateway_service_t gateway_svc,
                                             const agentos_svc_config_t *config);
agentos_error_t gateway_service_adapter_create_from_config(
    agentos_service_t *out_service, const char *config_path);

// 生命周期
agentos_error_t gateway_service_adapter_init(agentos_service_t service);
agentos_error_t gateway_service_adapter_start(agentos_service_t service);
agentos_error_t gateway_service_adapter_stop(agentos_service_t service, bool force);
void gateway_service_adapter_destroy(agentos_service_t service);

// 查询
agentos_error_t gateway_service_adapter_healthcheck(agentos_service_t service);
agentos_svc_state_t gateway_service_adapter_get_state(agentos_service_t service);
bool gateway_service_adapter_is_running(agentos_service_t service);
agentos_error_t gateway_service_adapter_get_stats(agentos_service_t service,
                                                  agentos_svc_stats_t *stats);
gateway_service_t gateway_service_adapter_get_original(agentos_service_t service);

// 注册/配置
agentos_error_t gateway_service_adapter_register(agentos_service_t service);
agentos_error_t gateway_service_adapter_unregister(agentos_service_t service);
agentos_error_t gateway_service_adapter_reload_config(agentos_service_t service,
                                                      const char *config_path);
agentos_error_t gateway_service_adapter_set_type_enabled(
    agentos_service_t service, gateway_daemon_type_t type, bool enabled);
bool gateway_service_adapter_supports_type(agentos_service_t service,
                                           gateway_daemon_type_t type);

// === 协议路由 (gateway_protocol_router.h) ===

gw_proto_router_t *gw_proto_router_create(void);
void gw_proto_router_destroy(gw_proto_router_t *router);
int gw_proto_router_init(gw_proto_router_t *router);
int gw_proto_router_shutdown(gw_proto_router_t *router);

// 协议检测
gw_proto_detect_result_t gw_proto_detect(const char *content_type,
                                         const char *path, const char *body);

// 路由注册与分发
int gw_proto_router_register(gw_proto_router_t *router,
                             gw_proto_detect_result_t proto_type,
                             gw_proto_request_handler_t handler, void *user_data);
int gw_proto_router_route(gw_proto_router_t *router,
                          gw_proto_detect_result_t proto_type,
                          const char *method, const char *path,
                          const char *body_json, char **response_json);
int gw_proto_router_route_auto(gw_proto_router_t *router,
                               const char *content_type, const char *method,
                               const char *path, const char *body_json,
                               char **response_json);

// 统计
int gw_proto_router_get_stats(gw_proto_router_t *router,
                              gw_proto_router_stats_t *stats);
bool gw_proto_router_is_healthy(gw_proto_router_t *router);

// === 协议转发 (gateway_forward.h) ===

gw_forward_t *gw_forward_create(const gw_forward_config_t *config);
void gw_forward_destroy(gw_forward_t *fw);

// 转发
int gw_forward_request(gw_forward_t *fw, gw_fwd_proto_t proto,
                       const char *method, const char *path,
                       const char *body, size_t body_len,
                       char **out_response, size_t *out_response_len);
int gw_forward_a2a(gw_forward_t *fw, const char *method, const char *path,
                   const char *body, size_t body_len,
                   char **out_response, size_t *out_response_len);
int gw_forward_mcp(gw_forward_t *fw, const char *method, const char *path,
                   const char *body, size_t body_len,
                   char **out_response, size_t *out_response_len);
int gw_forward_openai(gw_forward_t *fw, const char *method, const char *path,
                      const char *body, size_t body_len,
                      char **out_response, size_t *out_response_len);

// 协议检测
gw_fwd_proto_t gw_forward_detect_proto(const char *content_type,
                                       const char *path, const char *body,
                                       size_t body_len);

// 统计
int gw_forward_get_stats(gw_forward_t *fw, gw_forward_stats_t *stats);
void gw_forward_reset_stats(gw_forward_t *fw);
bool gw_forward_is_healthy(gw_forward_t *fw);
```

### 2.3 错误码

| 错误码 | 含义 |
|--------|------|
| `AGENTOS_SUCCESS` (0) | 成功 |
| `AGENTOS_EINVAL` | 无效参数 |
| `AGENTOS_ENOMEM` | 内存不足 |
| `AGENTOS_ENOTINIT` | 未初始化 |
| `AGENTOS_EBUSY` | 服务忙 |
| `AGENTOS_ERR_OUT_OF_MEMORY` | 内存不足（OOM） |

---

## 3. 依赖关系

### 3.1 内部依赖（编译时）

```
daemon/gateway_d/
  ├── daemon/common/                    — svc_common.h, svc_logger, svc_config, svc_auth
  ├── daemon/common/ipc/                — ipc_service_bus（IPC 服务总线）
  ├── daemon/common/                     — method_dispatcher, jsonrpc_helpers, circuit_breaker
  ├── agentos/gateway/                  — 底层协议转换层（HTTP/WS/Stdio 实现）
  ├── agentos/protocols/                — 协议适配器（MCP/A2A/OpenAI）
  ├── agentos/atoms/syscall/            — 系统调用接口
  ├── agentos/commons/utils/memory/     — 统一内存管理（Arena 分配器用于请求处理路径）
  └── agentos/commons/utils/compliance/ — banned_functions.h（通过 CMake -include 注入）
```

### 3.2 运行时依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| POSIX 线程 (libpthread) | 系统 | 服务线程管理 |
| 网络栈 (socket) | 系统 | HTTP/WebSocket 网络监听 |
| IPC 服务总线 | 运行时 | 与后端 daemon 通信（JSON-RPC 2.0） |

### 3.3 被依赖方

| 消费者 | 使用接口 | 说明 |
|--------|---------|------|
| CLI/TUI | HTTP API（通过 gateway_service） | 所有外部命令通过 HTTP API 调用 |
| 外部客户端 | HTTP/WebSocket/MCP/A2A/OpenAI API | 第三方集成通过网关访问 |
| 其他 daemon | IPC Bus 接收路由请求 | agent_d / tool_d / llm_d / sched_d |
| 测试框架 | 所有公开接口 | 单元测试和集成测试 |

---

## 4. 配置参数

### 4.1 网关服务配置 (`gateway_service_config_t`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `name` | const char* | — | 服务名称 |
| `version` | const char* | — | 服务版本 |
| `http.type` | enum | HTTP | HTTP 网关类型 |
| `http.host` | const char* | — | HTTP 监听地址 |
| `http.port` | uint16_t | — | HTTP 监听端口 |
| `http.enabled` | bool | true | 是否启用 HTTP |
| `http.max_request_size` | size_t | — | 最大请求大小 |
| `http.timeout_ms` | uint32_t | — | 请求超时（毫秒） |
| `ws.enabled` | bool | true | 是否启用 WebSocket |
| `stdio.enabled` | bool | false | 是否启用 Stdio |
| `enable_metrics` | bool | true | 启用指标收集 |
| `enable_tracing` | bool | true | 启用追踪 |
| `shutdown_timeout_ms` | uint32_t | — | 关闭超时（毫秒） |

### 4.2 转发配置 (`gw_forward_config_t`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `a2a_target_daemon` | const char* | `"sched_d"` | A2A 目标 daemon（agent 注册 + task 调度） |
| `mcp_target_daemon` | const char* | `"tool_d"` | MCP 目标 daemon |
| `openai_target_daemon` | const char* | `"llm_d"` | OpenAI 目标 daemon |
| `jsonrpc_target_daemon` | const char* | `"sched_d"` | JSON-RPC 目标 daemon |
| `a2a_channel` | const char* | `"a2a"` | A2A IPC 通道名 |
| `mcp_channel` | const char* | `"mcp"` | MCP IPC 通道名 |
| `openai_channel` | const char* | `"llm"` | OpenAI IPC 通道名 |
| `jsonrpc_channel` | const char* | `"sched"` | JSON-RPC IPC 通道名 |
| `request_timeout_ms` | uint32_t | 30000 | 请求超时（毫秒） |
| `enable_stats` | bool | true | 启用转发统计 |

### 4.3 协议路由器配置

| 参数 | 常量 | 说明 |
|------|:---:|------|
| `GW_PROTO_MAX_ADAPTERS` | 8 | 最大协议适配器数量 |
| `GW_PROTO_MAX_METHOD_LEN` | 128 | 最大方法名长度 |
| `GW_PROTO_MAX_PATH_LEN` | 512 | 最大请求路径长度 |

### 4.4 环境变量

| 变量 | 说明 |
|------|------|
| `TEST_GATEWAY_HTTP_PORT` | 测试环境 HTTP 端口（默认 8080） |
| `AGENTOS_TEST_MODE` | 测试模式标志 |

---

## 5. 跨团队接口合约

### 5.1 合约文件

- `contracts/contract_A_C_gateway_d.h` — 团队A（Gateway Daemon）与团队C（测试/质量）的接口合约
- `agentos/daemon/gateway_d/tests/` — 网关守护进程单元测试

### 5.2 测试接口

| 函数 | 用途 | 消费者 |
|------|------|--------|
| `gateway_service_get_state(service)` | 获取服务状态 | 测试/监控 |
| `gateway_service_is_running(service)` | 检查服务是否运行中 | 测试/监控 |
| `gateway_service_get_stats(service, stats)` | 获取服务统计信息 | 测试/监控 |
| `gateway_service_healthcheck(service)` | 执行健康检查 | 测试/监控 |
| `gateway_service_get_default_config(config)` | 获取默认配置 | 测试 |
| `gw_proto_router_get_stats(router, stats)` | 获取路由统计 | 测试/监控 |
| `gw_proto_router_is_healthy(router)` | 检查路由器健康状态 | 测试/监控 |
| `gw_forward_get_stats(fw, stats)` | 获取转发统计 | 测试/监控 |
| `gw_forward_is_healthy(fw)` | 检查转发器健康状态 | 测试/监控 |
| `gw_proto_detect(content_type, path, body)` | 协议检测 | 测试 |
| `gateway_service_adapter_get_interface()` | 获取适配器接口 | 测试/框架集成 |

---

## 6. 文件所有权

```
@owner: team-A
```

所有 `agentos/daemon/gateway_d/` 下的文件归属于团队A。团队C 仅可修改 `tests/` 目录下的测试文件。

---

## 7. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-06-17 | 初始版本，基于 v0.1.0 代码现状 |