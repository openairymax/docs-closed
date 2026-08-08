# AgentRT 全功能审查报告（v4.2）

> **审查日期**：2026-08-07\
> **审查范围**：工具使用、智能体调度、记忆系统、双思考系统、TUI UI/过程可视化 五大维度全链路逐字节核查\
> **审查方式**：5 路并行子代理 + 主会话复核\
> **审查结论**：AgentRT 的**骨架与各 daemon 真实可用**（15 daemon 全部在线、方法完整），但**对话主链路上存在 20+ 个断点**，导致用户感知为"只能简单对话、几乎无可用功能"。

---

## 0. 总体结论（TL;DR）

| 用户反馈 | 判定 | 根因 |
|---------|------|------|
| 只能简单对话，用不了工具 | ✅ 属实 | gateway 把工具 schema 暴露给 LLM，但 shell_run 被 ACL 默认拒绝、fs_list 参数 schema 与 validator 矛盾、工具循环 30s 超时过短 |
| 没办法调度智能体干活 | ✅ 属实 | TUI 永不传 `params.agent` → gateway 编排分支永不触发；sched_d 注册表恒空、无 DAG 引擎、无调用方 |
| 记不住历史对话 | ✅ 属实 | 对话历史只存在于 TUI 本地 JSONL，网络层无 messages 数组、gateway/llm_d 无会话状态 |
| 记忆卷载（MemoryRovol）起作用了吗 | ❌ 没有 | MemoryRovol 默认不编译不链接（CMake OFF + Cargo feature 关闭），对话链路不经过其 bridge，mem_d 无人调用 |
| 双思考系统正常工作吗 | ❌ 没有 | CoreLoopThree 是"孤儿库"——实现完整但 daemons 零调用；真实链路是 gateway→llm_d 单模型 complete |
| 看不到执行过程/思考过程 | ✅ 属实 | 链路是阻塞式单次响应（无流式、无事件、无思考订阅）；DAG 只在 GradConfirm 显示一次，Executing 阶段消失 |
| 表格 markdown 不能渲染 | ✅ 属实 | TUI 无任何 markdown 渲染库，表格/标题/列表原样输出，表格行被硬换行切断 |
| 对话展示混乱不美观 | ✅ 属实 | 无气泡/时间戳、角色名中英混排、内容缩进参差、新消息强制回底 |

**一句话**：AgentRT 的"零件"都在（C daemon、Python runner、MemoryRovol、CoreLoopThree 实现完整），但**组装**断了——TUI 只走 gateway→llm_d 直连，其余所有子系统（agent_d 编排、sched_d 调度、mem_d 记忆、coreloopthree 认知）全是"存在但未接线"。

---

## 1. 工具使用链路（工具"用不了"根因）

真实链路：TUI `agent.run` → gateway `gw_run_tool_loop`（8 轮上限）→ llm_d `complete` → LLM 返回 tool_calls → gateway `gw_execute_tool` → tool_d `execute_tool`。

| # | 断点 | 证据 | 后果 |
|---|------|------|------|
| T1 | **shell_run 被 gateway ACL 默认拒绝** | [gateway_business_handler.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/gateway_business_handler.c#L487-L498)：agent 固定 `"external"`，fail-closed；[main.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/main.c#L80-L82)：仅 `AIRY_GATEWAY_ACL_ALLOW_SHELL=true` 放行 | LLM 一调 shell_run 即 `Permission denied`，工具轨迹全失败 |
| T2 | **fs_list 参数 schema 与 validator 矛盾** | [gateway_business_handler.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/gateway_business_handler.c#L270-L273)：`"required":[]`；[validator.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/tool_d/src/validator.c#L180-L186)：所有已注册参数缺一即拒 | LLM 按 schema 省略 path 调用 fs_list → 必被拒 |
| T3 | **gateway→llm_d 仅 30s 超时** | [gateway_business_handler.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/gateway_business_handler.c#L46)：`GW_LLM_DEFAULT_TIMEOUT_MS 30000` | 长响应（含 tool_calls）>30s → 整轮失败 |
| T4 | **工具调用 30s 超时 < shell_run 60s 执行** | [gateway_business_handler.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/gateway_business_handler.c#L281)：`GW_TOOL_TIMEOUT_MS=30000`；[service.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/tool_d/src/service.c#L87)：shell_run `timeout_sec=60` | 长命令结果丢失 |
| T5 | **parse_llm_result 强制 content 为字符串** | [gateway_business_handler.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/gateway_business_handler.c#L853-L857) | 工具调用轮 LLM 返回 content=null → 解析失败，final_text 空 |
| T6 | **llm_d response_to_json 对 content=NULL 无保护** | [response.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/llm_d/src/response.c#L54) | 与 T5 联动，是"只能简单对话"链路的薄弱点 |
| T7 | MCP tools/call 响应缺 id 字段 | [gateway_mcp_server.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/protocol/gateway_mcp_server.c#L508-L513) | 严格 MCP 客户端无法关联响应 |
| T8 | MCP tools/list 缺 inputSchema | [gateway_mcp_server.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/protocol/gateway_mcp_server.c#L190-L191) | 客户端拿不到参数 schema |

**结论**：链路本身（方法名、参数格式、tool_calls 提取、approval/quota）均无断点；问题集中在 ACL 默认拒绝 + schema 矛盾 + 超时过短。**修复后工具即可用。**

---

## 2. 智能体调度链路（"没办法调度智能体干活"）

真实链路：TUI GCCP/GRAD（本地文本状态机）→ 但 DAG 仅用于可视化，**从不下发**。

| # | 断点 | 证据 | 后果 |
|---|------|------|------|
| S1 | **TUI 永不传 `params.agent`** | [client.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/client.rs#L73-L77)：params 仅 prompt/agent_file/interactive/model/session_id | gateway 编排分支判定 `params.agent` 恒 NULL → agent_d 编排永不触发，退化为纯对话 |
| S2 | **gateway 忽略 agent_file** | [gateway_business_handler.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/gateway_business_handler.c#L1191-L1214)：只读 prompt/messages/model/session_id/agent | TUI 传的 agent_file 是死参数 |
| S3 | **DAG 不落盘下发** | [app.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/app.rs#L631-L632)：仅 build_execute_prompt 拼接文本；gccp.rs:598-599 DAG 只进 render_dag_lines | 任务图仅用于展示 |
| S4 | **sched_d 注册表恒空** | [sched_d/main.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/sched_d/src/main.c#L516)：register_agent 无任何调用方 | `schedule_task` 永远选不出 agent |
| S5 | **sched_d 无队列/无 DAG 引擎** | [sched_service_impl.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/sched_d/src/sched_service_impl.c#L170-L238)：仅同步"选人"；README 设计的 sched.submit/dispatch 等全未实现 | 即便调用也无法执行多步骤任务 |
| S6 | **唯一 sched_d 入口是 A2A** | [gateway_business_handler.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/gateway_business_handler.c#L1742-L1805)：gw_biz_sched_schedule 仅 A2A 注册 | TUI 不用 A2A，链路对用户不可达 |
| S7 | **Python runner 直连外部 LLM** | [openlab/core/llm.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/core/llm.py#L212-L220)：直连 OpenAI 兼容端点；无 key 时 MockLLMClient | 即便 agent_d 被拉起，子进程不经 llm_d；无 key 是假执行 |

**结论**：agent_d 本身（spawn/invoke 协议、ready 校验、空闲回收）**是完好的**，Python 侧 8 角色注册表也存在。断在：TUI 不触发编排分支 + sched_d 无调用方 + 无 DAG 引擎。**修复方向**：TUI 在 grad_confirm 后把 DAG 提交为真实任务（传 params.agent 或新增 sched 客户端）。

---

## 3. 记忆系统（"记不住历史" + "记忆卷载起作用了吗"）

真实链路：TUI 本地 JsonlMemory（`$AIRY_HOME/tui/memory.jsonl`）→ 拼进 prompt 文本 → gateway/llm_d 单条消息。

| # | 断点 | 证据 | 后果 |
|---|------|------|------|
| M1 | **网络层无 messages 数组** | [client.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/client.rs#L73-L93)：agent.run 只发 prompt 字符串 | 历史只能挤进 prompt 文本 |
| M2 | **gateway 每次新建消息数组** | [gateway_business_handler.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/gateway_business_handler.c#L1068-L1080)：messages 生命周期仅单次工具循环 | 跨请求无历史 |
| M3 | **历史注入上限 = 最近 6 条** | [app.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/app.rs#L1079)：`memory.recent(6)` | 超长对话早期信息被截断 |
| M4 | **MemoryRovol 默认不编译不链接** | [agentrt/CMakeLists.txt](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/CMakeLists.txt#L65)：`AIRY_WITH_MEMORYROVOL OFF`；[Cargo.toml](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/Cargo.toml#L14-L18)：feature 默认关闭 | 运行时 MemoryRovol 完全不存在 |
| M5 | **对话链路不经过 memoryrovol_bridge** | [client.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/client.rs#L73-L93) 不传 agent 参数 → gateway 走 llm_d 直连 | bridge 形同虚设 |
| M6 | **mem_d 无人调用（悬挂服务）** | 全仓库 mem.write/search 无业务调用方；对话结束不自动写 mem_d | mem_d 是死服务 |
| M7 | **mem_d search 是子串匹配非向量** | [mem_d/service.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/mem_d/src/service.c#L175-L202)：strncmp 计数评分 | 无语义召回 |
| M8 | **TUI 记忆与 mem_d 是两套独立存储** | [memory.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/memory.rs#L71) vs [mem_d/service.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/mem_d/src/service.c#L269) | 数据不互通 |

**结论**：**MemoryRovol 的 L1-L4 真实实现存在**（[products/memoryrovol/src](file:///home/spharx/SpharxWorks/airymaxhub/products/memoryrovol/src) 70+ 文件：layer1_raw/layer2_feature/layer3_structure/layer4_pattern/forgetting/retrieval），但**默认不参与构建，且对话链路不经过它**。"记忆卷载起作用了吗"答案：没有——因为根本没接线。

---

## 4. 双思考系统（"正常工作吗"）

| # | 断点 | 证据 | 后果 |
|---|------|------|------|
| D1 | **CoreLoopThree 是孤儿库** | daemons 目录中 `orchestrator_create`/`airy_loop_submit`/`airy_cognition_process` **零匹配** | 认知引擎从不参与真实请求 |
| D2 | **set_tc3_models 全仓零调用** | [engine.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/atoms/coreloopthree/src/cognition/engine.c#L580-L608) 存在但无调用者 | 双思考（t2/t1-f/t1-p）从未被注入模型 |
| D3 | **dual_coordinate 此前无调用点** | [engine.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/atoms/coreloopthree/src/cognition/engine.c#L1564-L1598) 注释自述"断链" | 双模型交叉验证未运行 |
| D4 | **真实链路是单模型 complete** | [gateway_business_handler.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/gateway_business_handler.c#L1019)：method=complete 无 stream | 无思考事件可推送 |
| D5 | **无流式/无事件/阻塞响应** | [client.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/client.rs#L102)：等完整 body | 用户看不到思考过程是架构性必然 |
| D6 | **TUI 侧 GCCP 是独立前端实现** | [app.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/app.rs#L472-L631) 五问状态机 | 与 C 库 airy_gccp_probe/confirm 是两套，且 C 侧从未运行 |

**结论**：文档（[02-coreloopthree.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxRT/10-architecture/02-coreloopthree.md#L870)）宣称"✅ 双思考 TC3 已激活"，但工程上 CoreLoopThree **从未与任何 daemon 建立调用关系**。用户"双思考系统是否正常都不知道"——判定正确：**从未在对话链路上运行过**。

---

## 5. TUI UI 与过程可视化（"混乱不美观" + "看不到过程" + "表格不能渲染"）

真实渲染管线：[ui.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/ui.rs#L69-L77) 垂直 4 行布局（品牌栏/主内容/输入栏/快捷键），无侧边栏。

| # | 问题 | 证据 | 改造建议（参考 Claude） |
|---|------|------|------|
| U1 | **无 markdown 渲染**：表格/标题/列表原样输出，表格行被硬换行切断 | [Cargo.toml](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/Cargo.toml#L20-L58) 无 md 库；[chat.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/panels/chat.rs#L211-L235) 仅处理代码围栏；[chat.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/panels/chat.rs#L268-L293) wrap_line 硬断行 | 引入 tui-markdown 或自写轻量渲染：表格按列对齐、代码块保留缩进、行内代码/粗体着色 |
| U2 | **代码块缩进被破坏**：trim_start 剥掉前导空格 | [chat.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/panels/chat.rs#L212) | 代码块行不 trim，渲染为独立区块 |
| U3 | **消息无时间戳、无气泡** | [app.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/app.rs#L36-L40)：ChatMessage 仅 role+content | 加 timestamp；消息渲染为 surface 背景块，头部小字"角色名 · HH:MM:SS" |
| U4 | **执行阶段零过程可视化**：DAG 只在 GradConfirm 显示一次，Executing 只剩节点计数 | [chat.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/panels/chat.rs#L154-L178) | Executing 阶段持续渲染 DAG，节点按待执行/执行中/已完成着色 |
| U5 | **等待期无中间事件**：单次阻塞 POST | [client.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/client.rs#L102)（reqwest stream 特性已启用但未用） | 对接流式返回（SSE/NDJSON），边执行边上屏 |
| U6 | **工具轨迹静态折叠不可展开** | [app.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/app.rs#L430-L461)：MAX_VISIBLE_TOOL_TRACES=4；[main.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/main.rs#L243-L403) 无展开键 | 加折叠状态位，Enter/→ 展开 |
| U7 | **新消息强制回底** | [app.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/app.rs#L1119-L1122) | 仅当用户在底部才回底 |
| U8 | **角色名中英混排 + 内容缩进参差** | [chat.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/panels/chat.rs#L186-L201) | 统一中文（用户/助手/系统/工具/结果），固定内容起始列 |
| U9 | **thinking 动效弱、工具调用 dim 弱化** | [chat.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/panels/chat.rs#L22-L65)；[chat.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/panels/chat.rs#L241-L244) | 独立状态区"正在调用工具 X…"（Claude Code 式单行） |

---

## 6. 修复优先级（建议）

### P0 — 打通核心功能（让"能用"）
1. **工具链路**：gateway 默认放行 shell_run 或按 `AIRY_GATEWAY_ACL_ALLOW_SHELL` 显式配置 + fs_list schema 与 validator 对齐 + 超时拉长（LLM 60s / tool 90s）+ content=NULL 兜底
2. **历史记忆**：client.rs 发送 messages 数组（user/assistant 交替）→ gateway 透传整个数组（`gw_build_llm_request` 已支持深拷贝，llm_d 已支持多消息解析——**两端基础设施都在，只差接线**）；对话结束自动 mem.write
3. **记忆卷载启用**：`-DAIRY_WITH_MEMORYROVOL=ON` + `cargo build --features memoryrovol`（三步同时满足）

### P1 — 调度编排（让"能干复杂活"）
4. **TUI 传 params.agent** 触发 gateway 编排分支（gw_agent_run_orchestrate 已完好）
5. **sched_d 补 register_agent 调用方 + DAG 执行引擎**
6. **Python runner 改走 llm_d**（经 gateway 而非直连外部）

### P2 — UI 提升（参考 Claude）
7. **markdown 渲染**（表格/代码块/标题/列表）
8. **消息气泡 + 时间戳 + 统一角色名**
9. **Executing 阶段 DAG 持续渲染 + 节点状态**
10. **流式输出对接**（思考过程可见性）

### P3 — 双思考系统
11. CoreLoopThree 接入对话链路（orchestrator → gateway 或 llm_d 层）——改动最大，建议独立排期

---

## 7. 证据文件索引

- 工具链路：[gateway_business_handler.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/gateway_business_handler.c)、[tool_d/src/validator.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/tool_d/src/validator.c)、[gateway_mcp_server.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/protocol/gateway_mcp_server.c)
- 调度链路：[client.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/client.rs)、[sched_d/main.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/sched_d/src/main.c)、[sched_service_impl.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/sched_d/src/sched_service_impl.c)、[openlab/core/llm.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/core/llm.py)
- 记忆链路：[app.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/app.rs)、[memory.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/memory.rs)、[mem_d/service.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/mem_d/src/service.c)、[agentrt/CMakeLists.txt](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/CMakeLists.txt)
- 双思考：[coreloopthree engine.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/atoms/coreloopthree/src/cognition/engine.c)、[dual_model.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/atoms/coreloopthree/src/cognition/coordinator/dual_model.c)、[02-coreloopthree.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxRT/10-architecture/02-coreloopthree.md)
- TUI：[chat.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/panels/chat.rs)、[ui.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/ui.rs)、[app.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/app.rs)、[Cargo.toml](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/Cargo.toml)

---

## 8. 修复进展（2026-08-07 晚场，全部真实实现 + E2E 验证）

> 本场按「执行体真正可用 → 全链路集成 → 交互 UI 提升」三条线推进，核心断点已打通并经真实调用验证。

| # | 断点 | 修复 | 验证 |
|---|------|------|------|
| T0 | tool_d 仅 4 工具、无联网能力 | 新增 `web_fetch` 内置工具（curl 主路径 + network_common 层 http 降级，URL 注入防护），tool_d/gateway_d 双端注册 + ACL + MCP schema | 真实抓取 https://example.com 成功（HTTP 200，body 完整） |
| T1 | agent 8 角色零工具 | `SyscallProxy.tool_execute()`（IPC 直连 tool.sock）+ `AirymaxAgent._register_builtin_tools()` 注册 5 工具，dispatch 走 tool_d | 单测 343+18+176 全绿；coding 角色 shell_run 真实执行返回 `tool-wired-ok` |
| T2 | agent_d spawn 依赖未装 | 三包 editable 安装（agentrt / agentrt-openlab / agentrt-agents） | `import agentrt, openlab, airymax_agents` 通过；spawn+invoke E2E：LLM 调 fs_write+fs_read 写读文件成功（4.8s） |
| T3 | market_d install_agent UB | 字符串指针强转结构体指针 → 构造真实 `install_request_t` 并释放 result | register→install→缺参全部优雅返回，无崩溃 |
| T4 | plugin_d 无插件可载 / 技能断链 | 部署 text_summarization 技能插件（TF 抽取式摘要，C 实现）到 `$AIRY_HOME/ecosystem/plugins/` | plugin.list 返回 1 个；plugin.execute 真实输出 summary/keywords/stats |
| T5 | 主链路双思考 → 工具 → 记忆 | 复用既有 gateway 链（think_d GCCP+GRAD → llm_d → tool_d 工具循环 → mem_d 持久化） | E2E：5 节点 DAG 计划 + web_fetch 真实抓取 + 中文总结（28.8s，tokens=3701） |
| T6 | TUI 不展示双思考轨迹 | RunResponse 新增 `thinking` 字段 + chat 面板「双思考计划 N 节点」一行摘要（GRAD 轮数/修正数） | TUI 编译部署，工具轨迹折叠展示已有 |

**仍待跟进（非阻断）**：
- ~~sched_d 无队列/DAG 引擎~~ → 已补全（见 8.1）
- ecosystem/examples 子仓仅 README（无可运行示例）
- ~~plugin_d 仅 text_summarization 一个 .so 技能插件~~ → 已生成 4 个 C 插件（见 8.1）
- web_fetch 在 Windows 返回 NOT_SUPPORTED（network 层 TLS 未实现，curl 路径为 POSIX）
- ~~market_d install 目录解析用相对路径 `./agents`~~ → 已修复（见 8.1）

---

## 8.1 修复进展续（2026-08-08 凌晨场：sched_d DAG 引擎 + 阻塞项收敛）

| # | 项 | 修复 | 验证 |
|---|----|------|------|
| S5' | sched_d 无队列/DAG 引擎 | 队列 cancel RPC + 轻量 DAG 调度器（`sched_service_submit_dag/get_dag/cancel_dag`，64 节点/32 图上限，Kahn 环检测拒绝，依赖拓扑派发，节点失败级联取消，独 dag 工作线程 + 条件变量）；RPC 注册 11 个方法（含 `submit`/`query` 别名）；新增错误码 `AIRY_ERR_SVC_CYCLE (-308)` | 单测 4 用例全绿（拓扑顺序/环拒绝/失败级联/取消）；sched_d 3 测试全通过；端到端菱形 DAG 经 sched.sock 真实派发 agent_d，progress 0→4 全 completed，节点输出真实 LLM 文本 |
| T1' | agent 8 角色零工具 | （上轮已接线，本轮回归） | 全链路 agent.run E2E：GCCP 3 节点计划 + GRAD 双模型（dual_invocations=12, corrections=12）+ web_fetch 真实抓取 example.com + 中文总结，tokens=3080 |
| P1' | plugin_d 仅 1 个技能插件 | 生成 4 个 C 技能插件（code_review / data_analysis / security_audit / web_search，各 500-900 行真实逻辑移植自 skills/src/*.py），ABI 对齐 plugin_service.h | plugin.list 返回 5 插件；plugin.execute 逐一 RPC 验证：code_review 检出 eval/硬编码密钥、data_analysis CSV 统计（mean/median/IQR/趋势）、security_audit 权限+依赖 CVE、web_search URL 编码 |
| P2' | plugin_d 扫描目录相对路径 | `ecosystem/plugins/` 硬编码 → `$AIRY_HOME/ecosystem/plugins` 绝对路径（随 CWD 漂移的发现 bug） | 从任意 CWD 启动 plugin_d 均能扫描到 5 插件 |
| P3' | data_analysis 插件缺 math 库 | CMakeLists 补 `m` 链接 | dlopen 无 undefined symbol，execute 正常 |
| M1' | market_d install 相对路径 | `storage_path="market.log"`（误设日志名）改 NULL；impl 中 4 处 `./agents`/`./skills` 硬编码收敛为 `$AIRY_HOME/agents(/skills)`，父目录自动创建 | install RPC 落盘 `$AIRY_HOME/agents/demo-agent/agent.json`，install_path 返回绝对路径 |
| A1' | Rust spawn 回退失败（-32603） | 根因链：Rust binary 未构建 → execvp 失败 → fallback 前 `SVC_LOG_WARN`（INFO/WARN 写 **stdout**）污染 spawn ready 协议 → spawn 拒绝。修复：`commons/utils/logging/src/logging.c` 两处 console 输出统一改 **stderr**（POSIX 惯例，stdout 留给数据流；所有 daemon fd1/fd2 均重定向同文件无影响）；benchmark 测试补前置条件检查（binary 缺失 skip Rust 对比） | Rust spawn 优雅回退 Python runner（agent_id 正常返回 + invoke Mock 输出）；WARN 正确写入 agent_<id>.log；agents 测试套件 18 passed + 1 skipped |
| S6' | sched_d 队列/DAG 细致补全 | P0-1：cancel_dag 后 RUNNING 节点完成未归一 canceled（worker 死分支，头文件承诺「不再上屏输出」未兑现）→ worker 回写检测图已取消，节点置 CANCELED 丢弃输出；P0-2：validate 所有失败一律归 CYCLE_DETECTED（重复 id/依赖缺失/OOM 也报环）→ 逐点区分 INVALID_PARAM/OVERFLOW/OOM/CYCLE 并如实透传，main.c 区分错误消息；P0-3：submit_task 的 `task_seq++` 锁外递增（RPC 线程池 8 并发 data race）→ id 生成移入锁内；P1-4：priority 字段仅存储未生效 → worker 出队选最高优先级（同优先级 FIFO，`sched_queue_take_highest`）；P1-5：枚举缺 PRIORITY_BASED（协议声明 4 策略实际 3 种）→ 补枚举 + schedule_task 分支按任务优先级放大选人分数；P1-6：L2 标准方法 `sched.checkpoint_save` 缺失 → 实现状态快照 + 注册 RPC（12 方法）；P2：timeout_ms 结果层生效（超阈值 FAILED）、get_dag 节点导出 started/finished_at_ms、dag_id 分配 OOM 检查 | sched_d 3 测试全绿；DAG 单测 6 用例（新增 cancel 节点归一/错误码区分/优先级消费 URGENT→NORMAL→LOW，ASan 干净）；E2E：checkpoint_save 快照、重复 id 明确报错、链式 DAG（S_01→S_02）真实派发 agent_d completed 2/2、队列 URGENT 任务真实 spawn+invoke |

**仍待跟进（非阻断，后续轮次）**：
- ecosystem/examples 子仓仅 README（README 声称 10 个示例，代码被 commit 84a6015 删除，需重建）
- web_fetch 在 Windows 返回 NOT_SUPPORTED（network 层 TLS 未实现，curl 路径为 POSIX）
- mem_d search 为子串匹配非向量召回（MemoryRovol 语义检索待接线）
