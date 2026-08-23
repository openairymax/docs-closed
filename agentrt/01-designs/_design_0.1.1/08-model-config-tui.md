Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"From data intelligence emerges."

# 模型自由配置与 TUI 体验完善设计方案（模型链路 + 功能复活 + 视觉）

> **文档定位**：agentrt 用户态运行时「生产全量运行」体验完善——模型自由配置链路（A）+ TUI 空壳功能复活（B）+ 视觉改善（C）的**设计方案**\
> **文档状态**：DRAFT（待评审）\
> **最后更新**：2026-08-06\
> **上级文档**：[AgentRT 文档中心](../../README.md)\
> **关联文档**：[06-agent-gateway-wiring.md](../_design_0.1.1/06-agent-gateway-wiring.md)、[07-gateway-mem-acl.md](../_design_0.1.1/07-gateway-mem-acl.md)、[02-l2-service-protocol.md](../../../../docs/AirymaxRT/30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md)

---

## 1. 背景与目标

### 1.1 现状（已确认的真问题）

用户反馈三类问题，经调研确认根因如下：

| 问题 | 根因（调研证据） |
|------|------------------|
| **CLI 配置不完善、模型不能自由配置** | 模型 SSoT `ecosystem/manager/model/model.yaml` 的 `global.default_model` **代码从不读取**（llm_d YAML 加载器只解析 providers/models 两段）；gateway 硬编码 `GW_LLM_DEFAULT_MODEL "deepseek-v4-flash"`；TUI 无模型选择 UI（`RunRequest.model` 从不填充）；wizard"手动配置模型"是占位标记 |
| **很多功能不能用** | TUI F2 配置 / F3 日志 / F4 记忆 / F5 插件四面板渲染代码已写好但数据字段从不填充（`config_content`/`logs`/`memory_stats`/`plugin_list` 仅初始化）；`/api/v1/logs|memory/stats|plugins` 三个 HTTP 方法是 dead code；状态栏宣称的 turn/tokens/cost/elapsed_time 从不渲染；MCP/A2A 开关永远 false；`exit` 命令无效 |
| **页面视觉展示差** | 主题令牌（theme.rs "极简蓝晶"）齐全，但空态面板 + 无状态栏 + 无模型选择控件 → 整体"空壳感" |

### 1.2 目标与架构原则

- **A. 模型自由配置**：用户可在任意产品入口（TUI / agentrt CLI / airy_cli）自由选择与配置模型，全链路真实生效。
- **B. 功能复活**：F2-F5 面板、状态栏、MCP/A2A 指示器从"空壳入口"变为真实可用。
- **C. 视觉改善**：基于既有主题令牌，复活面板用真实数据渲染 + 状态栏 + 模型选择控件。
- 生产级标准（IRON-1~5）：真实实现、无桩函数、无占位；一个 commit 一个逻辑变更。
- 机制/策略分离（IRON-3）：llm_d 是机制层（模型解析/路由），模型选择策略在客户端（TUI/CLI）。
- [SC] 同源约束（IRON-9）：不触碰共享契约层 10 个头文件；遵循 L2 服务协议 `llm.*` 命名空间。

---

## 2. 模型自由配置设计（A）

### 2.1 配置面：SSoT + 用户覆盖文件

```
SSoT（仓库，权威基线）                   用户覆盖（$AIRY_HOME/config/model.yaml）
ecosystem/manager/model/model.yaml  +   （可不存在；存在则合并，用户优先）
```

- `model.yaml` 保持单一 SSoT 地位不变（模型/定价/路由的权威基线）。
- 新增用户级覆盖文件 `$AIRY_HOME/config/model.yaml`（用户自由增删 provider/模型/改 default）。
- 合并规则（与既有 YAML 解析器同构，避免重写解析器）：
  - **二次加载合并**：llm_d 启动时先 `svc_load_model_config(主配置)`，再检测用户覆盖文件，存在则 `svc_load_model_config(覆盖文件)` 得到第二组 provider，**同名 provider 后加载覆盖先加载**（用户优先），不同名追加。
  - `global` 段：主配置 + 用户覆盖均可设置 `default_provider`/`default_model`，用户覆盖优先。
- **效果**：用户无需改动仓库，在 `$AIRY_HOME/config/model.yaml` 写自己的模型即生效（重启 llm_d）。

### 2.2 查询面：llm_d 增加两个能力

**A2-1. `global` 段生效**：YAML 加载器增加 `global` 段解析，输出 `default_model`/`default_provider` 到 `llm_service_t`（新增字段 `char default_model[128]`）。

**A2-2. 缺省默认模型**：`llm.complete` 的 `parse_params` 中 model 缺失时不再报 `INVALID_PARAM`，改填 svc 的 `default_model`（无 default 才报错）。修复"llm_d 无缺省模型概念"缺口。

**A2-3. `llm.list_models`**：新增 L2 方法（注册 `list_models`，前缀 `llm.`），遍历 registry 返回：
```json
{"result": {"models": [
  {"name": "deepseek-v4-flash", "provider": "deepseek", "default": true,
   "context_window": 65536, "capabilities": ["chat","completion"]},
  ...
], "default_model": "deepseek-v4-flash", "default_provider": "deepseek"}}
```
客户端据此渲染模型列表（选择面依赖）。

### 2.3 选择面：三入口统一

| 入口 | 设计 |
|------|------|
| **TUI** | ① wizard 步骤 2 真正拉取 `llm.list_models` 渲染模型列表供选择（选中项持久化）；② F2 配置面板内模型列表导航（↑↓ 选择，Enter 生效）；③ 对话内 `/model <name>` 命令即时切换 |
| **agentrt CLI** | `agentrt llm list` 改为列出模型（含 provider/default 标记）；`agentrt config set llm.default_model <name>` 写入用户覆盖文件 |
| **airy_cli** | 保留 `AIRY_MODEL_T2/T1F/T1P` env 注入（三模型分离），新增 `/model` 查看当前模型；三模型缺省时回落 llm_d 默认 |

### 2.4 使用面：model 参数链路打通

- **TUI**：`client.rs` 的 `send_message` 填充 `RunRequest.model`（当前模型偏好）；偏好持久化到 `$AIRY_HOME/tui/config.toml`（新增，与 wizard.toml 同目录）。
- **gateway**：`agent.run` 已支持 `params.model`（用户显式 > env > 默认）；默认模型从硬编码宏提升为：`AIRY_AGENT_MODEL` env > 用户覆盖文件 `default_model` > 宏兜底。
- **llm_d**：`llm.complete` 收到 model 后按既有 registry 精确匹配（BAN-137 用户指定即尊重），不匹配回落 router 策略。

### 2.5 部署修复

- `tools/deploy/systemd/agentrt-llm.service`：`ExecStart=llm_d --manager <model.yaml>`。
- `tools/deploy/docker/entrypoint.sh`：llm_d 单独传 `--manager`（其参数解析只认 `--manager/--tcp/--help`，不认 `--config`）。

---

## 3. TUI 功能复活设计（B）

| 面板 | 现状 | 复活方案（真实数据） |
|------|------|---------------------|
| **F2 配置** | 恒显"配置未加载" | 读取并渲染：`$AIRY_HOME/config/model.yaml`（存在则合并展示）+ 仓库 model.yaml + 关键 env（AIRY_AGENT_MODEL/AGENTRT_GATEWAY_URL）+ 模型列表选择控件 |
| **F3 日志** | 永远空 | 读取 `$AIRY_HOME/logs/agentrt-tui.log` 尾部 N 行渲染（本地即有，不依赖网关）；保留 `get_logs()` 作为远程来源（非死代码） |
| **F4 记忆** | 永远空 | 渲染本地 `memory.jsonl` 统计（`self.memory.len()` + 最近 N 条摘要）+ skills 计数 |
| **F5 插件** | 永远空 | 渲染技能库 `skills.jsonl` 条目列表（名称/描述/触发词） |
| **状态栏** | 宣称但不存在 | 新增底部状态栏（品牌栏与快捷键栏之间或替代）：回合数、Token、成本、耗时、模型名、MCP/A2A 指示灯 |
| **MCP/A2A 开关** | 永远 false | 从 `$AIRY_HOME/tui/config.toml` 读取持久化开关，状态栏显示指示器 |

---

## 4. 视觉改善设计（C）

基于既有 `theme.rs` 令牌（PRIMARY 56,102,250 / ACCENT / SUCCESS / WARNING / DANGER），不重写主题：

1. **状态栏**：新增 `ui.rs` 底部一行——左：回合/Token/成本/耗时（dim 色）；中：当前模型（ACCENT 加粗）；右：● MCP ● A2A（SUCCESS/DIM 灯）。
2. **面板真实渲染**：F2-F5 复用各 panels 模块已写的渲染骨架，填充真实数据；空态分支保留（仅数据缺失时显示）。
3. **模型选择控件**：F2 面板内模型列表行——当前模型 PRIMARY 反白 + `●` 标记；↑↓ 移动、Enter 选中、Esc 关闭（焦点在面板内独立于快捷键栏）。
4. **一致性**：所有新增视觉沿用 theme.rs 函数（bg/surface/border/text/dim/faint），不散落硬编码颜色。

---

## 5. 文件修改清单

### A 模型链路（C 后端）

| 文件 | 修改 |
|------|------|
| `agentrt/daemons/llm_d/src/service.h` | `llm_service_t` 增 `default_model[128]` |
| `agentrt/daemons/llm_d/src/service.c` | YAML 加载器解析 `global` 段；`llm_service_create` 加载用户覆盖文件二次合并；新增 `llm_service_list_models()` |
| `agentrt/daemons/llm_d/src/main.c` | `parse_params` model 缺省回落 default；注册 `list_models` 方法 |
| `agentrt/daemons/gateway_d/src/gateway_business_handler.c` | 默认模型解析：env > 用户覆盖 > 宏 |
| `tools/deploy/systemd/agentrt-llm.service` | 补 `--manager` |
| `tools/deploy/docker/entrypoint.sh` | llm_d 单独传 `--manager` |

### B/C TUI（Rust）

| 文件 | 修改 |
|------|------|
| `sdk/tui/src/config.rs`（新增） | 用户配置 `config.toml` 读写：default_model、mcp_enabled、a2a_enabled |
| `sdk/tui/src/client.rs` | 填充 `RunRequest.model`；新增 `list_models()`（llm.list_models）；复活 `get_logs/get_memory_stats/get_plugins` 接线 |
| `sdk/tui/src/wizard.rs` | 步骤 2 拉模型列表真实选择 |
| `sdk/tui/src/app.rs` | 填充 config_content/logs/memory_stats/plugin_list；/model 命令；状态栏数据源 |
| `sdk/tui/src/ui.rs` | 状态栏渲染；F2 面板模型选择控件接入 |
| `sdk/tui/src/panels/{config,logs,memory,plugins}.rs` | 真实数据渲染（骨架已存在，填数据） |
| `sdk/tui/src/theme.rs` | 如需新增状态栏专用令牌 |

### CLI（Rust + C）

| 文件 | 修改 |
|------|------|
| `sdk/cli/src/commands/llm.rs` | `llm list` 列出模型（改走 llm.list_models） |
| `sdk/cli/src/commands/config_cmd.rs` | `config set llm.default_model` 写入用户覆盖文件 |
| `agentrt/tools/airy_cli/main.c` | `/model` 命令查看当前模型；缺省回落 llm_d default |

---

## 6. 实施步骤

1. **llm_d 后端**（A2）：global 解析 + 用户覆盖文件合并 + list_models + 缺省默认模型 → 单测 + curl 验证。
2. **gateway**（A1.5）：默认模型解析提升 → agent.run 无 model 时回落验证。
3. **TUI 模型选择**（A3/A4）：config.rs + client.rs + wizard + /model 命令 → cargo test。
4. **TUI 功能复活**（B）：F2-F5 数据填充 + 状态栏 → cargo test + 手动 e2e。
5. **CLI**（A3）：sdk/cli llm list + config set；airy_cli /model。
6. **部署修复**（A2.5）：systemd/docker。
7. **回归**：ctest + cargo test + 15 daemon e2e + 模型选择链路 e2e。

---

## 7. 风险

| # | 风险 | 缓解 |
|---|------|------|
| R1 | 用户覆盖文件合并破坏 SSoT 一致性 | 覆盖仅限同名 provider/global，不修改仓库文件；文档标注"用户文件优先"语义 |
| R2 | llm_d 缺省模型改动影响既有调用方 | 缺省仅当 model 缺失时生效；显式 model 行为不变（BAN-137 尊重用户指定） |
| R3 | TUI 拉模型列表失败（llm_d 未带 --manager） | wizard/面板显示错误与提示；网关默认模型兜底仍可用 |
| R4 | 配置面板展示大文件性能 | model.yaml 文本渲染限制行数 + 折叠；列表只渲染模型名 |
| R5 | [SC] 同源约束 | 全部改动在 agentrt 内部；L2 协议扩展 `llm.list_models` 遵循命名空间，不触共享契约头文件 |

---

## 8. 出口标准

1. `curl` llm_d：`llm.complete` 无 model 参数 → 返回 default_model 结果；`llm.list_models` 返回模型列表（含 default 标记）。
2. `$AIRY_HOME/config/model.yaml` 自定义 provider/模型 → llm_d 重启后生效（registry 可匹配自定义模型）。
3. TUI：wizard 可选择模型；`/model deepseek-v4-flash` 切换生效；F2-F5 面板显示真实数据；状态栏显示回合/Token/成本/耗时/模型。
4. `agentrt llm list` 列出模型；`agentrt config set llm.default_model <name>` 写入用户覆盖文件。
5. systemd/docker 部署 llm_d 带 `--manager`。
6. 全量回归：ctest + cargo test + 15 daemon e2e 无回退。

---

## 9. 同源约束说明

- 全部改动位于 agentrt 仓库内（llm_d / gateway_d / sdk / tools）；
- 不触碰 [SC] 共享契约层 10 个头文件（`agentrt/commons/include/airymax/`）；
- L2 服务协议扩展 `llm.list_models` 遵循 `llm.*` 命名空间既有契约；
- 用户覆盖文件 `$AIRY_HOME/config/model.yaml` 是运行时配置，非代码共享。

---

*本方案为 DRAFT，待评审确认后实施。*
