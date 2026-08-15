# DeepSeek Harness 工程设计思想与产品哲学对比分析报告

> **报告编号**：REVIEW-AGENTRT-2026-08-14
> **报告类型**：竞品/标杆工程研究（对标分析）
> **研究对象**：`deepseek-harness-master`（DeepSeek AI 开源 agent harness，简称 `dsh`）
> **对照对象**：`agentrt`（AirymaxRT 极境智能体运行底座平台工程，0.1.1 奠基版本）
> **产出目录**：`closed-docs/agentrt/00-reviews/_review_v4.3/`
> **审查日期**：2026-08-14
> **审查人**：SPHARX 工程标准组
> **状态**：研究性报告（非缺陷清单，供架构演进决策参考）

---

## 摘要

DeepSeek Harness（`dsh`）是由 DeepSeek AI 开发的开源 agent harness（智能体框架），采用**「一切皆插件」**的架构，由 Cordis 插件框架驱动，其设计哲学源自论文《A Programming Paradigm for Spatiotemporal Composability》。它以 TypeScript monorepo 组织，包含 51 个 packages、CLI/Web 两个应用、Python SDK 与 native Landlock 沙箱。

AgentRT 则是以 C11/C++17 实现、CMake 构建的**系统级运行时平台**，定位对标「Kubernetes 之于微服务」，采用循环分层架构（SDK → 服务 → 协议 → 网关 → 存储 → 安全 → 内核 → 支撑 → SDK），以 7 个叶子仓（atoms / commons / cupolas / heapstore / protocols / gateway / daemons）聚合实现。

两者技术栈与定位不同（TypeScript 插件框架 vs C 系统运行时），**不可照搬实现，但设计思想与产品哲学高度可互通**。本报告提炼出 **8 条可直接借鉴的工程设计思想**与 **5 条产品哲学**，并给出与 agentrt 现状的逐条对照与优先级落定路径。

**核心结论**：AgentRT 已在「机制/策略分离」「微核心最小化」「内生安全」「可拔插 provider（memory 层）」等方向与 dsh 不谋而合，但 dsh 在 **「能力接缝三角色抽象」「单一真相源事件流」「声明式组合系统」「工程纪律极致化」「文档分层工程」** 五个维度上有更系统化、更可执行的范式，值得在 1.0.1 演进周期内提炼吸收。

---

## 一、研究对象：deepseek-harness 是什么

### 1.1 项目本质

| 维度 | 说明 |
|------|------|
| 定位 | 开源 agent harness（智能体框架），`dsh` |
| 开发方 | DeepSeek AI |
| 许可证 | MIT |
| 阶段 | 开发者预览（Developer Preview），快速迭代，明确声明「未来将出现破坏兼容性的变更」 |
| 技术栈 | TypeScript（strict）、pnpm monorepo、ESM、Node.js ^22.19 \|\| >=24 |
| 规模 | 51 个 packages、2 个 apps（cli / web）、python SDK、native（Landlock 沙箱） |
| 核心依赖 | Cordis（vendored 插件框架，见 `vendor/`） |

### 1.2 架构一句话

> **一切皆插件（everything is a plugin）**，包括模型适配器、工具注册表、会话日志、agent loop 本身，都可由配置替换；**没有需要 patch 的特权核心**，扩展 dsh 的方式是「在其它插件旁挂载一个插件」。

---

## 二、deepseek-harness 的七大核心设计思想

### 2.1 一切皆插件 + Cordis 驱动（时空可组合性）

Cordis 是 dsh 底层 vendored 的插件框架，其五大思想（见 `docs/cordis-primer.md`）：

1. **插件是实现 `Service` 的对象**（函数 + 可选 `inject`/`apply(ctx)` 字段，或 `Service` 子类）。
2. **Context 是服务的仓库**：服务通过稳定的 `ctx.<key>`（如 `ctx.tools`、`ctx.llm`、`ctx.sessions`）被其它插件按 key 查找，而非 import 具体实现。
3. **通过 `inject` 声明服务依赖**：命名了必需服务的插件会等待该服务就绪，加载顺序由服务依赖表达，而非手写启动顺序。
4. **类型化事件通信**：服务通过 TypeScript 声明合并声明事件名，再以 `emit` / `waterfall` / `parallel` / `serial` 四种模式派发。
5. **注册是可逆副作用**：prompt 段、工具 schema、适配器、provider、监听器都通过 `ctx.effect()` / `ctx.on()` 安装，卸载时可靠回滚。

### 2.2 能力接缝（Capability Seam）三角色模型

这是 dsh 最精妙的设计抽象。一个 **seam**（可替换能力）由三个角色构成：

| 角色 | 职责 | 示例（shell 能力） |
|------|------|-------------------|
| **Service Definition** | 声明接口、拥有 `ctx.<key>` 与词汇类型（抽象类或具体注册表，**从不**是 TS `interface`） | `dsh-shell` |
| **Service Provider** | 实现接口（可多个） | `dsh-bash-local` / `dsh-bash-sandbox` |
| **Consumer** | 注入并使用服务（通常是模型可见工具） | `dsh-tool-bash` |

关键原则（AGENTS.md）：
- **一个能力接缝由三角色组成，才算完整，一个角色不算**；新增能力意味着设计三角色。
- 角色在独立演进时才拆到独立 package；同一关注点可同包多角色（如 `dsh-llm` 同时拥有 Service Definition 和 Consumer）。
- **换一个 provider 就换掉整个产品行为**：文件系统与 subprocess provider 共享同一执行世界，指向远程沙箱即同时移动 Bash/PTY/LSP，无需 provider fork。

### 2.3 Profile / Bundle 声明式组合系统

- **Profile**：命名组合，存于 Harness home，列出堆叠的 bundle、out-of-tree 插件、用户自己的 `cordis.patch.yml`。
- **Bundle**：Cordis 配置行的分发格式，可被上层 patch。
- 运行中的 `dsh` 是**启动时从有序层组合出的插件树**：`dsh-base`（模型/工具/持久化/沙箱/审批/设置/凭据/遥测）→ `dsh-web-app` / `dsh-headless` → profile 的 `cordis.patch.yml` → home 级 patch → `--patch` overlay。
- `dsh --profile web --dump-config` 可查看实际启动的插件树，任何一行都可通过 patch 替换。

### 2.4 Session Log 作为单一真相源 + 「模型可见 ⟺ 已记录」

- **session log 是模型所看到上下文的来源**：`deriveMessages()` 从日志投影模型历史；原始 `assistant/chunk` 事件保留 replay 与 UI 保真度。
- fork、resume、transcripts、telemetry、persistence 全部从这条 append-only 事件流派生。
- **运行时不变量断言**：「任何到达模型请求的内容必须能从日志重建」，新模型可见输入必须新增 session event（扩展 `SessionEventMap`）。

### 2.5 事件的三域分类

| 事件域 | 性质 | 用途 |
|--------|------|------|
| **Session events** | 持久事实，追加到日志并广播 | 需跨 reload 存活的记录 |
| **Agent events**（`agent/*`） | 携带 live `Agent` | 观察/拦截进行中的工作 |
| **Capability events**（`fs/*`、`tools/*`、`telemetry/*`） | 附加策略与适配器 | 无需 import loop |

### 2.6 极致工程纪律（AGENTS.md 核心约定）

- **覆盖率门禁**：CI 按 `packages/*/*/src` 每文件 100% 覆盖率（`test:coverage` 而非 `test` 才是 CI 门禁）。
- **Agent Note 强制**：非平凡变更必须在同一 PR 内附带 Agent Note（决策记录：为什么、放弃了什么、如何验证）。
- **注册即副作用**：一切贡献经 `ctx.effect()` / `ctx.on()`，registry 的 `register()` 返回 disposer。
- **模型可见 ⟺ 已记录**（如上）。
- **显式 > 隐式**：包边界上的默认值是 `resolve(request): Spec` 的显式步骤，而非隐藏在 `run()` 里的 `?? default`。
- **无硬编码可调参数**：部署相关选择必须是可验证的 `Config` 字段；`DEFAULT_*` 常量或测试钩子不算可配置性。
- **配置错误响亮失败**：自包含时加载即失败，否则在最早可解析点失败，绝不静默跳过缺失引用。
- **不透明跨边界 ID 品牌化**（`Branded<B>`），绝不裸 `string`。
- **类型系统信任**：同进程静态边界不加运行时校验；只在 parser/config、queued、model/tool JSON、durable/file、worker、process、wire 边界校验。
- **源平面 vs 制品平面，从不混用**。
- **测试描述行为而非正确性**：改行为连同测试一起改。

### 2.7 文档分层工程（Tier Taxonomy）

dsh 的 `docs/AGENTS.md` 定义了严格的文档分层标准，核心原则：

- **每个事实一个家（one home per fact）**：事实归属其所属层级，其它地方只链接。
- **分层 taxonomy**：根 `AGENTS.md`（常驻规则，1-3 行/条）→ 子树 `AGENTS.md` → `architecture.md`（有序地图）→ `subsystems/`（类型定义）→ Agent Notes（决策记录）→ postmortem（事故叙事）→ cookbook（分步指南）→ 包 README（包契约）。
- **字数控预算（wordcount budgets）**：`verify-doc-budgets` 门禁，根 `AGENTS.md` ≤ 1600 词、`architecture.md` ≤ 1800 词等。
- **slop 清单（反冗余审计）**：同一规则多处声明、历史叙述（"previously/now/no longer"）、实现状态注解、推理抄本、推理重复、段落墙、强调膨胀、spec-speak。
- **机器可检查链接**：`verify-md-links` 拒绝死链与失效锚点。
- **双语文档 i18n**：术语引导、成对更新、`dsh-translate-docs` 仅用户显式调用。

### 2.8 防御模式文档化（Defensive Patterns）

`docs/defensive-patterns.md` 将「实际踩过或差点踩过的 bug 类」规则化，例如：

1. **独立报告正交结果**：一个结果可同时是超时 + exit 0，每个独立事实单独呈现，不嵌套。
2. **公共契约双方遵守**：多表征归一化后再经公共 API 返回。
3. **异步状态不是同步状态**：`followup()` 无逐消息完成，勿把 `whenIdle()` 当作单次结果。
4. **释放必须达到静止**：teardown 发 kill 但未 await 子进程退出会留孤儿。
5. **回调异常包含在 dispatcher**：一个坏订阅者不能破坏核心生命周期。
6. **不把不可信输出交给环境或可预测路径**：spawned 命令用 scrubbed env（剔除 `*KEY*` 等），临时文件 0700 + 随机名 + owner-only open。
7. **删除 link 形路径**：`lstatSync().isSymbolicLink()` 后 `unlinkSync`，防 symlink race。

---

## 三、agentrt 当前状态对照

### 3.1 agentrt 架构现状（0.1.1）

| 维度 | agentrt 现状 |
|------|-------------|
| 语言/构建 | C11 + C++17，CMake（BAN-33 强制源外构建） |
| 架构 | **循环分层**：SDK → 服务层（17/20 daemons）→ 协议层（AgentsIPC/A2A/A2T）→ 网关层（gateway_d）→ 存储层（heapstore）→ 安全层（cupolas）→ 内核层（atoms 7 模块）→ 支撑层（commons）→ SDK（闭合） |
| 叶子仓 | 7 个（atoms / commons / cupolas / heapstore / protocols / gateway / daemons） |
| 内核层 | atoms：corekern（IPC/内存/调度/时间）、coreloopthree（认知/执行/记忆三循环）、syscall（5 类 + 4 级保护环）、taskflow（Pregel DAG）、frameworks（外部框架适配器）、memory（L1+L2 可拔插）、memoryrovol（商业记忆） |
| 安全层 | cupolas 四层内生安全（沙箱 workbench / RBAC+ABAC 权限 / 输入净化 / 审计追踪） |
| 机制/策略分离 | GCCP 目标完备确认（两阶段协议）、工作大厅（Work Hall）、交互式产品 CLI |
| 工程纪律 | BAN 规则、IRON 铁律、ASan+LSan+UBSan、严格合规模式（投毒不安全函数） |
| 许可证 | AGPL v3 + Apache 2.0 双许可证 |

### 3.2 已具备的「dsh 同源」基因

agentrt 并非从零起步，已在若干方向与 dsh 不谋而合：

| dsh 思想 | agentrt 已有对应 |
|----------|-----------------|
| 可拔插 provider | `memory/src/memory_provider.h`（函数指针表 + 能力标记）、`memoryrovol` 弱符号桥接 |
| 外部框架适配 | `atoms/frameworks`（线程安全注册表，兼容 LangChain/AutoGen/CrewAI/Semantic Kernel/LlamaIndex） |
| 机制/策略分离 | GCCP + 工作大厅 + 交互式 CLI |
| 内生安全 | cupolas 四层纵深防御（沙箱/RBAC/净化/审计） |
| 微核心最小化 | corekern 仅 IPC/内存/调度/时间 4 原子能力 |

---

## 四、可吸取的工程设计思想（8 条，按价值排序）

> 每条均含：dsh 做法 → agentrt 现状 → 差距 → 落地建议。

### 吸取点 1（最高价值）：能力接缝三角色模型系统化

- **dsh 做法**：能力 = Service Definition + Service Provider + Consumer 三角色，完整才算 seam；换 provider 换整个产品行为。
- **agentrt 现状**：`memory_provider.h` 已有「Service Definition（函数指针表）+ Provider（builtin/memoryrovol）」的雏形，但**缺少系统的 Consumer 角色与三角色完整性原则**；其余能力域（LLM、工具、存储、沙箱）未统一抽象。
- **差距**：能力抽象是碎片化的（memory 有 provider，LLM/tool 由 daemons 各自实现），无统一的「一个能力 = 三角色」元规则。
- **建议（1.0.1）**：提炼一条架构元规则「能力接缝 = Service Definition + Provider + Consumer，三角色完整方为能力」，并将 memory 的 provider 模式推广到 LLM、tool、storage、sandbox 四个核心能力域。这与 agentrt 的「机制/策略分离」IRON 铁律天然契合。

### 吸取点 2（最高价值）：单一真相源事件流 + 「模型可见 ⟺ 已记录」

- **dsh 做法**：append-only session log 是唯一真相源，`deriveMessages()` 投影模型历史，fork/resume/replay/telemetry 全从日志派生；运行时不变量断言「模型可见 ⟺ 已记录」。
- **agentrt 现状**：有 `heapstore` 堆式持久化、`coreloopthree` 三循环、AgentsIPC 消息传输，但**没有「单一真相源事件流」的明确原则**——认知循环的状态、记忆、审计分散在多个子系统，缺少一个可从日志重建模型上下文的权威流。
- **差距**：审计追踪（cupolas audit）与认知状态（coreloopthree）与记忆（memory）是三条独立的流，未统一为一个可回放、可 fork、可 resume 的事件流。
- **建议（1.0.1 重点）**：建立「Agent 会话事件流作为单一真相源」原则，让 coreloopthree 的认知循环输出 append-only 事件流，heapstore 持久化该流，审计/记忆/遥测从该流派生。这是从「状态散落」到「状态可重建」的关键跨越。

### 吸取点 3（高价值）：一切皆插件 / 注册即副作用 / 依赖注入驱动加载顺序

- **dsh 做法**：无特权核心，扩展即挂载插件；注册是可逆副作用（`ctx.effect()` 返回 disposer）；加载顺序由 `inject` 依赖表达而非手写启动顺序。
- **agentrt 现状**：20 个 daemons 静态编译、CMake 选项配置，`frameworks` 有线程安全注册表，但**缺少「注册即副作用 + 依赖注入 + 可逆卸载」的统一生命周期模型**。
- **差距**：daemon 的加载顺序、依赖关系、卸载清理多为手写，缺少声明式依赖表达。
- **建议**：在 commons 层引入「服务注册表 + 依赖注入」的统一原语，让 daemon 声明其依赖（而非手写启动顺序），注册返回 disposer 以支持可逆卸载。这与 agentrt 的 C ABI 稳定诉求兼容（C 函数指针表即可表达）。

### 吸取点 4（高价值）：声明式组合系统（Profile/Bundle）

- **dsh 做法**：运行实例 = 启动时从有序层组合出的插件树，可 `--dump-config` 查看，任何行可 patch。
- **agentrt 现状**：daemons 通过 CMake 选项 + 编译期配置组合，缺少运行时声明式组合与「查看实际组合」的能力。
- **差距**：组合是编译期的、静态的，无法在运行时声明式调整 daemon 组合。
- **建议（1.0.1）**：为 daemons 引入声明式组合配置（类似 `daemons.patch.yml`），支持「查看当前实际组合」与「按需 patch」，与「机制/策略分离」的产品闭环呼应。

### 吸取点 5（高价值）：预发布立场——基础优先于爆炸半径

- **dsh 做法**：明确声明「无外部消费者时，优先正确基础而非兼容 shim；SQLite 用单调 SCHEMA_VERSION，SESSION_FORMAT_VERSION 保持 0 无兼容承诺」。
- **agentrt 现状**：0.1.1 奠基版本，正处于「无大量外部消费者」窗口期，但**未在文档中显式声明这一立场**。
- **差距**：缺少一条「奠基期允许破坏性重构、优先正确基础」的明确工程立场，可能导致过度保守的兼容包袱。
- **建议（0.1.1 即可）**：在工程标准中显式声明「0.x 奠基期：基础正确性优先于兼容性，会话格式/内部 API 无兼容承诺」，1.0 起才固化兼容契约。这与 agentrt 的语义化版本 ABI 承诺（MAJOR 内稳定）形成清晰边界。

### 吸取点 6（高价值）：工程纪律极致化（Agent Note + 覆盖率门禁 + 显式>隐式）

- **dsh 做法**：Agent Note（非平凡变更强制附决策记录）、每文件 100% 覆盖率门禁、显式 > 隐式、无硬编码可调参数、配置错误响亮失败、源平面 vs 制品平面。
- **agentrt 现状**：已有 BAN 规则、IRON 铁律、sanitizers、严格合规模式，工程纪律已较严格。
- **差距**：缺少「Agent Note 决策记录」与「每文件覆盖率门禁」两类机制；「显式 > 隐式」「无硬编码可调参数」未提炼为明确规则。
- **建议**：① 引入 Agent Note 机制（非平凡变更附决策记录，归入 closed-docs）；② 将「显式 > 隐式」「无硬编码可调参数」「配置错误响亮失败」补充进工程标准 BAN/IRON 体系。

### 吸取点 7（高价值）：文档分层工程（Tier Taxonomy + one home per fact + slop 清单）

- **dsh 做法**：每个事实一个家；分层 taxonomy（常驻规则/架构地图/子系统类型/决策记录/事故叙事/分步指南/包契约）；字数控预算；slop 清单（反冗余审计）；机器可检查链接；双语文档 i18n。
- **agentrt 现状**：文档体系庞大（docs/AirymaxOS ~153 文档 + closed-docs），但**缺少「one home per fact」「slop 清单」「字数控预算」「机器可检查死链」的明确文档工程标准**，历史上已出现大量陈旧引用、跨文档不一致、命名残留等问题（见既往审查）。
- **差距**：这是 agentrt 文档体系当前最直接的收益点——既往审查反复发现的「陈旧引用」「跨文档不一致」「重复定义」问题，正是 dsh 的 slop 清单 + one home per fact 所针对的。
- **建议（0.1.1 即可，收益立竿见影）**：① 建立文档分层 taxonomy 与「one home per fact」原则；② 引入 slop 清单作为文档审计标准；③ 建立「机器可检查死链」CI；④ 建立字数控预算门禁。这四条直接根治 agentrt 文档体系的顽疾。

### 吸取点 8（中高价值）：防御模式文档化

- **dsh 做法**：把「实际踩过的 bug 类」规则化为 `defensive-patterns.md`（独立报告正交结果、异步状态不是同步状态、释放必须达到静止、回调异常包含、不可信输出环境隔离、symlink race 防护）。
- **agentrt 现状**：有 BAN 规则（投毒不安全函数）、安全编码规范，但**缺少「防御模式」这一层——针对生命周期/并发/子进程/teardown 的 bug 类规则**。
- **差距**：cupolas 有 workbench 子进程管理、audit 异步队列，daemons 有大量并发/生命周期代码，但「异步状态不是同步状态」「释放必须达到静止」等坑位规则未文档化。
- **建议**：在 closed-docs/agentrt 工程标准中新增「防御模式」章节，沉淀生命周期/并发/teardown 的 bug 类规则。

---

## 五、可吸取的产品哲学（5 条）

### 产品哲学 1：可组合性优先于单一实现

- **dsh**：「一切皆插件」，产品是插件的组合，而非一个固化实现。
- **agentrt 启示**：agentrt 已定位「运行时平台」而非「单一应用」，应进一步强化「平台 = 可组合原语的组合」，而非「平台 = 一组固定 daemons」。

### 产品哲学 2：单一真相源（Single Source of Truth）

- **dsh**：session log 是唯一真相源，其余全派生。
- **agentrt 启示**：应确立「Agent 会话事件流」为 agentrt 的单一真相源，记忆/审计/遥测/回放皆派生，避免多源状态不一致。

### 产品哲学 3：配置即组合（Composition over Configuration）

- **dsh**：profile/bundle/patch 三层声明式组合，`--dump-config` 可观测。
- **agentrt 启示**：daemon 组合应向声明式演进，让「运行什么、如何组合」成为可观测、可 patch 的配置，而非编译期硬编码。

### 产品哲学 4：诚实的产品立场

- **dsh**：明确「开发者预览」「未来将破坏兼容」，MIT 开源，社区驱动。
- **agentrt 启示**：0.1.1 奠基版本应诚实声明「奠基期无兼容承诺」，明确「基础优先于爆炸半径」，避免不切实际的兼容包袱。

### 产品哲学 5：文档即契约（Doc as Contract）

- **dsh**：每个 package 有 README 契约，JSDoc 是完整契约，文档与代码同 PR 更新，机器可检查。
- **agentrt 启示**：agentrt 已有 Doxygen + README 双语体系，可进一步强化「文档与代码同 PR 更新」与「文档契约机器可检查」。

---

## 六、优先级排序与落地路径

| 优先级 | 吸取点 | 落地周期 | 落地动作 |
|--------|--------|---------|---------|
| **P0（立即，0.1.1）** | 吸取点 5：预发布立场声明 | 0.1.1 | 工程标准新增「奠基期兼容立场」声明 |
| **P0（立即，0.1.1）** | 吸取点 7：文档分层工程 | 0.1.1 | 建立「one home per fact」+ slop 清单 + 死链 CI + 字数控预算 |
| **P1（1.0.1）** | 吸取点 2：单一真相源事件流 | 1.0.1 | coreloopthree 输出 append-only 事件流，heapstore 持久化 |
| **P1（1.0.1）** | 吸取点 1：能力接缝三角色 | 1.0.1 | 提炼架构元规则，推广 provider 模式到 LLM/tool/storage/sandbox |
| **P1（1.0.1）** | 吸取点 3：注册即副作用 + 依赖注入 | 1.0.1 | commons 引入服务注册表 + 依赖注入原语 |
| **P2（1.0.1）** | 吸取点 4：声明式组合 | 1.0.1 | daemons 引入声明式组合配置 |
| **P2（1.0.1）** | 吸取点 6：工程纪律补充 | 1.0.1 | Agent Note + 覆盖率门禁 + 显式>隐式规则 |
| **P2（1.0.1）** | 吸取点 8：防御模式文档化 | 1.0.1 | 新增「防御模式」章节 |

---

## 七、结论与边界说明

### 7.1 核心结论

1. **AgentRT 与 dsh 是「同目标、异技术栈」的两个工程**：前者是 C 系统级运行时平台（对标 K8s），后者是 TS 插件式 agent 框架（开发者预览）。设计思想互通，实现不可照搬。
2. **AgentRT 已具备 dsh 的「同源基因」**：机制/策略分离、微核心最小化、内生安全、可拔插 provider（memory 层）均已落地，说明两者在「平台化 Agent 运行时」这一目标上方法论趋同。
3. **dsh 最值得吸取的五个范式**：能力接缝三角色、单一真相源事件流、声明式组合、工程纪律极致化、文档分层工程。
4. **文档分层工程是 agentrt 当前最直接、收益最高的借鉴点**——它直接根治既往审查反复发现的「陈旧引用」「跨文档不一致」「重复定义」顽疾。

### 7.2 边界说明

- 本报告为**研究性对标分析**，非缺陷清单；具体采纳与否、采纳范围需架构评审决策。
- dsh 处于开发者预览，其部分机制（如 Cordis 的 TS 声明合并、`ctx.effect()` 可逆注册）依赖 TS 类型系统，C 语言落地需等价抽象（函数指针表 + 显式 disposer），不可机械迁移。
- 本报告不涉及许可证、不涉及代码修改，仅输出研究结论供决策参考。

---

*报告完*
