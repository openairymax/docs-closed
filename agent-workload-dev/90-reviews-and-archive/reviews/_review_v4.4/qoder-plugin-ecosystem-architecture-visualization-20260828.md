# Qoder 插件生态研究与 architecture-visualization 插件重构可行性报告

> **报告编号**：REVIEW-AGENTRT-2026-08-28-QODER
> **报告类型**：竞品/标杆工程研究（插件生态横评 + 单插件深度拆解 + 重构可行性）
> **研究对象**：Qoder 插件生态（`qoder-bundler` 官方内置 4 款 + `qoder-marketplace` 市场 4 款），重点深拆 `architecture-visualization`（架构可视化）
> **对照对象**：`agentrt`（AirymaxRT 极境智能体运行底座，0.1.5 版本）及其 `ecosystem` 生态层（manager / prompts / markets / skills / agents 五叶仓）
> **产出目录**：`docs-closed/agentrt/00-reviews/_review_v4.4/`
> **审查日期**：2026-08-28
> **审查人**：SPHARX 工程标准组
> **状态**：研究性报告（供架构演进决策参考）

---

## 摘要

Qoder 是字节跳动/通义系 AI IDE 生态（Qoder.cn），其插件体系是国内编码智能体插件规范中**最完整、最可机器校验**的一套：双 manifest（发布/运行时分离）、组件声明即校验、hooks 事件模型、MCP 一等公民、skill 目录即单一可调用单元。其中 **`architecture-visualization`（架构可视化）插件是 agentrt 最值得整体重构吸收的对象**——它不是"画图工具集合"，而是一套**证据驱动的软件架构建模/评审/演进方法论**：13 个 SKILL 按「路由 → 场景 → 基础」三层 MECE 组织，共享契约层 + 结构化证据模型（node/edge/sourceRefs/confidence）+ 文本图源交付规则 + 三个 Canvas viewer + 示例冒烟测试。

对照 agentrt：现有 `ecosystem/skills`（SkillPlugin 双实现）是**执行型技能**（输入/输出 JSON Schema 契约），但缺少**场景型/方法论型技能**（prompt 驱动、意图路由、共享契约、证据模型、文件交付规则）这一层；`plugin_d` 已有权限驱动加载，`hook_d` 已有 agent 内部生命周期 hooks（pre/post_tool 等），但缺**会话级/IDE 级 hooks 与上下文注入通道**；`markets` 已有 package.yaml 分发，但缺**离线 validator 与运行时/发布清单分离**。

本报告给出：Qoder 插件生态全景拆解（8 款插件）、architecture-visualization 深度拆解（13 SKILL + 契约层 + 证据模型 + viewer）、agentrt 生态现状对照、**14 条可借鉴机制清单（P0/P1/P2）**、以及 **architecture-visualization 重构为 agentrt 自带插件的完整可行性方案**（结论：可行，建议作为 ecosystem/markets 下的 `architecture-visualizer` 包落地，分层为契约层 + 场景技能层 + 渲染服务层）。

---

## 一、Qoder 插件生态全景研究

### 1.1 插件来源与分类

研究对象来自 `/works-engineering/.engineer-reference/user-reference/plugins/`（Qoder 客户端缓存目录，`installed_plugins_v2.json` 登记 8 款），分两个来源：

| 来源 | 插件 | 版本 | 定位 |
|------|------|------|------|
| `qoder-bundler`（官方随 IDE 内置） | `better-harness` | 0.2.9 | AI 编码智能体工程化评估 + CLI + hooks |
| | `security-scan` | 0.8.1 | 安全审查（三档能力，自举二进制） |
| | `computer-use` | 1.0.1 | Windows 桌面 UI 自动化（纯 MCP） |
| | `qoder-create-plugin` | 0.1.0 | 元插件：造插件的插件（隐藏） |
| `qoder-marketplace`（市场拉取） | `architecture-visualization` | 0.1.0 | 架构可视化（本报告深拆对象） |
| | `superpowers` | 5.1.0 | 方法论 skill 库（obra 上游适配） |
| | `redis` (redis-development) | 1.0.0 | Redis 官方 AI 最佳实践规则库（29 规则） |
| | `qmind-knowledge-cn` | 0.2.0 | QMind 知识库 CLI 工具集 |

关键观察：**官方内置插件（bundler）是"能力型"**（安全扫描、桌面操作、工程评估），**市场插件是"方法论/知识型"**（架构、开发流程、规则库、知识管理）。两类插件形态差异巨大，agentrt 生态定位"能力型 + 方法论型"都要覆盖。

### 1.2 插件清单规范：双 manifest 设计

Qoder 插件采用**发布清单与运行时清单分离**的双 manifest 结构（一手权威来自 `qoder-create-plugin/skills/create-plugin/references/qoder-plugin-manifest.md` 与 `qoder-components.md`）：

| 层 | 文件 | 消费方 | 字段特点 |
|----|------|--------|----------|
| 发布 manifest | 仓库根 `plugin.json` | 市场/安装器 | 基础字段 + `marketplaceName` / `defaultEnabled` / `visibility` / `preserveUpstreamMetadata` |
| 运行时清单 | `.qoder-plugin/plugin.json` | 运行时 daemon | 基础字段 + 组件声明 `skills` / `hooks` / `mcpServers` / `rules` / `agents` / `commands` + 可选 `interface`（市场 UI 元数据：`displayName`/`shortDescription`/`capabilities`/`defaultPrompt`/`brandColor`/`screenshots`） |

**组件声明规则**（机器可校验）：
- 所有组件路径必须以 `./` 开头、不得含 `..`、不得为绝对路径；
- JSON 组件路径以 `.json` 结尾；命令源必须是 `.md`；
- 声明必须对应磁盘上真实存在的文件（校验器强查）；
- 插件目录名与 `plugin.json.name` 必须一致，kebab-case。

**打包规则**：zip 根必须直接含 `.qoder-plugin/plugin.json`；禁止 `.codex-plugin`/`.cursor-plugin`/`.claude-plugin` 等跨平台冗余目录与本地运行时状态（`settings.local.json`、`__MACOSX`、`.DS_Store`）。

**离线校验器**（`validate_qoder_plugin.py`，纯 Python 零依赖）：清单存在性 → JSON 合法性 → `name`+`version` 必填 → 组件路径不越界且真实存在 → 每个 SKILL.md 有 `name`+`description` frontmatter → 禁止目录清单。**装前校验、装后 smoke** 的分级验证策略避免了"运行时才发现组件不可用"。

### 1.3 Skill 格式规范

- 目录约定：`skills/<skill-name>/SKILL.md`，**单目录 = 单一可调用单元**；可带 `references/`（证据/指南）、`scripts/`（辅助脚本）、`assets/`。
- frontmatter：必填 `name`（与目录一致）+ `description`（承担语义触发路由，约定 "Use when..." 句式）；可选 `version` / `description_zh` / `user-invocable` / `argument-hint`。
- 拆分策略：单一工作流 = 单 skill；仅当存在多个独立可调用工作流或内部 helper 才拆多 skill。
- **description 是触发入口**（superpowers 的"1% 可能适用就必须调用"规则依赖它），**内容才是行为规范**；触发条件、安全约束、引用文件关系必须保留。

### 1.4 Hooks 机制

Qoder hooks 是**会话/IDE 生命周期事件钩子**，与 agentrt 的 agent 内部生命周期 hooks 互补：

```json
{
  "hooks": {
    "SessionStart": [{ "matcher": "startup|clear|compact", "hooks": [{"type": "command", "command": "...", "timeout": 120, "async": false}] }],
    "PostToolUse": [{ "matcher": "Edit|Write|MultiEdit|NotebookEdit", "hooks": [{"type": "command", "command": "..."}] }],
    "Stop": []
  }
}
```

- 事件集：`SessionStart`（会话注入）、`PostToolUse`（编辑后实时检查）、`Stop`（停止时评审）等；
- 协议：hook 脚本 **stdin 收 JSON**；**退出码三态语义**：`0` 放行/继续、`2` 阻止（blockable 事件）、其他 = 非阻塞错误；
- hook stdout 可输出 JSON（`additionalContext`）注入会话上下文；
- `${QODER_PLUGIN_ROOT}` 占位符由运行时注入插件根路径；
- 跨平台：polyglot `.cmd`（cmd 段内嵌 bash 段）或"cmd 委托 bash"；无扩展名 hook 文件名规避 `.sh` 自动前缀；找不到 bash 时静默降级。

**superpowers 的 SessionStart 上下文注入**是精华：`hooks/session-start` 读取 `using-superpowers/SKILL.md` 全文 → bash 参数替换做 JSON 转义 → 按消费协议分派输出（`CURSOR_PLUGIN_ROOT` 存在 → `additional_context`；`CLAUDE_PLUGIN_ROOT` 且非 Copilot → `hookSpecificOutput.additionalContext`；否则 → 顶层 `additionalContext`）。**同一 hook 脚本适配三种消费协议**，用上下文注入取代修改 system prompt。

### 1.5 MCP 集成方式

`mcp.json`/`.mcp.json`：`{"mcpServers": {"<name>": {"command": "...", "args": [], "cwd": ".", "env_vars": [...]}}}`；STDIO 本地 / SSE / Streamable HTTP 远程三种传输。凭据禁止入库，用 `<YOUR_TOKEN>` 占位符 + `CONNECTORS.md` 文档化。computer-use 展示了"**MCP server 的可执行体由宿主共享运行时提供，插件只做定位与包装**"（launcher 解析 `QODER_HOME` → 定位共享 exe → 设置日志 env → exec），避免每插件捆绑二进制。

### 1.6 规则库范式（redis-development）

Redis 官方 AI 最佳实践包是**"规则即代码"治理管线**的完整范本：
- 单规则文件：`<prefix>-<desc>.md`，frontmatter（`title` / `impact` / `impactDescription`（量化，如 10x/50%）/ `tags` / `description` / `alwaysApply`），正文 **Correct-first + Pattern A（Incorrect 反模式）/ Pattern B（When to use / When NOT needed）二选一**；
- 元文件：`_sections.md`（文件名前缀 → 类别映射，`data-`/`ram-`/`rqe-`/`vector-`…）、`_template.md`（模板）、`_contributing.md`（写作规范，排除出构建）；
- **三形态输出**：`rules/` 单文件（细粒度注入）→ `SKILL.md`（索引 + 速查）→ `AGENTS.md`（编译全量文档，约 2200 行）；`metadata.json` 供市场检索；
- 写作规范强调：具体模式而非抽象建议、量化影响、多语言可运行示例、语义化命名、注释解释 why。

### 1.7 工作流设计范式（三个精华案例）

**security-scan（路由状态机 + 强制工具契约）**：
- 6 条显式路由优先级（全仓扫描→指定路径→显式 L2→显式 L3→裸命令固定 picker→隐式 push/PR/merge gate）；
- 显式状态机：`AWAITING_REMEDIATION_DECISION` → `POST_FIX_HALT` → `SCAN_SKIPPED_FOR_CURRENT_HANDOFF`（内存态，新 commit 清除）；
- 强制工具调用：必须真调用 `AskUserQuestion`（question 字段非空、选项顺序固定），禁止文本模拟；
- 静默执行：不向模型暴露 qodersec 命令/stdout/JSON/内部路由；唯一可透出 notice 白名单化（`qoder_credits_exhausted`）；
- fail-closed 配置解析：SKILL 只能消费 `qodersec review settings --format=json` 的 JSON 字段，`true` 才启用，禁止直接读 settings 文件。

**qmind-knowledge-cn（幂等/重放安全表）**：
- 用表格把"哪步可重试、哪步不可重放"显式编码给 agent（upload-folder 幂等、notebook create 不幂等需先 list、compile start 无幂等键消费 token 不可重放、delete 幂等 404）；
- 异步任务三态返回契约：`accepted/rejected/uncertain`，`uncertain` 必须保留证据并停止（POST 无幂等键绝不自动重放）；
- CLI 自举模式：首用按 OS/ARCH 探测下载到固定缓存路径，能力探测触发一次性升级（`compile help` 里没有 `compile start` 才 self-update）。

**better-harness（评估模型文档化 + 证据-评分脱钩）**：
- 5 维度（Task Understanding / Controlled Execution / Change Validation / Reliable Delivery / Learning Capture）× 15 check 的评分契约，每 check 有 `id` / `Look for`（资产+判定方法）/ `Typical findings`；
- **七态证据**：`Present / Wired / Exercised / Outcome-supported / Missing / Unobserved / N/A`，评分 ceiling 表：`Missing→59，Present→74，Wired→84，Exercised→94，Outcome-supported→100`；"配置≠行为"；
- finding 契约：一个可修复的因果问题映射一个 primary check；`interventionLedger` 跨 session 保持学习连续性；
- 三条独立证据通道（session/project/agent assets）并行派发只读 agent，brief 隔离防污染；
- CLI 机器契约：`--json/--no-color/--quiet/--no-input/--dry-run/--yes`；stdout parser-safe（禁 spinner/颜色），日志走 stderr；命令分 `workflow/advanced/maintainer` 三档；argv 数组分发；破坏性动作先 plan/dry-run 再 apply。

### 1.8 机制横向总结（对 agentrt 直接可复用的规范）

| # | 机制 | 最佳范本 | agentrt 现状 |
|---|------|----------|-------------|
| 1 | 发布/运行时清单分离 | create-plugin 规范 | 无（markets 仅 package.yaml） |
| 2 | 组件声明即校验 + 离线 validator | validate_qoder_plugin.py | 部分（plugin_d 运行期校验 manifest） |
| 3 | 会话级 hooks 事件模型 + 三态退出码 | security-scan / superpowers | 有 agent 内部 hooks（hook_d），无会话级 |
| 4 | SessionStart 上下文注入（替代改 system prompt） | superpowers session-start | 无 |
| 5 | MCP server 一等公民 + 共享运行时 launcher | computer-use | 无（gateway 为自研 JSON-RPC） |
| 6 | 规则库三形态管线（模板+前缀+编译） | redis-development | 无（skills 无 rules 形态） |
| 7 | 工作流状态机 + 强制工具调用 + 静默执行 | security-scan | 部分（CLI 决策链可视化，非 skill 内状态机） |
| 8 | 幂等/重放安全表 | qmind | 部分（事件流单真相源） |
| 9 | 评估模型文档化 + 证据-评分脱钩 | better-harness | 无 |
| 10 | CLI 机器契约（parser-safe/dry-run 分离） | better-harness | 部分（CLI/TUI 已成熟） |
| 11 | 自举下载二进制 + 版本钉扎 + 防递归 | security-scan / qmind | 无 |
| 12 | 自包含分发 + 校验签名 | create-plugin 打包规则 | 部分（发布链路 SSoT 已收敛） |

---

## 二、architecture-visualization 插件深度研究

### 2.1 定位与设计哲学

**一句话定位**：Model, review, evolve, and maintain **evidence-backed** software architecture（建模、评审、演进并维护"证据背书"的软件架构）。

其 README 明确的设计取舍——**"Canvas 支持刻意收窄"、"插件不捆绑语言提取器或确定性模型生成器"**：
- 只给架构产物（agent 在工作流中会写出的文件）配格式查看器：`canvases/dot/`（Graphviz）、`canvases/dsl/`（Structurizr DSL）、`canvases/mermaid/`（Mermaid）；
- 不提供语言专属提取器/模型生成器——因为"这些会被用户的语言、框架、部署栈、约定、证据源约束"；**默认工作流是 agent 检查目标项目后直接写出 Markdown/JSON/DOT/DSL/Mermaid/Draw.io 交付物**。

这一取舍与 agentrt「机制不是策略」「内核保持简单，智能在用户态」的工程哲学高度同构：**插件提供方法论与契约，不做确定性提取**。

### 2.2 13-SKILL 三层组织（MECE）

`skills/README.md` 公开面是"按架构任务优先路由，工作流内再选图/视图格式"，13 个 SKILL 分三层：

**Tier 1 — 路由层**
| Skill | 职责 |
|-------|------|
| `explore` | 宽泛架构请求的路由器，选最小可用场景技能集；含 Git 变更路由（PR/branch/commit）与业务应用路由 |

**Tier 2 — 场景层（9 个，每个回答一个不同架构任务）**
| Skill | 回答的问题 |
|-------|-----------|
| `system-modeler` | 今天这个系统/仓库/平台架构是什么？（证据背书当前态建模） |
| `flow-visualizer` | 业务动作/服务调用/事件/数据如何流动？（共享工作流，视图随流型变化） |
| `dependency-impact-analyzer` | 谁依赖谁，这个变更会影响什么？（静态依赖映射 + 影响遍历） |
| `deployment-topology-analyzer` | 它在哪里运行、如何连接、如何发布运维？（运行时拓扑与逻辑结构分离） |
| `evolution-planner` | 架构应如何变化、为什么？（当前/目标差距 + 决策建模 + 迁移切片） |
| `risk-quality-reviewer` | 这个架构对其目标是否足够健康、风险在哪？（评审/风险/技术债合并） |
| `legacy-system-visualizer` | 如何在证据不足时安全理解与改造遗留系统？（低证据发现 + 现代化切片） |
| `architecture-communicator` | 如何向特定受众清楚解释这个架构？（不发明新模型，只选视图适配受众） |
| `architecture-health` | 架构产物是否当前、可追溯、可维护？（living architecture / CI 化校验） |

**Tier 3 — 基础层（3 个）**
| Skill | 职责 |
|-------|------|
| `c4model` | C4/Structurizr DSL 语义源（landscape/context/container/component） |
| `graphviz` | 密集关系图 DOT 源（依赖/流程/部署/风险/血缘/影响图） |
| `drawio` | 可选 Draw.io / diagrams.net 可编辑交付 + 本地 MCP 指引（仅显式请求时用） |

**MECE 边界设计要点**：
- 场景按"架构任务"划分（结构/流动/依赖影响/部署运行时/演进/评审/遗留/沟通/健康），而非按"图类型"划分——`explore` 明确禁止"因为用户说了 diagram 就直接路由到视图"；
- `c4model`/`graphviz`/`drawio` 是**基础能力**而非场景；`drawio` 是**交付基础**而非生成管线依赖（保持证据模型为真相源，Draw.io 只是派生可编辑交付物）；
- 每个场景 SKILL 都声明 **NOT in scope**（如 system-modeler 明确"质量门发现→risk-quality-reviewer、DSL 语法问题→architecture-health、修复建议→evolution-planner"），防止职责越界。

### 2.3 共享契约层（references/）

所有场景 SKILL 通过 **Mandatory Shared Gate** 强制先读的共享契约（`explore` 未加载则各 SKILL 自行加载）：

| 参考文件 | 内容 |
|----------|------|
| `architecture-contract.md` | 核心原则（evidence first / 状态分离 / 一视图一问题 / 稳定 ID / 渐进披露 / 可读摘要 / skill 透明度）+ 视图层级（L0 业务能力→L4 代码符号 + 运行时拓扑 + 数据拓扑）+ 标准产物形状 + 证据置信度（high/medium/low/unknown）+ 图表接地规则 + 视觉约定 |
| `architecture-evidence-model.md` | 结构化证据模型：node 字段（id/label/type/state/owner/description/sourceRefs/confidence）+ edge 字段（from/to/type/sync/protocol/sourceRefs/confidence）+ 7 类证据类型（code/contract/config/data/runtime/document/human-assumption）+ 校验规则 |
| `diagram-output-formats.md` | 格式选择表（C4→Structurizr DSL、密集图→DOT、Markdown 原生→Mermaid、白板→Excalidraw、可编辑→Draw.io、发布→SVG、幻灯片→SVG+notes）+ 导出检查清单 |
| `structurizr-canvas-pipeline.md` | DSL 源形状（`<name>.structurizr.dsl` + `architecture-understanding.md` + `evidence.md`）+ 信任规则（DSL 是真相源，渲染是派生产物） |
| `diagram-delivery-recipes.md` | 交付/导出配方（原属独立 output-format skill） |
| `architecture-tooling-assessment.md` | 竞品插件模式对比（Data Analytics/Product Design 等的 router+scenario 模式）、13-skill 形状 MECE 论证、脚本策略、Canvas 决策、backlog 候选 |
| `business-application-fitness.md` | 业务应用（CRM/ERP/ecom/记账/LMS/CMS 等）建模与 agent 就绪度评估 |

**architecture-contract 核心规则摘录**（对 agentrt 最有迁移价值）：
- **文件交付规则**：图源文件（`.dot`/`.dsl`/`.mmd`/`.puml`）**必须写入磁盘为真实文件**，不得在聊天里内联；仅在用户显式要求时展示 ≤20 行摘要；
- **图表接地**：图表不得比文本更自信——文本说未知，图必须标 unknown 或从确认路径中省略；字段/表/枚举存在只确认数据形状，不确认业务动作（"分结构证据与行为证据"）；UI/表单只确认交互，不确认后端效果；factory/fixture 只确认样例形状，不确认生产行为；推断节点用虚线边 + `would create`/`needs validation` 标签；
- 稳定 ID：节点/边有稳定 ID 以便重新生成、diff、追溯。

### 2.4 证据模型（node/edge/sourceRefs/confidence）

`architecture-evidence-model.md` 定义的结构化模型是插件的事实层（示例 `examples/basic-architecture/architecture-model.json` 直接落地）：

```json
{
  "id": "service.order-api",
  "label": "Order API",
  "type": "service | module | database | queue | external-system | actor | capability | cloud-resource | decision | risk",
  "state": "current | target | deprecated | proposed | unknown",
  "owner": "team or person when known",
  "description": "short human-readable explanation",
  "sourceRefs": ["path/to/file.ts:10-80", "docs/adr-001.md"],
  "confidence": "high | medium | low | unknown"
}
```

校验规则：当前态节点至少一个 high/medium 证据源；目标态可无代码证据但必须标 target/proposed；推断关系必须低置信度 + 验证任务。示例自带 `run-smoke.mjs` 校验器（节点 ID 唯一、边端点存在、置信度枚举合法、sourceRefs 文件真实存在、viewer 能产出 SVG/workspace）。

### 2.5 Canvas viewer 三件套

三个 viewer 是"刻意收窄"的格式查看器（manifest 声明格式 + 内容探测规则）：

| viewer | 扩展名 | 内容探测 | dataKey |
|--------|--------|----------|---------|
| `dsl` | `.dsl` | `^\\s*workspace...` | `aicoding.formatViewer.dsl` |
| `dot` | `.dot`/`.gv` | — | `aicoding.formatViewer.dot` |
| `mermaid` | `.mmd`/`.mermaid` | `graph|flowchart|stateDiagram|sequenceDiagram|classDiagram|erDiagram|xychart` | `aicoding.formatViewer.mermaid` |

- `pathGlobs` 声明匹配文件（如 `**/*.structurizr.dsl`），`contentProbe` 探测内容防误判；
- `scripts/index.mjs` 是独立可执行 viewer（stdin 收 `QODER_CANVAS_SCRIPT_ARGS`，stdout 写 `QODER_CANVAS_DATA` JSON，含 `sourcePath`/`svg`/`workspace.views`），可被 smoke test 离线驱动；
- 设计决策：**不建第三个自定义架构 Canvas**，除非出现 C4/Graphviz 都表达不了的交互（多视图证据下钻、当前/目标 diff 回放、风险修复板、追溯覆盖热力图）——现阶段用 model JSON + Markdown 报告表达，Canvas 仅做文本图源的视觉检查。

### 2.6 质量门与示例冒烟

- **Root 脚本仅维护门**：`build:canvases`（同步 viewer）/ `validate:plugin`（校验包/skill 形状/引用/viewer 资源）/ `validate:examples`（轻量示例冒烟）/ `validate:all`；
- **示例**（`examples/basic-architecture/`）是"最小架构产物集"的模板：`architecture-model.json`（证据模型）+ `system-context.structurizr.dsl`（C4 源）+ `dependency-impact.dot`（关系图）+ `business-flow.mmd`（轻量流图）+ `architecture-understanding.md`（阅读指南/已知缺口）+ `run-smoke.mjs`（端到端冒烟，含 viewer 离线驱动）。

### 2.7 设计亮点提炼（10 条）

1. **场景优先、图型次之**的路由哲学（MECE 边界防职责漂移）；
2. **证据模型作为统一事实层**（node/edge/sourceRefs/confidence 贯穿所有 skill）；
3. **"图表不得比文本更自信"的接地规则**（防 AI 幻觉可视化）；
4. **分结构证据与行为证据**（字段/表确认形状，行为需动作路径证据）——对 agentrt 的"权威功能保证正确性"是直接借鉴；
5. **文件交付规则**（图源写盘、不内联）——输出纪律；
6. **共享契约层 + Mandatory Shared Gate**（契约先行，避免 13 个 skill 各自为政）；
7. **不捆绑提取器**（方法论与契约，不做确定性生成）；
8. **Canvas 收窄 + 文本图源为真相源 + 派生渲染**（SSoT 思想贯穿到图）；
9. **living architecture（architecture-health）**：用 git diff 判断图是否过期、建追溯索引、CI 化校验——架构产物与代码对齐的持续保障；
10. **Business Application Fitness**：对业务应用先问"模型能否安全解释业务以改变它"，再谈图——补上 agent 就绪度评估维度。

---

## 三、agentrt 生态现状对照

### 3.1 agentrt 现有生态架构（0.1.5）

agentrt 生态层为 `airymaxhub/agent-workload/ecosystem/` 管理仓（聚合五叶仓）：

| 叶仓 | 角色 | 关键产物 |
|------|------|----------|
| `manager` | 配置治理根 | 11 JSON Schema（~272 规则）、`skill/registry.yaml`（技能注册表：skill_id/name/version/source/enabled/unit_type/contract_path/permissions/dependencies/compatibility/resource_limits/rate_limit）、3 环境 overlay |
| `prompts` | 提示词库 | 14 模板 4 类（Cognition/Memory/Security/System）+ registry + tuner |
| `markets` | 分发层 | `package.yaml`（name/category/version/default_installed/install.script/shared_venv/components/capabilities/downgrade）+ install.sh 自包含安装器 + 包模板 + 示例 agent；`market_d` daemon 解析 |
| `skills` | 官方技能 | 5 个 Python `SkillPlugin`（code_review/text_summarization/security_audit/data_analysis/web_search）+ 5 个 C 插件（`manifest.yaml` + `libairy_skill_*.so`，plugin_d dlopen）；`definitions/*.md` 为契约 SSoT；`contrib/` 3 个规范阶段技能 |
| `agents` | 内置执行体 | 11 角色 agent（各含 `contract.json` + `prompts/system.md` + `AirymaxAgent` 子类）+ Rust coding agent + orchestration 框架 |

**Skill 契约**（`sdk-python/agentrt/plugin_types.py`）：`SkillPlugin` 继承 `BasePlugin`，实现 `get_definition()`（返回 `SkillDefinition`：name/version/category/tags/输入输出 JSON Schema）+ `execute(parameters)`。另有 `AgentPlugin`（on_cognition/on_planning/on_execution/on_reflection 生命周期钩子）、`ToolPlugin`、`HookPlugin`。

**plugin_d**（插件管理 daemon）：`${AIRY_HOME}/ecosystem/plugins` 目录扫描 + `manifest.yaml` 解析 → 权限校验（16 项权限 → Cupolas 守卫映射，strict_mode 默认开启 fail-closed）→ dlopen 加载 → 状态机（UNLOADED→LOADED→INITIALIZED→RUNNING→ERROR/DISABLED）；13 个 JSON-RPC 方法（load/unload/start/stop/execute/get_metadata/get_state/get_stats/list/install/uninstall/health_check/shutdown）。

**hook_d**（Hook 事件注入 daemon）：**agent 内部生命周期 hooks**（8 类型：pre_exec/post_exec/pre_llm/post_llm/pre_tool/post_tool/on_error/on_memory_evolve；4 实现：shell/python/webhook/callback；决策：continue/skip/retry/abort/modify）；核心在 `atoms/coreloopthree/src/hook/`（registry/service/executor/interceptor/timeout/audit/metrics/trace handlers + 12 内置 handler）。

### 3.2 对照差距分析

| 维度 | agentrt 现状 | architecture-visualization / Qoder 生态 | 差距 |
|------|-------------|----------------------------------------|------|
| 技能形态 | **执行型**（输入/输出 JSON Schema，deterministic） | **场景型/方法论型**（prompt 驱动、意图路由、证据建模） | agentrt 缺场景型技能层 |
| 技能组织 | 平铺 5 技能 + registry | 三层 MECE（路由→场景→基础） | 缺路由器 + 场景边界 |
| 共享契约 | definitions/*.md 单技能契约 | 全局共享契约层（contract/evidence-model/formats） | 缺跨技能共享契约 |
| 证据模型 | 无（skills 输出 JSON 结果） | node/edge/sourceRefs/confidence 统一事实层 | 缺结构化证据模型 |
| 上下文注入 | 无（system prompt 由 prompts/ 管理） | SessionStart hook 注入 skill 引导全文 | 缺会话级注入通道 |
| Hooks | agent 内部生命周期（pre/post_tool） | **会话/IDE 级**（SessionStart/PostToolUse/Stop）+ 三态退出码 | 缺会话级 hooks |
| 校验 | plugin_d 运行期 manifest 校验 | **装前离线 validator + 装后 smoke** | 缺离线校验 |
| 清单 | package.yaml 单一清单 | 发布/运行时双 manifest | 缺运行时清单分离 |
| 规则库 | 无 | 三形态管线（规则→索引→编译全量） | 缺 rules 形态 |
| 交付纪律 | CLI/TUI 成熟 | 图源写盘不内联 + 派生渲染 SSoT | 缺产物交付规则层 |
| 评估 | GRAD/决策链（运行评估） | better-harness 七态证据 + ceiling 表（工程成熟度评估） | 缺工程化评估模型 |
| 幂等/重放 | 事件流单真相源 | qmind 幂等表（哪步可重试） | 可借鉴建模为 SKILL 内契约 |
| 双通道 | plugin_d（执行）+ hook_d（生命周期） | hooks（确定性）+ skills（agentic）双通道配合 | 部分对齐，缺会话级 hooks 作 skill 触发信号 |

---

## 四、agentrt 可借鉴点清单（P0 / P1 / P2）

结合 agentrt daemon 架构（gateway JSON-RPC 总线 + 多 daemon + atoms 微核心）与 K8s 类比定位，按优先级给出：

### P0 — 立即可借鉴（低成本高价值，契合 0.1.5 收尾期）

1. **Skill 场景路由层**（skill 两层化）：在 `SkillPlugin` 之上抽象"场景型 skill"（`ScenarioSkill`：`get_description()` 承担语义触发路由 + `get_shared_gates()` 声明契约依赖 + `get_scene_boundary()` 声明 NOT-in-scope），router skill 依据用户意图选最小场景集。把 architecture-visualization 的 `explore` 路由表作为首个实现范例。
2. **共享契约层**：为 skills 增加 `contracts/` 目录（跨技能共享的 Markdown/JSON 契约，如 evidence-model），`definitions/*.md` 之外的全局契约；skill 加载时声明依赖的契约清单（Mandatory Shared Gate）。
3. **文件交付规则标准化**：图源/产物写盘不内联的规则写入 skill 契约模板；agentrt CLI/TUI 侧提供"产物落盘路径约定"（`$AIRY_HOME` 之外的项目相对路径）。
4. **离线 validator**：移植 `validate_qoder_plugin.py` 检查项为 agentrt 的 `market_d` 装前校验（package.yaml 合法性、组件路径存在性、SKILL frontmatter 必填、manifest 与目录名一致），装前失败即拒绝安装。

### P1 — 中期借鉴（与 0.1.6+ 演进对齐）

5. **发布/运行时清单分离**：markets 的 `package.yaml` 拆分——发布清单（市场元数据）与运行时清单（`manifest.yaml`，声明 skills/hooks/mcpServers/rules，被 plugin_d/market_d 消费），运行时 daemon 只信任运行时清单。
6. **会话级 hooks + 上下文注入**：在 hook_d 增加会话级事件（`session_start`/`post_tool`/`session_stop`，与既有 pre/post_tool 区分）；hook 输出 JSON 注入上下文（`additional_context`），用注入取代改 system prompt；hook 退出码三态语义对齐（0/2/other）。
7. **MCP server 一等公民**：manifest 声明 `mcpServers`（STDIO/SSE/HTTP），launcher 复用宿主共享运行时定位可执行体 + `env_vars` 白名单；为将来"外部工具/桌面控制"能力铺路。
8. **规则库三形态管线**：为 skills 增加 `rules/` 形态（单规则文件模板 + `_sections.md` 前缀归类 + 编译聚合 SKILL/全量文档），首用 `manager` 的安全/配置规则库试点。
9. **CLI 机器契约收敛**：把 better-harness 的 `--json/--no-color/--quiet/--no-input/--dry-run/--yes` 与命令三档分类固化为 agentrt CLI 全量规范（CLI 与 TUI 共用）。

### P2 — 战略借鉴（长期演进）

10. **评估模型文档化**：参考 better-harness 的 5 维度 × 15 check + 七态证据 + ceiling 表，把 GRAD 决策链与"工程成熟度"评估固化为可被 LLM 消费的契约文档，干预账本跨会话。
11. **证据-评分脱钩**：评估时证据状态约束分数天花板而非公式；"配置≠行为"。
12. **幂等/重放安全表**：为所有"消费 token/不可重放"的外部操作（如 maths_d 符号后端、支付类工具）建立幂等契约表，随 SKILL 分发。
13. **自举下载 + 版本钉扎 + 防递归**：skill 依赖的外部 CLI 二进制统一走 launcher（版本钉扎 env、子进程防递归标记、fail-closed 验签——复用 0.1.5 发布链路的 cosign 门禁）。
14. **自包含分发**：markets 包 zip 化 + 签名校验 + 根校验（zip 根直接含运行时清单），与 0.1.5 发布链 SSoT 对齐。

---

## 五、architecture-visualization 重构为 agentrt 自带插件的可行性

### 5.1 可行性结论

**结论：可行，且是 v4.4 轮次内最高性价比的重构候选。** 理由：

1. **契约契合**：插件"方法论与契约、不做确定性提取"的取舍与 agentrt「机制不是策略」同构；其证据模型与 agentrt 的"权威功能保证正确性"、"事件流单一真相源"思想同源；
2. **形态契合**：agentrt 的 11 角色 agent + LLM 驱动管线天然擅长"检查项目后写出证据背书产物"，这正是插件的默认工作流假设；
3. **可剥离**：插件本身不依赖 Qoder 专属 API（`QODER_CANVAS_SCRIPT_ARGS` 仅用于 viewer 离线驱动），契约层/场景层/证据模型可 100% 迁移；
4. **差异化**：agentrt 作为"Agent 编排的 K8s"，内置"架构可视化"能力既是 dogfooding 也是生态样板——展示第三方如何用场景型 skill + 契约层 + 渲染服务构建方法论插件。

**需适配的 Qoder 专属部分**（不可直接迁移）：
- `canvases/*` 依赖 Qoder 的 `aicoding.formatViewer.*` dataKey 协议与 Canvas 宿主；
- `interface` 市场 UI 元数据（agentrt 市场无 UI 面）；
- 三个 viewer 的 `scripts/index.mjs` 为打包产物（单文件 >1MB），可保留契约但需适配 agentrt 的渲染出口（CLI/TUI/HTTP）。

### 5.2 重构方案（三层落地）

建议以 `markets` 包形式落地：**`ecosystem/markets/tools/architecture-visualizer/`**（category: `skill`），与 maths-toolkit 并列，经 market_d 安装；核心为三层：

```
architecture-visualizer/
├── package.yaml                  # 包元数据（SSoT，含 capabilities: [architecture-visualizer]）
├── install.sh                    # 安装器（可选：graphviz/dot 渲染依赖探测，缺失降级）
├── contracts/                    # ★ 契约层（迁移自 references/，agentrt 化）
│   ├── architecture-contract.md
│   ├── evidence-model.json       # 结构化证据模型（JSON Schema，可机器校验）
│   └── diagram-output-formats.md
├── skills/                       # ★ 场景技能层（13 个，转译为 agentrt skill 格式）
│   ├── architecture-explore/SKILL.md        # 路由层
│   ├── system-modeler/ ...                 # 场景层（9 个）
│   └── c4model/ graphviz/ drawio/          # 基础层（3 个）
├── examples/basic-architecture/            # 示例 + run-smoke（照搬，改 npm→ctest/python）
└── render/                        # ★ 渲染服务层（agentrt 化出口，替代 Qoder Canvas）
    ├── dot_renderer    # 调用系统 graphviz 生成 SVG（缺失降级为 ASCII/TUI 预览）
    ├── dsl_parser      # 轻量 structurizr DSL 校验（workspace 存在性/视图数）
    └── mermaid_checker # mmd 语法校验（节点 ID/边端点/形状定界符）
```

**三个关键适配点**：

**(a) 场景 skill 转译为 agentrt skill 格式**：保留 `name` + `description`（"Use when..." 语义触发），补 `get_definition()` 的输入/输出 Schema（输入：`scope`/`audience`/`evidence`；输出：产物清单），`execute()` 内实现路由 + 契约门 + 产物落盘（遵守文件交付规则）；或采用 5.3 中的轻量方案。

**(b) 证据模型 SSoT 化**：`architecture-contract.md` 规定"当前态节点至少一个 high/medium 证据源"，转译为 `evidence-model.json` Schema + 校验器（迁移 run-smoke 的 `validateModel()`），并把"图不得比文本更自信"固化为产物校验规则（输出 JSON 中 node/edge 的 confidence 与 sourceRefs 完整性硬校验）。

**(c) viewer → agentrt 渲染出口**：
- CLI 场景：`airy_cli` 增加 `arch-viz render <file>` 命令，调 `render/` 服务（graphviz 存在 → SVG；缺失 → 结构树/ASCII 预览）；
- TUI 场景：事件流/看板之外增加"架构视图"面板（复用 `render/` 的解析结果渲染节点表）；
- 首选方案是**文本图源为真相源**（与插件一致），渲染均为派生产物。

### 5.3 落地建议（分阶段）

| 阶段 | 内容 | 验证 |
|------|------|------|
| **M1（契约层）** | 迁移 `contracts/` 4 文件 + 证据模型 JSON Schema + 校验器 | 示例模型通过校验；183 ctest 回归 |
| **M2（场景层）** | 13 个 SKILL.md 转译为 agentrt skill 格式（frontmatter + 契约门 + 产物规则），先落地 `architecture-explore` 路由 + `system-modeler` + `graphviz` 三个 | 端到端：对 agentrt 自身仓库跑一次 system-modeler，产出架构模型 + C4 源 + 关系图 |
| **M3（渲染层）** | `render/` 三服务 + CLI 命令 + TUI 面板 | 对 M2 产物渲染 SVG/预览；无 graphviz 环境降级路径验证 |
| **M4（发布）** | `package.yaml` + install.sh + 市场注册 + 签名打包 | market_d 安装/卸载/启用验证；与 0.1.5 发布链路 SSoT 对齐 |

### 5.4 风险与边界

| 风险 | 缓解 |
|------|------|
| 13 个 skill 全量转译工作量大 | M2 先落地 3 个核心（explore/system-modeler/graphviz），其余按需增量（与插件同哲学：不捆绑，路由到最小集） |
| DSL/DOT 渲染依赖外部工具 | render/ 缺依赖降级为文本/ASCII 预览，install.sh 探测并提示（对齐 maths_d 的降级策略） |
| "图表不得比文本更自信"的规则约束力 | 证据模型校验器硬校验 + 示例回归，把软规则转为硬门 |
| 场景 skill 与既有执行型 skill 边界 | 场景型 = 方法论（产出证据背书产物），执行型 = 确定性（输入输出 JSON）；registry.yaml 用 `unit_type: scenario` 区分 |
| 过度建模风险（用户只想要一张图） | explore 路由强制"最小场景集"+"一视图一问题"，与插件一致防过度 |

---

## 六、结论

1. **Qoder 插件生态是当前编码智能体插件规范中可机器校验程度最高的范本**：双 manifest、组件声明即校验、会话级 hooks、MCP 一等公民、规则三形态管线、CLI 机器契约、证据-评分脱钩——7 大机制对 agentrt 生态层有直接迁移价值。
2. **architecture-visualization 是"方法论型插件"的标杆**：其"场景优先路由 + 共享契约 + 结构化证据模型 + 图源写盘 + living architecture"五件套，与 agentrt「权威功能保证正确性」「SSoT 单一真相源」的工程哲学高度同构。
3. **agentrt 现状差距集中在"场景型技能层"与"会话级 hooks/上下文注入"**：现有 `ecosystem/skills` 是执行型技能，缺方法论层；`hook_d` 是 agent 内部生命周期 hooks，缺会话级注入通道。
4. **重构可行**：以 `markets/tools/architecture-visualizer` 包形式落地，M1 契约层 → M2 场景层 → M3 渲染层 → M4 发布四阶段推进；M2 先落地 `architecture-explore` / `system-modeler` / `graphviz` 三核心，并以"对 agentrt 自身仓库做一次架构建模"作为端到端验收。

---

## 附：证据来源索引

- Qoder 插件生态根目录：`/works-engineering/.engineer-reference/user-reference/plugins/`（`installed_plugins.json` / `installed_plugins_v2.json`）
- architecture-visualization 插件：`.../plugins/cache/qoder-marketplace/architecture-visualization/0.1.0/`（README.md / .qoder-plugin/plugin.json / skills/（13 SKILL.md + references/）/ canvases/{dsl,dot,mermaid}/ / examples/basic-architecture/（含 run-smoke.mjs）/ THIRD_PARTY_NOTICES.txt）
- 插件规范一手权威：`.../qoder-bundler/qoder-create-plugin/skills/create-plugin/`（SKILL.md + references/qoder-plugin-manifest.md + qoder-components.md + validation-and-packaging.md + scripts/validate_qoder_plugin.py）
- hooks 实例：`.../qoder-bundler/security-scan/.qoder-plugin/qoder-hooks.json`、`.../qoder-marketplace/superpowers/5.1.0/hooks/`（hooks.json / run-hook.cmd / session-start）
- 规则库范式：`.../qoder-marketplace/redis/1.0.0/redis-development/`（SKILL.md / AGENTS.md / rules/_template.md / _sections.md / _contributing.md）
- 工作流/评估范式：`.../qoder-bundler/security-scan/skills/security-scan/SKILL.md`、`.../qoder-marketplace/qmind-knowledge-cn/0.2.0/skills/qmind-knowledge/SKILL.md`、`.../qoder-bundler/better-harness/`（models/*.md / docs/ARCHITECTURE.md）
- agentrt 生态对照：`airymaxhub/agent-workload/ecosystem/`（skills/README.md + definitions/ + plugins/README.md、markets/README.md + package.yaml、manager/skill/registry.yaml）、`agentrt/daemons/plugin_d/README.md`、`agentrt/daemons/hook_d/README.md`、`sdk/sdk-python/agentrt/plugin_types.py`
- 历史评审对照：`docs-closed/agentrt/00-reviews/_review_v4.3/vendor-engineering-synthesis-20260814.md`
