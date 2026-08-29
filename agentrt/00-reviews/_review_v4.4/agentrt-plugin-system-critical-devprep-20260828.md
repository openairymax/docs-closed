# agentrt 插件系统批判性开发准备报告

> **报告编号**：REVIEW-AGENTRT-2026-08-28-PLUGIN-SYS
> **报告类型**：批判性开发准备（critical development preparation）——插件系统设计研究
> **研究输入**：① `_review_v4.3` 历史审查 12 份报告（含 dsh 哲学/源码级/底座对比）② `docs/AirymaxRT/10-architecture`（agentrt 自身工程思想）③ `agent-linux` Unify Design SSoT（10-unify-design.md + ssot-registry.yaml + validate-ssot.py）④ `deepseek-harness-master`（Cordis 插件框架）⑤ Qoder `plugins` 插件生态
> **核心问题**：agentrt 要怎么做自己的插件系统？可借鉴融合两个参考项目的哪些点？
> **铁律**：所有技术融入点一律改为 agentrt 自身工程实现与技术命名（`airy_*` / daemon 形态 / [SC]/[SS]/[IND]/[DSL] 四层模型 / vtable 模式 / SSoT），避免抄袭嫌疑
> **产出目录**：`docs-closed/agentrt/00-reviews/_review_v4.4/`
> **审查日期**：2026-08-28
> **审查人**：SPHARX 工程标准组
> **状态**：开发准备研究（供插件系统立项前决策）

---

## 摘要

本报告回答两个问题：**agentrt 的插件系统是什么**、**怎么用 agentrt 自己的语言把它做出来**。

**结论先行**：

1. **agentrt 插件系统的本质 = 统一扩展机制**，不是新造一个"插件框架"，而是把 agentrt 已拥有的原生扩展基因（`airy_*_provider_t` vtable 模式、daemon 服务隔离、syscall.xml codegen SSoT、IPC 128B 契约、`airy_effect` 注册原语）**从 memory 一个能力域推广到全能力域 + 统一注册表**。这一结论在 v4.3 已定案（0.1.2 阶段 2「统一扩展机制」），本报告将其落实为可立项的具体设计。

2. **两个参考项目提供的是"抽象模式"而非"可抄机制"**：DeepSeek Harness（dsh）的 Cordis 是"进程内 TS 类型系统 + 插件"（框架形态），Qoder 插件是"IDE 宿主 + 声明式组件清单"（宿主形态）——agentrt 是"跨进程平台 + daemon 服务"（平台形态，K8s 类比）。物种不同，**只取抽象模式，全部用 agentrt 的 C 原语等价重构并重命名**。dsh 的 `Context`/`Fiber`/`inject`/`effect`/capability seam 对应 agentrt 的**服务注册表**/生命周期状态机/依赖契约/注册即撤销/能力插槽；Qoder 的 manifest/validator/组件模型对应 agentrt 的**扩展清单**/扩展校验器/能力组件模型。

3. **去抄袭化策略**：所有融入点采用 agentrt 既有命名体系（`airy_` 前缀、`*_provider_t` vtable、`*_d` daemon、`[SC]` 契约头、A-UEF 错误码、SSoT 单一权威源）。附录给出逐条"参考项目概念 → agentrt 原生命名"对照表，杜绝术语雷同。

4. **路线图**：P0（统一扩展契约 + 注册表 SSoT + 校验器）→ P1（场景能力新形态 + 事件流接入）→ P2（依赖注入 + 作用域隔离 + 组合层）。严格遵循 v4.3「先能跑、再抽象」的减法节奏。

---

## 一、研究输入与方法

| 输入 | 内容 | 使用方法 |
|------|------|----------|
| `_review_v4.3`（12 份） | dsh 哲学/源码级/底座对比、0.1.2 Unify 计划、逆向精简、跨域修正、全功能运行、三方综合、功能审计 | 子代理逐行精读，提取对插件系统的 18 条约束性决策 + 12 条正反借鉴结论 |
| `10-architecture/` | 五维正交原则（S/K/C/E/A 共 24 条）、系统架构、CoreLoopThree、IRON-9 共享模型、GCCP、GRAD | 精读内核观（K-1~K-4）与工程观（E-1~E-8），提取对扩展机制的设计约束 |
| `agent-linux` Unify Design SSoT | `10-unify-design.md`（A-UEF/A-ULP/A-UCS/A-ULS/A-IPC 五模块）、`ssot-registry.yaml`（TP-001~011 技术点权威源）、`validate-ssot.py`（规则 ID 注册校验） | 提取"每个技术点只允许有一个权威源"的工程化范式，作为插件契约 SSoT 的方法论依据 |
| `deepseek-harness-master` | Cordis 插件框架源码 + docs（architecture/capability-seams/agent-lifecycle/persistence-catalog）+ 示例 | 提取插件运行时模型（服务/生命周期/依赖/事件/作用域）的抽象模式 |
| Qoder `plugins` | architecture-visualization 全量 + create-plugin 规范 + security-scan hooks + superpowers + redis + qmind + better-harness | 提取声明式组件清单 + 离线校验 + 场景型技能 + 规则管线的抽象模式 |

---

## 二、agentrt 自身工程思想底座（插件系统的锚点）

### 2.1 五维正交原则（00-architectural-principles.md）

agentrt 的插件系统必须锚定在自身架构原则上，而非参考项目上：

| 维度 | 原则 | 对插件系统的约束 |
|------|------|-----------------|
| **内核观 K-1** | 内核极简：内核只留原子机制，一切用户态可实现的功能必须用户态实现 | 插件系统的**运行时核心**（注册表/生命周期/契约校验）属用户态服务（daemon），**不进 corekern**；corekern 只保留原子机制 |
| **K-2** | 接口契约化：跨模块交互必须通过明确定义接口，七维契约（方向/所有权/线程安全/可重入/前置后置/跨引用/版本） | 插件接口（`airy_*_iface_t`）必须带完整契约注释 + `@since`/`@deprecated` 版本标记 + 契约测试 |
| **K-3** | 服务隔离：所有用户态服务作为独立 daemon，服务之间不直接通信，必须经内核路由 | 插件**不新开 daemon**（一个 daemon 一个职责面，CodeGeeX 教训）；插件挂载到既有 daemon 的能力面上，经 IPC 总线通信 |
| **K-4** | 可插拔策略：所有算法选择为可运行时替换的策略接口，三函数模式（执行/销毁/私有数据） | **`airy_*_provider_t` vtable 是 agentrt 原生的可插拔机制**（memory 已落地），插件系统 = 该模式推广 + 统一注册 |
| **E-5** | 命名语义化 | 插件契约所有符号用 `airy_*` 语义化命名 |
| **E-6** | 错误可追溯 | 插件错误码走 A-UEF（`AIRY_E*` 负错误 / `AIRY_FAULT_*` 正故障），新增子空间需 SSoT 注册 |
| **E-7** | 文档即代码 | 插件契约文档与代码同源，生成式目录门控（dsh tool-catalog 范式的 agentrt 化） |
| **E-8** | 可测试性 | 插件契约测试（`tests/contract/`）+ 冒烟测试（扩展校验器） |

### 2.2 Unify Design SSoT 方法论（10-unify-design.md + ssot-registry.yaml）

agentrt-linux 的 Unify Design 是插件系统**元方法论**的直接来源：

1. **四句话哲学**（§1.2）：
   - 机制在内核，策略在用户态 → **机制在 daemon，策略在插件**；
   - 内核冷酷执法，用户温情裁决 → **注册表冷酷校验，用户态插件温情扩展**；
   - **每个技术点只允许有一个权威源**（SSoT v2）→ 插件系统的每个能力（接口/实现/权限/错误码/事件）一个权威源；
   - IPC 就是能力校验（Capability Folding）→ 插件调用的能力校验折叠进 IPC 数据面，不新增控制面 syscall。

2. **技术点权威源注册表（TP-001~TP-011）**：`ssot-registry.yaml` 为每个技术点登记 `authority_doc` + `sc_header` + `constraint`。**插件系统的技术点（扩展清单 Schema / 能力接口 / 权限位 / 错误码子空间 / 事件类型）同样登记入册**，由 `validate-ssot.py` 范式（扫描使用点 → 比对注册表 → fail-closed）保证漂移即失败。

3. **[SC]/[SS]/[IND]/[DSL] 四层模型（IRON-9 v3）**：插件契约分层——
   - `[SC]`：扩展清单二进制布局、能力接口头（字节级冻结，两端一致）；
   - `[SS]`：插件语义同源实现（daemon 侧）；
   - `[IND]`：第三方插件完全独立实现（只遵守 [SC] 契约）；
   - `[DSL]`：插件缺失/损坏时降级生存（内置能力兜底）。

### 2.3 agentrt 已拥有的原生扩展基因（实测）

| 基因 | 实物 | 状态 |
|------|------|------|
| vtable 可插拔 | `atoms/memory/src/memory_provider.h`：17 槽函数指针表 + capabilities 位图 + set_active 热切换 + sync_target 双向同步 | ✅ 已落地（memory 唯一能力域） |
| 注册即撤销 | `airy_effect` 原语（v4.3 定案 P1） | ⏳ 规划中 |
| 代码生成 SSoT | `atoms/syscall/include/syscall.xml` + `syscall_gen.py` + `--check` 防漂移 | ✅ 已落地（23 syscall） |
| daemon 服务隔离 | 18 daemon + IPC 总线 + `DAEMON_DECLARE_SHUTDOWN_METHOD` 统一标准方法 | ✅ 已落地 |
| 统一错误码 | A-UEF `AIRY_E*` / `AIRY_FAULT_*`（[SC] error.h 字节级冻结） | ✅ 已落地 |
| IPC 128B 契约 | `airymax/ipc.h` Layout C v4（magic ARE1 + badge + crc32） | ✅ 已落地 |
| 事件流单一真相源 | append-only 事件流 + 全局 seq + 「模型可见⟺已记录」 | ✅ 0.1.2 必做⑥ |

**关键判断**：agentrt 插件系统**不是从零建设，而是把上述基因统一收敛**。这正是 Unify Design SSoT 的"收敛多个权威源为唯一权威"思想在扩展机制上的落地。

---

## 三、历史审查（v4.3）对插件系统的既有决策链

12 份报告已形成完整决策链（详见配套摘要，此处给约束力最强的 10 条）：

| # | 决策 | 约束力 | 对插件系统的含义 |
|---|------|--------|------------------|
| 1 | 不砍 corekern/commons，反而加强 | 已定案 | 插件基础原语（注册表/`airy_effect`/不变量）落 commons |
| 2 | Unify Design SSoT 是元方法论 | 已定案 | 插件每个技术点一个权威源 |
| 3 | 双 IPC 协议收敛为 `airymax/ipc.h` 128B | 已定案 | 插件通信走 [SC] IPC 头，不新造协议 |
| 4 | 事件流单一真相源（必做⑥） | 已定案 | 插件产生的可观测事实汇入权威事件流 |
| 5 | memory_provider vtable 是差异化资产，作为能力接缝母版 | 已定案 | **插件主形态 = vtable 推广** |
| 6 | 能力三角色完整方为能力（Def/Provider/Consumer） | 已定案（0.1.2 阶段 2） | 插件接口必须三角色齐全 |
| 7 | 注册目标从"全局单例"演进为"按 key 注册表" | 已定案 | C 语言 hash 表 + 字符串 key |
| 8 | 注册即副作用 + disposer（`airy_effect`） | P1 | 插件注册可逆、卸载逆序回滚 |
| 9 | 服务按 key 查找 + 依赖注入 | P2 后置 | 先手写启动顺序跑通，再抽象 |
| 10 | 一个 daemon 一个职责面，新能力优先插件/GCCP 工具形态 | 已定案 | 插件化是控复杂度手段，不无限新增 daemon |
| 11 | 先能跑、再抽象（减法优先） | 已定案 | 插件系统按 P0→P1→P2 渐进，不一步到位 |
| 12 | 工程纪律类借鉴（文档分层/死链/字数预算/覆盖率门禁）不增运行时复杂度，立即做 | 已定案 | 插件契约文档配套纪律 |

**结论**：插件系统的**方向已被 v4.3 定死**——本报告不再争论方向，只把它落成可立项的工程设计。

---

## 四、批判性再审视：两个参考项目的"真可借鉴"与"伪可借鉴"

### 4.1 物种判别（先划界，再谈借鉴）

| 维度 | dsh（Cordis） | Qoder 插件 | agentrt |
|------|---------------|-----------|---------|
| 形态 | 框架/库（单进程 Node + 进程内 DI） | IDE 宿主 + 声明式组件清单 | **跨进程平台 + daemon 服务**（K8s 类比） |
| 插件本质 | 编程式插件（JS/TS 函数/类/对象） | 声明式组件 bundle（skills/hooks/mcpServers） | **vtable 策略 + 声明式清单**（两者都要） |
| 通信 | 进程内事件总线 + 服务注入 | 宿主固定 hook 点 | **IPC 总线（128B 契约）+ daemon 服务** |
| 生命周期 | Fiber 状态机 + effect 可逆 | 宿主挂载/卸载 | **daemon 生命周期 + 插件状态机** |
| 类型安全 | TS 声明合并（编译期） | 配置即契约（弱类型） | **[SC] 字节级 ABI + 契约测试（最强）** |

**批判性判断**：
- **dsh 的进程内 DI/事件机制不能照搬**（v4.3 已判：物种之别，给平台照抄框架的进程内机制方向就错）；
- **Qoder 的"宿主即 IDE"模型不能照搬**（agentrt 宿主是 daemon 群）；
- **可借鉴的是两者的抽象模式**：dsh 的"统一运行时模型"（服务/生命周期/依赖/作用域/事件五分发）与 Qoder 的"声明式清单 + 离线校验 + 组件分类"。

### 4.2 真可借鉴点（12 条，均将 agentrt 化）

| # | 参考项目 | 抽象模式 | agentrt 化落地 | 优先级 |
|---|---------|---------|----------------|--------|
| 1 | dsh | 服务按 key 注册与查找（Context 仓库） | `airy_service_registry`：C hash 表 + 字符串 key，daemon 启动注册，IPC 查询 | P1 |
| 2 | dsh | 依赖声明驱动加载顺序（inject） | `airy_dep_contract`：插件声明依赖服务 key，注册表等依赖就绪再激活 | P2 |
| 3 | dsh | Fiber 生命周期状态机 + 状态迁移事件 | `airy_ext_state`：`REGISTERED→ENABLED→ACTIVE→FAILED→DISABLED→REMOVED` + 状态事件入权威事件流 | P1 |
| 4 | dsh | 注册即副作用 + disposer 逆序回滚 | `airy_effect`（v4.3 已定名）：注册返回撤销令牌，卸载逆序执行 | P1 |
| 5 | dsh | 能力接缝三角色（Def/Provider/Consumer） | `airy_cap_slot`（能力插槽）：`airy_*_iface_t`（声明）+ `airy_*_provider_t`（实现）+ consumer（调用方） | P0 |
| 6 | dsh | 事件五分发模式（观察/拦截/并行/顺序/表决） | `airy_event` + 五模式（observe/intercept/parallel/sequence/verdict） | P1 |
| 7 | dsh | 作用域隔离（agent.ctx） | `airy_agent_scope`：per-agent 能力集隔离，子 agent 世界装配 + 失败整体回滚 | P2 |
| 8 | dsh | 生成式目录门控（tool-catalog） | `airy_cap_catalog` 生成器：boot 各能力读真实 schema 生成目录 + CI 漂移即失败 | P0 |
| 9 | Qoder | 声明式组件清单 + 双清单分离 | `airy_ext_manifest.yaml`（运行时清单）+ `market 发布清单`分离 | P0 |
| 10 | Qoder | 离线校验器（validate_qoder_plugin.py） | `airy_ext_validator`：装前校验（清单合法/路径/契约/frontmatter）+ 装后冒烟 | P0 |
| 11 | Qoder | 场景型技能（SKILL.md 方法论插件） | `airy_scenario`（场景能力）：prompt 驱动 + 路由 + 契约门 | P1 |
| 12 | Qoder/redis | 规则库三形态管线（规则→索引→编译全量） | `airy_rules`：单规则文件 + `_sections` 前缀归类 + 编译聚合 | P2 |

### 4.3 伪可借鉴点（排除，避免误抄）

| # | 参考项目 | 排除理由 |
|---|---------|----------|
| 1 | dsh vendoring Cordis 全家桶 | agentrt 用 C 原生实现，无框架可 vendor；借鉴设计不搬代码 |
| 2 | dsh `SESSION_FORMAT_VERSION=0` 无兼容承诺 | agentrt 面向生产，[SC] 契约字节级冻结 + 版本演进策略（TP 注册表） |
| 3 | dsh Typert 类型图 + 跨进程 RPC 网关 | 协议面规模不匹配 daemon 架构；agentrt 有 [SC] 字节级 ABI |
| 4 | dsh Code Mode 自修改运行时 | 安全边界极重，agentrt 不做 agent 修改自身运行时 |
| 5 | dsh 每包 invariant + 100% 单测门控 | 团队纪律非架构设计，按阶段引入（不构成插件系统组成部分） |
| 6 | dsh Claude Code/Codex hook 桥 | 具体协议适配，agentrt 无此宿主；通用 hook 词汇可参考（见 4.2-6） |
| 7 | Qoder `canvases/*` viewer（dataKey 协议） | 依赖 Qoder IDE 宿主，agentrt 渲染出口为 CLI/TUI/HTTP |
| 8 | Qoder `interface` 市场 UI 元数据 | agentrt 市场无 UI 面 |
| 9 | Qoder `mcpServers` 一等组件 | agentrt 网关自研 JSON-RPC，MCP 作**协议桥**（gateway 侧适配），非一等组件 |

---

## 五、agentrt 插件系统设计（批判性开发准备）

### 5.1 定位与哲学

**一句话**：agentrt 插件系统 = **统一扩展机制**——把 `airy_*_provider_t` vtable 模式从 memory 推广到全能力域，配统一注册表、统一契约、统一校验、统一事件流接入。

**三条哲学**（agentrt 原生表述，源自 K-4 + Unify Design）：
1. **机制在 daemon，策略在插件**：daemon 提供能力面（机制），插件挂在能力面上提供策略（对应 K-1/K-3）；
2. **一个能力插槽，一个权威源**：每个能力域（`airy_*_iface_t`）一个权威定义，其余只引用（对应 SSoT）；
3. **注册即撤销，卸载必回滚**：所有插件注册返回撤销令牌，卸载逆序执行 disposer（对应 E-8 可测试性）。

### 5.2 五类能力组件（agentrt 原生分类）

| 组件类型 | agentrt 命名 | 契约 | 运行时承载 | 示例 |
|---------|-------------|------|-----------|------|
| 策略实现 | `airy_*_provider_t`（vtable） | `airy_*_iface_t` + 契约测试 | 既有 daemon（dlopen/静态链接） | memory_provider / llm_provider / tool_provider / storage_provider / sandbox_provider |
| 工具包 | `airy_tool_pkg`（market 包） | `package.yaml`（SSoT） | market_d + tool_d | maths-toolkit |
| 场景能力 | `airy_scenario` | `CAPABILITY.md` + 契约门 | plugin_d（内容加载，非 dlopen） | 架构可视化 |
| 外部桥 | `airy_bridge` | 桥接器契约（STDIO/HTTP） | gateway_d 侧适配 | MCP / ACP / A2A 桥 |
| 规则库 | `airy_rules` | 规则文件 + 编译聚合 | 注入上下文 | 安全规则 / 配置规则 |

### 5.3 统一扩展清单（`airy_ext_manifest.yaml`，[SC] 契约）

```yaml
# 扩展清单（运行时清单，plugin_d 消费；市场发布清单在 markets 侧分离）
name: airy-ext-architecture-visualization   # kebab-case，与目录一致
version: 0.1.0                              # semver，与发布版本一致
kind: scenario                              # provider | tool_pkg | scenario | bridge | rules
iface: airy_scenario_iface                  # 能力插槽接口 key（注册表查找键）
entry:                                      # 加载入口（按 kind 解释）
  scenario_dir: ./capabilities/
deps:                                       # 依赖契约（airy_dep_contract）
  - service: airy_llm                       # 依赖服务 key
    optional: false
permissions:                                # 复用 plugin_d 16 项权限 → Cupolas 守卫
  - file_read: ["${AIRY_HOME}/ecosystem/**"]
  - network_outbound: true
lifecycle:                                  # 生命周期契约（airy_ext_state）
  timeout_sec: 30
scope: global                               # global | per_agent
config_schema: ./schema.json                # standard-schema 校验器
```

**[SC] 约束**：manifest 二进制布局/字段枚举冻结，`plugin_discovery` 升级为 schema 校验（fail-closed）；`manager/schema/` 新增 `airy-ext-manifest.schema.json`，技术点登记入 `ssot-registry.yaml`（TP-012）。

### 5.4 统一注册表（`airy_service_registry`，SSoT 收敛）

**现状缺陷**（实测）：技能注册表三处并存（skills 定义 / manager registry 引用悬空 / market_d 内存表）、Agent 注册表两处不一致、memory provider 注册到全局单例。

**收敛设计**：
- `airy_service_registry`：C hash 表 + 字符串 key，承载所有能力服务（`airy_llm` / `airy_tool` / `airy_memory` / `airy_sched` / ...）；
- 注册项 = `{key, iface, provider, state, deps, scope, manifest_ref}`；
- **生成式目录门控**：`airy_cap_catalog` 生成器 boot 各能力读真实 schema 生成 `capability-catalog.json`（唯一权威注册表），CI 漂移即失败——**消灭 E-1/E-2 双注册表漂移**；
- 注册表自身作为 daemon 服务（plugin_d 承载），经 IPC `plugin.*` 方法族访问。

### 5.5 生命周期与状态机（`airy_ext_state`）

```
REGISTERED → ENABLED → ACTIVE → FAILED ─┐
     │           │         │            │
     │           │         └──→ DISABLED → REMOVED
     └───────────┴─────────────→ REMOVED
```

- 状态迁移发事件入权威事件流（`plugin/state`，带 seq + trace_id）；
- 激活前校验：manifest schema → 权限裁决（Cupolas）→ 依赖就绪（若启用依赖契约）→ 接口契约测试；
- 卸载：逆序执行 disposer（`airy_effect` 撤销令牌）；
- 故障：走 A-UEF `AIRY_E*`（可恢复）/ `AIRY_FAULT_*`（不可恢复，Macro-Supervisor 裁决）。

### 5.6 事件模型（`airy_event`，agentrt 化）

| 分发模式 | agentrt 命名 | 语义 | 用例 |
|---------|-------------|------|------|
| emit | `AIRY_EVENT_OBSERVE` | 观察，不等待 | 插件统计/审计 |
| waterfall | `AIRY_EVENT_INTERCEPT` | 洋葱中间件，可短路 | 工具执行前拦截、策略 |
| parallel | `AIRY_EVENT_PARALLEL` | 并行 await | 多插件并行处理 |
| serial | `AIRY_EVENT_SEQUENCE` | 顺序直到裁决值 | 权限链 |
| bail | `AIRY_EVENT_VERDICT` | 顺序表决 | 审批链 |

事件三域（agentrt 化）：
- **事实事件**（session 持久事实，入权威事件流）；
- **运行事件**（daemon 协调，live 状态）；
- **能力事件**（挂策略到能力插槽）。

### 5.7 场景能力（`airy_scenario`）——Qoder architecture-visualization 的归处

```
ecosystem/skills/scenarios/architecture-visualization/
├── CAPABILITY.md              # 场景能力主体（frontmatter: name/description 承担语义路由）
├── capabilities/              # 子场景（explore 路由 → system-modeler/flow-visualizer/...）
├── contracts/                 # 场景共享契约（[SC] 头 or Markdown 契约 + schema）
├── examples/                  # 最小产物集 + 冒烟测试
└── render/                    # 渲染服务（graphviz→SVG，降级 ASCII/TUI）
```

运行时：`airy_scenario_iface`（`get_description()` 路由 + `get_contracts()` 契约门 + `get_boundary()` 边界声明），注册进统一注册表（`unit_type: scenario`），plugin_d 以内容包加载（不 dlopen）。

### 5.8 依赖契约、作用域、组合层（P2 后置）

- `airy_dep_contract`：插件声明依赖服务 key，注册表等依赖就绪再激活（v4.3 判 P2 后置，先手写顺序跑通）；
- `airy_agent_scope`：per-agent 能力集隔离，子 agent 世界装配 + 失败整体回滚（多智能体协作关键）；
- `airy_overlay`：声明式组合层（profile/叠加层），`--dump-config` 可观测（P2）。

### 5.9 融入 Unify Design SSoT（登记入册）

| 技术点 | ID | 权威源 | 约束 |
|--------|----|--------|------|
| 扩展清单 Schema | TP-012 | `manager/schema/airy-ext-manifest.schema.json` | 字段枚举冻结，fail-closed |
| 能力插槽接口 | TP-013 | `commons/include/airy_cap_slot.h`（[SC] 头） | 三角色完整方为能力 |
| 能力注册表 | TP-014 | `daemons/plugin_d/README.md`（方法表） | key 唯一，漂移即失败 |
| 插件错误码子空间 | TP-015 | `[SC] error.h`（A-UEF，`AIRY_EPLUGIN*` 子空间） | 禁止双轨 |
| 插件事件类型 | TP-016 | 权威事件流类型表 | 「插件可见⟺已记录」 |

---

## 六、去抄袭化对照表（附录 A：命名映射）

所有融入点必须使用 agentrt 原生命名，杜绝术语雷同。本表是开发时的强制对照：

| 参考项目概念 | 参考项目术语 | agentrt 原生命名 | 依据 |
|-------------|-------------|------------------|------|
| 依赖容器/服务定位 | Context / `ctx.<key>` | `airy_service_registry` / 能力服务 key（`airy_llm` 等） | K-3 服务隔离 + [SC] 契约 |
| 插件生命周期单元 | Fiber | `airy_ext_state`（扩展状态机） | E-8 可测试性 |
| 依赖声明 | inject | `airy_dep_contract`（依赖契约） | K-2 接口契约化 |
| 注册即副作用 | effect / disposer | `airy_effect`（注册即撤销）+ 撤销令牌 | v4.3 已定名 |
| 能力接缝三角色 | capability seam（Def/Provider/Consumer） | `airy_cap_slot`（能力插槽）：`airy_*_iface_t` + `airy_*_provider_t` + consumer | memory_provider 母版 + 三角色完整原则 |
| 事件分发模式 | emit/waterfall/parallel/serial/bail | `AIRY_EVENT_OBSERVE/INTERCEPT/PARALLEL/SEQUENCE/VERDICT` | 事件流单一真相源 |
| 插件清单 | plugin.json / cordis.yml | `airy_ext_manifest.yaml`（扩展清单） | 双清单分离（SSoT） |
| 离线校验器 | validate_qoder_plugin.py | `airy_ext_validator`（扩展校验器） | syscall_gen.py `--check` 范式 |
| 场景型技能 | SKILL.md 场景 skill | `airy_scenario` + `CAPABILITY.md` | skill 场景路由 |
| 规则管线 | rules/ + _sections + AGENTS.md | `airy_rules` + 规则文件 + 编译聚合 | 文档即代码（E-7） |
| 生成式目录 | tool-catalog / persistence-catalog | `airy_cap_catalog`（能力目录） | syscall.xml SSoT + `--check` |
| 作用域隔离 | agent.ctx / isolate | `airy_agent_scope`（Agent 作用域） | 多智能体协作 |
| 声明式组合 | profile / bundle / patch | `airy_overlay`（叠加层） | A-UCS 配置管理 |
| 外部能力接入 | mcpServers | `airy_bridge`（桥接器，gateway 侧适配） | 网关 JSON-RPC 架构 |
| 生命周期状态 | fiber 状态（PENDING/ACTIVE/...） | `airy_ext_state`（REGISTERED/ENABLED/ACTIVE/FAILED/DISABLED/REMOVED） | daemon 生命周期对齐 |
| 会话级 hooks | SessionStart/PostToolUse/Stop | `AIRY_HOOK_SESSION_START/TOOL_POST/STOP`（hook_d 扩展事件） | hook_d 8 类型 + 会话级扩展 |

> **红线**：以上映射是"抽象模式的 agentrt 化等价"，**禁止在 agentrt 代码/文档中出现参考项目术语**（Cordis/Context/Fiber/inject/effect/seam/plugin manifest/SKILL.md 等一律改用上表右列命名）。

---

## 七、融入路线图（P0/P1/P2，对齐 v4.3 减法节奏）

| 阶段 | 交付 | 验证 |
|------|------|------|
| **P0** | ① `airy_cap_slot` 能力插槽契约 + `airy_ext_manifest` schema（TP-012/013 登记）② `plugin_discovery` 升级 schema 校验（fail-closed）③ `airy_ext_validator`（装前校验 + 装后冒烟）④ `airy_cap_catalog` 生成式目录 + CI 漂移门控（收敛双注册表） | 183 ctest 回归；对既有 memory/llm/tool provider 跑目录生成 |
| **P1** | ⑤ `airy_effect` 注册即撤销原语（commons）⑥ `airy_ext_state` 生命周期状态机 + 状态事件入权威事件流 ⑦ `airy_scenario` 场景能力形态 + architecture-visualization 重构入 `skills/scenarios/` ⑧ `AIRY_HOOK_SESSION_START` 会话级 hooks（hook_d 扩展） | 端到端：场景能力对 agentrt 自身建模跑通 |
| **P2** | ⑨ `airy_service_registry` 服务注册表（按 key）⑩ `airy_dep_contract` 依赖契约 ⑪ `airy_agent_scope` 作用域隔离 ⑫ `airy_overlay` 组合层 ⑬ `airy_bridge` MCP 桥 | 多 Agent 协作 + 组合配置冒烟 |

**暂缓红线**（v4.3 明确）：
- 不新建 daemon 承载插件运行时（plugin_d 升级承担）；
- 不进 corekern（插件机制用户态化）；
- 不新增 IPC 协议（复用 128B [SC] 头）；
- 不做自修改运行时（agent 不动态改自身插件集）；
- 不机械迁移 TS 类型系统（C 等价：不透明结构体 + vtable + hash 表）。

---

## 八、风险与边界

| 风险 | 缓解 |
|------|------|
| 能力插槽推广到四域新增复杂度（v4.3 曾暂缓） | 严格按 P0→P1 渐进；先 memory 一个插槽跑通验证再推广（v4.3「先能跑」） |
| 统一注册表迁移冲击既有 manager registry / market_d 内存表 | 生成式目录先行（P0-④），以 `airy_cap_catalog` 为权威，人工清单降级为生成物输入 |
| 场景能力与既有执行型技能边界 | registry 用 `unit_type: scenario|provider|tool_pkg|bridge|rules` 区分，契约各自独立 |
| 插件安全（权限/沙箱/供应链） | 复用 plugin_d 16 项权限 + Cupolas 守卫 + 0.1.5 发布链路 cosign 验签门禁 + fail-closed 校验 |
| 命名去抄袭化不彻底 | 附录 A 对照表 + CI 术语检查（扫描参考项目术语出现即失败） |

---

## 九、结论

1. **agentrt 插件系统 = 统一扩展机制**：不是新框架，而是把已拥有的 `airy_*_provider_t` vtable 基因 + syscall.xml SSoT 范式 + daemon 服务隔离 + `airy_effect` 原语统一收敛。方向已由 v4.3 定案，本报告给出可立项工程设计。
2. **两个参考项目只取抽象模式**：dsh 提供统一运行时模型（服务/生命周期/依赖/事件/作用域），Qoder 提供声明式清单/离线校验/场景能力/规则管线——全部用 agentrt 的 C 原语等价重构并命名，杜绝术语抄袭。
3. **SSoT 是元方法论**：插件系统的每个技术点（清单/接口/注册表/错误码/事件）登记入 `ssot-registry.yaml`（TP-012~016），生成式目录 + 漂移门控保证单一权威源。
4. **落地节奏**：P0 统一契约+校验+目录 → P1 场景能力+事件流+会话 hooks → P2 注册表+依赖+作用域+组合。严格遵循「先能跑、再抽象」。
5. **去抄袭化是硬约束**：附录 A 命名映射为开发强制对照，CI 术语检查兜底。

---

## 附：证据来源索引

- 历史审查：`docs-closed/agentrt/00-reviews/_review_v4.3/`（12 份，重点 `agentrt-0.1.2-unify-plan-20260814.md` / `agentrt-vs-dsh-base-comparison-20260814.md` / `deepseek-harness-philosophy-20260814.md` / `deepseek-harness-source-level-20260814.md`）
- 工程思想：`docs/AirymaxRT/10-architecture/`（`00-architectural-principles.md` K-1~K-4 / E-1~E-8、`01-system-architecture.md`、`02-coreloopthree.md`）
- Unify Design SSoT：`docs/AirymaxOS/10-architecture/10-unify-design.md`（五模块 + 四句话哲学 + Capability Folding）、`agent-linux/ssot-registry.yaml`（TP-001~011）、`agent-linux/tools/validate-ssot.py`
- 参考项目：`works-engineering/.engineer-reference/user-reference/deepseek-harness-master/`（vendor/cordis/src/*.ts、docs/capability-seams.md、docs/agent-lifecycle.md、docs/event-producer-consumer.md、docs/persistence-catalog.md）、`.../plugins/`（architecture-visualization、create-plugin、security-scan、superpowers、redis-development、qmind、better-harness）
- 原生基因实测：`agent-workload/agentrt/atoms/memory/src/memory_provider.h`、`atoms/syscall/include/syscall.xml`、`daemons/plugin_d/`（plugin_discovery.c manifest 解析）、`daemons/hook_d/README.md`、`daemons/market_d/`、`commons/include/airy_types.h`、`sdk/sdk-python/agentrt/plugin_types.py`
