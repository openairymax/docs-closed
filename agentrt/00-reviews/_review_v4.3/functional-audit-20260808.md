# AgentRT 全功能审查与补齐报告（v4.3）

> **审查日期**：2026-08-08
> **审查范围**：14 模块（agentrt 7 模块 + ecosystem 6 模块 + products/memoryrovol）全功能可用性、执行体工具链/联网/项目分析、daemon 标准方法合规、agent-linux 协作契约、用户交互提升
> **审查方式**：3 路并行子代理审计 + 2 路并行开发子代理补齐 + 主会话 E2E 验证
> **审查结论**：v4.2 报告中的**工具链路/调度链路断点已全部修复**，执行体已能**真实调用工具（fs_glob/fs_grep/fs_edit/web_search）联网并分析具体路径项目**；本轮补齐 16 daemon 标准方法（shutdown/get_stats）、MCP 9 工具、gateway 四传输（HTTP/WS/Stdio/HTTP2）、AGTS 任务描述符、manager 管理 CLI 等。15 daemon 全部在线运行，E2E 全链路（spawn→invoke→工具调用→终止）验证通过。

---

## 1. 总体结论（TL;DR）

| 用户诉求 | 状态 | 说明 |
|---------|------|------|
| 执行体能真正使用工具 | ✅ 已验证 | 9 个内置工具（fs_read/fs_write/fs_list/shell_run/web_fetch/fs_glob/fs_grep/fs_edit/web_search）真实实现；E2E 实测 agent 用 fs_glob+fs_grep 分析 sched_d 项目并输出结论 |
| 可以联网 | ✅ 已验证 | web_search 双后端（DuckDuckGo→Bing 降级）、web_fetch HTTP(S)；research-agent 在线链路 bug 已修复 |
| 分析具体路径项目 | ✅ 已验证 | fs_glob/fs_grep/fs_read 组合分析项目结构、搜索符号定义、读取文件 |
| 14 个模块全面可用 | ✅ 大部分 | 见 §3 交付清单；剩余未实现项见 §7 |
| 用户交互/UI 提升 | ✅ 部分 | gateway 四传输接线（WS/Stdio/HTTP2 可支持 WebUI/进程内交互）；manager CLI 统一入口；TUI 提升仍为后续项 |
| agent-linux 协作 | ✅ 部分 | AGTS 任务描述符已实现；[SC] IPC 头 L2 文档已对齐；多后端服务发现/内存卷载桥接为后续项 |
| 遵循 50 工程规范 | ✅ | 本轮实现均真实（无桩）、SSoT 对齐、中文注释、SPDX 头 |

---

## 2. E2E 全链路验证（执行体核心能力）

**测试场景**：spawn coding agent → invoke「分析 sched_d/src 目录：fs_glob 列出 .c 文件 → fs_grep 搜索 submit_dag → 报告文件数与定义位置」

**验证结果**（真实 LLM deepseek-v4-flash）：
- fs_glob 返回 4 个 .c 文件：sched_service_impl.c / sched_svc_adapter.c / monitor.c / main.c
- fs_grep 定位 submit_dag 定义于 `sched_service_impl.c:1151`（sched_service_submit_dag），另 3 处函数内日志 + main.c:297 调用点
- LLM 综合分析输出 Markdown 结论

**验证链路**：agent.sock(spawn/invoke/terminate) → agent_d fork Python runner → LLMAgent 工具回路 → SyscallProxy → tool_d 内置工具真实执行 → 结果回流 LLM。

**关键修复**（使真实 LLM 可用）：
1. [openlab/core/llm.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/core/llm.py)：`make_llm_client` 增加 `_provider_default_model()` 跟随 model.yaml SSoT（deepseek-v4-flash），不再回退 gpt-4o-mini
2. 新增 `_load_secrets_env()`：agent 子进程自动加载 `$AIRY_HOME/config/secrets.env`，daemon 无论经 bootstrap 还是手动 nohup 启动均可获得 LLM 凭据
3. [coding/contract.json](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/agents/airymax_agents/coding/contract.json)：system2 由遗留的 gpt-4o-mini 修正为 deepseek-v4-flash（与其余 7 个契约对齐）

---

## 3. 本轮交付清单

### 3.1 执行体工具链（tool_d + openlab）
- **9 个内置工具真实实现**：[builtin.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/tool_d/src/builtin.c) 新增 fs_glob（多段/递归通配）、fs_grep（正则+目录递归+二进制检测）、fs_edit（精确字符串替换）、web_search（DDG→Bing 双后端）；[service.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/tool_d/src/service.c) 注册 tools[9] 元数据 + ACL 授权
- **工具回路保护**：[agents/llm.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/agents/llm.py) 64KiB 结果截断（MAX_TOOL_RESULT_CHARS）+ 连续重复工具调用 3 次警告/4 次终止（对标 Atom Code ToolLoopPolicy）
- **shell_run 超时执行**：fork+pipe+poll+waitpid，超时 SIGKILL（60s），1MB 输出截断

### 3.2 daemon 标准方法（L2 服务协议合规）
- **`<ns>.shutdown`**：新增 [daemon_main.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/common/include/daemon_main.h) `DAEMON_DECLARE_SHUTDOWN_METHOD` 宏，16 个 daemon 全部注册并真实生效（验证 tool_d/agent_d 调用后优雅退出）
- **`<ns>.get_stats`**：补齐 8 个 daemon（agent_d/tool_d/mem_d/a2a_d/monit_d/market_d/channel_d/hook_d 别名），返回真实统计 JSON（daemon/uptime_s/计数）
- **gateway_d MCP server 9 工具**：[main.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/main.c) MCP tools/list 从 5 扩至 9（补齐 fs_glob/fs_grep/fs_edit/web_search），ACL 默认放行

### 3.3 gateway 四传输接线
- **WS/Stdio/HTTP2 接线**：[service.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/daemons/gateway_d/src/service.c) 按 config 启动 ws_gateway/stdio_gateway/http2_gateway；修复 ws_gateway 两个既有缺陷（缺 lws 事件线程、ws_callback 对 NULL user 解引用崩溃）
- 验证：8080(HTTP)/8081(WS)/8082(HTTP2) 三端口均在监听，Stdio 启用

### 3.4 agent-linux 协作契约
- **AGTS 任务描述符**：新增 [task_desc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/commons/include/airymax/task_desc.h)（128B aligned(64)，magic 0x41475453）与 [task_desc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/commons/utils/task/src/task_desc.c)（创建/校验/CRC-32 IEEE 802.3），篡改 payload_len/crc32 分别返回 AIRY_EIPC_PAYLOAD/AIRY_EIPC_CRC32
- **IPC 头文档对齐**：[02-l2-service-protocol.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxRT/30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md) §2.1 更新为 Layout C v4（11 字段、capability_badge@40、payload_len@48、crc32@52、reserved[72]@56、aligned(64)），与 [SC] 契约头逐字节一致

### 3.5 ecosystem 补齐
- **manager 统一 CLI**：[manager.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/manager/manager.py) 子命令：daemon status/start/stop、health（JSON-RPC 探活）、model show/validate、logs
- **contrib/strategies 真实实现**：[planning.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/contrib/strategies/planning/planning.py)（HierarchicalPlanner 支持可选 LLM 分解 + 启发式真实分解；ReactivePlanner 能力校验；ReflectivePlanner 反馈改进）、[dispatching.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/contrib/strategies/dispatching/dispatching.py)（4 策略真实 dispatch，按能力过滤+select 组装）
- **FileStorage**：[storage.py](file:///home/spharx/SpharxWorks/airymaxhub/ecosystem/openlab/openlab/core/storage.py) 新增 JSONL 文件存储后端（重启可恢复）
- **3 个新 Agent**：data_engineer / reviewer / analyst（contract.json + prompts/system.md + agent.py），AGENT_REGISTRY 8→11，registry.yaml implemented 7→10
- **examples**：research-agent / code-review-agent 补 requirements.txt

### 3.6 Bug 修复
| 位置 | 问题 | 修复 |
|------|------|------|
| research-agent/main.py:140 | `_try_online_search(proxy, query, max)` 3 实参 vs 2 参数签名，在线链路恒降级 | 去掉多余 proxy 实参 |
| config_version_cleanup.py:186 | `gzip.compress(file_path.encode())` 压缩路径字符串而非文件内容 | 读文件字节再压缩 |
| coding/contract.json | system2 遗留 gpt-4o-mini（DeepSeek 不支持） | 改 deepseek-v4-flash |
| base.py:167 | docstring 称 5 工具 | 更新为 9 工具 |
| router_std_remove_route | 假实现直接返回 INVALID_PARAM | 接入 protocol_router_remove_rule 真实删除 |
| a2a_v03_adapter.c | 4 处错误码全用 NOT_SUPPORTED + 复制粘贴日志 | 按语义改（PERMISSION_DENIED/STATE_ERROR/NOT_FOUND/ENOTCONN） |
| evaluate.py _call_gateway | 离线静默返回 {} 无提示 | 显式警告离线模式 |

### 3.7 测试与验证
- openlab：176 passed；agents：18 passed 1 skipped；prompts tuner：63 passed；manager：182 passed
- products/memoryrovol：CMake 构建成功（含 e2e_l3_l4 等测试目标）

---

## 4. v4.2 断点修复对照

| v4.2 断点 | 现状 | 修复方式 |
|-----------|------|---------|
| T1 shell_run ACL 默认拒绝 | ✅ 已修复 | tool_d 内置工具经 daemon_security ACL 显式授权（本轮 + 前轮） |
| T2 fs_list schema 与 validator 矛盾 | ✅ 已修复 | SSoT 对齐 required 标志 |
| T3/T4 超时过短 | ✅ 已修复 | LLM 超时/工具超时按元数据 timeout_sec |
| T5/T6 content=null 解析 | ✅ 已修复 | 工具回路协议处理 |
| T7/T8 MCP 缺 id/inputSchema | ✅ 已修复 | MCP server 补齐 |
| S1 TUI 不传 params.agent | ⏳ 部分 | gateway 编排分支已就绪；TUI 下发 DAG 为后续项 |
| S2 gateway 忽略 agent_file | ⏳ 部分 | 执行体链路（agent_d spawn/invoke）已可用 |
| S3 DAG 不落盘下发 | ⏳ 部分 | sched_d DAG 引擎已补全（前轮）；TUI 触发为后续项 |
| S4 sched_d 注册表恒空 | ✅ 已修复 | agent_d spawn 后自动 register_agent（前轮） |
| S5 sched_d 无队列/无 DAG 引擎 | ✅ 已修复 | sched_d 全套补全：Kahn 环检测/拓扑派发/级联取消/DAG worker（前轮） |
| S7 Python runner 直连 LLM 无 key | ✅ 已修复 | secrets.env 自动加载 + model.yaml SSoT 跟随（本轮） |
| M1-M8 记忆系统断点 | ⏳ 部分 | mem_d 方法已完整（evolve/health_check）；MemoryRovol 桥接/向量检索为后续项 |

---

## 5. 用户交互与视觉 UI

本轮完成：
- gateway WS/Stdio 接线 → 支持 WebUI 会话、进程内（子进程）交互通道
- manager CLI 统一入口（daemon/health/model/logs）
- TUI markdown 渲染（表格/标题/列表/引用/行内样式）：[markdown.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/markdown.rs)
- TUI 气泡式对话：[panels/chat.rs](file:///home/spharx/SpharxWorks/airymaxhub/sdk/tui/src/panels/chat.rs) 角色分侧气泡 + 流式增量占位气泡
- TUI 流式输出：gateway `POST /api/v1/chat/stream`（SSE）→ `client.rs::stream_chat` 逐块回调 → 增量渲染；llm_d 流式发送修复（阻塞式 `llm_stream_send_all` + `[DONE]` 不再误报 STREAM-FAIL）
- 工具级权限审批交互（Claude Code 风格 permission prompt）：tool_d `interactive_approval`（队列+条件变量+120s 超时）→ gateway `tool.pending`/`tool.approve` 转发 → TUI 审批按键 a/A/n（允许本次/始终允许/拒绝）
- 会话恢复 --resume（Codex sessions / Claude /resume）：TUI `--resume` 恢复记忆库最近 30 条 user/assistant 轮次
- 项目上下文文件机制（AGENTS.md 等价物）：TUI `--project` + openlab `project_context.py` 向上查找 AGENTS.md/CLAUDE.md/.airymax/AGENTS.md（.git 为界），注入系统提示首条

持续提升方向（后续项）：
- shell_run OS 级沙箱（bwrap/landlock，对标 Codex linux-sandbox）
- TUI 多会话 tab / 会话列表切换（当前 --resume 单会话恢复）

---

## 6. 遵循的工程规范

- **IRON-1~5**：本轮全部为真实实现（fs_glob/grep/edit/web_search、shutdown/get_stats、strategies、storage、AGTS 均真实可用），无新增桩
- **SSoT**：模型默认模型跟随 model.yaml；IPC 头以 [SC] 契约头为 SSoT；工具 schema 与 tool_d 元数据对齐
- **文档-实现一致**：IPC L2 §2.1 对齐；base.py 工具数文档同步
- **SPDX 头**：新增文件均带 SPDX-FileCopyrightText / SPDX-License-Identifier

---

## 7. 剩余未实现项（后续排期）

### 7.1 已完成项（本轮收官）

| 优先级 | 项 | 完成情况 |
|--------|-----|------|
| P0 | 会话恢复 --resume | 完成：TUI `--resume` 恢复记忆库最近 30 条 user/assistant；`resume_session_restores_history` 测试覆盖 |
| P0 | 工具级交互式权限审批 | 完成：tool_d `interactive_approval`（pending/approve/超时）→ gateway 转发 → TUI 按键 a/A/n；E2E 14/14 通过（allow/deny/超时/缓存防绕过/已授权直放） |
| P1 | MemoryRovol 桥接接线 | 完成：memoryrovol_bridge 10 处 ENOTSUP → 真实桥接；`test_c_link_12_memoryrovol_bridge` 10/10 通过 |
| P1 | 工作大厅持久化 | 完成：work_hall 状态 JSON 持久化到 `$AIRY_HOME/state/work_hall_state.json`（原子写 + 变更自动触发） |
| P1 | 服务发现多后端 | 完成：`AIRY_SD_BACKEND=shm\|file` 双后端（file 后端写 `$AIRY_HOME/state/sd/`） |
| P1 | 项目上下文文件（AGENTS.md） | 完成：openlab `project_context.py` + TUI `--project` 向上查找注入；182 tests / TUI 44 tests 覆盖 |
| P1 | git/diff/apply 工具 | 完成：tool_d 注册 git_exec/git_diff/git_apply（fork+pipe+poll，60s 超时 1MB 截断） |

### 7.2 交互式审批触发链路修复（本次新增）

- `handle_execute` 支持可选 `agent_id` 透传：真实 Agent（如 coding_v1）调用工具时以该主体做 ACL 判定，未授权进入 pending（此前固定 "tool_d" 全放行，审批永不触发）
- 审批链 `tool_approval_check_for_agent` → `safety_guard_bridge_check_for_agent` 按请求主体执行权限/审计守卫
- SDK `SyscallProxy.tool_execute` / agent `base.py` 透传 `self.agent_id`
- 缓存防绕过：缓存键纳入 agent_id，且仅静态 ACL 授权主体可命中缓存（allow 为一次性授予，重复调用必须重新审批）

### 7.3 待排期项 → 已全部完成（本轮 P2）

| 优先级 | 项 | 完成情况 |
|--------|-----|------|
| P2 | shell_run OS 级沙箱 | 完成：Landlock（内核文件系统白名单，workspace 可写/全局只读/strict 收紧）+ seccomp BPF 黑名单（mount/unshare/ptrace 等 23 个特权 syscall）+ rlimit 资源限制；fork 后 exec 前应用；`AIRY_TOOL_SANDBOX_MODE=off\|workspace\|strict` 配置；单测 22/22 + E2E 6/6（写 $HOME 拒绝、写 /tmp 允许、unshare/mount 拒绝） |
| P2 | mem_d 向量检索 | 完成：自研 TF-IDF（英文单词 + 中文单字/bigram tokenizer、IDF 平滑）+ 余弦相似度，与子串评分 0.6/0.4 加权融合；可选 OpenAI 兼容 embedding 后端（`AIRY_MEM_EMBEDDING_URL/KEY`，失败自动降级）；JSONL 持久化不变；13 测试通过（语义排序/中文/降级/一致性） |
| P2 | syscall.xml codegen 管道 | 完成：`atoms/syscall/include/syscall.xml` 为 SSoT（23 syscall），`tools/codegen/syscall_gen.py` 生成枚举头 + 分发表，`--check` 防漂移接入 CMake（构建时校验）+ CI workflow；系统调用测试 3/3 无回归 |
| P2 | MCP 客户端能力 | 完成：`protocols/standards/mcp/{include/mcp_client.h,src/mcp_client.c}`（stdio 帧解析状态机 + HTTP），gateway_d 经 `AIRY_MCP_CLIENTS` 环境变量连接外部 MCP server、`<client>_<tool>` 前缀注册工具并转发 tools/call；E2E：mock server 工具 `mock_mock_echo` 可列出可调用；同时修复 gateway MCP server tools/list/resources/list 缺 JSON-RPC result 包装的合规 bug |
| P2 | cupolas 独立 daemon | 完成：`daemons/cupolas_d/`（check_permission/sanitize/execute_command/add_rule/audit_flush/get_stats/shutdown 8 方法，cupolas.sock）；修复 cupolas workbench 既有管道死锁 bug（子进程输出无人读取 → 永久阻塞）；JSON-RPC 全方法验证通过，cupolas_d 独立运行中 |

### 7.4 用户交互/视觉优化（本轮）

- TUI 工具审批提示条（Claude Code 风格 permission prompt）：pending 审批时在输入栏上方插入高亮横幅，展示工具/主体/参数预览与 `[a] 允许本次  [A] 始终允许  [n] 拒绝` 快捷键提示；TUI 44+32 测试通过，release 已部署

---

## 8. 涉及路径索引

- 执行体：`ecosystem/agents/airymax_agents/{base.py,runner.py}`、`ecosystem/openlab/openlab/{agents/llm.py,core/llm.py,core/storage.py,contrib/strategies/}`、`agentrt/daemons/tool_d/src/{builtin.c,service.c}`
- daemon 标准方法：`agentrt/daemons/common/include/daemon_main.h`、16 个 daemon 的 `src/main.c`
- gateway：`agentrt/daemons/gateway_d/src/{main.c,service.c,gateway_business_handler.c}`、`agentrt/gateway/src/gateway/{ws_gateway.c,stdio_gateway.c,http2_gateway.c}`
- 契约层：`agentrt/commons/include/airymax/{ipc.h,task_desc.h}`、`agentrt/commons/utils/task/src/task_desc.c`、`02-l2-service-protocol.md`
- protocols：`agentrt/protocols/src/airy_protocol_interface.c`、`agentrt/protocols/core/router/src/protocol_router.c`、`agentrt/protocols/standards/a2a/src/a2a_v03_adapter.c`
- manager：`ecosystem/manager/manager.py`、`ecosystem/manager/model/model.yaml`
- TUI：`sdk/tui/src/{app.rs,client.rs,markdown.rs,memory.rs,main.rs}`、`sdk/tui/src/panels/chat.rs`
- 流式端点：`agentrt/gateway/src/gateway/http_gateway_routes.c`、`agentrt/daemons/llm_d/src/{main.c,providers/{provider.c,deepseek.c}}`
- 交互式审批：`agentrt/daemons/tool_d/src/{tool_interactive_approval.c,executor.c,main.c,service.c,cache.c,tool_approval.c,safety_guard_bridge.c}`、`sdk/sdk-python/agentrt/syscall.py`
- 项目上下文：`ecosystem/openlab/openlab/core/project_context.py`、`ecosystem/agents/airymax_agents/runner.py`
- sched_d 队列日志：`agentrt/daemons/sched_d/src/sched_service_impl.c`、`agentrt/commons/utils/logging/src/logging.c`（AIRY_LOG_LEVEL）
- 参考实现：`.engineer-reference/{codex-main,claude-code-main,atomcode-main}`
