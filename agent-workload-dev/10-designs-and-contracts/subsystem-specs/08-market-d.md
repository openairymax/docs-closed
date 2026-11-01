# Market Daemon 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-18 | **团队**: A（Agent 能力市场）
> **代码路径**: `agentrt/daemons/market_d/`

---

## 1. 职责边界

Market Daemon 是 AgentRT 的 Agent 能力市场守护进程，负责 Agent 和 Skill 的全生命周期管理。它实现 4 大多智能体协作模式中的 **Market 模式**：Agent 在市场中发布能力，消费者通过搜索/竞价发现并选择最优 Agent/Skill 进行安装调用。

### 核心职责

| 模块 | 职责 | 源文件 |
|------|------|--------|
| **市场服务核心** | 市场服务生命周期管理（创建/销毁/重载配置），Agent 和 Skill 的 CRUD 操作 | `src/market_service_impl.c` |
| **市场服务适配器** | 将 market_service 适配为 airy_service_t 标准接口，支持统一服务框架 | `src/market_svc_adapter.c` |
| **Agent 注册表** | Agent 注册/注销/查询/搜索，线程安全，支持按名称/描述模糊搜索 | `src/agent_registry.c` |
| **Agent 注册核心** | Agent 元数据管理（版本号/下载URL/校验和），标签搜索，版本追踪 | `src/agent_registry_core.c` |
| **Skill 注册表** | Skill 注册/注销/查询，支持工具型/知识型/集成型/自定义四种类型 | `src/skill_registry.c` |
| **发布管理** | 资源发布到市场，版本更新检查，远程注册中心同步 | `src/publisher.c` |
| **安装管理** | 资源下载/安装/卸载，包签名验证，依赖检查，支持强制更新和自定义安装路径 | `src/installer.c` |
| **守护进程入口** | JSON-RPC 2.0 服务端，方法分发器路由，Unix Socket/TCP 双模式，线程池并发处理 | `src/main.c` |

### 非职责（明确排除）

- LLM 推理与认知循环（属于 CoreLoopThree / llm_d）
- 任务编排与子 Agent 调度（属于 Orchestrator）
- 安全守卫/内容过滤/包签名验证（属于 Cupolas / daemon_security）
- 网络协议层通信（属于 gateway_d）
- 持久化存储引擎（属于 HeapStore / Memory Provider）
- 内存管理/任务调度等底层基础设施（属于 CoreKern）
- 配置管理基础设施（属于 commons + config_manager）

---

## 2. 公共接口

### 2.1 头文件清单

| 头文件 | 用途 | 公开 API 数量 |
|--------|------|:---:|
| `market_service.h` | 市场服务核心 API（Agent/Skill 注册、搜索、安装、卸载、更新检查） | 14 |
| `market_svc_adapter.h` | 市场服务适配器（统一服务框架接口） | 8 |
| `agent_registry_core.h` | Agent 注册核心（元数据管理、版本追踪、标签搜索） | 11 |

### 2.2 关键 API 签名

```c
// 市场服务生命周期
int market_service_create(const market_config_t *config, market_service_t **service);
int market_service_destroy(market_service_t *service);
int market_service_reload_config(market_service_t *service, const market_config_t *config);
int market_service_sync_registry(market_service_t *service);

// Agent 管理
int market_service_register_agent(market_service_t *service, const agent_info_t *agent_info);
int market_service_search_agents(market_service_t *service, const search_params_t *params,
                                 agent_info_t ***agents, size_t *count);
int market_service_install_agent(market_service_t *service, const install_request_t *request,
                                 install_result_t **result);
int market_service_uninstall_agent(market_service_t *service, const char *agent_id);
int market_service_get_installed_agents(market_service_t *service, agent_info_t ***agents,
                                        size_t *count);

// Skill 管理
int market_service_register_skill(market_service_t *service, const skill_info_t *skill_info);
int market_service_search_skills(market_service_t *service, const search_params_t *params,
                                 skill_info_t ***skills, size_t *count);
int market_service_install_skill(market_service_t *service, const install_request_t *request,
                                 install_result_t **result);
int market_service_uninstall_skill(market_service_t *service, const char *skill_id);
int market_service_get_installed_skills(market_service_t *service, skill_info_t ***skills,
                                        size_t *count);

// 更新检查
int market_service_check_update(market_service_t *service, const char *id, bool *has_update,
                                char **latest_version);

// 服务适配器
airy_err_t market_service_adapter_create(airy_service_t *out_service,
                                              const airy_svc_config_t *config);
airy_err_t market_service_adapter_wrap(airy_service_t *out_service,
                                            market_service_t market_svc,
                                            const airy_svc_config_t *config);
market_service_t market_service_adapter_get_original(airy_service_t service);

// Agent 注册核心
agent_registry_t *agent_registry_core_create(void);
int agent_registry_core_init(agent_registry_t *registry, const char *db_path);
int agent_registry_core_add(agent_registry_t *registry, const agent_entry_t *reg);
int agent_registry_core_remove(agent_registry_t *registry, const char *agent_id);
const agent_entry_t *agent_registry_core_get(agent_registry_t *registry, const char *agent_id);
size_t agent_registry_core_search(agent_registry_t *registry, const char *query,
                                  const agent_entry_t **out_entries, size_t max_entries);
size_t agent_registry_core_search_by_tag(agent_registry_t *registry, const char *tag,
                                         const agent_entry_t **out_entries, size_t max_entries);
int agent_registry_core_add_version(agent_registry_t *registry, const char *agent_id,
                                    const agent_version_t *version);
```

### 2.3 核心数据结构

```c
// 市场配置
typedef struct {
    char *registry_url;          // 远程注册中心 URL
    char *storage_path;          // 本地存储路径
    uint32_t sync_interval_ms;   // 同步间隔
    uint32_t cache_ttl_ms;       // 缓存 TTL
    bool enable_remote_registry; // 是否启用远程注册中心
    bool enable_auto_update;     // 是否启用自动更新
} market_config_t;

// Agent 信息
typedef struct {
    char *agent_id; char *name; char *version; char *description;
    agent_type_t type; agent_status_t status;
    char *author; char *repository; char *dependencies;
    float rating; uint32_t download_count; uint64_t last_updated;
} agent_info_t;

// Skill 信息
typedef struct {
    char *skill_id; char *name; char *version; char *description;
    skill_type_t type; char *author; char *repository; char *dependencies;
    float rating; uint32_t download_count; uint64_t last_updated;
} skill_info_t;

// 搜索参数
typedef struct {
    char *query; agent_type_t agent_type; skill_type_t skill_type;
    bool only_installed; bool sort_by_rating; bool sort_by_download;
    size_t limit; size_t offset;
} search_params_t;

// 安装请求/结果
typedef struct {
    char *id; char *version; bool force_update; char *install_path;
} install_request_t;

typedef struct {
    bool success; char *message; char *installed_version;
    char *install_path; int error_code;
} install_result_t;
```

### 2.4 错误码

| 错误码 | 值 | 含义 |
|--------|:---:|------|
| `AIRY_SUCCESS` | 0 | 成功 |
| `AIRY_ERR_INVALID_PARAM` | — | 无效参数 |
| `AIRY_ERR_OUT_OF_MEMORY` | — | 内存不足 |
| `AIRY_ERR_NOT_FOUND` | — | Agent/Skill 未找到 |
| `AIRY_ERR_OVERFLOW` | — | 注册表已满 |
| `AIRY_ERR_IO` | — | 文件/网络 I/O 错误 |
| `AIRY_ERR_ALREADY_EXISTS` | — | Agent/Skill 已存在 |
| `MARKET_ERR_ALREADY_EXISTS` | DAEMON_BASE + 0x20 | 重复注册（market_d 特化） |
| `MARKET_ERR_INSTALL_FAIL` | DAEMON_BASE + 0x21 | 安装失败 |

### 2.5 JSON-RPC 2.0 方法

| 方法 | 说明 | 入参 | 出参 |
|------|------|------|------|
| `register_agent` | 注册 Agent 到市场 | `agent` 对象 | `status`, `agent_id` |
| `search_agents` | 搜索 Agent | `keyword`, `offset`, `limit` | Agent 数组 |
| `install_agent` | 安装 Agent | `agent_id`, `version` | `status`, `installed_version` |
| `register_skill` | 注册 Skill | `skill` 对象 | `status`, `skill_id` |
| `search_skills` | 搜索 Skill | `keyword` | Skill 数组 |
| `health_check` | 健康检查 | — | `service`, `healthy`, `timestamp` |

---

## 3. 依赖关系

### 3.1 内部依赖（编译时）

```
market_d
  ├── svc_common (daemon 公共库)
  │     ├── svc_common.h         — 服务框架接口
  │     ├── svc_logger.h         — 统一日志
  │     ├── svc_config.h         — 配置服务
  │     ├── svc_cache.h          — 缓存服务
  │     ├── ipc_service_bus.h    — IPC 服务总线
  │     ├── method_dispatcher.h  — 方法分发器
  │     ├── jsonrpc_helpers.h    — JSON-RPC 辅助
  │     ├── daemon_security.h    — 安全框架（包签名验证）
  │     ├── thread_pool.h        — 线程池
  │     ├── param_validator.h    — 参数校验
  │     ├── safe_string_utils.h  — 安全字符串
  │     ├── daemon_bootstrap_sd.h  — 服务发现启动
  │     └── daemon_bootstrap_ipc.h — IPC 启动
  ├── airy_common (commons 统一基础库)
  │     ├── utils/memory/    — memory_compat.h
  │     ├── utils/error/     — error.h, error_types.h
  │     ├── utils/logging/   — logging.h
  │     ├── utils/string/    — 安全字符串操作
  │     ├── utils/sync/      — 互斥锁
  │     ├── utils/network/   — 网络抽象
  │     ├── utils/ipc/       — IPC 抽象
  │     ├── utils/cache/     — 缓存
  │     └── platform/        — 平台抽象层
  ├── cJSON                    — JSON 解析
  └── yaml                     — YAML 配置解析
```

### 3.2 运行时依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| POSIX 线程 (libpthread) | 系统 | 线程池并发处理 |
| curl (可选) | 外部 | 远程注册中心同步、Agent 包下载 |
| tar (可选) | 外部 | 下载包解压 |
| 文件系统 | 系统 | Agent 安装目录创建、元数据文件写入 |

### 3.3 被依赖方

| 消费者 | 使用接口 | 说明 |
|--------|---------|------|
| Orchestrator | `market_service_search_agents` | 编排器根据任务需求从市场发现合适的 Agent |
| CoreLoopThree | `market_service_search_skills` | 认知引擎查找可用 Skill 进行工具调用 |
| gateway_d | JSON-RPC `search_agents`, `install_agent` | 通过 API 网关暴露市场能力给外部用户 |
| tool_d | `market_service_get_installed_skills` | 工具执行器查询已安装的 Skill 列表 |

---

## 4. 配置参数

### 4.1 市场服务配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `registry_url` | char* | NULL | 远程注册中心 URL |
| `storage_path` | char* | `"market.log"` | 本地存储/安装路径 |
| `sync_interval_ms` | uint32_t | 30000 | 远程同步间隔(ms) |
| `cache_ttl_ms` | uint32_t | 3600000 | 缓存过期时间(ms) |
| `enable_remote_registry` | bool | false | 是否启用远程注册中心同步 |
| `enable_auto_update` | bool | false | 是否启用自动更新检查 |

### 4.2 守护进程配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `DEFAULT_SOCKET_PATH_UNIX` | string | `AIRY_RUNTIME_DIR/market.sock` | Unix Socket 路径 |
| `DEFAULT_SOCKET_PATH_WIN` | string | `\\.\pipe\airy_market` | Windows 命名管道路径 |
| `DEFAULT_TCP_PORT` | uint16_t | 8082 | TCP 模式端口 |
| `MAX_BUFFER` | size_t | 65536 | 请求缓冲区大小 |
| 线程池 `min_threads` | uint32_t | 4 | 最小线程数 |
| 线程池 `max_threads` | uint32_t | 8 | 最大线程数 |
| 线程池 `queue_size` | uint32_t | 256 | 任务队列大小 |
| 线程池 `idle_timeout_ms` | uint32_t | 30000 | 线程空闲超时(ms) |

### 4.3 注册表容量限制

| 参数 | 值 | 说明 |
|------|:---:|------|
| `MAX_AGENTS` (market_service) | 256 | 市场服务最大 Agent 数 |
| `MAX_SKILLS` (market_service) | 256 | 市场服务最大 Skill 数 |
| `MAX_AGENTS` (agent_registry) | 1024 | Agent 注册表最大容量 |
| `MAX_AGENT_ID_LEN` | 128 | Agent ID 最大长度 |
| `MAX_AGENT_NAME_LEN` | 256 | Agent 名称最大长度 |
| `MAX_DESCRIPTION_LEN` | 4096 | 描述最大长度 |
| `MAX_TAGS_PER_AGENT` | 16 | 每个 Agent 最大标签数 |
| `MAX_VERSIONS_PER_AGENT` | 32 | 每个 Agent 最大版本数 |

---

## 5. 跨团队接口合约

### 5.1 合约文件

- `contracts/contract_A_B.h` — 团队A(Market Daemon) 与 团队B(Orchestrator) 的接口合约（Agent 发现与选择）
- `contracts/contract_A_C.h` — 团队A(Market Daemon) 与 团队C(测试/质量) 的接口合约

### 5.2 测试接口

| 函数 | 用途 | 消费者 |
|------|------|--------|
| `market_service_create()` | 创建市场服务实例 | 单元测试 |
| `market_service_register_agent()` | 注册 Agent 用于测试 | 单元测试 |
| `market_service_search_agents()` | 验证搜索功能 | 单元测试 |
| `market_service_install_agent()` | 验证安装流程 | 单元测试 |
| `agent_registry_core_create()` | 创建注册核心实例 | 单元测试 |
| `agent_registry_core_add()` | 添加 Agent 元数据 | 单元测试 |
| `agent_registry_core_search()` | 验证搜索功能 | 单元测试 |

### 5.3 测试文件

| 测试文件 | 测试范围 |
|----------|---------|
| `tests/test_market.c` | 市场服务集成测试 |
| `tests/test_agent_registry.c` | Agent 注册表单元测试 |
| `tests/test_agent_registry_core.c` | Agent 注册核心单元测试 |
| `tests/test_skill_registry.c` | Skill 注册表单元测试 |
| `tests/test_installer.c` | 安装器单元测试 |
| `tests/unit/daemon/market_d/test_market.c` | 市场服务单元测试（外部） |
| `tests/unit/daemon/market_d/test_agent_registry.c` | Agent 注册表单元测试（外部） |
| `tests/unit/daemon/market_d/test_agent_registry_core.c` | Agent 注册核心单元测试（外部） |
| `tests/unit/daemon/market_d/test_skill_registry.c` | Skill 注册表单元测试（外部） |
| `tests/unit/daemon/market_d/test_installer.c` | 安装器单元测试（外部） |

---

## 6. 文件所有权

```
@owner: team-A
```

所有 `agentrt/daemons/market_d/` 下的文件归属于团队A。团队C 仅可修改 `tests/` 目录下的测试文件。

### 通信方式

| 方向 | 协议 | 说明 |
|------|------|------|
| 入站 | JSON-RPC 2.0 over Unix Socket / TCP | 通过 IPC Service Bus 接收请求 |
| 出站 | HTTPS (curl) | 与远程注册中心同步、下载 Agent 包 |

---

## 7. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-06-18 | 初始版本，基于 v0.1.0 代码现状 |