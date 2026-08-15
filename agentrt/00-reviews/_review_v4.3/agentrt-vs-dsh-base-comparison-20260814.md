# agentrt vs deepseek-harness 行业底座对比研究报告

> **报告编号**：REVIEW-AGENTRT-2026-08-14-COMPARE
> **报告类型**：竞品深度对比（平台 vs 框架物种判别）
> **对比对象**：`agentrt`（AI Agent 运行时平台，0.1.1→0.1.2）vs `deepseek-harness`（dsh，开源 agent harness）
> **产出目录**：`closed-docs/agentrt/00-reviews/_review_v4.3/`
> **审查日期**：2026-08-14
> **审查人**：SPHARX 工程标准组
> **状态**：研究性报告（供 0.1.2 战略决策参考）

---

## 摘要

深度对比的客观结论是：**agentrt 与 dsh 不是同类竞品，而是"平台 vs 框架"的物种之别**（最贴切类比是 K8s vs Spring，而非 K8s vs Docker）。

- **架构定位上，agentrt 更接近"行业底座"（平台）**：常驻多进程 daemon、控制面/数据面分离、跨进程 128B 二进制 ABI、跨态组合（用户态↔内核态）——这些是 dsh 完全没有的维度。
- **工程成熟度上，dsh 现在更接近"能用"（框架）**：真开源、可运行、可验证、可组合、已收敛。

**核心发现**：agentrt 要成为 K8s 式底座，真正的差距不是"缺功能"，而是"缺平台本质属性"——但**并非必须照抄 K8s 的 4 个组件**（reconcile/etcd/CRD/全开源）。本报告区分"平台本质（必须达到）"与"K8s 具体实现（可选路径）"，并论证 agentrt 已通过认知闭环部分达到本质，只需延伸和统一，而非从零复刻。

---

## 一、7 维度逐项对比（源码事实）

| 维度 | dsh | agentrt | 占优 |
|------|-----|---------|------|
| 形态本质 | 框架/库：单进程 Node + 进程内 DI | 平台外形：17 常驻 daemon + AIRY_HOME + 控制面/数据面分离 | agentrt |
| 控制面/数据面 | 无显式分离 | 有（sched_d/gateway_d/mem_d 控制面 vs agent_d/tool_d/llm_d 数据面） | agentrt |
| 稳定契约 | 进程内 TS 类型，无跨进程 ABI，无版本承诺 | 128B IPC 头 + [SC] 跨态契约（但 3 套分叉未收敛） | 潜力 agentrt |
| 可组合扩展 | 强：Cordis DI + 能力接缝三角色 + profile/bundle | 弱：仅 memory vtable（全局单例），扩展点分散 | dsh |
| 运行形态 | 进程内库 | 托管运行时（daemon 常驻，agent 是子进程工作负载） | agentrt |
| 生态开放 | 真开源可验证（MIT + npm + 100% 覆盖率 + 快照） | L3/L4 闭源、沙箱依赖 docker、无公开基准 | dsh |
| 工程成熟度 | 能跑已收敛（npx 即用，23 万行测试） | 不能收敛（385k 行手写 C，多套冗余） | dsh |

**关键事实**：dsh 的 `src`≈19.8 万行 + `tests`≈23 万行（1:1）；agentrt 385,725 行 C/C++ / 1301 文件 / 17 daemon 目录（README 仍写 12，漂移）。

---

## 二、物种判别：平台 vs 框架

**dsh ≈ agent 界的 Spring Boot / Koishi**：回答"如何在单进程内可组合、可替换地写出一个 agent"。它成为底座的方式是成为"事实标准的框架/库"，而非"平台"。dsh 自己明确声明"THERE WILL BE COMPATIBILITY-BREAKING CHANGES"、`SESSION_FORMAT_VERSION=0`——它甚至不做"稳定契约"的承诺。

**agentrt ≈ 一个自称 K8s、但还没有 reconcile/etcd/CRD 的多进程运行时**：回答"如何像操作系统/K8s 一样托管一群 agent 进程"。它的愿景甚至比 K8s 更低层（跨态延伸到内核），但当前实现是"半成品平台"。

**结论**：两者不在同一层竞争。dsh 竞争"开发者心智/库标准"，agentrt 竞争"运行时/编排平台"。把两者当"同类竞品"比较是范畴错误——这也是为何"加法式借鉴 dsh 能力接缝/事件流"会被 reversal-slimming 报告纠偏的深层原因：给平台照抄框架的进程内机制，方向就错了。

---

## 三、平台本质 vs K8s 实现方式（核心辨析）

agentrt 要接近"平台本质"，**不是必须照抄 K8s 的 4 个组件**。区分如下：

| 子代理列出的差距 | 平台本质（必须达到） | K8s 实现（可选路径） | agentrt 自己的路径 |
|-----------------|---------------------|---------------------|-------------------|
| reconcile 闭环 | 声明式 + 自愈收敛 | controller watch etcd | **认知层已有雏形**：蓝图（desired）→ GRAD 收敛 → 执行 → 复核（DRIFT）→ 回灌（replan）。需延伸到生命周期层 |
| etcd 等价物 | 状态可共享、可 watch、可恢复 | 分布式一致 KV（Raft） | 单机阶段用事件流 + SQLite WAL + watch；分布式 etcd 推迟到云原生多机（agentrt-linux cloudnative） |
| 统一扩展机制 | 第三方不改核心即可接入 | CRD/Operator | memory vtable 推广到 LLM/tool/storage/sandbox + 统一注册表（dsh Cordis 三角色为参考） |
| 可验证开源 | 第三方能独立验证复现 | conformance + 全开源 | L1/L2 开源 + 公开评测基准 + 文档分层（生态准入）；L3/L4 闭源是商业策略可保留 |

**核心洞察**：agentrt 缺的不是"本质"本身，而是"本质未被系统化 + 被 K8s 组件名称遮蔽"。

1. **reconcile 闭环其实已存在**：蓝图调度 + GRAD + 复核回灌就是 agent 界的 reconcile（声明蓝图 → 执行 → 检测 DRIFT → 重规划）。缺的是资源/生命周期层的 reconcile（agent 自愈、任务重调度），不是从零造 controller。

2. **etcd 等价物不是当前必须**：agentrt 还没做多机集群。单机多 daemon 用"事件流（⑥）+ SQLite WAL + watch"就达到"状态可共享可恢复"的本质。分布式 etcd 是云原生多机阶段才需要的。

3. **统一扩展机制是真正需补的**：不是造 CRD，而是把 memory vtable 的"能力接缝"模式统一推广（这正是 Unify Design 的 SSoT 思想）。

4. **可验证开源是生态问题**：L1/L2 开源 + 评测基准 + 文档分层是"底座"准入门槛，但 L3/L4 闭源不影响"平台本质"。

---

## 四、修正后的结论

### 4.1 谁更能成为行业底座？

- **K8s 式平台底座**：只有 agentrt 有资格冲（dsh 架构上出局），但 agentrt 现在还不是。
- **Spring 式框架底座**：dsh 现在更接近（真开源、能跑、可组合、有纪律）。

### 4.2 agentrt 要达到"平台本质"，真正必须做的只有 2 项

1. **reconcile 闭环的延伸**：把已有的"认知层 reconcile"（蓝图+GRAD+复核）延伸到"生命周期/资源层"（agent 自愈、任务重调度）——从已有本质延伸，不是从零造。

2. **统一扩展机制**：把 memory vtable 的能力接缝模式统一推广（LLM/tool/storage/sandbox 四域 + 统一注册表）。

**推迟项**：etcd 等价物（分布式一致 KV）→ 云原生多机阶段（agentrt-linux cloudnative）；可验证开源 → 生态工作（与平台本质正交）。

### 4.3 0.1.2 范围修正

| 阶段 | 内容 | 对应本质 |
|------|------|---------|
| 阶段 1 | SSoT 收敛（8 冲突点）+ CLI/TUI | 契约收敛 + 复杂度收敛（让系统能收敛） |
| 阶段 2 | reconcile 延伸 + 统一扩展机制 | 平台本质（声明式自愈 + 可组合扩展） |
| 阶段 3（后置） | 分布式一致存储 + 云原生多机 | 多机集群（agentrt-linux cloudnative） |
| 阶段 4（生态） | L1/L2 开源 + 评测基准 + 文档分层 | 生态信任（可验证开源） |

---

## 五、战略结论

1. **agentrt 的差异化定位正确**：它是唯一以"K8s 式平台形态"（常驻运行时 + 控制面 + 跨进程契约 + 跨态）设计的 agent 项目，dsh 在架构上无法竞争这个定位。

2. **但"能成为"不等于"已成为"**：agentrt 缺的是"平台本质"（声明式自愈 + 统一扩展），而非"功能"。而这些本质中，**认知层 reconcile 已经存在**（蓝图+GRAD+复核），只需延伸；**统一扩展**可复用 memory vtable 模式；**etcd** 可推迟。

3. **正确的 0.1.2 路线**：SSoT 收敛（让系统收敛）→ 平台本质补齐（reconcile 延伸 + 统一扩展）→ 云原生多机（后置）。不是"照抄 K8s 组件"，而是"用 agentrt 自己的认知闭环 + 跨态契约达到平台本质"。

---

*本报告基于 7 篇前序文档 + dsh 源码亲自核对 + agentrt 源码亲自核对，客观对比，不带预设立场。*
