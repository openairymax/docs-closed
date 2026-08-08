Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"From data intelligence emerges."

# Agent 运行时与网关协议边界接线设计方案（agent_d + gateway）
> **文档定位**：agentrt 用户态运行时「全量启动」接线方案——打通 agent_d（驱动 ecosystem/agents）、gateway 协议边界、mem_d 记忆服务三链路的**设计方案**（DRAFT，待确认后实施）\
> **文档状态**：DRAFT（待确认）\
> **最后更新**：2026-08-06\
> **上级文档**：[AgentRT 文档中心](../../README.md)\
> **关联文档**：[工作大厅 08-work-hall.md](../../../../docs/AirymaxRT/10-architecture/08-work-hall.md)、[系统架构 01-system-architecture.md](../../../../docs/AirymaxRT/10-architecture/01-system-architecture.md)、[L2 服务协议 02-l2-service-protocol.md](../../../../docs/AirymaxRT/30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md)

---

## 1. 背景与目标

### 1.1 现状（已确认的真问题）

agentrt 15 个 daemon 均已启动，但存在三处**已设计、未接线**的链路：

| 链路 | 设计依据 | 现状 |
|------|---------|------|
| agent_d 驱动 `ecosystem/agents` | [08-work-hall.md](./08-work-hall.md#54) 节点 handler → `agent_d`（spawn/invoke）| agent.spawn/invoke 无运行期调用方（仅 `airy_cli` 的 Work Hall 触发）|
| gateway 外部协议（MCP/OpenAI/A2A/JSON-RPC）| C-L11 `gateway_forward.c` | 转发器已创建但从未被调用；且 `gateway.forward` 机制存在**架构反模式**（见 §3）|
| gateway→mem_d 记忆转发 | `mem_d/README.md`：gateway 转发 `airy_sys_memory_*` | gateway 无任何 mem_d 调用；TUI 记忆走本地 JSONL（可用但双轨）|

### 1.2 目标与架构原则

**目标**：外部请求经 gateway → agent_d 驱动 `ecosystem/agents` 真实执行；MCP/OpenAI/A2A/JSON-RPC 四协议正确接入；mem_d 记忆链路贯通；不破坏现有 TUI→gateway→llm_d 直连主链路。

**架构原则（行业底座标准，对照 K8s / Envoy / Linux 内核）**：

| 原则 | 行业参照 | 本项目落点 |
|------|---------|-----------|
| **协议边界在网关** | K8s `kube-apiserver` 是唯一入口，外部 REST ↔ 内部 API；Envoy 做 HTTP/gRPC 翻译+路由+鉴权 | gateway 是唯一外部协议边界；daemon 暴露**稳定领域服务 API**（L2 服务协议 `<daemon>.<method>`，见 02-l2-service-protocol.md）|
| **机制/策略分离**（IRON-3）| Linux：调度/文件系统是机制，规则是策略 | 路由与协议适配（策略）集中在 gateway；领域服务（机制）留在 daemon |
| **稳定 ABI/接口**（IRON-1）| Linux 用户空间 ABI 永不破坏 | 内部服务方法（agent.* / mem.* / tool.* / llm.* / sched.*）作为稳定契约，不暴露 daemon 内部实现细节 |
| **标准依赖管理** | Python 生态用 pip/site-packages；Linux 动态库用 ldconfig/DT_RUNPATH | Python 包（agentrt SDK / openlab / airymax_agents）标准安装，**不用运行时 PYTHONPATH hack 解决依赖布局** |
| **可验证性** | 路径/接口可静态验证，不依赖启发式 | 服务发现走显式注册（IPC Bus / 配置），不靠"从可执行文件位置反推源码树" |
| **无隐藏瑕疵** | 乔布斯"看不见的地方要同样精致" | 不做"透传壳先把链路打通，问题留给以后"的补丁 |

---

## 2. 数据流验证（模拟验证结论）

> 已对运行中的真实 daemon 发起 JSON-RPC 验证（`/tmp/airy_wiring_sim.py`），结论：**均为真问题，且链路基础设施完整，仅差接线**。

### 2.1 已验证可用的链路

| 链路 | 验证方式 | 结果 |
|------|---------|------|
| mem_d 服务端 | 直连 `$AIRY_RUNTIME_DIR/mem.sock` 调 write/get/search/delete | ✅ 全通（record_id、检索命中、删除确认）|
| SyscallProxy→mem_d | sdk-python `SyscallProxy(backend="ipc")` 调 memory_write/search/get | ✅ 全通（runner.py 内部记忆持久化路径可达）|
| agent_d 服务端 | 直连 `$AIRY_RUNTIME_DIR/agent.sock` 调 spawn/invoke/terminate | ✅ 全通；**真实 LLM 推理输出 `"2"`** |
| agent_d→runner→ecosystem/agents | spawn `{"role":"coding","language":"python"}` → runner → `agent.execute()` | ✅ 全通（openlab LLMAgent + DEEPSEEK fallback）|
| gateway 转发器基础设施 | `gw_forward_create` 已 `ipc_bus_helper_init`；`do_forward` 经 `ipc_bus_helper_request` 发往目标 daemon socket | ✅ 通道可达（但协议设计需纠正，见 §3）|

### 2.2 确认的断点

| 断点 | 证据 | 性质 |
|------|------|------|
| `gateway.forward` 未注册 | 向 llm.sock/sched.sock/tool.sock 发 `{"method":"gateway.forward"}` → 均 `-32601 Method not found` | 转发机制即使接上也需逐个 daemon 注册——**但该机制本身应废弃（§3 D2）** |
| `gw_forward_request` 无调用入口 | 全仓库检索仅定义处与头文件声明 | 需接入 gateway 路由 |
| agent_d spawn 的 PYTHONPATH 反推失败 | `agent_<id>.log` 报 `ModuleNotFoundError: airymax_agents` | `agent_find_repo_root` 从 `/proc/self/exe` 反推源码树，构建目录在仓库外且 `/proc/self/exe` 仅 Linux——**应改标准安装（§3 D1）** |

---

## 3. 行业底座判断（核心结论）

> 以 K8s / Envoy / Linux 内核 / Python 生态标准，对两个关键决策点给出**严谨结论**。判断标准：稳定边界、机制/策略分离、标准依赖管理、可验证性、无隐藏瑕疵。

### 3.1 D1：Python 依赖路径 —— 标准安装（pip），否决运行时 hack

| 候选 | 行业底座评估 | 结论 |
|------|-------------|------|
| A. 环境变量 `AIRY_AGENTS_PYTHONPATH` 注入 | 把"正确路径"散落于启动脚本，跨机器漂移、无法验证；环境变量应表达**配置**，不应解决**依赖布局** | ❌ 补丁式，否决 |
| B. `agent_find_repo_root` 反推健壮化 | ① `/proc/self/exe` 仅 Linux，macOS/Windows 上 readlink 必然失败（违反三平台约束）；② "从可执行文件反推源码树"在 K8s/Linux 组件中无先例——组件依赖安装布局/配置，不靠启发式；③ 生产裁剪安装不适用 | ❌ 改进的启发式仍是启发式，否决为主方案 |
| **C. 标准安装** | sdk-python 已有 `setup.py`、openlab 已有 `pyproject.toml`——标准机制已存在；补 `airymax_agents` 的 `pyproject.toml`，`pip install -e`（editable）开发 / `pip install` 生产；agent_d 的 `python3 -m airymax_agents.runner` 走标准 Python 模块解析，**删除 PYTHONPATH 注入逻辑** | ✅ **正解** |

**结论 D1**：以 **C（标准安装）** 为唯一方案。`agent_d` 的 `agent_build_agents_pypath` 注入逻辑删除（或仅保留 `AIRY_LIB_DIR` 生产路径）；`agent_find_repo_root` 一并删除（其存在即是为掩盖依赖布局问题）。开发期用 editable install 保证改动即时生效。

### 3.2 D2：gateway 外部协议接入 —— 网关集中翻译，否决 gateway.forward 透传

| 候选 | 行业底座评估 | 结论 |
|------|-------------|------|
| A. `gateway.forward` 透传壳 | ① **协议泄漏**：外部客户端必须知道 daemon 内部方法名（complete/execute_tool/schedule_task），违背"gateway 是协议边界"；② 协议翻译下放到每个 daemon，各自重复实现、易漂移；③ 安全边界模糊：所有内部方法直接对外暴露；④ 与已有 `gateway_d/src/protocol/`（mcp_server/openai_compat/a2a_handler）本地协议 handler 自相矛盾 | ❌ **架构反模式**，否决 |
| B. 协议翻译（每个 daemon 各自翻译）| 翻译逻辑散落 daemon 侧，仍是重复耦合 | ❌ 方向对但实现位置错 |
| **C. 网关集中翻译（推荐）** | K8s/Envoy 模式：gateway 复用/扩展 `protocol/` 适配器，把 MCP `tools/call`、OpenAI `chat/completions`、A2A `task/delegate` **翻译为内部服务调用**（`tool.execute` / `llm.complete` / `sched.submit` / `agent.*` / `mem.*`）；daemon 侧零协议知识，只暴露稳定领域服务 API | ✅ **正解** |

**结论 D2**：否决 `gateway.forward` 透传机制（标记废弃，不注册任何 `gateway.forward` 方法）。采用 **C：gateway 协议适配层 → 内部服务路由**。内部服务路由即现有 L2 服务协议（`<daemon>.<method>`，02-l2-service-protocol.md §2 已定义 `agent.spawn` / `mem.write` / `sched.submit` 等标准方法）——gateway 作为该协议的**客户端**调用 daemon，daemon 作为**服务端**保持现状（方法已注册，已验证可用）。

> 说明：此判断**推翻**了 11-agent-gateway-wiring.md 初稿中"方案 A 透传壳先行"的建议。透传壳是"先把链路弄通、问题以后再说"的补丁，不符合"无隐藏瑕疵"标准。

### 3.3 既有代码处置

| 代码 | 处置 |
|------|------|
| `gateway_forward.c` / `gateway_forward.h`（C-L11）| **废弃**（删除或标记 DEPRECATED）：detect_proto 协议检测可保留给 gateway 路由复用，`do_forward`/`gateway.forward` 消息构造删除 |
| `gateway_d/src/protocol/`（mcp_server/openai_compat/a2a_handler）| **保留并接线**：这些本地 handler 是协议适配的正确载体，改造为调用内部服务路由 |
| `agent_build_agents_pypath` / `agent_find_repo_root` | **删除**，Python 依赖改标准安装 |

---

## 4. 目标架构（修订版）

```
外部客户端（TUI / SDK / MCP 客户端 / OpenAI 客户端 / A2A 对端）
      │  标准协议（JSON-RPC / MCP / OpenAI / A2A）
      ▼
┌──────────────────────────────────────────────────────────┐
│ gateway_d —— 协议边界（唯一外部入口）                       │
│  ┌──────────┬────────────┬────────────┬────────────────┐ │
│  │ JSON-RPC │ MCP 适配   │ OpenAI 适配 │ A2A 适配       │ │
│  │ agent.run│ tools/call │ chat/       │ task/delegate │ │
│  │ ping     │ resources  │ completions │ discover      │ │
│  │ mem.*    │            │            │               │ │
│  └────┬─────┴─────┬──────┴─────┬──────┴───────┬────────┘ │
│       │ 内部服务路由（L2 协议客户端，Unix socket JSON-RPC） │
│       │ agent.*   mem.*   tool.*   llm.*   sched.*       │
└───────┼──────────┼────────┼────────┼────────┼────────────┘
        ▼          ▼        ▼        ▼        ▼
     agent.sock mem.sock tool.sock llm.sock sched.sock
        │
        │ fork + 管道（行分隔 JSON）
        ▼
  python3 -m airymax_agents.runner   （标准安装，无 PYTHONPATH hack）
   → get_agent(role) → agent.execute()
   → SyscallProxy(ipc) ──mem.sock──▶ mem_d   ← 记忆沉淀
```

要点：
- **gateway 是唯一协议边界**：外部只见到 JSON-RPC/MCP/OpenAI/A2A；内部方法名不外泄。
- **daemon 侧零改动**（agent_d/mem_d/tool_d/llm_d/sched_d 服务端已就绪、已验证）：不注册 `gateway.forward`，不做协议翻译。
- **改动集中在 gateway**：协议适配器接线 + 内部服务路由客户端。
- **部署侧**：Python 包标准安装（`pip install -e sdk/sdk-python openlab agents`），删除 PYTHONPATH 注入。

---

## 5. 接口修改清单（修订版）

### 5.1 部署/构建侧

| # | 修改 | 文件 |
|---|------|------|
| B1 | 补 `ecosystem/agents/airymax_agents/pyproject.toml`（其余两包已有 setup.py/pyproject.toml）| `ecosystem/agents/airymax_agents/` |
| B2 | 安装脚本/文档：`pip install -e`（开发）三包 | 构建脚本 |
| B3 | agent_d 启动不再依赖 `AIRY_AGENTS_PYTHONPATH`；移除 `agent_build_agents_pypath`/`agent_find_repo_root` | `daemons/agent_d/src/service.c` |

### 5.2 gateway_d 侧（改动主体）

| # | 修改 | 说明 |
|---|------|------|
| G1 | **内部服务路由客户端**：新增 `gw_svc_call(daemon, method, params)`（Unix socket JSON-RPC，复用 `tool_call_rpc` 模式），路由表：`agent.*→agent.sock`、`mem.*→mem.sock`、`tool.*→tool.sock`、`llm.*→llm.sock`、`sched.*→sched.sock` | `gateway_business_handler.c` |
| G2 | **agent.run 编排路径**：`params.agent` 存在 → `agent.spawn` + `agent.invoke`（参考 work_hall.c 的 spec/input/output 语义）；否则保持 llm_d 直连 | 同上 |
| G3 | **mem.* 方法**：`mem.write/search/get/delete` → `gw_svc_call("mem_d", ...)` 透传 | 同上 |
| G4 | **协议适配接线**：`protocol/mcp_server.c` 的 `tools/call`、`protocol/openai_compat.c` 的 `chat/completions`、`protocol/a2a_handler.c` 的 `task/delegate` 改造为调用 `gw_svc_call`（而非本地空转）| `protocol/*.c` |
| G5 | **废弃 C-L11**：删除 `gateway_forward.c/h` 的 `do_forward`/`gateway.forward` 消息构造；`detect_proto` 保留给 G4 复用 | `gateway_forward.c/h`、`main.c` |
| G6 | 长请求超时：agent invoke 含 LLM 往返（30s+），HTTP handler 超时与线程模型核对 | `main.c`/HTTP 层 |

### 5.3 daemon 侧

| # | 修改 | 说明 |
|---|------|------|
| D1 | **零协议改动**：不注册 `gateway.forward`；服务端方法维持现状 | 各 daemon `main.c` |
| D2 | 唯一可选优化：`agent_service_reap_idle` 与长 invoke 的空闲误判核对（R6）| `daemons/agent_d/src/service.c` |

---

## 6. 潜在风险点

| # | 风险 | 说明与缓解 |
|---|------|-----------|
| R1 | 标准安装改变运行布局 | editable install（`pip install -e`）保持开发即时生效；生产走 venv 安装；CI 增加 `pip install -e` 步骤并验证 `python3 -m airymax_agents.runner` 可导入 |
| R2 | HTTP 长请求阻塞 | agent invoke 30s+；确认 HTTP 线程池模型支持并发长请求，按方法差异化超时（参考现有 30s 工具超时先例）|
| R3 | 协议适配语义边界 | MCP `tools/call` → `tool.execute` 的参数映射需与工具 schema 对齐；OpenAI `chat/completions` → `llm.complete` 的 tool_calls 透传已具备（llm_d 已实现 function calling）|
| R4 | 安全边界 | gateway 协议适配层加 ACL（fail-closed）：外部请求不得直接触达 `shell_run` 等敏感工具（保持 approval 链）；`mem.*` 需鉴权 |
| R5 | 废弃 C-L11 的回归 | 删除 `gateway_forward` 前确认无其他引用（已确认仅 main.c 统计用）；统计能力由 gateway 服务层指标替代 |
| R6 | agent 空闲回收 vs 长 invoke | `reap_idle` 可能误杀长 invoke 中的子进程；核对 `last_active` 更新时机，必要时 invoke 期间豁免回收 |
| R7 | TUI 记忆双轨 | 维持 TUI 本地 JSONL 不迁移（功能完整）；mem_d 作为 agent 执行期记忆（runner SyscallProxy 已通）——两条路径职责不同，文档标注即可 |
| R8 | [SC] 同源约束（IRON-9）| 全部改动在 agentrt 内部；不触碰 [SC] 共享契约层；`<daemon>.<method>` 命名空间遵循 02-l2-service-protocol.md 既有契约 |

---

## 7. 分阶段实施方案

| 阶段 | 内容 | 出口标准 | 状态 |
|------|------|---------|------|
| **Phase 0** | 标准安装：补 `airymax_agents/pyproject.toml`；`pip install -e` 三包；删除 agent_d PYTHONPATH 注入 | 无 PYTHONPATH 环境下 spawn 真实 agent 成功、invoke 返回 LLM 输出 | ✅ |
| **Phase 1** | gateway 内部服务路由（G1）+ agent.run 编排路径（G2）| curl agent.run（含 agent 参数）→ agent_d → ecosystem/agents → 返回结果；既有 llm_d 直连路径不回退 | ✅ |
| **Phase 2** | 协议适配接线（G4）+ 废弃 C-L11（G5）| MCP `tools/call`→tool_d、OpenAI `chat/completions`→llm_d、A2A→sched_d 端到端成功 | ✅ |
| **Phase 3** | mem.* 转发（G3）+ 安全加固（R4）| gateway mem.* 可用；外部协议均过 ACL（详见 [07-gateway-mem-acl.md](../_design_0.1.1/07-gateway-mem-acl.md)）| ✅ |
| **Phase 4** | 全量回归：118 ctest + 57 cargo test + 15 daemon e2e + agent.run 工具 e2e | 无回归 | ✅ |

---

## 8. 验证方案

1. **模拟基线**：复用已通过的 `/tmp/airy_wiring_sim.py`（mem_d / agent_d / 转发探测）。
2. **Phase 0 验证**：`python3 -m airymax_agents.runner --spec '{"role":"coding"}'` 在纯净环境（无 PYTHONPATH）可导入执行。
3. **单元**：gw_svc_call 路由表单测；协议适配参数映射单测。
4. **集成**：`curl` MCP `tools/call` / OpenAI `chat/completions` / JSON-RPC `agent.run`（含 agent）/ `mem.write`，逐一验证数据流。
5. **回归**：全量 ctest + cargo test + 15 daemon 重启 + agent.run 内置工具 e2e（保存文件/shell 执行）不回退。

---

## 9. 同源约束说明

agentrt 是 agentrt-linux（AirymaxOS）的用户态运行时。本方案：

- 全部改动位于 agentrt 仓库内（daemons/SDK/ecosystem packaging），**不新增**与 agentrt-linux 的代码共享；
- 不触碰 [SC] 共享契约层 10 个头文件（`agentrt/commons/include/airymax/`）；
- 内部服务协议遵循既有 L2 服务协议（02-l2-service-protocol.md）`<daemon>.<method>` 命名空间；
- 若后续对外协议语义需与内核态能力联动，再同步核对 [SC] 契约语义一致性（IRON-9 v3）。

---

## 10. 决策结论汇总（严谨判断）

| 决策点 | 结论 | 否决理由 |
|--------|------|---------|
| D1 Python 依赖路径 | **标准安装（pip install -e）**，删除 PYTHONPATH 注入与源码树反推 | 环境变量是补丁；`/proc/self/exe` 反推仅 Linux 且违背可验证性（§3.1）|
| D2 外部协议接入 | **网关集中翻译**（复用 protocol/ 适配器 → 内部服务路由）；**废弃 gateway.forward** | 透传壳协议泄漏、翻译下放 daemon 重复耦合、安全边界模糊（§3.2）|
| D3 TUI 记忆 | 维持本地 JSONL；mem_d 供 agent 执行期记忆（职责不同，不强制迁移）| 功能已完整，双轨职责清晰 |
| D4 agent.run 触发 | `params.agent` 显式触发编排路径；默认保持 llm_d 直连（向后兼容）| 显式优于自动判定（可预测、不破坏现有调用）|

---

*本方案为 DRAFT，待评审确认后按 Phase 0→4 实施。*
