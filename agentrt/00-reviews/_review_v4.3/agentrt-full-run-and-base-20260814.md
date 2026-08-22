# agentrt 全功能运行与行业底座目标综合评估报告

> **报告编号**：REVIEW-AGENTRT-2026-08-14-FINAL
> **报告类型**：综合战略评估（核心机制价值论证 + 跨态组合 + 全功能运行路线）
> **对照对象**：`agentrt`（用户态运行时，0.1.1）+ `agent-linux`（AirymaxOS，1.0.1）+ `deepseek-harness-master`（标杆参照）
> **产出目录**：`closed-docs/agentrt/00-reviews/_review_v4.3/`
> **审查日期**：2026-08-14
> **审查人**：SPHARX 工程标准组
> **状态**：研究性报告（供架构演进决策参考）
> **前序文档链**：`functional-audit` → `deepseek-harness-philosophy` → `deepseek-harness-source-level` → `agentrt-reversal-slimming` → `agentrt-cross-domain-correction` → 本报告

---

## 摘要

本报告对两个核心问题给出最终裁决：

1. **agentrt 的 DAG、双思考、蓝图调度、GCCP、GRAD 是否有价值？** —— **有，且是真实的、不可替代的核心价值**。此前 `agentrt-reversal-slimming` 报告"后置 Pregel DAG / orchestrator Phase 0-4 / checkpoint"的结论**部分误伤**：它把"功能语义"与"实现复杂度"混为一谈。正确裁决是——**五个认知机制的"功能语义"必须全功能保留（这是 agentrt 相对 dsh/Kimi/智谱的护城河），真正可瘦身的是"实现复杂度"（Pregel BSP 半成品、orchestrator 与 engine 的重复管线、各增强层）。**

2. **agentrt 与 agent-linux 如何可组合？** —— 通过 **IRON-9 v3 的 [SC] 共享契约层**（10 核心头文件 + 12 核心 syscall + 128B IPC 头）实现字节级同源。跨态复用的**正确形态**是：内核态复用"无浮点、无 I/O、可确定性判定"的机制子集（GRAD Kahn 拓扑、Roadmap L1 状态机、graph_engine 拓扑遍历），用户态保留 LLM 驱动的完整协议。

**目标锚定**：让 agentrt **全功能运行**（不是"先砍到能跑"），同时**削减实现复杂度**（不是削减功能）。这两者不矛盾——砍掉的是"手写 malloc 替代品、重复的 DAG 引擎、半成品的 BSP 超步"，保留的是"GCCP 事实确认、GRAD 逻辑确认、三级降级、三权分立、依赖调度、认知-执行解耦"这些功能语义。

---

## 一、核心认知机制价值论证（对"瘦身结论"的重新裁决）

> 以下论证全部基于源码事实，逐机制给出"功能语义（必须保留）"与"实现复杂度（可简化）"的区分。

### 1.1 GCCP（事实确认）与 GRAD（逻辑确认）—— 最核心，不可替换

**价值**：回答"LLM 生成的计划，凭什么值得执行？"，并把"凭什么"拆成两类不可互相替代的确认：

- **GCCP（事实确认）**：五问模型（终点 Φ / 起点 x₀ / 卡点 U / 受众 w / 完成判据 Q5），解决"用户意图是否完整、可验证"。核心价值在**机制/策略分离**——协议只负责"何时问、如何补全"，"向用户收集答案"是产品层回调，故同一协议在 CLI/TUI/内核态（无 UI）都可复用。
- **GRAD（逻辑确认）**：确定性四验是**零生成 Token 的硬逻辑检查**，主链不可替换的核心证据是 E-02 死锁检测用 **Kahn 拓扑排序**（确定性算法，客观可判定、可复现、零 Token），而非 LLM 文本批判（主观、随机、耗 Token）。A/C/B 三权分立（生成/硬验证/终裁）+ 决策链落盘（`trace/chain.jsonl`）。

**功能语义（保留）**：GCCP 五问 + 机制/策略分离；GRAD 四验（尤其 E-02 Kahn）+ A/C/B 三权分立 + 决策链可追溯。
**实现复杂度（可简化）**：`grad_coordinator.c` 的"差分熵削减"当前仍是全量验证（注释明言差分是"预留"）；workspace 四目录落盘可裁剪。

### 1.2 蓝图调度（Roadmap Sched，L1/L2/L3）—— 高频交互的成本核心

**价值**：解决"已收敛过的认知如何近零成本复用"，避免每次"继续/下一步"重进 LLM。三级降级：
- **L1 状态记忆（零 Token）**：状态机确定性转移 `Out(S_k) = { n | n.deps ∋ S_k }`，命中直接返回不进入认知管线；
- **L2 语义缓存（低 Token）**：真实检索链（MemoryRovol L2 向量索引 → bigram Jaccard → L3），θ 动态阈值 + 失败指纹；
- **L3 全量规划（GCCP+GRAD）**：兜底。

关键设计是**缓存质量自演化**：只允许 `PASS + SUCCESS` 写入 L2（准入门），`FATAL` 失效、`on_cancel` 触发 L1 回滚 + L2 失效——L1/L2 是用执行结果反向训练的，不是静态缓存。

**功能语义（保留）**：三级渐进降级 + 取消回滚 + replan + PASS/SUCCESS 准入门 + 结果回灌自演化。
**实现复杂度（可简化）**：L2 的 HNSW+BM25+bigram 三段降级链是性能增强（单阈值+有序缓存表即可达到功能语义）；multiplan 评审是附加能力。

### 1.3 双思考（Thinkdual：t2 / t1-f / t1-p）—— 双系统三权分立

**价值**：Kahneman S1/S2 落地为三模型分权（源码 `engine.c` 三槽）：
| 槽 | 角色 | 职责 |
|----|------|------|
| `tc3_s2_model` | t2 系统二（慢） | 构造/修正 DAG 计划（模型 A） |
| `tc3_s1_verify_model` | t1-f（事实终裁） | 语境终裁（模型 B） |
| `tc3_s1_expert_model` | t1-p（专业） | 确定性四验（零生成 Token，模型 C） |

`think_service.c` 证明它是托管 cognition engine 的服务实体，`enabled=0` 时优雅降级为单轮规划。

**功能语义（保留）**：三模型分权；[SC] 契约 `AIRY_THINK_FAST/SLOW` + Q16.16 定点（内核无浮点可用）；优雅降级。
**实现复杂度（可简化）**：feedback 环形缓冲（TUI 增强）、dual_coordinate 二次验证（附加层）。

### 1.4 DAG 调度 —— 依赖语义必须保留，Pregel BSP 是半成品

**关键源码事实**：当前存在**两套并行 DAG 机制**，运行时实际只用一套：
- `graph_engine`（通用图引擎）：存储/遍历/BFS/DFS，真实可用；
- `pregel_engine`（BSP 超步）：`run_superstep()` 只搬消息**不调用 compute_func**，`worker_thread_func` 是轮询循环（10ms sleep）**非 BSP 屏障模型**，`BAN-333` 强制 `max_workers=1`；
- `taskflow_advanced`（工作流 DAG）：`execute_ready_batch()` 才是真正的"依赖就绪 → ready batch 执行"，**Work Hall 实际走这条路径**。

**裁决**：DAG 的**功能语义**（依赖→拓扑→ready batch 调度 + 错误策略/重试/取消/超时）必须全功能保留——它已经跑起来了；但 **Pregel BSP 超步是"实现复杂度"**——半成品、与 taskflow_advanced 语义重复、无主链路调用，可折叠进 graph_engine 或删除。

### 1.5 任务大厅（Work Hall）—— 认知-执行解耦

**价值**：认知层（GCCP+GRAD 产出计划）与执行层（真实 agent 进程）之间的宿主与调度中枢。源码证明闭环完整：发布（`plan_to_dag`）→ 领取（`wh_register_handlers` 绑定 agent 路由）→ 回传 + 复核（`execution_review` → t1-f 终裁）→ 回灌（PASS 缓存 / REJECT 失效 + replan）。

**功能语义（保留）**："认知发布→执行领取→产物回传→复核+回灌"解耦闭环 + agent 路由 handler + 统一看板。
**实现复杂度（可后置）**：governance（token 预留）、workspace isolation、hall_store（event sourcing 全量落盘）、nested delegation 四层增强。

### 1.6 对"瘦身结论"的最终裁决

| 原结论（reversal-slimming） | 修正后裁决 |
|---------------------------|-----------|
| "后置 Pregel DAG" | ✅ 正确——Pregel BSP 半成品可折叠，但 **DAG 功能语义保留**（taskflow_advanced 已跑通） |
| "后置 orchestrator Phase 0-4" | ⚠️ 需澄清——`orchestrator.c` 与 `engine_process.c` 是**两套平行管线**，应**收敛为一条主链**而非砍掉；engine 内 Phase 0-4（含 GCCP+GRAD）是核心价值 |
| "后置 checkpoint" | ⚠️ 可后置但不等于无价值——是可靠性增强，全功能运行最终需它支撑长任务恢复 |

**一句话总结**：五个机制的**功能语义全部有真实不可替代的价值，应全功能运行**；真正可瘦身的是**实现复杂度**——Pregel BSP 半成品、orchestrator 重复管线、以及 governance/isolation/event-sourcing/multiplan/差分等增强层。

---

## 二、agentrt + agent-linux 可组合性论证

### 2.1 8 子仓与 agentrt 的同源映射

| agent-linux 子仓 | 复用 agentrt 模块 | 职责 |
|-------------------|------------------|------|
| `kernel/` | atoms/corekern | Linux 6.6 + sched_tac + eBPF + io_uring + 微内核化改造 |
| `services/` | daemons | 12 daemon systemd 集成 + io_uring 消息传递 |
| `security/` | cupolas | capability(seL4) + LSM + Landlock + 机密计算 + 国密 |
| `memory/` | heapstore + memoryrovol | MemoryRovol 内核态 + CXL + PMEM + MGLRU |
| `cognition/` | coreloopthree + frameworks | CoreLoopThree kthread + Wasm 3.0 + LLM 调度 |
| `cloudnative/` | gateway + sdk | K8s CRD + containerd shim + OCI + CNI |
| `system/` | commons | RPM + dnf + 配置 + shell |
| `tests-linux/` | 全模块 | 单元 + 集成 + 形式化(seL4) + Soak + 混沌 |

### 2.2 [SC] 共享契约层（跨态桥梁）

跨态组合靠 **IRON-9 v3 四层模型**精确划界：
- **[SC] 共享契约层**：10 核心头文件（`error.h`/`log_types.h`/`ipc.h`/`sched.h`/`memory_types.h`/`security_types.h`/`lsm_types.h`/`cognition_types.h`/`syscalls.h`/`uapi_compat.h`），字节级完全共享。物理宿主 `kernel/include/uapi/linux/airymax/`，agentrt 经 `commons/include/airymax/` 同步。
- **[SS] 语义同源层**：调度/IPC/安全/记忆/认知 API 语义同源、实现独立。
- **[IND] 完全独立层**：平台适配、构建系统、跨平台兼容——**无需对齐**。
- **[DSL] 降级生存层**：`#ifdef AIRY_SC_FALLBACK` 最小生存子集。

**关键认知**：这纠正了此前"OS 级设计是过度设计"的误判——OS 级设计在 **[SC] 契约层是必要的（跨态必须字节一致）**，错误只在于把它**延伸到了 [IND] 层**（用户态内部手写四层分配器/保护环）。

### 2.3 跨态复用的正确形态

当前现状：`cognition_types.h` 已共享枚举 + Q16.16 定点契约，但**五个认知机制本体只在用户态**，内核态 `clt_main.c` 是"kthread 三阶段循环 + think_mode 占位"。

正确形态是**分层复用**：
- **内核态复用**"无浮点、无 I/O、可确定性判定"的机制子集：GRAD E-02 Kahn 拓扑（纯 C、零 Token）、Roadmap L1 状态机（确定性状态转移）、graph_engine 拓扑遍历——这些天然适合 kthread 低延迟场景；
- **用户态保留** LLM 驱动的完整协议（GCCP 五问交互、GRAD 语义层、L2 向量检索）。

**结论**：跨态组合不是"把整套 LLM 协议搬进内核"，而是"内核态承接确定性判定子集，用户态保留认知智能主体"——这正符合"内核不应该思考，机制在平台、策略在用户态"的硬约束。

---

## 三、源码现状与底座硬伤

（详见 `functional-audit-20260808.md` 与前序审查，此处列结论）

**规模**：约 38.5 万行（atoms 11.2万 / daemons 10万 / commons 7.2万 / cupolas 3.6万 / protocols 2.8万 / heapstore 1.6万 / gateway 1.4万），大部分**真实实现非桩**，测试 195 文件。

**三个底座硬伤**（此前文档未充分覆盖）：
1. **四层记忆开源侧 L3/L4 缺失**：`builtin_provider.c` 明确 `l3_structure=0 / l4_pattern=0 / faiss=0`，向量检索是 TF-IDF 非 embedding；L3/L4 只在闭源 memoryrovol——"四层记忆"护城河在开源侧是空的。
2. **状态管理无一致性**：checkpoint 是内存快照，无 watch/租约/跨进程一致 KV（缺 etcd 类能力）。
3. **沙箱依赖外部 docker + Windows 降级桩**：`workbench_container.c` 用 `docker exec`；Windows 上 daemon 间 Unix socket 直接 return NULL。

---

## 四、改进路线图（分优先级，锚定"全功能运行"）

### P0 —— 削减实现复杂度 + 全功能运行闭环（最高优先）

核心原则：**减"实现复杂度"，不减"功能语义"**。

1. **砍 `atoms/corekern/src/mem/` 四层分配器 + 6 个 OOM 文件**（15 文件）→ `malloc`/`mmap` + 对象池，OOM 交给 OS。
2. **折叠 Pregel BSP 超步**：保留 `graph_engine` + `taskflow_advanced` 作为 DAG 主链，Pregel 的检查点职责折叠进 graph_engine，删除半成品超步路径——**消除"两套 DAG 引擎"的维护税**。
3. **收敛 orchestrator 与 engine 两套平行管线为一条主链**：保留 engine 内 Phase 0-4（含 GCCP+GRAD），删除 orchestrator 重复管线。
4. **替换 commons 29 个手写基础模块**（logging/string/uuid/config/sync/network）→ 成熟 C 库（glib/libuv），只留 memory/ipc/observability。
5. **保留 [SC] 契约层**（10 头文件 + 12 syscall + 128B IPC 头），这是跨态组合根基，**不砍**。
6. **五机制全功能运行闭环**（各机制最小动作）：
   - Roadmap：接入 loop 提交入口前置路由，闭环 `wh_progress_cb → absorb`；
   - GCCP/GRAD：补 E-04 语义层判定，抽 Kahn 拓扑为无依赖纯函数供内核复用；
   - Thinkdual：验证三模型回调各用各的模型名；
   - DAG：确认 taskflow_advanced 的 ready-batch/错误策略/取消/超时单测通过；
   - Work Hall：用真实 agent_d 端到端验证一次全链路（认知→执行→复核→回灌）。

### P1 —— 补底座硬伤（行业底座的关键）

7. **沙箱去 docker 化**：移植 dsh 的 Landlock 实现（`native/landlock-run` 纯 C11 单文件，fail-closed 三处、无环境变量输入、functional probe），替换 `docker exec`。
8. **收敛双 IPC 协议头**：删 `airy_types.h` 旧 `airy_ipc_header_t`（AOSP magic），统一到 `airymax/ipc.h`（ARE1 + badge + crc32）；同步 README 12→17 daemon。
9. **补四层记忆开源侧 L3/L4**：要么开源 L3/L4 最小可用实现，要么明确声明开源侧能力边界（L1+L2），让"四层记忆"护城河不依赖闭源库。
10. **状态一致性**：为 heapstore 增加 watch/租约语义，向 etcd 类能力演进（1.0.1 目标）。

### P2 —— 工程纪律（dsh 低风险高收益借鉴）

11. 注册即副作用 + disposer + 逆序回滚（`airy_effect` 原语）。
12. 品牌化 ID（`trace_id`/`correlation_id`/`msg_id` 从不透明结构体）。
13. 每文件覆盖率门禁 + Agent Note 决策记录。
14. 文档分层 + "one home per fact" + slop 清单 + 死链/字数预算。
15. 边界错误 vs 内部错误分层。

### 暂缓项（1.0.1 后，等系统收敛）

16. 能力接缝三角色推广、append-only 单一真相源事件流、runtime invariant companion、声明式组合系统、服务按 key 查找 + 依赖注入——这些是 dsh 精华，但先"能跑"再上。

---

## 五、对标 K8s 的最终差距

| K8s 底座要素 | agentrt 现状 | 关键缺口 |
|-------------|-------------|---------|
| kube-apiserver | gateway_d 白名单 + 协议转换 | ✅ 缺声明式 RBAC 对象 |
| kube-scheduler | sched_d 4 策略 + DAG | ✅ checkpoint 不持久化 |
| **etcd** | heapstore SQLite + hall_store | ⚠️ 无跨进程一致性/watch/租约 |
| kubelet | agent_d spawn/invoke | ✅ 缺 reconcile 循环 |
| CRD/Operator | plugin_d + tool_d + memory vtable | ⚠️ 扩展点分散未统一 |
| **安全沙箱** | cupolas 四层 + docker | ⚠️ 依赖外部 docker |
| 生态信任 | 三平台 CI + 覆盖率 | ⚠️ 缺基准矩阵公开化 |

---

## 六、战略结论

1. **核心认知机制（GCCP/GRAD/蓝图调度/双思考/DAG/任务大厅）是 agentrt 真正的护城河**，其"功能语义"有真实不可替代的价值（零 Token 硬逻辑验证、三级降级复用、三权分立、认知-执行解耦），**必须全功能运行，不是砍掉**。

2. **"全功能运行"与"削减复杂度"不矛盾**：砍的是"实现复杂度"（四层分配器、Pregel BSP 半成品、重复管线、手写基础库），保留的是"功能语义"。这才是 reversal-slimming 报告的正确解读。

3. **跨态组合靠 [SC] 契约层**：agentrt 与 agent-linux 是"同一架构在用户态与内核态的两端"，内核态承接确定性判定子集（GRAD Kahn、Roadmap L1、graph_engine 拓扑），用户态保留认知智能主体。这既符合"内核不思考"硬约束，又让五机制真正跨态复用。

4. **行业底座差距在四项非功能性硬伤**：一致性存储、原生沙箱、开源侧记忆完整性、复杂度控制。前三项补短板，第四项做减法——**而第四项是前三项能落地的前提**。

---

*本报告整合前序 9 篇文档 + 源码审查 + deepseek-harness 逐字节研究 + 核心机制价值论证 + agent-linux 跨态分析，是 `_review_v4.3` 文档链的收束之作。*
