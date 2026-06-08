# AgentOS 宏观架构图

> **项目**: 极境智能体操作系统 | **版本**: v0.0.5 | **许可证**: Apache-2.0  
> **开源边界**: AgentOS + Desktop + Docker + Docs 四个子项目，捐赠予 **开放原子开源基金会**  
> **仓库**: [AtomGit](https://atomgit.com/openairymax/agentos) | [GitHub](https://github.com/SpharxTeam/AgentOS)

---

## 目录

1. [开源边界全景](#第一章-开源边界全景)
2. [AgentOS 核心架构分解](#第二章-agentos-核心架构分解)
3. [Desktop 客户端架构](#第三章-desktop-客户端架构)
4. [Docker 部署架构](#第四章-docker-部署架构)
5. [外部系统与协议栈](#第五章-外部系统与协议栈)
6. [开源组件与合作策略](#第六章-开源组件与合作策略)
7. [双思考系统与认知循环](#第七章-双思考系统与认知循环)
8. [Triple Coordinator 三核心组件 (t2/t1-f/t1-p)](#第八章-triple-coordinator-三核心组件-t2t1-ft1-p)
9. [闭源组件清单](#第九章-闭源组件清单)

---

## 图例说明

| 样式 | 含义 |
|------|------|
| **蓝色实线粗边框** | **开源边界** — 捐赠给开放原子开源基金会的全部代码 |
| **蓝色虚线边框** | 开源边界内的子模块 |
| **红色实线边框** | **外部闭源/商业服务** — 通过标准 API 协议调用，不纳入本系统 |
| **绿色虚线边框** | **第三方开源组件** — 遵循上游协议，可替换 |
| **橙色虚线边框** | **可选组件** — 不影响核心功能的中立性 |
| **实线箭头** | **强依赖** / 数据流 |
| **虚线箭头** | **弱依赖** / 可选集成 |
| **双线** | 标准化协议通信 |

---

## 第一章 开源边界全景

```mermaid
flowchart TB
    subgraph OPEN_SOURCE_BOUNDARY["开源边界 — 捐赠予开放原子开源基金会"]
        style OPEN_SOURCE_BOUNDARY stroke:#2563eb,stroke-width:4px,fill:#eff6ff
        
        subgraph AGENTOS["AgentOS — 核心智能体操作系统"]
            style AGENTOS stroke:#2563eb,stroke-width:2px,stroke-dasharray: 5 5
            direction TB
            
            subgraph KERNEL_LAYER["微内核层 (C)"]
                style KERNEL_LAYER stroke:#475569,stroke-width:1px
                CoreKern["CoreKern: IPC、内存管理、任务调度、时钟服务"]
                CoreLoopThree["CoreLoopThree: 感知-规划-执行 认知循环"]
                Memory["Memory: L1-L4 分层记忆体系"]
                TaskFlow["TaskFlow: DAG 任务编排"]
            end
            
            subgraph DAEMON_LAYER["守护进程群 (C)"]
                style DAEMON_LAYER stroke:#475569,stroke-width:1px
                GatewayD["gateway_d: API 网关"]
                LLMD["llm_d: LLM 调用抽象"]
                SchedD["sched_d: 任务调度"]
                ToolD["tool_d: 工具执行"]
                MonitD["monit_d: 监控上报"]
                MarketD["market_d: 智能体市场"]
            end
            
            subgraph MANAGEMENT_LAYER["管理层 (Python)"]
                style MANAGEMENT_LAYER stroke:#475569,stroke-width:1px
                AgentMgr["智能体管理"]
                SkillMgr["技能注册"]
                ModelMgr["模型加载"]
                ToolMgr["MCP 工具管理"]
            end
            
            subgraph SECURITY_LAYER["安全层 — Cupolas"]
                style SECURITY_LAYER stroke:#475569,stroke-width:1px
                Sandbox["执行沙箱"]
                RBAC["RBAC 权限引擎"]
                Sanitizer["输入净化"]
                Audit["审计追踪"]
            end
            
            subgraph PROTOCOL_LAYER["协议栈"]
                style PROTOCOL_LAYER stroke:#475569,stroke-width:1px
                A2A["A2A v0.3.0 协议"]
                MCP["MCP v1.0 协议"]
                OTEL["OpenTelemetry 导出"]
            end
            
            KERNEL_LAYER --> DAEMON_LAYER
            DAEMON_LAYER --> MANAGEMENT_LAYER
            MANAGEMENT_LAYER --> SECURITY_LAYER
            MANAGEMENT_LAYER --> PROTOCOL_LAYER
        end
        
        subgraph DESKTOP["Desktop — 跨平台客户端"]
            style DESKTOP stroke:#2563eb,stroke-width:2px,stroke-dasharray: 5 5
            Tauri["Tauri v2 Rust 原生壳"]
            ReactUI["React + TypeScript UI"]
            Plugins["Tauri 插件"]
            Tauri --> ReactUI --> Plugins
        end
        
        subgraph DOCKER["Docker — 容器化部署"]
            style DOCKER stroke:#2563eb,stroke-width:2px,stroke-dasharray: 5 5
            Compose["Docker Compose 编排"]
            Dockerfiles["Dockerfile 集合"]
            K8sConfigs["K8s 部署配置"]
            Compose --> Dockerfiles --> K8sConfigs
        end
        
        subgraph DOCS["Docs — 技术文档"]
            style DOCS stroke:#2563eb,stroke-width:2px,stroke-dasharray: 5 5
            Specs["协议规范文档"]
            Guides["开发者指南"]
            Architecture["架构设计文档"]
            Whitepaper["白皮书"]
            Specs --> Guides --> Architecture --> Whitepaper
        end
        
        AGENTOS --- DESKTOP
        AGENTOS --- DOCKER
        DOCS -.-> AGENTOS
        DOCS -.-> DESKTOP
        DOCS -.-> DOCKER
    end
    
    subgraph EXTERNAL["外部系统"]
        style EXTERNAL stroke:#dc2626,stroke-width:2px
        LLM_API["大语言模型 API 服务<br/>OpenAI / DeepSeek / 通义千问"]
        Database["数据库服务<br/>PostgreSQL / Redis"]
        Storage["对象存储<br/>MinIO / S3"]
        Monitoring["监控服务<br/>Prometheus / Grafana"]
    end
    
    subgraph OPTIONAL_COMPONENTS["可选组件"]
        style OPTIONAL_COMPONENTS stroke:#f97316,stroke-width:2px,stroke-dasharray: 5 5
        MemoryRovol["MemoryRovol Pro<br/>商业记忆引擎"]
    end
    
    subgraph UPSTREAM["上游标准组织"]
        style UPSTREAM stroke:#16a34a,stroke-width:2px,stroke-dasharray: 5 5
        A2A_Std["Google A2A v0.3.0 标准"]
        MCP_Std["Anthropic MCP v1.0 标准"]
        OTEL_Std["CNCF OpenTelemetry 标准"]
    end
    
    OPEN_SOURCE_BOUNDARY -->|"A2A 协议"| A2A_Std
    OPEN_SOURCE_BOUNDARY -->|"MCP 协议"| MCP_Std
    OPEN_SOURCE_BOUNDARY -->|"OTEL 导出"| OTEL_Std
    OPEN_SOURCE_BOUNDARY -->|"API 调用"| EXTERNAL
    OPTIONAL_COMPONENTS -.->|"可选替换"| OPEN_SOURCE_BOUNDARY
```

### 四项目分工

| 项目 | 定位 | 目标用户 | 技术栈 |
|------|------|---------|--------|
| **AgentOS** | 核心智能体操作系统 | 开发者 / 企业 | C (内核) + Python (管理) + C (服务) |
| **Desktop** | 跨平台桌面客户端 | 个人用户 | Tauri v2 + React/TS + Rust |
| **Docker** | 容器化部署方案 | 专业/企业用户 | Docker Compose + K8s + Nginx |
| **Docs** | 完整技术文档体系 | 所有用户 | Markdown + Sphinx + Mermaid |

---

## 第二章 AgentOS 核心架构分解

```mermaid
flowchart LR
    subgraph L1["应用与 SDK 层"]
        style L1 stroke:#2563eb,stroke-width:2px
        direction TB
        DesktopClient["Desktop 客户端"]
        WebPanel["Web 管理面板"]
        CLI["CLI 命令行工具"]
        PythonSDK["Python SDK"]
        GoSDK["Go SDK"]
        RustSDK["Rust SDK"]
        TSSDK["TypeScript SDK"]
    end
    
    subgraph L2["管理层 — Python"]
        style L2 stroke:#475569,stroke-width:2px
        direction TB
        AgentMgmt["智能体管理"]
        SkillRegistry["技能注册"]
        ModelLoader["模型加载"]
        MCPToolMgr["MCP 工具管理"]
        DeployMgr["部署管理"]
        AuditLog["审计日志"]
    end
    
    subgraph L3["守护进程群 — C"]
        style L3 stroke:#475569,stroke-width:2px
        direction TB
        GatewayD2["gateway_d"]
        LLMD2["llm_d"]
        SchedD2["sched_d"]
        ToolD2["tool_d"]
        MonitD2["monit_d"]
        MarketD2["market_d"]
        NotifyD2["notify_d"]
        ObserveD2["observe_d"]
        ChannelD2["channel_d"]
        InfoD2["info_d"]
    end
    
    subgraph L4["安全层 — Cupolas"]
        style L4 stroke:#475569,stroke-width:2px
        direction TB
        Sandbox2["执行沙箱"]
        RBAC2["RBAC 权限引擎"]
        Sanitizer2["输入净化"]
        Audit2["审计追踪"]
    end
    
    subgraph L5["微内核层 — Atoms (C)"]
        style L5 stroke:#2563eb,stroke-width:2px
        direction TB
        CoreKern2["CoreKern<br/>IPC、内存、调度"]
        CoreLoop3["CoreLoopThree<br/>感知-规划-执行"]
        Memory2["Memory<br/>L1-L4 分层记忆"]
        TaskFlow2["TaskFlow<br/>DAG 任务编排"]
        Syscall["Syscall<br/>系统调用接口"]
        Frameworks["Frameworks<br/>基础框架"]
    end
    
    subgraph L6["支撑层 — Commons"]
        style L6 stroke:#475569,stroke-width:2px
        direction TB
        PlatformAbs["三平台抽象层"]
        LogError["日志与错误码"]
        ConfigMgr["配置管理"]
        MemString["内存与字符串工具"]
        IPCNet["IPC 与网络"]
        Observability["可观测性"]
    end
    
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5
    L5 --> L6
```

### 内核层子系统详表

| 模块 | 路径 | 功能 | 代码量 |
|------|------|------|--------|
| **corekern** | atoms/corekern/ | IPC + 内存管理 + 任务调度 + 时钟服务 | ~25,000 |
| **coreloopthree** | atoms/coreloopthree/ | 认知循环：感知-规划-执行 三阶段 | ~8,000 |
| **memory** | atoms/memory/ | L1 原始层至 L4 模式层分层记忆 | ~6,000 |
| **taskflow** | atoms/taskflow/ | DAG 任务编排 + 并行度优化 | ~5,000 |
| **syscall** | atoms/syscall/ | 用户态与内核态标准接口 + 沙箱工具 | ~4,000 |
| **frameworks** | atoms/frameworks/ | 公共类型、日志、错误码基座 | ~3,000 |

### 守护进程群

| 守护进程 | 路径 | 职责 |
|----------|------|------|
| **gateway_d** | daemon/gateway_d/ | API 网关：REST/WS/gRPC 入口，A2A + MCP 协议处理 |
| **llm_d** | daemon/llm_d/ | LLM 调用抽象层：多模型统一接口 |
| **sched_d** | daemon/sched_d/ | 任务调度：定时、周期、事件驱动 |
| **tool_d** | daemon/tool_d/ | 工具执行：MCP 工具沙箱化运行 |
| **monit_d** | daemon/monit_d/ | 监控上报：OpenTelemetry 指标导出 |
| **market_d** | daemon/market_d/ | 市场服务：智能体、技能、模型注册发现 |
| **notify_d** | daemon/notify_d/ | 通知推送：事件、告警、消息 |
| **observe_d** | daemon/observe_d/ | 可观测性：Trace + Metric + Log 收集 |
| **channel_d** | daemon/channel_d/ | 跨通道通信：智能体间、人-智能体间消息路由 |
| **info_d** | daemon/info_d/ | 元信息服务：版本、状态、配置查询 |

---

## 第三章 Desktop 客户端架构

```mermaid
flowchart TB
    subgraph FRONTEND["前端 — React"]
        style FRONTEND stroke:#475569,stroke-width:2px
        direction TB
        Pages["页面路由<br/>首页、智能体、市场、设置"]
        Components["UI 组件<br/>聊天、仪表板、编辑器"]
        State["状态管理<br/>智能体状态、配置"]
        Pages --> Components --> State
    end
    
    subgraph BRIDGE["Tauri 桥接层"]
        style BRIDGE stroke:#475569,stroke-width:2px
        direction TB
        Invoke["invoke() 命令调用"]
        Events["Listen/Emit 事件系统"]
        FS["文件系统插件"]
        Invoke --> Events --> FS
    end
    
    subgraph BACKEND["后端 — Rust"]
        style BACKEND stroke:#475569,stroke-width:2px
        direction TB
        Commands["Tauri 命令<br/>agent_start、agent_stop<br/>config_get、config_set"]
        IPCClient["AgentOS IPC 客户端<br/>连接本地/远端内核"]
        Native["原生能力<br/>系统托盘、全局快捷键<br/>进程管理、资源监控"]
        Commands --> IPCClient --> Native
    end
    
    subgraph TARGETS["目标内核"]
        style TARGETS stroke:#2563eb,stroke-width:2px
        LocalKernel["本地 AgentOS 内核<br/>嵌入式部署"]
        RemoteKernel["远端 AgentOS 内核<br/>Docker/K8s 部署"]
    end
    
    FRONTEND -->|"invoke()"| BRIDGE
    BRIDGE -->|"Command"| BACKEND
    BACKEND -->|"IPC/Binder"| LocalKernel
    BACKEND -->|"HTTP/WS"| RemoteKernel
```

| 层 | 技术 | 说明 |
|----|------|------|
| **前端** | React 18 + TypeScript + Vite | 类 Electron 的 Web UI，依赖：react-router-dom、zustand |
| **桥接层** | Tauri v2 + Plugins | Rust 与 JS 双向通信，比 Electron 小 10 倍（约 5MB vs 约 50MB） |
| **后端** | Rust + tauri::command + tokio | 系统级原生能力：托盘、快捷键、进程管理 |
| **通信** | HTTP/WS/本地IPC | 自动检测本地内核，降级到远端连接 |

---

## 第四章 Docker 部署架构

```mermaid
flowchart TB
    subgraph CORE_SERVICES["核心服务组"]
        style CORE_SERVICES stroke:#2563eb,stroke-width:2px
        Kernel["agentos-kernel<br/>内核与守护进程<br/>端口: 9000-9099"]
        Gateway["agentos-gateway<br/>API 网关<br/>端口: 80/443"]
        MemorySvc["agentos-memory<br/>FAISS + SQLite<br/>端口: 6379"]
        Kernel --> Gateway
        Kernel --> MemorySvc
    end
    
    subgraph INFRA["基础设施组"]
        style INFRA stroke:#16a34a,stroke-width:2px,stroke-dasharray: 5 5
        Nginx["Nginx<br/>负载均衡与反向代理"]
        PostgreSQL["PostgreSQL<br/>L3 结构层存储"]
        Redis["Redis<br/>缓存与会话管理"]
        MinIO["MinIO<br/>对象存储<br/>端口: 9000"]
    end
    
    subgraph MONITOR["可观测性组"]
        style MONITOR stroke:#16a34a,stroke-width:2px,stroke-dasharray: 5 5
        Prometheus["Prometheus<br/>指标收集"]
        Grafana["Grafana<br/>可视化仪表板"]
        Jaeger["Jaeger（可选）<br/>分布式追踪"]
    end
    
    Gateway --> Nginx
    MemorySvc --> PostgreSQL
    MemorySvc --> Redis
    MemorySvc --> MinIO
    Kernel --> Prometheus
    Prometheus --> Grafana
    Gateway --> Jaeger
    
    subgraph EXTERNAL["外部网络"]
        style EXTERNAL stroke:#dc2626,stroke-width:2px
        User["用户浏览器"]
        LLMExt["大语言模型 API"]
        PeerAgent["A2A 对等智能体"]
    end
    
    User -->|"HTTPS"| Nginx
    Gateway -->|"API"| LLMExt
    Gateway -->|"A2A"| PeerAgent
```

### 部署模式对比

| 模式 | 目标 | 容器数 | 内存需求 | 一键启动 |
|------|------|--------|----------|----------|
| **Desktop** | 个人用户 | 0（嵌入式） | 4GB | 双击桌面图标 |
| **Docker** | 专业用户 | 8 | 8GB | docker-compose up -d |
| **Kubernetes** | 企业用户 | 10+ | 16GB+ | kubectl apply -f k8s/ |

### Docker 文件组织

```
Docker/
├── docker-compose.yml          # 一键编排 8 个容器
├── Dockerfile.agentos          # AgentOS 内核镜像
├── Dockerfile.desktop-builder  # Desktop 构建镜像
├── Dockerfile.gateway          # 网关镜像
├── config/                     # 部署配置
│   ├── nginx/                  #   Nginx 反向代理
│   ├── prometheus/             #   Prometheus 抓取配置
│   └── grafana/                #   Grafana 仪表板配置
├── scripts/                    # 运维脚本
│   ├── init-db.sh             #   数据库初始化
│   ├── backup.sh              #   备份脚本
│   └── healthcheck.sh         #   健康检查
└── k8s/                        # K8s 部署 YAML
```

---

## 第五章 外部系统与协议栈

```mermaid
flowchart LR
    subgraph PROTOCOL_IMPL["AgentOS 协议实现层"]
        style PROTOCOL_IMPL stroke:#2563eb,stroke-width:2px
        direction TB
        A2AAdapter["A2A v0.3.0 适配器<br/>protocols/standards/a2a/<br/>智能体发现、任务委托、结果同步"]
        MCPAdapter["MCP v1.0 适配器<br/>protocols/standards/mcp/<br/>工具注册与发现、资源管理、提示模板"]
        OTELExport["OpenTelemetry 导出<br/>monit_d + observe_d<br/>Trace 导出、指标收集、日志聚合"]
    end
    
    subgraph UPSTREAM_STANDARDS["上游标准定义"]
        style UPSTREAM_STANDARDS stroke:#16a34a,stroke-width:2px,stroke-dasharray: 5 5
        A2AStd2["Google A2A 标准"]
        MCPStd2["Anthropic MCP 标准"]
        OTELStd2["CNCF OTEL 标准"]
    end
    
    subgraph PEER_SYSTEMS["对等系统 (A2A)"]
        style PEER_SYSTEMS stroke:#dc2626,stroke-width:2px,stroke-dasharray: 5 5
        ThirdPartyAgent["第三方智能体"]
        ThirdPartySkill["第三方技能"]
        ThirdPartyModel["第三方模型"]
    end
    
    subgraph MCP_TOOLS["MCP 工具生态"]
        style MCP_TOOLS stroke:#16a34a,stroke-width:2px,stroke-dasharray: 5 5
        FileSystem["文件系统"]
        Database["数据库"]
        WebAPI["Web API"]
        CodeExec["代码执行"]
    end
    
    subgraph LLM_INTEGRATION["大语言模型集成层"]
        style LLM_INTEGRATION stroke:#16a34a,stroke-width:2px,stroke-dasharray: 5 5
        OpenAICompat["OpenAI 兼容"]
        ClaudeCompat["Claude 兼容"]
        ChinaEco["中国生态<br/>通义千问、DeepSeek、文心一言"]
    end
    
    subgraph FRAMEWORK_ADAPT["框架适配器"]
        style FRAMEWORK_ADAPT stroke:#f97316,stroke-width:2px,stroke-dasharray: 5 5
        LangChain["LangChain 桥接"]
        AutoGen["AutoGen 桥接"]
        OpenClaw["OpenClaw 桥接"]
        OpenJiuwen["OpenJiuwen 桥接"]
    end
    
    A2AStd2 -->|"遵循"| A2AAdapter
    MCPStd2 -->|"遵循"| MCPAdapter
    OTELStd2 -->|"集成"| OTELExport
    
    A2AAdapter -->|"通信"| ThirdPartyAgent
    A2AAdapter -->|"通信"| ThirdPartySkill
    A2AAdapter -->|"通信"| ThirdPartyModel
    
    MCPAdapter -->|"调用"| FileSystem
    MCPAdapter -->|"调用"| Database
    MCPAdapter -->|"调用"| WebAPI
    MCPAdapter -->|"调用"| CodeExec
    
    PROTOCOL_IMPL -->|"统一调用"| LLM_INTEGRATION
    PROTOCOL_IMPL -.->|"可选适配"| FRAMEWORK_ADAPT
```

### 大语言模型多模型兼容策略

AgentOS 通过 protocols/integrations/ 实现统一的大语言模型调用抽象层：

```
用户代码
   | agentos.llm.invoke(model, prompt)
   v
大语言模型统一抽象层 (protocols/integrations/)
   ├── openai/      -> GPT-4o / GPT-4 / o1
   ├── claude/      -> Claude 3.5 / Haiku
   ├── china_eco/   -> 通义千问 / DeepSeek / 文心一言 / 百川
   └── openjiuwen/  -> 开源模型 API 兼容
```

---

## 第六章 开源组件与合作策略

### 6.1 C/C++ 核心依赖（运行时）

| 组件 | 版本 | 在 AgentOS 中的用途 | 许可证 | 获取方式 |
|------|------|--------------------|--------|----------|
| OpenSSL | >=3.2 | 传输层加密、证书管理 | Apache-2.0 | 系统包管理器 |
| libcurl | >=8.5 | 大语言模型 API HTTP 客户端 | MIT | apt/brew/vcpkg |
| libmicrohttpd | latest | 内置轻量 HTTP 服务器 | LGPL-2.1 | 动态链接 |
| libwebsockets | latest | WebSocket 实时通信 | MIT | 可选编译 |
| libevent | latest | 异步事件循环 | BSD-3 | 可选编译 |
| cJSON | >=1.7.15 | JSON 解析 | MIT | 内嵌集成 |
| libyaml | >=0.2.5 | YAML 配置解析 | MIT | 系统包管理器 |

### 6.2 Python 核心依赖

| 组件 | 版本 | 用途 | 许可证 |
|------|------|------|--------|
| FAISS | >=1.7.4 | L2 特征层向量索引 | MIT |
| Sentence-Transformers | >=2.2 | 文本向量化 | Apache-2.0 |
| SQLite3 | >=3.45 | L3 结构层关系存储 | Public Domain |
| numpy/pandas/scipy | latest | 科学计算与数据处理 | BSD-3 |
| httpx/aiohttp | latest | 异步 HTTP/Web 框架 | BSD-3 / Apache-2.0 |
| pytest/black/mypy | latest | 测试、格式化、类型检查 | MIT |

### 6.3 Desktop 前端依赖

| 组件 | 用途 | 许可证 |
|------|------|--------|
| React 18 + TypeScript | UI 框架 | MIT |
| Vite | 构建工具 | MIT |
| Tauri v2 + Plugins | 原生壳 | MIT / Apache-2.0 |
| serde/tokio | Rust 序列化与异步 | MIT |

### 6.4 Docker 基础设施依赖（外部）

| 组件 | 用途 | 许可证 | 关系 |
|------|------|--------|------|
| Docker / docker-compose | 容器化部署 | Apache-2.0 | 运行环境 |
| Nginx | 反向代理与负载均衡 | BSD-2 | Docker 容器内运行 |
| PostgreSQL | 关系数据库 | PostgreSQL License | Docker 容器内运行 |
| Redis | 缓存与消息队列 | BSD-3 | Docker 容器内运行 |
| MinIO | 对象存储 | AGPL v3 | Docker 容器内运行 |
| Prometheus | 指标收集 | Apache-2.0 | Docker 容器内运行 |
| Grafana | 可视化仪表板 | AGPL v3 | Docker 容器内运行 |

### 6.5 与上游社区合作策略

| 上游 | AgentOS 角色 | 具体合作方式 |
|------|-------------|------------|
| **Google A2A v0.3.0** | 标准协议实现者 | 完整适配器实现、兼容性测试、Issue 反馈 |
| **Anthropic MCP v1.0** | 标准协议实现者 | Server/Client 实现、工具市场集成、安全反馈 |
| **CNCF OpenTelemetry** | SDK 集成者 | OTLP 导出器、Prometheus 集成、最佳实践 |
| **FAISS (Meta)** | 嵌入式向量引擎 | 默认集成、可替换 Milvus/Qdrant |
| **SQLite** | 嵌入式数据库 | 默认集成、可替换 PostgreSQL |
| **Tauri** | 跨平台框架 | 为 AI 智能体场景贡献反馈 |
| **LangChain/AutoGen** | 框架适配 | 桥接适配器、互操作性测试 |

---

## 第七章 双思考系统与认知循环

### 7.1 CoreLoopThree 顶层架构

```mermaid
flowchart LR
    subgraph INPUT["输入源"]
        style INPUT stroke:#475569,stroke-width:2px
        direction TB
        UserMsg["用户消息"]
        A2AMsg["A2A 消息"]
        ToolResult["工具结果"]
        SystemEvent["系统事件"]
    end
    
    subgraph PERCEIVE["感知层 — <10ms"]
        style PERCEIVE stroke:#2563eb,stroke-width:2px
        direction TB
        ContextProc["上下文处理<br/>context_processor"]
        IntentClass["意图分类<br/>intent_classifier"]
        EntityExtract["实体提取<br/>entity_extractor"]
        ContextProc --> IntentClass --> EntityExtract
    end
    
    subgraph THINKING["双思考系统"]
        style THINKING stroke:#2563eb,stroke-width:2px
        direction TB
        
        subgraph DUAL_MODEL["双模型并行推理"]
            style DUAL_MODEL stroke:#475569,stroke-width:1px
            direction LR
            PrimaryModel["主模型<br/>大参数、高质量<br/>~100-300ms"]
            SecondaryModel["副模型<br/>轻量级、低延迟<br/>~20-50ms"]
        end
        
        subgraph COORDINATOR["协调器"]
            style COORDINATOR stroke:#475569,stroke-width:1px
            direction LR
            Arbiter["仲裁器"]
            Majority["多数投票"]
            Weighted["加权融合"]
            DualStrategy["双模型策略"]
        end
        
        subgraph VALIDATION["交叉验证"]
            style VALIDATION stroke:#475569,stroke-width:1px
            direction LR
            BasicValidation["基础验证<br/>一致性检查"]
            AdvancedValidation["高级验证<br/>置信度评估"]
            AdaptiveValidation["自适应验证<br/>学习调整"]
        end
        
        subgraph METACOGNITION["元认知"]
            style METACOGNITION stroke:#475569,stroke-width:1px
            direction LR
            CognitiveEval["认知评估"]
            ConfidenceCal["置信度校准<br/>confidence_calibrator"]
            StreamCritic["流式评审<br/>stream_critic"]
        end
        
        PrimaryModel --> COORDINATOR
        SecondaryModel --> COORDINATOR
        COORDINATOR --> VALIDATION
        COORDINATOR --> METACOGNITION
    end
    
    subgraph PLAN["规划层 — <50ms"]
        style PLAN stroke:#2563eb,stroke-width:2px
        direction TB
        Hierarchical["分层规划<br/>hierarchical"]
        Reactive["反应式规划<br/>reactive"]
        Reflective["反思式规划<br/>reflective"]
        MLPlanner["ML 规划<br/>ml_planner"]
    end
    
    subgraph EXECUTE["执行层 — <100ms"]
        style EXECUTE stroke:#2563eb,stroke-width:2px
        direction TB
        Engine["执行引擎<br/>engine"]
        Compensation["补偿机制<br/>compensation"]
        Trace["执行追踪<br/>trace"]
    end
    
    subgraph TOOLS["工具单元"]
        style TOOLS stroke:#475569,stroke-width:2px
        direction LR
        APICall["API 调用"]
        FileOps["文件操作"]
        ShellExec["Shell 执行"]
        DatabaseTool["数据库"]
        CodeExec2["代码执行"]
        Browser["浏览器"]
    end
    
    subgraph MEMORY["四层记忆体系"]
        style MEMORY stroke:#2563eb,stroke-width:2px
        direction LR
        L1Raw["L1 原始层<br/>逐帧保留"]
        L2Feature["L2 特征层<br/>FAISS 索引"]
        L3Struct["L3 结构层<br/>知识图谱"]
        L4Pattern["L4 模式层<br/>经验学习"]
    end
    
    INPUT --> PERCEIVE
    PERCEIVE -->|"意图与实体"| THINKING
    THINKING -->|"思考链"| PLAN
    THINKING -.->|"置信度"| MEMORY
    PLAN -->|"DAG 工作流"| EXECUTE
    PLAN -.->|"策略"| L4Pattern
    EXECUTE -->|"结果反馈"| PERCEIVE
    EXECUTE -->|"工具调用"| TOOLS
    EXECUTE -->|"学习写入"| L1Raw
    L1Raw --> L2Feature --> L3Struct --> L4Pattern
```

### 7.2 双思考系统详解

```mermaid
flowchart TB
    subgraph INPUT2["用户输入"]
        style INPUT2 stroke:#475569,stroke-width:2px
        ComplexTask["复杂任务或问题"]
    end
    
    subgraph DUAL_INFERENCE["双模型并行推理"]
        style DUAL_INFERENCE stroke:#475569,stroke-width:2px
        direction LR
        Primary["主模型<br/>GPT-4o / Claude 3.5<br/>高质量输出<br/>深度推理<br/>~100-300ms"]
        Secondary["副模型<br/>DeepSeek / 通义千问<br/>低延迟输出<br/>快速响应<br/>~20-50ms"]
    end
    
    subgraph COORD_STRATEGIES["三协同策略 协调器"]
        style COORD_STRATEGIES stroke:#475569,stroke-width:2px
        direction TB
        ArbiterStrategy["仲裁器<br/>比较一致性<br/>选择置信度更高<br/>适用于简单任务"]
        MajorityStrategy["多数投票<br/>多模型投票<br/>取多数共识<br/>适用于中等复杂任务"]
        WeightedStrategy["加权融合<br/>动态权重分配<br/>根据任务类型<br/>自适应调整"]
    end
    
    subgraph CV_LEVELS["四阶交叉验证"]
        style CV_LEVELS stroke:#475569,stroke-width:2px
        direction TB
        NoneCV["无验证 NONE<br/>无验证<br/>单模型直接输出"]
        BasicCV["基础验证 BASIC<br/>结果一致性检查<br/>差异超阈值则重推理"]
        AdvancedCV["高级验证 ADVANCED<br/>置信度评估<br/>仲裁器决策<br/>质量评分"]
        AdaptiveCV["自适应验证 ADAPTIVE<br/>学习历史决策<br/>动态验证级别<br/>性能统计优化"]
    end
    
    subgraph META_LAYER["元认知层"]
        style META_LAYER stroke:#475569,stroke-width:2px
        direction TB
        SelfEval["认知自我评估<br/>不确定性检测<br/>任务复杂度判断"]
        ConfCalibration["置信度校准<br/>概率校准<br/>动态阈值调整"]
        RealtimeCritic["实时评审<br/>监控输出质量<br/>异常中断"]
    end
    
    subgraph THINKING_CHAIN["思维链"]
        style THINKING_CHAIN stroke:#475569,stroke-width:2px
        MultiStepChain["多步推理链<br/>分解复杂任务<br/>链式验证<br/>错误回溯"]
    end
    
    subgraph OUTPUT["输出"]
        style OUTPUT stroke:#475569,stroke-width:2px
        FinalResult["最终答案或动作<br/>附带置信度"]
        PerformanceStats["性能统计<br/>一致性率<br/>平均延迟<br/>决策历史"]
    end
    
    ComplexTask --> Primary
    ComplexTask --> Secondary
    Primary --> ArbiterStrategy
    Primary --> MajorityStrategy
    Primary --> WeightedStrategy
    Secondary --> ArbiterStrategy
    Secondary --> MajorityStrategy
    Secondary --> WeightedStrategy
    ArbiterStrategy --> NoneCV
    ArbiterStrategy --> BasicCV
    ArbiterStrategy --> AdvancedCV
    ArbiterStrategy --> AdaptiveCV
    MajorityStrategy --> NoneCV
    MajorityStrategy --> BasicCV
    MajorityStrategy --> AdvancedCV
    MajorityStrategy --> AdaptiveCV
    WeightedStrategy --> NoneCV
    WeightedStrategy --> BasicCV
    WeightedStrategy --> AdvancedCV
    WeightedStrategy --> AdaptiveCV
    AdvancedCV --> SelfEval
    AdaptiveCV --> SelfEval
    AdaptiveCV --> ConfCalibration
    AdaptiveCV --> RealtimeCritic
    AdaptiveCV --> MultiStepChain
    SelfEval --> FinalResult
    ConfCalibration --> FinalResult
    RealtimeCritic --> FinalResult
    AdaptiveCV -.->|"记录决策历史"| PerformanceStats
```

### 7.3 双思考系统核心组件

| 组件 | 路径 | 功能 | 说明 |
|------|------|------|------|
| **双模型协调器** | coreloopthree/src/cognition/coordinator/dual_model.c | 主副模型协同推理 | 加权融合、交叉验证、置信度评估 |
| **仲裁器** | coreloopthree/src/cognition/coordinator/arbiter.c | 多模型输出仲裁 | 一致性比较、选择最优输出 |
| **多数投票** | coreloopthree/src/cognition/coordinator/majority.c | 多模型投票决策 | 取多数共识，降低幻觉率 |
| **加权融合** | coreloopthree/src/cognition/coordinator/weighted.c | 动态权重分配 | 根据任务类型或历史性能调整 |
| **置信度校准** | coreloopthree/src/cognition/confidence_calibrator.c | 动态校准置信度 | 历史决策统计分析 |
| **元认知** | coreloopthree/src/cognition/metacognition.c | 认知自我评估 | 不确定性检测、任务复杂度判断 |
| **思维链** | coreloopthree/src/cognition/thinking_chain.c | 多步推理链 | 复杂任务分解、链式验证 |
| **流式评审** | coreloopthree/src/cognition/stream_critic.c | 实时输出质量监控 | 异常中断、质量评估 |
| **认知演化** | coreloopthree/src/cognition/cognitive_evolution.c | 学习策略优化 | 自适应调整策略参数 |
| **并行调度** | coreloopthree/src/cognition/parallel_dispatcher.c | 多任务并行处理 | 优先级、轮询、加权、ML 策略 |

### 7.4 交叉验证四阶模式

| 模式 | 复杂度 | 适用场景 | 验证内容 |
|------|--------|---------|----------|
| **NONE** | 最低 | 简单问答 | 无验证，直接输出 |
| **BASIC** | 低 | 中简单任务 | 主副模型一致性检查 |
| **ADVANCED** | 中 | 复杂推理 | 置信度评估与仲裁决策 |
| **ADAPTIVE** | 高 | 关键任务 | 学习历史与动态调整与性能优化 |

### 7.5 认知循环时序

```
用户输入
   | <10ms
   v
+--------------------------------------------------+
| 感知层                                             |
| 上下文处理 -> 意图分类 -> 实体提取                  |
| 输出: {意图, 实体, 上下文}                         |
+------------------------+-------------------------+
                         |
                         v
+--------------------------------------------------+
| 思考层 (Triple Coordinator)                       |
|  +------------------------------------------+    |
|  |  T2: 深度推理 (100-300ms/单元)            |    |
|  |    生成语义单元流 -> 接收批判 -> 修正       |    |
|  +------------------+-----------------------+    |
|                     | 输出语义单元               |
|                     v                             |
|  +------------------+-----------------------+    |
|  |  T1-F: 快速验证 (10-30ms/单元)            |    |
|  |    实时检查 -> 评分 -> 决策矩阵             |    |
|  +------------------+-----------------------+    |
|                     | 评分 <0.3 或多次修正失败    |
|                     v                             |
|  +------------------------------------------+    |
|  |  T1-P: 专业仲裁 (200-500ms)               |    |
|  |    多领域专家验证 -> 最终裁决               |    |
|  +------------------------------------------+    |
|  总延迟: ~200-800ms (取决于循环次数)              |
+------------------------+-------------------------+
                         |
                         v
+--------------------------------------------------+
| 规划层 (<50ms)                                    |
| 分层规划 / 反应式 / 反思式 / ML规划                |
| 输出: DAG 工作流                                   |
+------------------------+-------------------------+
                         |
                         v
+--------------------------------------------------+
| 执行层 (<100ms)                                   |
| 智能体调度 -> 工具调用 -> 状态管理 -> 结果收集      |
| 工具: API/文件/Shell/数据库/代码/浏览器            |
+------------------------+-------------------------+
                         |
                         v
              输出 -> 反馈循环
```

---

## 第八章 Triple Coordinator 三核心组件 (t2/t1-f/t1-p)

### 8.1 Triple Coordinator 组件架构

```mermaid
flowchart TB
    subgraph INPUT3["用户输入或复杂任务"]
        style INPUT3 stroke:#475569,stroke-width:2px
        TaskContext["任务上下文与意图"]
    end
    
    subgraph T2_ENGINE["T2 — Think2 深度推理引擎"]
        style T2_ENGINE stroke:#2563eb,stroke-width:3px
        direction TB
        T2Gen["语义单元生成器<br/>持续输出 token 流<br/>自动分割为语义单元<br/>~100-300ms/单元"]
        T2Correct["修正器<br/>接收 t1-f 批判反馈<br/>修正问题语义单元<br/>重新输出修正版本"]
        T2Complete["执行完成<br/>所有单元验证通过<br/>输出最终推理结果"]
        T2Gen --> T2Correct --> T2Complete
    end
    
    subgraph SEMANTIC_UNITS["语义单元流 — su_stream_detector"]
        style SEMANTIC_UNITS stroke:#475569,stroke-width:2px
        direction TB
        Unit1["单元1: 前提假设"]
        Unit2["单元2: 推理步骤"]
        Unit3["单元3: 中间结论"]
        UnitN["单元N: 最终答案"]
        Unit1 --> Unit2 --> Unit3 --> UnitN
    end
    
    subgraph T1F_ENGINE["T1-F — Fast-Think1 快速验证"]
        style T1F_ENGINE stroke:#f59e0b,stroke-width:3px
        direction TB
        T1FValidate["流式验证器<br/>实时检查每个语义单元<br/>一致性、完整性、安全性<br/>~10-30ms/单元<br/>输出: 分数与批判"]
        T1FDecision["决策矩阵<br/>分数 >=0.7: 接受<br/>分数 >=0.5: 小修<br/>分数 >=0.3: 大修<br/>分数 <0.3: 拒绝"]
        T1FEscalate["异常升级<br/>多次修正失败<br/>高复杂度场景<br/>移交 t1-p 仲裁"]
        T1FValidate --> T1FDecision --> T1FEscalate
    end
    
    subgraph T1P_ENGINE["T1-P — Pro-Think1 专业仲裁"]
        style T1P_ENGINE stroke:#16a34a,stroke-width:3px
        direction TB
        T1PAudit["专业领域审计<br/>多领域专家验证<br/>代码、数学、逻辑、安全<br/>~200-500ms<br/>最终裁决权"]
        T1PResult["仲裁结果<br/>接受<br/>重大修改<br/>拒绝并回退"]
        T1PAudit --> T1PResult
    end
    
    subgraph METACOGNITION2["元认知层"]
        style METACOGNITION2 stroke:#475569,stroke-width:2px
        direction TB
        MetaEval["认知评估<br/>confidence_calibrator"]
        MetaCritic["流式评审<br/>stream_critic"]
    end
    
    TaskContext --> T2Gen
    T2Gen -->|"输出语义单元"| SEMANTIC_UNITS
    SEMANTIC_UNITS -->|"每个单元"| T1FValidate
    T1FDecision -->|"分数 >=0.7 接受"| T2Complete
    T1FDecision -->|"分数 0.5-0.7 小修"| T2Correct
    T1FDecision -->|"分数 0.3-0.5 大修"| T2Correct
    T1FDecision -->|"分数 <0.3 拒绝"| T1FEscalate
    T2Correct -->|"修正后单元"| SEMANTIC_UNITS
    T1FEscalate -->|"升级请求"| T1PAudit
    T1PResult -->|"最终裁决"| T2Complete
    T1FValidate -.->|"实时反馈"| METACOGNITION2
    METACOGNITION2 -.->|"置信度校准"| T1FDecision
```

### 8.2 流式批判循环详解

```
+-------------------------------------------------------------------+
|                        流式批判循环                                  |
+-------------------------------------------------------------------+

步骤 1: T2 生成语义单元
   t2: "假设 f(x) 连续且在 [a,b] 上可导..."
   | (分割为语义单元 su_1)
   v

步骤 2: T1-F 实时验证 (10-30ms)
   t1-f: 检查一致性 通过，完整性 通过，安全性 通过
   评分: 0.85 -> 接受
   |
   v

步骤 3: T2 继续生成下一单元
   t2: "根据拉格朗日中值定理，存在 c 属于 (a,b)..."
   | (分割为语义单元 su_2)
   v

步骤 4: T1-F 验证发现问题
   t1-f: 发现推理跳跃，缺失前提条件
   评分: 0.45 -> 大修
   批判: "需要补充 f(x) 在闭区间连续的条件"
   |
   v

步骤 5: T2 修正问题单元
   t2: (接收批判) 修正为: "设 f(x) 在 [a,b] 上连续，在 (a,b) 上可导..."
   | (重新输出修正后的 su_2')
   v

步骤 6: T1-F 再次验证
   t1-f: 修正后检查通过
   评分: 0.78 -> 接受
   |
   v

步骤 7: 高复杂度场景触发 T1-P
   (若多次修正失败或涉及专业领域)
   t1-p: 专业数学验证 -> 最终裁决 接受或拒绝
```

### 8.3 Triple Coordinator 核心接口

| 组件 | 源码文件 | 职责 | 延迟 |
|------|----------|------|------|
| **T2 (Think2)** | triple_coordinator.c | 深度推理、语义单元生成、接收批判修正 | ~100-300ms/单元 |
| **T1-F (Fast-Think1)** | triple_coordinator.c | 流式验证、实时批判、决策矩阵 | ~10-30ms/单元 |
| **T1-P (Pro-Think1)** | triple_coordinator.c | 专业仲裁、多领域审计、最终裁决 | ~200-500ms |
| **元认知** | metacognition.c | 认知评估、置信度校准、流式评审 | ~5-15ms |

### 8.4 语义单元流与决策矩阵

| T1-F 评分区间 | 决策动作 | T2 响应 | 是否触发 T1-P |
|:-------------:|:--------:|:-------:|:-------------:|
| **>=0.7** | 接受 | 继续生成下一单元 | 否 |
| **0.5 ~ 0.7** | 小修 | 微调当前单元 | 否 |
| **0.3 ~ 0.5** | 大修 | 重构当前单元 | 若 3 次修正失败则触发 |
| **<0.3** | 拒绝 | 回退到上一状态 | 立即触发仲裁 |

---

## 第九章 闭源组件清单

| 组件 | 类型 | 用途 | 是否必须 | 可获得性 | 开源替代 |
|------|------|------|:------:|----------|----------|
| **MemoryRovol Pro** | 商业记忆引擎 | L1-L4 高性能记忆存储检索 | 否 | 联系 SPHARX 获取商业授权 | FAISS + SQLite（默认内置） |

> **开源中立性声明**: 本系统所有闭源或商业组件均设计为**可选、可替换**。不依赖任何闭源组件即可实现全部核心功能。MemoryRovol Pro 默认由 FAISS + SQLite 开源方案替代，功能完整可用。此设计确保本系统捐赠予 **开放原子开源基金会** 后的完全 **开源中立性** 和 **社区自治能力**。

---

## 文档版本

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.0 | 2026-05-14 | 全面重新设计：去除图标符号、边界清晰、专业排版、中文版本 |

> 版权所有 2026 OpenAirymax. 遵循 Apache-2.0 许可证.  
> 捐赠予 **开放原子开源基金会**  
> 仓库: https://atomgit.com/openairymax/agentos
