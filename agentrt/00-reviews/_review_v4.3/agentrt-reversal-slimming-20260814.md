# agentrt 过度设计诊断与瘦身反推论证报告

> **报告编号**：REVIEW-AGENTRT-2026-08-14-RV（反推论证 / 瘦身诊断）
> **报告类型**：架构反推论证（对既往「加法式借鉴」报告的纠偏与补充）
> **论证对象**：`agentrt`（AirymaxRT 0.1.1，~32 万行 C 代码）
> **对照基准**：`deepseek-harness-master`（`dsh`，~23 万行 TS 代码，可运行）
> **产出目录**：`closed-docs/agentrt/00-reviews/_review_v4.3/`
> **审查日期**：2026-08-14
> **审查人**：SPHARX 工程标准组
> **前置报告**：本报告是对 `deepseek-harness-philosophy-20260814.md`（架构级）与 `deepseek-harness-source-level-20260814.md`（源码级）的**反推纠偏**。前两份报告回答「dsh 有哪些思想可吸取」，本份回答「agentrt 为什么还不能跑、是否过度设计、真正该吸取的是减法还是加法」。

---

## 摘要（直接回答四个质疑）

本报告基于源码级定量对比与逐文件审视，直接回答用户提出的四个尖锐问题：

| 质疑 | 结论 |
|------|------|
| **agentrt 自身的设计没有亮点吗？** | **有亮点，且是真实差异化**：四层记忆（L1 原始/L2 特征/L3 结构/L4 模式）、四层内生安全（cupolas）、机制/策略分离（GCCP/工作大厅）、可拔插 provider（`memory_provider` 17 槽 vtable）、128 字节 IPC 头 + 全链路 `trace_id`。这些是 dsh 没有的。 |
| **是不是过于复杂了？** | **是，且是「性质性」的过度复杂**：agentrt 把「操作系统内核的复杂度」搬进了「用户态运行时」。证据：从零手写 15 个文件的内存分配器 + OOM 系统、29 个模块的基础库、6 万行的三循环引擎。 |
| **目前还是不能正常使用？** | **客观承认**：0.1.1 有 29 个 main 入口（17 daemons + CLI + gateway + 示例），但整体尚未收敛为「可正常使用」的运行时。根因不是「代码不够」，而是「基础设施太重、无法收敛」。 |
| **对比 dsh，agentrt 是不是太庞大了？** | **行数同量级（32 万 vs 23 万），但庞大在「性质」不在「行数」**：dsh 的 23 万行是 51 个薄薄的业务插件（可组合性被 Cordis 框架吸收）；agentrt 的 32 万行里有大量是「从零手写本应复用的基础设施」。 |

**一句话核心结论**：agentrt 的问题不是「要加 dsh 的能力接缝/事件流」（前两份报告的方向），而是「先砍掉内核级基础设施，用成熟能力替换手写实现，聚焦产品级差异化，让系统能跑」。

---

## 一、定量对比：庞大在「性质」不在「行数」

### 1.1 代码规模（源码级实测）

| 维度 | deepseek-harness | agentrt |
|------|------------------|---------|
| 源码文件数 | 1,397（packages 1,247 + apps 11 + scripts 139） | 1,098（.c/.h） |
| 源码行数 | ~231,000 行 | ~322,000 行 |
| 可执行入口（main） | 1 CLI + 1 Web | **29 个**（17 daemons + CLI + gateway + 示例） |
| 语言 | TypeScript（有 GC） | C11/C++17（无 GC，手写内存管理） |
| 框架 | Cordis（vendored 现成 DI 框架） | **无框架，全部从零手写** |

### 1.2 关键差异：dsh 复用基础设施，agentrt 手写基础设施

| 基础设施 | dsh 的做法 | agentrt 的做法 |
|----------|-----------|---------------|
| 内存管理 | V8 GC，零手写 | **15 个文件手写**：arena/mempool/slab/tcache/alloc/pool/refcount + OOM 系统（oom_handler/oom_daemon/oom_degrade/oom_pressure/oom_recovery/oom_config） |
| 基础库 | 复用 npm 生态（zod/schemastery 等） | **29 个模块手写**：logging/string/uuid/config/sync/network/observability 等 |
| 可组合性 | Cordis DI 框架（`ctx.effect`/`inject`） | 手写启动顺序 + 手写注册表 |
| 调度 | 交给 Node 事件循环 | 手写 scheduler（scheduler_core/priority/deps/posix/windows） |
| 类型安全 | TS strict + `Branded`/`assertNever` | 手写 `_Static_assert` + 不透明句柄 |

**结论**：两者行数同量级，但 dsh 的 23 万行是「业务」——session、agent-loop、tools、shell、fs 这些产品能力；agentrt 的 32 万行里有相当一部分是「本应复用的基础设施」——内存分配器、基础库、调度器、IPC 协议。

---

## 二、agentrt 的亮点（客观承认，不是没有亮点）

反推论证必须诚实：agentrt **有真实亮点**，且这些亮点是 dsh 不具备的差异化：

### 亮点 1：四层记忆（L1 原始 / L2 特征 / L3 结构 / L4 模式）

- dsh 只有 `Session.log`（append-only 会话日志），是「上下文管理」而非「记忆系统」。
- agentrt 的四层记忆是**真正的时间尺度分层记忆**：L1 原始数据、L2 特征索引、L3 结构化事务 KV、L4 模式提炼，配合遗忘引擎（`forget_ratio=0.1`）、演化（索引压缩）、吸引子。
- **这是 agentrt 的核心差异化，dsh、Kimi、智谱都没有这么系统的记忆分层。**

### 亮点 2：四层内生安全（cupolas）

- dsh 的 sandbox 只是 capability seam 的一个 provider（Landlock/bwrap），是「外挂式」沙箱。
- agentrt 的 cupolas 是「内生安全」：沙箱 workbench → RBAC+ABAC 权限 → 输入净化 → 审计追踪，四层纵深防御 + 零信任（默认拒绝、每次授权、完全可审计）。
- **这是 agentrt 相比 dsh 的安全优势。**

### 亮点 3：机制/策略分离的落地（GCCP / 工作大厅 / CLI）

- dsh 的机制/策略分离靠「插件 + preset」表达。
- agentrt 落地为「GCCP 目标完备确认（两阶段协议）+ 工作大厅（任务图注册/看板/取消）+ 交互式产品 CLI」，是**产品闭环**而非抽象机制。

### 亮点 4：可拔插 provider + 能力标记

- `memory_provider.h` 的 17 槽函数指针表 + `capabilities` 位图 + `set_active` 热切换 + `sync_target` 双向同步，是 capability seam 的 C 语言等价物，且比 dsh 多了「能力标记位图」和「双向同步」两个 dsh 没有的维度。

### 亮点 5：128 字节 IPC 头 + 全链路 trace_id

- `are_ipc_message_header_t`：magic `0x41524531` + `trace_id` + `correlation_id` + CRC32 + `_Static_assert` 锁死每个字段偏移。
- 这是「自描述的二进制 ABI 契约」，dsh 的 IPC 是 JSON-RPC，没有这么严格的二进制契约。

**小结**：agentrt 的亮点集中在「产品级差异化」（记忆分层、内生安全、机制策略分离、可拔插 provider），而非「基础设施」（内存分配器、基础库、调度器）。问题恰恰在于：**亮点被基础设施的复杂度淹没了**。

---

## 三、过度设计诊断：三大证据

### 证据 1：手写内存分配器 + OOM 系统（15 个文件）

```
atoms/corekern/src/mem/
├── arena.c / mempool.c / slab.c / tcache.c   # 四层分配器
├── alloc.c / pool.c / refcount.c / guard.c    # 通用内存
└── oom_handler.c / oom_daemon.c / oom_degrade.c / oom_pressure.c / oom_recovery.c / oom_config.c  # OOM 系统
```

**诊断**：一个**用户态运行时**（对标 K8s，跑在 Linux 之上），从零手写了四层内存分配器 + 完整的 OOM 处理系统。这是「内核级」复杂度——Linux 内核自己才需要 slab/buddy 分配器 + OOM killer。K8s 不需要手写 slab 分配器，它用 Go runtime 的 GC + 内存池。

**应当**：用户态运行时直接用 `malloc`/`mmap` + 一个简单的对象池即可；性能瓶颈出现时再优化（dsh 的「基础优先于爆炸半径」）。

### 证据 2：手写基础库（commons 29 个模块）

```
commons/utils/ = cache / cjson / cognition / compat / compliance / config_unified /
cost / error / execution / io / ipc / logging / memory / network / observability /
platform / print / quality / resource / sd / security / strategy / string /
sync / task / token / types / uuid
```

**诊断**：logging、string、uuid、config、network、sync 这些是成熟库（glib、boost、folly、libuv）已提供的能力，从零手写是**重复造轮子**。29 个模块里，真正属于 agentrt 产品差异化的可能只有 memory/ipc/observability 少数几个。

**应当**：引入成熟 C 库（或 C++ 标准库），只保留产品差异化的模块。

### 证据 3：三循环引擎体量（6.3 万行 + 单文件上千行）

```
coreloopthree（仅 .c 文件）总行数 62,736 行
  work_hall.c                        1,024 行
  cognition/engine_process.c           982 行
  dispatch/roadmap_sched.c             976 行
  prompt_loader.c                      973 行
  cognition/ext/multi_agent_collaboration.c  952 行
  checkpoint_adapter.c                 932 行
```

**诊断**：三循环引擎（认知/执行/记忆）+ orchestrator（Phase 0-4 管线）+ Pregel DAG + checkpoint + 多智能体协作，每个都是「完整设计」，但单文件上千行说明**复杂度已失控**。dsh 的 agent-loop 核心 `agent.ts` 才 496 行，且靠 waterfall 事件可插拔。

**应当**：先做「线性编排」跑通闭环，DAG/checkpoint/多智能体协作后置。

### 必要复杂度 vs 过度设计（区分表）

| 组件 | 复杂度 | 判定 | 理由 |
|------|--------|------|------|
| 四层记忆 | 高 | **必要** | 产品核心差异化 |
| 四层内生安全 | 高 | **必要** | 产品核心差异化 |
| 机制/策略分离 | 中 | **必要** | 平台定位根基 |
| 可拔插 provider | 中 | **必要** | 平台可扩展性 |
| 128 字节 IPC + trace_id | 中 | **必要** | 跨进程契约 |
| 四层内存分配器 + OOM | 高 | **过度设计** | 用户态不需手写 |
| commons 29 模块基础库 | 高 | **过度设计** | 成熟库已有 |
| syscall 4 级保护环 | 高 | **过度设计** | 用户态用进程隔离+seccomp 即可 |
| Pregel DAG 引擎 | 高 | **过度设计（可后置）** | 先线性编排跑通 |
| orchestrator Phase 0-4 | 中 | **过度设计（可后置）** | 先单管线 |
| checkpoint 容错 | 中 | **过度设计（可后置）** | 先能跑 |

---

## 四、deepseek 为什么「能跑且不庞大」

反推 dsh 的「能跑」秘诀，本质是三个「减法决策」：

1. **选 TS（有 GC）**：把内存管理完全交给 V8，零手写分配器。这是 dsh 最关键的「减法」——它**根本没有内存分配器这一层复杂度**。

2. **选 Cordis（现成 DI 框架）**：把可组合性交给框架（`ctx.effect`/`inject`/`declare module`），自己只写「薄薄的插件」。51 个 package 里每个 package 就是「一个 Service 定义 + 几个 Provider/Consumer」，平均每个 package 不到 4000 行。

3. **「基础优先于爆炸半径」**：明确声明「无外部消费者时优先正确基础而非兼容 shim」，先能跑、快速迭代，而不是追求「完备设计」。

**对照 agentrt 的三个「加法决策」**：
1. 选 C（无 GC）→ 手写四层分配器 + OOM 系统。
2. 不选框架 → 手写启动顺序、注册表、调度器、IPC。
3. 追求「完备」→ 四层记忆 + 四层安全 + 三循环 + Pregel DAG + checkpoint 全部一次到位，导致无法收敛。

---

## 五、反推论证：真正可落地的融合点（减法式）

**关键纠偏**：前两份报告给出的是「加法式借鉴」（引入 capability seam、单一真相源事件流、运行时 invariant）——如果照做，会**进一步加重复杂度**，让 agentrt 更难收敛。反推论证后，真正应该借鉴的是「减法式」：

### 减法融合点 1（最高优先）：用成熟能力替换手写基础设施

- **砍掉**：`corekern/src/mem/` 的四层分配器 + OOM 系统（15 个文件）。
- **替换**：`malloc`/`mmap` + 简单对象池；OOM 交给操作系统。
- **保留**：`memory_provider` 的 17 槽 vtable（这是产品差异化，不是基础设施）。
- **依据**：dsh 的「基础优先于爆炸半径」——先用最简单的，性能瓶颈出现再优化。

### 减法融合点 2（最高优先）：先「线性编排」跑通，再上 DAG

- **砍掉/后置**：Pregel DAG 引擎、orchestrator Phase 0-4 管线、checkpoint 容错、多智能体协作。
- **先做**：`coreloopthree` 的线性「认知 → 执行 → 记忆」单循环，跑通最小闭环。
- **依据**：dsh 的 agent-loop 核心 `agent.ts` 才 496 行，就是「线性 turn/step 循环」，靠事件可插拔扩展，而非一次性上 DAG。

### 减法融合点 3：引入成熟 C 库替换 commons 手写模块

- **砍掉**：commons 29 个模块中可复用的（logging/string/uuid/config/sync/network）。
- **替换**：glib / libuv / 成熟 C 库。
- **保留**：memory/ipc/observability 等产品差异化模块。

### 减法融合点 4（仍然值得，但不增加复杂度）：工程纪律类借鉴

前两份报告中的「文档分层工程」「死链检测」「Agent Note」「覆盖率门禁」**仍然值得借鉴**，且**不增加运行时复杂度**——它们是「让复杂系统能收敛」的纪律，而非「更多机制」。

### 不推荐立即融合（加法式，会加重复杂度）

| 前两份报告建议 | 反推结论 | 理由 |
|---------------|---------|------|
| capability seam 推广到 LLM/tool/storage/sandbox | **暂缓** | 会新增 4 套 vtable，加重复杂度；先聚焦 memory 一个 seam 跑通 |
| 单一真相源事件流 | **暂缓** | 需要重构 coreloopthree 状态管理，先能跑再说 |
| 运行时 invariant companion | **暂缓** | 先有可运行系统，再补不变量 |
| 声明式组合（profile/bundle） | **暂缓** | 先手写启动顺序跑通，再抽象 |

---

## 六、瘦身路线图

### P0（立即，0.1.1 收敛期）：砍掉过度设计，先能跑

1. **砍掉手写内存分配器**：`corekern/src/mem/` 的 arena/mempool/slab/tcache + OOM 系统，替换为 `malloc` + 对象池。
2. **砍掉 syscall 4 级保护环**：用户态用进程隔离 + seccomp 即可。
3. **后置 Pregel DAG / checkpoint / 多智能体协作**：先线性编排跑通「认知 → 执行 → 记忆」最小闭环。
4. **引入成熟 C 库**：替换 commons 的 logging/string/uuid/config/sync/network。

### P1（1.0.1）：聚焦产品差异化，收敛

5. **保留并打磨四个亮点**：四层记忆、四层内生安全、机制/策略分离、可拔插 provider。
6. **引入工程纪律**：文档分层工程 + 死链检测 + Agent Note + 覆盖率门禁（不增加运行时复杂度）。

### P2（1.0.1+）：性能瓶颈出现时再优化

7. 只有当性能基准显示「内存分配是瓶颈」时，才考虑引入专用分配器。
8. 只有当「线性编排无法满足并行/条件需求」时，才上 DAG。

---

## 七、结论

1. **agentrt 有亮点，且是真实差异化**（四层记忆、四层内生安全、机制/策略分离、可拔插 provider），这些是 dsh 没有的。问题不是「没有亮点」，而是「亮点被基础设施复杂度淹没」。

2. **agentrt 确实过于复杂**，且是「性质性」的过度复杂：它把「操作系统内核的复杂度」（手写内存分配器 + OOM、syscall 保护环、Pregel DAG、三循环引擎）搬进了「用户态运行时」（对标 K8s）。

3. **agentrt 不能跑的根本原因**：不是「代码不够」，而是「基础设施太重、无法收敛」。32 万行里有相当一部分是「本应复用的基础设施」，导致系统无法收敛为「可正常运行」。

4. **对比 dsh，agentrt 的庞大不在行数**（32 万 vs 23 万，同量级），**而在性质**：dsh 的 23 万行是 51 个薄薄的业务插件（可组合性被 Cordis 吸收），agentrt 的 32 万行里有大量是「从零手写本应复用的基础设施」。

5. **真正该吸取的是「减法」而非「加法」**：前两份报告的「capability seam 推广」「事件流」「invariant」如果照做会进一步加重复杂度；真正该做的是「砍掉手写基础设施 + 后置过度设计 + 先能跑 + 聚焦产品差异化」。

6. **agentrt 的核心竞争力不在「实现多少内核级机制」，而在「四层记忆 + 内生安全 + 机制策略分离」这三个产品级差异化**——这三者才是 dsh 和 Kimi/智谱都不具备的护城河。瘦身不是否定 agentrt，而是让它的真正亮点浮出水面。

---

*报告完*
