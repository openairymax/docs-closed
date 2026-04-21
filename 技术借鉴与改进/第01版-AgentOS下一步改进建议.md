# AgentOS 下一步改进建议

> 基于 hermes-agent、openclaw、openJiuwen 三大参考项目深度分析，结合历史改进计划文档，面向"AgentOS成为行业基础设施"目标制定

---

## 目录

1. [战略定位与核心洞察](#1-战略定位与核心洞察)
2. [三大参考项目的核心借鉴价值](#2-三大参考项目的核心借鉴价值)
3. [AgentOS当前状态评估](#3-agentos当前状态评估)
4. [P0改进：生产就绪基线（1-2月）](#4-p0改进生产就绪基线1-2月)
5. [P1改进：核心能力深化（3-4月）](#5-p1改进核心能力深化3-4月)
6. [P2改进：生态基础设施（5-6月）](#6-p2改进生态基础设施5-6月)
7. [实施路线图与资源估算](#7-实施路线图与资源估算)
8. [风险与应对](#8-风险与应对)

---

## 1. 战略定位与核心洞察

### 1.1 AgentOS的终极定位

AgentOS不应仅仅是一个智能体操作系统，而应成为**AI Agent生态的互操作基础设施**——所有Agent项目都能通过AgentOS实现无缝协作，正如所有网络设备都能通过TCP/IP实现互联互通。

### 1.2 三大核心洞察

**洞察一：协议标准化是成为基础设施的"入场券"**

AI Agent领域正在快速标准化。MCP已被30%主流项目采纳，OpenAI API覆盖80%以上项目，A2A正在成为Agent间通信的事实标准。AgentOS若不支持这些协议，将被排除在主流生态之外。这是**生存问题**，不是优化问题。

**洞察二：微内核架构是差异化竞争的核心壁垒**

三个参考项目中，没有任何一个具备AgentOS的微内核架构。hermes-agent是单进程Python应用，openclaw是Node.js插件平台，openJiuwen是Python SDK+图执行引擎。AgentOS的多进程微内核+系统调用抽象+内核级安全，是它们完全不具备的差异化优势。**保持内核极简，所有兼容功能在用户态实现**是正确方向。

**洞察三：开发者体验决定生态繁荣的上限**

hermes-agent有55+内置工具，openJiuwen有50+预置工具，openclaw有25+通道插件。AgentOS目前工具数量有限、SDK体验参差不齐（Python SDK完成度仅65%）。**"1小时从零到第一个应用"**是必须达到的门槛。

### 1.3 改进原则

| 原则 | 说明 |
|------|------|
| **理论保持** | 体系并行论+五维正交+CoreLoopThree+MemoryRovol的理论体系不动摇 |
| **工程借鉴** | 从参考项目借鉴工程实践，形成AgentOS自己的命名和实现 |
| **标准优先** | 协议兼容优先于功能扩展，先入生态再建壁垒 |
| **内核不变** | atoms层接口签名不变，所有扩展通过新增文件和配置参数实现 |
| **渐进增强** | 新功能可通过配置开关启用/禁用，默认关闭确保向后兼容 |

---

## 2. 三大参考项目的核心借鉴价值

### 2.1 hermes-agent：全栈Agent的工程典范

| 借鉴方向 | hermes-agent实现 | AgentOS化命名 | 优先级 |
|---------|-----------------|-------------|--------|
| 工具并行执行 | 静态分类+运行时路径冲突检测 | ParallelToolDispatcher | P1 |
| 智能模型路由 | 简单任务廉价模型/复杂任务强模型 | SmartModelRouter | P1 |
| 上下文压缩交接框架 | 结构化摘要+活跃任务追踪 | ContextHandoff | P1 |
| 多凭证池故障转移 | 同Provider多凭证轮转+错误分类 | CredentialPool | P0 |
| API错误分类恢复 | 6种错误类型×对应恢复策略 | ErrorRecovery | P0 |
| 冻结快照记忆 | 会话开始时冻结，写入立即持久化 | FrozenSnapshotMemory | P2 |
| SOUL.md人格系统 | 文件系统定义+安全扫描 | AgentPersona | P2 |
| 子Agent委派 | 并行子Agent+受限工具集+最大深度2 | SubAgentDelegation | P1 |
| MCP协议集成 | Stdio+HTTP传输+自动重连 | MCPClient | P0 |

### 2.2 openclaw：多通道网关的架构标杆

| 借鉴方向 | openclaw实现 | AgentOS化命名 | 优先级 |
|---------|-------------|-------------|--------|
| 多通道统一收件箱 | 25+消息通道ChannelPlugin抽象 | UnifiedChannel | P1 |
| Plugin SDK | 100+子路径导出+Proxy懒加载 | PluginSDK | P1 |
| ACP协议桥接 | IDE Agent到Gateway的协议翻译 | ACPServer | P2 |
| 配置类型安全 | 37个类型拆分+Zod运行时验证 | ConfigSchema | P2 |
| 跨平台守护进程 | launchd/systemd/schtasks统一 | DaemonManager | P0 |
| 懒加载优化 | 入口/插件/模型信息三级懒加载 | LazyLoader | P2 |
| 安全纵深防御 | DM配对+SSRF防护+沙箱+密钥管理 | 已有Cupolas | - |

### 2.3 openJiuwen：工业级执行引擎的技术标杆

| 借鉴方向 | openJiuwen实现 | AgentOS化命名 | 优先级 |
|---------|---------------|-------------|--------|
| Pregel图执行引擎 | BSP超步模型+Channel+Router | TaskFlow（已有原型） | P1 |
| 流批一体能力模型 | INVOKE/STREAM/COLLECT/TRANSFORM | StreamCapability | P1 |
| 中断-恢复人机交互 | Checkpointer+GraphInterrupt+InteractiveInput | WorkflowCheckpoint | P1 |
| Agent自演进 | Operator-Optimizer+RL训练+双渠道经验 | CognitiveEvolution | P2 |
| 多层记忆引擎 | 五层分类+scope隔离+分布式锁 | 已有MemoryRovol | - |
| 上下文处理器链 | 可插拔处理器+装饰器注册 | ContextProcessor | P1 |
| 多智能体团队 | P2P/PubSub/Hybrid+Git工作树 | AgentTeam | P2 |
| 安全护栏 | Guardrail风险评估+数据修正 | SafetyGuard | P0 |

---

## 3. AgentOS当前状态评估

### 3.1 模块完成度矩阵

| 模块 | 完成度 | 关键短板 |
|------|--------|---------|
| atoms/corekern | 85% | sync.c部分禁用；IPC结构体冲突；缺少跨进程IPC |
| atoms/coreloopthree | 80% | 主循环忙等待；缺少事件驱动；双思维模型待实现 |
| atoms/memoryrovol | 90% | LLM客户端可能仅为接口；向量存储依赖SQLite3 |
| atoms/syscall | 75% | 缺少完整映射文档；sandbox隔离能力待验证 |
| atoms/taskflow | 70% | 缺少与执行引擎集成；缺少动态图支持 |
| atoms/frameworks | 30% | 仅有框架文件 |
| cupolas | 88% | 异步守卫为同步包装；部分子目录仅有README |
| daemon/gateway_d | 90% | 协议栈默认未启用；缺少TLS直接支持 |
| daemon/llm_d | 88% | 单线程同步处理；缺少并发和背压 |
| daemon/tool_d | 92% | 单线程；缺少沙箱隔离和版本管理 |
| daemon/monit_d | 85% | 缺少Prometheus导出和持久化 |
| daemon/sched_d | 75% | ML策略未实现；测试最少 |
| daemon/market_d | 82% | 远程仓库/自动更新未启用 |
| SDK/Go | 90% | 缺少WebSocket和遥测实现 |
| SDK/Rust | 88% | 缺少连接池和流式响应 |
| SDK/TypeScript | 85% | 版本号不一致；缺少双端适配 |
| SDK/Python | 65% | 架构不一致；测试极度不足 |

### 3.2 与三大参考项目的差距分析

| 能力维度 | hermes-agent | openclaw | openJiuwen | AgentOS现状 |
|---------|-------------|----------|-----------|------------|
| 协议兼容 | MCP客户端 | ACP服务端 | MCP/A2A C++ SDK | 协议栈未启用 |
| 通道覆盖 | 20+平台 | 25+通道 | 8+ IM渠道 | 仅CLI/Web |
| 工具数量 | 55+ | 扩展插件 | 50+预置 | 8种执行单元 |
| 图执行引擎 | 无 | 无 | Pregel BSP | TaskFlow原型70% |
| 安全深度 | 应用层 | 应用层 | Guardrail | 内核级Cupolas |
| 记忆系统 | 冻结快照 | LanceDB | 五层分类 | 四层MemoryRovol |
| 认知循环 | 无 | 无 | 无 | CoreLoopThree |
| 自演进 | RL训练 | 无 | Operator-Optimizer | 无 |
| 开发者体验 | 开箱即用 | 开箱即用 | 丰富示例 | 编译C代码 |

### 3.3 核心差距总结

AgentOS在**理论深度**（体系并行论、五维正交、CoreLoopThree、MemoryRovol）上领先所有参考项目，但在**工程完备度**上存在三个关键差距：

1. **协议孤岛**：不支持MCP/A2A/OpenAI API，无法与任何主流Agent项目互操作
2. **通道缺失**：没有多通道接入能力，Agent无法触达用户
3. **工程粗糙**：守护进程单线程、Python SDK残缺、测试覆盖不足

---

## 4. P0改进：生产就绪基线（1-2月）

> 目标：让AgentOS从"能编译"升级为"能生产运行"

### 4.1 守护进程并发模型升级

**问题**：所有6个daemon的main循环为单线程同步accept-handle，无法处理并发请求。

**方案**：引入事件驱动+线程池混合模型

```
当前模型：
  main() -> accept() -> handle_client() -> close()  (阻塞)

目标模型：
  main() -> event_loop()
    -> on_accept: 创建client_fd
    -> on_read: 提交到thread_pool
    -> thread_pool: 执行JSON-RPC处理
    -> on_write: 返回结果
```

**实现位置**：`agentos/daemon/common/` 新增 `daemon_event_loop.c/h`

```c
typedef struct daemon_event_loop {
    int epoll_fd;                          /* Linux: epoll; Windows: IOCP */
    agentos_thread_pool_t* worker_pool;    /* 工作线程池 */
    int max_connections;                   /* 最大并发连接数 */
    int backlog_size;                      /* 待处理队列大小 */
    agentos_atomic_int active_connections; /* 当前活跃连接数 */
} daemon_event_loop_t;

AGENTOS_API agentos_error_t agentos_daemon_event_loop_create(
    int max_connections,
    int worker_threads,
    daemon_event_loop_t** out_loop);

AGENTOS_API agentos_error_t agentos_daemon_event_loop_run(
    daemon_event_loop_t* loop,
    int server_fd);

AGENTOS_API void agentos_daemon_event_loop_stop(
    daemon_event_loop_t* loop);
```

**影响范围**：6个daemon的main.c均需重构主循环，但JSON-RPC处理逻辑不变。

### 4.2 MCP协议栈激活与完善

**问题**：gateway_d中MCP/A2A/OpenAI协议栈受`AGENTOS_HAS_PROTOCOLS`宏控制，默认未启用。

**方案**：

**Step 1**：在`agentos/daemon/gateway_d/src/`新增协议处理模块

```
gateway_d/src/
├── protocol/
│   ├── mcp_server.c/h          /* MCP v1.0 服务端 */
│   ├── mcp_transport_stdio.c   /* MCP Stdio传输 */
│   ├── mcp_transport_http.c    /* MCP HTTP传输 */
│   ├── a2a_handler.c/h         /* A2A v0.3.0 处理器 */
│   ├── openai_compat.c/h       /* OpenAI API兼容层 */
│   └── protocol_router.c/h     /* 协议路由器 */
```

**Step 2**：MCP服务端核心接口

```c
typedef struct mcp_server {
    daemon_event_loop_t* event_loop;
    mcp_transport_type_t transport;      /* STDIO / HTTP */
    char* server_name;
    char* server_version;
    mcp_tool_registry_t* tools;         /* 工具注册表 */
    mcp_resource_registry_t* resources; /* 资源注册表 */
} mcp_server_t;

AGENTOS_API agentos_error_t agentos_mcp_server_create(
    const char* name,
    const char* version,
    mcp_transport_type_t transport,
    mcp_server_t** out_server);

AGENTOS_API agentos_error_t agentos_mcp_server_register_tool(
    mcp_server_t* server,
    const char* tool_name,
    const char* description,
    const cJSON* input_schema,
    mcp_tool_handler_t handler);

AGENTOS_API agentos_error_t agentos_mcp_server_start(
    mcp_server_t* server);
```

**Step 3**：OpenAI API兼容层

```c
typedef struct openai_compat {
    mcp_server_t* mcp_backend;          /* 底层复用MCP工具注册 */
    agentos_llm_client_t* llm_client;   /* LLM调用代理 */
} openai_compat_t;

/* 兼容端点：
   POST /v1/chat/completions  -> agentos_llm_complete
   POST /v1/completions       -> agentos_llm_complete
   GET  /v1/models            -> agentos_llm_list_models
   POST /v1/tools/call        -> agentos_mcp_tool_call
*/
```

**Step 4**：CMake配置更新

```cmake
option(AGENTOS_ENABLE_PROTOCOLS "Enable MCP/A2A/OpenAI protocol stack" ON)

if(AGENTOS_ENABLE_PROTOCOLS)
    target_compile_definitions(agentos_gateway_d PRIVATE AGENTOS_HAS_PROTOCOLS=1)
    target_sources(agentos_gateway_d PRIVATE
        src/protocol/mcp_server.c
        src/protocol/mcp_transport_stdio.c
        src/protocol/mcp_transport_http.c
        src/protocol/a2a_handler.c
        src/protocol/openai_compat.c
        src/protocol/protocol_router.c
    )
endif()
```

### 4.3 API错误分类与恢复系统

**借鉴**：hermes-agent的`error_classifier.py`，将API错误从简单的"重试或放弃"升级为结构化恢复策略。

**实现位置**：`agentos/daemon/llm_d/src/` 新增 `error_recovery.c/h`

```c
typedef enum agentos_failover_reason {
    AGENTOS_FAILOVER_AUTH = 0,            /* 401/403 -> 刷新/轮转凭证 */
    AGENTOS_FAILOVER_BILLING,             /* 402 -> 立即轮转 */
    AGENTOS_FAILOVER_RATE_LIMIT,          /* 429 -> 退避后轮转 */
    AGENTOS_FAILOVER_OVERLOADED,          /* 503/529 -> 退避 */
    AGENTOS_FAILOVER_CONTEXT_OVERFLOW,    /* 上下文过大 -> 压缩 */
    AGENTOS_FAILOVER_MODEL_NOT_FOUND,     /* 404 -> 切换模型 */
    AGENTOS_FAILOVER_TIMEOUT,             /* 超时 -> 重试 */
    AGENTOS_FAILOVER_NETWORK_ERROR,       /* 网络错误 -> 重试 */
} agentos_failover_reason_t;

typedef struct agentos_error_recovery {
    agentos_credential_pool_t* cred_pool;   /* 多凭证池 */
    int max_retries;                        /* 最大重试次数 */
    float base_backoff_sec;                 /* 基础退避时间 */
    float max_backoff_sec;                  /* 最大退避时间 */
} agentos_error_recovery_t;

AGENTOS_API agentos_failover_reason_t agentos_classify_api_error(
    int http_status,
    const char* error_body);

AGENTOS_API agentos_error_t agentos_error_recovery_execute(
    agentos_error_recovery_t* recovery,
    agentos_failover_reason_t reason,
    agentos_llm_request_t* request);
```

### 4.4 多凭证池

**借鉴**：hermes-agent的`credential_pool.py`

**实现位置**：`agentos/daemon/llm_d/src/` 新增 `credential_pool.c/h`

```c
typedef enum agentos_cred_status {
    AGENTOS_CRED_OK = 0,
    AGENTOS_CRED_EXHAUSTED,
    AGENTOS_CRED_INVALID,
} agentos_cred_status_t;

typedef struct agentos_credential {
    char* id;
    char* api_key;
    char* base_url;
    agentos_cred_status_t status;
    uint64_t exhausted_at;        /* 耗尽时间戳 */
    uint64_t request_count;       /* 请求计数 */
} agentos_credential_t;

typedef struct agentos_credential_pool {
    char* provider;                         /* "openai", "anthropic", etc. */
    agentos_credential_t* creds;            /* 凭证数组 */
    size_t cred_count;                      /* 凭证数量 */
    size_t current_index;                   /* 当前轮转索引 */
    agentos_mutex_t lock;                   /* 线程安全 */
} agentos_credential_pool_t;

AGENTOS_API agentos_error_t agentos_credential_pool_create(
    const char* provider,
    agentos_credential_pool_t** out_pool);

AGENTOS_API agentos_error_t agentos_credential_pool_add(
    agentos_credential_pool_t* pool,
    const char* api_key,
    const char* base_url);

AGENTOS_API agentos_error_t agentos_credential_pool_get_next(
    agentos_credential_pool_t* pool,
    agentos_credential_t** out_cred);

AGENTOS_API agentos_error_t agentos_credential_pool_mark_exhausted(
    agentos_credential_pool_t* pool,
    const char* cred_id);
```

### 4.5 Python SDK重构

**问题**：Python SDK完成度仅65%，架构与其他SDK不一致，测试极度不足。

**方案**：对齐Go/Rust/TypeScript SDK的分层架构

```
toolkit/python/agentos/
├── __init__.py
├── agentos.py              # 主入口（版本3.0.0）
├── client/
│   ├── __init__.py
│   ├── http_client.py      # HTTP同步客户端
│   ├── async_client.py     # aiohttp异步客户端
│   └── mock_client.py      # Mock客户端（测试用）
├── modules/
│   ├── __init__.py
│   ├── task_manager.py     # 任务管理
│   ├── memory_manager.py   # 记忆管理
│   ├── session_manager.py  # 会话管理
│   └── skill_manager.py    # 技能管理
├── types/
│   ├── __init__.py
│   ├── errors.py           # 错误码体系（对齐C层0x0xxx~0x6xxx）
│   ├── models.py           # 数据模型
│   └── protocol.py         # 协议类型
└── utils/
    ├── __init__.py
    ├── config.py           # 配置管理
    ├── retry.py            # 重试策略
    └── telemetry.py        # 遥测
```

**测试目标**：至少8个测试文件，覆盖client/modules/types/utils各层。

### 4.6 核心Bug修复

| 问题 | 位置 | 修复方案 |
|------|------|---------|
| sync.c部分函数被`#if 0`禁用 | atoms/corekern/src/task/sync.c | 移除`#if 0`，统一到platform.h内联实现 |
| IPC结构体定义冲突 | binder.c与channel.c | 拆分为`agentos_ipc_binder_channel`和`agentos_ipc_message_channel` |
| TypeScript SDK版本号不一致 | package.json 1.0.0 vs 代码3.0.0 | 统一为3.0.0 |
| loop.c忙等待 | atoms/coreloopthree/src/loop.c | 引入eventfd/pipe事件通知替代Sleep(10) |

---

## 5. P1改进：核心能力深化（3-4月）

> 目标：让AgentOS从"能运行"升级为"能智能运行"

### 5.1 TaskFlow图执行引擎完善

**借鉴**：openJiuwen的Pregel BSP超步模型

**当前状态**：`atoms/taskflow/`已有原型（70%），但缺少与coreloopthree执行引擎的集成。

**完善方案**：

**Step 1**：实现BSP超步执行器

```c
typedef struct taskflow_pregel_loop {
    taskflow_graph_t* graph;               /* 执行图 */
    taskflow_channel_mgr_t* channels;      /* Channel管理器 */
    taskflow_node_version_t* versions;     /* 节点版本号 */
    taskflow_task_pool_t* executor;        /* 并行任务池 */
    int superstep;                         /* 当前超步编号 */
    int max_supersteps;                    /* 最大超步数 */
} taskflow_pregel_loop_t;

AGENTOS_API agentos_error_t taskflow_pregel_run(
    taskflow_pregel_loop_t* loop,
    const taskflow_graph_input_t* input,
    taskflow_graph_output_t** out_output);
```

**Step 2**：实现三种Channel类型

```c
typedef enum taskflow_channel_type {
    TASKFLOW_CHANNEL_TRIGGER = 0,    /* 1对1激活 */
    TASKFLOW_CHANNEL_BARRIER,        /* N对1汇聚 */
    TASKFLOW_CHANNEL_LAST_VALUE,     /* 状态传递 */
} taskflow_channel_type_t;
```

**Step 3**：实现三种Router模式

```c
typedef enum taskflow_router_type {
    TASKFLOW_ROUTER_STATIC = 0,       /* 静态扇出 */
    TASKFLOW_ROUTER_BARRIER,          /* 汇聚等待 */
    TASKFLOW_ROUTER_CONDITIONAL,      /* 条件分支 */
} taskflow_router_type_t;
```

**Step 4**：与coreloopthree执行引擎集成

在`agentos_execution_engine_process`中，当检测到任务类型为`AGENTOS_TASK_WORKFLOW`时，委托给TaskFlow引擎执行。

### 5.2 SafetyGuard安全守卫

**借鉴**：openJiuwen的Guardrail风险评估模型

**实现位置**：`agentos/cupolas/src/guards/` 新增 `safety_guard.c/h`

```c
typedef enum agentos_risk_level {
    AGENTOS_RISK_SAFE = 0,
    AGENTOS_RISK_LOW,
    AGENTOS_RISK_MEDIUM,
    AGENTOS_RISK_HIGH,
    AGENTOS_RISK_CRITICAL,
} agentos_risk_level_t;

typedef struct agentos_guard_result {
    agentos_risk_level_t risk_level;
    int is_safe;
    char* risk_type;                      /* "prompt_injection", "data_leak", etc. */
    char* modified_data;                  /* 修正/脱敏后的数据 */
    size_t modified_data_len;
    char* explanation;                    /* 风险说明 */
} agentos_guard_result_t;

typedef struct agentos_safety_guard {
    agentos_guard_rule_t* rules;          /* 安全规则集 */
    size_t rule_count;
    agentos_llm_client_t* llm_client;     /* LLM辅助判断 */
    int enable_llm_judge;                 /* 启用LLM辅助判断 */
    float llm_judge_threshold;            /* LLM判断阈值 */
} agentos_safety_guard_t;

AGENTOS_API agentos_error_t agentos_safety_guard_check_input(
    agentos_safety_guard_t* guard,
    const char* input,
    size_t input_len,
    agentos_guard_result_t** out_result);

AGENTOS_API agentos_error_t agentos_safety_guard_check_output(
    agentos_safety_guard_t* guard,
    const char* output,
    size_t output_len,
    agentos_guard_result_t** out_result);
```

**与Cupolas集成**：SafetyGuard作为Cupolas的guard_core的新检测器类型注册，复用现有的优先级排序和同步/异步检测框架。

### 5.3 上下文处理器链

**借鉴**：openJiuwen的ContextEngine处理器链

**实现位置**：`agentos/atoms/coreloopthree/src/cognition/` 新增 `context_processor.c/h`

```c
typedef struct agentos_context_processor {
    char* name;
    char* type;                           /* "window_trimmer", "compressor", "summarizer" */
    agentos_error_t (*process)(
        struct agentos_context_processor* self,
        agentos_model_context_t* context,
        const agentos_context_processor_config_t* config);
    void (*destroy)(struct agentos_context_processor* self);
} agentos_context_processor_t;

typedef struct agentos_context_engine {
    agentos_context_processor_t** processors;  /* 处理器链 */
    size_t processor_count;
    agentos_llm_client_t* llm_client;          /* LLM客户端（压缩/摘要用） */
} agentos_context_engine_t;

AGENTOS_API agentos_error_t agentos_context_engine_register_processor(
    agentos_context_engine_t* engine,
    agentos_context_processor_t* processor);

AGENTOS_API agentos_error_t agentos_context_engine_process(
    agentos_context_engine_t* engine,
    agentos_model_context_t* context);
```

**预置处理器**：

| 处理器 | 功能 | 借鉴来源 |
|--------|------|---------|
| WindowTrimmer | 按token预算裁剪上下文窗口 | hermes-agent |
| LLMCompressor | LLM摘要式压缩中间轮次 | hermes-agent |
| StructuredSummarizer | 结构化摘要（已解决/待决问题追踪） | hermes-agent交接框架 |
| MemoryAugmenter | 从MemoryRovol检索相关记忆注入上下文 | AgentOS原创 |

### 5.4 工具并行执行引擎

**借鉴**：hermes-agent的工具并行化决策

**实现位置**：`agentos/atoms/coreloopthree/src/execution/` 新增 `parallel_dispatcher.c/h`

```c
typedef enum agentos_tool_safety_class {
    AGENTOS_TOOL_READ_ONLY = 0,     /* 只读工具，可并行 */
    AGENTOS_TOOL_WRITE_SHARED,      /* 写共享资源，需路径冲突检测 */
    AGENTOS_TOOL_INTERACTIVE,       /* 交互式工具，必须串行 */
    AGENTOS_TOOL_SIDE_EFFECT,       /* 有副作用，必须串行 */
} agentos_tool_safety_class_t;

typedef struct agentos_parallel_dispatcher {
    agentos_tool_registry_t* registry;
    int max_parallel;                      /* 最大并行度 */
    agentos_thread_pool_t* pool;           /* 线程池 */
} agentos_parallel_dispatcher_t;

AGENTOS_API agentos_error_t agentos_parallel_dispatcher_dispatch(
    agentos_parallel_dispatcher_t* dispatcher,
    const agentos_tool_call_t* calls,
    size_t call_count,
    agentos_tool_result_t** out_results,
    size_t* out_result_count);
```

**并行化决策算法**：

```
1. 单工具调用 -> 串行
2. 包含交互式工具(clarify) -> 全部串行
3. 包含写共享资源工具 -> 检查路径冲突：
   - 无冲突 -> 并行
   - 有冲突 -> 冲突工具串行，其余并行
4. 全部只读工具 -> 全部并行
5. 其他 -> 串行
```

### 5.5 子Agent委派

**借鉴**：hermes-agent的delegate_tool

**实现位置**：`agentos/atoms/coreloopthree/src/execution/units/` 新增 `delegate.c/h`

```c
typedef struct agentos_delegate_config {
    const char* focus_prompt;              /* 聚焦提示词 */
    const char** allowed_tools;            /* 允许的工具列表 */
    size_t allowed_tool_count;
    int max_depth;                         /* 最大委派深度（默认2） */
    int max_iterations;                    /* 最大迭代次数 */
    float token_budget_ratio;              /* token预算比例 */
} agentos_delegate_config_t;

AGENTOS_API agentos_error_t agentos_delegate_task(
    agentos_cognition_engine_t* parent,
    const char* task_description,
    const agentos_delegate_config_t* config,
    char** out_result);
```

**安全约束**：
- 最大深度2层（parent -> child -> grandchild被拒绝）
- 子Agent禁止的工具：delegate_task（递归）、clarify（用户交互）、memory（共享写入）
- 子Agent获得独立会话（无父历史），避免上下文污染

### 5.6 WorkflowCheckpoint中断恢复

**借鉴**：openJiuwen的Checkpointer+GraphInterrupt

**实现位置**：`agentos/atoms/taskflow/src/` 新增 `checkpoint.c/h`

```c
typedef struct taskflow_checkpoint {
    int superstep;                         /* 当前超步 */
    taskflow_channel_snapshot_t* channels; /* Channel快照 */
    int* node_versions;                    /* 节点版本号 */
    size_t node_count;
    cJSON* pending_buffer;                 /* 待处理缓冲区 */
    char* interrupt_reason;                /* 中断原因 */
} taskflow_checkpoint_t;

AGENTOS_API agentos_error_t taskflow_checkpoint_save(
    taskflow_pregel_loop_t* loop,
    taskflow_checkpoint_t** out_checkpoint);

AGENTOS_API agentos_error_t taskflow_checkpoint_restore(
    taskflow_pregel_loop_t* loop,
    const taskflow_checkpoint_t* checkpoint);

AGENTOS_API agentos_error_t taskflow_interrupt(
    taskflow_pregel_loop_t* loop,
    const char* reason,
    taskflow_checkpoint_t** out_checkpoint);
```

---

## 6. P2改进：生态基础设施（5-6月）

> 目标：让AgentOS从"能智能运行"升级为"能生态运行"

### 6.1 UnifiedChannel统一通道层

**借鉴**：openclaw的ChannelPlugin抽象 + hermes-agent的20+平台适配器

**实现位置**：`agentos/daemon/gateway_d/src/` 新增 `channel/` 目录

```c
typedef struct agentos_channel_plugin {
    char* channel_id;                      /* "telegram", "wechat", "slack", etc. */
    char* channel_name;
    
    agentos_error_t (*connect)(struct agentos_channel_plugin* self);
    agentos_error_t (*disconnect)(struct agentos_channel_plugin* self);
    agentos_error_t (*send_message)(struct agentos_channel_plugin* self,
                                    const char* chat_id,
                                    const char* content);
    agentos_error_t (*on_message)(struct agentos_channel_plugin* self,
                                   const char* chat_id,
                                   const char* content,
                                   const char* sender);
    int (*is_connected)(struct agentos_channel_plugin* self);
} agentos_channel_plugin_t;

typedef struct agentos_channel_manager {
    agentos_channel_plugin_t** channels;   /* 已注册通道 */
    size_t channel_count;
    agentos_channel_router_t* router;      /* 消息路由器 */
    daemon_event_loop_t* event_loop;       /* 事件循环 */
} agentos_channel_manager_t;
```

**优先实现通道**（按用户覆盖排序）：

| 优先级 | 通道 | 覆盖用户群 |
|--------|------|-----------|
| P2-1 | CLI | 开发者 |
| P2-2 | WebChat | 通用用户 |
| P2-3 | WeChat/WeCom | 中国企业用户 |
| P2-4 | Feishu/DingTalk | 中国企业用户 |
| P2-5 | Telegram | 国际用户 |
| P2-6 | Slack/Discord | 开发者社区 |

### 6.2 CognitiveEvolution认知进化系统

**借鉴**：openJiuwen的Operator-Optimizer架构 + SkillEvolver

**实现位置**：`agentos/atoms/coreloopthree/src/cognition/` 新增 `cognitive_evolution.c/h`

```c
typedef enum agentos_tunable_kind {
    AGENTOS_TUNABLE_PROMPT = 0,           /* 提示词调优 */
    AGENTOS_TUNABLE_CONTINUOUS,           /* 连续参数调优（temperature等） */
    AGENTOS_TUNABLE_DISCRETE,             /* 离散参数调优（模型选择等） */
    AGENTOS_TUNABLE_TOOL_SELECTOR,        /* 工具选择策略调优 */
    AGENTOS_TUNABLE_MEMORY_SELECTOR,      /* 记忆检索策略调优 */
} agentos_tunable_kind_t;

typedef struct agentos_tunable_spec {
    char* name;
    agentos_tunable_kind_t kind;
    float min_value;
    float max_value;
    float current_value;
    char** candidates;                     /* 离散选项 */
    size_t candidate_count;
} agentos_tunable_spec_t;

typedef struct agentos_evolution_patch {
    char* target;                          /* "description" / "body" */
    char* section;                         /* "Instructions" / "Examples" / "Troubleshooting" */
    char* action;                          /* "append" / "merge" / "skip" */
    char* content;                         /* 增量内容 */
    float confidence;                      /* 置信度 */
} agentos_evolution_patch_t;

typedef struct agentos_cognitive_evolution {
    agentos_memoryrovol_t* memory;         /* 记忆系统引用 */
    agentos_llm_client_t* llm_client;      /* LLM客户端 */
    agentos_tunable_spec_t* tunables;      /* 可调参数声明 */
    size_t tunable_count;
    float learning_rate;                   /* 学习率 */
} agentos_cognitive_evolution_t;

AGENTOS_API agentos_error_t agentos_cognitive_evolution_generate_experience(
    agentos_cognitive_evolution_t* evolution,
    const char* task_context,
    const char* execution_result,
    agentos_evolution_patch_t*** out_patches,
    size_t* out_patch_count);
```

**与MemoryRovol集成**：进化经验存储在MemoryRovol L3结构层，通过L4模式层进行跨任务泛化。

### 6.3 AgentTeam多智能体团队

**借鉴**：openJiuwen的AgentTeams

**实现位置**：`agentos/atoms/coreloopthree/src/` 新增 `team/` 目录

```c
typedef enum agentos_team_role {
    AGENTOS_TEAM_COORDINATOR = 0,          /* 协调者 */
    AGENTOS_TEAM_DISPATCHER,               /* 调度者 */
    AGENTOS_TEAM_MEMBER,                   /* 成员 */
} agentos_team_role_t;

typedef enum agentos_team_comm_mode {
    AGENTOS_TEAM_COMM_P2P = 0,            /* 点对点 */
    AGENTOS_TEAM_COMM_PUBSUB,             /* 发布订阅 */
    AGENTOS_TEAM_COMM_HYBRID,             /* 混合模式 */
} agentos_team_comm_mode_t;

typedef struct agentos_team {
    char* team_id;
    agentos_team_role_t* roles;            /* 角色分配 */
    size_t member_count;
    agentos_team_comm_mode_t comm_mode;    /* 通信模式 */
    agentos_ipc_channel_t* message_bus;    /* 消息总线 */
    agentos_credential_pool_t* cred_pool;  /* 共享凭证池 */
} agentos_team_t;
```

### 6.4 PluginSDK插件开发框架

**借鉴**：openclaw的Plugin SDK

**实现位置**：`agentos/toolkit/` 各SDK中新增plugin子模块

**核心设计**：每个SDK语言提供统一的插件开发接口

```python
# Python SDK示例
class AgentOSPlugin:
    def register_tools(self, api: PluginAPI) -> None:
        api.register_tool(
            name="my_tool",
            description="Custom tool description",
            input_schema={...},
            handler=self.handle_tool_call
        )
    
    def register_channels(self, api: PluginAPI) -> None:
        api.register_channel(
            channel_id="my_channel",
            channel_name="My Channel",
            connect=self.connect,
            send_message=self.send,
            on_message=self.on_message
        )
```

---

## 7. 实施路线图与资源估算

### 7.1 三阶段路线图

```
Phase 1: 生产就绪基线 (P0, 1-2月)
├── Week 1-2: 守护进程并发模型升级
├── Week 2-4: MCP协议栈激活与完善
├── Week 3-5: API错误分类+多凭证池
├── Week 4-6: Python SDK重构
├── Week 5-6: 核心Bug修复
└── 里程碑: AgentOS可通过MCP协议被外部Agent调用

Phase 2: 核心能力深化 (P1, 3-4月)
├── Week 7-9: TaskFlow图执行引擎完善
├── Week 8-10: SafetyGuard安全守卫
├── Week 9-11: 上下文处理器链
├── Week 10-12: 工具并行执行引擎
├── Week 11-13: 子Agent委派
├── Week 12-14: WorkflowCheckpoint中断恢复
└── 里程碑: AgentOS可执行复杂工作流并支持人机交互

Phase 3: 生态基础设施 (P2, 5-6月)
├── Week 15-18: UnifiedChannel统一通道层
├── Week 17-20: CognitiveEvolution认知进化
├── Week 19-22: AgentTeam多智能体团队
├── Week 21-24: PluginSDK插件开发框架
└── 里程碑: AgentOS成为可扩展的Agent生态基础设施
```

### 7.2 资源估算

| 阶段 | 所需人力 | 核心技能 |
|------|---------|---------|
| Phase 1 | 3-4人 | C系统编程、网络编程、Python |
| Phase 2 | 4-5人 | C系统编程、图算法、LLM API |
| Phase 3 | 5-6人 | C/Python/TypeScript、协议设计、分布式系统 |

### 7.3 成功度量

| 指标 | 当前值 | Phase 1目标 | Phase 2目标 | Phase 3目标 |
|------|--------|-----------|-----------|-----------|
| 协议兼容度 | 0% | MCP v1.0 100% | +A2A v0.3.0 | +OpenAI API |
| 并发处理能力 | 1连接/进程 | 100连接 | 1000连接 | 10000连接 |
| 工具数量 | 8种执行单元 | 8+MCP工具 | 8+MCP+并行 | 30+工具 |
| SDK完成度 | 65-90% | Python≥85% | 全部≥90% | 全部≥95% |
| 测试覆盖 | 70% | 80% | 85% | 90% |
| 通道覆盖 | CLI/Web | +MCP | +HTTP API | +6 IM渠道 |
| 工作流能力 | 简单链式 | 简单链式 | Pregel BSP | +中断恢复 |
| 安全等级 | Cupolas | +ErrorRecovery | +SafetyGuard | +Guardrail |

---

## 8. 风险与应对

### 8.1 技术风险

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|---------|
| MCP/A2A协议版本变化 | 中 | 高 | 实现协议版本协商，保持向后兼容 |
| 守护进程并发重构引入稳定性问题 | 高 | 高 | 渐进式重构，先新增event_loop，再逐步替换main循环 |
| TaskFlow与CoreLoopThree集成冲突 | 中 | 中 | 通过配置开关切换执行模式，保留原有执行路径 |
| Python SDK重构破坏现有用户 | 低 | 中 | 保留旧API标记为deprecated，提供迁移指南 |

### 8.2 工程风险

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|---------|
| Windows平台daemon构建问题 | 高 | 中 | 优先保证Linux/macOS稳定，Windows作为best-effort |
| 人力不足导致进度延期 | 中 | 高 | 严格按P0>P1>P2优先级，P0必须完成 |
| 测试覆盖不足导致回归 | 中 | 高 | 每个Phase结束前必须通过全量回归测试 |

### 8.3 战略风险

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|---------|
| 行业标准被单一厂商主导 | 中 | 高 | 积极参与MCP/A2A标准工作组，从兼容者转变为贡献者 |
| 参考项目快速迭代拉大差距 | 中 | 中 | 聚焦差异化优势（微内核+MemoryRovol+CoreLoopThree），不追求功能对齐 |
| 生态建设缓慢 | 高 | 高 | 降低开发者入门门槛至1小时，提供开箱即用的示例和模板 |

---

## 附录：命名映射表

| 参考项目原命名 | AgentOS化命名 | 模块位置 |
|--------------|-------------|---------|
| Pregel (openJiuwen) | TaskFlow | atoms/taskflow |
| Rail/Guardrail (openJiuwen) | SafetyGuard | cupolas/guards |
| Evolver (openJiuwen) | CognitiveEvolution | coreloopthree/cognition |
| Channel (openclaw) | UnifiedChannel | daemon/gateway_d |
| Plugin SDK (openclaw) | PluginSDK | toolkit/ |
| ACP (openclaw/hermes) | ACPServer | daemon/gateway_d |
| CredentialPool (hermes) | CredentialPool | daemon/llm_d |
| ErrorClassifier (hermes) | ErrorRecovery | daemon/llm_d |
| ContextCompressor (hermes) | ContextHandoff | coreloopthree/cognition |
| SmartModelRouting (hermes) | SmartModelRouter | daemon/llm_d |
| DelegateTool (hermes) | SubAgentDelegation | coreloopthree/execution |
| Checkpointer (openJiuwen) | WorkflowCheckpoint | atoms/taskflow |
| Operator (openJiuwen) | CognitiveEvolution | coreloopthree/cognition |
| AgentTeams (openJiuwen) | AgentTeam | coreloopthree/team |
