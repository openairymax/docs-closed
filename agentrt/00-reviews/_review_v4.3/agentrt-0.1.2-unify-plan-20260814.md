# agentrt 0.1.2 规划：Unify Design SSoT 收敛融合总纲

> **报告编号**：REVIEW-AGENTRT-2026-08-14-012PLAN
> **报告类型**：版本规划（0.1.2 权威功能整合统一总纲）
> **方法论文本**：`docs/AirymaxOS/10-architecture/10-unify-design.md`（Airymax Unify Design 总纲）
> **对照对象**：`agentrt`（0.1.1 → 0.1.2）+ `agentrt-linux`（AirymaxOS，设计阶段）+ `deepseek-harness-master`（标杆参照）
> **产出目录**：`closed-docs/agentrt/00-reviews/_review_v4.3/`
> **审查日期**：2026-08-14
> **审查人**：SPHARX 工程标准组
> **状态**：规划文档（供 0.1.2 执行参考）

---

## 摘要

agentrt 0.1.2 的核心方法论是 **Unify Design 的 SSoT（Single Source of Truth，单一权威源）收敛融合**：

> **不砍功能，而是把"同一技术点的多个权威源"收敛为唯一权威实现，用"唯一权威"思想做变相削减复杂度。**

这直接对应 Unify Design 消解 7+1 个架构冲突点（C-01~C-08）的方法：50 个文件的调度策略统一成 sched_tac、双轨错误码统一成 A-UEF、双轨日志统一成 A-ULP、双平面 IPC 统一成 Capability Folding 单平面。agentrt 0.1.2 要做的是**把同样的方法应用于 agentrt 内部**——识别 agentrt 的"多权威源冲突点"，逐点收敛为唯一权威实现。

**核心立场（已确认）**：
- corekern/commons **不砍反而加强**（它们是 [SC] 契约 + 微核心原语 + 跨平台抽象的承载者，未来 agentrt-linux 跨态复用的基石）；
- 五认知机制（GCCP/GRAD/蓝图调度/双思考/DAG/任务大厅）的**功能语义全保留**，全功能运行；
- "削减复杂度"通过 **SSoT 收敛**（消除冗余权威源）实现，而非删除功能。

---

## 一、Unify Design SSoT 方法论回顾

### 1.1 设计哲学（四句话）

1. **机制在内核，策略在用户态**——内核只保留最小机制，全部策略下沉用户态守护进程。
2. **内核冷酷执法，用户温情裁决**——A-ULS 双 Supervisor 模型。
3. **每个技术点只允许有一个权威源**——SSoT v2 单一权威源模型，[SC] 共享契约头物理宿主唯一，CI 强制逐字节校验。
4. **IPC 就是能力校验**——Capability Folding 将 capability check 折叠到 IPC 数据面 fastpath。

### 1.2 五模块统一（A-UEF / A-ULP / A-UCS / A-ULS / A-IPC）

| 模块 | 全称 | 权威源 | 消解的冲突 |
|------|------|--------|-----------|
| **A-UEF** | 统一错误码与故障定义 | `error.h`（10 子空间 + Fault 码） | C-05 错误码双轨制 |
| **A-ULP** | 统一日志与打印系统 | `log_types.h`（128B 固定记录） | C-06 日志双轨制 |
| **A-UCS** | 统一配置管理 | `config/`（RCU 热重载） | 配置多源 |
| **A-ULS** | 统一生命周期监管 | `superv/`（8 态生命周期） | 调度表述不一致 |
| **A-IPC** | 统一进程间通信 | `ipc.h`（Layout C v4 + Capability Folding） | C-02/C-04/C-08 |

### 1.3 冲突点消解（C-01~C-08）

这是 Unify Design 的**方法论核心**：每个冲突点 = 一个"技术点有多个权威源"，消解方式 = "收敛为唯一权威源"。agentrt 0.1.2 直接复用这套方法。

---

## 二、技术借鉴点提取（真正有用的，SSoT 视角）

从 `_review_v4.3` 全部报告 + deepseek-harness 逐字节研究 + 三家厂商 + Unify Design 中，提取**真正能落地、且符合 SSoT 思想**的技术借鉴点：

### 2.1 从 deepseek-harness（工程模式，SSoT 可落地）

| # | 借鉴点 | SSoT 落点 | 优先级 |
|---|--------|----------|--------|
| 1 | **单一真相源事件流**（`seq=log.length` + `deriveMessages()` + 运行时断言"模型可见⟺已记录"） | 建立 agentrt 的**权威事件流功能**（对应 A-ULP Ring Buffer 是日志 SSoT） | P0（必做⑥） |
| 2 | **运行时 invariant companion**（每模块 `invariant.ts` 注册关系不变量） | 事件流配套：跨模块关系断言（task_plan 无环、IPC 响应匹配请求） | P0（⑥配套） |
| 3 | **边界错误 vs 内部错误分层**（adapter 边界 throw → finish chunk；内部 throw → 保留） | 对应 A-UEF 的 Error/Fault 分层 | P1（错误码收敛） |
| 4 | **注册即副作用 + disposer + 逆序回滚**（`ctx.effect()` 精确语义） | commons 统一 `airy_effect` 原语 | P1（commons 加强） |
| 5 | **品牌化 ID**（`Branded<B>` 类型层不可互赋） | `trace_id`/`msg_id` 从不透明结构体 | P1 |
| 6 | **文档分层 + one home per fact + slop 清单 + 死链/字数预算** | 正是 Unify Design 的 SSoT 声明思想 | P1 |
| 7 | **能力接缝三角色**（Definition+Provider+Consumer） | 对应 [SC]/[SS] 分层，memory_provider vtable 已雏形 | P2 |
| 8 | **服务按 key 查找 + 依赖注入**（`ctx.<key>` + `inject` 驱动加载顺序） | 服务注册到唯一 context，替代手写启动顺序 | P2（后置） |

### 2.2 从三家厂商（认知机制，已有对应，需加强）

| 借鉴点 | agentrt 已有对应 | 状态 |
|--------|----------------|------|
| 规划/执行解耦 | 任务大厅（Work Hall） | ✅ 已有 |
| 思考预算多档 | 双思考（Thinkdual t2/t1-f/t1-p） | ✅ 已有 |
| 可验证奖励优先 | GRAD 四验（E-02 Kahn 零 Token） | ✅ 已有 |
| 软约束替代硬惩罚 | Roadmap 三级降级（L1/L2/L3） | ✅ 已有 |
| 两级检索 | L2 语义缓存 | ✅ 已有 |
| 轨迹即资产 | 缺权威事件流（hall_store 雏形） | ⚠️ 需加强（= 必做⑥） |

### 2.3 从 Unify Design（架构方法，0.1.2 的直接指导）

| 借鉴点 | 0.1.2 落点 |
|--------|-----------|
| SSoT 单一权威源 | agentrt 内部冲突点收敛（见 §三） |
| 五模块统一 | 错误码/日志/IPC 收敛到 A-UEF/A-ULP/A-IPC |
| Capability Folding | IPC 头收敛（H1 Layout C v4 冻结） |
| 冲突点消解 | 把 C-01~C-08 方法映射到 agentrt |

---

## 三、agentrt 内部"多权威源冲突点"（SSoT 收敛清单）

这是 0.1.2 的**"变相削减复杂度"核心工作清单**。每个冲突点 = 一个技术点有多个权威源，收敛方式 = 保留唯一权威实现，其余冗余权威源统一到它。**这不是删功能，是消除"同一事实的多个权威定义"。**

| # | agentrt 冲突点 | Unify Design 对应 | 冗余权威源 | 唯一权威源（收敛目标） |
|---|---------------|------------------|-----------|----------------------|
| S-1 | **错误码双轨制** | C-05 | `airy_types.h` `AIRY_E*`（POSIX 负值）vs `airymax/error.h` `AIRY_E*`（正数幅值 10 子空间） | A-UEF：`airymax/error.h`（10 子空间 + Fault 码空间） |
| S-2 | **日志双轨制** | C-06 | `LOG_*` vs `AIRY_LOG_*`，128B 记录格式多处定义 | A-ULP：`airymax/log_types.h`（128B 固定记录 + 5 级枚举） |
| S-3 | **IPC 头三处分叉** | C-04 + A-IPC H1 | `airy_types.h` 旧 `airy_ipc_header_t`（AOSP magic）+ `corekern/are_ipc.h`（source/target 字符串）+ `airymax/ipc.h`（Layout C v4 + capability_badge） | A-IPC：`airymax/ipc.h` Layout C v4（magic ARE1 + badge + crc32，128B 冻结） |
| S-4 | **DAG 三套引擎** | C-01 同源 | `graph_engine`（图存储/遍历）+ `pregel_engine`（BSP 超步，半成品）+ `taskflow_advanced`（ready-batch，主链） | DAG 主链：`taskflow_advanced`（调度权威）+ `graph_engine`（图原语权威），Pregel 检查点职责折叠进 graph_engine |
| S-5 | **认知管线双套** | C-01 同源 | `orchestrator.c`（Phase 0-4）vs `engine_process.c`（Phase 0-4，含 GCCP+GRAD） | ~~认知主链：`engine_process`（含 GCCP+GRAD），orchestrator 重复管线合并~~ **不收敛（2026-08-14 用户决策）：两者功能不同**——orchestrator 是编排器（多任务/阶段编排、熔断、重试、进度、取消、自定义 pipeline），engine_process 是认知引擎（单次完整五阶段处理）。已确认现状：DECOMPOSITION/PLANNING/GENERATION 复用 `airy_cognition_process`（合理复用，保留）；orchestrator 整条执行管线无运行时调用方（孤儿 API，无冲突）。维持双管线并存，不合并。 |
| S-6 | **事件流无权威源** | A-ULP 思想 | `hall_store`（七类任务文件，雏形）+ 各模块各自记录，无全局 seq + 无"模型可见⟺已记录"断言 | 权威事件流：append-only 事件流 + 全局 seq + 运行时 invariant（对应 A-ULP Ring Buffer 是观测 SSoT） |
| S-7 | **沙箱依赖外部 docker** | A-ULS（纯 C 不用 BPF） | `workbench_container.c`（docker exec）vs `workbench.c`（fork/execvp） | 原生沙箱：Landlock + seccomp（dsh `landlock-run` 纯 C11 可移植） |
| S-8 | **[SC] 契约漂移** | C-04 | commons 侧与内核侧 10 头在 SPDX/include 前缀/空白对齐不一致 | [SC] 字节级对齐（`sc-dual-ci.yml` diff -q 通过） |

**关键洞察**：S-1~S-8 的每个冲突点，都是"同一技术点被多个文件/模块重复定义权威"，这正是复杂度膨胀的**结构性根因**。用 SSoT 收敛后，每个技术点只有一个权威源，复杂度自然下降——这就是"用唯一权威思想做变相削减复杂度"。

---

## 四、0.1.2 六项必做 + Unify Design 映射

六项必做项与 S-1~S-8 冲突点的对应关系：

| 必做项 | 对应冲突点 | 收敛动作 |
|--------|-----------|---------|
| ①删除半成品超步路径 + ②消除两套 DAG | S-4 | Pregel BSP 的检查点职责折叠进 graph_engine，删除半成品超步路径；taskflow_advanced 为调度权威 |
| ③收敛 orchestrator/engine 两套管线 | S-5 | ~~engine_process（含 GCCP+GRAD）为唯一认知主链，orchestrator 重复管线合并~~ **取消（2026-08-14 用户决策）：功能不同，不收敛**，维持双管线并存 |
| ④沙箱去 docker 化 | S-7 | 移植 dsh Landlock 纯 C11 实现，替换 docker exec |
| ⑤收敛双 IPC 协议头 | S-3 | 收敛三处分叉到 `airymax/ipc.h` Layout C v4，删除旧头 |
| ⑥单一真相源事件流 | S-6 | 建立 append-only 事件流 + seq + invariant 断言 |

**额外必做（从 SSoT 冲突点派生，与六项并列）**：
- **S-1/S-2 错误码/日志收敛**：airy_types.h 的 `AIRY_E*` 与 airymax/error.h 对齐（A-UEF），`LOG_*` 与 `AIRY_LOG_*` 对齐（A-ULP）——这是 Unify Design C-05/C-06 在 agentrt 的直接落地。
- **S-8 [SC] 契约对齐**：commons 与内核侧 10 头逐字节对齐，`sc-dual-ci.yml` 通过。

---

## 五、corekern/commons 加强方向（不砍，反而加强）

| 模块 | 加强动作 | 依据 |
|------|---------|------|
| corekern IPC 契约 | 收敛 are_ipc.h 到 [SC] Layout C v4，使 IPC 契约成为跨态唯一权威源 | S-3 |
| corekern 微核心原语 | 四层分配器/OOM/调度保留并加强（未来 agentrt-linux 内核态复用） | 用户立场 |
| commons [SC] 契约 | 10 头逐字节对齐内核侧（S-8） | C-04 |
| commons 平台抽象 | platform/compat/atomic_compat 保留加强（三平台基石） | 用户立场 |
| commons 零依赖安全基元 | banned_functions/logging/memory/security/sync 保留（工程规范执行器） | 用户立场 |
| commons 统一原语 | 引入 `airy_effect`（注册即副作用 + disposer + 逆序回滚，dsh 借鉴） | §2.1-4 |

---

## 六、CLI/TUI 优化（建立在必做⑥事件流之上）

| 方向 | 内容 | 依赖 |
|------|------|------|
| CLI 决策链可视化 | 展示 GCCP 五问、GRAD 四验（E-02 Kahn）、蓝图 L1/L2/L3 命中、任务大厅复核/终裁的真实决策链 | ⑥事件流 |
| TUI 多会话 + 看板 | 多会话 tab、会话列表、任务看板实时刷新 | ⑥事件流 |
| TUI 事件流驱动 | 滚动事件流 + 可回放 + fork/resume（dsh 式） | ⑥事件流 |
| 视觉体验 | 大幅度提升（配色/布局/层次/进度可视化） | 独立 |

**关键依赖**：CLI/TUI 的"决策链可视化 + 事件流驱动"都建立在⑥单一真相源事件流之上——先有权威事件流，CLI/TUI 才能可信地可视化决策链。

---

## 七、执行顺序（先评估再动工）

> **补充（2026-08-14 对比研究后）**：SSoT 收敛只解决"契约收敛 + 复杂度收敛"，是"让系统能收敛"的必要前提，但**不是"成为行业底座"的充分条件**。平台本质 = 声明式自愈（reconcile）+ 统一扩展机制。据此 0.1.2 范围修正为「SSoT 收敛 + 平台本质补齐」两阶段（详见 `agentrt-vs-dsh-base-comparison-20260814.md`）。

1. **阶段 0：影响面评估**（已完成）——对 S-1~S-8 每个冲突点做影响面评估（涉及文件、调用方、跨态影响、回滚风险），产出逐项评估清单。
2. **阶段 1：SSoT 收敛（六项必做 + S-1/S-2/S-8）**——先做①②③⑤（统一收敛，纯代码内收敛）+ ④（原生替换）+ ⑥（权威事件流，CLI/TUI 底座）。目标：契约收敛 + 复杂度收敛，让系统能收敛。
3. **阶段 2：平台本质补齐**——
   - **reconcile 闭环延伸**：把已有的"认知层 reconcile"（蓝图 desired → GRAD 收敛 → 执行 → 复核 DRIFT → 回灌 replan）延伸到"生命周期/资源层"（agent 自愈重启、任务失败自动重调度）。这是从已有本质延伸，非从零造 controller。
   - **统一扩展机制**：把 memory vtable 的"能力接缝"模式统一推广到 LLM/tool/storage/sandbox 四域 + 统一注册表（参考 dsh Cordis 三角色，但用 agentrt 的 vtable 形态）。
4. **阶段 3：corekern/commons 加强**——[SC] 对齐 + airy_effect 原语 + 品牌化 ID。
5. **阶段 4：CLI/TUI 优化**——基于⑥事件流做决策链可视化 + 多会话 + 事件流驱动 + 视觉优化。
6. **后置（不属 0.1.2）**：分布式一致存储（etcd 等价物）→ 云原生多机阶段（agentrt-linux cloudnative 子仓）；L1/L2 开源 + 评测基准 + 文档分层 → 生态工作。

---

## 八、结论

agentrt 0.1.2 的定位是 **"以 Unify Design SSoT 单一权威源思想，把 agentrt 内部的 8 个多权威源冲突点（S-1~S-8）逐点收敛为唯一权威实现"**。这不是"削减复杂度"（删功能），而是"变相削减复杂度"（消除冗余权威源）——每个技术点只有一个权威源后，复杂度自然下降，且与"全功能运行"完全兼容（功能语义全保留，只是不再有多个互相矛盾的权威定义）。

corekern/commons 作为 [SC] 契约 + 微核心原语 + 跨平台抽象的承载者，是收敛后的**唯一权威源本身**，必须加强而非削弱。五认知机制（GCCP/GRAD/蓝图/双思考/DAG/任务大厅）的功能语义全保留，全功能运行。

---

*本报告整合 `_review_v4.3` 全部 10 篇文档 + deepseek-harness 逐字节研究 + agentrt 源码审查 + corekern/commons 价值论证 + Unify Design 总纲，是 0.1.2 规划的权威总纲。*
