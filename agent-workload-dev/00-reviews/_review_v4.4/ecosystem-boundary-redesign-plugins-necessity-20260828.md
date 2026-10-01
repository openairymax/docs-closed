# agentrt ecosystem 五叶仓边界深度重设计与 plugins 模块必要性分析报告

> **报告编号**：REVIEW-AGENTRT-2026-08-28-ECOSYS
> **报告类型**：架构边界重设计研究（生态层模块边界深度重整理 + 插件模块必要性论证 + 可借鉴点复核）
> **研究对象**：Qoder 插件生态（`plugins`，8 款插件）+ DeepSeek Harness（`deepseek-harness-master`，基于 Cordis 的插件框架 agent harness）+ agentrt `ecosystem` 五叶仓实测（agents / manager / markets / prompts / skills）
> **产出目录**：`docs-closed/agentrt/00-reviews/_review_v4.4/`
> **审查日期**：2026-08-28
> **审查人**：SPHARX 工程标准组
> **状态**：研究性报告（供架构演进决策参考）
> **配套文档**：`qoder-plugin-ecosystem-architecture-visualization-20260828.md`（上一份 Qoder 生态研究）

---

## 摘要

针对"agentrt 是否需要在 ecosystem 单独创建 plugins 模块并与五叶仓同级"这一核心问题，本报告基于两个参考项目的深度研究（Qoder 插件生态 + DeepSeek Harness 插件框架）与 ecosystem 五叶仓的真实文件实测，给出结论：

**不新建第 6 个"plugins"叶仓**。理由是：

1. agentrt 的"插件"并非单一概念，而是 5 种异质机制（C dlopen 插件 / Python SkillPlugin / Agent 执行体 / market 工具包 / Hook），它们分属不同生命周期与不同运行时，强行合并进一个叶仓会制造新的 SSoT 冲突；
2. 当前真实病灶不是"缺一个模块"，而是**插件契约分散在 skills（定义）/ manager（无 schema）/ plugin_d（运行）/ markets（分发）四处、同一概念三份权威、零自动化对齐**（实测发现 9 类边界问题，详见第四章）；
3. DeepSeek Harness 的"everything is a plugin"提供的是**统一插件契约与运行时模型**（service seam 三元角色 + inject 依赖 + fiber 生命周期 + disposer 纪律），而非"多一个目录"——借鉴其设计而非其组织。

正确动作是**做一次五叶仓 + 运行时的"统一插件契约"重构**：新增一个跨叶仓的 `plugin-manifest` v2 契约（覆盖 skill/agent/tool/hook/mcp 五类组件）、把场景型技能（scenario skill，Qoder architecture-visualization 属于此类）确立为 skills 的新技能形态、补 plugin manifest schema + 离线 validator + 生成式目录门控。架构轴从"五个并列内容仓"重构为「治理（manager）→ 定义（skills/agents/prompts）→ 内容（scenario/prompt）→ 分发（markets）→ 运行（plugin_d/market_d/agent_d/hook_d）」五轴分层。

对上一份报告 14 条可借鉴点逐一复核：**13 条确认真实可借鉴（经 dsh 交叉印证），1 条降级**（MCP 一等公民——agentrt 网关为自研 JSON-RPC，MCP 适配应作为协议桥而非一等组件）；dsh 新发现 **10 条高价值借鉴点**（capability seam 三元角色、disposer 纪律、inject 依赖排序、五态事件分发、模型可见⟺已记录、scope 隔离、生成式目录门控等）。

---

## 一、研究背景与方法

| 输入 | 来源 | 方法 |
|------|------|------|
| Qoder 插件生态 | `.engineer-reference/user-reference/plugins/`（8 款插件） | 逐文件精读 architecture-visualization（13 SKILL + 契约层 + viewer + 示例）；子代理并行深读其余 7 款 |
| DeepSeek Harness | `.engineer-reference/user-reference/deepseek-harness-master/` | 子代理深度研究 Cordis 框架源码（vendor/cordis/src/*.ts）+ docs（architecture/capability-seams/agent-lifecycle/event-producer-consumer/persistence-catalog/tool-catalog/cordis-primer）+ 示例（acp-agent 等） |
| agentrt ecosystem | `airymaxhub/agent-workload/ecosystem/` 五叶仓 + `agentrt/daemons/` | 子代理逐文件实测五叶仓边界与 18 daemon 消费映射；交叉验证 install.sh / plugin_d / market_d / agent_d / tool_d 源码 |

---

## 二、参考项目深度研究（针对"插件模块"问题的聚焦提炼）

### 2.1 DeepSeek Harness（dsh）：插件框架的运行时模型

**核心信条：everything is a plugin**——模型适配器、工具注册表、会话日志、agent 主循环本身都是插件，每个产品部件都可配置替换。它构建在 vendored 的 **Cordis** 插件框架之上，其插件模型是 agentrt 最值得对照的运行时设计：

| Cordis 概念 | 机制 | 对 agentrt 的启示 |
|-------------|------|-------------------|
| **Context** | 依赖容器（Proxy），`ctx.tools`/`ctx.llm` 等键即服务定位符 | 插件间通过服务键互操作，不 import 具体实现 |
| **Service** | `class X extends Service`，构造即注册，卸载即注销；`init/check/invoke/extend/config` 静态钩子 | 每类能力一个注册表服务 |
| **Fiber** | 插件生命周期单元，状态机 `PENDING→LOADING→ACTIVE→FAILED/UNLOADING→DISPOSED` | 显式状态机 + `internal/status` 状态迁移事件 |
| **inject** | 插件声明依赖服务，`_refresh()` 等到全部依赖就绪才激活；**加载顺序由依赖图决定而非手工排序** | 消灭 daemon 启动顺序魔法 |
| **effect（注册即效应）** | `ctx.effect()` 立即执行并收集 disposer；`ctx.on()/provide()/mixin()` 全是 effect 包装；**卸载逆序撤销注册** | 根治"插件卸载残留" |
| **Events 五分发模式** | `emit`（观察）/ `waterfall`（洋葱中间件，可短路）/ `parallel` / `serial` / `bail`（顺序表决） | hook_d 的策略/拦截点全部可表达 |
| **Registry** | 插件三种形态（函数/类/对象）+ 元数据 `name/Config/inject/provide/intercept` | 插件元数据模型 |
| **Loader** | `cordis.yml` 插件行列表 + patch 分层叠放 + 事务性配置重载（先导入新名再处置旧实现、失败回滚） | 配置驱动 + 失败即大声 |
| **Scope** | `extend`（继承）/ `isolate`（服务隔离）/ `agent.ctx`（per-agent 作用域，销毁即撤销） | 子 agent 局部世界装配 + 失败整体回滚 |

**Capability Seam（能力缝隙）**——dsh 最重要的组织模式：一个可替换能力 = 三角色齐全——**Service Definition**（声明接口的包）+ **Service Provider**（实现包，可整族替换）+ **Consumer**（消费包，只依赖 Definition 绝不依赖具体 Provider）。例：`ctx.shell` 的 provider 有 bash-local/bash-sandbox/pwsh-local，`tool-bash` 只依赖 seam 接口；filesystem 与 subprocess 共享一个执行世界，整体迁移到远程沙箱（E2B）时 Consumer 零改动。完整性守卫由 `scripts/gen-doc-graphs.ts` 从 Cordis 声明自动发现并带 completeness guard。

**"模型可见 ⟺ 已记录"**（architecture.md:96, AGENTS.md:107）：任何到达模型请求的内容必须能从 session 日志重建；新的模型可见输入 = 需要新 session 事件。这恰与 agentrt「事件流单一真相源」「权威功能保证正确性」同源。

**Skill 在 dsh 中的形态**：`ctx.skills` 是一个 seam（注册表服务），skill-filesystem 等是 provider，模型通过 `skill` 工具消费——**SKILL.md 是 provider 提供的内容，不是独立插件类型**。这是判断"场景型技能放哪"的关键依据。

**生成式目录门控**：`tool-catalog.md` / `persistence-catalog.md` 由脚本 **boot 每个插件到真实 context 读 schema** 生成（工具 schema 不是静态可知的），带 completeness guard + freshness 门控，"新工具不能悄悄未文档化"。这是解决 agentrt 双注册表漂移的现成范式。

### 2.2 Qoder 插件生态：声明式组件模型

Qoder 是"宿主 + 声明式组件"模型（与 dsh 的"运行时 + 编程式插件"相对）：插件 = 宿主消费的资源描述。上一份报告已详述，此处仅聚焦与"插件模块"决策相关的四点：

1. **双 manifest**：发布清单（根 `plugin.json`，市场元数据）与运行时清单（`.qoder-plugin/plugin.json`，声明 skills/hooks/mcpServers/rules/agents/commands）分离，运行时只信任运行时清单；
2. **组件声明即校验**：路径 `./` 相对、不得 `..`、必须真实存在；`validate_qoder_plugin.py` 离线校验（清单合法/必填/路径越界/SKILL frontmatter/禁止目录）；
3. **插件 = 组件 bundle**：一个插件目录可含多类组件（skills + hooks + mcpServers + rules），组件间无编程耦合（区别于 dsh 的服务注入）；
4. **场景型插件**（architecture-visualization）：SKILL.md + references 契约 + examples + viewer——**内容是"方法论 + 契约"，不是可执行代码**，这类插件在 agentrt 生态中没有对应物（详见第七章）。

### 2.3 两个模型对 agentrt 的本质启示

| 维度 | Qoder | dsh | agentrt 落点 |
|------|-------|-----|-------------|
| 插件本质 | 声明式组件 bundle | 编程式服务插件 | 两者都需要：**声明式清单（分发/校验）+ 编程式契约（运行）** |
| 组件耦合 | 零编程耦合 | 服务注入 + 事件 | 声明式组件走 manifest；能力走 service seam |
| 生命周期 | 宿主挂载/卸载 | Fiber 状态机 + effect 可逆 | 插件 = manifest + 生命周期契约 |
| 触发 | 宿主 hooks | 类型化事件五分发 | 会话级 hooks（补）+ agent 内部 hooks（已有） |

**结论：agentrt 应吸收 dsh 的"统一契约/运行时模型"，吸收 Qoder 的"声明式组件清单/离线校验"，而不是照搬任何一方的目录组织。**

---

## 三、ecosystem 五叶仓现状实测

### 3.1 五叶仓当前定位（README 声明）

| 叶仓 | 定位 | 关键产物 |
|------|------|----------|
| `manager` | 统一配置与生命周期管理（SSoT） | 11 JSON Schema、`skill/registry.yaml`（10 技能）、`agent/registry.yaml`、`configs/agentrt.yaml`、`model/model.yaml`、三层环境 overlay、sanitizer/security/audit |
| `prompts` | 提示词模板库 + 评测/调优框架 | `registry.yaml`（14 模板）、`templates/`（cognition/memory/security/system）、`tuner/`（scorer/evaluate/ab_test） |
| `markets` | 官方包市场（分发层） | `package.yaml`（maths-toolkit）、`client/`、`agents/`（安装器+契约）、`templates/`、`examples/` |
| `skills` | 官方技能定义与实现 | `definitions/*.md`（契约 SSoT）、`src/*.py`（SkillPlugin）、`plugins/`（C 插件 manifest+so）、`contrib/` |
| `agents` | 内置 Agent 执行体 + 编排框架 | 11 角色（contract.json + system.md + agent.py）、Rust coding agent、`orchestration/`、`registry/agents.yaml` |

### 3.2 daemon 消费映射（18 daemon）

| daemon | 消费叶仓 | 方式 |
|--------|----------|------|
| `plugin_d` | skills/plugins/* | 扫描 `${AIRY_HOME}/ecosystem/plugins`，解析 manifest.yaml（**仅简单 key-value 解析，无 schema 校验**）→ dlopen |
| `market_d` | markets/ | 内存注册表（skill_registry/agent_registry），靠 RPC 写入，**不直接读 package.yaml** |
| `agent_d` | agents/ | spawn 子进程执行体（python/Rust） |
| `tool_d` | manager/service/tool_d/tool.yaml | YAML 解析工具清单 |
| `llm_d` | manager/model/model.yaml | provider/model 解析 |
| `gateway_d` | manager/configs/agentrt.yaml | --manager 参数；MCP prompts/list 仅协议路由 |
| `maths_d` | markets/tools/maths-toolkit | stdio JSON-RPC 调 Python 后端 |
| `hook_d` | 不消费 ecosystem（hooks 已迁 sdk-python） | atoms/coreloopthree 薄壳 |
| `prompt_d` | **不存在** | — |

### 3.3 实测发现的 9 类边界问题（SSoT 冲突/重叠/缺口）

**E-1 技能注册表三处并存、命名体系互不相认（最严重）**：
- `skills` 叶仓：5 官方技能（code_review/text_summarization/security_audit/data_analysis/web_search）+ 3 contrib；
- `manager/skill/registry.yaml`：10 个完全不同命名的"内置技能"（filesystem_skill/shell_skill/http_skill/python_skill/...），其 `contract_path`（如 `ecosystem/skills/contrib/filesystem/contract.json`）在 skills 仓中**全部悬空**（contrib 只有 browser/database/github 三个 README，无 contract.json，不存在 filesystem/shell/http 目录）；
- `market_d` 运行时内存注册表：第三份。
→ 同一"技能"概念三个权威、两套命名、零自动化对齐。

**E-2 Agent 注册表两处计数/字段不一致**：`agents/registry/agents.yaml`（14 条：12 enabled + 2 planned，自称"运行时单一可信源"）vs `manager/agent/registry.yaml`（_metadata 13 total/11 implemented/2 planned，README 又说 12）→ 无机制保证同步。

**E-3 prompts 运行时消费断裂**：`prompts/README.md:114` 声称"runtime reads registry.yaml；serves /v1/prompt/execute"，但 18 daemon 无 prompt_d，gateway 仅 MCP 协议层 `prompts/list` 路由（未关联 registry.yaml），sdk-python 无 prompt 模块 → "prompt 工程 → 运行时渲染"链路断裂。

**E-4 插件功能三方共管、manifest 无 schema**：skills/plugins（定义侧）+ plugin_d（运行侧，`plugin_discovery.c:47` 注释原文"Only parses the simple key-value pairs"）+ markets（分发侧）；manager/schema 11 个 schema 中**无 plugin-manifest.schema.json**；C 插件无契约测试（test_skills.py 只测 Python 侧）。

**E-5 skills 仓内两种契约方言并存**：官方技能遵循 SDK `SkillPlugin`（get_definition/execute），contrib 定义另一套 `Skill` 接口（initialize/execute(action,params)/cleanup）+ 另一套 contract.json 字段 → contrib 即便实现也无法直接并入官方体系。

**E-6 markets/agents 双 Schema 跨仓耦合无自动化**：分发元数据（markets/agents/contracts/schema.json）与运行时能力契约（agents/shared/contracts/agent.schema.json）"安装校验时两者并用"，靠安装器调用次序保证，跨仓变更无 CI 联动。

**E-7 manager 悬空引用**：README 提到 `tools/scripts/ops/templates` 目录不存在；README 自称 v0.1.1 而 configs/agentrt.yaml 为 v0.1.5（版本滞后）。

**E-8 跨仓人工同步点（易碎）**：`agents/airymax_agents/base.py` BUILTIN_TOOL_SCHEMAS 与 tool_d 注册参数靠人工同步；`skills/src/code_review.py:17-19` 硬编码 `parents[3]/sdk/sdk-python` sys.path（依赖工作区布局）；`examples/run_pm.py` 同样硬编码。

**E-9 分支/版本表述漂移**：`.gitmodules`（develop/hubs-01 ×4、agents=main）与各叶仓 README 徽章（feature/official-hubs-01）不一致。

---

## 四、核心问题：agentrt 需要 plugins 模块吗？

### 4.1 "插件"概念在 agentrt 的 5 种现形态

| 形态 | 契约 | 生命周期 | 运行时 | 归属 |
|------|------|----------|--------|------|
| C dlopen 插件 | manifest.yaml（无 schema） | UNLOADED→...→RUNNING | plugin_d | skills/plugins |
| Python SkillPlugin | get_definition/execute | SDK 加载 | sdk-python + plugin_d | skills/src |
| Agent 执行体 | contract.json + system.md | spawn 子进程 | agent_d | agents/ |
| market 工具包 | package.yaml | 安装/注册 | market_d + install.sh | markets/tools |
| Hook | 8 类型/4 实现 | 注册→触发 | hook_d / atoms | sdk-python hooks |

这 5 种形态**生命周期、执行模型、契约方言均不同**——它们不是"同一个插件的 5 种包装"，而是 5 种独立的扩展机制。把它们塞进一个 `plugins/` 叶仓只会产生一个"什么都装的大杂烩目录"，无法统一运行时。

### 4.2 三个候选方案

**方案 A：新建 plugins 叶仓（用户提问的方案）**
- 形态：`ecosystem/plugins/` 与五叶仓同级，容纳插件 manifest schema、validator、插件包模板、场景型插件内容。
- 优点：直观呼应 Qoder/dsh 的"插件"概念；为架构可视化这类场景型插件提供家。
- 缺点：与 skills（定义）/markets（分发）/manager（schema）/plugin_d（运行）大面积职责重叠；新叶仓会复制 manager/schema 与 markets/templates 的既有职能；"插件"边界无法画清（skill 算不算插件？market 包算不算？）；**制造第 4 份技能权威**，加剧 E-1。

**方案 B：维持五叶仓 + 各补各的（现状微调）**
- 优点：改动小。
- 缺点：E-1~E-9 一个都不解决；场景型技能仍无家可归；"插件"概念仍分散。

**方案 C：不新建叶仓，做"统一插件契约"重构（本报告推荐）**
- 形态：在**治理轴（manager/schema）**新增 `plugin-manifest` v2 Schema（统一覆盖 skill/agent/tool/hook/mcp 五类组件声明）；在 **skills** 确立"场景型技能"新形态（Qoder SKILL.md 方法论插件归此）；在 **markets** 统一分发契约；**plugin_d 升级为统一加载器**（C dlopen + Python SkillPlugin + scenario 内容 + manifest v2）；新增离线 validator（移植 validate_qoder_plugin.py）+ 生成式目录门控（移植 dsh tool-catalog 范式）。
- 优点：解决 E-1~E-9 的根因（契约统一）；吸收两个参考项目的精华组织；不制造新权威；契合 agentrt「SSoT 单一真相源」铁律。

### 4.3 结论

**不新建 plugins 叶仓。** 核心判据：
1. dsh 证明"插件化"的实质是**统一契约 + 统一运行时模型**，不是目录结构；agentrt 的 plugin_d 已经是统一运行时的雏形，缺的是契约层；
2. Qoder 的 plugins 是"宿主 + 组件清单"模型，其宿主是 IDE；agentrt 的宿主是 daemon 群 + 五叶仓，组件清单应落在 manager/schema（治理轴）；
3. 若一定要给"场景型方法论插件"一个物理家，它属于 **skills（定义）+ markets（分发）** 的既有职责带，不需要第 6 个叶仓。

---

## 五、ecosystem 五叶仓深度重设计

### 5.1 架构轴重构：从"五个并列内容仓"到"五轴分层"

```
┌─────────────────────────────────────────────────────────────┐
│ 治理轴 manager      （管"是什么、谁能用"）                    │
│   11 schema → 12+（新增 plugin-manifest.v2）                │
│   skill/agent 注册表 → 收敛为单一权威 + 生成式目录门控        │
├─────────────────────────────────────────────────────────────┤
│ 定义轴 skills/agents （管"能力定义与实现"）                   │
│   skills: 执行型技能（SkillPlugin 双实现）+ 场景型技能(新增)  │
│   agents: 角色执行体 + orchestration + Rust                  │
│   prompts: 提示词模板（含 registry + tuner）                 │
├─────────────────────────────────────────────────────────────┤
│ 分发轴 markets       （管"如何打包、安装、卸载"）             │
│   工具包/技能包/Agent 包 + 统一分发契约 + 离线 validator      │
├─────────────────────────────────────────────────────────────┤
│ 运行轴 daemons       （管"如何加载、执行、回收"）             │
│   plugin_d（统一加载器）/ market_d / agent_d / hook_d /      │
│   tool_d / llm_d / prompt_d(新增或由 gateway 承接)           │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 五叶仓重构后的职责边界（重新定义）

| 叶仓 | 管什么（重构后） | 不管什么（边界） |
|------|-----------------|------------------|
| **manager** | 全部配置/契约 Schema（**新增 plugin-manifest.v2、scenario-skill**）；**单一权威注册表**（skill/agent 合并为 capability registry，附生成式门控）；sanitizer/security/audit/deployment 治理 | 不产实现本体；不直接加载运行时 |
| **skills** | 技能**定义（definitions）+ 执行实现（src/plugins）+ 场景型技能（scenarios/，新增，SKILL.md 方法论插件）+ 共享契约（contracts/，新增）**；**统一契约方言**（废弃 contrib 的异种接口，收敛到 SkillPlugin） | 不分发（交给 markets）；不注册（交给 manager） |
| **agents** | 角色执行体 + orchestration + Rust + **contract 单一权威**（移除与 manager 注册表的双份） | 不做运行时调度（既有约束保持）；不做分发 |
| **prompts** | 提示词模板 + registry + tuner；**明确"供运行时渲染"契约**（与 gateway/prompt 服务对齐，见 5.5） | 不持有技能/agent 内容 |
| **markets** | 分发契约 + 安装器 + 模板 + 示例；**统一为唯一分发入口**（tool/skill/agent/scenario 包） | 不持有实现本体；不定义能力契约（权威在 skills/agents） |

### 5.3 统一 plugin-manifest v2 Schema（新增，覆盖五类组件）

参照 Qoder 组件模型 + dsh 插件元数据 + agentrt 现状，设计统一清单（JSON Schema，入 manager/schema）：

```yaml
# plugin-manifest.v2 概念模型（字段说明）
name:        # 唯一名，kebab-case，与目录一致
version:     # semver
kind:        # skill | agent | tool | hook | mcp   ← 五类组件
contract:    # 契约引用（skills/definitions/*.md 或 agents/contract.json 或 package.yaml）
entry:       # 加载入口：dlopen 库 | python 模块 | 可执行体 | scenario SKILL.md 目录
deps:        # inject 式依赖声明（移植 dsh：等到依赖就绪才激活）
permissions: # 复用 plugin_d 既有 16 项权限 → Cupolas 守卫映射
lifecycle:   # 生命周期契约（load/start/stop/execute 或 apply/cleanup）
scope:       # global | per-agent（移植 dsh agent.ctx 作用域）
config:      # standard-schema 校验器引用（移植 schemastery）
```

配套动作：
- `plugin_discovery.c` 从"简单 key-value 解析"升级为 schema 校验（fail-closed）；
- `manager/schema/` 新增 `plugin-manifest.schema.json` + `scenario-skill.schema.json`；
- 新增 `manager/tools/plugin_validator.py`（移植 validate_qoder_plugin.py 检查项：清单合法/必填/路径越界/frontmatter/禁止目录）。

### 5.4 场景型技能（scenario skill）——新技能形态

**定位**：prompt 驱动、意图路由、产出证据背书产物（Qoder architecture-visualization 即此类），区别于执行型技能（deterministic JSON-in/JSON-out）。

**落点**：`skills/scenarios/<scenario-name>/`，与 `src/`、`plugins/` 并列。目录约定（吸收 architecture-visualization + dsh skill-provider 思想）：

```
skills/scenarios/architecture-visualization/
├── SKILL.md                      # 场景技能主体（frontmatter: name/description 承担语义触发路由）
├── references/                   # 共享契约（跨场景引用，对应 architecture-contract/evidence-model）
├── skills/                       # 子技能（explore 路由 → system-modeler/flow-visualizer/...）
├── examples/                     # 最小产物集模板 + 冒烟测试
└── render/                       # 渲染服务（graphviz/dsl/mermaid → SVG/ASCII，降级）
```

**运行时**：`SkillPlugin` 抽象出 `ScenarioSkill`（`get_description()` 承担路由 + `get_shared_gates()` 声明契约依赖 + `get_scene_boundary()` 声明 NOT-in-scope）；router skill（explore）按用户意图选最小场景集。**注册进 manager 的 capability registry（unit_type: scenario）**，由 plugin_d 以"内容包"形式加载（不 dlopen，仅解析 SKILL.md + 契约）。

### 5.5 补缺口（prompts 运行时链路 + 生成式目录门控）

- **prompts 链路修复**（E-3）：两个方案择一——(a) 新增轻量 `prompt_d`（读 registry.yaml + 模板渲染，经 gateway `/v1/prompt/execute` 暴露）；(b) 由 gateway_d 直接承接（已有 MCP `prompts/list` 路由雏形，补渲染实现 + registry 关联）。建议 (b)（gateway 已读 agentrt.yaml，加模板渲染成本低），后续版本需要时再拆 (a)。
- **生成式目录门控**（解决 E-1/E-2/E-4）：移植 dsh 的 tool-catalog 范式——`manager/tools/gen_capability_catalog.py`：**boot 各技能/agent/工具到真实 context 读 schema** 生成 `capability-catalog.json`（技能清单/契约路径/权限/实现语言），带 completeness guard（扫描 skills/agents/markets 断言每个包在清单中）+ freshness 门控（CI 中 diff 漂移即失败）。**该生成物成为唯一权威注册表**，替换 manager/skill/registry.yaml 与 manager/agent/registry.yaml 的人工清单（或让人工清单成为生成物的版本化输入）。

### 5.6 优先实施顺序（对齐 0.1.6+）

| 阶段 | 动作 | 解决 |
|------|------|------|
| **P0** | plugin-manifest.v2 schema + plugin_d schema 校验 + 离线 validator | E-4 |
| **P0** | 生成式 capability 目录 + CI 门控 | E-1 / E-2 |
| **P1** | 场景型技能确立（scenario-skill schema + ScenarioSkill 抽象）+ architecture-visualization 重构入 skills/scenarios/ | 场景型技能缺口 |
| **P1** | skills contrib 契约方言收敛到 SkillPlugin | E-5 |
| **P1** | prompts 运行时链路修复（gateway 承接渲染） | E-3 |
| **P2** | manager 悬空引用清理 + README 版本对齐 | E-7 / E-9 |
| **P2** | markets/agents 双 Schema CI 联动 | E-6 |
| **P2** | 消除硬编码 sys.path（skills/src、examples） | E-8 |

---

## 六、可借鉴点复核（上一份报告 14 条）

复核基于 dsh + ecosystem 实测交叉印证：

| # | 原可借鉴点 | 复核结论 | 依据 |
|---|-----------|----------|------|
| 1 | Skill 场景路由层（skill 两层化） | ✅ 确认真实可借鉴 | dsh `ctx.skills` seam + router skill；ecosystem 实测无场景型技能 |
| 2 | 共享契约层（跨技能契约） | ✅ 确认真实可借鉴 | dsh capability seams 契约先行；skills 现状只有单技能 definitions |
| 3 | 文件交付规则（图源写盘） | ✅ 确认真实可借鉴 | 与 agentrt「产物落盘」实践一致，成本极低 |
| 4 | 离线 validator（装前校验） | ✅ **双源印证，最实** | Qoder validate_qoder_plugin.py + dsh 生成式目录 freshness 门控 |
| 5 | 发布/运行时清单分离 | ✅ 确认真实可借鉴 | Qoder 双 manifest；ecosystem 实测 package.yaml 单清单 |
| 6 | 会话级 hooks + 上下文注入 | ✅ 确认真实可借鉴 | dsh hooks 是事件 listener（agent/pre-step 等 waterfall）；agentrt hook_d 仅 agent 内部生命周期 |
| 7 | MCP server 一等公民 | ⚠️ **降级为"协议桥"** | agentrt 网关为自研 JSON-RPC（L2 协议），MCP 应作为外部能力适配桥（gateway 侧），而非 plugin manifest 一等组件；dsh 的 acp 也是桥角色 |
| 8 | 规则库三形态管线 | ✅ 确认真实可借鉴 | redis 规则管线；dsh AGENTS.md 编译范式 |
| 9 | CLI 机器契约 | ✅ 确认真实可借鉴 | better-harness 契约；agentrt CLI/TUI 已成熟，收敛为规范 |
| 10 | 评估模型文档化 | ✅ 确认真实可借鉴 | better-harness models/*.md；dsh docs 即契约 |
| 11 | 证据-评分脱钩 | ✅ 确认真实可借鉴 | better-harness 七态证据；dsh 证据丰富度路由 |
| 12 | 幂等/重放安全表 | ✅ 确认真实可借鉴 | qmind 幂等表；agentrt 事件流 SSoT 同源 |
| 13 | 自举下载 + 版本钉扎 | ✅ 确认真实可借鉴 | security-scan/qmind；dsh python/sdk-runtime；复用 0.1.5 cosign 门禁 |
| 14 | 自包含分发 | ✅ 确认真实可借鉴 | create-plugin 打包规则；dsh bundle；与发布链 SSoT 对齐 |

**结论：14 条中 13 条确认、1 条降级（MCP 从"一等组件"降为"协议桥"）。**

---

## 七、dsh 新发现的可借鉴点（10 条，上一份报告未覆盖）

| # | 借鉴点 | 机制 | agentrt 落点 | 优先级 |
|---|--------|------|--------------|--------|
| 15 | **Capability Seam 三元角色** | 定义/Provider/Consumer 分离，Provider 可整族替换，Consumer 只依赖接口 | market_d 的每个包按"接口声明+实现+消费"三件套组织；plugin_d 暴露统一服务键 | P0 |
| 16 | **注册即效应（disposer 纪律）** | 所有注册必返回 disposer，卸载逆序撤销 | 根治 plugin_d 卸载残留；hook_d 注册可逆 | P0 |
| 17 | **inject 依赖声明替代手工排序** | 插件声明依赖，等依赖就绪才激活 | daemon/插件加载顺序由依赖图决定 | P1 |
| 18 | **显式生命周期状态机** | PENDING→LOADING→ACTIVE→FAILED→UNLOADING→DISPOSED + 状态迁移事件 | plugin_d 已有六态雏形，补状态迁移事件 | P1 |
| 19 | **五分发事件模式** | emit/waterfall/parallel/serial/bail | hook_d 策略点（pre/post_tool）用 waterfall 中间件；观察用 emit | P1 |
| 20 | **模型可见 ⟺ 已记录** | 到达模型的任何内容可自日志重建 | 与「事件流单一真相源」合并为同一不变量，补审计断言 | P0 |
| 21 | **scope 隔离原语** | agent.ctx + isolate：子世界装配 + 失败整体回滚 | agent_d 子 agent 局部工具/prompt 隔离 | P2 |
| 22 | **配置驱动 + 失败即大声** | 部署差异全走配置，插件禁硬编码可调参数；加载期大声失败 | markets 包禁止硬编码 tunables；plugin manifest 校验 fail-closed | P1 |
| 23 | **生成式目录作为文档/注册门控** | boot 真实 context 读 schema 生成目录 + completeness guard + freshness | 见 5.5（capability-catalog） | P0 |
| 24 | **配置热更新事务化** | 先导入新实现再处置旧实现、失败回滚 | plugin_d `update`/`restart` 事务化 | P2 |

---

## 八、伪可借鉴点排除（避免照搬）

**dsh 侧**（8 条）：
1. Vendoring 整个 Cordis 框架——借鉴设计不搬代码；agentrt 用 C 实现，直接依赖框架层无意义；
2. `SESSION_FORMAT_VERSION=0` 无兼容承诺——agentrt 面向生产，持久化格式须一上来有版本演进策略（与 0.1.5 SSoT 对齐）；
3. Typert 类型图 + 跨进程 RPC 网关——协议面规模不匹配 daemon 架构；
4. Code Mode 自修改运行时 + tool-cordis 动态挂载插件——安全边界极重，agentrt 不做自修改运行时；
5. 每包 invariant + 100% 单测门控——团队纪律非架构设计，按阶段引入；
6. keyless 快照重放测试体系——与 dsh ACP/JSONL 协议强绑定；
7. 双语文档 + word budget + 生成文档站——工程文化投入；
8. Claude Code/Codex hook 桥——具体协议适配（但其**通用 hook 协议词汇**值得学，见第 6 条）。

**Qoder 侧**（3 条）：
9. `canvases/*` viewer（依赖 Qoder `aicoding.formatViewer.*` dataKey 协议）——agentrt 渲染出口为 CLI/TUI/HTTP，viewer 契约保留、实现重写；
10. `interface` 市场 UI 元数据（brandColor/screenshots）——agentrt 市场无 UI 面；
11. 双 manifest 的 `visibility: hidden` 等市场字段——无对应概念。

---

## 九、architecture-visualization 重构方案更新（基于新设计）

上一份报告建议以 `markets/tools/architecture-visualizer` 包落地。基于本报告的五轴分层设计，**修正落点为 `skills/scenarios/architecture-visualization/`**：

| 层 | 原方案落点 | 新方案落点 | 理由 |
|----|-----------|-----------|------|
| 契约层 | 包内 contracts/ | `skills/contracts/`（跨场景共享）+ manager/schema 证据模型 Schema | 契约应为生态级而非包级 |
| 场景技能层 | 13 SKILL.md 转译 | `skills/scenarios/architecture-visualization/skills/`（explore 路由 + 9 场景 + 3 基础） | 归入"场景型技能"新形态 |
| 渲染层 | 包内 render/ | `skills/scenarios/architecture-visualization/render/`（graphviz→SVG，降级 ASCII/TUI） | 随场景技能分发 |
| 分发 | markets 包 | 经 markets 统一分发（scenario 包类型）+ manager capability registry 注册 | 定义归 skills、分发归 markets、注册归 manager，各归其位 |
| 验收 | 对 agentrt 自身建模 | 同（explore→system-modeler 对 agentrt 跑一次，产出 evidence model + C4 源 + 关系图） | 不变 |

**这恰好验证了五轴分层设计的正确性**：一个跨"契约/定义/分发/注册"的复杂能力，只有把各层职责归位，才不会变成又一个"三份权威"。

---

## 十、结论

1. **不新建 plugins 叶仓**。agentrt 的"插件"是 5 种异质机制，统一的是**契约与运行时模型**而非目录；新建叶仓会制造第 4 份技能权威，加剧 SSoT 冲突。
2. **正确重构 = 五轴分层 + 统一契约**：治理（manager：plugin-manifest.v2 + capability registry + validator + 生成式门控）→ 定义（skills/agents/prompts）→ 分发（markets）→ 运行（plugin_d 统一加载器 + prompt 链路修复）。
3. **场景型技能是新形态**（skills/scenarios/），architecture-visualization 归此；这是 Qoder 生态对 agentrt 最有增量价值的吸收点。
4. **可借鉴点复核**：上一份 14 条 13 条确认、1 条降级（MCP 作协议桥）；dsh 新增 10 条高价值点，其中 capability seam、disposer 纪律、模型可见⟺已记录、生成式目录门控为 P0。
5. **伪可借鉴已排除**：dsh 8 条 + Qoder 3 条，避免照搬框架代码、协议绑定方案与纯工程文化投入。

---

## 附：证据来源索引

- dsh：`.engineer-reference/user-reference/deepseek-harness-master/`（vendor/cordis/src/{context,service,fiber,registry,reflect,events}.ts、docs/{architecture,capability-seams,agent-lifecycle,event-producer-consumer,persistence-catalog,tool-catalog,cordis-primer,module-graph}.md、AGENTS.md、packages/AGENTS.md、examples/acp-agent/cordis.yml、native/landlock-run、python/sdk）
- Qoder：`.engineer-reference/user-reference/plugins/`（architecture-visualization 全量、create-plugin 规范、security-scan hooks、superpowers、redis-development、qmind、better-harness）
- ecosystem 实测：`airymaxhub/agent-workload/ecosystem/`（agents/registry/agents.yaml、manager/skill/registry.yaml、manager/agent/registry.yaml、manager/schema/ 11 个、markets/tools/maths-toolkit/package.yaml、prompts/registry.yaml、skills/definitions + plugins/manifest.yaml）
- daemon 交叉验证：`agentrt/daemons/`（plugin_d/src/{main,plugin_discovery,plugin_permission,plugin_service}.c、market_d/src/{market_service_install,skill_registry,agent_registry}.c、agent_d/src/{service_child,service_spawn}.c、tool_d/src/config.c、hook_d/README.md、gateway_d/src/{main,gateway_business_handler}.c、llm_d/README.md）、`agentrt/scripts/install.sh`、`sdk/sdk-python/agentrt/plugin_types.py`
