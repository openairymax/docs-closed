# agentrt-0.1.6 版本改进方案（大底座 · 小插件）——R2 修订版

> **方案编号**：PLAN-AGENTRT-0.1.6-20260828-R2
> **方案类型**：SSoT 大规模瘦身精炼 + 生态收敛 + 发布落地
> **决策依据**：`_review_v4.3`（12 份历史审查）+ `_review_v4.4`（4 份本周期研究 + 插件/五叶仓实测）+ `docs/AirymaxRT/10-architecture`（五维正交原则）+ agent-linux `Unify Design`（SSoT 单一权威源）
> **本版变更**：R2 修订版——在 R1（证伪修订）基础上，按 2026-08-29 评审意见完成 **3 处范围性修正**：
>   1. **范围收敛**：0.1.6 只做「减法收敛 + 生态 SSoT 收敛 + 发布链路落地」；五认知机制 vtable 策略化拆出为 0.1.7 独立方案，不与减法同版本；
>   2. **DAG 收敛加实证门**：两套 DAG 收敛前先 diff 证伪，确认重复实现才删；
>   3. **生态开放前置**：五叶仓实测（E-1~E-9）发现的真实 SSoT 冲突提升为 P0 级收敛项，作为生态开放的前提。
> **产出路径**：`docs-closed/agentrt/`
> **状态**：待评审（开发准备）
> **版本目标**：0.1.5a → 0.1.6

---

## 摘要

0.1.6 是一次**减法式重构 + 生态收敛 + 发布落地**：以 Unify Design SSoT（每个技术点一个权威源）为元方法论，把 agentrt 从"功能堆叠、多套并存、边界模糊"收敛为「**大底座 + 小插件**」。

底座（纯 C、收敛稳定、可验证）= `atoms` + `commons` + `cupolas` + `heapstore` + `gateway` + `protocols` + `daemons`。小插件（完全开放社区）= `ecosystem` + `sdk`。

**R2 范围声明**（与 R1 的本质差异）：

| 范围 | 0.1.6（本方案） | 0.1.7+（后续方案） |
|------|----------------|-------------------|
| 减法收敛（frameworks 撤销 / memory 合并 / tests 统一 / 分配器真重复消除） | ✅ 落地 | — |
| 两套 DAG 收敛（实证门后） | ✅ 落地 | — |
| commons 大域原子化 + 依赖图最小机制 | ✅ 落地 | — |
| **五认知机制物理聚合**（目录/文件组织，公共接口不变） | ✅ 落地 | — |
| **五认知机制 vtable 策略化**（机制策略分离的语义改造） | ❌ 不做 | 0.1.7 独立方案 |
| 生态层 SSoT 收敛（注册表/契约/缺口） | ✅ 落地（P0） | — |
| 发布链路落地（0.1.5a 已修未发成果 + 新制品） | ✅ 落地 | — |
| 插件机制增强（双 manifest / 离线 validator / SessionStart 注入） | 🔶 取 P0/P1 级子集 | 完整落地 |

> **为什么拆出版本**：R1 把「五认知机制聚合」与「减法重构」放同一版本。前者是对 73,595 行 coreloopthree 核心引擎的语义级重构（"只动目录/接口不动语义"自相矛盾——动接口即动语义边界），回归风险与"减法式重构"的低风险定位冲突。R2 将其**拆两步**：0.1.6 只做物理聚合（搬文件 + include 调整 + 公共接口不变 + 回归验证），vtable 策略化（机制策略分离）放 0.1.7 单独推进。这使 0.1.6 的每个变更点都可独立验证、可单独回滚。

---

## 一、现状诊断（逐字节实测）

### 1.1 模块规模（.c/.h 文件数 + 行数）

| 模块 | 文件数 | 行数 | 定位 |
|------|-------|------|------|
| `atoms/corekern` | 70 | 15,932 | 微核心原语（core/error/ipc/mem/observability/task/time） |
| `atoms/coreloopthree` | 260 | 73,595 | 核心运行时引擎（已吞 14 域） |
| `atoms/frameworks` | 2 | 926 | 通用框架适配器注册表（**仅被 core_init 引用 1 次**） |
| `atoms/memory` | 5 | 1,882 | 内置免费记忆 provider（L1+L2） |
| `atoms/memoryrovol` | 1 | 15 | 商业 MemoryRovol 构建桥 |
| `atoms/syscall` | 37 | 7,811 | 系统调用（[SC] 契约） |
| `atoms/taskflow` | 31 | 9,412 | DAG 任务流引擎（graph_engine + taskflow_advanced + workflow_patterns） |
| `commons` | — | 41,440（.c） | 统一基础库（33 子域） |
| `cupolas` | 133 | 36,924 | 安全穹顶 |
| `gateway` | 62 | 16,081 | 统一能力网关 |
| `heapstore` | 59 | 16,332 | 堆存储数据面 |
| `protocols` | 113 | 28,521 | 协议栈（core 4k + frameworks 2.9k + integrations 8.3k + standards） |
| `daemons` | ~240 | ~85,000（+common 33.5k） | 18 服务守护进程 |
| `ecosystem` 五叶仓 | — | — | 社区开放层（manager/prompts/markets/skills/agents） |

### 1.2 关键实测事实（R1 证伪依据，R2 保留）

1. **taskflow 依赖**：仅依赖 commons（`airy_memory.h`/`error.h`/`platform.h`/`logging.h`），**不依赖 coreloopthree**；被 `atoms/coreloopthree`（4 头）+ `tools/airy_cli`（6 处）共同消费 → 它是独立图引擎，非 coreloopthree 私有。
2. **atoms/frameworks 使用率**：`airy_frameworks.h` 仅被 `atoms/corekern/src/core/core_init.c` 引用 1 次；`protocols/` 内 **零引用** `airy_framework_adapter_t` → frameworks 是低使用率冗余。
3. **protocols/frameworks 独立性**：langchain_adapter（tool/proto/chain/agent/memory）+ autogen_adapter（msg/proto/agent）共 2,949 行，**自建接口**，不依赖 atoms/frameworks → 两者无耦合，非"同一套"。
4. **两套分配器语义**：`commons/utils/memory`（14 文件 4,037 行）含 memory_debug 五件套 + memory_pool + prealloc + stats_reporter（用户态门面/调试）；`corekern/src/mem`（3,687 行）含 alloc/arena/mempool/slab/tcache/pool/OOM 全家桶（微核心原语）→ 语义不同，非简单重复。
5. **commons 原子化现状**：33 子域，分布极不均——config_unified 6,982 行 / memory 4,037 / sync 3,299 / string 2,749 / logging 2,212 / ipc 2,364 为大域；已有 12+ 个"单文件子域"（uuid/task/strategy/id/effect/error/...）。

### 1.3 生态层实测（R2 新增，`_review_v4.4` 五叶仓边界报告 E 节）

生态层存在**真实 SSoT 冲突**（此前按 README 自述判定"边界清晰"过于乐观，内容级核查发现）：

- **E-1 技能注册表三处并存**：skills 叶仓（5 官方技能 + 3 contrib）/ manager/skill/registry.yaml（10 个不同命名"内置技能"，`contract_path` 在 skills 仓**全部悬空**）/ market_d 运行时 skill_registry.c——同一概念三份权威、两套命名、零自动化对齐。
- **E-2 Agent 注册表两处不一致**：agents/registry/agents.yaml（14 条）vs manager/agent/registry.yaml（13/11/12 计数互斥）+ market_d 内存注册表第三份。
- **E-3 prompts"运行时消费"声明与实现脱节**：README 声称 runtime 读 registry.yaml 解析 prompt，实际**无 prompt_d**、gateway 无 prompts 路由实现、sdk-python 无 prompt 模块。
- **E-4 插件功能三方共管无 schema 校验**：skills/plugins（定义）+ plugin_d（加载）+ markets（分发）；manifest.yaml 仅简单 key-value 解析，无 plugin-manifest.schema.json。
- **E-5 skills 仓内两种契约方言并存**：官方技能（SkillPlugin 契约）vs contrib（另一套 Skill 接口 + contract.json）。
- **E-6~E-9**：markets/agents 双 Schema 跨仓无自动化、manager 悬空引用、跨仓人工同步点（BUILTIN_TOOL_SCHEMAS、sys.path 硬编码）、分支/版本表述漂移。

---

## 二、目标架构：大底座 · 小插件

```
┌─────────────────────────────────────────────────────────────┐
│  社区开放层（开发者随意组装，不触碰底座）                      │
│  ecosystem（manager/prompts/markets/skills/agents）           │
│  sdk（sdk-python/sdk-rust/sdk-go/sdk-typescript/cli/tui）     │
├─────────────────────────────────────────────────────────────┤
│  ★ agentrt 底座（纯 C，机制稳定 + 策略可插拔）★               │
│                                                             │
│  atoms —— 微核心与原子能力                                    │
│    ├─ corekern       微核心原语（机制层，稳定）               │
│    ├─ coreloopthree  认知引擎（14 域 → 5 机制物理聚合）       │
│    ├─ taskflow       任务流/DAG 图引擎（唯一 DAG 权威）        │
│    ├─ memory         记忆子系统（免费+商业 provider 合一）     │
│    └─ syscall        系统调用（[SC] 契约）                    │
│  commons —— 原子化统一基础库（唯一基础设施权威 + 依赖图）      │
│  cupolas —— 安全穹顶（四层内生安全，机制层）                  │
│  heapstore —— 堆存储数据面                                    │
│  gateway —— 统一能力网关（唯一外部入口 + 能力校验）            │
│  protocols —— 统一协议栈（AgentsIPC/A2A/MCP + 框架/集成）     │
│  daemons —— 18 服务（共享壳 + 依赖图自动管理 + 只写业务）      │
└─────────────────────────────────────────────────────────────┘
```

**三大全局约束**（继承 v4.3 + Unify Design + 用户决策）：

1. **机制与策略分离**（K-4 + seL4 思想）：机制（IPC/内存/生命周期/能力校验/图引擎/安全穹顶）在底座，**稳定不因功能变动而改**；策略（认知策略/调度策略/遗忘策略/工具策略）以可插拔 vtable 表达，任一策略改动**不影响其他模块**。0.1.6 仅完成机制的物理聚合，vtable 策略化在 0.1.7。
2. **每个技术点一个权威源**（SSoT）：底座与生态任何能力一个权威定义，其余只引用。
3. **底座只减不增**：新能力走插件/协议/GCCP 工具，不新增 daemon，不新增核心域。

---

## 三、证伪报告（R1 保留 + R2 新增）

### 3.1 R1 证伪结论（保留）

| # | 技术点 | R1 修订 | R2 状态 |
|---|--------|---------|---------|
| 1 | taskflow 保留独立图引擎 | 维持独立，coreloopthree `loop_dag.c` 收敛 | ✅ 保留，但收敛加**实证门**（见 3.2） |
| 2 | frameworks 撤销 | atoms/frameworks 直接撤销；protocols/frameworks 保留 | ✅ 保留 |
| 3 | 两套分配器二选一 | 不二选一，逐文件 diff 消除真重复 | ✅ 保留 |
| 4 | 依赖图自动加载 | 采纳并扩展为统一依赖图机制 | ✅ 保留，0.1.6 最小实现 |
| 5 | commons 无限拆小 | 原子能力子域 + 无环依赖，非一文件一夹 | ✅ 保留 |
| 6 | 五认知机制聚合收敛 | 采纳 | ⚠️ **R2 拆两步**：0.1.6 物理聚合，0.1.7 vtable 化 |
| 7 | 五模块共用功能下沉 commons | 真/假重复逐项区分 | ✅ 保留 |
| 8 | tests 整合 | 采纳 | ✅ 保留 |
| 9 | gateway 统一能力网关 | 采纳 | ✅ 保留 |

### 3.2 R2 新增证伪（2026-08-29 评审）

| # | 评审点 | 结论 | 处置 |
|---|--------|------|------|
| 10 | 两套 DAG 是否真重复 | ⚠️ **未实证**：coreloopthree `loop_dag.c` 与 taskflow `graph_engine` 的功能对比缺失。若 loop_dag 含 loop 集成/checkpoint 等 taskflow 不具备能力，直接删即丢功能 | **加实证门**：执行前输出两接口/能力 diff；确认为重复实现才删；能力不足则"能力下沉 taskflow + loop_dag 改薄壳" |
| 11 | 五认知机制"只动目录/接口不动语义" | ❌ **自相矛盾**：动接口即动语义边界。73k 行引擎同版本 vtable 化回归风险不可控 | **拆两步**：0.1.6 物理聚合（公共接口不变），0.1.7 vtable 策略化 |
| 12 | 生态开放前置条件 | ❌ **前置缺失**：E-1~E-9 显示生态层注册表/契约存在真实冲突，不收敛即开放 = 把冲突暴露给社区 | 生态 SSoT 收敛提升为 **P0 级**，开放（P2）以其为前提 |
| 13 | 发布链路 | ⚠️ 0.1.5a 已修复问题（riscv64 构建链 / ver_cmp 更新器 / maths-toolkit 安装器）已入库但修复版制品**未发布**（atomgit 无法覆盖附件） | 0.1.6 发布一次性带上全部修复 + 新制品 |

---

## 四、核心整合决策（R2 修订后）

### 决策 1：taskflow 保留独立，两套 DAG 收敛（实证门前置）

- **taskflow 保留**为 `atoms/taskflow` 独立图引擎（DAG 图原语 + 调度 + 检查点的唯一权威）。
- **实证门**（新增，P0-2a）：先输出 `coreloopthree/src/loop/loop_dag.c` vs `taskflow/src/graph_engine.c` 的接口/能力 diff 报告（函数面、状态模型、checkpoint 语义、调度能力），确认重复才删。
  - 分支 A（重复实现）：删除 `loop_dag.c`，coreloopthree 改消费 taskflow 接口；
  - 分支 B（能力互补）：将 loop_dag 独有能力下沉 taskflow，loop_dag 改薄壳引用。
- 依据：taskflow 仅依赖 commons（无环），被 coreloopthree + airy_cli 共享；独立保留符合"机制层稳定"。

### 决策 2：frameworks 直接撤销

- **atoms/frameworks 撤销**：实测为低使用率冗余（仅 core_init 引用 1 次，protocols 零引用）。
- **protocols/frameworks 保留**：langchain/autogen 适配器是真实独立实现（2,949 行），与 atoms/frameworks 无耦合，不动。
- 撤销前先确认 core_init 对 frameworks 的依赖可移除；"通用框架适配器接口"若未来有真实需求，由统一能力插槽机制（`airy_cap_slot` + 注册表）承担。

### 决策 3：memory + memoryrovol 合并为统一记忆子系统

```
atoms/memory/
├── provider.h               # airy_memory_provider_t 接口（[SC] 权威）
├── builtin/                 # 免费 provider（L1+L2，原 memory/src）
└── memoryrovol/             # 商业 provider 构建桥（原 memoryrovol）
```

（目录级合并，商业授权边界与构建方式不变。）

### 决策 4：两套分配器消除真重复（不二选一）

| 层 | 保留内容 | 处置 |
|----|---------|------|
| `corekern/src/mem` | 微核心分配器原语（arena/mempool/slab/tcache/pool/OOM/guard/refcount） | 保留，未来内核态复用（用户定案） |
| `commons/utils/memory` | 用户态门面（AIRY_MALLOC 宏）+ 调试统计（memory_debug/prealloc/stats_reporter） | 保留语义，但**与 corekern 逐行同构的 arena/tcache 改为调 corekern**，消除重复实现 |

**执行前提**：先逐文件 diff（corekern arena.c vs commons arena.c 等），判定"逐行同构"才合并；同名不同实现（如 pool 语义不同）保留，不强行合并（v4.3 判据）。

### 决策 5：五模块共用功能下沉 commons（细化 + 真/假重复区分）

| 功能 | 权威归宿 | 真重复判定依据 |
|------|---------|---------------|
| JSON 解析/生成 | `commons/utils/cjson` | 各模块内嵌 cJSON 副本 |
| IPC 头构造/解析 | `commons/utils/ipc` | [SC] 128B 契约唯一实现 |
| 日志/打印 | `commons/utils/logging` | A-ULP 对齐，各 daemon 不得自写 |
| 错误码 | `commons/utils/error` | A-UEF 码空间唯一 |
| 内存分配宏 | `commons/utils/memory` | AIRY_MALLOC 族唯一 |
| 线程/平台抽象 | `commons/platform` | 三平台一致 |
| 配置解析 | `commons/utils/config_unified` | A-UCS 唯一 |
| 能力注册表 | `commons/utils/ext` | airy_cap_slot 唯一 |

**执行原则**：下沉 = 删源模块重复实现 + 改 include；每下沉一处跑对应测试；同名不同实现（假重复）不合并。

---

## 五、五认知机制聚合收敛（R2：物理聚合 + 分版两步）

### 5.1 现状：coreloopthree 14 域 → 5 认知机制

实测 coreloopthree 已吞 14 域（orchestrator/work_hall/roadmap_sched/lang_gateway/gccp/grad/cognition/hook/memory/governance/workspace/dispatch/registry/validators），违背"机制策略分离 + 单一职责"。

**聚合目标（物理层）**：按五认知机制收敛为 5 个独立目录域 + 机制层目录域。**公共接口不变、引擎语义不变**，只做文件组织 + include 调整。

| 认知机制 | 聚合后目录 | 收敛来源（原 14 域） |
|---------|-----------|---------------------|
| **GCCP**（目标完备确认） | `cognition/gccp` | gccp + cognition 部分 |
| **GRAD**（计划批判循环） | `cognition/grad` | grad/critique + cognition 部分 |
| **蓝图调度**（三级图纸调度） | `dispatch/roadmap` | roadmap_sched + dispatch |
| **双思考**（快慢思维） | `cognition/think` | cognition 引擎 + think_d 协同 |
| **任务大厅**（任务图/看板） | `work_hall` | work_hall + registry + validators |

**机制层（非策略，保留稳定）**：orchestrator / governance / lang_gateway / hook / memory / workspace。

### 5.2 分版两步（R2 核心修正）

| 步骤 | 版本 | 内容 | 验证 | 风险 |
|------|------|------|------|------|
| 第一步 | **0.1.6** | 物理聚合：搬文件到 5 机制目录 + 机制层目录，`#include` 路径调整，公共头文件/API 签名不变 | 全量 ctest 183+ 全通过 + 18 daemon 冒烟 + 行为回归（核心链路 socket 通） | 低（纯组织性，可整体回滚） |
| 第二步 | **0.1.7**（独立方案） | 语义改造：每个机制暴露 `airy_*_strategy_t` vtable，机制间仅经 vtable 交互，独立测试套件 | 各机制独立测试 + 换策略验证"改一不影响其他" | 高（语义级，须独立版本） |

> **禁止**：0.1.6 内同时做目录聚合与接口/语义改造。任何一步混入语义变更即违反本方案范围声明。

---

## 六、commons 原子化 + 依赖图（R2 修订后）

### 6.1 原子化粒度（证伪修订：非"无限拆小"）

**正确粒度** = 「一个原子能力一个子域 + 职责单一 + 依赖无环」，而非「一个文件一个文件夹」。

- **大域继续拆**：config_unified（6,982）→ 按 config 子能力拆；memory（4,037）→ 门面/调试/池化/预分配分离；sync（3,299）、string（2,749）、logging（2,212）、ipc（2,364）→ 按原子能力拆。
- **单文件子域不强行再拆**：uuid/task/strategy/id/effect/error 已是原子能力，再拆是负优化。

### 6.2 自动依赖图 + 环检测（0.1.6 最小实现）

**每个 commons 子域（以及 daemon、认知策略）声明依赖**，构建时自动生成依赖图 + 检测循环：

```
依赖声明（manifest/dep 段）:
  commons/utils/cache: 依赖 [error, memory, string]
  commons/utils/ipc:   依赖 [error, types, platform]

构建期自动:
  ① 收集全部声明 → 构建 DAG
  ② Kahn 拓扑排序 → 环检测（有环即 fail，报环路径）
  ③ 生成依赖图报告（谁依赖谁一目了然）
```

**复用 taskflow 的图引擎**（graph_engine 的 traverse/环检测原语）。

**R2 最小实现边界**（防范围蔓延）：
- 0.1.6 只做：commons 子域依赖声明 + 拓扑排序 + 环检测 + 依赖图报告；
- **不扩展到**认知策略 vtable 依赖（0.1.7 随 vtable 化一起做）；
- daemon 启动拓扑排序复用同一机制，但仅接入 commons 子域声明（18 daemon 启动顺序保持现状，不做调度改动）。

---

## 七、底座强化（减法后加固）

1. **gateway 统一能力网关**：统一 cap_key 路由 + SSoT 校验（注册表存在性 + 契约版本 + 权限）+ 事件流埋点。
2. **依赖图自动加载（最小）**：见 6.2，0.1.6 仅 commons 子域。
3. **能力插槽统一扩展机制**：`airy_*_provider_t` vtable 推广四域（llm/tool/storage/sandbox）+ 统一注册表——**0.1.7 随 vtable 策略化推进**；0.1.6 仅确认注册表基座（commons/utils/ext）就绪。
4. **事件流单一真相源**：append-only + 全局 seq +「模型可见⟺已记录」断言。

---

## 八、生态层 SSoT 收敛（R2 新增专章，0.1.6 P0 级）

> 依据：`_review_v4.4` 五叶仓边界报告 E-1~E-9。生态开放（P2）的前提是注册表/契约收敛。

### 8.1 收敛任务清单

| # | 问题 | 收敛方案 | 验证 |
|---|------|---------|------|
| S-1 | 技能注册表三处并存、命名互不相认、manager 引用悬空 | 技能定义单一权威 = **skills 叶仓**；manager/registry.yaml 改为**引用**（自动生成或校验存在性）；market_d skill_registry.c 由 skills 清单生成；删除悬空 contract_path | registry 一致性测试 + 悬空引用扫描 = 0 |
| S-2 | Agent 注册表两处计数/字段不一致 | 执行体权威 = **agents/registry/agents.yaml**；manager/agent/registry.yaml 仅存运维字段并自动对齐 | 双 registry 字段 diff 校验 |
| S-3 | prompts"运行时消费"声明无实现 | 两种处置选一：a) 实现 prompts 运行时渲染（gateway /v1/prompt/execute 落地）；b) 修正 README 声明为"离线评测 + 模板库"（当前事实）。**倾向 b**（避免新增 daemon，符合"底座只减不增"） | 文档-实现一致性校验 |
| S-4 | 插件 manifest 无 schema 校验 | 新增 `plugin-manifest.schema.json`（manager/schema 第 12 个），plugin_discovery.c 解析改为 schema 校验 | 非法 manifest 拒绝加载 |
| S-5 | skills 双契约方言并存 | contrib 契约对齐官方 SkillPlugin 契约（或明确 contrib = 社区实验区并文档化隔离） | 双实现契约测试 |
| S-6 | 跨仓人工同步点 | BUILTIN_TOOL_SCHEMAS vs tool_d 参数集、sys.path 硬编码：改为包安装 + CI 一致性测试 | 同步点自动化测试 |
| S-7 | 悬空引用/版本漂移 | 清理 manager 悬空引用、统一 .gitmodules 分支与 README 徽章 | 引用扫描 + 版本核对 |

### 8.2 插件机制增强（0.1.6 取 P0/P1 级子集）

从插件研究 14 条借鉴清单中选取**不改底座、纯生态层**的子集：

| 借鉴点 | 落地位置 | 阶段 |
|--------|---------|------|
| 组件声明即校验（离线 validator） | markets/插件分发校验器（Python 或 shell，随 market 包） | P1 |
| 运行时清单与发布清单分离 | skills/plugins manifest.yaml（运行时）vs 发布元数据 | P1 |
| 规则库三形态管线（模板→索引→编译） | prompts 叶仓构建管线 | P1 |
| SessionStart 上下文注入通道 | hook_d 会话级 hook（改 hook_d，不改底座） | P1 |

> 完整插件机制落地（disposer 纪律、生命周期状态机、Capability Seam 三元组织等）归 0.1.7+ 生态开放方案。

---

## 九、发布链路落地（R2 新增专章）

0.1.5a 发布轮已修复但**未随制品发布**的问题，0.1.6 一次性带上：

| 项 | 0.1.5a 状态 | 0.1.6 处置 |
|----|------------|-----------|
| riscv64 构建链（gitee 镜像 cmake / rust-lld / 断点续传） | 已修复入库（tools d62d7f2） | 0.1.6 制品使用修复后构建链出包 |
| 更新器 ver_cmp 字母后缀 bug | 已修复（latest/airymaxrt 2c2e555） | 0.1.6 包内启动器内置修复版 |
| maths-toolkit 安装器静默成功 bug | 已修复入库（markets 673e140） | 0.1.6 制品带修复版 modules/maths-toolkit |
| 发布流程 | 0.1.6 执行完整 publish-release.sh 链路（cosign + GPG + manifest + latest/ 更新） | 三架构（x86_64/aarch64/riscv64）+ 安装器随附件 |

---

## 十、实施路线（0.1.6 范围：P0 减法 + 生态收敛 + 发布落地）

### P0（收敛 + 生态 SSoT，先减法）

| 项 | 内容 | 验证 |
|----|------|------|
| P0-1 | memory + memoryrovol 合并（目录级） | 记忆测试 |
| P0-2a | **DAG 实证门**：loop_dag vs graph_engine diff 报告 | 实证报告评审 |
| P0-2b | 两套 DAG 收敛（分支 A 删 / 分支 B 下沉） | taskflow + coreloopthree 回归 |
| P0-3 | frameworks 撤销（先确认 core_init 依赖可移除） | 编译 + 全量 ctest |
| P0-4 | tests 整合到 tests/，统一 ctest | 183+ ctest |
| P0-5 | 两套分配器逐文件 diff，消除真重复 | 分配器单测 |
| P0-6 | **五认知机制物理聚合**（搬文件 + include 调整，公共接口不变） | 全量 ctest + 18 daemon 冒烟 + 核心链路回归 |
| S-1~S-7 | 生态层 SSoT 收敛（技能/Agent 注册表、prompts 声明、插件 schema、双契约、同步点、悬空引用） | 各收敛项校验 + 一致性测试 |

### P1（底座强化 + 原子化 + 插件子集）

| 项 | 内容 | 验证 |
|----|------|------|
| P1-1 | commons 大域拆原子能力（config/memory/sync/string/logging/ipc） | 编译 + 单测 |
| P1-2 | 依赖图最小机制（commons 子域声明 + 拓扑排序 + 环检测 + 报告） | 依赖图报告 + 环检测用例 |
| P1-3 | 五模块共用功能下沉 commons（真重复） | 各模块回归 |
| P1-4 | gateway 统一能力网关 | 能力调用链路 |
| P1-5 | 插件机制子集（离线 validator / 双清单 / 规则库管线 / SessionStart 注入） | 插件分发冒烟 |

### P2（生态开放前置验证 + 收尾）

| 项 | 内容 | 验证 |
|----|------|------|
| P2-1 | ecosystem/sdk 独立 clone 组装（在 S-1~S-7 收敛后） | 独立 clone 组装冒烟 |
| P2-2 | 事件流单一真相源 + 断言 | 审计/回放 |
| P2-3 | SSoT 技术点登记（TP-012~016）+ validate-ssot CI 门禁 | CI 漂移即失败 |

### 0.1.7+（后续独立方案，不在本版本范围）

- 五认知机制 vtable 策略化（机制策略分离语义改造）；
- 能力插槽推广四域 + 统一注册表（provider 化）；
- 完整插件机制（disposer 纪律 / 生命周期状态机 / Capability Seam 三元组织）；
- daemon 启动依赖图调度接入。

---

## 十一、风险与约束

| 风险 | 缓解 |
|------|------|
| frameworks 撤销误伤（core_init 引用） | 先确认 core_init 对 frameworks 的依赖可移除；移除后全量编译验证 |
| 两套 DAG 收敛误删（loop_dag 有独有能力） | **实证门 P0-2a 强制前置**：diff 报告评审后才执行分支 A/B |
| 五认知机制物理聚合破坏 S-5 收敛 | 聚合只动目录/include，公共接口不变；全量 ctest + 18 daemon 冒烟保回归；可整体回滚 |
| commons 依赖图引入循环依赖 | 环检测 fail-closed；构建期报环路径，禁止绕过 |
| 生态 S-1~S-7 收敛破坏社区兼容 | 收敛以"权威单一化 + 其余改引用"为原则，字段不删只对齐 |
| 生态开放后耦合未断 | P2-1 显式验证独立 clone 组装 |
| 0.1.6 范围蔓延（混入语义重构） | 范围声明硬约束：vtable 策略化一律归 0.1.7 |

**红线（不可违背）**：不砍 corekern/commons；五认知机制功能语义全保留（0.1.6 只做物理聚合）；不新增 daemon；纯 C；[SC] 字节冻结；一个技术点一个权威源；机制策略分离（机制稳定、策略可插拔——0.1.6 机制物理就位，0.1.7 策略化）。

---

## 十二、交付物与验收

- **交付**：本方案（R2）+ 各 P 阶段提交链（叶子仓 → agentrt → agent-workload → tools → airymaxhub）。
- **验收标准**：
  1. atoms 从 7 → 5 目录（corekern/coreloopthree/taskflow/memory/syscall），frameworks 撤销；
  2. 两套 DAG、真重复分配器各收敛为一（DAG 收敛前实证报告已评审）；protocols/frameworks 保持独立；
  3. coreloopthree 14 域 → 5 认知机制物理聚合 + 机制层，公共接口不变，全量 ctest 通过；
  4. commons 大域原子化 + 依赖图/环检测生效（最小机制）；
  5. tests 统一到 tests/，183+ ctest 全通过；
  6. 生态层 S-1~S-7 收敛完成（注册表单一权威 + 悬空引用清零）；
  7. ecosystem/sdk 可独立 clone 组装；
  8. 0.1.6 制品（三架构）发布 atomgit，携带全部 0.1.5a 修复；
  9. SSoT 技术点注册 + validate-ssot CI 门禁；
  10. 0.1.7 范围（vtable 策略化）已在独立方案登记，不在 0.1.6 验收内。

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | agentrt-0.1.6 版本改进方案（R2 修订版）| 2026-08-29
