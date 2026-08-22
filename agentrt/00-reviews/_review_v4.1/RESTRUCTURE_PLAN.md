# Agent 执行体集中化重构方案

> **状态**：已确认，实施中
> **范围**：`airymaxhub/ecosystem/agents/` 及 agentrt daemon 扩展
> **依据**：4 个参考项目研究 + agentrt 现状精确调研 + 用户决策

## 用户已确认的决策

| 决策 | 选定方案 |
|------|----------|
| A. Python 接入 agentrt | A1: FFI 优先（SyscallProxy ctypes） |
| B. Rust Agent 范围 | B2: 骨架 + 1-2 个样板（**CodingAgent 为最重要样板**） |
| C. agent_id 格式 | C1: `X_v1`（符合 schema） |
| D. framework/ 重型框架 | D1: 重命名冲突类型（AgentContext→AppContext, AgentStatus→AppState） |
| E. 历史遗留清理 | 删除 broken architect / 修复 registry.yaml / 删除空 coding/ |
| F. 新增 daemon | **创建全功能 daemon**：agent_d / a2a_d / mem_d，从 syscall_router.c 抽离逻辑，gateway 经 Unix socket IPC 调用 |

---

## 1. 现状诊断（基于精确调研）

### 1.1 分散点（共 8 处）

| # | 位置 | 内容 | 状态 |
|---|------|------|------|
| 1 | [ecosystem/agents/airymax_agents/](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/agents/airymax_agents/) | 7 个 Python Agent（stub 实现，契约驱动） | ✅ 可用但孤立 |
| 2 | [ecosystem/openlab/openlab/agents/](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/agents/) | `LLMAgent` 基类 + 1 个历史 `ArchitectAgent` | ⚠️ 基类被依赖，历史 Agent 已坏 |
| 3 | [ecosystem/openlab/openlab/core/agent.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/core/agent.py) | `Agent` ABC + `AgentRegistry` + `AgentContext/Status/Capability` | 基类层 |
| 4 | [sdk/sdk-python/agentrt/](file:///home/spharx/SpharxWorks/airymaxhub/sdk/sdk-python/agentrt/) | `AgentRT`/`AsyncAgentRT` HTTP 客户端 + `SyscallProxy` ctypes FFI + `framework/` 独立重型框架 | ⚠️ FFI 未被业务 Agent 引用 |
| 5 | [ecosystem/openlab/markets/agents/](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/markets/agents/) | `AgentInstaller`/`AgentCLI`/`AgentContractValidator` | 市场安装器 |
| 6 | [ecosystem/manager/agent/registry.yaml](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/manager/agent/registry.yaml) | 12 个 Agent 配置，**contract_path 全指向已删除的 `contrib/agents/`** | ❌ 配置失效 |
| 7 | [products/desktop/src-tauri/src/](file:///home/spharx/SpharxWorks/airymaxhub/products/desktop/src-tauri/src/) | Rust `get_agent_details` Tauri 命令 | 桌面端入口 |
| 8 | [agentrt/gateway/src/utils/syscall_router.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/gateway/src/utils/syscall_router.c) | C 侧 `airy_sys_agent_spawn/invoke/terminate/list` | ✅ 系统调用层 |

### 1.2 重复造轮子

| 重复项 | 位置 | 严重度 |
|--------|------|--------|
| 两套 Agent 框架 | openlab（轻量 `Agent`+`LLMAgent`）vs sdk-python/framework（重型 250KB+ `AgentApplication`） | 高 |
| 两个同名 `AgentContext` | [openlab/core/agent.py#L67](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/core/agent.py#L67) vs [sdk-python/framework/application.py#L145](file:///home/spharx/SpharxWorks/airymaxhub/sdk/sdk-python/agentrt/framework/application.py#L145) | 高 |
| 两个同名 `AgentStatus` | [openlab/core/agent.py#L21](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/core/agent.py#L21) vs [markets/client/models.py#L28](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/markets/client/models.py#L28) | 中 |
| 两套 Agent 注册表 | [openlab/core/agent.py#L387](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/core/agent.py#L387)（async）vs [airymax_agents/__init__.py#L33](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/agents/airymax_agents/__init__.py#L33)（sync dict） | 中 |
| 两个同名 `ArchitectAgent` | [airymax_agents/architect/agent.py#L11](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/agents/airymax_agents/architect/agent.py#L11)（新，可用）vs [openlab/agents/architect/agent.py#L27](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/agents/architect/agent.py#L27)（旧，签名不兼容） | 高 |

### 1.3 三种 agent_id 格式（不一致）

| 格式 | 来源 | 示例 | 符合 schema？ |
|------|------|------|---------------|
| `com.airymax.X.v1` | contract.json | `com.airymax.architect.v1` | ❌ 含点号 |
| `X_v1` | registry.yaml | `architect_v1` | ✅ 符合 `^[a-z][a-z0-9_]*_v\d+$` |
| `X` | permission_rules.yaml | `architect` | ❌ 无版本后缀 |

schema 在 [agent-registry.schema.json#L39](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/manager/schema/agent-registry.schema.json#L39) 规定 `^[a-z][a-z0-9_]*_v\d+$`。

### 1.4 三层配置不一致

| 层 | Agent 数 | 来源 |
|----|----------|------|
| schema 允许 | 12 角色 | [agent-registry.schema.json](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/manager/schema/agent-registry.schema.json) |
| registry.yaml 定义 | 12（5 个无实现） | [registry.yaml](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/manager/agent/registry.yaml) |
| permission_rules.yaml 配置 | 7 | [permission_rules.yaml](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/manager/security/permission_rules.yaml) |
| airymax_agents 实现 | 7 | [airymax_agents/](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/agents/airymax_agents/) |

### 1.5 核心 gap：业务 Agent 与 agentrt 完全断链

`rg -l "airy_sys_agent|agentrt.syscall"` 全仓**仅命中 sdk-python/agentrt/syscall.py 一个文件**。

7 个 Python Agent 直接调 OpenAI 兼容 LLM API，**既不走 FFI 也不走 HTTP**，是纯 Python 孤岛。

---

## 2. 参考项目研究精华

| 项目 | 语言 | 最值得借鉴的设计 |
|------|------|------------------|
| **agent-store-main** | Python | YAML frontmatter + Markdown body 双语义契约；Rail 钩子链；HITL Cascade；配置驱动工具 schema；`community/EDPAgent` 完整参考 |
| **codex-main** | Rust 95.7% | Cargo workspace 40+ crate 划分；`Agent` trait + `agent-identity`/`apply-patch`/`sandboxing`/`code-mode` 独立 crate；`spawn_agent` via `runner.rs`；seccomp/landlock 沙箱 |
| **openai-agents-js-main** | TypeScript | `Agent` 类含 `handoffs`/`outputType`(Zod)；`Runner`/`AgentLoop` 生命周期；`AgentToolSourceRegistry`（Agent 即工具）；pnpm workspace `packages/` 划分 |
| **jiuwenswarm-develop** | Rust + Python | `AgentTrait`；swarm orchestrator；消息总线；`registry/` 动态注册 |

**共性**：契约驱动 + 注册表 + 工具系统 + 生命周期管理 + 多 Agent 编排。
**对 Airymax 的关键启示**：codex-rs 的 workspace 多 crate 划分是 Rust Agent 执行体的最佳实践；openai-agents-js 的 handoff 模式适合多 Agent 协作；agent-store 的双语义契约可借鉴。

---

## 3. 集中化方案

### 3.1 用户决策约束（不可违背）

1. **agentrt 核心平台（`airymaxhub/agentrt/`）只能用纯 C** —— 与 agent-linux 同源
2. **所有 Agent 执行体集中到 `airymaxhub/ecosystem/agents/`** —— Agent 可用 Rust 或 Python 实现
3. **减少重复造轮子**

### 3.2 新目录结构

```
airymaxhub/ecosystem/agents/
├── README.md
├── RESTRUCTURE_PLAN.md           # 本文档
│
├── airymax_agents/               # 【保留】Python Agent 执行体（现有 7 个）
│   ├── __init__.py               # AGENT_REGISTRY + get_agent() + list_agents()
│   ├── base.py                   # AirymaxAgent(LLMAgent) 基类
│   ├── product_manager/          # 每个 Agent: agent.py + contract.json + prompts/system.md
│   ├── architect/
│   ├── backend/
│   ├── frontend/
│   ├── devops/
│   ├── security/
│   ├── tester/
│   └── (删除空的 coding/ 目录)
│
├── airymax_agents_rs/             # 【新增】Rust Agent 执行体（Cargo workspace，仿 codex-rs）
│   ├── Cargo.toml                 # workspace 根
│   ├── crates/
│   │   ├── agent-core/            # Rust Agent trait + 生命周期 + 上下文
│   │   │   ├── Cargo.toml
│   │   │   └── src/
│   │   │       ├── lib.rs
│   │   │       ├── agent.rs       # trait Agent { fn run(); fn stop(); fn identity(); }
│   │   │       ├── context.rs     # AgentContext（与 Python 侧对齐字段名）
│   │   │       └── status.rs      # AgentStatus 枚举
│   │   ├── agent-ffi/             # FFI 绑定 agentrt C 系统调用（libagentrt.so）
│   │   │   └── src/
│   │   │       ├── lib.rs
│   │   │       └── syscalls.rs     # extern "C" { airy_sys_agent_spawn ... }
│   │   ├── agent-contract/        # 契约解析与校验（serde + JSON Schema）
│   │   │   └── src/
│   │   │       └── schema.rs       # 与 Python contract.json 共享同一 schema
│   │   └── (后续按需添加具体 Rust Agent crate)
│   └── tests/
│
├── shared/                       # 【新增】跨语言共享资源
│   ├── contracts/
│   │   ├── agent.schema.json     # contract.json 的 JSON Schema（机器可校验）
│   │   └── README.md             # 引用 docs 中的 01-agent-contract.md 规范
│   └── prompts/                  # 跨 Agent 共享的提示词片段（可选）
│
├── registry/                    # 【新增】统一执行体注册表（运行时引用）
│   └── agents.yaml               # 唯一可信执行体清单（替代 manager/agent/registry.yaml 的执行体部分）
│
└── examples/
    └── run_pm.py                 # 现有端到端示例
```

### 3.3 关键设计决策

#### 决策 A：Python Agent 接入 agentrt 的方式

| 选项 | 机制 | 优点 | 缺点 |
|------|------|------|------|
| A1（推荐） | 通过 [sdk-python/agentrt/syscall.py](file:///home/spharx/SpharxWorks/airymaxhub/sdk/sdk-python/agentrt/syscall.py) 的 `SyscallProxy`（ctypes FFI） | 高性能；已实现；无需额外 daemon | 需 `libagentrt.so` 可加载 |
| A2 | 通过 [sdk-python/agentrt/agent.py](file:///home/spharx/SpharxWorks/airymaxhub/sdk/sdk-python/agentrt/agent.py) 的 `AgentRT`（HTTP:18789） | 解耦；跨进程 | 需 agentrt HTTP 服务运行 |
| A3 | 两者都支持，配置选择 | 灵活 | 复杂度上升 |

**推荐 A1**：在 `airymax_agents/base.py` 的 `AirymaxAgent` 中注入 `SyscallProxy`，让 `execute()` 可选调用 `airy_sys_memory_write/search` 持久化上下文，`airy_sys_agent_invoke` 委派子 Agent。LLM 调用仍走 OpenAI 兼容 API（`make_llm_client`），agentrt 负责记忆/调度/委派，不负责 LLM 推理。

#### 决策 B：Rust Agent 执行体本次是否实现

| 选项 | 范围 | 说明 |
|------|------|------|
| B1（推荐） | 本次只搭骨架（workspace + agent-core + agent-ffi + agent-contract），不实现具体业务 Rust Agent | 骨架就位后，后续按需添加；避免本次范围爆炸 |
| B2 | 本次实现 1-2 个 Rust Agent 作为样板（如 `rust_reviewer`） | 验证骨架可用性，但增加工作量 |
| B3 | 本次不引入 Rust | 简化但违背"双语言"决策 |

**推荐 B1**：搭骨架，留接口；后续按需添加具体 Rust Agent。

#### 决策 C：agent_id 格式统一

| 选项 | 格式 | 影响 |
|------|------|------|
| C1（推荐） | `X_v1`（如 `architect_v1`）符合现有 schema | 重写 7 个 contract.json 的 `agent_id` 字段；registry.yaml/permission_rules 已基本对齐 |
| C2 | `com.airymax.X.v1`（保留现有 contract.json 格式） | 需修改 schema pattern；与 registry.yaml 不一致 |
| C3 | `X`（纯角色名） | 无版本，不可演进 |

**推荐 C1**：统一为 `X_v1`，重写 7 个 contract.json。

#### 决策 D：sdk-python/framework/ 重型框架处理

| 选项 | 处理 | 说明 |
|------|------|------|
| D1（推荐） | 保留但重命名内部冲突类型（`AgentContext` → `AppContext`、`AgentStatus` → `AppState`） | 消除与 openlab 同名冲突；保留 SDK 框架独立性 |
| D2 | 删除 framework/，统一用 openlab | 减少重复但丢失重型框架能力 |
| D3 | 合并 framework/ 进 openlab | 工作量大，风险高 |

**推荐 D1**：重命名冲突类型，不合并框架。

#### 决策 E：历史遗留清理

- **删除** [openlab/openlab/agents/architect/](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/agents/architect/)（签名不兼容，已被 try/except 包裹）
- **修复** [openlab/openlab/agents/__init__.py#L8](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/agents/__init__.py#L8) 过期文档（仍引用已删除的 `contrib/agents/`）
- **修复** [manager/agent/registry.yaml](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/manager/agent/registry.yaml) 12 个 `contract_path` → 重指到 `ecosystem/agents/airymax_agents/<role>/contract.json`
- **删除** [airymax_agents/coding/](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/agents/airymax_agents/coding/) 空目录
- **对齐** registry.yaml：5 个无实现的 Agent（data_engineer/coordinator/reviewer/analyst/custom）设 `enabled: false` + `implementation_status: planned`

#### 决策 F：新增 agent_d / a2a_d / mem_d 全功能 daemon（用户已确认）

**核查结论**：这三个 daemon 在代码中完全不存在（无目录、无源码、无头文件），但 [L2 服务协议](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxRT/30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md#L333-336) 规划为 12 daemon 之三。功能当前由 [syscall_router.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/gateway/src/utils/syscall_router.c) 的 `airy_sys_agent_*` / `airy_sys_memory_*` 进程内联实现。项目审查 [02-closed-docs-review.md#L309-311](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agentrt/00-reviews/_review_v4.0/02-closed-docs-review.md#L309-311) 已记录此缺失。

**实施**（用户选定"创建全功能 daemon"）：

1. 在 `agentrt/daemons/` 下新建 `agent_d/` / `a2a_d/` / `mem_d/` 三个目录，遵循现有 daemon 模式（如 [tool_d](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/tool_d/)）：每个含 `CMakeLists.txt` + `include/*.h` + `src/{main.c, service.c, service.h, *_svc_adapter.c}` + `tests/` + `README.md`
2. 从 [syscall_router.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/gateway/src/utils/syscall_router.c) 抽离 `airy_sys_agent_spawn/terminate/invoke/list` → `agent_d`；`airy_sys_memory_write/search/get/delete` → `mem_d`；A2A 协议适配 → `a2a_d`
3. daemon 通过 Unix socket 暴露服务：`/var/run/agentrt/agent.sock` / `a2a.sock` / `mem.sock`
4. `syscall_router.c` 改为 thin IPC client，经 Unix socket 转发请求到对应 daemon
5. 更新 [daemons/CMakeLists.txt](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/CMakeLists.txt) 添加三个新 daemon
6. daemon 命名空间对齐：`agent.*` → agent_d，`mem.*` → mem_d，`a2a.*` → a2a_d（当前 a2a 由 sched_d 服务，需迁移）

### 3.4 接入 agentrt 系统调用的设计

`AirymaxAgent` 基类增强（伪代码）：

```python
class AirymaxAgent(LLMAgent):
    def __init__(self, ..., syscall_proxy: Optional[SyscallProxy] = None):
        super().__init__(...)
        self._sys = syscall_proxy  # None 时退化为纯 Python 模式（向后兼容）

    async def execute(self, input_data, context):
        # 1. 可选：将上下文写入 agentrt 记忆
        if self._sys:
            self._sys.memory_write(session_id, {"input": input_data})
        # 2. LLM 推理（现有逻辑）
        result = await super().execute(input_data, context)
        # 3. 可选：持久化结果
        if self._sys:
            self._sys.memory_write(session_id, {"output": result})
        return result
```

向后兼容：`syscall_proxy=None` 时行为与现有一致（纯 Python LLM 模式，MockLLMClient 可跑）。

---

## 4. 实施步骤（按依赖顺序）

### 阶段 1：清理与对齐（无破坏性）

1. 删除 [airymax_agents/coding/](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/agents/airymax_agents/coding/) 空目录
2. 删除 [openlab/openlab/agents/architect/](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/agents/architect/)（已坏的历史 Agent）
3. 修复 [openlab/openlab/agents/__init__.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/agents/__init__.py) 过期文档
4. 修复 [manager/agent/registry.yaml](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/manager/agent/registry.yaml) 的 12 个 `contract_path`
5. 统一 7 个 contract.json 的 `agent_id` 为 `X_v1` 格式
6. registry.yaml 中 5 个无实现的 Agent 设 `enabled: false`

### 阶段 2：消除同名冲突

7. 重命名 [sdk-python/framework/application.py](file:///home/spharx/SpharxWorks/airymaxhub/sdk/sdk-python/agentrt/framework/application.py) 的 `AgentContext` → `AppContext`
8. 重命名 `AgentStatus` → `AppState`（framework/lifecycle.py）
9. 更新所有引用

### 阶段 3：新增 3 个 C daemon（agent_d / a2a_d / mem_d）

10. 研究现有 daemon 模式（[tool_d](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/tool_d/) / [llm_d](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/llm_d/)）与 [syscall_router.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/gateway/src/utils/syscall_router.c) 的 `airy_sys_agent_*` / `airy_sys_memory_*` 实现
11. 创建 `agentrt/daemons/mem_d/`：CMakeLists.txt + include/mem_service.h + src/{main.c, service.c, service.h, mem_svc_adapter.c} + tests/ + README.md；承载 `mem.*` 命名空间（memory_write/search/get/delete）
12. 创建 `agentrt/daemons/agent_d/`：同结构；承载 `agent.*` 命名空间（agent_spawn/terminate/invoke/list）
13. 创建 `agentrt/daemons/a2a_d/`：同结构；承载 `a2a.*` 命名空间（A2A v0.3 协议适配，从 [protocols/standards/a2a](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/protocols/standards/a2a/) 迁移）
14. 更新 [daemons/CMakeLists.txt](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/CMakeLists.txt) 添加三个新 daemon
15. 更新 [syscall_router.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/gateway/src/utils/syscall_router.c) 改为 thin IPC client，经 Unix socket 转发到 daemon
16. daemon 单元测试（tests/test_*.c）

### 阶段 4：Python Agent 接入 agentrt（FFI）

17. 在 [airymax_agents/base.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/agents/airymax_agents/base.py) 的 `AirymaxAgent` 中注入可选 `SyscallProxy`
18. 增强 `execute()` 在有 syscall_proxy 时调用 `airy_sys_memory_*` / `airy_sys_agent_invoke`
19. 更新 [examples/run_pm.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/agents/examples/run_pm.py) 验证 FFI 模式

### 阶段 5：Rust Agent 骨架 + CodingAgent 样板

20. 创建 `airymax_agents_rs/Cargo.toml`（workspace）
21. 创建 `crates/agent-core/`（Agent trait + Context + Status）
22. 创建 `crates/agent-ffi/`（extern "C" 绑定 `airy_sys_*`）
23. 创建 `crates/agent-contract/`（serde 解析 contract.json）
24. 创建 `crates/coding_agent/`（**CodingAgent 样板**，最重要）
25. `cargo test` 验证骨架

### 阶段 6：共享资源

26. 创建 `shared/contracts/agent.schema.json`（机器可校验的 JSON Schema）
27. 创建 `registry/agents.yaml`（运行时引用的执行体清单）

### 阶段 7：验证

28. 跑通 `examples/run_pm.py`（无 API key 的 Mock 模式）
29. 跑通 Rust 骨架的 `cargo test`
30. C daemon 构建 + 单元测试
31. 验证 contract.json 符合 schema

---

## 5. 影响分析

### 不变（向后兼容）

- openlab `Agent` ABC + `LLMAgent` 基类的核心逻辑
- 现有 7 个 Python Agent 的目录结构与契约
- sdk-python 的 HTTP 客户端 + FFI 层的现有 API
- `airy_sys_agent_*` / `airy_sys_memory_*` 对外 C 接口签名（实现迁移到 daemon，但 ABI 不变）

### 新增

- `agentrt/daemons/agent_d/` / `a2a_d/` / `mem_d/` 三个全功能 C daemon
- `airymax_agents_rs/` Rust workspace（agent-core / agent-ffi / agent-contract / coding_agent）
- `shared/contracts/agent.schema.json`
- `registry/agents.yaml`
- `AirymaxAgent` 的可选 `SyscallProxy` 注入
- Unix socket IPC：`/var/run/agentrt/{agent,a2a,mem}.sock`

### 删除

- `airymax_agents/coding/`（空目录）
- `openlab/openlab/agents/architect/`（历史坏 Agent）

### 修改

- 7 个 contract.json 的 `agent_id` 格式（`com.airymax.X.v1` → `X_v1`）
- `registry.yaml` 的 12 个 `contract_path`
- `sdk-python/framework/` 的 2 个同名类型重命名
- `AirymaxAgent` 基类增强（可选 syscall_proxy）
- [syscall_router.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/gateway/src/utils/syscall_router.c) 改为 thin IPC client
- [daemons/CMakeLists.txt](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/CMakeLists.txt) 添加 3 个新 daemon
