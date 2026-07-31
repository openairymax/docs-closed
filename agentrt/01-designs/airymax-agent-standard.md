# Airymax Agent 标准 v1.0

> **状态**：基线规范，指导 Python/Rust 双语言实现与 agentrt 适配
> **依据**：4 个参考项目研究（openai-agents-js / codex-rs / jiuwenswarm / agent-store）+ agentrt 现状 + RESTRUCTURE_PLAN 决策
> **范围**：定义 Agent 契约、注册表、工具系统、生命周期、记忆、编排、guardrail 的统一规范

---

## 0. 设计原则

1. **契约驱动**：每个 Agent 由一份 `contract.json` 声明式定义，机器可校验
2. **注册表发现**：统一注册表 + 工厂函数，运行时按 role 实例化
3. **双语言对齐**：Python（`airymax_agents/`）与 Rust（`airymax_agents_rs/`）共享同一契约 schema 与 agent_id 规则
4. **agentrt 适配可选**：Agent 可在纯语言模式（无 agentrt）与 agentrt 增强模式（记忆持久化 + 调度）间无缝切换
5. **best-effort 持久化**：agentrt 集成失败不阻断核心推理（业务可用性优先）

---

## 1. Agent 契约（contract.json）

### 1.1 字段规范

每个 Agent 子目录须含 `contract.json`，字段如下：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `agent_id` | string | 是 | 格式 `^[a-z][a-z0-9_]*_v\d+$`（如 `architect_v1`），全仓唯一 |
| `role` | string | 是 | 角色名（如 `architect`），与目录名一致 |
| `name` | string | 是 | 人类可读名（如 "架构师 Agent"） |
| `description` | string | 是 | 一句话职责描述 |
| `model` | string | 否 | 默认 LLM 模型（可被 contract_overrides 覆盖） |
| `tools` | array<string> | 否 | 工具名列表（引用工具注册表） |
| `handoffs` | array<string> | 否 | 可委派的目标 role 列表 |
| `input_schema` | object | 否 | 输入 JSON Schema（可选） |
| `output_schema` | object | 否 | 输出 JSON Schema（可选） |
| `guardrails` | object | 否 | 输入/输出 guardrail 配置 |
| `metadata` | object | 否 | 自定义元数据 |

### 1.2 目录约定

```
airymax_agents/<role>/
├── agent.py            # Python 实现（继承 AirymaxAgent）
├── contract.json       # 契约
└── prompts/
    └── system.md       # 系统提示词
```

Rust 实现对应 `airymax_agents_rs/crates/<role>_agent/`，共享同一 `contract.json`（通过 `agent-contract` crate 解析）。

---

## 2. 注册表与发现

### 2.1 静态注册表（编译期/启动期）

**Python**：`airymax_agents/__init__.py` 的 `AGENT_REGISTRY: Dict[str, type]`，`get_agent(role, ...) -> AirymaxAgent` 工厂。

**Rust**：`agent-core` crate 的 `registry` 模块，`get_agent(role) -> Box<dyn Agent>`。

### 2.2 运行时注册表

`registry/agents.yaml`：唯一可信执行体清单，含 enabled/implementation_status 字段，供管理器与权限系统引用。

### 2.3 agent_id 一致性

三方对齐：`contract.json.agent_id` == `registry.yaml` 条目 == `permission_rules.yaml` 主体。格式统一 `X_v1`（见 RESTRUCTURE_PLAN 决策 C1）。

---

## 3. 生命周期

### 3.1 状态机

```
                  initialize()
    ┌─────────┐ ───────────────> ┌──────────┐
    │ CREATED │                  │  READY   │
    └─────────┘                  └──────────┘
                                       │
                            execute()  │
                              ┌────────▼─────────┐
                              │     RUNNING      │
                              └────────┬─────────┘
                          ┌────────────┼────────────┐
                   success│      failure│     terminate()│
                          ▼            ▼            ▼
                   ┌──────────┐ ┌──────────┐ ┌──────────┐
                   │ COMPLETED│ │  FAILED  │ │TERMINATED│
                   └──────────┘ └──────────┘ └──────────┘
```

状态值（与 agent_d C 侧 `status` 字段对齐）：
- `1` = RUNNING（spawn 后）
- `2` = COMPLETED
- `3` = TERMINATED
- `4` = FAILED

### 3.2 生命周期接口

**Python（AirymaxAgent）**：
```python
async def initialize() -> None          # 加载契约 + 提示词 + LLM 客户端
async def execute(input_data, context) -> TaskResult   # 核心推理
async def terminate() -> None            # 释放资源
```

**Rust（agent-core trait）**：
```rust
pub trait Agent: Send + Sync {
    fn identity(&self) -> &AgentIdentity;       // agent_id + role + version
    async fn initialize(&mut self) -> Result<()>;
    async fn execute(&mut self, input: AgentInput, ctx: &AgentContext) -> Result<TaskResult>;
    async fn terminate(&mut self) -> Result<()>;
    fn status(&self) -> AgentStatus;
}
```

### 3.3 生命周期 Hook（借鉴 openai-agents-js）

可选 hook，Agent 可覆写：
- `on_before_run(context)` — 推理前
- `on_after_run(context, result)` — 推理后
- `on_tool_call(tool_name, args)` — 工具调用前
- `on_handoff(target_role, payload)` — 委派时

---

## 4. 工具系统

### 4.1 工具定义

每个工具是一个独立单元，含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 工具名（全仓唯一） |
| `description` | string | 功能描述（供 LLM 选择） |
| `parameters` | JSON Schema | 输入参数 schema |
| `invoke(args, context) -> result` | callable | 同步/异步执行 |

### 4.2 工具注册表

独立于 Agent 的工具注册表，Agent 通过 `contract.json.tools` 引用名，运行时解析为可调用实体。

### 4.3 调用协议

- **Python**：工具为 `async def` 函数，参数经 JSON Schema 校验后调用
- **agentrt 集成**：工具调用经 `airy_sys_skill_execute`（若工具作为 skill 注册）或在 Agent 进程内直接调用
- **结果**：返回值 JSON 序列化后回传给 LLM 继续推理

---

## 5. 记忆与会话

### 5.1 记忆记录格式（mem_d）

mem_d 存储的记录结构：

```json
{
  "record_id": "32 字符十六进制",
  "data": "<任意字节，通常 JSON>",
  "metadata": {"agent_id": "...", "task_id": "...", "role": "...", "phase": "input|output"},
  "created_at": 1785494041
}
```

### 5.2 AirymaxAgent 持久化协议

`AirymaxAgent.execute()` 在有 `syscall_proxy` 时：
1. **推理前**：`memory_write(input_payload, metadata={phase:input, agent_id, task_id, role})`
2. **推理后**：`memory_write(result_payload, metadata={phase:output, agent_id, task_id, role, success})`

**best-effort**：持久化异常仅 `logger.warning`，不抛出，保证 LLM 推理不被 agentrt 故障阻断。

### 5.3 检索

`memory_search(query, limit)` 返回 `[(record_id, score), ...]`，score 基于子串匹配密度（无嵌入模型退化方案）。跨会话/跨 Agent 检索通过 metadata 中的 agent_id/task_id 过滤。

### 5.4 持久化（mem_d 落盘）

mem_d 须支持重启不丢数据：
- **格式**：JSONL（每行一条记录，纯 C stdio 实现，无外部依赖）
- **写入**：`memory_write` 成功后追加一行到 `${AIRY_RUNTIME_DIR}/mem.jsonl`
- **删除**：`memory_delete` 后重写整个 JSONL（或标记墓碑，定期 compaction）
- **启动**：`mem_service_create` 时从 JSONL 加载历史记录重建哈希表

---

## 6. 多 Agent 编排

### 6.1 Handoff 模式（借鉴 openai-agents-js）

Agent 可在 `contract.json.handoffs` 声明可委派目标。运行时通过 `agent_invoke` 系统调用委派：

```
Agent_A.execute(input)
  → 若需委派：syscall.agent_invoke(agent_b_id, handoff_payload)
  → Agent_B.execute(handoff_payload)
  → 返回结果给 Agent_A
```

handoff payload 含：原 agent_id、task_id、上下文摘要、委派原因。

### 6.2 Supervisor 模式（借鉴 jiuwenswarm）

Supervisor Agent 编排多个子 Agent：
- 维护 `WorkflowRun` 状态（phase/agent_assignment/status）
- 经 `agent_spawn` 创建子 Agent，`agent_invoke` 分发任务，`agent_terminate` 回收
- 聚合子 Agent 输出（借鉴 agent-store 的 agent_aggregation）

### 6.3 HandoffPort 协议（借鉴 jiuwenswarm）

委派前预检：
- `preflight(target_role, payload) -> bool`：目标是否可接收
- `request_handoff(target_role, payload) -> handoff_result`：执行委派

---

## 7. Guardrail

### 7.1 类型

- **InputGuardrail**：推理前校验输入（如敏感词、长度、格式）
- **OutputGuardrail**：推理后校验输出（如安全过滤、schema 校验）
- **ExecutionRail**：执行期约束（如迭代次数上限、超时，借鉴 agent-store EDPAgent）

### 7.2 接口

```python
class Guardrail:
    name: str
    async def check(input_or_output, context) -> GuardrailResult  # pass/blocked/transformed
```

---

## 8. agentrt 适配

### 8.1 IPC 协议

Python SDK `_IpcBackend` 与 agent_d/mem_d 通过 Unix socket + JSON-RPC 2.0 通信：

```
→ {"jsonrpc":"2.0","method":"write","params":{"data":"...","metadata":{}},"id":1}
← {"jsonrpc":"2.0","result":{"record_id":"..."},"id":1}
```

Socket 路径：`/tmp/agentrt/mem.sock`、`/tmp/agentrt/agent.sock`（由 `AIRY_RUNTIME_DIR` 派生）。

### 8.2 命名空间

| 命名空间 | daemon | 方法 |
|----------|--------|------|
| `mem.*` | mem_d | write / search / get / delete |
| `agent.*` | agent_d | spawn / terminate / invoke / list |
| `a2a.*` | a2a_d | A2A v0.3 协议适配 |

### 8.3 syscall ABI

C 侧 `airy_sys_*` 系统调用签名不变（ABI 稳定），实现迁移到 daemon，gateway 经 thin IPC 转发。

### 8.4 SyscallProxy backend 选择

- `auto`（默认）：FFI 优先，找不到 libagentrt.so 时回退 IPC
- `ffi`：强制 FFI（高性能，需 .so）
- `ipc`：直连 daemon（不依赖 .so，适合 agentrt 作为 STATIC 构建时）

---

## 9. 跨语言映射

| 概念 | Python | Rust | C (agentrt) |
|------|--------|------|-------------|
| Agent 基类 | `AirymaxAgent(LLMAgent)` | `trait Agent` | — |
| 契约 | `contract.json` (dict) | `serde` struct（agent-contract） | — |
| 上下文 | `AgentContext` | `AgentContext` struct | — |
| 状态 | `AgentStatus` enum | `AgentStatus` enum | `status` int 字段 |
| 记忆 | `SyscallProxy.memory_*` | `agent-ffi` extern calls | `mem_service_*` |
| 调度 | `SyscallProxy.agent_*` | `agent-ffi` extern calls | `agent_service_*` |
| agent_id | `X_v1` string | `AgentIdentity` struct | 32 字符 hex（运行时 ID） |

---

## 10. 验证清单

- [ ] 7 个 contract.json 符合字段规范且 agent_id 格式为 `X_v1`
- [ ] `shared/contracts/agent.schema.json` 可校验 contract.json
- [ ] `registry/agents.yaml` 与 contract.json 一致
- [ ] mem_d 重启后数据不丢失（JSONL 持久化）
- [ ] agent_d spawn 实际 fork 子进程并经 invoke 驱动执行
- [ ] `_IpcBackend` pytest 全绿（write/get/search/delete/list + 重试 + 错误容错）
- [ ] `AirymaxAgent.execute` 持久化 best-effort 行为有测试覆盖
- [ ] Rust 骨架 `cargo test` 通过
- [ ] `examples/run_pm.py` Mock 模式 + IPC 模式均跑通
