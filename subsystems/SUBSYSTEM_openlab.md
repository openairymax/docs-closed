# OpenLab 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-18 | **团队**: B
> **代码路径**: `ecosystem/openlab/`

## 1. 职责边界

### 核心职责

| 职责 | 说明 |
|------|------|
| Agent 生命周期管理 | Agent 抽象基类（`initialize` → `execute` → `shutdown`），8 种状态机（CREATED/INITIALIZING/READY/RUNNING/PAUSED/SHUTTING_DOWN/SHUTDOWN/ERROR），线程安全注册表 |
| 任务调度与编排 | 异步任务调度器（`TaskScheduler`），支持优先级队列、并发控制（Semaphore）、超时管理、检查点（checkpoint）保存/恢复、执行计划（`ExecutionPlan`）步骤管理 |
| 工具执行框架 | 工具抽象基类（`Tool`），支持 INPUT_SCHEMA/OUTPUT_SCHEMA 验证、安全前置检查（`_pre_execute_check`）、执行历史记录、6 种工具类别、6 种工具能力 |
| 数据存储抽象 | 存储抽象层（`Storage`），提供 MemoryStorage（内存）和 SQLiteStorage（SQLite）两种实现，支持 TTL 过期、版本号、条件查询、JSON 序列化 |
| 多智能体协作 | 社区贡献的 7 种角色 Agent（Architect/Backend/Frontend/DevOps/Security/Tester/ProductManager），每种 Agent 带有 contract.json 契约和 system prompt |
| 应用生态 | 4 个官方应用（DocGen 文档生成、E-Commerce 电商助手、Research 研究助手、VideoEdit 视频编辑），每个应用有独立的 manifest.json 和 config.yaml |
| 市场与分发 | Agent 和 Skill 的市场注册机制（registry/index.json），安装器 CLI（`markets/agents/installer/`、`markets/skills/installer/`），契约验证（`contract_audit.py`） |
| 策略插件 | 可插拔的调度策略（`contrib/strategies/dispatching/`）和规划策略（`contrib/strategies/planning/`） |
| 协议通信 | 通过 JSON-RPC 2.0 协议与 AgentRT 核心运行时集成 |
| 异常处理 | 完整的异常层级：`OpenLabError` → `AgentError`/`TaskError`/`ToolError`/`StorageError`/`ValidationError`，每类包含 2-3 个子异常 |

### 非职责（明确排除）

- 不负责底层数据持久化存储引擎（由 heapstore/Checkpoint 负责）
- 不负责配置管理与分发（由 Manager 负责）
- 不负责系统级日志收集（由 heapstore 日志子系统负责）
- 不负责网络通信协议实现（由 protocols 层负责）
- 不负责安全认证与授权（由 Manager 安全策略负责）
- 不负责 LLM 模型调用（Agent 通过工具系统间接调用）

## 2. 公共接口

### 核心文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `openlab/__init__.py` | Python 包 | 模块入口，导出所有核心类 |
| `openlab/core/agent.py` | Python 模块 | Agent 基类、状态、注册表、上下文、消息 |
| `openlab/core/task.py` | Python 模块 | 任务定义、状态机、调度器、执行计划 |
| `openlab/core/tool.py` | Python 模块 | 工具抽象、注册表、执行器 |
| `openlab/core/storage.py` | Python 模块 | 存储抽象、MemoryStorage、SQLiteStorage |
| `openlab/utils/exceptions.py` | Python 模块 | 异常层级定义 |
| `openlab/utils/logging.py` | Python 模块 | 日志配置 |
| `openlab/protocols/__init__.py` | Python 模块 | 协议处理模块 |
| `openlab/agents/architect/agent.py` | Python 模块 | 预构建架构师 Agent |
| `pyproject.toml` | 构建配置 | 项目依赖、构建系统、工具配置 |

### 关键 API 签名

```python
# === Agent 管理 (openlab.core.agent) ===
class Agent(ABC):
    agent_id: str
    capabilities: Set[AgentCapability]
    manager: Optional[Any]
    workbench_id: Optional[str]
    status: AgentStatus  # property

    async def initialize(self) -> None                 # 抽象方法
    async def execute(self, input_data: Any, context: AgentContext) -> TaskResult  # 抽象方法
    async def shutdown(self) -> None                   # 抽象方法
    async def handle_message(self, message: Message) -> Optional[Message]
    def register_tool(self, name: str, tool: Any) -> None
    def get_tool(self, name: str) -> Optional[Any]

class AgentRegistry:
    async def register(self, agent: Agent) -> bool
    async def unregister(self, agent_id: str) -> bool
    async def get(self, agent_id: str) -> Optional[Agent]
    async def list_agents(self) -> List[Agent]
    async def count(self) -> int

# === 任务调度 (openlab.core.task) ===
class TaskScheduler:
    def __init__(self, max_concurrent: int = 100, max_queue_size: int = 10000)
    async def submit(self, definition: TaskDefinition) -> str
    async def schedule(self, definition: TaskDefinition, executor: Callable) -> asyncio.Task
    async def get_state(self, task_id: str) -> Optional[TaskState]
    async def cancel(self, task_id: str) -> bool
    async def save_checkpoint(self, task_id: str, checkpoint_data: Dict) -> bool
    async def load_checkpoint(self, task_id: str) -> Optional[Dict[str, Any]]
    async def shutdown(self, wait: bool = True, timeout: Optional[float] = None) -> None
    def get_stats(self) -> Dict[str, Any]

# === 工具系统 (openlab.core.tool) ===
class Tool(ABC):
    NAME: str
    DESCRIPTION: str
    CATEGORY: ToolCategory
    CAPABILITIES: Set[ToolCapability]
    INPUT_SCHEMA: Optional[Dict]
    OUTPUT_SCHEMA: Optional[Dict]

    async def execute(self, parameters: Dict, context: Optional[ToolContext] = None) -> ToolResult
    async def _do_execute(self, parameters: Dict, context: ToolContext) -> ToolResult  # 抽象方法
    async def _pre_execute_check(self, parameters: Dict, context: ToolContext) -> tuple[bool, Optional[str]]
    def get_info(self) -> Dict[str, Any]

class ToolRegistry:
    async def register(self, tool: Tool) -> bool
    async def unregister(self, tool_id: str) -> bool
    async def get(self, tool_id: str) -> Optional[Tool]
    async def list_tools(self) -> List[Tool]
    async def find_by_category(self, category: ToolCategory) -> List[Tool]
    async def find_by_capability(self, capability: ToolCapability) -> List[Tool]

class ToolExecutor:
    def __init__(self, max_concurrent: int = 50, default_timeout: float = 60.0)
    async def register_tool(self, tool: Tool) -> bool
    async def execute(self, tool_id: str, parameters: Dict, context: Optional[ToolContext] = None) -> ToolResult
    async def shutdown(self, wait: bool = True) -> None
    def get_stats(self) -> Dict[str, Any]

# === 存储系统 (openlab.core.storage) ===
class Storage(ABC):
    async def initialize(self) -> None
    async def close(self) -> None
    async def get(self, key: str) -> Optional[StorageRecord]
    async def set(self, key: str, value: Any, category: DataCategory, metadata: Dict, ttl: float) -> bool
    async def delete(self, key: str) -> bool
    async def exists(self, key: str) -> bool
    async def query(self, category: DataCategory, filter_func: callable, offset: int, limit: int) -> QueryResult
    async def clear(self) -> None
    async def get_json(self, key: str) -> Optional[Any]
    async def set_json(self, key: str, value: Any, **kwargs) -> bool

class MemoryStorage(Storage): ...
class SQLiteStorage(Storage): ...
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| `TOOL_DISABLED` | 工具已禁用 |
| `INVALID_INPUT` | 输入参数无效 |
| `SECURITY_CHECK_FAILED` | 安全前置检查失败 |
| `EXECUTION_ERROR` | 工具执行异常 |
| `TIMEOUT` | 执行超时 |
| `TOOL_NOT_FOUND` | 工具未找到 |
| `EXECUTOR_SHUTDOWN` | 执行器已关闭 |

**异常层级**：

```
OpenLabError
├── AgentError
│   ├── AgentInitializationError
│   ├── AgentExecutionError
│   └── AgentNotFoundError
├── TaskError
│   ├── TaskCreationError
│   ├── TaskExecutionError
│   └── TaskNotFoundError
├── ToolError
│   ├── ToolInitializationError
│   ├── ToolExecutionError
│   └── ToolNotFoundError
├── StorageError
│   ├── StorageConnectionError
│   ├── StorageReadError
│   └── StorageWriteError
└── ValidationError
    ├── InputValidationError
    └── ConfigurationError
```

## 3. 依赖关系

### 内部依赖

| 依赖模块 | 用途 |
|----------|------|
| AgentRT protocols 层 | JSON-RPC 2.0 协议通信 |
| `openlab.core.agent` | Agent 基类与注册表（被所有 Agent 实现依赖） |
| `openlab.core.task` | 任务调度器（被 App 层和 Agent 层依赖） |
| `openlab.core.tool` | 工具执行框架（被 Agent 层依赖） |
| `openlab.core.storage` | 数据存储抽象（被 TaskScheduler 和 Agent 层依赖） |

### 运行时依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | ≥ 3.10 | 运行环境 |
| asyncio | 标准库 | 异步 I/O |
| sqlite3 | 标准库 | SQLite 存储后端 |
| fastapi | ≥ 0.104.0 | Web API 框架 |
| uvicorn | ≥ 0.24.0 | ASGI 服务器 |
| sqlalchemy | ≥ 2.0.0 | ORM 框架 |
| pydantic | ≥ 2.4.0 | 数据验证 |
| pyyaml | ≥ 6.0.0 | YAML 配置解析 |
| redis | ≥ 5.0.0 | 缓存（可选） |
| jinja2 | ≥ 3.1.0 | 模板渲染（DocGen） |
| pytest | ≥ 7.4.0 | 测试框架 |
| pytest-asyncio | ≥ 0.21.0 | 异步测试支持 |

### 被依赖方

| 消费模块 | 使用接口 |
|----------|----------|
| Manager | 通过 TaskManager/SessionManager/MemoryManager/SkillManager 调用 OpenLab 核心（基准测试） |
| 外部开发者 | 通过 `openlab` CLI 和 `pyproject.toml` 入口点使用生态系统 |
| CI/CD 流水线 | 通过 `pytest` 运行 `tests/` 下的单元测试 |

## 4. 配置参数

核心配置文件 `openlab/config.yaml`：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `app.name` | `string` | `OpenLab` | 应用名称 |
| `app.version` | `string` | `0.1.0` | 版本号 |
| `app.environment` | `string` | `development` | 运行环境 |
| `app.debug` | `bool` | `true` | 调试模式 |
| `logging.level` | `string` | `INFO` | 日志级别 |
| `logging.format` | `string` | `json` | 日志格式 |
| `logging.output` | `string` | `stdout` | 日志输出 |
| `agent.max_instances` | `int` | `100` | 最大 Agent 实例数 |
| `agent.shutdown_timeout` | `float` | `30.0` | Agent 关闭超时（秒） |
| `agent.health_check_interval` | `float` | `60.0` | 健康检查间隔（秒） |
| `scheduler.max_concurrent` | `int` | `100` | 最大并发任务数 |
| `scheduler.max_queue_size` | `int` | `10000` | 最大队列大小 |
| `scheduler.default_timeout` | `float` | `300.0` | 默认超时（秒） |
| `scheduler.retry_base_delay` | `float` | `1.0` | 重试基础延迟（秒） |
| `scheduler.retry_max_delay` | `float` | `60.0` | 重试最大延迟（秒） |
| `tool.max_concurrent` | `int` | `50` | 工具最大并发执行数 |
| `tool.default_timeout` | `float` | `60.0` | 工具默认超时（秒） |
| `tool.pool_size` | `int` | `10` | 工具池大小 |
| `storage.backend` | `string` | `sqlite` | 存储后端（memory/sqlite） |
| `storage.path` | `string` | `./data/openlab.db` | SQLite 数据库路径 |
| `storage.wal_mode` | `bool` | `true` | WAL 模式 |
| `storage.busy_timeout` | `float` | `30.0` | 数据库忙超时（秒） |

## 5. 跨团队接口合约

### 合约文件

| 合约 | 文件 | 说明 |
|------|------|------|
| Agent 契约 | `contrib/agents/*/contract.json` | 7 种角色 Agent 的输入/输出契约定义 |
| 应用清单 | `app/*/manifest.json` | 应用的元数据、依赖、入口点定义 |
| 市场索引 | `markets/agents/registry/index.json` | Agent 市场注册索引 |
| 市场索引 | `markets/skills/registry/index.json` | Skill 市场注册索引 |
| 项目构建 | `pyproject.toml` | 包依赖、入口点、工具配置 |

### 测试接口

| 测试文件 | 覆盖范围 |
|----------|----------|
| `tests/unit/test_agent.py` | Agent 基类、注册表、状态机 |
| `tests/unit/test_task.py` | TaskScheduler、TaskState、ExecutionPlan |
| `tests/unit/test_tool.py` | Tool 基类、ToolRegistry、ToolExecutor |
| `tests/unit/test_storage.py` | MemoryStorage、SQLiteStorage |
| `tests/unit/test_planning.py` | 规划策略 |
| `tests/unit/test_dispatching.py` | 调度策略 |
| `tests/unit/test_contract_consistency.py` | Agent 契约一致性验证 |
| `tests/unit/test_videoedit.py` | VideoEdit 应用测试 |
| `tests/conftest.py` | 测试 fixtures 和配置 |

## 6. 文件所有权

```
@owner: team-B
```

## 7. 变更记录

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v1.0.0 | 2026-06-18 | 初始版本，基于 OpenLab 代码分析创建 | team-B |